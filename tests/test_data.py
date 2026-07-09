
import pytest
from data.repository import (
    UserRepository,
    ContentRepository,
    SkillRepository,
    UserSkillRepository,
    ContentSkillRepository,
    InteractionRepository
)


def test_user_repository(db_session):
    """Test UserRepository CRUD operations."""
    repo = UserRepository(db_session)
    
    # Create
    user = repo.create(username="testuser", email="test@example.com", hashed_password="hashedpass")
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    
    # Get by ID
    retrieved = repo.get_by_id(user.id)
    assert retrieved is not None
    assert retrieved.username == "testuser"
    
    # Get by username
    by_username = repo.get_by_username("testuser")
    assert by_username is not None
    assert by_username.id == user.id
    
    # Get by email
    by_email = repo.get_by_email("test@example.com")
    assert by_email is not None
    assert by_email.id == user.id
    
    # Get all
    all_users = repo.get_all()
    assert len(all_users) == 1
    
    # Update
    updated = repo.update(user.id, username="updateduser")
    assert updated is not None
    assert updated.username == "updateduser"
    
    # Delete
    deleted = repo.delete(user.id)
    assert deleted is True
    assert repo.get_by_id(user.id) is None


def test_content_repository(db_session):
    """Test ContentRepository CRUD operations."""
    repo = ContentRepository(db_session)
    
    # Create
    content = repo.create(title="Test Title", description="Test Description")
    assert content.id is not None
    assert content.title == "Test Title"
    
    # Get by ID
    retrieved = repo.get_by_id(content.id)
    assert retrieved is not None
    assert retrieved.title == "Test Title"
    
    # Get all
    all_content = repo.get_all()
    assert len(all_content) == 1
    
    # Update
    updated = repo.update(content.id, title="Updated Title")
    assert updated is not None
    assert updated.title == "Updated Title"
    
    # Delete
    deleted = repo.delete(content.id)
    assert deleted is True
    assert repo.get_by_id(content.id) is None


def test_skill_repository(db_session):
    """Test SkillRepository CRUD operations."""
    repo = SkillRepository(db_session)
    
    # Create
    skill = repo.create(name="Python", description="Python programming")
    assert skill.id is not None
    assert skill.name == "Python"
    
    # Get by ID
    retrieved = repo.get_by_id(skill.id)
    assert retrieved is not None
    assert retrieved.name == "Python"
    
    # Get by name
    by_name = repo.get_by_name("Python")
    assert by_name is not None
    assert by_name.id == skill.id
    
    # Get all
    all_skills = repo.get_all()
    assert len(all_skills) == 1
    
    # Update
    updated = repo.update(skill.id, name="Python3")
    assert updated is not None
    assert updated.name == "Python3"
    
    # Delete
    deleted = repo.delete(skill.id)
    assert deleted is True
    assert repo.get_by_id(skill.id) is None


def test_user_skill_repository(db_session, sample_data):
    """Test UserSkillRepository CRUD operations."""
    repo = UserSkillRepository(db_session)
    user = sample_data["users"][0]
    skill = sample_data["skills"][0]
    
    # Get by user
    user_skills = repo.get_by_user(user.id)
    assert len(user_skills) == 2
    
    # Get by user and skill
    us = repo.get_by_user_and_skill(user.id, skill.id)
    assert us is not None
    assert us.proficiency == 0.9
    
    # Update
    updated = repo.update(user.id, skill.id, proficiency=1.0)
    assert updated is not None
    assert updated.proficiency == 1.0
    
    # Delete
    deleted = repo.delete(user.id, skill.id)
    assert deleted is True
    assert repo.get_by_user_and_skill(user.id, skill.id) is None


def test_content_skill_repository(db_session, sample_data):
    """Test ContentSkillRepository CRUD operations."""
    repo = ContentSkillRepository(db_session)
    content = sample_data["content"][0]
    skill = sample_data["skills"][0]
    
    # Get by content
    content_skills = repo.get_by_content(content.id)
    assert len(content_skills) == 2
    
    # Get by content and skill
    cs = repo.get_by_content_and_skill(content.id, skill.id)
    assert cs is not None
    assert cs.relevance == 0.9
    
    # Update
    updated = repo.update(content.id, skill.id, relevance=1.0)
    assert updated is not None
    assert updated.relevance == 1.0
    
    # Delete
    deleted = repo.delete(content.id, skill.id)
    assert deleted is True
    assert repo.get_by_content_and_skill(content.id, skill.id) is None


def test_interaction_repository(db_session, sample_data):
    """Test InteractionRepository CRUD operations."""
    repo = InteractionRepository(db_session)
    user = sample_data["users"][0]
    content = sample_data["content"][0]
    
    # Get by user
    interactions = repo.get_by_user(user.id)
    assert len(interactions) == 2
    
    # Get by user and content
    interaction = repo.get_by_user_and_content(user.id, content.id)
    assert interaction is not None
    assert interaction.rating == 5
    
    # Update
    updated = repo.update(user.id, content.id, rating=4)
    assert updated is not None
    assert updated.rating == 4
    
    # Record feedback
    repo.record_feedback(user.id, content.id, rating=5, interaction_type="love")
    updated_interaction = repo.get_by_user_and_content(user.id, content.id)
    assert updated_interaction.rating == 5
    assert updated_interaction.interaction_type == "love"
    
    # Delete
    deleted = repo.delete(user.id, content.id)
    assert deleted is True
    assert repo.get_by_user_and_content(user.id, content.id) is None

