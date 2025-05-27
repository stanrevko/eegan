"""
EEG Timeline Analysis
Main EEG signal display as an analysis tab
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QSpinBox, QPushButton, QCheckBox, QGroupBox,
                             QScrollArea, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt
from utils.ui_helpers import setup_dark_plot


class EEGTimelineAnalysis(QWidget):
    """EEG Timeline analysis widget for signal visualization"""
    
    # Signals
    time_changed = pyqtSignal(float)  # current time position
    channel_visibility_changed = pyqtSignal(int, bool)  # channel, visible
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.current_channel = 0
        self.current_time = 0
        self.duration = 0
        self.y_scale = 200  # microvolts
        self.spacing = 3
        self.visible_channels = {}
        self.channel_names = []
        self.window_size = 10.0  # seconds visible
        self.time_offset = 0.0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the EEG timeline UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls panel
        controls_layout = QHBoxLayout()
        
        # Time controls
        time_group = QGroupBox("Time Navigation")
        time_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
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
        time_layout = QVBoxLayout(time_group)
        
        # Time slider
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(1000)
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self.on_time_slider_changed)
        self.time_slider.setStyleSheet("""
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
                border-radius: 3px;
            }
        """)
        time_layout.addWidget(self.time_slider)
        
        # Time info
        time_info_layout = QHBoxLayout()
        self.time_label = QLabel("Time: 0.0s / 0.0s")
        self.time_label.setStyleSheet("color: #888888;")
        time_info_layout.addWidget(self.time_label)
        
        # Window size control
        time_info_layout.addWidget(QLabel("Window:"))
        self.window_spinbox = QSpinBox()
        self.window_spinbox.setRange(5, 60)
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
        """)
        time_info_layout.addWidget(self.window_spinbox)
        time_info_layout.addStretch()
        
        time_layout.addLayout(time_info_layout)
        controls_layout.addWidget(time_group)
        
        # Display controls
        display_group = QGroupBox("Display")
        display_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
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
        display_layout = QVBoxLayout(display_group)
        
        # Y-scale control
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Y-Scale:"))
        self.scale_spinbox = QSpinBox()
        self.scale_spinbox.setRange(50, 1000)
        self.scale_spinbox.setValue(self.y_scale)
        self.scale_spinbox.setSuffix("μV")
        self.scale_spinbox.valueChanged.connect(self.on_scale_changed)
        self.scale_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px;
                border-radius: 3px;
                min-width: 70px;
            }
        """)
        scale_layout.addWidget(self.scale_spinbox)
        
        # Spacing control
        scale_layout.addWidget(QLabel("Spacing:"))
        self.spacing_spinbox = QSpinBox()
        self.spacing_spinbox.setRange(1, 10)
        self.spacing_spinbox.setValue(self.spacing)
        self.spacing_spinbox.setSuffix("x")
        self.spacing_spinbox.valueChanged.connect(self.on_spacing_changed)
        self.spacing_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px;
                border-radius: 3px;
                min-width: 60px;
            }
        """)
        scale_layout.addWidget(self.spacing_spinbox)
        scale_layout.addStretch()
        
        display_layout.addLayout(scale_layout)
        controls_layout.addWidget(display_group)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Main content area with channel list and plot
        content_layout = QHBoxLayout()
        
        # Channel visibility controls
        channels_frame = QFrame()
        channels_frame.setMaximumWidth(200)
        channels_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 5px;
            }
        """)
        channels_layout = QVBoxLayout(channels_frame)
        
        channels_label = QLabel("Channel Visibility")
        channels_label.setStyleSheet("font-weight: bold; color: #ffffff; padding: 5px;")
        channels_layout.addWidget(channels_label)
        
        # Scrollable channel list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #3c3c3c;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
            }
        """)
        
        self.channels_widget = QWidget()
        self.channels_layout = QVBoxLayout(self.channels_widget)
        self.channels_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area.setWidget(self.channels_widget)
        channels_layout.addWidget(scroll_area)
        
        content_layout.addWidget(channels_frame)
        
        # EEG Plot
        self.plot_widget = pg.PlotWidget()
        setup_dark_plot(self.plot_widget, "Time (seconds)", "Channels")
        
        # Configure plot
        self.plot_widget.showGrid(x=True, y=False, alpha=0.3)
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMin=0)
        self.plot_widget.getPlotItem().showAxis('left', False)  # Hide left axis
        
        # Add current time line
        self.time_line = pg.InfiniteLine(pos=0, angle=90, 
                                        pen=pg.mkPen(color='#00ff00', width=2, style=2))
        self.plot_widget.addItem(self.time_line)
        
        content_layout.addWidget(self.plot_widget, 1)
        layout.addLayout(content_layout)
        
    def on_time_slider_changed(self, value):
        """Handle time slider changes"""
        if self.duration > 0:
            self.current_time = (value / 1000.0) * self.duration
            self.time_offset = max(0, self.current_time - self.window_size / 2)
            self.update_time_display()
            self.update_plot()
            self.time_changed.emit(self.current_time)
            
    def on_window_size_changed(self, value):
        """Handle window size changes"""
        self.window_size = float(value)
        self.update_plot()
        
    def on_scale_changed(self, value):
        """Handle Y-scale changes"""
        self.y_scale = value
        self.update_plot()
        
    def on_spacing_changed(self, value):
        """Handle spacing changes"""
        self.spacing = value
        self.update_plot()
        
    def on_channel_visibility_changed(self, channel_idx, checked):
        """Handle channel visibility changes"""
        self.visible_channels[channel_idx] = checked
        self.update_plot()
        self.channel_visibility_changed.emit(channel_idx, checked)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        if analyzer and hasattr(analyzer, 'processor') and analyzer.processor:
            self.duration = analyzer.processor.get_duration()
            self.channel_names = analyzer.processor.get_channel_names()
            self.setup_channel_controls()
            self.time_slider.setMaximum(1000)
            self.update_time_display()
        self.update_plot()
        
    def set_channel(self, channel_idx):
        """Set the current channel"""
        self.current_channel = channel_idx
        
    def set_time_window(self, current_time, total_duration):
        """Set the current time window"""
        self.current_time = max(0, current_time)
        self.duration = total_duration
        if total_duration > 0:
            slider_value = int((current_time / total_duration) * 1000)
            self.time_slider.setValue(slider_value)
        self.update_time_display()
        self.update_plot()
        
    def setup_channel_controls(self):
        """Setup channel visibility controls"""
        # Clear existing controls
        for i in reversed(range(self.channels_layout.count())):
            self.channels_layout.itemAt(i).widget().setParent(None)
            
        # Channel colors
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # Add channel checkboxes
        for i, name in enumerate(self.channel_names):
            clean_name = name.replace("EEG ", "") if name.startswith("EEG ") else name
            
            checkbox = QCheckBox(f"{i+1}: {clean_name}")
            checkbox.setChecked(i < 10)  # Show first 10 channels by default
            checkbox.stateChanged.connect(
                lambda state, idx=i: self.on_channel_visibility_changed(idx, state)
            )
            
            color = colors[i % len(colors)]
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {color};
                    font-weight: bold;
                    spacing: 5px;
                    padding: 2px;
                }}
                QCheckBox::indicator {{
                    width: 13px;
                    height: 13px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {color};
                    border: 1px solid {color};
                }}
                QCheckBox::indicator:unchecked {{
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                }}
            """)
            
            self.visible_channels[i] = i < 10
            self.channels_layout.addWidget(checkbox)
            
        self.channels_layout.addStretch()
        
    def update_time_display(self):
        """Update time display label"""
        self.time_label.setText(f"Time: {self.current_time:.1f}s / {self.duration:.1f}s")
        self.time_line.setPos(self.current_time)
        
    def update_plot(self):
        """Update the EEG timeline plot"""
        if not self.analyzer:
            return
            
        try:
            # Clear existing plot items (except time line)
            items = self.plot_widget.getPlotItem().items[:]
            for item in items:
                if item != self.time_line:
                    self.plot_widget.removeItem(item)
            
            # Get data for current time window
            start_time = self.time_offset
            end_time = min(start_time + self.window_size, self.duration)
            
            data, times = self.analyzer.processor.get_filtered_data(
                start_time=start_time, 
                stop_time=end_time
            )
            
            if data is None or len(data) == 0:
                return
                
            # Convert to microvolts
            data = data * 1e6
            
            # Channel colors
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
            # Plot visible channels
            visible_count = 0
            for channel_idx in range(len(self.channel_names)):
                if not self.visible_channels.get(channel_idx, False):
                    continue
                    
                channel_data = data[channel_idx]
                
                # Normalize and offset for display
                normalized_data = channel_data / self.y_scale
                offset_data = normalized_data + (visible_count * self.spacing)
                
                # Plot
                color = colors[channel_idx % len(colors)]
                pen = pg.mkPen(color=color, width=1)
                
                # Adjust times to match the time window
                plot_times = times + start_time
                
                self.plot_widget.plot(plot_times, offset_data, pen=pen)
                
                visible_count += 1
            
            # Set plot ranges
            if visible_count > 0:
                self.plot_widget.setXRange(start_time, end_time, padding=0)
                self.plot_widget.setYRange(-self.spacing, visible_count * self.spacing, padding=0)
                
        except Exception as e:
            print(f"Error updating EEG timeline plot: {e}")
            import traceback
            traceback.print_exc()
            
    def clear_plot(self):
        """Clear the plot"""
        items = self.plot_widget.getPlotItem().items[:]
        for item in items:
            if item != self.time_line:
                self.plot_widget.removeItem(item)
