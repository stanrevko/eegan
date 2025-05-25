"""
Power Plot
Frequency band power visualization widget - Fixed for all bands
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from utils.ui_helpers import setup_dark_plot


class PowerPlot(QWidget):
    """Frequency band power plot widget"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.current_channel = 0
        self.current_band = 'Alpha'
        self.current_time = 0
        self.duration = 0
        self.timeframe_start = 0
        self.timeframe_end = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the power plot UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        setup_dark_plot(self.plot_widget, "Time (seconds)", "Power (μV²)")
        
        # Configure plot
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Constrain plot view - no negative times, no scrolling beyond data
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMin=0, yMin=0)
        
        layout.addWidget(self.plot_widget)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        if analyzer and hasattr(analyzer, 'processor') and analyzer.processor:
            self.duration = analyzer.processor.get_duration()
            self.timeframe_end = self.duration
            # Set maximum X limit to data duration
            self.plot_widget.getPlotItem().getViewBox().setLimits(xMax=self.duration)
        self.update_plot()
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        self.update_plot()
        
    def set_band(self, band_name):
        """Set the frequency band to analyze"""
        self.current_band = band_name
        self.update_plot()
        
    def set_time_window(self, current_time, total_duration):
        """Set the current time window"""
        self.current_time = max(0, current_time)  # No negative times
        self.duration = total_duration
        # Update X limits
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMax=total_duration)
        self.update_plot()
        
    def set_timeframe(self, start_time, end_time):
        """Set analysis timeframe"""
        self.timeframe_start = max(0, start_time)  # No negative times
        self.timeframe_end = min(end_time, self.duration) if self.duration > 0 else end_time
        self.update_plot()
        
    def update_plot(self):
        """Update the power plot for any frequency band"""
        if not self.analyzer:
            return
            
        try:
            # Clear existing plot
            self.plot_widget.clear()
            
            # Use the enhanced calculate_band_power method for all bands
            if hasattr(self.analyzer, 'calculate_band_power'):
                # Use timeframe if set, otherwise full duration
                start_time = self.timeframe_start if self.timeframe_start > 0 or self.timeframe_end < self.duration else None
                end_time = self.timeframe_end if self.timeframe_start > 0 or self.timeframe_end < self.duration else None
                
                power_data = self.analyzer.calculate_band_power(
                    self.current_band,
                    channel_idx=self.current_channel,
                    start_time=start_time,
                    end_time=end_time
                )
                
                if power_data is not None and len(power_data) > 0:
                    # Create time vector
                    if start_time is not None and end_time is not None:
                        time_vector = np.linspace(start_time, end_time, len(power_data))
                    else:
                        time_vector = np.linspace(0, self.duration, len(power_data))
                    
                    # Define band colors
                    band_colors = {
                        'Alpha': '#ff9800',    # Orange
                        'Beta': '#2196f3',     # Blue  
                        'Theta': '#9c27b0',    # Purple
                        'Delta': '#4caf50',    # Green
                        'Gamma': '#f44336'     # Red
                    }
                    
                    color = band_colors.get(self.current_band, '#ff9800')
                    pen = pg.mkPen(color=color, width=2)
                    
                    # Plot power data
                    self.plot_widget.plot(time_vector, power_data, pen=pen)
                    
                    # Set X range (no negative times, bounded by data)
                    x_min = max(0, np.min(time_vector))
                    x_max = min(self.duration, np.max(time_vector)) if self.duration > 0 else np.max(time_vector)
                    self.plot_widget.setXRange(x_min, x_max, padding=0)
                    
                    # Set Y range (no negative values)
                    y_max = np.max(power_data) if len(power_data) > 0 and np.max(power_data) > 0 else 1
                    self.plot_widget.setYRange(0, y_max * 1.1, padding=0)
                    
                    # Add current position indicator
                    if self.current_time >= x_min and self.current_time <= x_max:
                        pos_line = pg.InfiniteLine(pos=self.current_time, angle=90, 
                                                 pen=pg.mkPen(color='#00ff00', width=2, style=2))
                        self.plot_widget.addItem(pos_line)
                        
                    # Add timeframe boundary lines if using custom timeframe
                    if start_time is not None and end_time is not None:
                        start_line = pg.InfiniteLine(pos=start_time, angle=90, 
                                                   pen=pg.mkPen(color='#00ff00', width=1, style=3))
                        end_line = pg.InfiniteLine(pos=end_time, angle=90, 
                                                 pen=pg.mkPen(color='#ff0000', width=1, style=3))
                        self.plot_widget.addItem(start_line)
                        self.plot_widget.addItem(end_line)
                        
            else:
                # Fallback for older analyzer
                if self.current_band == 'Alpha':
                    time_vector, power_data = self.analyzer.calculate_alpha_power_sliding(
                        channel_idx=self.current_channel,
                        window_length=2.0,
                        overlap=0.5
                    )
                    
                    if time_vector is not None and power_data is not None and len(power_data) > 0:
                        pen = pg.mkPen(color='#ff9800', width=2)
                        self.plot_widget.plot(time_vector, power_data, pen=pen)
                        
                        # Constrain ranges
                        x_min = max(0, np.min(time_vector))
                        x_max = min(self.duration, np.max(time_vector)) if self.duration > 0 else np.max(time_vector)
                        self.plot_widget.setXRange(x_min, x_max, padding=0)
                        
                        y_max = np.max(power_data) if np.max(power_data) > 0 else 1
                        self.plot_widget.setYRange(0, y_max * 1.1, padding=0)
                
        except Exception as e:
            print(f"Error updating power plot: {e}")
            import traceback
            traceback.print_exc()
            
    def update_power_data(self, power_data, start_time, end_time):
        """Update plot with specific power data and timeframe"""
        if power_data is None or len(power_data) == 0:
            return
            
        try:
            # Clear existing plot
            self.plot_widget.clear()
            
            # Ensure no negative times
            start_time = max(0, start_time)
            end_time = max(start_time + 0.1, end_time)
            
            # Create time vector for the timeframe
            time_vector = np.linspace(start_time, end_time, len(power_data))
            
            # Band colors
            band_colors = {
                'Alpha': '#ff9800',    # Orange
                'Beta': '#2196f3',     # Blue  
                'Theta': '#9c27b0',    # Purple
                'Delta': '#4caf50',    # Green
                'Gamma': '#f44336'     # Red
            }
            
            color = band_colors.get(self.current_band, '#ff9800')
            pen = pg.mkPen(color=color, width=2)
            
            # Plot power data
            self.plot_widget.plot(time_vector, power_data, pen=pen)
            
            # Set X range (no negative times, bounded by data)
            self.plot_widget.setXRange(start_time, min(end_time, self.duration) if self.duration > 0 else end_time, padding=0)
            
            # Set Y range (no negative values)
            y_max = np.max(power_data) if np.max(power_data) > 0 else 1
            self.plot_widget.setYRange(0, y_max * 1.1, padding=0)
                
            # Add timeframe boundary lines
            start_line = pg.InfiniteLine(pos=start_time, angle=90, 
                                       pen=pg.mkPen(color='#00ff00', width=1, style=3))
            end_line = pg.InfiniteLine(pos=end_time, angle=90, 
                                     pen=pg.mkPen(color='#ff0000', width=1, style=3))
            self.plot_widget.addItem(start_line)
            self.plot_widget.addItem(end_line)
            
        except Exception as e:
            print(f"Error updating power data: {e}")
            
    def clear_plot(self):
        """Clear the plot"""
        self.plot_widget.clear()
