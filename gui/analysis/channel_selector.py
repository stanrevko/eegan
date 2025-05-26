"""
Channel Selector
EEG channel selection widget for analysis
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import pyqtSignal


class ChannelSelector(QWidget):
    """EEG channel selection widget"""
    
    # Signals
    channel_changed = pyqtSignal(int)  # channel index
    
    def __init__(self):
        super().__init__()
        self.channel_names = []
        self.current_channel = 0
        self._updating_programmatically = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the channel selector UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Channel selection label
        channel_label = QLabel("🔌 Channel:")
        channel_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        layout.addWidget(channel_label)
        
        # Channel dropdown
        self.channel_combo = QComboBox()
        self.channel_combo.currentIndexChanged.connect(self.on_channel_changed)
        self.channel_combo.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 5px;
                border-radius: 3px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                selection-background-color: #0078d4;
            }
        """)
        layout.addWidget(self.channel_combo)
        
    def set_channels(self, channel_names):
        """Set available channels"""
        self.channel_names = channel_names
        self.channel_combo.clear()
        
        # Add channels with index for clarity
        for i, name in enumerate(channel_names):
            # Clean up channel name (remove EEG prefix if present)
            clean_name = name.replace("EEG ", "") if name.startswith("EEG ") else name
            self.channel_combo.addItem(f"{i}: {clean_name}")
            
        # Set to first channel if available
        if len(channel_names) > 0:
            self.current_channel = 0
            self.channel_combo.setCurrentIndex(0)
            
    def on_channel_changed(self, index):
        """Handle channel selection changes"""
        if self._updating_programmatically:
            return  # Prevent recursion
            
        if 0 <= index < len(self.channel_names):
            self.current_channel = index
            self.channel_changed.emit(index)
            
    def get_current_channel(self):
        """Get currently selected channel index"""
        return self.current_channel
        
    def set_current_channel(self, channel_idx):
        """Set current channel selection"""
        if 0 <= channel_idx < len(self.channel_names):
            self._updating_programmatically = True
            self.current_channel = channel_idx
            self.channel_combo.setCurrentIndex(channel_idx)
            self._updating_programmatically = False
            
    def get_current_channel_name(self):
        """Get currently selected channel name"""
        if 0 <= self.current_channel < len(self.channel_names):
            name = self.channel_names[self.current_channel]
            # Clean up channel name (remove EEG prefix if present)
            return name.replace("EEG ", "") if name.startswith("EEG ") else name
        return ""
