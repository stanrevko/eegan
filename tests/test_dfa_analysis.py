#!/usr/bin/env python3
"""
Test script for DFA Analysis
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from gui.analysis.dfa_analysis import DFAAnalysis
import numpy as np


class TestWindow(QMainWindow):
    """Simple test window for DFA analysis"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 DFA Analysis Test")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create DFA analysis
        self.dfa_analysis = DFAAnalysis()
        
        # Generate test data (fractional Brownian motion)
        np.random.seed(42)
        n_samples = 2000
        test_data = np.cumsum(np.random.randn(n_samples))  # Brownian motion (alpha ≈ 1.5)
        
        # Set test data
        self.dfa_analysis.current_data = test_data
        self.dfa_analysis.sfreq = 500
        
        # Connect signals
        self.dfa_analysis.analysis_completed.connect(self.on_analysis_completed)
        
        layout.addWidget(self.dfa_analysis)
        
        print("🎯 DFA Analysis test window created")
        print(f"📊 Test data: {len(test_data)} samples (Brownian motion)")
        print("🔬 Click 'Calculate DFA' to test the analysis")
        
    def on_analysis_completed(self, alpha):
        """Handle analysis completion"""
        print(f"✅ DFA Analysis completed: α = {alpha:.4f}")
        if 1.3 <= alpha <= 1.7:
            print("🎉 Result looks correct for Brownian motion (expected α ≈ 1.5)")
        else:
            print("⚠️  Unexpected result - check algorithm")


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
    
    print("\n🚀 DFA Analysis test is running!")
    print("📝 Instructions:")
    print("   • Adjust parameters if needed (default should work)")
    print("   • Click 'Calculate DFA' to run analysis")
    print("   • Expected result: α ≈ 1.5 for Brownian motion")
    print("   • Check the log-log plot for linearity")
    print("   • Close window to exit")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
