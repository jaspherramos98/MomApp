import datetime
from email.mime import application
from PyQt5.QtCore import Qt, QTimer, QTime, pyqtSignal, QThread
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QApplication
from PyQt5.QtMultimedia import QSound
from PyQt5.QtGui import QFont, QColor

class DraggableOverlay(QWidget):
    def __init__(self, syncOverlay = None):
        super().__init__()
        self.syncOverlay = syncOverlay
        self.dragging = False
        self.drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            new_position = event.globalPos() - self.drag_position
            self.move(new_position)
            if self.syncOverlay:
                self.syncOverlay.move(new_position)
            event.accept()

    def ensureOnScreen(self):
        screen = QApplication.primaryScreen().geometry()
        rect = self.geometry()

        if rect.right() > screen.right():
            rect.moveRight(screen.right())
        if rect.left() < screen.left():
            rect.moveLeft(screen.left())
        if rect.bottom() > screen.bottom():
            rect.moveBottom(screen.bottom())
        if rect.top() < screen.top():
            rect.moveTop(screen.top())

        self.setGeometry(rect)

class TimeOverlay(DraggableOverlay):
    breakTimeUpdated = pyqtSignal(str)
    totalBreakTimeUpdated = pyqtSignal(str)
    resetRequested = pyqtSignal()

    def __init__(self, shared_settings, user_id=None):
        self.user_id = user_id
        super().__init__()
        self.shared_settings = shared_settings
        self.mainTimer = QTimer(self)
        self.mainTimer.timeout.connect(self.updateMainDisplay)
        self.mainTimer.setTimerType(Qt.PreciseTimer)

        self.breakTimer = QTimer(self)
        self.breakTimer.timeout.connect(self.updateBreakDisplay)
        self.breakTimer.setTimerType(Qt.PreciseTimer)

        self.running = False
        self.isBreak = False
        self.mainStartTime = QTime.currentTime()
        self.breakStartTime = None

        self.mainElapsedTime = 0
        self.breakElapsedTime = 0
        self.totalBreakTime = 0
        
        self.opacity = 1.0
        
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.timerLabel = QLabel("00:00:00", self)
        self.timerLabel.setFont(QFont('MODERN WARFARE', 30))
        self.timerLabel.setStyleSheet("QLabel { color: white; }")
        self.applySettings()
        self.timerLabel.setAlignment(Qt.AlignCenter)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.timerLabel)
        self.setLayout(layout)
        self.setGeometry(100, 100, 200, 100)
        self.show()

    def applySettings(self):
        self.timerLabel.setFont(self.shared_settings['font'])
        self.timerLabel.setStyleSheet(f"QLabel {{ color: {self.shared_settings['color']}; }}")
        self.setWindowOpacity(self.shared_settings['opacity'])
    
    def startTimer(self):
        if not self.running:
            self.mainStartTime = QTime.currentTime()
            self.mainTimer.start(1000)
            self.running = True
            
    def resetTimer(self):
        # Stop the main and break timers if they are running
        self.mainTimer.stop()
        self.breakTimer.stop()

        # Reset all time-tracking variables
        self.mainElapsedTime = 0
        self.breakElapsedTime = 0
        self.totalBreakTime = 0
        self.isBreak = False
        self.running = False

        # Update UI elements to reflect the reset
        self.timerLabel.setText("00:00:00")
        self.breakTimeUpdated.emit("Current Break: 00:00:00")
        self.totalBreakTimeUpdated.emit("Total Break: 00:00:00")

        # Send a signal to other parts of the app to handle the reset
        self.resetRequested.emit()


    def pauseTimer(self):
        if self.running:
            self.updateMainElapsedTime()
            self.mainTimer.stop()
            self.running = False
            self.startBreak()

    def startBreak(self):
        if not self.isBreak:
            self.breakStartTime = QTime.currentTime()
            self.breakTimer.start(1000)
            self.isBreak = True

    def resumeTimer(self):
        if not self.running and not self.isBreak:
            self.mainStartTime = QTime.currentTime()
            self.mainTimer.start(1000)
            self.running = True
            
    def endBreak(self):
        if self.isBreak:
            self.updateBreakDisplay()
            self.breakTimer.stop()
            self.breakElapsedTime = 0
            self.isBreak = False
            self.resumeTimer()

    def updateMainElapsedTime(self):
        current_time = self.mainStartTime.msecsTo(QTime.currentTime())
        self.mainElapsedTime += current_time
        self.mainStartTime = QTime.currentTime()

    def updateMainDisplay(self):
        if self.running:
            current_time = self.mainStartTime.msecsTo(QTime.currentTime())
            total_time = self.mainElapsedTime + current_time
            time_str = QTime(0, 0).addMSecs(total_time).toString("hh:mm:ss")
            self.timerLabel.setText(time_str)

    def updateBreakDisplay(self):
        if self.isBreak:
            current_break_time = self.breakStartTime.msecsTo(QTime.currentTime())
            self.breakElapsedTime += current_break_time
            self.breakStartTime = QTime.currentTime()
            break_time_str = QTime(0, 0).addMSecs(self.breakElapsedTime).toString("hh:mm:ss")
            self.breakTimeUpdated.emit("Current Break: " + break_time_str)
            self.totalBreakTime += current_break_time
            total_break_time_str = QTime(0, 0).addMSecs(self.totalBreakTime).toString("hh:mm:ss")
            self.totalBreakTimeUpdated.emit("Total Break: " + total_break_time_str)
            
    def startPeriodicNotifications(self, interval_minutes, notificationOverlay):
        self.notificationInterval = interval_minutes * 60000  # Convert minutes to milliseconds
        if hasattr(self, 'notificationTimer'):
            self.notificationTimer.stop()  # Stop existing timer if it's running
        self.notificationTimer = QTimer(self)  # Create a new QTimer instance
        self.notificationTimer.timeout.connect(lambda: notificationOverlay.showNotification(notificationOverlay.notificationMessage))
        self.notificationTimer.start(self.notificationInterval)
        print(f"Notifications will appear every {interval_minutes} minutes.")
    
    def get_total_time(self):
            self.updateMainElapsedTime()  # Update elapsed time before getting the value
            if self.mainElapsedTime < 1:
                return 0
            else:
                return round(self.mainElapsedTime / 1000 / 60)

    def save_session(self):
        from src.core.database import SessionRecord, Session
        db = Session()
        session = SessionRecord(
            user_id=self.user_id,
            start_time=datetime.now(),
            screen_time=self.get_total_time(),
            break_time=self.totalBreakTime // 60000
        )
        db.add(session)
        db.commit()

class NotificationOverlay(DraggableOverlay):
    def __init__(self, timeOverlay, shared_settings, sound_file):
        super().__init__()
        self.timeOverlay = timeOverlay  # Reference to the TimeOverlay instance
        self.shared_settings = shared_settings
        self.notificationMessage = "Time to take a break!"  # Default message
        self.sound = QSound(sound_file)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.notificationLabel = QLabel("", self)
        self.notificationLabel.setFont(self.shared_settings['font'])  # Set initial font
        self.notificationLabel.setStyleSheet("QLabel { color: white; }")
        self.applySettings()  # Apply shared settings
        self.notificationLabel.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.notificationLabel)
        self.setLayout(layout)
        self.setGeometry(100, 100, 300, 100)

    def applySettings(self):
        # Update font, color, and opacity based on shared settings
        self.notificationLabel.setFont(self.shared_settings['font'])
        self.notificationLabel.setStyleSheet(f"QLabel {{ color: {self.shared_settings['color']}; }}")
        self.setWindowOpacity(self.shared_settings['opacity'])

    def showNotification(self, message):
        self.notificationLabel.setText(message)
        self.adjustSize()
        self.ensureOnScreen()
        self.show()
        if self.timeOverlay:
            self.timeOverlay.hide()  # Hide the timer overlay
        self.sound.play()
        # Set a timer to hide the notification after 10 seconds
        QTimer.singleShot(5000, self.hideNotification)

    def hideNotification(self):
        self.hide()
        if self.timeOverlay:
            self.timeOverlay.show()  # Show the timer overlay again
    
    def ensureVisibility(self):
        screen = QApplication.primaryScreen().geometry()
        overlay = self.geometry()
        x, y = overlay.x(), overlay.y()

        if overlay.right() > screen.right():
            x = screen.right() - overlay.width()
        if overlay.bottom() > screen.bottom():
            y = screen.bottom() - overlay.height()
        if overlay.left() < screen.left():
            x = screen.left()
        if overlay.top() < screen.top():
            y = screen.top()

        self.move(x, y)
