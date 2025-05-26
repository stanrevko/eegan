#!/usr/bin/env python3
"""
Test script for the new Channel Selector
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from gui.analysis.channel_selector import ChannelSelector


class TestWindow(QMainWindow):
    """Simple test window for the channel selector"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔌 EEG Channel Selector Test")
        self.setGeometry(100, 100, 600, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create channel selector
        self.channel_selector = ChannelSelector()
        
        # Set some test channels
        test_channels = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T3', 'T4', 'T5', 'T6']
        self.channel_selector.set_channels(test_channels)
        
        # Connect signals
        self.channel_selector.channel_changed.connect(self.on_channel_changed)
        
        layout.addWidget(self.channel_selector)
        
        # Status label
        self.status_label = QLabel("Current channel: 0 - Fp1")
        self.status_label.setStyleSheet("color: #ffffff; font-size: 14px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        print("🎯 Test window created with channel selector")
        print(f"📊 Available channels: {len(test_channels)}")
        for i, name in enumerate(test_channels):
            print(f"   • Channel {i}: {name}")
            
    def on_channel_changed(self, channel_idx):
        """Handle channel changes"""
        channel_name = self.channel_selector.get_current_channel_name()
        print(f"🔌 Channel changed to: {channel_idx} - {channel_name}")
        self.status_label.setText(f"Current channel: {channel_idx} - {channel_name}")


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
    print("   • Use the channel dropdown to select different EEG channels")
    print("   • The status label will update to show the current selection")
    print("   • Console will show channel change events")
    print("   • Close the window to exit")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
