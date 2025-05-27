"""
Band Spikes Analysis
Widget for analyzing spike events in frequency bands
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from utils.ui_helpers import setup_dark_plot


class BandSpikes(QWidget):
    """Frequency band spike analysis widget"""
    
    spike_detected = pyqtSignal(float, str)  # time, band
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.current_channel = 0
        self.current_band = 'Alpha'
        self.current_time = 0
        self.duration = 0
        self.threshold_multiplier = 2.0
        self.spike_events = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the spike analysis UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        setup_dark_plot(self.plot_widget, "Time (seconds)", "Power (μV²)")
        
        # Configure plot
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMin=0, yMin=0)
        
        # Set initial plot range
        self.plot_widget.setYRange(0, 100)
        self.plot_widget.setXRange(0, 10)
        
        layout.addWidget(self.plot_widget)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        if analyzer and hasattr(analyzer, 'processor') and analyzer.processor:
            self.duration = analyzer.processor.get_duration()
            self.plot_widget.getPlotItem().getViewBox().setLimits(xMax=self.duration)
            # Initial plot update
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
        self.current_time = max(0, current_time)
        self.duration = total_duration
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMax=total_duration)
        self.update_plot()
        
    def set_threshold(self, value):
        """Set the threshold multiplier"""
        print(f"🎯 BandSpikes: Setting threshold to {value} (multiplier: {value/10.0})")
        self.threshold_multiplier = value / 10.0
        self.update_plot()
        
    def detect_spikes(self):
        """Detect spikes in the current band"""
        print(f"🔥 BandSpikes: Starting spike detection with threshold multiplier: {self.threshold_multiplier}")
        if not self.analyzer:
            return
            
        try:
            # Get band power data
            power_data = self.analyzer.calculate_band_power(
                self.current_band,
                channel_idx=self.current_channel
            )
            
            if power_data is None or len(power_data) == 0:
                return
                
            # Calculate threshold
            mean_power = np.mean(power_data)
            std_power = np.std(power_data)
            threshold = mean_power + (self.threshold_multiplier * std_power)
            
            # Detect spikes
            self.spike_events = []
            for i, power in enumerate(power_data):
                if power > threshold:
                    time_step = self.duration / len(power_data) if len(power_data) > 0 else 1.0
                    time = i * time_step
                    self.spike_events.append((time, power))
                    self.spike_detected.emit(time, self.current_band)
            
            self.update_plot()
            
        except Exception as e:
            print(f"Error detecting spikes: {e}")
            
    def update_plot(self):
        """Update the spike analysis plot"""
        if not self.analyzer:
            return
            
        try:
            # Clear existing plot
            self.plot_widget.clear()
            
            # Get band power data
            power_data = self.analyzer.calculate_band_power(
                self.current_band,
                channel_idx=self.current_channel
            )
            
            if power_data is None or len(power_data) == 0:
                print("No power data available")
                return
                
            # Create time vector
            time_step = self.duration / len(power_data) if len(power_data) > 0 else 1.0
            times = np.arange(len(power_data)) * time_step
            
            # Plot power data
            pen = pg.mkPen(color='#2196f3', width=2)  # Blue color
            self.plot_widget.plot(times, power_data, pen=pen)
            
            # Calculate and plot threshold
            mean_power = np.mean(power_data)
            std_power = np.std(power_data)
            threshold = mean_power + (self.threshold_multiplier * std_power)
            
            # Plot threshold line
            threshold_line = pg.InfiniteLine(
                pos=threshold,
                angle=0,
                pen=pg.mkPen(color='#ff9800', width=2, style=Qt.DashLine)  # Orange dashed line
            )
            self.plot_widget.addItem(threshold_line)
            
            # Plot detected spikes
            if self.spike_events:
                spike_times = [event[0] for event in self.spike_events]
                spike_powers = [event[1] for event in self.spike_events]
                
                scatter = pg.ScatterPlotItem(
                    x=spike_times,
                    y=spike_powers,
                    size=10,
                    pen=None,
                    brush='#f44336'  # Red color
                )
                self.plot_widget.addItem(scatter)
            
            # Set plot ranges
            y_max = np.max(power_data) * 1.2 if np.max(power_data) > 0 else 100
            self.plot_widget.setYRange(0, y_max)
            self.plot_widget.setXRange(0, self.duration if self.duration > 0 else 10)
            
        except Exception as e:
            print(f"Error updating spike plot: {e}")
            
    def get_spike_count(self):
        """Get the number of detected spikes"""
        return len(self.spike_events)
