"""
EEG Timeline Analysis
Main EEG signal display as an analysis tab - Fixed and Enhanced
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QPushButton, QCheckBox, QGroupBox,
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
        self.y_scale = 50  # microvolts - changed from 200 to 50
        self.spacing = 1   # spacing multiplier - changed from 3 to 1
        self.visible_channels = {}
        self.channel_names = []
        self.start_time = 0
        self.end_time = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the EEG timeline UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create plot widget first (now on the left)
        self.plot_widget = pg.PlotWidget()
        setup_dark_plot(self.plot_widget, "Time (seconds)", "Amplitude (μV)")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        main_layout.addWidget(self.plot_widget, stretch=1)
        
        # Right panel for controls
        controls_panel = QWidget()
        controls_panel.setFixedWidth(250)
        controls_layout = QVBoxLayout(controls_panel)
        
        # Channel Visibility Group
        channels_group = QGroupBox("Channel Visibility")
        channels_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #3c3c3c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        channels_layout = QVBoxLayout(channels_group)
        
        # Select All/None buttons
        buttons_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_none_btn = QPushButton("None")
        
        button_style = """
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                color: #ffffff;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """
        self.select_all_btn.setStyleSheet(button_style)
        self.select_none_btn.setStyleSheet(button_style)
        
        self.select_all_btn.clicked.connect(self.select_all_channels)
        self.select_none_btn.clicked.connect(self.select_no_channels)
        
        buttons_layout.addWidget(self.select_all_btn)
        buttons_layout.addWidget(self.select_none_btn)
        channels_layout.addLayout(buttons_layout)
        
        # Channel checkboxes container
        self.channels_container = QWidget()
        self.channels_layout = QVBoxLayout(self.channels_container)
        self.channels_layout.setSpacing(2)
        
        # Scroll area for channel checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.channels_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        channels_layout.addWidget(scroll_area)
        
        controls_layout.addWidget(channels_group)
        
        # Display Controls Group
        display_group = QGroupBox("Display")
        display_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #3c3c3c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        display_layout = QVBoxLayout(display_group)
        
        # Y-scale control
        y_scale_layout = QHBoxLayout()
        y_scale_layout.addWidget(QLabel("Y-Scale:"))
        self.y_scale_spinbox = QSpinBox()
        self.y_scale_spinbox.setRange(10, 500)
        self.y_scale_spinbox.setValue(self.y_scale)
        self.y_scale_spinbox.setSuffix(" μV")
        self.y_scale_spinbox.valueChanged.connect(self.on_y_scale_changed)
        self.y_scale_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px;
                border-radius: 3px;
                min-width: 60px;
            }
        """)
        y_scale_layout.addWidget(self.y_scale_spinbox)
        display_layout.addLayout(y_scale_layout)
        
        # Spacing control
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(QLabel("Spacing:"))
        self.spacing_spinbox = QSpinBox()
        self.spacing_spinbox.setRange(1, 5)
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
        spacing_layout.addWidget(self.spacing_spinbox)
        display_layout.addLayout(spacing_layout)
        
        controls_layout.addWidget(display_group)
        controls_layout.addStretch()
        
        # Add controls panel to main layout (now on the right)
        main_layout.addWidget(controls_panel)
        
        # Add time line
        self.time_line = pg.InfiniteLine(angle=90, movable=True)
        self.time_line.setPen(pg.mkPen(color='r', width=2))
        self.time_line.sigPositionChanged.connect(self.on_time_line_moved)
        self.plot_widget.addItem(self.time_line)
        
    def select_all_channels(self):
        """Select all channels"""
        for i in range(len(self.channel_names)):
            self.visible_channels[i] = True
            
        # Update checkboxes
        for i in range(self.channels_layout.count() - 1):  # -1 for stretch
            item = self.channels_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QCheckBox):
                item.widget().setChecked(True)
                
        self.update_plot()
        
    def select_no_channels(self):
        """Deselect all channels"""
        for i in range(len(self.channel_names)):
            self.visible_channels[i] = False
            
        # Update checkboxes
        for i in range(self.channels_layout.count() - 1):  # -1 for stretch
            item = self.channels_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QCheckBox):
                item.widget().setChecked(False)
                
        self.update_plot()
        
    def on_y_scale_changed(self, value):
        """Handle Y-scale changes"""
        self.y_scale = value
        self.update_plot()
        
    def on_spacing_changed(self, value):
        """Handle spacing changes"""
        self.spacing = value
        self.update_plot()
        
    def on_time_line_moved(self, line):
        """Handle time line movement"""
        new_time = line.pos().x()
        if self.start_time <= new_time <= self.end_time:
            self.current_time = new_time
            self.time_changed.emit(new_time)
        
    def on_channel_visibility_changed(self, channel_idx, checked):
        """Handle channel visibility changes"""
        self.visible_channels[channel_idx] = checked
        self.update_plot()
        self.channel_visibility_changed.emit(channel_idx, checked)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        print(f"🔄 EEG Timeline: Setting analyzer...")
        self.analyzer = analyzer
        if analyzer and hasattr(analyzer, "processor") and analyzer.processor:
            self.duration = analyzer.processor.get_duration()
            self.channel_names = analyzer.processor.get_channel_names()
            print(f"📊 EEG Timeline: Duration={self.duration:.1f}s, Channels={len(self.channel_names)}")
            
            # Initialize timeframe to full duration
            self.start_time = 0
            self.end_time = self.duration
            
            self.setup_channel_controls()
            print(f"✅ EEG Timeline: Analyzer set successfully")
        else:
            print(f"❌ EEG Timeline: No analyzer or processor available")
        self.update_plot()
        
    def set_channel(self, channel_idx):
        """Set the current channel"""
        self.current_channel = channel_idx
        
    def set_time_window(self, current_time, total_duration):
        """Set the current time window from main timeline controls"""
        self.current_time = max(0, current_time)
        self.duration = total_duration
        
        # Only update time line position if within current timeframe
        if self.start_time <= self.current_time <= self.end_time:
            self.time_line.setPos(self.current_time)
            
        # Update plot with current timeframe
        self.update_plot()
        
    def set_timeframe(self, start_time, end_time):
        """Set analysis timeframe"""
        print(f"🔄 EEG Timeline: Setting timeframe {start_time:.1f}s - {end_time:.1f}s")
        self.start_time = start_time
        self.end_time = end_time
        
        # Update plot X-axis range
        self.plot_widget.setXRange(start_time, end_time, padding=0)
        
        # Update time line position if needed
        if self.current_time < start_time:
            self.current_time = start_time
            self.time_line.setPos(start_time)
        elif self.current_time > end_time:
            self.current_time = end_time
            self.time_line.setPos(end_time)
            
        # Force plot update with new timeframe
        self.update_plot()
        
    def setup_channel_controls(self):
        """Setup channel visibility controls"""
        # Clear existing controls
        for i in reversed(range(self.channels_layout.count())):
            item = self.channels_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
        # Reset visible channels dictionary
        self.visible_channels = {}
        
        # Channel colors
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                 "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        
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
                    background-color: #3c3c3c;
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
        
        visible_count = sum(1 for v in self.visible_channels.values() if v)
        print(f"🎛️ EEG Timeline: Setup {len(self.channel_names)} channels, {visible_count} visible")
        
    def update_plot(self):
        """Update the EEG timeline plot"""
        if not self.analyzer:
            print("⚠️ EEG Timeline: No analyzer available for plot update")
            return
            
        try:
            # Clear existing plot items (except time line)
            items = self.plot_widget.getPlotItem().items[:]
            for item in items:
                if item != self.time_line:
                    self.plot_widget.removeItem(item)
            
            # Get data for current timeframe
            if self.start_time == 0 and self.end_time == 0:
                # If no timeframe set, use full duration
                self.start_time = 0
                self.end_time = self.duration
                
            print(f"📊 EEG Timeline: Getting data for timeframe {self.start_time:.1f}s - {self.end_time:.1f}s")
            data, times = self.analyzer.processor.get_filtered_data(self.start_time, self.end_time)
            
            if data is None or len(data) == 0:
                print("⚠️ EEG Timeline: No data available for plotting")
                return
                
            print(f"📊 EEG Timeline: Got data - channels={data.shape[0]}, samples={data.shape[1]}")
                
            # Convert to microvolts
            data = data * 1e6
            
            # Channel colors
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                     "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            
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
                
                # Plot the data with explicit x and y values
                self.plot_widget.plot(x=times, y=offset_data, pen=pen)
                
                visible_count += 1
            
            # Set plot ranges
            if visible_count > 0:
                # Set X range to match timeframe
                self.plot_widget.setXRange(self.start_time, self.end_time, padding=0)
                
                # Set Y range based on number of visible channels
                y_min = -self.spacing
                y_max = visible_count * self.spacing
                self.plot_widget.setYRange(y_min, y_max, padding=0.1)
                
                print(f"✅ EEG Timeline: Plotted {visible_count} visible channels ({self.start_time:.1f}s - {self.end_time:.1f}s)")
            else:
                print(f"⚠️ EEG Timeline: No visible channels to plot (total channels: {len(self.channel_names)})")
                
            # Update time line position
            self.time_line.setPos(self.current_time)
                
        except Exception as e:
            print(f"❌ Error updating EEG timeline plot: {e}")
            import traceback
            traceback.print_exc()
            
    def clear_plot(self):
        """Clear the plot"""
        self.plot_widget.clear()
        # Re-add time line
        self.time_line = pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen(color="#00ff00", width=2, style=2))
        self.plot_widget.addItem(self.time_line)
