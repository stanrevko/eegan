"""
All Bands Power Analysis
Widget for comparing power across all frequency bands
"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QGroupBox
from PyQt5.QtCore import pyqtSignal
from utils.ui_helpers import setup_dark_plot


class AllBandsPower(QWidget):
    """All frequency bands power comparison widget"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.current_channel = 0
        self.current_time = 0
        self.duration = 0
        self.timeframe_start = 0
        self.timeframe_end = 0
        
        # Band visibility toggles
        self.band_visibility = {
            'Alpha': True,
            'Beta': True,
            'Theta': True,
            'Delta': True,
            'Gamma': True
        }
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the all bands UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        setup_dark_plot(self.plot_widget, "Time (seconds)", "Normalized Power")
        
        # Configure plot
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMin=0, yMin=0)
        
        # Add legend
        self.plot_widget.addLegend()
        
        layout.addWidget(self.plot_widget)
        
    def create_band_controls(self):
        """Create band visibility controls group"""
        band_group = QGroupBox("Band Visibility")
        band_group.setStyleSheet("""
            QGroupBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #ffffff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        band_layout = QVBoxLayout()
        band_layout.setSpacing(8)
        
        self.band_checkboxes = {}
        band_colors = {
            'Alpha': '#ff9800',
            'Beta': '#2196f3', 
            'Theta': '#9c27b0',
            'Delta': '#4caf50',
            'Gamma': '#f44336'
        }
        
        for band_name, color in band_colors.items():
            checkbox = QCheckBox(band_name)
            checkbox.setChecked(self.band_visibility[band_name])
            checkbox.stateChanged.connect(lambda state, name=band_name: self.toggle_band_visibility(name, state))
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {color};
                    font-weight: bold;
                    spacing: 5px;
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
            
            self.band_checkboxes[band_name] = checkbox
            band_layout.addWidget(checkbox)
            
        band_group.setLayout(band_layout)
        return band_group
        
    def toggle_band_visibility(self, band_name, state):
        """Toggle visibility of a frequency band"""
        self.band_visibility[band_name] = bool(state)
        self.update_plot()
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        if analyzer and hasattr(analyzer, 'processor') and analyzer.processor:
            self.duration = analyzer.processor.get_duration()
            self.timeframe_end = self.duration
            self.plot_widget.getPlotItem().getViewBox().setLimits(xMax=self.duration)
        self.update_plot()
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        self.update_plot()
        
    def set_time_window(self, current_time, total_duration):
        """Set the current time window"""
        self.current_time = max(0, current_time)
        self.duration = total_duration
        self.plot_widget.getPlotItem().getViewBox().setLimits(xMax=total_duration)
        self.update_plot()
        
    def set_timeframe(self, start_time, end_time):
        """Set analysis timeframe"""
        self.timeframe_start = max(0, start_time)
        self.timeframe_end = min(end_time, self.duration) if self.duration > 0 else end_time
        self.update_plot()
        
    def update_plot(self):
        """Update the all bands power plot"""
        if not self.analyzer:
            return
            
        try:
            # Clear existing plot
            self.plot_widget.clear()
            
            # Band colors and info
            band_colors = {
                'Alpha': '#ff9800',
                'Beta': '#2196f3', 
                'Theta': '#9c27b0',
                'Delta': '#4caf50',
                'Gamma': '#f44336'
            }
            
            # Calculate power for each band
            all_power_data = {}
            time_vector = None
            
            for band_name in band_colors.keys():
                if not self.band_visibility[band_name]:
                    continue
                    
                # Use timeframe if set
                start_time = self.timeframe_start if self.timeframe_start > 0 or self.timeframe_end < self.duration else None
                end_time = self.timeframe_end if self.timeframe_start > 0 or self.timeframe_end < self.duration else None
                
                power_data = self.analyzer.calculate_band_power(
                    band_name,
                    channel_idx=self.current_channel,
                    start_time=start_time,
                    end_time=end_time
                )
                
                if power_data is not None and len(power_data) > 0:
                    # Normalize power data to 0-1 range for comparison
                    min_power = np.min(power_data)
                    max_power = np.max(power_data)
                    if max_power > min_power:
                        normalized_power = (power_data - min_power) / (max_power - min_power)
                    else:
                        normalized_power = power_data
                    
                    all_power_data[band_name] = normalized_power
                    
                    # Create time vector (same for all bands)
                    if time_vector is None:
                        if start_time is not None and end_time is not None:
                            time_vector = np.linspace(start_time, end_time, len(power_data))
                        else:
                            time_vector = np.linspace(0, self.duration, len(power_data))
            
            # Plot all visible bands
            if time_vector is not None:
                for band_name, power_data in all_power_data.items():
                    color = band_colors[band_name]
                    pen = pg.mkPen(color=color, width=2)
                    
                    # Plot with legend
                    curve = self.plot_widget.plot(time_vector, power_data, pen=pen, name=band_name)
                
                # Set X range
                x_min = max(0, np.min(time_vector))
                x_max = min(self.duration, np.max(time_vector)) if self.duration > 0 else np.max(time_vector)
                self.plot_widget.setXRange(x_min, x_max, padding=0)
                
                # Set Y range (normalized 0-1)
                self.plot_widget.setYRange(0, 1.5, padding=0)
                
                # Add current position indicator
                if self.current_time >= x_min and self.current_time <= x_max:
                    pos_line = pg.InfiniteLine(pos=self.current_time, angle=90, 
                                             pen=pg.mkPen(color='#00ff00', width=2, style=2))
                    self.plot_widget.addItem(pos_line)
                    
                # Add timeframe boundary lines if using custom timeframe
                if (self.timeframe_start > 0 or self.timeframe_end < self.duration):
                    start_line = pg.InfiniteLine(pos=self.timeframe_start, angle=90, 
                                               pen=pg.mkPen(color='#00ff00', width=1, style=3))
                    end_line = pg.InfiniteLine(pos=self.timeframe_end, angle=90, 
                                             pen=pg.mkPen(color='#ff0000', width=1, style=3))
                    self.plot_widget.addItem(start_line)
                    self.plot_widget.addItem(end_line)
                    
        except Exception as e:
            print(f"Error updating all bands plot: {e}")
            import traceback
            traceback.print_exc()
            
    def clear_plot(self):
        """Clear the plot"""
        self.plot_widget.clear()
