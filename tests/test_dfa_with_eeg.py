#!/usr/bin/env python3
"""
Test DFA Analysis with real EEG data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from gui.analysis.dfa_analysis import DFAAnalysis
from eeg.processor import EEGProcessor
from eeg.analyzer import EEGAnalyzer
import mne


class TestWindow(QMainWindow):
    """Test window for DFA with real EEG data"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 DFA Analysis - EEG Data Test")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create DFA analysis
        self.dfa_analysis = DFAAnalysis()
        
        # Load real EEG data
        self.setup_eeg_data()
        
        # Connect signals
        self.dfa_analysis.analysis_completed.connect(self.on_analysis_completed)
        
        layout.addWidget(self.dfa_analysis)
        
        print("🎯 DFA Analysis test with real EEG data")
        
    def setup_eeg_data(self):
        """Set up real EEG data"""
        try:
            # Load EEG file
            eeg_file = "/Users/stanrevko/projects/eegan/eeg_data/background-3f.edf"
            raw = mne.io.read_raw_edf(eeg_file, preload=True, verbose=False)
            print(f"📊 Loaded EEG: {len(raw.ch_names)} channels, {len(raw.times)} samples")
            
            # Set up processor
            processor = EEGProcessor()
            processor.set_raw_data(raw)
            
            # Set up analyzer
            analyzer = EEGAnalyzer()
            analyzer.set_processor(processor)
            
            # Set analyzer in DFA
            self.dfa_analysis.set_analyzer(analyzer)
            self.dfa_analysis.set_channel(0)  # Set to first channel
            
            print(f"✅ EEG data set up successfully")
            print(f"🔌 Channel 0: {raw.ch_names[0]}")
            
        except Exception as e:
            print(f"❌ Error setting up EEG data: {e}")
            
    def on_analysis_completed(self, alpha):
        """Handle analysis completion"""
        print(f"✅ DFA Analysis completed: α = {alpha:.4f}")


def main():
    """Run the test"""
    app = QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
    """)
    
    window = TestWindow()
    window.show()
    
    print("\n🚀 DFA Analysis with EEG data test is running!")
    print("📝 Instructions:")
    print("   • Real EEG data should be loaded automatically")
    print("   • Click 'Calculate DFA' to run analysis on EEG data")
    print("   • Expected result: α typically 0.5-1.5 for EEG signals")
    print("   • Close window to exit")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
