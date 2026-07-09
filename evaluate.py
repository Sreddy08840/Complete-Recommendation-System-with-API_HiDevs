
"""
Recommendation System Evaluation Script
Computes:
- Precision@5
- Recall@5
- NDCG@5
- Coverage
- Diversity
- Novelty
Generates:
- Markdown report
- Matplotlib bar chart
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Set, Tuple

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from data.database import SessionLocal
from data.repository import (
    UserRepository,
    ContentRepository,
    InteractionRepository,
    UserSkillRepository,
    ContentSkillRepository
)
from engine.orchestrator import RecommendationOrchestrator


def precision_at_k(recommended: List[int], relevant: Set[int], k: int = 5) -> float:
    """
    Compute Precision@k: fraction of top-k recommended items that are relevant
    """
    if not recommended:
        return 0.0
    top_k = recommended[:k]
    relevant_count = sum(1 for item in top_k if item in relevant)
    return relevant_count / k


def recall_at_k(recommended: List[int], relevant: Set[int], k: int = 5) -> float:
    """
    Compute Recall@k: fraction of relevant items that are in top-k recommendations
    """
    if not recommended or not relevant:
        return 0.0
    top_k = recommended[:k]
    relevant_count = sum(1 for item in top_k if item in relevant)
    return relevant_count / len(relevant)


def dcg_at_k(recommended: List[int], relevant_scores: Dict[int, float], k: int = 5) -> float:
    """
    Compute Discounted Cumulative Gain at k
    """
    dcg = 0.0
    for i in range(min(k, len(recommended))):
        item = recommended[i]
        rel = relevant_scores.get(item, 0.0)
        dcg += rel / np.log2(i + 2)  # i starts at 0, denominator is log2(i+2)
    return dcg


def ndcg_at_k(recommended: List[int], relevant_scores: Dict[int, float], k: int = 5) -> float:
    """
    Compute Normalized Discounted Cumulative Gain at k
    """
    # Compute ideal DCG
    ideal_recommended = sorted(relevant_scores.items(), key=lambda x: x[1], reverse=True)
    ideal_recommended = [item for item, _ in ideal_recommended]
    idcg = dcg_at_k(ideal_recommended, relevant_scores, k)
    
    if idcg == 0:
        return 0.0
    
    dcg = dcg_at_k(recommended, relevant_scores, k)
    return dcg / idcg


def coverage(recommended_lists: List[List[int]], all_items: Set[int]) -> float:
    """
    Compute Coverage: fraction of all items that appear in any recommendation list
    """
    recommended_items = set()
    for rec_list in recommended_lists:
        recommended_items.update(rec_list)
    return len(recommended_items) / len(all_items) if all_items else 0.0


def diversity(recommended: List[int], item_features: Dict[int, Set[int]]) -> float:
    """
    Compute Diversity: average pairwise Jaccard distance between items' features in recommendation list
    """
    if len(recommended) < 2:
        return 0.0
    
    total_distance = 0.0
    pair_count = 0
    
    for i in range(len(recommended)):
        for j in range(i + 1, len(recommended)):
            item1 = recommended[i]
            item2 = recommended[j]
            features1 = item_features.get(item1, set())
            features2 = item_features.get(item2, set())
            
            # Compute Jaccard distance
            intersection = len(features1 & features2)
            union = len(features1 | features2)
            jaccard_sim = intersection / union if union != 0 else 0.0
            jaccard_dist = 1 - jaccard_sim
            
            total_distance += jaccard_dist
            pair_count += 1
    
    return total_distance / pair_count if pair_count > 0 else 0.0


def novelty(recommended: List[int], item_popularity: Dict[int, int], total_interactions: int) -> float:
    """
    Compute Novelty: average inverse log popularity of recommended items
    """
    if not recommended:
        return 0.0
    
    total_novelty = 0.0
    for item in recommended:
        # Popularity is number of interactions
        pop = item_popularity.get(item, 1)
        # Inverse log popularity
        novelty_score = 1 / np.log2(pop + 1)  # +1 to avoid log(1) = 0 for pop=1
        total_novelty += novelty_score
    
    return total_novelty / len(recommended)


def main():
    """
    Main evaluation function
    """
    print("Starting evaluation...")
    
    # Load data
    with SessionLocal() as db:
        user_repo = UserRepository(db)
        content_repo = ContentRepository(db)
        interaction_repo = InteractionRepository(db)
        user_skill_repo = UserSkillRepository(db)
        content_skill_repo = ContentSkillRepository(db)
        
        users = user_repo.get_all()
        contents = content_repo.get_all()
        
        # Prepare data structures
        user_relevant_items: Dict[int, Set[int]] = {}
        user_relevant_scores: Dict[int, Dict[int, float]] = {}
        all_items = set(content.id for content in contents)
        item_features: Dict[int, Set[int]] = {}
        item_popularity: Dict[int, int] = {}
        
        # Build item features
        for content in contents:
            skills = content_skill_repo.get_by_content(content.id)
            item_features[content.id] = set(skill.skill_id for skill in skills)
        
        # Build user relevant items and scores
        for user in users:
            interactions = interaction_repo.get_by_user(user.id)
            relevant = set()
            scores = {}
            for interaction in interactions:
                relevant.add(interaction.content_id)
                # Use rating or interaction type as score; default to 1
                scores[interaction.content_id] = interaction.rating if interaction.rating else 1.0
                # Update item popularity
                item_popularity[interaction.content_id] = item_popularity.get(interaction.content_id, 0) + 1
            
            user_relevant_items[user.id] = relevant
            user_relevant_scores[user.id] = scores
        
        # Compute total interactions for novelty
        total_interactions = sum(item_popularity.values())
    
    # Load orchestrator and get recommendations for all users
    orchestrator = RecommendationOrchestrator()
    orchestrator.load_database_data()
    
    all_recommended_lists: List[List[int]] = []
    precision_scores: List[float] = []
    recall_scores: List[float] = []
    ndcg_scores: List[float] = []
    diversity_scores: List[float] = []
    novelty_scores: List[float] = []
    
    k = 5  # Evaluate at 5
    
    for user in users:
        recommendations = orchestrator.get_recommendations(user.id, limit=k)
        recommended_item_ids = [rec["id"] for rec in recommendations]
        
        all_recommended_lists.append(recommended_item_ids)
        
        # Compute metrics for this user
        relevant = user_relevant_items.get(user.id, set())
        relevant_scores = user_relevant_scores.get(user.id, {})
        
        precision_scores.append(precision_at_k(recommended_item_ids, relevant, k))
        recall_scores.append(recall_at_k(recommended_item_ids, relevant, k))
        ndcg_scores.append(ndcg_at_k(recommended_item_ids, relevant_scores, k))
        diversity_scores.append(diversity(recommended_item_ids, item_features))
        novelty_scores.append(novelty(recommended_item_ids, item_popularity, total_interactions))
    
    # Aggregate metrics
    avg_precision = np.mean(precision_scores)
    avg_recall = np.mean(recall_scores)
    avg_ndcg = np.mean(ndcg_scores)
    overall_coverage = coverage(all_recommended_lists, all_items)
    avg_diversity = np.mean(diversity_scores)
    avg_novelty = np.mean(novelty_scores)
    
    # Print metrics
    print("\nEvaluation Metrics:")
    print(f"Precision@{k}: {avg_precision:.4f}")
    print(f"Recall@{k}: {avg_recall:.4f}")
    print(f"NDCG@{k}: {avg_ndcg:.4f}")
    print(f"Coverage: {overall_coverage:.4f}")
    print(f"Diversity: {avg_diversity:.4f}")
    print(f"Novelty: {avg_novelty:.4f}")
    
    # Generate markdown report
    report_content = f"""# Recommendation System Evaluation Report
Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Evaluation Metrics (k=5)
| Metric          | Value  |
|-----------------|--------|
| Precision@5     | {avg_precision:.4f} |
| Recall@5        | {avg_recall:.4f} |
| NDCG@5          | {avg_ndcg:.4f} |
| Coverage        | {overall_coverage:.4f} |
| Diversity       | {avg_diversity:.4f} |
| Novelty         | {avg_novelty:.4f} |

## Summary
This report summarizes the performance of the recommendation system using standard information retrieval metrics.
"""
    report_path = os.path.join(project_root, "evaluation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"\nMarkdown report generated at: {report_path}")
    
    # Generate matplotlib bar chart
    metrics = ["Precision@5", "Recall@5", "NDCG@5", "Coverage", "Diversity", "Novelty"]
    values = [avg_precision, avg_recall, avg_ndcg, overall_coverage, avg_diversity, avg_novelty]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(metrics, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
    plt.title("Recommendation System Evaluation Metrics")
    plt.xlabel("Metric")
    plt.ylabel("Score")
    plt.ylim(0, 1.1)  # Set y-axis limit to 1.1 for better visibility
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.4f}',
                 ha='center', va='bottom')
    
    plt.tight_layout()
    chart_path = os.path.join(project_root, "evaluation_metrics_chart.png")
    plt.savefig(chart_path, dpi=300)
    print(f"Bar chart generated at: {chart_path}")
    plt.close()
    print("Evaluation complete!")


if __name__ == "__main__":
    main()
