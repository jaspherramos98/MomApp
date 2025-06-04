#!/usr/bin/env python3
"""
Reset the database for the Mom App.
This will delete all existing data and create a fresh database.
"""

import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Remove existing database file
    db_path = "app.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Import after removing the database
    from src.core.database import engine, Session
    from src.core.models import Base, User
    
    print("Creating new database...")
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Database created successfully!")
    
    # Create a test user
    session = Session()
    try:
        # Create test user
        user = User(username="test", age=25)
        user.set_password("test123")
        session.add(user)
        
        # Create another demo user
        demo_user = User(username="demo", age=30)
        demo_user.set_password("demo123")
        session.add(demo_user)
        
        session.commit()
        print("\nTest users created:")
        print("1. username='test', password='test123'")
        print("2. username='demo', password='demo123'")
        
    except Exception as e:
        print(f"Error creating test users: {e}")
        session.rollback()
    finally:
        session.close()
        
except Exception as e:
    print(f"Error resetting database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)