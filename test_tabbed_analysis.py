#!/usr/bin/env python3
"""
Test script for the new Tabbed Analysis Panel
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from gui.analysis import TabbedAnalysisPanel


class TestWindow(QMainWindow):
    """Simple test window for the tabbed analysis panel"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 EEG Tabbed Analysis Panel Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create tabbed analysis panel
        self.analysis_panel = TabbedAnalysisPanel()
        
        # Connect signals
        self.analysis_panel.band_changed.connect(self.on_band_changed)
        self.analysis_panel.spike_detected.connect(self.on_spike_detected)
        
        layout.addWidget(self.analysis_panel)
        
        print("🎯 Test window created with tabbed analysis panel")
        print(f"📊 Available tabs: {self.analysis_panel.tab_widget.count()}")
        for i in range(self.analysis_panel.tab_widget.count()):
            tab_text = self.analysis_panel.tab_widget.tabText(i)
            print(f"   • Tab {i}: {tab_text}")
            
    def on_band_changed(self, band_name):
        """Handle band changes"""
        print(f"🎵 Band changed to: {band_name}")
        
    def on_spike_detected(self, spike_time, band_name):
        """Handle spike detection"""
        print(f"⚡ Spike detected: {band_name} at {spike_time:.2f}s")


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
    
    print("\n🚀 Test window is now running!")
    print("📝 Instructions:")
    print("   • Switch between tabs to test different analysis tools")
    print("   • Try changing frequency bands using the band selector")
    print("   • In the 'Band Spikes' tab, click 'Detect Spikes' to test spike detection")
    print("   • Use checkboxes in 'All Bands' tab to toggle band visibility")
    print("   • Close the window to exit")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
