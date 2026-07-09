
"""
Recommendation orchestration module.

Coordinates the entire recommendation pipeline:
- Load database data
- Generate candidates
- Score candidates
- Handle cold starts
- Cache recommendations
- Generate explanations
"""
import sys
import os
from typing import List, Dict, Optional, Any
from collections import defaultdict

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.database import SessionLocal
from data.repository import (
    UserRepository,
    ContentRepository,
    SkillRepository,
    UserSkillRepository,
    ContentSkillRepository,
    InteractionRepository
)

# Handle imports both as package and as script
try:
    from .candidate_gen import CandidateGenerator
    from .scorer import RecommendationScorer
    from .cache import RecommendationCache
except ImportError:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    from engine.candidate_gen import CandidateGenerator
    from engine.scorer import RecommendationScorer
    from engine.cache import RecommendationCache


class RecommendationOrchestrator:
    """
    Main orchestrator for the recommendation system.
    Handles all steps from data loading to recommendation delivery.
    """

    def __init__(self, cache_ttl_seconds: int = 300, cache_max_size: int = 1000):
        """
        Initialize recommendation orchestrator.

        Args:
            cache_ttl_seconds: Time-to-live for cached recommendations (default 5 minutes)
            cache_max_size: Maximum number of cached recommendation sets (default 1000)
        """
        # Initialize components
        self.candidate_generator = CandidateGenerator()
        self.scorer = RecommendationScorer()

        # Initialize cache using our RecommendationCache class
        self.cache = RecommendationCache(ttl_seconds=cache_ttl_seconds, max_size=cache_max_size)

        # Data storage (loaded from database)
        self.loaded = False
        self.user_interactions: Dict[int, List[int]] = defaultdict(list)
        self.item_features: Dict[int, List[int]] = defaultdict(list)
        self.item_popularity: Dict[int, int] = defaultdict(int)
        self.user_skills: Dict[int, List[int]] = defaultdict(list)
        self.item_skills: Dict[int, List[int]] = defaultdict(list)
        self.item_details: Dict[int, Dict[str, Any]] = {}
        self.user_details: Dict[int, Dict[str, Any]] = {}

    def load_database_data(self) -> None:
        """
        Load all required data from the database into memory for fast access.
        """
        print("Loading database data...")
        with SessionLocal() as db:
            # Load users
            user_repo = UserRepository(db)
            users = user_repo.get_all()
            for user in users:
                self.user_details[user.id] = {
                    "username": user.username,
                    "email": user.email
                }

            # Load content
            content_repo = ContentRepository(db)
            contents = content_repo.get_all()
            for content in contents:
                self.item_details[content.id] = {
                    "title": content.title,
                    "description": content.description
                }
                self.item_popularity[content.id] = 0

            # Load skills
            # No need to store skills directly, just user and content skill mappings

            # Load user skills
            user_skill_repo = UserSkillRepository(db)
            user_skills = user_skill_repo.get_all()
            for us in user_skills:
                self.user_skills[us.user_id].append(us.skill_id)

            # Load content skills
            content_skill_repo = ContentSkillRepository(db)
            content_skills = content_skill_repo.get_all()
            for cs in content_skills:
                self.item_skills[cs.content_id].append(cs.skill_id)
                self.item_features[cs.content_id].append(cs.skill_id)

            # Load interactions and build user_interactions and item_popularity
            interaction_repo = InteractionRepository(db)
            interactions = interaction_repo.get_all()
            for interaction in interactions:
                self.user_interactions[interaction.user_id].append(interaction.content_id)
                self.item_popularity[interaction.content_id] += 1

        self.loaded = True
        print(f"Successfully loaded data: {len(self.user_details)} users, {len(self.item_details)} content items")

    def _handle_cold_start(self, user_id: int, limit: int) -> List[int]:
        """
        Handle cold-start for users with no interactions or skills.

        Strategy: Return top-N most popular content items.

        Args:
            user_id: ID of the cold-start user
            limit: Maximum number of recommendations to return

        Returns:
            List of top-N most popular content item IDs
        """
        # Sort items by popularity in descending order
        sorted_items = sorted(
            self.item_popularity.items(),
            key=lambda x: x[1],
            reverse=True
        )
        # Return top N item IDs
        return [item_id for item_id, _ in sorted_items[:limit]]

    def _generate_explanations(self, user_id: int, item_id: int) -> List[str]:
        """
        Generate explanations for why a particular item is recommended to a user.

        Args:
            user_id: ID of the user
            item_id: ID of the recommended item

        Returns:
            List of explanation strings
        """
        explanations = []
        user_skills_set = set(self.user_skills.get(user_id, []))
        item_skills_set = set(self.item_skills.get(item_id, []))

        # Skill overlap explanation
        skill_overlap = user_skills_set.intersection(item_skills_set)
        if skill_overlap:
            explanations.append(f"Recommended because you share skills like {', '.join(map(str, skill_overlap))}")

        # Similar users explanation (if collaborative filtering was used)
        # Simplified for now
        if self.item_popularity.get(item_id, 0) > 10:
            explanations.append("Many other users like this content")

        return explanations

    def get_recommendations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations for a user.

        Steps:
        1. Check cache for existing recommendations
        2. If not in cache:
           a. Check if user is cold-start
           b. If cold-start: use popularity-based recommendations
           c. Else: generate candidates, score, then rank
        3. Cache recommendations
        4. Generate explanations and return enriched recommendations

        Args:
            user_id: ID of the user to get recommendations for
            limit: Maximum number of recommendations to return (default 10)

        Returns:
            List of recommendation dictionaries with:
                - id: content item ID
                - title: content title
                - description: content description
                - explanations: list of explanation strings
        """
        # Ensure data is loaded
        if not self.loaded:
            self.load_database_data()

        # Create cache key
        cache_key = (user_id, limit)

        # Check cache first using our RecommendationCache.get() method
        cached_recs = self.cache.get(cache_key)
        if cached_recs is not None:
            return cached_recs

        # Determine if user is cold-start
        user_interactions = self.user_interactions.get(user_id, [])
        user_skill_list = self.user_skills.get(user_id, [])
        is_cold_start = len(user_interactions) == 0 and len(user_skill_list) == 0

        if is_cold_start:
            print(f"User {user_id} is cold-start, using popularity recommendations")
            recommended_item_ids = self._handle_cold_start(user_id, limit)
        else:
            # Generate candidates using all strategies
            collab_candidates = self.candidate_generator.collaborative_filtering(
                self.user_interactions, user_id, top_k=limit * 3
            )
            content_candidates = self.candidate_generator.content_based_filtering(
                self.item_features, user_interactions, top_k=limit * 3
            )
            skill_candidates = self.candidate_generator.skill_matching(
                user_skill_list, self.item_skills, user_interactions, top_k=limit * 3
            )
            popularity_candidates = self.candidate_generator.popularity_based(
                self.item_popularity, user_interactions, top_k=limit * 3
            )

            # Score candidates using the scorer
            recommended_item_ids = self.scorer.score_recommendations(
                collab_candidates,
                content_candidates,
                skill_candidates,
                popularity_candidates
            )

        # Take top N items
        recommended_item_ids = recommended_item_ids[:limit]

        # Enrich recommendations with details and explanations
        recommendations = []
        for item_id in recommended_item_ids:
            details = self.item_details.get(item_id, {})
            recommendations.append({
                "id": item_id,
                "title": details.get("title", "Unknown Item"),
                "description": details.get("description", ""),
                "explanations": self._generate_explanations(user_id, item_id)
            })

        # Cache the results using our RecommendationCache.set() method
        self.cache.set(cache_key, recommendations)

        return recommendations

    def record_feedback(
        self,
        user_id: int,
        content_id: int,
        rating: Optional[float] = None,
        interaction_type: Optional[str] = None
    ) -> None:
        """
        Record user feedback/interaction and invalidate cache.

        Args:
            user_id: ID of the user providing feedback
            content_id: ID of the content item
            rating: Optional rating given by user (e.g., 1-5)
            interaction_type: Optional type of interaction (e.g., "view", "like")
        """
        print(f"Recording feedback: user {user_id} interacted with content {content_id}")

        # Update in-memory data
        if content_id not in self.user_interactions.get(user_id, []):
            self.user_interactions[user_id].append(content_id)
        self.item_popularity[content_id] += 1

        # Save to database
        with SessionLocal() as db:
            interaction_repo = InteractionRepository(db)
            interaction_repo.record_feedback(
                user_id=user_id,
                content_id=content_id,
                rating=rating,
                interaction_type=interaction_type
            )

        # Invalidate cache for this user using our RecommendationCache.invalidate_user()
        self.cache.invalidate_user(user_id)

    def clear_cache(self) -> None:
        """
        Clear all cached recommendations.
        """
        self.cache.clear()
        print("Recommendation cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        return self.cache.get_stats()

    def reset_cache_stats(self) -> None:
        """
        Reset cache hit/miss statistics.
        """
        self.cache.reset_stats()


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Recommendation Orchestrator - Example Usage")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = RecommendationOrchestrator(cache_ttl_seconds=60)  # 1-minute TTL for testing

    # Load data
    orchestrator.load_database_data()

    # Get recommendations for user 1 twice to test caching
    print("\n--- First request (should be a cache miss) ---")
    recs = orchestrator.get_recommendations(1, limit=5)
    print("\nRecommendations:")
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Description: {rec['description']}")
        print(f"   Explanations: {', '.join(rec['explanations'])}")

    print("\n--- Second request (should be a cache hit) ---")
    recs_cached = orchestrator.get_recommendations(1, limit=5)

    # Print cache stats
    print("\n--- Cache Statistics ---")
    cache_stats = orchestrator.get_cache_stats()
    print(f"Hits: {cache_stats['hits']}")
    print(f"Misses: {cache_stats['misses']}")
    print(f"Current Size: {cache_stats['current_size']}")
    print(f"Max Size: {cache_stats['max_size']}")

    # Record some feedback
    print("\n--- Recording Feedback ---")
    orchestrator.record_feedback(1, recs[0]['id'], rating=5, interaction_type="like")

    # Check stats again after invalidation
    print("\n--- Cache Statistics After Feedback ---")
    print(orchestrator.get_cache_stats())

    # Clear cache
    orchestrator.clear_cache()
