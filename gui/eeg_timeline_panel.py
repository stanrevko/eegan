"""
EEG Timeline Panel Module - Simplified clean version
Full timeline with proper X-axis limits matching recording duration
"""

import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QCheckBox, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg
from utils.ui_helpers import setup_dark_plot, create_styled_button


class EEGTimelinePanel(QWidget):
    """EEG timeline panel with proper recording duration limits"""
    
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
        return channel_name[4:] if channel_name.startswith('EEG ') else channel_name
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Header
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
        timeline_group.setStyleSheet("QGroupBox { color: #ffffff; border: 1px solid #555555; border-radius: 4px; margin-top: 10px; padding-top: 10px; }")
        
        timeline_layout = QHBoxLayout(timeline_group)
        
        self.position_label = QLabel("0.0s / 0.0s")
        self.position_label.setStyleSheet("color: #cccccc;")
        timeline_layout.addWidget(self.position_label)
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.setValue(0)
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)
        self.timeline_slider.setEnabled(False)
        timeline_layout.addWidget(self.timeline_slider, stretch=2)
        
        start_btn = create_styled_button("⏮ Start", "secondary")
        start_btn.clicked.connect(lambda: self.timeline_slider.setValue(0))
        timeline_layout.addWidget(start_btn)
        
        end_btn = create_styled_button("⏭ End", "secondary")
        end_btn.clicked.connect(lambda: self.timeline_slider.setValue(int(self.total_duration * 10)) if self.processor else None)
        timeline_layout.addWidget(end_btn)
        
        layout.addWidget(timeline_group)
        
        # Info label
        self.info_label = QLabel("Load an EEG file to view full timeline")
        self.info_label.setStyleSheet("padding: 8px; background: #3c3c3c; border-radius: 4px; color: #cccccc;")
        layout.addWidget(self.info_label)
        
    def create_channel_controls(self):
        """Create channel visibility controls"""
        widget = QWidget()
        widget.setMaximumWidth(280)
        widget.setMinimumHeight(500)
        widget.setStyleSheet("QWidget { background-color: #3c3c3c; border: 1px solid #555555; border-radius: 4px; }")
        
        layout = QVBoxLayout(widget)
        
        self.channel_title = QLabel("Channel Visibility")
        self.channel_title.setStyleSheet("color: #ffffff; font-weight: bold; padding: 8px; font-size: 13px;")
        layout.addWidget(self.channel_title)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.select_all_btn = create_styled_button("All", "secondary")
        self.select_all_btn.clicked.connect(self.select_all_channels)
        button_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = create_styled_button("None", "secondary")
        self.select_none_btn.clicked.connect(self.select_no_channels)
        button_layout.addWidget(self.select_none_btn)
        
        layout.addLayout(button_layout)
        
        self.channel_info_label = QLabel("0/0 channels available")
        self.channel_info_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 4px;")
        layout.addWidget(self.channel_info_label)
        
        # Scrollable channel list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(350)
        
        self.channel_checkboxes_widget = QWidget()
        self.channel_checkboxes_layout = QVBoxLayout(self.channel_checkboxes_widget)
        scroll_area.setWidget(self.channel_checkboxes_widget)
        layout.addWidget(scroll_area)
        
        return widget
        
    def set_processor(self, processor):
        """Set the EEG processor and configure timeline bounds"""
        self.processor = processor
        
        if processor:
            self.total_duration = processor.get_duration()
            self.timeline_slider.setEnabled(True)
            self.timeline_slider.setRange(0, int(self.total_duration * 10))
            self.timeline_slider.setValue(0)
            self.current_position = 0
            
            # Set plot X-axis limits to exact recording duration
            self.eeg_plot.setLimits(xMin=0, xMax=self.total_duration, yMin=0)
            
            self.available_channels = len(processor.get_channel_names())
            self.setup_channel_controls()
            self.update_timeline_display()
            
            info = processor.raw.info
            info_text = f"📊 {info['nchan']} channels | ⚡ {info['sfreq']} Hz | ⏱️ {self.total_duration:.1f}s"
            self.info_label.setText(info_text)
        else:
            self.timeline_slider.setEnabled(False)
            
    def setup_channel_controls(self):
        """Setup channel checkboxes"""
        if not self.processor:
            return
            
        # Clear existing
        for checkbox in self.channel_checkboxes.values():
            checkbox.deleteLater()
        self.channel_checkboxes.clear()
        
        actual_channel_names = self.processor.get_channel_names()
        colors = ['#00bfff', '#ff4444', '#44ff44', '#ff8800', '#8844ff', '#ff44ff', '#ffff44', '#88ffff']
        
        for i, channel_name in enumerate(actual_channel_names):
            clean_name = self.clean_channel_name(channel_name)
            checkbox = QCheckBox(clean_name)
            checkbox.setEnabled(True)
            checkbox.setChecked(i < 8)  # First 8 visible
            checkbox.setStyleSheet(f"QCheckBox {{ color: {colors[i % len(colors)]}; font-weight: bold; padding: 6px; font-size: 12px; }}")
            checkbox.stateChanged.connect(self.on_channel_visibility_changed)
            
            self.channel_checkboxes[i] = checkbox
            self.channel_checkboxes_layout.addWidget(checkbox)
            
        self.channel_title.setText(f"Channel Visibility ({len(actual_channel_names)})")
        self.channel_info_label.setText(f"{len(actual_channel_names)} channels available")
        self.update_visible_channels()
        
    def update_visible_channels(self):
        """Update visible channels list"""
        self.visible_channels = [i for i, checkbox in self.channel_checkboxes.items() if checkbox.isChecked()]
        self.channel_visibility_changed.emit(self.visible_channels)
        self.update_timeline_display()
        
    def on_channel_visibility_changed(self):
        """Handle channel visibility change"""
        self.update_visible_channels()
        
    def select_all_channels(self):
        """Select all channels"""
        for checkbox in self.channel_checkboxes.values():
            checkbox.setChecked(True)
            
    def select_no_channels(self):
        """Deselect all channels"""
        for checkbox in self.channel_checkboxes.values():
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
            self.current_position = min(value / 10.0, self.total_duration)
            self.position_label.setText(f"{self.current_position:.1f}s / {self.total_duration:.1f}s")
            self.timeline_changed.emit(self.current_position)
            
    def update_timeline_display(self):
        """Update the EEG display"""
        if not self.processor or not self.visible_channels:
            self.eeg_plot.clear()
            return
            
        try:
            data, times = self.processor.raw.get_data(return_times=True)
            data_uv = data * 1e6
            
            self.eeg_plot.clear()
            
            colors = ['#00bfff', '#ff4444', '#44ff44', '#ff8800', '#8844ff', '#ff44ff', '#ffff44', '#88ffff']
            channel_names = self.processor.get_channel_names()
            
            for plot_idx, channel_idx in enumerate(self.visible_channels):
                if channel_idx < len(data):
                    y_offset = (plot_idx + 1) * self.channel_spacing
                    normalized_signal = (data_uv[channel_idx] / self.eeg_scale) * 0.8 + y_offset
                    
                    color = colors[channel_idx % len(colors)]
                    self.eeg_plot.plot(times, normalized_signal, pen=pg.mkPen(color=color, width=1))
                    
                    clean_name = self.clean_channel_name(channel_names[channel_idx])
                    text_item = pg.TextItem(clean_name, color=color, anchor=(0, 0.5))
                    self.eeg_plot.addItem(text_item)
                    text_item.setPos(times[0], y_offset)
            
            if times.size > 0:
                # X-axis: 0 to exact recording duration
                self.eeg_plot.setXRange(0, self.total_duration)
                
                max_y = len(self.visible_channels) * self.channel_spacing + self.channel_spacing
                self.eeg_plot.setYRange(0, max_y)
                
        except Exception as e:
            print(f"Error updating timeline: {e}")
            
    def get_visible_channels(self):
        """Get visible channel indices"""
        return self.visible_channels.copy()
        
    def get_current_position(self):
        """Get current timeline position"""
        return self.current_position
        
    def get_total_duration(self):
        """Get total recording duration"""
        return self.total_duration
