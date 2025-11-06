"""
Database initialization script.
Creates the database schema and initial owner user.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models import *  # Import all models to register them


def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def create_owner_user():
    """Create the initial owner user."""
    db = SessionLocal()
    try:
        # Check if owner already exists
        existing_owner = db.query(User).filter(User.role == UserRole.OWNER).first()
        if existing_owner:
            print(f"✓ Owner user already exists: {existing_owner.username}")
            return

        # Create owner user
        owner = User(
            username="admin",
            email="admin@jewelryshop.com",
            password_hash=get_password_hash("admin123"),  # Change this password!
            role=UserRole.OWNER
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        print(f"✓ Owner user created successfully!")
        print(f"  Username: {owner.username}")
        print(f"  Email: {owner.email}")
        print(f"  Password: admin123")
        print(f"\n⚠️  IMPORTANT: Change this password after first login!")

    except Exception as e:
        print(f"✗ Error creating owner user: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function."""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    print()

    init_database()
    print()
    create_owner_user()

    print()
    print("=" * 60)
    print("Initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
