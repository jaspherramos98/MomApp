from PyQt5.QtWidgets import (QWidget, QGridLayout, QTextEdit, QLineEdit, QPushButton, 
                            QHBoxLayout, QLabel, QSlider, QCheckBox, QFontDialog, 
                            QColorDialog, QInputDialog, QMessageBox)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from src.core.openai_integration import Worker, generate_openai_response


class SettingsWindow(QWidget):
    def __init__(self, overlay, notificationOverlay, shared_settings, user_age):
        super().__init__()
        self.overlay = overlay
        self.notificationOverlay = notificationOverlay
        self.shared_settings = shared_settings
        self.user_age = user_age
        self.worker = None
        self.chat_history = []
        self.initUI()
        self.overlay.resetRequested.connect(self.onResetRequested)
        self.overlay.breakTimeUpdated.connect(self.updateBreakTimeDisplay)
        self.overlay.totalBreakTimeUpdated.connect(self.updateTotalBreakTimeDisplay)
        self.send_welcome_message()

    def initUI(self):
        self.setWindowTitle("Settings")
        self.setStyleSheet("background-color: #333; color: white;")
        layout = QGridLayout(self)

        # Add chat display area
        self.chatDisplay = QTextEdit(self)
        self.chatDisplay.setReadOnly(True)
        layout.addWidget(self.chatDisplay, 0, 0, 1, 2)  # Span across two columns

        # Input area for sending messages
        self.inputField = QLineEdit(self)
        self.inputField.setPlaceholderText("Ask anything")
        self.sendButton = QPushButton("Send", self)
        self.sendButton.clicked.connect(self.send_message)

        # Layout for input area
        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.inputField)
        inputLayout.addWidget(self.sendButton)
        layout.addLayout(inputLayout, 1, 0, 1, 2)  # Place it below the chatDisplay, spanning two columns

        self.startStopButton = QPushButton("Start", self)
        self.startStopButton.clicked.connect(self.toggleTimer)
        layout.addWidget(self.startStopButton, 2, 0)
        
        self.stopButton = QPushButton("Stop and reset", self)
        self.stopButton.clicked.connect(self.stopAllTimers)
        layout.addWidget(self.stopButton, 2, 1)

        fontBtn = QPushButton("Change Font", self)
        fontBtn.clicked.connect(self.changeFont)
        layout.addWidget(fontBtn, 3, 0)

        fontColorBtn = QPushButton("Change Font Color", self)
        fontColorBtn.clicked.connect(self.changeFontColor)
        layout.addWidget(fontColorBtn, 3, 1)
        
        notificationIntervalBtn = QPushButton("Set time", self)
        notificationIntervalBtn.clicked.connect(self.setNotificationInterval)
        layout.addWidget(notificationIntervalBtn, 4, 0)
        
        changeNotificationMsgBtn = QPushButton("Change Notification Message", self)
        changeNotificationMsgBtn.clicked.connect(self.changeNotificationMessage)
        layout.addWidget(changeNotificationMsgBtn, 4, 1)

        opacityLabel = QLabel("Opacity:", self)
        self.opacitySlider = QSlider(Qt.Horizontal, self)
        self.opacitySlider.setRange(0, 100)
        self.opacitySlider.setValue(int(self.overlay.opacity * 100))
        self.opacitySlider.valueChanged.connect(self.changeOpacity)
        opacityLayout = QHBoxLayout()
        opacityLayout.addWidget(opacityLabel)
        opacityLayout.addWidget(self.opacitySlider)
        layout.addLayout(opacityLayout, 5, 0, 1, 2)
        
        self.breakTimeLabel = QLabel("Current Break: 00:00:00", self)
        layout.addWidget(self.breakTimeLabel, 6, 0)
        self.totalBreakTimeLabel = QLabel("Total Break: 00:00:00", self)
        layout.addWidget(self.totalBreakTimeLabel, 6, 1)
        self.breakTimeLabel.setAlignment(Qt.AlignLeft)
        self.totalBreakTimeLabel.setAlignment(Qt.AlignRight)
        
        self.toggleTimerVisibilityCheckBox = QCheckBox("Notifications Only", self)
        self.toggleTimerVisibilityCheckBox.setChecked(True)
        self.toggleTimerVisibilityCheckBox.stateChanged.connect(self.toggleTimerVisibility)
        layout.addWidget(self.toggleTimerVisibilityCheckBox, 8, 0)

        self.testNotificationBtn = QPushButton("Test Notification: " + self.notificationOverlay.notificationMessage, self)
        self.testNotificationBtn.clicked.connect(self.testNotification)
        layout.addWidget(self.testNotificationBtn, 7, 0, 1, 2)

        self.setLayout(layout)
        self.setGeometry(500, 500, 350, 500)
        
    def onResetRequested(self):
        # Reset the chat display or other elements if necessary
        self.chatDisplay.append("\nSystem: The timer has been reset. You can start a new session.\n\n")
        self.startStopButton.setText("Start")

    def stopAllTimers(self):
        self.handleReset()
        self.overlay.resetTimer()
        #if not self.overlay.running and not self.overlay.isBreak:
         #   self.overlay.startTimer()

    def toggleTimerVisibility(self, state):
        if state == Qt.Checked:
            self.overlay.hide()
        else:
            self.overlay.show()
        
    def updateTestButtonLabel(self):
        self.testNotificationBtn.setText("Test Notification: " + self.notificationOverlay.notificationMessage)

    def testNotification(self):
        self.notificationOverlay.showNotification(self.notificationOverlay.notificationMessage)    
    
    def toggleTimer(self):
        if not self.overlay.running and not self.overlay.isBreak:
            self.overlay.startTimer()
            self.startStopButton.setText("Pause")
        elif self.overlay.running:
            self.overlay.pauseTimer()
            self.evaluate_break_time()
            self.startStopButton.setText("Resume")
        else:
            self.overlay.endBreak()
            self.overlay.resumeTimer()
            self.startStopButton.setText("Pause")

    def changeFontColor(self):
        currentColor = QColor(self.shared_settings['color'])
        color = QColorDialog.getColor(currentColor, self)
        if color.isValid():
            self.shared_settings['color'] = color.name()
            self.overlay.applySettings()
            self.notificationOverlay.applySettings()

    def changeFont(self):
        font, ok = QFontDialog.getFont(self.shared_settings['font'], self)
        if ok:
            self.shared_settings['font'] = font
            self.overlay.applySettings()
            self.notificationOverlay.applySettings()

    def changeOpacity(self, value):
        opacity = value / 100.0
        self.shared_settings['opacity'] = opacity
        self.overlay.applySettings()
        self.notificationOverlay.applySettings()
    
    def get_user_age(self):
        return self.user_age
    
    def calculate_recommendations(self, user_age):
        if user_age < 2:
            return 0, 50  # Recommended screen time in hours and brightness in percentage
        elif user_age <= 5:
            return 1, 60
        elif user_age <= 17:
            return 2, 70
        else:
            return 4, 80
    
    def evaluate_break_time(self):
        # Analyze total time spent and suggest a break
        total_time = self.overlay.get_total_time()  # Assuming this method exists
        recommended_break = self.calculate_break_time(total_time)
        break_message = f"You've been using the screen for {total_time} minutes. It's recommended to take a {recommended_break} minute break."
        self.display_response(break_message)

    def calculate_break_time(self, total_time):
        return (total_time // 60) * 15 
     
    def send_welcome_message(self):
        # This is a placeholder function, implement with OpenAI API call
        recommended_brightness = 70
        age = self.get_user_age()
        if age:
            recommended_time, recommended_brightness = self.calculate_recommendations(age)
            welcome_message = f"Welcome! Based on your age, here are my recommendations:\nTotal usage time: {recommended_time} hours\nBrightness: {recommended_brightness}%\nBreak Time: 15 minutes per hour."
            self.display_response(welcome_message)

    def handleReset(self):
        # Move the AI advice logic here
        total_time = self.overlay.get_total_time()  # Assuming this method exists
        break_time = self.overlay.totalBreakTime / 1000 / 60  # Convert ms to minutes

        # Create a prompt asking for specific advice
        user_input = f"Please provide advice and recommendations based on the following session summary: {total_time} hours of work with {break_time} minutes of break."

        # Check if worker is available and not running, then start the worker with the new prompt
        if not self.worker or not self.worker.isRunning():
            self.worker = Worker(user_input, self.chat_history)
            self.worker.response.connect(self.display_advice)
            self.worker.start()
        
    def display_advice(self, advice):
        formatted_advice = advice.replace('?', '.').strip()  # Simple example to replace questions
        self.chatDisplay.append(f"AI: {formatted_advice} \n")

    def send_message(self):
        user_input = self.inputField.text()
        if user_input:
            self.chatDisplay.append("You: " + user_input)
            self.interact_with_ai(user_input)

    def interact_with_ai(self, user_input):
        # Process input as before, update chat display with the response
        if not self.worker or not self.worker.isRunning():
            self.worker = Worker(user_input, self.chat_history)
            self.worker.response.connect(self.display_response)
            self.worker.start()

    def display_response(self, response):
        self.chatDisplay.append("AI: " + response + " \n" )
        # Optionally, update the GUI or state based on response

    def prepare_worker(self, prompt):
        if not self.worker or not self.worker.isRunning():
            self.worker = Worker(prompt)
            self.worker.response.connect(self.display_response)
            self.worker.start()
        
    def updateBreakTimeDisplay(self, break_time_str):
        self.breakTimeLabel.setText(break_time_str)
    
    def updateTotalBreakTimeDisplay(self, total_break_time_str):
        self.totalBreakTimeLabel.setText(total_break_time_str)

    def setNotificationInterval(self):
        interval, ok = QInputDialog.getInt(self, "Set Interval", "Enter the interval for notifications (in minutes):", 5, 1, 60)
        if ok:
            self.overlay.startPeriodicNotifications(interval, self.notificationOverlay)
            
    def changeNotificationMessage(self):
        message, ok = QInputDialog.getText(self, "Change Notification Message", "Enter new notification message:")
        if ok and message:
            self.notificationOverlay.notificationMessage = message
            self.updateTestButtonLabel()
