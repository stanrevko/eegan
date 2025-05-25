#!/usr/bin/env python3
"""
EEG Analysis Application - Fixed Version
Main entry point that works with the main window
"""

import sys
import os

# Add project directories to Python path
sys.path.append(os.path.dirname(__file__))


def main():
    """Main application launcher"""
    print("🧠 Starting EEG Analysis Suite...")
    print("📁 Features: Auto-loading, File browser, EEG timeline, Band analysis")
    print("🎛️ Controls: Channel visibility, Y-axis scaling, Timeline navigation")
    print("⚡ Bands: Alpha, Beta, Theta, Delta, Gamma")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from gui.main_window import main as gui_main
        
        # Start the GUI application
        gui_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the virtual environment:")
        print("   source venv/bin/activate")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("🔧 Check the error message above for details")


if __name__ == "__main__":
    main()
