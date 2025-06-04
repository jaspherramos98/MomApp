# auth.py - Authentication module for Mom App
import hashlib
import json
import os
from datetime import datetime
import sqlite3
from typing import Optional, Dict, Any

try:
    from .database import Session, init_db
    from .models import User
    USE_SQLALCHEMY = True
    # Initialize database tables if needed
    try:
        init_db()
    except:
        pass  # Database might already be initialized
except ImportError:
    USE_SQLALCHEMY = False
    print("Using file-based authentication")

class AuthManager:
    """Handles user authentication and registration"""
    
    def __init__(self):
        self.users_file = "data/users.json"
        self.db_file = "data/users.db"
        self.ensure_data_directory()
        
        if not USE_SQLALCHEMY:
            self.init_file_storage()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs("data", exist_ok=True)
    
    def init_file_storage(self):
        """Initialize file-based storage if not using database"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user_sqlalchemy(self, username: str, password: str) -> bool:
        """Authenticate user using SQLAlchemy"""
        session = Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user and user.check_password(password):
                # Try to update last_login if column exists
                try:
                    user.last_login = datetime.now()
                    session.commit()
                except:
                    pass  # Column might not exist
                return True
            return False
        finally:
            session.close()
    
    def authenticate_user_file(self, username: str, password: str) -> bool:
        """Authenticate user using file storage"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username in users:
                stored_password = users[username].get('password')
                if stored_password == self.hash_password(password):
                    # Update last login
                    users[username]['last_login'] = datetime.now().isoformat()
                    with open(self.users_file, 'w') as f:
                        json.dump(users, f, indent=2)
                    return True
            return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def register_user_sqlalchemy(self, username: str, password: str, **kwargs) -> bool:
        """Register user using SQLAlchemy"""
        session = Session()
        try:
            # Check if user exists
            existing = session.query(User).filter_by(username=username).first()
            if existing:
                return False
            
            # Create new user
            user = User(
                username=username,
                age=kwargs.get('age', 18)
            )
            
            # Set optional fields if the columns exist
            try:
                user.created_at = datetime.now()
            except:
                pass  # Column might not exist
                
            user.set_password(password)
            
            session.add(user)
            session.commit()
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def register_user_file(self, username: str, password: str, **kwargs) -> bool:
        """Register user using file storage"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username in users:
                return False  # User already exists
            
            # Create new user
            users[username] = {
                'password': self.hash_password(password),
                'age': kwargs.get('age', 18),
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'preferences': kwargs.get('preferences', {})
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    def get_user_data(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user data by username"""
        if USE_SQLALCHEMY:
            session = Session()
            try:
                user = session.query(User).filter_by(username=username).first()
                if user:
                    user_data = {
                        'username': user.username,
                        'age': user.age
                    }
                    
                    # Add optional fields if they exist
                    try:
                        if hasattr(user, 'created_at'):
                            user_data['created_at'] = user.created_at
                        if hasattr(user, 'last_login'):
                            user_data['last_login'] = user.last_login
                    except:
                        pass
                        
                    return user_data
                return None
            finally:
                session.close()
        else:
            try:
                with open(self.users_file, 'r') as f:
                    users = json.load(f)
                return users.get(username)
            except:
                return None
    
    def update_user_preferences(self, username: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        if USE_SQLALCHEMY:
            session = Session()
            try:
                user = session.query(User).filter_by(username=username).first()
                if user:
                    # Update preferences (you may need to add this field to your User model)
                    # user.preferences = json.dumps(preferences)
                    session.commit()
                    return True
                return False
            finally:
                session.close()
        else:
            try:
                with open(self.users_file, 'r') as f:
                    users = json.load(f)
                
                if username in users:
                    users[username]['preferences'] = preferences
                    with open(self.users_file, 'w') as f:
                        json.dump(users, f, indent=2)
                    return True
                return False
            except:
                return False

# Create global auth manager instance
auth_manager = AuthManager()

# Public API functions
def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user with username and password"""
    if USE_SQLALCHEMY:
        return auth_manager.authenticate_user_sqlalchemy(username, password)
    else:
        return auth_manager.authenticate_user_file(username, password)

def register_user(username: str, password: str, **kwargs) -> bool:
    """Register a new user"""
    if USE_SQLALCHEMY:
        return auth_manager.register_user_sqlalchemy(username, password, **kwargs)
    else:
        return auth_manager.register_user_file(username, password, **kwargs)

def hash_password(password: str) -> str:
    """Hash a password"""
    return auth_manager.hash_password(password)

def get_user_data(username: str) -> Optional[Dict[str, Any]]:
    """Get user data"""
    return auth_manager.get_user_data(username)

def update_user_preferences(username: str, preferences: Dict[str, Any]) -> bool:
    """Update user preferences"""
    return auth_manager.update_user_preferences(username, preferences)

# For testing
if __name__ == "__main__":
    # Test registration
    if register_user("test_user", "test_password", age=25):
        print("User registered successfully")
    else:
        print("Registration failed")
    
    # Test authentication
    if authenticate_user("test_user", "test_password"):
        print("Authentication successful")
    else:
        print("Authentication failed")
    
    # Test getting user data
    user_data = get_user_data("test_user")
    if user_data:
        print(f"User data: {user_data}")