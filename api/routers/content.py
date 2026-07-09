
"""API routes for Content operations."""
from fastapi import APIRouter
from typing import List
from ..schemas import Content, ContentCreate

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/", response_model=List[Content])
async def get_content():
    """Get all content items."""
    return []


@router.post("/", response_model=Content)
async def create_content(content: ContentCreate):
    """Create new content."""
    return content
