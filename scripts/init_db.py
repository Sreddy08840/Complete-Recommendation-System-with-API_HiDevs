
"""Script to initialize the database and create all tables."""
import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from data.database import Base, engine


def init_db() -> None:
    """
    Initialize the database by creating all tables defined in the models.

    This function uses SQLAlchemy's metadata.create_all() to create tables
    for all models that inherit from Base.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully! All tables created.")


if __name__ == "__main__":
    init_db()

