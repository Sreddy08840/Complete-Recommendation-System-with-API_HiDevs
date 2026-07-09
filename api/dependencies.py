
import sys
import os
from typing import Generator
from .config import settings

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.orchestrator import RecommendationOrchestrator

# Singleton instance of RecommendationOrchestrator
_orchestrator: RecommendationOrchestrator | None = None


def get_orchestrator() -> RecommendationOrchestrator:
    """Dependency injection to get the singleton RecommendationOrchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RecommendationOrchestrator()
        _orchestrator.load_database_data()
    return _orchestrator

