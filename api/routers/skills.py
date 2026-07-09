
"""API routes for Skill operations."""
from fastapi import APIRouter
from typing import List
from ..schemas import Skill, SkillCreate

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=List[Skill])
async def get_skills():
    """Get all skills."""
    return []


@router.post("/", response_model=Skill)
async def create_skill(skill: SkillCreate):
    """Create a new skill."""
    return skill
