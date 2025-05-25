"""
EEG Plot Widget
Core EEG visualization widget
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from utils.ui_helpers import setup_dark_plot


class EEGPlotWidget(QWidget):
    """EEG visualization plot widget"""
    
    # Signals
    position_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.processor = None
        self.current_position = 0
        self.total_duration = 0
        self.eeg_scale = 200
        self.channel_spacing = 3
        self.visible_channels = []
        self.plot_items = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the plot widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        setup_dark_plot(self.plot_widget, "Time (seconds)", "Channels")
        
        # Configure plot
        self.plot_widget.showGrid(x=True, y=False, alpha=0.3)
        
        layout.addWidget(self.plot_widget)
        
    def set_processor(self, processor):
        """Set the EEG processor"""
        self.processor = processor
        if processor:
            self.total_duration = processor.get_duration()
            self.update_plot_limits()
            
    def set_visible_channels(self, channels):
        """Set visible channels"""
        self.visible_channels = channels
        self.update_plot()
        
    def set_scale(self, scale):
        """Set EEG amplitude scale"""
        self.eeg_scale = scale
        self.update_plot()
        
    def set_spacing(self, spacing):
        """Set channel spacing"""
        self.channel_spacing = spacing
        self.update_plot()
        
    def update_plot_limits(self):
        """Update plot axis limits - constrain to recorded timeframe"""
        if self.total_duration > 0:
            # Set fixed range - no scrolling beyond recorded data
            self.plot_widget.setXRange(0, self.total_duration, padding=0)
            # Disable auto-ranging to prevent scrolling out of bounds
            # Block scrolling left of 0 and right of total_duration
            self.plot_widget.getPlotItem().getViewBox().setLimits(
                xMin=0, xMax=self.total_duration, yMin=None, yMax=None)
            self.plot_widget.getPlotItem().getViewBox().setMouseEnabled(x=True, y=True)
            # Allow zoom but constrain to time limits (0 to total_duration)
            self.plot_widget.getPlotItem().getViewBox().setXRange(0, self.total_duration, padding=0)

    def update_plot(self):
        """Update the EEG plot"""
        if not self.processor or not self.visible_channels:
            return
            
        # Clear existing plots
        self.plot_widget.clear()
        self.plot_items = []
        
        try:
            # Get filtered data from processor (returns tuple)
            data, times = self.processor.get_filtered_data()
            if data is None:
                print("No filtered data available")
                return
                
            sfreq = self.processor.get_sampling_rate()
            
            # Use provided times or create time vector
            if times is not None:
                time = times
            else:
                n_samples = data.shape[1]
                time = np.linspace(0, self.total_duration, n_samples)
            
            # Plot each visible channel
            colors = ['#00bfff', '#ff4444', '#44ff44', '#ff8800', '#8844ff', 
                     '#ff44ff', '#ffff44', '#88ffff']
            
            for i, ch_idx in enumerate(self.visible_channels):
                if ch_idx < data.shape[0]:
                    # Get channel data and apply scaling
                    ch_data = data[ch_idx, :] * 1e6  # Convert to µV
                    
                    # Apply vertical offset for channel separation
                    offset = (len(self.visible_channels) - i - 1) * self.channel_spacing * self.eeg_scale
                    ch_data_offset = ch_data + offset
                    
                    # Create plot item
                    color = colors[i % len(colors)]
                    pen = pg.mkPen(color=color, width=1)
                    plot_item = self.plot_widget.plot(time, ch_data_offset, pen=pen)
                    self.plot_items.append(plot_item)
                    
            # Update Y-axis range
            if self.visible_channels:
                y_range = len(self.visible_channels) * self.channel_spacing * self.eeg_scale
                self.plot_widget.setYRange(-self.eeg_scale, y_range, padding=0.1)
                
            print(f"✅ EEG plot updated: {len(self.visible_channels)} channels, {data.shape[1]} samples")
                
        except Exception as e:
            print(f"Error updating EEG plot: {e}")
            import traceback
            traceback.print_exc()
            
    def get_current_position(self):
        """Get current timeline position"""
        return self.current_position
        
    def set_current_position(self, position):
        """Set current timeline position"""
        self.current_position = max(0, min(position, self.total_duration))
        self.position_changed.emit(self.current_position)
