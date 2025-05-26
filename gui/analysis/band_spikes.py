"""
Band Spikes Analysis
Widget for analyzing spike events in frequency bands
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton
from PyQt5.QtCore import pyqtSignal
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
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Threshold:"))
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(10, 50)
        self.threshold_spinbox.setValue(int(self.threshold_multiplier * 10))
        self.threshold_spinbox.setSuffix("x")
        self.threshold_spinbox.valueChanged.connect(self.on_threshold_changed)
        self.threshold_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px;
                border-radius: 3px;
                min-width: 60px;
            }
        """)
        controls_layout.addWidget(self.threshold_spinbox)
        
        self.detect_button = QPushButton("Detect Spikes")
        self.detect_button.clicked.connect(self.detect_spikes)
        self.detect_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                border: none;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        controls_layout.addWidget(self.detect_button)
        
        self.spike_count_label = QLabel("Spikes: 0")
        self.spike_count_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        controls_layout.addWidget(self.spike_count_label)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        setup_dark_plot(self.plot_widget, "Time (seconds)", "Power (μV²)")
        
        # Configure plot
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMin=0, yMin=0)
        
        layout.addWidget(self.plot_widget)
        
    def on_threshold_changed(self, value):
        """Handle threshold changes"""
        self.threshold_multiplier = value / 10.0
        self.update_plot()
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        if analyzer and hasattr(analyzer, 'processor') and analyzer.processor:
            self.duration = analyzer.processor.get_duration()
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
        self.current_time = max(0, current_time)
        self.duration = total_duration
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMax=total_duration)
        self.update_plot()
        
    def detect_spikes(self):
        """Detect spike events in the current band"""
        if not self.analyzer:
            return
            
        try:
            # Get power data for the current band
            power_data = self.analyzer.calculate_band_power(
                self.current_band,
                channel_idx=self.current_channel
            )
            
            if power_data is not None and len(power_data) > 0:
                # Calculate threshold
                mean_power = np.mean(power_data)
                std_power = np.std(power_data)
                threshold = mean_power + (self.threshold_multiplier * std_power)
                
                # Find spikes
                spike_indices = np.where(power_data > threshold)[0]
                
                # Convert to time points
                time_vector = np.linspace(0, self.duration, len(power_data))
                spike_times = time_vector[spike_indices]
                
                # Group nearby spikes (within 0.5 seconds)
                self.spike_events = []
                if len(spike_times) > 0:
                    current_spike = spike_times[0]
                    for spike_time in spike_times[1:]:
                        if spike_time - current_spike > 0.5:
                            self.spike_events.append(current_spike)
                            current_spike = spike_time
                    self.spike_events.append(current_spike)
                
                self.spike_count_label.setText(f"Spikes: {len(self.spike_events)}")
                
                # Emit signals for detected spikes
                for spike_time in self.spike_events:
                    self.spike_detected.emit(spike_time, self.current_band)
                    
        except Exception as e:
            print(f"Error detecting spikes: {e}")
            
        self.update_plot()
        
    def update_plot(self):
        """Update the spike analysis plot"""
        if not self.analyzer:
            return
            
        try:
            # Clear existing plot
            self.plot_widget.clear()
            
            # Get power data
            power_data = self.analyzer.calculate_band_power(
                self.current_band,
                channel_idx=self.current_channel
            )
            
            if power_data is not None and len(power_data) > 0:
                # Create time vector
                time_vector = np.linspace(0, self.duration, len(power_data))
                
                # Band colors
                band_colors = {
                    'Alpha': '#ff9800',
                    'Beta': '#2196f3',
                    'Theta': '#9c27b0',
                    'Delta': '#4caf50',
                    'Gamma': '#f44336'
                }
                
                color = band_colors.get(self.current_band, '#ff9800')
                pen = pg.mkPen(color=color, width=2)
                
                # Plot power data
                self.plot_widget.plot(time_vector, power_data, pen=pen)
                
                # Calculate and plot threshold line
                mean_power = np.mean(power_data)
                std_power = np.std(power_data)
                threshold = mean_power + (self.threshold_multiplier * std_power)
                
                threshold_line = pg.InfiniteLine(pos=threshold, angle=0, 
                                               pen=pg.mkPen(color='#ff0000', width=1, style=2))
                self.plot_widget.addItem(threshold_line)
                
                # Mark spike events
                for spike_time in self.spike_events:
                    spike_line = pg.InfiniteLine(pos=spike_time, angle=90, 
                                               pen=pg.mkPen(color='#ffff00', width=2))
                    self.plot_widget.addItem(spike_line)
                
                # Set ranges
                self.plot_widget.setXRange(0, self.duration, padding=0)
                y_max = np.max(power_data) if np.max(power_data) > 0 else 1
                self.plot_widget.setYRange(0, y_max * 1.5, padding=0)
                
                # Add current position indicator
                if 0 <= self.current_time <= self.duration:
                    pos_line = pg.InfiniteLine(pos=self.current_time, angle=90, 
                                             pen=pg.mkPen(color='#00ff00', width=2, style=2))
                    self.plot_widget.addItem(pos_line)
                    
        except Exception as e:
            print(f"Error updating spike plot: {e}")
            
    def clear_plot(self):
        """Clear the plot"""
        self.plot_widget.clear()
        self.spike_events = []
        self.spike_count_label.setText("Spikes: 0")
