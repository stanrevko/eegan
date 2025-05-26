"""
Analysis Controls
Controls for analysis parameters and display
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox
from PyQt5.QtCore import pyqtSignal


class AnalysisControls(QWidget):
    """Analysis parameter controls"""
    
    # Signals
    window_size_changed = pyqtSignal(float)
    step_size_changed = pyqtSignal(float)
    channel_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.window_size = 2.0
        self.step_size = 0.5
        self.current_channel = 0
        self._updating_programmatically = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize analysis controls UI"""
        layout = QVBoxLayout(self)
        
        # Window size control
        window_layout = QHBoxLayout()
        window_layout.addWidget(QLabel("Window:"))
        
        self.window_spinbox = QSpinBox()
        self.window_spinbox.setRange(1, 10)
        self.window_spinbox.setValue(int(self.window_size))
        self.window_spinbox.setSuffix("s")
        self.window_spinbox.valueChanged.connect(self.on_window_size_changed)
        self.window_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px;
                border-radius: 3px;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #555555;
                border: none;
                width: 16px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #666666;
            }
        """)
        window_layout.addWidget(self.window_spinbox)
        window_layout.addStretch()
        
        layout.addLayout(window_layout)
        
        # Step size control
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Step:"))
        
        self.step_spinbox = QSpinBox()
        self.step_spinbox.setRange(1, 20)
        self.step_spinbox.setValue(int(self.step_size * 10))  # Convert to deciseconds
        self.step_spinbox.setSuffix("0ms")
        self.step_spinbox.valueChanged.connect(self.on_step_size_changed)
        self.step_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px;
                border-radius: 3px;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #555555;
                border: none;
                width: 16px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #666666;
            }
        """)
        step_layout.addWidget(self.step_spinbox)
        step_layout.addStretch()
        
        layout.addLayout(step_layout)
        
        # Channel info display
        self.channel_label = QLabel("Channel: 0")
        self.channel_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(self.channel_label)
        
    def on_window_size_changed(self, value):
        """Handle window size changes"""
        self.window_size = float(value)
        self.window_size_changed.emit(self.window_size)
        
    def on_step_size_changed(self, value):
        """Handle step size changes"""
        self.step_size = value / 10.0  # Convert from deciseconds
        self.step_size_changed.emit(self.step_size)
        
    def set_channel(self, channel_idx):
        """Set current channel"""
        self.current_channel = channel_idx
        self.channel_label.setText(f"Channel: {channel_idx}")
        if not self._updating_programmatically:
            self.channel_changed.emit(channel_idx)
        
    def get_window_size(self):
        """Get window size"""
        return self.window_size
        
    def get_step_size(self):
        """Get step size"""
        return self.step_size
        
    def get_current_channel(self):
        """Get current channel"""
        return self.current_channel
