
"""
Recommendation scoring module.

Scores recommendation candidates using weighted combination of:
- 35% Collaborative Filtering
- 30% Content Similarity
- 20% Skill Match
- 15% Popularity
"""
from typing import List, Dict, Tuple
from collections import defaultdict


class RecommendationScorer:
    """
    Main class for scoring recommendation candidates.
    """

    # Weight constants as specified
    WEIGHTS = {
        "collaborative": 0.35,
        "content": 0.30,
        "skill": 0.20,
        "popularity": 0.15
    }

    def __init__(self):
        """Initialize recommendation scorer."""
        pass

    def _normalize_scores(
        self,
        scores: Dict[int, float]
    ) -> Dict[int, float]:
        """
        Normalize scores to [0, 1] range using min-max normalization.

        Formula for each score s:
        s_normalized = (s - s_min) / (s_max - s_min)
        If all scores are the same (s_max == s_min), set all normalized scores to 1.0

        Args:
            scores: Dictionary mapping item IDs to raw scores

        Returns:
            Dictionary mapping item IDs to normalized scores [0, 1]
        """
        normalized = {}

        if not scores:
            return normalized

        # Find min and max raw scores
        s_min = min(scores.values())
        s_max = max(scores.values())

        # Avoid division by zero if all scores are equal
        if s_max == s_min:
            normalized = {item_id: 1.0 for item_id in scores}
        else:
            for item_id, s in scores.items():
                normalized[item_id] = (s - s_min) / (s_max - s_min)

        return normalized

    def _extract_candidate_scores(
        self,
        candidates: List[Tuple[int, float]]
    ) -> Dict[int, float]:
        """
        Convert list of (item_id, score) tuples to a dictionary.

        Args:
            candidates: List of (item_id, score) tuples

        Returns:
            Dictionary mapping item IDs to scores
        """
        return {item_id: score for item_id, score in candidates}

    def score_recommendations(
        self,
        collab_candidates: List[Tuple[int, float]],
        content_candidates: List[Tuple[int, float]],
        skill_candidates: List[Tuple[int, float]],
        popularity_candidates: List[Tuple[int, float]]
    ) -> List[int]:
        """
        Score recommendation candidates using weighted combination.

        Final score formula for each item:
        final_score = (w_collab * collab_score) +
                      (w_content * content_score) +
                      (w_skill * skill_score) +
                      (w_popularity * popularity_score)

        Where:
        - w_collab = 0.35
        - w_content = 0.30
        - w_skill = 0.20
        - w_popularity = 0.15

        Args:
            collab_candidates: List of (item_id, score) from collaborative filtering
            content_candidates: List of (item_id, score) from content similarity
            skill_candidates: List of (item_id, score) from skill matching
            popularity_candidates: List of (item_id, score) from popularity

        Returns:
            List of item IDs ranked by final score (highest to lowest)
        """
        # Extract candidate scores into dictionaries
        collab_scores = self._extract_candidate_scores(collab_candidates)
        content_scores = self._extract_candidate_scores(content_candidates)
        skill_scores = self._extract_candidate_scores(skill_candidates)
        popularity_scores = self._extract_candidate_scores(popularity_candidates)

        # Find all unique candidate items across all sources
        all_items = set()
        all_items.update(collab_scores.keys())
        all_items.update(content_scores.keys())
        all_items.update(skill_scores.keys())
        all_items.update(popularity_scores.keys())

        # Normalize each score type independently
        norm_collab = self._normalize_scores(collab_scores)
        norm_content = self._normalize_scores(content_scores)
        norm_skill = self._normalize_scores(skill_scores)
        norm_popularity = self._normalize_scores(popularity_scores)

        # Calculate final weighted scores
        final_scores: Dict[int, float] = defaultdict(float)

        for item_id in all_items:
            # Get normalized scores for each component (0 if not present)
            collab = norm_collab.get(item_id, 0.0)
            content = norm_content.get(item_id, 0.0)
            skill = norm_skill.get(item_id, 0.0)
            popularity = norm_popularity.get(item_id, 0.0)

            # Calculate weighted score using the specified formula
            final_score = (
                self.WEIGHTS["collaborative"] * collab +
                self.WEIGHTS["content"] * content +
                self.WEIGHTS["skill"] * skill +
                self.WEIGHTS["popularity"] * popularity
            )

            final_scores[item_id] = final_score

        # Sort items by final score in descending order
        ranked_items = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return just the item IDs
        return [item_id for item_id, _ in ranked_items]


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Recommendation Scorer - Example Usage")
    print("=" * 60)

    # Sample candidate scores
    sample_collab = [(101, 0.8), (102, 0.6), (103, 0.4)]
    sample_content = [(102, 0.9), (103, 0.7), (104, 0.5)]
    sample_skill = [(101, 0.7), (104, 0.6), (105, 0.4)]
    sample_popularity = [(103, 0.9), (102, 0.8), (101, 0.7)]

    # Initialize scorer
    scorer = RecommendationScorer()

    # Score recommendations
    ranked = scorer.score_recommendations(
        sample_collab,
        sample_content,
        sample_skill,
        sample_popularity
    )

    print("\nFinal ranked recommendations:")
    print(ranked)
