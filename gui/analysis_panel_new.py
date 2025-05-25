"""
Analysis Panel - Simplified and Modular
Uses separate components for band selection, power plot, and controls
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PyQt5.QtCore import pyqtSignal

from gui.analysis import BandSelector, PowerPlot, AnalysisControls


class AnalysisPanel(QWidget):
    """Simplified frequency band analysis panel using modular components"""
    
    # Signals
    band_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.current_channel = 0
        self.current_time = 0
        self.current_duration = 0
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the UI with modular components"""
        layout = QVBoxLayout(self)
        
        # Create main group box
        main_group = QGroupBox()
        main_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
        """)
        main_layout = QVBoxLayout(main_group)
        
        # Header with band selector
        header_layout = QHBoxLayout()
        
        # Title
        self.title_label = QLabel("⚡ Alpha Power (8-13Hz)")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ff9800;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Band selector
        self.band_selector = BandSelector()
        header_layout.addWidget(self.band_selector)
        
        main_layout.addLayout(header_layout)
        
        # Content area
        content_layout = QHBoxLayout()
        
        # Left: Power plot (takes most space)
        self.power_plot = PowerPlot()
        content_layout.addWidget(self.power_plot, stretch=3)
        
        # Right: Analysis controls
        self.analysis_controls = AnalysisControls()
        content_layout.addWidget(self.analysis_controls, stretch=1)
        
        main_layout.addLayout(content_layout)
        
        layout.addWidget(main_group)
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # Band selector to power plot and title
        self.band_selector.band_changed.connect(self.on_band_changed)
        self.band_selector.band_changed.connect(self.power_plot.set_band)
        self.band_selector.band_changed.connect(self.band_changed.emit)
        
        # Analysis controls to power plot
        self.analysis_controls.window_size_changed.connect(self.on_analysis_params_changed)
        self.analysis_controls.step_size_changed.connect(self.on_analysis_params_changed)
        self.analysis_controls.channel_changed.connect(self.power_plot.set_channel)
        
    def on_band_changed(self, band_name):
        """Handle band selection changes"""
        band_info = self.band_selector.get_band_info(band_name)
        if band_info:
            low_freq, high_freq, color = band_info
            self.title_label.setText(f"⚡ {band_name} Power ({low_freq}-{high_freq}Hz)")
            self.title_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
            
    def on_analysis_params_changed(self):
        """Handle analysis parameter changes"""
        # Trigger plot update when parameters change
        self.power_plot.update_plot()
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer for all components"""
        self.analyzer = analyzer
        self.power_plot.set_analyzer(analyzer)
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        self.analysis_controls.set_channel(channel_idx)
        self.power_plot.set_channel(channel_idx)
        
    def set_time_window(self, current_time, total_duration):
        """Set the current time window"""
        self.current_time = current_time
        self.current_duration = total_duration
        self.power_plot.set_time_window(current_time, total_duration)
        
    def get_current_band(self):
        """Get currently selected frequency band"""
        return self.band_selector.get_current_band()
        
    def get_current_channel(self):
        """Get current channel"""
        return self.current_channel
