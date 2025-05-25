"""
Power Plot
Frequency band power visualization widget
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
        
        layout.addWidget(self.plot_widget)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
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
        self.current_time = current_time
        self.duration = total_duration
        self.update_plot()
        
    def update_plot(self):
        """Update the power plot"""
        if not self.analyzer:
            return
            
        try:
            # Clear existing plot
            self.plot_widget.clear()
            
            # Use existing analyzer methods based on current band
            if self.current_band == 'Alpha':
                # Use the existing alpha power calculation
                time_vector, power_data = self.analyzer.calculate_alpha_power_sliding(
                    channel_idx=self.current_channel,
                    window_length=2.0,
                    overlap=0.5
                )
            else:
                # For other bands, calculate frequency bands power
                try:
                    bands_power = self.analyzer.get_frequency_bands_power(
                        channel_idx=self.current_channel
                    )
                    if self.current_band in bands_power:
                        # Create a simple single-point plot for now
                        power_value = bands_power[self.current_band]
                        time_vector = np.array([0, self.duration if self.duration > 0 else 1])
                        power_data = np.array([power_value, power_value])
                    else:
                        return
                except:
                    return
            
            if time_vector is not None and power_data is not None and len(power_data) > 0:
                # Plot power data
                pen = pg.mkPen(color='#ff9800', width=2)
                self.plot_widget.plot(time_vector, power_data, pen=pen)
                
                # Add current position indicator if we have a timeline
                if self.current_time > 0 and self.duration > 0:
                    pos_line = pg.InfiniteLine(pos=self.current_time, angle=90, 
                                             pen=pg.mkPen(color='#00ff00', width=2, style=2))
                    self.plot_widget.addItem(pos_line)
                    
                # Set reasonable Y range
                if np.max(power_data) > 0:
                    self.plot_widget.setYRange(0, np.max(power_data) * 1.1, padding=0)
                    
                # Set X range
                if len(time_vector) > 1:
                    self.plot_widget.setXRange(np.min(time_vector), np.max(time_vector), padding=0)
                
        except Exception as e:
            print(f"Error updating power plot: {e}")
            
    def clear_plot(self):
        """Clear the plot"""
        self.plot_widget.clear()
