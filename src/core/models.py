from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
import hashlib

# Create the base class for SQLAlchemy models
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    preferences = Column(Text)  # Store JSON string of preferences

    def set_password(self, password):
        """Hash and set the user's password using SHA-256"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def __repr__(self):
        return f'<User {self.username}>'