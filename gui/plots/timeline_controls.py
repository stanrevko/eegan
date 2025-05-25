"""
Timeline Controls
Timeline slider and position controls
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt, pyqtSignal


class TimelineControls(QWidget):
    """Timeline position controls"""
    
    # Signals
    position_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.total_duration = 0
        self.current_position = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize timeline controls UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Timeline label
        self.timeline_label = QLabel("📍 Timeline:")
        self.timeline_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        layout.addWidget(self.timeline_label)
        
        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(1000)
        self.timeline_slider.setValue(0)
        self.timeline_slider.valueChanged.connect(self.on_slider_changed)
        self.timeline_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 8px;
                background: #3c3c3c;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #0078d4;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #106ebe;
            }
        """)
        layout.addWidget(self.timeline_slider)
        
        # Position display
        self.position_label = QLabel("0.0s / 0.0s")
        self.position_label.setStyleSheet("color: #ffffff; min-width: 100px;")
        layout.addWidget(self.position_label)
        
    def set_duration(self, duration):
        """Set total duration"""
        self.total_duration = duration
        self.update_position_display()
        
    def set_position(self, position):
        """Set current position"""
        # Ensure position is within bounds (0 to total_duration)
        self.current_position = max(0, min(position, self.total_duration))
        
        # Update slider without triggering signal
        if self.total_duration > 0:
            slider_value = int((self.current_position / self.total_duration) * 1000)
            self.timeline_slider.blockSignals(True)
            self.timeline_slider.setValue(slider_value)
            self.timeline_slider.blockSignals(False)
            
        self.update_position_display()        
    def on_slider_changed(self, value):
        """Handle slider value changes"""
        if self.total_duration > 0:
            new_position = (value / 1000.0) * self.total_duration
            # Ensure position stays within bounds
            self.current_position = max(0, min(new_position, self.total_duration))
            self.update_position_display()
            self.position_changed.emit(self.current_position)            
    def update_position_display(self):
        """Update position display"""
        self.position_label.setText(f"{self.current_position:.1f}s / {self.total_duration:.1f}s")
        
    def get_current_position(self):
        """Get current position"""
        return self.current_position
