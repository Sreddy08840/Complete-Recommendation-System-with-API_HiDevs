
"""API routes for Interaction operations."""
from fastapi import APIRouter
from typing import List
from ..schemas import Interaction, InteractionCreate

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.get("/", response_model=List[Interaction])
async def get_interactions():
    """Get all interactions."""
    return []


@router.post("/", response_model=Interaction)
async def create_interaction(interaction: InteractionCreate):
    """Create a new interaction."""
    return interaction
