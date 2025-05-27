#!/usr/bin/env python3
"""
Simple GUI test to verify PyQt5 is working
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EEG App Test - Can you see this window?")
        self.setGeometry(200, 200, 600, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Add labels
        title = QLabel("🧠 EEG Analysis Test")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        
        status = QLabel("✅ If you can see this window, PyQt5 is working!")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("font-size: 16px; padding: 20px;")
        
        instruction = QLabel("Close this window and try running 'python main.py' again")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("font-size: 14px; color: #666; padding: 20px;")
        
        layout.addWidget(title)
        layout.addWidget(status)
        layout.addWidget(instruction)

def main():
    print("🔍 Testing PyQt5 GUI...")
    print("📖 A window should appear on your screen")
    print("❌ If no window appears, there may be a display issue")
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    window.raise_()  # Bring to front
    window.activateWindow()  # Make sure it's active
    
    print("✅ Test window created and shown")
    print("👀 Check your screen for the test window")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
