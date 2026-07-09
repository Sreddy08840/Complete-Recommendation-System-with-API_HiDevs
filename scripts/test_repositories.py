
"""Test script for repository classes."""
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Base, engine, SessionLocal
from data.repository import (
    UserRepository,
    ContentRepository,
    SkillRepository,
    UserSkillRepository,
    ContentSkillRepository,
    InteractionRepository,
)


def init_test_db():
    """Initialize test database."""
    Base.metadata.create_all(bind=engine)
    print("Test database initialized")


def test_repositories():
    """Test all repository methods."""
    db = SessionLocal()
    try:
        # Initialize repositories
        user_repo = UserRepository(db)
        content_repo = ContentRepository(db)
        skill_repo = SkillRepository(db)
        user_skill_repo = UserSkillRepository(db)
        content_skill_repo = ContentSkillRepository(db)
        interaction_repo = InteractionRepository(db)

        # Test UserRepository
        print("\nTesting UserRepository...")
        user = user_repo.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpass123"
        )
        print(f"Created user: {user.username} (ID: {user.id})")

        retrieved_user = user_repo.get_user(user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"
        print("get_user() works")

        all_users = user_repo.get_all_users()
        assert len(all_users) >= 1
        print("get_all_users() works")

        # Test ContentRepository
        print("\nTesting ContentRepository...")
        content = content_repo.create(
            title="Test Content",
            description="This is a test content item"
        )
        print(f"Created content: {content.title} (ID: {content.id})")

        # Test SkillRepository
        print("\nTesting SkillRepository...")
        skill = skill_repo.create(
            name="Python",
            description="Python programming language"
        )
        print(f"Created skill: {skill.name} (ID: {skill.id})")

        # Test UserSkillRepository
        print("\nTesting UserSkillRepository...")
        user_skill = user_skill_repo.create(
            user_id=user.id,
            skill_id=skill.id,
            proficiency=0.8
        )
        print(f"Created user-skill association: User {user.id} -> Skill {skill.id}")

        # Test ContentSkillRepository
        print("\nTesting ContentSkillRepository...")
        content_skill = content_skill_repo.create(
            content_id=content.id,
            skill_id=skill.id,
            relevance=0.9
        )
        print(f"Created content-skill association: Content {content.id} -> Skill {skill.id}")

        # Test ContentRepository helper method
        content_by_skill = content_repo.get_content_by_skill(skill.id)
        assert len(content_by_skill) >= 1
        print("get_content_by_skill() works")

        # Test InteractionRepository
        print("\nTesting InteractionRepository...")
        interaction = interaction_repo.record_feedback(
            user_id=user.id,
            content_id=content.id,
            rating=4.5,
            interaction_type="view"
        )
        print(f"Recorded feedback: {interaction.interaction_type} (Rating: {interaction.rating})")

        # Test UserRepository helper method
        user_history = user_repo.get_user_history(user.id)
        assert len(user_history) >= 1
        print("get_user_history() works")

        print("\nAll repository tests passed!")

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    init_test_db()
    test_repositories()
