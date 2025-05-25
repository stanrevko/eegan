#!/usr/bin/env python3
"""
EEG Analysis Application
Main entry point for the minimal GUI version
"""

import sys
import os

# Add project directories to Python path
sys.path.append(os.path.dirname(__file__))

# Import after setting path
try:
    print("🧠 Starting EEG Analysis Application...")
    print("📁 Loading from: /Users/stanrevko/projects/eegan/eeg_data")
    
    from PyQt5.QtWidgets import QApplication
    from gui.main_window import MainWindow
    
    def main():
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Modern look
        
        # Create and show main window
        print("🖥️  Creating main window...")
        window = MainWindow()
        window.show()
        window.raise_()  # Bring to front
        window.activateWindow()  # Make sure it's active
        
        print("✅ EEG Analysis Application started successfully!")
        print("👀 Check your screen for the main application window")
        
        sys.exit(app.exec_())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the virtual environment:")
    print("   source venv/bin/activate")
except Exception as e:
    print(f"❌ Error starting application: {e}")
    print("🔧 Try running the test first: python test_gui.py")
