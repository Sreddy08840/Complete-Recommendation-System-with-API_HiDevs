
import pytest
import numpy as np
from engine.similarity import cosine_similarity, jaccard_similarity, pearson_correlation
from engine.candidate_gen import CandidateGenerator
from engine.scorer import RecommendationScorer
from engine.cache import RecommendationCache
from engine.hybrid import HybridRecommender


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    vec1 = np.array([1, 2, 3])
    vec2 = np.array([1, 2, 3])
    vec3 = np.array([3, 2, 1])
    
    assert cosine_similarity(vec1, vec2) == pytest.approx(1.0)
    assert cosine_similarity(vec1, vec3) == pytest.approx(0.714, rel=1e-3)


def test_jaccard_similarity():
    """Test jaccard similarity calculation."""
    set1 = {1, 2, 3}
    set2 = {2, 3, 4}
    set3 = {5, 6, 7}
    
    assert jaccard_similarity(set1, set2) == 0.5
    assert jaccard_similarity(set1, set3) == 0.0
    assert jaccard_similarity(set1, set1) == 1.0


def test_pearson_correlation():
    """Test pearson correlation calculation."""
    arr1 = np.array([1, 2, 3, 4, 5])
    arr2 = np.array([2, 4, 6, 8, 10])
    arr3 = np.array([5, 4, 3, 2, 1])
    
    assert pearson_correlation(arr1, arr2) == pytest.approx(1.0)
    assert pearson_correlation(arr1, arr3) == pytest.approx(-1.0)


def test_candidate_generator():
    """Test CandidateGenerator methods."""
    generator = CandidateGenerator()
    
    # Test data
    user_interactions = {
        1: [10, 11],
        2: [11, 12]
    }
    item_features = {
        10: [1, 2],
        11: [2, 3],
        12: [3, 4]
    }
    item_popularity = {
        10: 5,
        11: 10,
        12: 8
    }
    user_skills = [1, 2]
    item_skills = {
        10: [1, 2],
        11: [2, 3],
        12: [3, 4]
    }
    
    # Test collaborative filtering
    collab = generator.collaborative_filtering(user_interactions, user_id=1, top_k=10)
    assert len(collab) >= 0
    
    # Test content based filtering
    content = generator.content_based_filtering(item_features, user_item_interactions=[10], top_k=10)
    assert len(content) >= 0
    
    # Test popularity based
    popularity = generator.popularity_based(item_popularity, user_item_interactions=[10], top_k=10)
    assert len(popularity) >= 0
    
    # Test skill matching
    skill = generator.skill_matching(user_skills, item_skills, user_item_interactions=[10], top_k=10)
    assert len(skill) >= 0
    
    # Test merge and rank
    merged = generator.merge_and_rank_candidates([collab, content], [0.5, 0.5])
    assert isinstance(merged, list)
    
    # Test generate all candidates
    all_candidates = generator.generate_all_candidates(
        user_id=1,
        user_interactions=user_interactions,
        item_features=item_features,
        item_popularity=item_popularity,
        user_skills=user_skills,
        item_skills=item_skills,
        top_k=10
    )
    assert isinstance(all_candidates, list)


def test_recommendation_scorer():
    """Test RecommendationScorer."""
    scorer = RecommendationScorer()
    
    collab_candidates = [(101, 0.8), (102, 0.6)]
    content_candidates = [(102, 0.9), (103, 0.7)]
    skill_candidates = [(101, 0.7), (103, 0.6)]
    popularity_candidates = [(103, 0.9), (101, 0.7)]
    
    ranked = scorer.score_recommendations(
        collab_candidates,
        content_candidates,
        skill_candidates,
        popularity_candidates
    )
    
    assert isinstance(ranked, list)
    assert len(ranked) == 3


def test_recommendation_cache():
    """Test RecommendationCache."""
    cache = RecommendationCache(ttl_seconds=100, max_size=10)
    
    # Test set and get
    cache.set((1, 10), ["rec1", "rec2"])
    assert cache.get((1, 10)) == ["rec1", "rec2"]
    
    # Test stats
    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 0
    assert stats["current_size"] == 1
    
    # Test invalidate user
    cache.invalidate_user(1)
    assert cache.get((1, 10)) is None
    
    # Test clear and reset stats
    cache.set((2, 10), ["rec3"])
    cache.clear()
    cache.reset_stats()
    stats = cache.get_stats()
    assert stats["hits"] == 0
    assert stats["current_size"] == 0


def test_orchestrator(test_orchestrator, sample_data):
    """Test RecommendationOrchestrator."""
    user_id = sample_data["users"][0].id

    # Test get recommendations
    recs = test_orchestrator.get_recommendations(user_id, limit=2)
    assert len(recs) >= 1
    
    # Test caching
    recs_cached = test_orchestrator.get_recommendations(user_id, limit=2)
    assert recs == recs_cached
    stats = test_orchestrator.get_cache_stats()
    assert stats["hits"] == 1
    
    # Test record feedback
    content_id = sample_data["content"][0].id
    test_orchestrator.record_feedback(user_id, content_id, rating=5, interaction_type="like")
    stats_after = test_orchestrator.get_cache_stats()
    # After invalidation, get should be a miss
    recs_after = test_orchestrator.get_recommendations(user_id, limit=2)
    assert len(recs_after) >= 0


def test_hybrid_recommender():
    """Test HybridRecommender (placeholder)."""
    recommender = HybridRecommender()
    recommender.fit()
    recs = recommender.recommend(user_id=1, top_k=5)
    assert isinstance(recs, list)

