
"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ============ User Schemas ============
class UserBase(BaseModel):
    """Base schema for User model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new User."""
    password: str = Field(..., min_length=8)


class User(UserBase):
    """Schema for returning User data."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Content Schemas ============
class ContentBase(BaseModel):
    """Base schema for Content model."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ContentCreate(ContentBase):
    """Schema for creating new Content."""
    pass


class Content(ContentBase):
    """Schema for returning Content data."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Skill Schemas ============
class SkillBase(BaseModel):
    """Base schema for Skill model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class SkillCreate(SkillBase):
    """Schema for creating a new Skill."""
    pass


class Skill(SkillBase):
    """Schema for returning Skill data."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ UserSkill Schemas ============
class UserSkillBase(BaseModel):
    """Base schema for UserSkill model."""
    user_id: int
    skill_id: int
    proficiency: Optional[float] = Field(None, ge=0.0, le=1.0)


class UserSkillCreate(UserSkillBase):
    """Schema for creating a new UserSkill."""
    pass


class UserSkill(UserSkillBase):
    """Schema for returning UserSkill data."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ ContentSkill Schemas ============
class ContentSkillBase(BaseModel):
    """Base schema for ContentSkill model."""
    content_id: int
    skill_id: int
    relevance: Optional[float] = Field(None, ge=0.0, le=1.0)


class ContentSkillCreate(ContentSkillBase):
    """Schema for creating a new ContentSkill."""
    pass


class ContentSkill(ContentSkillBase):
    """Schema for returning ContentSkill data."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Interaction Schemas ============
class InteractionBase(BaseModel):
    """Base schema for Interaction model."""
    user_id: int
    content_id: int
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    interaction_type: Optional[str] = None


class InteractionCreate(InteractionBase):
    """Schema for creating a new Interaction."""
    pass


class Interaction(InteractionBase):
    """Schema for returning Interaction data."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Recommendation Schemas ============
class RecommendationRequest(BaseModel):
    """Schema for recommendation requests."""
    user_id: int
    top_k: int = Field(10, ge=1, le=100)


class RecommendationItem(BaseModel):
    """Schema for a single recommended item."""
    id: int
    title: str
    description: Optional[str]
    explanations: List[str]


class RecommendationResponse(BaseModel):
    """Schema for recommendation responses."""
    user_id: int
    recommendations: List[RecommendationItem]


class FeedbackCreate(BaseModel):
    """Schema for creating feedback (interaction)."""
    user_id: int
    content_id: int
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    interaction_type: Optional[str] = None


class MetricsResponse(BaseModel):
    """Schema for cache and API metrics."""
    cache_hits: int
    cache_misses: int
    cache_current_size: int
    cache_max_size: int
