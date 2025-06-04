import datetime
from datetime import datetime  # Add this import
import json
import sys
import os
import signal  # Add this for process termination
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QFile, QTextStream, QTimer

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask-Login components
from flask_login import LoginManager

# Import your custom modules
from src.core.settings_window import SettingsWindow
from src.core.overlays import TimeOverlay, NotificationOverlay

from src.utils.styles import load_stylesheet
from src.core.database import Session
from src.core.models import User

import resources_rc as resources_rc

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db = Session()
    try:
        return db.query(User).get(int(user_id))
    finally:
        db.close()

def prompt_user_age():
    """This function is replaced by the login system"""
    pass

# Add signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\nReceived interrupt signal. Shutting down gracefully...")
    QApplication.quit()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.user_data = None
        self.overlay = None
        self.notification_overlay = None
        self.settings = None
        self.auto_save_timer = None  # Add timer reference
        self.login_window_active = False  # Track if login window is active
        
        # Load stylesheet
        stylesheet = load_stylesheet()
        self.app.setStyleSheet(stylesheet)
        
        # Enable Ctrl+C handling in console
        self.app.setAttribute(0x10000000)  # Qt.AA_DontShowIconsInMenus
        
    def show_login(self):
        """Show the modern login window"""
        try:
            from src.core.login_window import ModernMomApp
            self.login_window_active = True
            login_app = ModernMomApp(parent_app=self)
            login_app.run()
            
            # If we reach here and login window is closed without successful login
            # The on_window_close method in login_window will handle the exit
            
        except Exception as e:
            print(f"Login error: {e}")
            self.emergency_shutdown()

    def emergency_shutdown(self):
        """Emergency shutdown method"""
        print("Exiting application...")
        if self.auto_save_timer and self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
        if self.app:
            self.app.quit()
        sys.exit(0)

    def on_login_success(self, username):
        """Called when login is successful"""
        try:
            self.login_window_active = False  # Login window is no longer active
            
            # Get user data from auth system
            from src.core.auth import get_user_data
            user_info = get_user_data(username)
            
            # 1. Store user information
            self.user_data = {
                'username': username,
                'login_time': datetime.now(),
                'is_logged_in': True,
                'age': user_info.get('age', 25) if user_info else 25  # Get age from auth system
            }
            
            # 2. Load user-specific data/preferences
            self.load_user_preferences(username)
            self.load_user_data(username)
            
            # 3. Initialize the main application interface
            self.initialize_main_app()  # Use your existing method
            
            # 4. Show welcome message (optional)
            # self.show_welcome_message(username)
            
            # 5. Set up user session
            self.setup_user_session()
            
            # 6. Log the login event
            self.log_user_activity(f"User {username} logged in successfully")
            
            # 7. Start any background processes needed for the user
            self.start_user_processes()
            
        except Exception as e:
            print(f"Error in login success: {e}")
            self.emergency_shutdown()

    def load_user_preferences(self, username):
        """Load user-specific settings and preferences"""
        try:
            # Load from file, database, or config
            prefs_file = f"data/{username}_preferences.json"
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r') as f:
                    self.user_preferences = json.load(f)
            else:
                # Set default preferences
                self.user_preferences = {
                    'theme': 'light',
                    'notifications': True,
                    'language': 'en'
                }
        except Exception as e:
            print(f"Error loading preferences: {e}")
            self.user_preferences = {
                'theme': 'light',
                'notifications': True,
                'language': 'en'
            }

    def load_user_data(self, username):
        """Load user's personal data (tasks, notes, etc.)"""
        try:
            # Load user's tasks, calendar events, notes, etc.
            data_file = f"data/{username}_data.json"
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    self.user_content = json.load(f)
            else:
                # Initialize empty user data structure
                self.user_content = {
                    'tasks': [],
                    'calendar_events': [],
                    'notes': [],
                    'family_members': []
                }
        except Exception as e:
            print(f"Error loading user data: {e}")
            self.user_content = {
                'tasks': [],
                'calendar_events': [],
                'notes': [],
                'family_members': []
            }

    def show_welcome_message(self, username):
        """Display welcome message to the user (PyQt5 version)"""
        try:
            current_hour = datetime.now().hour
            
            if current_hour < 12:
                greeting = "Good morning"
            elif current_hour < 18:
                greeting = "Good afternoon"
            else:
                greeting = "Good evening"
            
            # Use PyQt5 message box instead of tkinter
            msg = QMessageBox()
            msg.setWindowTitle("Welcome")
            msg.setText(f"{greeting}, {username}! 🌟")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            
        except Exception as e:
            print(f"Error showing welcome message: {e}")

    def setup_user_session(self):
        """Set up user session management"""
        self.session_start_time = datetime.now()
        self.is_session_active = True

    def log_user_activity(self, message):
        """Log user activities for audit/debugging"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            # Create logs directory if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            with open("logs/user_activity.log", "a") as log_file:
                log_file.write(log_entry)
        except Exception as e:
            print(f"Error logging activity: {e}")

    def start_user_processes(self):
        """Start any background processes specific to the user"""
        # Start auto-save timer (PyQt5 version)
        self.setup_auto_save()

    def setup_auto_save(self):
        """Set up automatic saving of user data (PyQt5 version)"""
        try:
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.save_user_data)
            self.auto_save_timer.start(300000)  # 5 minutes in milliseconds
        except Exception as e:
            print(f"Error setting up auto-save: {e}")

    def save_user_data(self):
        """Save current user data to file"""
        try:
            if hasattr(self, 'user_data') and hasattr(self, 'user_content'):
                username = self.user_data.get('username')
                if username:
                    # Create data directory if it doesn't exist
                    os.makedirs("data", exist_ok=True)
                    
                    # Save user content
                    data_file = f"data/{username}_data.json"
                    with open(data_file, 'w') as f:
                        json.dump(self.user_content, f, indent=2)
                    
                    # Save preferences
                    prefs_file = f"data/{username}_preferences.json"
                    with open(prefs_file, 'w') as f:
                        json.dump(self.user_preferences, f, indent=2)
                    
                    print(f"Auto-saved data for {username}")
                        
        except Exception as e:
            print(f"Error saving user data: {e}")
        
    def initialize_main_app(self):
        """Initialize the main application after successful login"""
        try:
            sound_file = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sounds', 'Levelup3.wav')
            
            shared_settings = {
                'color': 'white',
                'opacity': 1.0,
                'font': QFont('MODERN WARFARE', 30)
            }
            
            self.overlay = TimeOverlay(shared_settings)
            self.notification_overlay = NotificationOverlay(self.overlay, shared_settings, sound_file)
            self.overlay.syncOverlay = self.notification_overlay
            
            self.settings = SettingsWindow(
                self.overlay, 
                self.notification_overlay, 
                shared_settings, 
                self.user_data['age']  # Pass the age from user data
            )
            self.settings.show()
            
        except Exception as e:
            print(f"Error initializing main app: {e}")
            self.emergency_shutdown()
        
    def run(self):
        """Run the application"""
        try:
            # Show login window
            self.show_login()
            
            # Only run the Qt event loop if login was successful
            # The login window will handle the exit if closed without login
            if hasattr(self, 'user_data') and self.user_data:
                return self.app.exec_()
            else:
                # If no user data, login was cancelled
                return 0
                
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
            return 0
        except Exception as e:
            print(f"Application error: {e}")
            return 1
        finally:
            # Cleanup
            if self.auto_save_timer and self.auto_save_timer.isActive():
                self.auto_save_timer.stop()
                self.save_user_data()  # Save one last time before exit

if __name__ == '__main__':
    try:
        main_app = MainApplication()
        exit_code = main_app.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)