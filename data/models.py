
"""SQLAlchemy ORM models for the recommendation system."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base


class User(Base):
    """User model representing system users."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user_skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction", back_populates="user", cascade="all, delete-orphan"
    )


class Content(Base):
    """Content model representing recommendable content items."""
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    content_skills: Mapped[List["ContentSkill"]] = relationship(
        "ContentSkill", back_populates="content", cascade="all, delete-orphan"
    )
    interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction", back_populates="content", cascade="all, delete-orphan"
    )


class Skill(Base):
    """Skill model representing skills/tags for users and content."""
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="skill", cascade="all, delete-orphan"
    )
    content_skills: Mapped[List["ContentSkill"]] = relationship(
        "ContentSkill", back_populates="skill", cascade="all, delete-orphan"
    )


class UserSkill(Base):
    """Association model between User and Skill."""
    __tablename__ = "user_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 to 1.0
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="user_skills")

    # Unique constraint to prevent duplicate user-skill pairs
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="_user_skill_uc"),)


class ContentSkill(Base):
    """Association model between Content and Skill."""
    __tablename__ = "content_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content_id: Mapped[int] = mapped_column(Integer, ForeignKey("contents.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)
    relevance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 to 1.0
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    content: Mapped["Content"] = relationship("Content", back_populates="content_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="content_skills")

    # Unique constraint to prevent duplicate content-skill pairs
    __table_args__ = (UniqueConstraint("content_id", "skill_id", name="_content_skill_uc"),)


class Interaction(Base):
    """Interaction model representing user-content interactions."""
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    content_id: Mapped[int] = mapped_column(Integer, ForeignKey("contents.id"), nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # e.g., 1.0 to 5.0
    interaction_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # e.g., "view", "like", "share"
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="interactions")
    content: Mapped["Content"] = relationship("Content", back_populates="interactions")

    # Unique constraint to prevent duplicate user-content pairs (optional, depending on requirements)
    __table_args__ = (UniqueConstraint("user_id", "content_id", name="_user_content_uc"),)
