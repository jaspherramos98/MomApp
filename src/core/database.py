from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "sqlite:///app.db"  

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database by creating all tables"""
    from src.core.models import Base
    Base.metadata.create_all(engine)
    print("Database initialized successfully")

def get_db_session():
    """Get a new database session"""
    return Session()

def reset_db():
    """Reset the database - useful for development"""
    from src.core.models import Base
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database reset successfully")

# Don't auto-initialize on import - let main.py handle it