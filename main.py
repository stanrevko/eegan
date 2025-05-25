#!/usr/bin/env python3
"""
EEG Analysis Application - Enhanced Modular Version
Main entry point with all requested features implemented
"""

import sys
import os

# Add project directories to Python path
sys.path.append(os.path.dirname(__file__))

def main():
    """Main application launcher"""
    print("🧠 Starting Enhanced EEG Analysis Suite...")
    print("📁 Features: Auto-loading, Folder selection, Configurable bands, Full timeline")
    print("🎛️ Controls: Collapsible sidebar, Channel visibility, Y-axis scaling")
    print("⚡ Bands: Alpha, Beta, Theta, Delta, Gamma - All configurable!")
    
    try:
        from gui.main_window import main as gui_main
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
