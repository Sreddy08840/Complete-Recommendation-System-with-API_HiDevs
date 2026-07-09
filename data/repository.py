
"""Repository classes for database operations with full CRUD and helper methods."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from .models import (
    User,
    Content,
    Skill,
    UserSkill,
    ContentSkill,
    Interaction,
)


class UserRepository:
    """Repository for User model operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ============ CRUD Methods ============
    def create(self, username: str, email: str, hashed_password: str) -> User:
        """Create a new user."""
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_all(self) -> List[User]:
        """Get all users from the database."""
        return self.db.query(User).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by their ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email."""
        return self.db.query(User).filter(User.email == email).first()

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update a user's details."""
        db_user = self.get_by_id(user_id)
        if db_user:
            for key, value in kwargs.items():
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
            db_user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        """Delete a user by ID. Returns True if successful, False otherwise."""
        db_user = self.get_by_id(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    # ============ Helper Methods ============
    def get_user(self, user_id: int) -> Optional[User]:
        """Alias for get_by_id to match the requirement."""
        return self.get_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """Alias for get_all to match the requirement."""
        return self.get_all()

    def get_user_history(self, user_id: int) -> List[Interaction]:
        """Get a user's interaction history with content, ordered by most recent."""
        return (
            self.db.query(Interaction)
            .options(joinedload(Interaction.content))
            .filter(Interaction.user_id == user_id)
            .order_by(Interaction.created_at.desc())
            .all()
        )


class ContentRepository:
    """Repository for Content model operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ============ CRUD Methods ============
    def create(self, title: str, description: Optional[str] = None) -> Content:
        """Create a new content item."""
        db_content = Content(
            title=title,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)
        return db_content

    def get_all(self) -> List[Content]:
        """Get all content items from the database."""
        return self.db.query(Content).all()

    def get_by_id(self, content_id: int) -> Optional[Content]:
        """Get a content item by its ID."""
        return self.db.query(Content).filter(Content.id == content_id).first()

    def update(self, content_id: int, **kwargs) -> Optional[Content]:
        """Update a content item's details."""
        db_content = self.get_by_id(content_id)
        if db_content:
            for key, value in kwargs.items():
                if hasattr(db_content, key):
                    setattr(db_content, key, value)
            db_content.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_content)
        return db_content

    def delete(self, content_id: int) -> bool:
        """Delete a content item by ID. Returns True if successful, False otherwise."""
        db_content = self.get_by_id(content_id)
        if db_content:
            self.db.delete(db_content)
            self.db.commit()
            return True
        return False

    # ============ Helper Methods ============
    def get_content_by_skill(self, skill_id: int) -> List[Content]:
        """Get all content items associated with a specific skill."""
        return (
            self.db.query(Content)
            .join(ContentSkill, ContentSkill.content_id == Content.id)
            .filter(ContentSkill.skill_id == skill_id)
            .all()
        )


class SkillRepository:
    """Repository for Skill model operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ============ CRUD Methods ============
    def create(self, name: str, description: Optional[str] = None) -> Skill:
        """Create a new skill."""
        db_skill = Skill(
            name=name,
            description=description,
            created_at=datetime.utcnow(),
        )
        self.db.add(db_skill)
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill

    def get_all(self) -> List[Skill]:
        """Get all skills from the database."""
        return self.db.query(Skill).all()

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        """Get a skill by its ID."""
        return self.db.query(Skill).filter(Skill.id == skill_id).first()

    def get_by_name(self, name: str) -> Optional[Skill]:
        """Get a skill by its name."""
        return self.db.query(Skill).filter(Skill.name == name).first()

    def update(self, skill_id: int, **kwargs) -> Optional[Skill]:
        """Update a skill's details."""
        db_skill = self.get_by_id(skill_id)
        if db_skill:
            for key, value in kwargs.items():
                if hasattr(db_skill, key):
                    setattr(db_skill, key, value)
            self.db.commit()
            self.db.refresh(db_skill)
        return db_skill

    def delete(self, skill_id: int) -> bool:
        """Delete a skill by ID. Returns True if successful, False otherwise."""
        db_skill = self.get_by_id(skill_id)
        if db_skill:
            self.db.delete(db_skill)
            self.db.commit()
            return True
        return False


class UserSkillRepository:
    """Repository for UserSkill model operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ============ CRUD Methods ============
    def create(
        self, user_id: int, skill_id: int, proficiency: Optional[float] = None
    ) -> UserSkill:
        """Create a new user-skill association."""
        db_user_skill = UserSkill(
            user_id=user_id,
            skill_id=skill_id,
            proficiency=proficiency,
            created_at=datetime.utcnow(),
        )
        self.db.add(db_user_skill)
        self.db.commit()
        self.db.refresh(db_user_skill)
        return db_user_skill

    def get_all(self) -> List[UserSkill]:
        """Get all user-skill associations from the database."""
        return self.db.query(UserSkill).all()

    def get_by_user_and_skill(
        self, user_id: int, skill_id: int
    ) -> Optional[UserSkill]:
        """Get a user-skill association by user ID and skill ID."""
        return (
            self.db.query(UserSkill)
            .filter(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
            .first()
        )

    def get_by_user(self, user_id: int) -> List[UserSkill]:
        """Get all skills for a specific user."""
        return (
            self.db.query(UserSkill)
            .options(joinedload(UserSkill.skill))
            .filter(UserSkill.user_id == user_id)
            .all()
        )

    def update(
        self, user_id: int, skill_id: int, **kwargs
    ) -> Optional[UserSkill]:
        """Update a user-skill association's details."""
        db_user_skill = self.get_by_user_and_skill(user_id, skill_id)
        if db_user_skill:
            for key, value in kwargs.items():
                if hasattr(db_user_skill, key):
                    setattr(db_user_skill, key, value)
            self.db.commit()
            self.db.refresh(db_user_skill)
        return db_user_skill

    def delete(self, user_id: int, skill_id: int) -> bool:
        """Delete a user-skill association. Returns True if successful, False otherwise."""
        db_user_skill = self.get_by_user_and_skill(user_id, skill_id)
        if db_user_skill:
            self.db.delete(db_user_skill)
            self.db.commit()
            return True
        return False


class ContentSkillRepository:
    """Repository for ContentSkill model operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ============ CRUD Methods ============
    def create(
        self, content_id: int, skill_id: int, relevance: Optional[float] = None
    ) -> ContentSkill:
        """Create a new content-skill association."""
        db_content_skill = ContentSkill(
            content_id=content_id,
            skill_id=skill_id,
            relevance=relevance,
            created_at=datetime.utcnow(),
        )
        self.db.add(db_content_skill)
        self.db.commit()
        self.db.refresh(db_content_skill)
        return db_content_skill

    def get_all(self) -> List[ContentSkill]:
        """Get all content-skill associations from the database."""
        return self.db.query(ContentSkill).all()

    def get_by_content_and_skill(
        self, content_id: int, skill_id: int
    ) -> Optional[ContentSkill]:
        """Get a content-skill association by content ID and skill ID."""
        return (
            self.db.query(ContentSkill)
            .filter(
                ContentSkill.content_id == content_id,
                ContentSkill.skill_id == skill_id,
            )
            .first()
        )

    def get_by_content(self, content_id: int) -> List[ContentSkill]:
        """Get all skills for a specific content item."""
        return (
            self.db.query(ContentSkill)
            .options(joinedload(ContentSkill.skill))
            .filter(ContentSkill.content_id == content_id)
            .all()
        )

    def update(
        self, content_id: int, skill_id: int, **kwargs
    ) -> Optional[ContentSkill]:
        """Update a content-skill association's details."""
        db_content_skill = self.get_by_content_and_skill(content_id, skill_id)
        if db_content_skill:
            for key, value in kwargs.items():
                if hasattr(db_content_skill, key):
                    setattr(db_content_skill, key, value)
            self.db.commit()
            self.db.refresh(db_content_skill)
        return db_content_skill

    def delete(self, content_id: int, skill_id: int) -> bool:
        """Delete a content-skill association. Returns True if successful, False otherwise."""
        db_content_skill = self.get_by_content_and_skill(content_id, skill_id)
        if db_content_skill:
            self.db.delete(db_content_skill)
            self.db.commit()
            return True
        return False


class InteractionRepository:
    """Repository for Interaction model operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ============ CRUD Methods ============
    def create(
        self,
        user_id: int,
        content_id: int,
        rating: Optional[float] = None,
        interaction_type: Optional[str] = None,
    ) -> Interaction:
        """Create a new user-content interaction."""
        db_interaction = Interaction(
            user_id=user_id,
            content_id=content_id,
            rating=rating,
            interaction_type=interaction_type,
            created_at=datetime.utcnow(),
        )
        self.db.add(db_interaction)
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction

    def get_all(self) -> List[Interaction]:
        """Get all interactions from the database."""
        return self.db.query(Interaction).all()

    def get_by_user_and_content(
        self, user_id: int, content_id: int
    ) -> Optional[Interaction]:
        """Get an interaction by user ID and content ID."""
        return (
            self.db.query(Interaction)
            .filter(
                Interaction.user_id == user_id,
                Interaction.content_id == content_id,
            )
            .first()
        )

    def get_by_user(self, user_id: int) -> List[Interaction]:
        """Get all interactions for a specific user."""
        return (
            self.db.query(Interaction)
            .filter(Interaction.user_id == user_id)
            .order_by(Interaction.created_at.desc())
            .all()
        )

    def update(
        self, user_id: int, content_id: int, **kwargs
    ) -> Optional[Interaction]:
        """Update an interaction's details."""
        db_interaction = self.get_by_user_and_content(user_id, content_id)
        if db_interaction:
            for key, value in kwargs.items():
                if hasattr(db_interaction, key):
                    setattr(db_interaction, key, value)
            self.db.commit()
            self.db.refresh(db_interaction)
        return db_interaction

    def delete(self, user_id: int, content_id: int) -> bool:
        """Delete an interaction. Returns True if successful, False otherwise."""
        db_interaction = self.get_by_user_and_content(user_id, content_id)
        if db_interaction:
            self.db.delete(db_interaction)
            self.db.commit()
            return True
        return False

    # ============ Helper Methods ============
    def record_feedback(
        self,
        user_id: int,
        content_id: int,
        rating: Optional[float] = None,
        interaction_type: Optional[str] = None,
    ) -> Interaction:
        """
        Record user feedback/interaction with content.
        If an interaction already exists, update it; otherwise, create a new one.
        """
        existing_interaction = self.get_by_user_and_content(user_id, content_id)
        if existing_interaction:
            return self.update(
                user_id=user_id,
                content_id=content_id,
                rating=rating,
                interaction_type=interaction_type,
            )
        return self.create(
            user_id=user_id,
            content_id=content_id,
            rating=rating,
            interaction_type=interaction_type,
        )
