
"""Script to seed the database with realistic fake data using Faker."""
import sys
import os
import random
from typing import List, Tuple, Set

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from data.database import Base, engine, SessionLocal
from data.repository import (
    UserRepository,
    ContentRepository,
    SkillRepository,
    UserSkillRepository,
    ContentSkillRepository,
    InteractionRepository,
)

# Initialize Faker
fake = Faker()
random.seed(42)  # For reproducibility


def init_database():
    """Initialize the database, creating tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized (tables created if needed)")


def generate_users(db, count: int = 10) -> List[int]:
    """Generate unique users, return their IDs."""
    user_repo = UserRepository(db)
    generated_user_ids: List[int] = []
    used_usernames: Set[str] = set()
    used_emails: Set[str] = set()

    while len(generated_user_ids) < count:
        username = fake.user_name()
        email = fake.unique.email()

        # Ensure uniqueness
        if username in used_usernames or email in used_emails:
            continue

        # Create user
        user = user_repo.create(
            username=username,
            email=email,
            hashed_password=fake.password(length=12)
        )
        generated_user_ids.append(user.id)
        used_usernames.add(username)
        used_emails.add(email)
        print(f"Created user: {username} ({email})")

    print(f"\nSuccessfully generated {len(generated_user_ids)} users")
    return generated_user_ids


def generate_skills(db, count: int = 15) -> List[int]:
    """Generate unique skills, return their IDs."""
    skill_repo = SkillRepository(db)
    generated_skill_ids: List[int] = []
    used_skill_names: Set[str] = set()

    # List of common tech/soft skills to draw from
    skill_candidates = [
        "Python", "JavaScript", "React", "Node.js", "SQL", "Docker",
        "Kubernetes", "AWS", "Machine Learning", "Data Analysis",
        "Project Management", "Communication", "Leadership",
        "Graphic Design", "UI/UX", "Mobile Development",
        "DevOps", "Cybersecurity", "Cloud Computing", "Git"
    ]

    # Use candidates first, then generate random if needed
    for skill_name in skill_candidates:
        if len(generated_skill_ids) >= count:
            break
        if skill_name in used_skill_names:
            continue

        skill = skill_repo.create(
            name=skill_name,
            description=fake.sentence(nb_words=10)
        )
        generated_skill_ids.append(skill.id)
        used_skill_names.add(skill_name)
        print(f"Created skill: {skill_name}")

    # If we need more skills, generate random ones
    while len(generated_skill_ids) < count:
        skill_name = fake.word(ext_word_list=["Skill", "Tech", "Tool", "Methodology"]) + " " + fake.word()
        if skill_name in used_skill_names:
            continue

        skill = skill_repo.create(
            name=skill_name,
            description=fake.sentence(nb_words=10)
        )
        generated_skill_ids.append(skill.id)
        used_skill_names.add(skill_name)
        print(f"Created skill: {skill_name}")

    print(f"\nSuccessfully generated {len(generated_skill_ids)} skills")
    return generated_skill_ids


def generate_content(db, count: int = 20, skill_ids: List[int] = None) -> List[int]:
    """Generate unique content items, return their IDs."""
    content_repo = ContentRepository(db)
    content_skill_repo = ContentSkillRepository(db)
    generated_content_ids: List[int] = []
    used_titles: Set[str] = set()

    while len(generated_content_ids) < count:
        title = fake.sentence(nb_words=4)[:200]  # Keep title under 200 chars
        if title in used_titles:
            continue

        # Create content
        content = content_repo.create(
            title=title,
            description=fake.paragraph(nb_sentences=5)
        )
        generated_content_ids.append(content.id)
        used_titles.add(title)
        print(f"Created content: {title}")

        # Add random skills to content
        if skill_ids:
            num_skills = random.randint(1, 4)
            selected_skill_ids = random.sample(skill_ids, min(num_skills, len(skill_ids)))
            for skill_id in selected_skill_ids:
                relevance = round(random.uniform(0.3, 1.0), 2)
                content_skill_repo.create(
                    content_id=content.id,
                    skill_id=skill_id,
                    relevance=relevance
                )

    print(f"\nSuccessfully generated {len(generated_content_ids)} content items with skills")
    return generated_content_ids


def generate_user_skills(db, user_ids: List[int], skill_ids: List[int]) -> None:
    """Generate user-skill associations."""
    user_skill_repo = UserSkillRepository(db)
    total_associations = 0

    for user_id in user_ids:
        # Assign 2-8 random skills per user
        num_skills = random.randint(2, 8)
        selected_skill_ids = random.sample(skill_ids, min(num_skills, len(skill_ids)))
        for skill_id in selected_skill_ids:
            proficiency = round(random.uniform(0.2, 1.0), 2)
            user_skill_repo.create(
                user_id=user_id,
                skill_id=skill_id,
                proficiency=proficiency
            )
            total_associations += 1

    print(f"Successfully generated {total_associations} user-skill associations")


def generate_interactions(db, user_ids: List[int], content_ids: List[int], count: int = 100) -> None:
    """Generate unique user-content interactions."""
    interaction_repo = InteractionRepository(db)
    used_interactions: Set[Tuple[int, int]] = set()
    interaction_types = ["view", "like", "share", "comment", "save", "rate"]
    generated = 0

    while generated < count:
        user_id = random.choice(user_ids)
        content_id = random.choice(content_ids)
        interaction_key = (user_id, content_id)

        # Skip duplicate user-content pairs
        if interaction_key in used_interactions:
            continue

        rating = random.uniform(1.0, 5.0) if random.random() > 0.3 else None  # 70% have ratings
        interaction_type = random.choice(interaction_types)

        interaction_repo.record_feedback(
            user_id=user_id,
            content_id=content_id,
            rating=round(rating, 1) if rating else None,
            interaction_type=interaction_type
        )
        used_interactions.add(interaction_key)
        generated += 1
        if generated % 10 == 0:
            print(f"Generated {generated}/{count} interactions")

    print(f"\nSuccessfully generated {count} interactions")


def main():
    """Main function to seed the database."""
    print("=" * 50)
    print("Starting database seeding process")
    print("=" * 50)

    # Step 1: Initialize database
    init_database()

    # Open a single database session for all operations
    db = SessionLocal()

    try:
        # Step 2: Generate users
        print("\n" + "-" * 50)
        user_ids = generate_users(db, count=10)

        # Step 3: Generate skills
        print("\n" + "-" * 50)
        skill_ids = generate_skills(db, count=15)

        # Step 4: Generate content with skills
        print("\n" + "-" * 50)
        content_ids = generate_content(db, count=20, skill_ids=skill_ids)

        # Step 5: Generate user skills
        print("\n" + "-" * 50)
        generate_user_skills(db, user_ids, skill_ids)

        # Step 6: Generate interactions
        print("\n" + "-" * 50)
        generate_interactions(db, user_ids, content_ids, count=100)

    finally:
        db.close()

    print("\n" + "=" * 50)
    print("Database seeding complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
