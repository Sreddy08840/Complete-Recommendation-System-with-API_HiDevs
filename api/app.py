
"""
FastAPI Application for Recommendation System
Endpoints:
- GET /health
- GET /recommend/{user_id}
- POST /feedback
- GET /metrics
"""
import logging
from fastapi import FastAPI, Depends, Path
from typing import List
from .config import settings
from .dependencies import get_orchestrator
from .schemas import (
    RecommendationItem,
    RecommendationResponse,
    FeedbackCreate,
    MetricsResponse
)
from .logging_config import setup_logging
from .middleware import RequestLoggingMiddleware
from .routers import users, content, skills, interactions, recommendations
from engine.orchestrator import RecommendationOrchestrator

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Recommendation System API",
    description="A complete recommendation system with collaborative filtering, content-based filtering, skill matching, and popularity-based recommendations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(users.router)
app.include_router(content.router)
app.include_router(skills.router)
app.include_router(interactions.router)
app.include_router(recommendations.router)


@app.get("/health", tags=["Health"], summary="Health check endpoint")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}


@app.get(
    "/recommend/{user_id}",
    tags=["Recommendations"],
    summary="Get recommendations for a user",
    response_model=RecommendationResponse
)
async def get_recommendations(
    user_id: int = Path(..., ge=1, description="The ID of the user to get recommendations for"),
    limit: int = 10,
    orchestrator: RecommendationOrchestrator = Depends(get_orchestrator)
):
    """
    Get personalized recommendations for a given user ID.

    Parameters:
        user_id: User ID (must be >= 1)
        limit: Number of recommendations to return (default 10, max 100)
        orchestrator: Injected RecommendationOrchestrator instance

    Returns:
        RecommendationResponse with list of recommendations and explanations
    """
    # Clamp limit to between 1 and 100
    limit = max(1, min(100, limit))

    # Get recommendations from orchestrator
    rec_list = orchestrator.get_recommendations(user_id, limit=limit)

    # Convert to RecommendationItem list
    recommendation_items: List[RecommendationItem] = [
        RecommendationItem(
            id=rec["id"],
            title=rec["title"],
            description=rec["description"],
            explanations=rec["explanations"]
        )
        for rec in rec_list
    ]

    return RecommendationResponse(
        user_id=user_id,
        recommendations=recommendation_items
    )


@app.post(
    "/feedback",
    tags=["Feedback"],
    summary="Record user feedback"
)
async def record_feedback(
    feedback: FeedbackCreate,
    orchestrator: RecommendationOrchestrator = Depends(get_orchestrator)
):
    """
    Record user feedback/interaction with content.

    Parameters:
        feedback: FeedbackCreate schema
        orchestrator: Injected RecommendationOrchestrator instance
    """
    orchestrator.record_feedback(
        user_id=feedback.user_id,
        content_id=feedback.content_id,
        rating=feedback.rating,
        interaction_type=feedback.interaction_type
    )
    return {"status": "success", "message": "Feedback recorded successfully"}


@app.get(
    "/metrics",
    tags=["Metrics"],
    summary="Get cache and system metrics",
    response_model=MetricsResponse
)
async def get_metrics(
    orchestrator: RecommendationOrchestrator = Depends(get_orchestrator)
):
    """
    Get system metrics including cache statistics.

    Parameters:
        orchestrator: Injected RecommendationOrchestrator instance
    """
    cache_stats = orchestrator.get_cache_stats()
    return MetricsResponse(
        cache_hits=cache_stats["hits"],
        cache_misses=cache_stats["misses"],
        cache_current_size=cache_stats["current_size"],
        cache_max_size=cache_stats["max_size"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
