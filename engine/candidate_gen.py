
"""
Candidate generation module for recommendation system.

Generates recommendation candidates using multiple strategies:
- Collaborative Filtering
- Content-Based Filtering
- Popularity-Based
- Skill Matching
"""
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import numpy as np


class CandidateGenerator:
    """
    Main class for generating recommendation candidates.
    """

    def __init__(self):
        """Initialize candidate generator.
        """
        pass

    def collaborative_filtering(
        self,
        user_interactions: Dict[int, List[int]],
        user_id: int,
        top_k: int = 50
    ) -> List[Tuple[int, float]]:
        """
        Generate candidates using collaborative filtering (item-based).

        Args:
            user_interactions: Dictionary mapping user IDs to lists of item IDs they've interacted with
            user_id: ID of user to generate candidates for
            top_k: Maximum number of candidates to return

        Returns:
            List of (item_id, score) tuples
        """
        # Build item-item co-occurrence matrix
        item_cooccurrence: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

        # For each user, count how many times items appear together
        for items in user_interactions.values():
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    item_a = items[i]
                    item_b = items[j]
                    item_cooccurrence[item_a][item_b] += 1
                    item_cooccurrence[item_b][item_a] += 1

        # Score items based on user's interactions
        candidate_scores: Dict[int, float] = defaultdict(float)
        user_items = user_interactions.get(user_id, [])

        for item in user_items:
            if item in item_cooccurrence:
                for related_item, count in item_cooccurrence[item].items():
                    if related_item not in user_items:
                        candidate_scores[related_item] += count

        # Normalize scores
        if candidate_scores:
            max_score = max(candidate_scores.values())
            for item_id in candidate_scores:
                candidate_scores[item_id] /= max_score

        # Sort and return top_k candidates
        sorted_candidates = sorted(
            candidate_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        return sorted_candidates

    def content_based_filtering(
        self,
        item_features: Dict[int, List[int]],
        user_item_interactions: List[int],
        top_k: int = 50
    ) -> List[Tuple[int, float]]:
        """
        Generate candidates using content-based filtering.

        Args:
            item_features: Dictionary mapping item IDs to list of feature/skill IDs
            user_item_interactions: List of item IDs the user has interacted with
            top_k: Maximum number of candidates to return

        Returns:
            List of (item_id, score) tuples
        """
        try:
            from .similarity import jaccard_similarity
        except ImportError:
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, project_root)
            from engine.similarity import jaccard_similarity

        # Build user's feature profile
        user_features: Set[int] = set()
        for item_id in user_item_interactions:
            if item_id in item_features:
                user_features.update(item_features[item_id])

        # Score items by feature overlap
        candidate_scores: Dict[int, float] = defaultdict(float)
        for item_id, features in item_features.items():
            if item_id in user_item_interactions:
                continue
            feature_set = set(features)
            score = jaccard_similarity(user_features, feature_set)
            candidate_scores[item_id] = score

        # Sort and return top_k candidates
        sorted_candidates = sorted(
            candidate_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        return sorted_candidates

    def popularity_based(
        self,
        item_popularity: Dict[int, int],
        user_item_interactions: List[int],
        top_k: int = 50
    ) -> List[Tuple[int, float]]:
        """
        Generate candidates using popularity-based recommendation.

        Args:
            item_popularity: Dictionary mapping item IDs to interaction counts
            user_item_interactions: List of item IDs the user has interacted with
            top_k: Maximum number of candidates to return

        Returns:
            List of (item_id, score) tuples
        """
        # Score items by popularity (excluding already interacted items)
        candidate_scores: Dict[int, float] = defaultdict(float)
        for item_id, count in item_popularity.items():
            if item_id in user_item_interactions:
                continue
            candidate_scores[item_id] = count

        # Normalize scores
        if candidate_scores:
            max_score = max(candidate_scores.values())
            for item_id in candidate_scores:
                candidate_scores[item_id] /= max_score

        # Sort and return top_k candidates
        sorted_candidates = sorted(
            candidate_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        return sorted_candidates

    def skill_matching(
        self,
        user_skills: List[int],
        item_skills: Dict[int, List[int]],
        user_item_interactions: List[int],
        top_k: int = 50
    ) -> List[Tuple[int, float]]:
        """
        Generate candidates using skill matching.

        Args:
            user_skills: List of skill IDs for the user
            item_skills: Dictionary mapping item IDs to list of skill IDs
            user_item_interactions: List of item IDs the user has interacted with
            top_k: Maximum number of candidates to return

        Returns:
            List of (item_id, score) tuples
        """
        try:
            from .similarity import jaccard_similarity
        except ImportError:
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, project_root)
            from engine.similarity import jaccard_similarity

        user_skill_set = set(user_skills)
        candidate_scores: Dict[int, float] = defaultdict(float)

        for item_id, skills in item_skills.items():
            if item_id in user_item_interactions:
                continue
            item_skill_set = set(skills)
            score = jaccard_similarity(user_skill_set, item_skill_set)
            candidate_scores[item_id] = score

        # Sort and return top_k candidates
        sorted_candidates = sorted(
            candidate_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        return sorted_candidates

    def merge_and_rank_candidates(
        self,
        candidate_lists: List[List[Tuple[int, float]]],
        weights: List[float] = None
    ) -> List[int]:
        """
        Merge and rank recommendation candidates.

        Args:
            candidate_lists: List of candidate lists, each a list of (item_id, score) tuples
            weights: Optional list of weights for each candidate list (must be same length as candidate_lists)

        Returns:
            List of ranked candidate IDs
        """
        if weights is None:
            # Default to equal weights
            weights = [1.0 for _ in candidate_lists]

        if len(candidate_lists) != len(weights):
            raise ValueError("Number of candidate lists and weights must have the same length")

        # Aggregate scores
        total_scores: Dict[int, float] = defaultdict(float)

        for candidates, weight in zip(candidate_lists, weights):
            for item_id, score in candidates:
                total_scores[item_id] += score * weight

        # Sort candidates by total score
        ranked_candidates = sorted(
            total_scores.items(), key=lambda x: x[1], reverse=True)
        # Extract just the item IDs
        return [item_id for item_id, _ in ranked_candidates]

    def generate_all_candidates(
        self,
        user_id: int,
        user_interactions: Dict[int, List[int]],
        item_features: Dict[int, List[int]],
        item_popularity: Dict[int, int],
        user_skills: List[int],
        item_skills: Dict[int, List[int]],
        top_k: int = 100,
        strategy_weights: List[float] = None
    ) -> List[int]:
        """
        Generate candidates using all available strategies.

        Args:
            user_id: ID of user to generate candidates for
            user_interactions: Dictionary mapping user IDs to lists of item IDs they've interacted with
            item_features: Dictionary mapping item IDs to list of feature IDs
            item_popularity: Dictionary mapping item IDs to interaction counts
            user_skills: List of skill IDs for the user
            item_skills: Dictionary mapping item IDs to list of skill IDs
            top_k: Maximum number of final candidates to return
            strategy_weights: Optional list of weights for each strategy (collab, content, popularity, skill)

        Returns:
            List of ranked candidate item IDs
        """
        user_item_interactions = user_interactions.get(user_id, [])

        # Generate candidates using each strategy
        collab_candidates = self.collaborative_filtering(
            user_interactions, user_id, top_k=top_k
        )
        content_candidates = self.content_based_filtering(
            item_features, user_item_interactions, top_k=top_k
        )
        popularity_candidates = self.popularity_based(
            item_popularity, user_item_interactions, top_k=top_k
        )
        skill_candidates = self.skill_matching(
            user_skills, item_skills, user_item_interactions, top_k=top_k
        )

        # Merge and rank
        all_candidate_lists = [collab_candidates, content_candidates, popularity_candidates, skill_candidates]
        ranked_candidates = self.merge_and_rank_candidates(all_candidate_lists, strategy_weights)

        return ranked_candidates[:top_k]


if __name__ == "__main__":
    # Add project root to path for direct script execution
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    # Example usage
    print("=" * 60)
    print("Candidate Generator - Example Usage")
    print("=" * 60)

    # Create some sample data
    sample_user_interactions = {
        1: [10, 11, 12],
        2: [11, 12, 13],
        3: [10, 13, 14]
    }
    sample_item_features = {
        10: [1, 2, 3],
        11: [2, 3, 4],
        12: [3, 4, 5],
        13: [4, 5, 6],
        14: [5, 6, 7]
    }
    sample_item_popularity = {
        10: 50,
        11: 75,
        12: 100,
        13: 80,
        14: 60
    }
    sample_user_skills = [1, 2, 3]
    sample_item_skills = {
        10: [1, 2],
        11: [2, 3, 4],
        12: [3, 4],
        13: [4, 5, 6],
        14: [5, 6]
    }

    # Initialize candidate generator
    generator = CandidateGenerator()

    # Test individual strategies
    print("\n--- Collaborative Filtering Candidates ---")
    collab = generator.collaborative_filtering(sample_user_interactions, user_id=1, top_k=10)
    print(collab)

    print("\n--- Content-Based Filtering Candidates ---")
    content = generator.content_based_filtering(
        sample_item_features, user_item_interactions=[10, 11, 12], top_k=10
    )
    print(content)

    print("\n--- Popularity-Based Candidates ---")
    pop = generator.popularity_based(
        sample_item_popularity, user_item_interactions=[10, 11, 12], top_k=10
    )
    print(pop)

    print("\n--- Skill Matching Candidates ---")
    skill = generator.skill_matching(
        sample_user_skills, sample_item_skills, user_item_interactions=[10, 11, 12], top_k=10
    )
    print(skill)

    # Test combined candidates
    print("\n--- Combined & Ranked Candidates ---")
    combined = generator.generate_all_candidates(
        user_id=1,
        user_interactions=sample_user_interactions,
        item_features=sample_item_features,
        item_popularity=sample_item_popularity,
        user_skills=sample_user_skills,
        item_skills=sample_item_skills,
        top_k=10
    )
    print(combined)
