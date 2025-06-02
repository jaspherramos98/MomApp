import sys
import os
from PyQt5.QtWidgets import QApplication, QInputDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QFile, QTextStream

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now use absolute imports
from src.core.settings_window import SettingsWindow
from src.core.overlays import TimeOverlay, NotificationOverlay
from src.utils.styles import load_stylesheet
import resources_rc as resources_rc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def prompt_user_age():
    dialog = QInputDialog()
    dialog.setStyleSheet(QApplication.instance().styleSheet())
    user_age, ok = QInputDialog.getInt(None, "User Age", "Enter your age:", 18, 0, 100)
    return user_age if ok else None

def load_stylesheet():
    file = QFile(":/qss/dark.qss")  # Use QFile for resource system
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        return stream.readAll()
    print("Failed to load stylesheet")
    return ""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())  # Call the function
    
    user_age = prompt_user_age()
    if not user_age:
        print("No age provided. Exiting application.")
        sys.exit(0)

    sound_file = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sounds', 'Levelup3.wav')
    
    shared_settings = {
        'color': 'white',
        'opacity': 1.0,
        'font': QFont('MODERN WARFARE', 30)
    }
    
    overlay = TimeOverlay(shared_settings)
    notificationOverlay = NotificationOverlay(overlay, shared_settings, sound_file)
    overlay.syncOverlay = notificationOverlay
    
    settings = SettingsWindow(overlay, notificationOverlay, shared_settings, user_age)
    settings.show()
    sys.exit(app.exec_())