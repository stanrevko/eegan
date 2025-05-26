"""
Tabbed Analysis Panel
Main analysis panel with tabs for different analysis tools
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QGroupBox
from PyQt5.QtCore import pyqtSignal

from gui.analysis import BandSelector, ChannelSelector, PowerPlot, AnalysisControls, DFAAnalysis
from gui.analysis.band_spikes import BandSpikes
from gui.analysis.all_bands_power import AllBandsPower


class TabbedAnalysisPanel(QWidget):
    """Tabbed frequency band analysis panel with multiple analysis tools"""
    
    # Signals
    band_changed = pyqtSignal(str)
    spike_detected = pyqtSignal(float, str)
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.current_channel = 0
        self.current_time = 0
        self.current_duration = 0
        
        self.init_ui()
        self.setup_connections()
        
        
    def init_ui(self):
        """Initialize the tabbed UI"""
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
        
        # Header with shared controls
        header_layout = QHBoxLayout()
        
        # Title
        self.title_label = QLabel("⚡ Alpha Power (8-13Hz)")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ff9800;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Channel selector
        self.channel_selector = ChannelSelector()
        header_layout.addWidget(self.channel_selector)
        
        header_layout.addStretch()
        # Shared band selector
        self.band_selector = BandSelector()
        header_layout.addWidget(self.band_selector)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
                border-radius: 3px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3c3c3c;
                border-bottom: 2px solid #ff9800;
            }
            QTabBar::tab:hover {
                background-color: #404040;
            }
        """)
        
        # Tab 1: Band Power
        self.create_band_power_tab()
        
        # Tab 2: Band Spikes  
        self.create_band_spikes_tab()
        
        # Tab 3: All Band Powers
        self.create_all_bands_tab()
        
        # Tab 4: DFA Analysis (moved to last)
        self.create_dfa_tab()
        
        main_layout.addWidget(self.tab_widget)
        layout.addWidget(main_group)
        
    def create_band_power_tab(self):
        """Create the Band Power analysis tab"""
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(5, 5, 5, 5)
        
        # Power plot (takes most space)
        self.power_plot = PowerPlot()
        tab_layout.addWidget(self.power_plot, stretch=3)
        
        # Analysis controls
        self.analysis_controls = AnalysisControls()
        tab_layout.addWidget(self.analysis_controls, stretch=1)
        
        self.tab_widget.addTab(tab_widget, "📊 Band Power")
        
    def create_band_spikes_tab(self):
        """Create the Band Spikes analysis tab"""
        self.band_spikes = BandSpikes()
        self.tab_widget.addTab(self.band_spikes, "⚡ Band Spikes")
        
    def create_all_bands_tab(self):
        """Create the All Band Powers comparison tab"""
        self.all_bands_power = AllBandsPower()
        self.tab_widget.addTab(self.all_bands_power, "📈 All Bands")
        
    def create_dfa_tab(self):
        """Create the DFA analysis tab"""
        self.dfa_analysis = DFAAnalysis()
        self.tab_widget.addTab(self.dfa_analysis, "📊 DFA Analysis")
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # Channel selector affects all tabs
        self.channel_selector.channel_changed.connect(self.on_channel_changed)
        
        # Band selector affects all tabs
        self.band_selector.band_changed.connect(self.on_band_changed)
        self.band_selector.band_changed.connect(self.power_plot.set_band)
        self.band_selector.band_changed.connect(self.band_spikes.set_band)
        self.band_selector.band_changed.connect(self.band_changed.emit)
        
        # Analysis controls to power plot
        self.analysis_controls.window_size_changed.connect(self.on_analysis_params_changed)
        self.analysis_controls.step_size_changed.connect(self.on_analysis_params_changed)
        self.analysis_controls.channel_changed.connect(self.on_channel_changed_from_controls)
        
        # Spike detection signal
        self.band_spikes.spike_detected.connect(self.spike_detected.emit)
        
    def on_band_changed(self, band_name):
        """Handle band selection changes"""
        band_info = self.band_selector.get_band_info(band_name)
        if band_info:
            low_freq, high_freq, color = band_info
            channel_name = self.channel_selector.get_current_channel_name()
            if channel_name:
                self.title_label.setText(f"⚡ {band_name} Power ({low_freq}-{high_freq}Hz) - Channel: {channel_name}")
            else:
                self.title_label.setText(f"⚡ {band_name} Power ({low_freq}-{high_freq}Hz)")
            self.title_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
            
    def on_channel_changed(self, channel_idx):
        """Handle channel selection changes"""
        self.current_channel = channel_idx
        
        # Update title to show current channel
        channel_name = self.channel_selector.get_current_channel_name()
        current_band = self.band_selector.get_current_band()
        band_info = self.band_selector.get_band_info(current_band)
        if band_info:
            low_freq, high_freq, color = band_info
            self.title_label.setText(f"⚡ {current_band} Power ({low_freq}-{high_freq}Hz) - Channel: {channel_name}")
            self.title_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
        
        # Update analysis controls display
        if hasattr(self, "analysis_controls"):
            self.analysis_controls._updating_programmatically = True
            self.analysis_controls.set_channel(channel_idx)
            self.analysis_controls._updating_programmatically = False
        # Update all tabs with new channel
        self.power_plot.set_channel(channel_idx)
        self.band_spikes.set_channel(channel_idx)
        self.all_bands_power.set_channel(channel_idx)
        self.dfa_analysis.set_channel(channel_idx)        
    def on_analysis_params_changed(self):
        """Handle analysis parameter changes"""
        # Trigger plot updates when parameters change
        self.power_plot.update_plot()
        
    def on_channel_changed_from_controls(self, channel_idx):
        """Handle channel changes from analysis controls - no recursion"""
        self.current_channel = channel_idx
        # Update channel selector display without triggering its signal
        self.channel_selector.set_current_channel(channel_idx)
        # Update all plots directly without triggering analysis_controls again
        self.power_plot.set_channel(channel_idx)
        self.band_spikes.set_channel(channel_idx)
        self.all_bands_power.set_channel(channel_idx)
        self.dfa_analysis.set_channel(channel_idx)        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer for all components"""
        self.analyzer = analyzer
        self.power_plot.set_analyzer(analyzer)
        self.band_spikes.set_analyzer(analyzer)
        self.all_bands_power.set_analyzer(analyzer)
        self.dfa_analysis.set_analyzer(analyzer)        
        # Initialize channel selector with available channels
        if analyzer and analyzer.processor and hasattr(analyzer.processor, "get_channel_names"):
            channel_names = analyzer.processor.get_channel_names()
            self.channel_selector.set_channels(channel_names)
            # Set initial channel
            if len(channel_names) > 0:
                self.channel_selector.set_current_channel(0)
                self.current_channel = 0
        elif analyzer and hasattr(analyzer, "raw") and analyzer.raw:
            # Fallback to direct raw access
            channel_names = analyzer.raw.ch_names
            self.channel_selector.set_channels(channel_names)
            # Set initial channel
            if len(channel_names) > 0:
                self.channel_selector.set_current_channel(0)
                self.current_channel = 0
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        # Update channel selector display
        self.channel_selector.set_current_channel(channel_idx)
        # Update analysis controls display
        if hasattr(self, "analysis_controls"):
            self.analysis_controls.set_channel(channel_idx)
        # Update all plots
        self.power_plot.set_channel(channel_idx)
        self.band_spikes.set_channel(channel_idx)
        self.all_bands_power.set_channel(channel_idx)
        self.dfa_analysis.set_channel(channel_idx)        
    def set_time_window(self, current_time, total_duration):
        """Set the current time window"""
        self.current_time = current_time
        self.current_duration = total_duration
        self.power_plot.set_time_window(current_time, total_duration)
        self.band_spikes.set_time_window(current_time, total_duration)
        self.all_bands_power.set_time_window(current_time, total_duration)
        self.dfa_analysis.set_timeframe(current_time, current_time + total_duration)        
    def set_timeframe(self, start_time, end_time):
        """Set analysis timeframe for all tabs"""
        self.power_plot.set_timeframe(start_time, end_time)
        self.all_bands_power.set_timeframe(start_time, end_time)
        self.dfa_analysis.set_timeframe(start_time, end_time)        
    def get_current_band(self):
        """Get currently selected frequency band"""
        return self.band_selector.get_current_band()
        
    def get_current_channel(self):
        """Get current channel"""
        return self.current_channel
        
    def get_current_channel_name(self):
        """Get current channel name"""
        return self.channel_selector.get_current_channel_name()
        
    def get_current_tab_index(self):
        """Get current tab index"""
        return self.tab_widget.currentIndex()
        
    def set_current_tab(self, index):
        """Set current tab by index"""
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
