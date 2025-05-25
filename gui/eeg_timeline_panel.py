"""
EEG Timeline Panel Module - Clean channel names
Full timeline EEG display with cleaned channel names (no "EEG" prefix)
"""

import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QCheckBox, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg
from utils.ui_helpers import setup_dark_plot, create_styled_button


class EEGTimelinePanel(QWidget):
    """Enhanced EEG timeline panel with clean channel names"""
    
    # Signals
    timeline_changed = pyqtSignal(float)
    channel_visibility_changed = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.processor = None
        self.total_duration = 0
        self.current_position = 0
        self.visible_channels = []
        self.eeg_scale = 200
        self.channel_spacing = 3
        self.channel_checkboxes = {}
        self.available_channels = 0
        
        self.init_ui()
        
    def clean_channel_name(self, channel_name):
        """Remove 'EEG' prefix from channel names"""
        if channel_name.startswith('EEG '):
            return channel_name[4:]  # Remove 'EEG ' (4 characters)
        return channel_name
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        title = QLabel("🧠 EEG Signal Visualization (Full Timeline)")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Scale control
        scale_label = QLabel("Scale:")
        scale_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(scale_label)
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 1000)
        self.scale_slider.setValue(200)
        self.scale_slider.setMaximumWidth(150)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        header_layout.addWidget(self.scale_slider)
        
        self.scale_label = QLabel("200μV")
        self.scale_label.setStyleSheet("color: #cccccc;")
        header_layout.addWidget(self.scale_label)
        
        # Channel controls button
        self.channel_controls_button = create_styled_button("📋 Channels", "secondary")
        self.channel_controls_button.setCheckable(True)
        self.channel_controls_button.toggled.connect(self.toggle_channel_controls)
        header_layout.addWidget(self.channel_controls_button)
        
        layout.addLayout(header_layout)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # EEG plot
        self.eeg_plot = pg.PlotWidget(background='#2b2b2b')
        setup_dark_plot(self.eeg_plot, 'Time (seconds)', 'Channels')
        self.eeg_plot.setLimits(xMin=0, yMin=0)
        self.eeg_plot.getViewBox().setMouseEnabled(x=True, y=False)
        content_layout.addWidget(self.eeg_plot, stretch=3)
        
        # Channel controls (hidden initially)
        self.channel_controls_widget = self.create_channel_controls()
        self.channel_controls_widget.setVisible(False)
        content_layout.addWidget(self.channel_controls_widget)
        
        layout.addLayout(content_layout)
        
        # Timeline controls
        timeline_group = QGroupBox("Timeline Controls")
        timeline_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        timeline_layout = QHBoxLayout(timeline_group)
        
        # Position label
        self.position_label = QLabel("0.0s / 0.0s")
        self.position_label.setStyleSheet("color: #cccccc;")
        timeline_layout.addWidget(self.position_label)
        
        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.setValue(0)
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)
        self.timeline_slider.setEnabled(False)
        timeline_layout.addWidget(self.timeline_slider, stretch=2)
        
        layout.addWidget(timeline_group)
        
        # Info label
        self.info_label = QLabel("Load an EEG file to view full timeline")
        self.info_label.setStyleSheet("padding: 8px; background: #3c3c3c; border-radius: 4px; color: #cccccc;")
        layout.addWidget(self.info_label)
        
    def create_channel_controls(self):
        """Create enhanced channel visibility controls"""
        widget = QWidget()
        widget.setMaximumWidth(280)
        widget.setMinimumHeight(500)
        widget.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 4px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        # Title with channel count
        self.channel_title = QLabel("Channel Visibility")
        self.channel_title.setStyleSheet("color: #ffffff; font-weight: bold; padding: 8px; font-size: 13px;")
        layout.addWidget(self.channel_title)
        
        # All/None buttons
        button_layout = QHBoxLayout()
        
        self.select_all_btn = create_styled_button("All", "secondary")
        self.select_all_btn.clicked.connect(self.select_all_channels)
        button_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = create_styled_button("None", "secondary")
        self.select_none_btn.clicked.connect(self.select_no_channels)
        button_layout.addWidget(self.select_none_btn)
        
        # Available channels button
        self.available_only_btn = create_styled_button("Available", "secondary")
        self.available_only_btn.clicked.connect(self.select_available_channels)
        button_layout.addWidget(self.available_only_btn)
        
        layout.addLayout(button_layout)
        
        # Info about available channels
        self.channel_info_label = QLabel("0/0 channels available")
        self.channel_info_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 4px; text-align: center;")
        layout.addWidget(self.channel_info_label)
        
        # Scrollable channel list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(350)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                background-color: #3c3c3c;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #0078d4;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #106ebe;
            }
        """)
        
        self.channel_checkboxes_widget = QWidget()
        self.channel_checkboxes_layout = QVBoxLayout(self.channel_checkboxes_widget)
        
        scroll_area.setWidget(self.channel_checkboxes_widget)
        layout.addWidget(scroll_area)
        
        return widget
        
    def set_processor(self, processor):
        """Set the EEG processor"""
        self.processor = processor
        
        if processor:
            self.total_duration = processor.get_duration()
            self.timeline_slider.setEnabled(True)
            self.timeline_slider.setRange(0, int(self.total_duration * 10))
            self.timeline_slider.setValue(0)
            self.current_position = 0
            
            # Get actual number of channels in file
            self.available_channels = len(processor.get_channel_names())
            
            self.setup_channel_controls()
            self.update_timeline_display()
            
            info = processor.raw.info
            info_text = f"📊 {info['nchan']} channels | ⚡ {info['sfreq']} Hz | ⏱️ {self.total_duration:.1f}s"
            self.info_label.setText(info_text)
        else:
            self.timeline_slider.setEnabled(False)
            self.info_label.setText("Load an EEG file to view full timeline")
            
    def setup_channel_controls(self):
        """Setup enhanced channel checkboxes with clean names"""
        if not self.processor:
            return
            
        # Clear existing
        for checkbox in self.channel_checkboxes.values():
            checkbox.deleteLater()
        self.channel_checkboxes.clear()
        
        # Get actual channel names from file
        actual_channel_names = self.processor.get_channel_names()
        
        # Standard channel names without "EEG" prefix
        standard_channels = [
            'Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 
            'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 
            'T3', 'T4', 'T5', 'T6', 'Fz', 'Cz', 
            'Pz', 'A1', 'A2', 'Pg1', 'Pg2'
        ]
        
        colors = ['#00bfff', '#ff4444', '#44ff44', '#ff8800', '#8844ff', '#ff44ff', '#ffff44', '#88ffff']
        
        # Create checkboxes for all standard channels
        for i, standard_name in enumerate(standard_channels):
            checkbox = QCheckBox(standard_name)
            
            # Check if this channel exists in the actual file
            channel_exists = i < len(actual_channel_names)
            
            if channel_exists:
                # Channel exists - use clean name from file
                clean_name = self.clean_channel_name(actual_channel_names[i])
                checkbox.setText(clean_name)
                
                # Normal styling and functionality
                checkbox.setEnabled(True)
                checkbox.setChecked(i < 8)  # First 8 visible by default
                checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        color: {colors[i % len(colors)]};
                        font-weight: bold;
                        padding: 6px;
                        font-size: 12px;
                    }}
                    QCheckBox::indicator {{
                        width: 18px;
                        height: 18px;
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {colors[i % len(colors)]};
                        border: 2px solid {colors[i % len(colors)]};
                        border-radius: 3px;
                    }}
                    QCheckBox::indicator:unchecked {{
                        background-color: #3c3c3c;
                        border: 2px solid #555555;
                        border-radius: 3px;
                    }}
                """)
            else:
                # Channel doesn't exist - disabled styling
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
                checkbox.setText(f"{standard_name} (not available)")
                checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        color: #666666;
                        font-weight: normal;
                        padding: 6px;
                        font-size: 12px;
                    }}
                    QCheckBox::indicator {{
                        width: 18px;
                        height: 18px;
                        background-color: #2b2b2b;
                        border: 2px solid #444444;
                        border-radius: 3px;
                    }}
                """)
            
            checkbox.stateChanged.connect(self.on_channel_visibility_changed)
            
            self.channel_checkboxes[i] = checkbox
            self.channel_checkboxes_layout.addWidget(checkbox)
            
        # Update title and info
        available_count = len(actual_channel_names)
        total_standard = len(standard_channels)
        
        self.channel_title.setText(f"Channel Visibility ({available_count}/{total_standard})")
        self.channel_info_label.setText(f"{available_count} channels available in file")
        
        # Update visible channels list
        self.update_visible_channels()
        
    def update_visible_channels(self):
        """Update visible channels list (only for available channels)"""
        self.visible_channels = []
        
        for i, checkbox in self.channel_checkboxes.items():
            if checkbox.isEnabled() and checkbox.isChecked():
                # Only include channels that exist in the file
                if i < self.available_channels:
                    self.visible_channels.append(i)
        
        self.channel_visibility_changed.emit(self.visible_channels)
        self.update_timeline_display()
        
    def on_channel_visibility_changed(self):
        """Handle channel visibility change"""
        self.update_visible_channels()
        
    def select_all_channels(self):
        """Select all available channels"""
        for i, checkbox in self.channel_checkboxes.items():
            if checkbox.isEnabled():  # Only select available channels
                checkbox.setChecked(True)
            
    def select_no_channels(self):
        """Deselect all channels"""
        for checkbox in self.channel_checkboxes.values():
            checkbox.setChecked(False)
            
    def select_available_channels(self):
        """Select only the available channels"""
        for i, checkbox in self.channel_checkboxes.items():
            if checkbox.isEnabled():  # Available channel
                checkbox.setChecked(i < 8)  # First 8 available channels
            else:  # Unavailable channel
                checkbox.setChecked(False)
                
    def toggle_channel_controls(self, visible):
        """Toggle channel controls visibility"""
        self.channel_controls_widget.setVisible(visible)
        
    def on_scale_changed(self, value):
        """Handle scale change"""
        self.eeg_scale = value
        self.scale_label.setText(f"{value}μV")
        self.update_timeline_display()
        
    def on_timeline_changed(self, value):
        """Handle timeline change"""
        if self.processor:
            self.current_position = value / 10.0
            self.position_label.setText(f"{self.current_position:.1f}s / {self.total_duration:.1f}s")
            self.timeline_changed.emit(self.current_position)
            
    def update_timeline_display(self):
        """Update the EEG display with clean channel names"""
        if not self.processor or not self.visible_channels:
            self.eeg_plot.clear()
            return
            
        try:
            # Get full data
            data, times = self.processor.raw.get_data(return_times=True)
            data_uv = data * 1e6
            
            self.eeg_plot.clear()
            
            # Plot visible channels
            colors = ['#00bfff', '#ff4444', '#44ff44', '#ff8800', '#8844ff', '#ff44ff', '#ffff44', '#88ffff']
            channel_names = self.processor.get_channel_names()
            
            for plot_idx, channel_idx in enumerate(self.visible_channels):
                if channel_idx < len(data):
                    y_offset = (plot_idx + 1) * self.channel_spacing
                    normalized_signal = (data_uv[channel_idx] / self.eeg_scale) * 0.8 + y_offset
                    
                    color = colors[channel_idx % len(colors)]
                    self.eeg_plot.plot(times, normalized_signal, 
                                     pen=pg.mkPen(color=color, width=1))
                    
                    # Channel label with clean name (no "EEG" prefix)
                    clean_name = self.clean_channel_name(channel_names[channel_idx])
                    text_item = pg.TextItem(clean_name, 
                                          color=color, anchor=(0, 0.5))
                    self.eeg_plot.addItem(text_item)
                    text_item.setPos(times[0], y_offset)
            
            # Set ranges - no negative values
            if times.size > 0:
                self.eeg_plot.setXRange(0, times[-1])
                max_y = len(self.visible_channels) * self.channel_spacing + self.channel_spacing
                self.eeg_plot.setYRange(0, max_y)
                
        except Exception as e:
            print(f"Error updating timeline: {e}")
            
    def get_visible_channels(self):
        """Get visible channel indices"""
        return self.visible_channels.copy()
