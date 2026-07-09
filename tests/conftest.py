
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.database import Base
from data.repository import (
    UserRepository,
    ContentRepository,
    SkillRepository,
    UserSkillRepository,
    ContentSkillRepository,
    InteractionRepository
)
from api.app import app as fastapi_app
from api.dependencies import get_orchestrator
from engine.orchestrator import RecommendationOrchestrator


# Create in-memory SQLite engine for testing
@pytest.fixture(scope="function")
def db_session():
    """Fixture for database session using in-memory SQLite."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def sample_data(db_session):
    """Fixture to create sample test data."""
    # Create users
    user_repo = UserRepository(db_session)
    user1 = user_repo.create(username="testuser1", email="test1@example.com", hashed_password="hashed1")
    user2 = user_repo.create(username="testuser2", email="test2@example.com", hashed_password="hashed2")

    # Create content
    content_repo = ContentRepository(db_session)
    content1 = content_repo.create(title="Test Content 1", description="Desc 1")
    content2 = content_repo.create(title="Test Content 2", description="Desc 2")
    content3 = content_repo.create(title="Test Content 3", description="Desc 3")

    # Create skills
    skill_repo = SkillRepository(db_session)
    skill1 = skill_repo.create(name="Python", description="Python programming")
    skill2 = skill_repo.create(name="FastAPI", description="FastAPI framework")
    skill3 = skill_repo.create(name="SQLAlchemy", description="SQLAlchemy ORM")

    # Create user skills
    user_skill_repo = UserSkillRepository(db_session)
    user_skill_repo.create(user_id=user1.id, skill_id=skill1.id, proficiency=0.9)
    user_skill_repo.create(user_id=user1.id, skill_id=skill2.id, proficiency=0.8)
    user_skill_repo.create(user_id=user2.id, skill_id=skill2.id, proficiency=0.7)

    # Create content skills
    content_skill_repo = ContentSkillRepository(db_session)
    content_skill_repo.create(content_id=content1.id, skill_id=skill1.id, relevance=0.9)
    content_skill_repo.create(content_id=content1.id, skill_id=skill2.id, relevance=0.8)
    content_skill_repo.create(content_id=content2.id, skill_id=skill2.id, relevance=0.9)
    content_skill_repo.create(content_id=content2.id, skill_id=skill3.id, relevance=0.7)
    content_skill_repo.create(content_id=content3.id, skill_id=skill1.id, relevance=0.8)

    # Create interactions
    interaction_repo = InteractionRepository(db_session)
    interaction_repo.create(user_id=user1.id, content_id=content1.id, rating=5, interaction_type="like")
    interaction_repo.create(user_id=user1.id, content_id=content2.id, rating=4, interaction_type="view")
    interaction_repo.create(user_id=user2.id, content_id=content2.id, rating=5, interaction_type="like")
    interaction_repo.create(user_id=user2.id, content_id=content3.id, rating=3, interaction_type="view")

    return {
        "users": [user1, user2],
        "content": [content1, content2, content3],
        "skills": [skill1, skill2, skill3]
    }


@pytest.fixture(scope="function")
def test_orchestrator(db_session, sample_data):
    """Fixture for RecommendationOrchestrator with test data."""
    orchestrator = RecommendationOrchestrator(cache_ttl_seconds=10)
    
    # Manually load data from test db instead of using load_database_data()
    user_repo = UserRepository(db_session)
    content_repo = ContentRepository(db_session)
    user_skill_repo = UserSkillRepository(db_session)
    content_skill_repo = ContentSkillRepository(db_session)
    interaction_repo = InteractionRepository(db_session)
    
    for user in user_repo.get_all():
        orchestrator.user_details[user.id] = {"username": user.username, "email": user.email}
    
    for content in content_repo.get_all():
        orchestrator.item_details[content.id] = {"title": content.title, "description": content.description}
        orchestrator.item_popularity[content.id] = 0
    
    for us in user_skill_repo.get_all():
        orchestrator.user_skills[us.user_id].append(us.skill_id)
    
    for cs in content_skill_repo.get_all():
        orchestrator.item_skills[cs.content_id].append(cs.skill_id)
        orchestrator.item_features[cs.content_id].append(cs.skill_id)
    
    for interaction in interaction_repo.get_all():
        orchestrator.user_interactions[interaction.user_id].append(interaction.content_id)
        orchestrator.item_popularity[interaction.content_id] += 1
    
    orchestrator.loaded = True
    return orchestrator


@pytest.fixture(scope="function")
def client(test_orchestrator):
    """Fixture for TestClient with overridden orchestrator dependency."""
    def override_get_orchestrator():
        return test_orchestrator
    
    fastapi_app.dependency_overrides[get_orchestrator] = override_get_orchestrator
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()

