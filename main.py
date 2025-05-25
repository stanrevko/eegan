#!/usr/bin/env python3
"""
EEG Analysis Application
Main entry point for the minimal GUI version
"""

import sys
import os

# Add project directories to Python path
sys.path.append(os.path.dirname(__file__))

from gui.main_window import main

if __name__ == "__main__":
    print("🧠 Starting EEG Analysis Application...")
    print("📁 Loading from: /Users/stanrevko/projects/eegan/eeg_data")
    main()
