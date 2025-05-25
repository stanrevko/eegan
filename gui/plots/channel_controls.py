"""
Channel Controls
Channel visibility and scaling controls
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QCheckBox, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal


class ChannelControls(QWidget):
    """Channel visibility and scaling controls"""
    
    # Signals
    visibility_changed = pyqtSignal(list)
    scale_changed = pyqtSignal(int)
    spacing_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.channel_checkboxes = {}
        self.available_channels = 0
        self.eeg_scale = 200
        self.channel_spacing = 3
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize channel controls UI"""
        layout = QVBoxLayout(self)
        
        # Scaling controls group
        scaling_group = QGroupBox("🎛️ EEG Display")
        scaling_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        scaling_layout = QVBoxLayout(scaling_group)
        
        # Y-axis scale control
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Y-scale:"))
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(1000)
        self.scale_slider.setValue(self.eeg_scale)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(self.scale_slider)
        
        self.scale_label = QLabel(f"{self.eeg_scale}μV")
        self.scale_label.setMinimumWidth(60)
        scale_layout.addWidget(self.scale_label)
        
        scaling_layout.addLayout(scale_layout)
        
        # Channel spacing control
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(QLabel("Spacing:"))
        
        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setMinimum(1)
        self.spacing_slider.setMaximum(10)
        self.spacing_slider.setValue(self.channel_spacing)
        self.spacing_slider.valueChanged.connect(self.on_spacing_changed)
        spacing_layout.addWidget(self.spacing_slider)
        
        self.spacing_label = QLabel(f"{self.channel_spacing}x")
        self.spacing_label.setMinimumWidth(60)
        spacing_layout.addWidget(self.spacing_label)
        
        scaling_layout.addLayout(spacing_layout)
        layout.addWidget(scaling_group)
        
        # Channel visibility group
        channels_group = QGroupBox("📺 Channel Visibility")
        channels_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        channels_layout = QVBoxLayout(channels_group)
        
        # Available channels info
        self.channels_info_label = QLabel("📊 No channels available")
        self.channels_info_label.setStyleSheet("color: #888888; font-style: italic;")
        channels_layout.addWidget(self.channels_info_label)
        
        # Scrollable channel list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #555555;
                background-color: #3c3c3c;
            }
        """)
        
        self.channels_widget = QWidget()
        self.channels_layout = QVBoxLayout(self.channels_widget)
        scroll_area.setWidget(self.channels_widget)
        channels_layout.addWidget(scroll_area)
        
        layout.addWidget(channels_group)
        
    def clean_channel_name(self, channel_name):
        """Remove 'EEG' prefix from channel names"""
        return channel_name[4:] if channel_name.startswith('EEG ') else channel_name
        
    def set_channels(self, channel_names):
        """Set available channels with color coding"""
        # Clear existing checkboxes
        for checkbox in self.channel_checkboxes.values():
            checkbox.deleteLater()
        self.channel_checkboxes.clear()
        
        self.available_channels = len(channel_names)
        
        # Update info label
        self.channels_info_label.setText(f"📊 {self.available_channels} channels available")
        
        # EEG plot colors (same as in EEGPlotWidget)
        colors = ["#00bfff", "#ff4444", "#44ff44", "#ff8800", "#8844ff", 
                 "#ff44ff", "#ffff44", "#88ffff"]
        
        # Create checkboxes for each channel
        for i, channel_name in enumerate(channel_names):
            clean_name = self.clean_channel_name(channel_name)
            color = colors[i % len(colors)]  # Cycle through colors
            
            checkbox = QCheckBox(f"{i+1:2d}. {clean_name}")
            checkbox.setChecked(True)  # All channels visible by default
            checkbox.stateChanged.connect(self.on_channel_visibility_changed)
            
            # Apply color styling to match EEG plot
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {color};
                    font-weight: bold;
                    padding: 2px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                QCheckBox::indicator:unchecked {{
                    border: 1px solid #555555;
                    background-color: #2b2b2b;
                }}
                QCheckBox::indicator:checked {{
                    border: 1px solid {color};
                    background-color: {color};
                }}
            """)
            
            self.channel_checkboxes[i] = checkbox
            self.channels_layout.addWidget(checkbox)
            
        # Emit initial visibility
        self.on_channel_visibility_changed()
        
    def on_scale_changed(self, value):
        """Handle scale changes"""
        self.eeg_scale = value
        self.scale_label.setText(f"{value}μV")
        self.scale_changed.emit(value)
        
    def on_spacing_changed(self, value):
        """Handle spacing changes"""
        self.channel_spacing = value
        self.spacing_label.setText(f"{value}x")
        self.spacing_changed.emit(value)
        
    def on_channel_visibility_changed(self):
        """Handle channel visibility changes"""
        visible_channels = []
        for i, checkbox in self.channel_checkboxes.items():
            if checkbox.isChecked():
                visible_channels.append(i)
                
        self.visibility_changed.emit(visible_channels)
        
    def get_visible_channels(self):
        """Get currently visible channels"""
        visible_channels = []
        for i, checkbox in self.channel_checkboxes.items():
            if checkbox.isChecked():
                visible_channels.append(i)
        return visible_channels
        
    def set_scale(self, scale):
        """Set scale value"""
        self.scale_slider.blockSignals(True)
        self.scale_slider.setValue(scale)
        self.scale_slider.blockSignals(False)
        self.on_scale_changed(scale)
        
    def set_spacing(self, spacing):
        """Set spacing value"""
        self.spacing_slider.blockSignals(True)
        self.spacing_slider.setValue(spacing)
        self.spacing_slider.blockSignals(False)
        self.on_spacing_changed(spacing)
