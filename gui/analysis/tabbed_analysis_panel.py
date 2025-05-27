"""
Tabbed Analysis Panel
Main analysis panel with tabs for different analysis tools
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox
from PyQt5.QtCore import pyqtSignal

from gui.analysis import PowerPlot, AnalysisControls, DFAAnalysis, EEGTimelineAnalysis
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
        
        
    def init_ui(self):
        """Initialize the tabbed UI"""
        layout = QVBoxLayout(self)
        
        # Create main group box without visible border
        main_group = QGroupBox()
        main_group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                padding-top: 0px;
                background-color: #2b2b2b;
            }
        """)
        main_layout = QVBoxLayout(main_group)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
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
        
        # Tab 1: EEG Timeline (moved to first position)
        self.create_eeg_timeline_tab()
        
        # Tab 2: Band Power (with selectors moved here)
        self.create_band_power_tab()
        
        # Tab 3: Band Spikes (with selectors moved here)
        self.create_band_spikes_tab()
        
        # Tab 4: All Band Powers
        self.create_all_bands_tab()
        
        # Tab 5: DFA Analysis
        self.create_dfa_tab()
        
        main_layout.addWidget(self.tab_widget)
        layout.addWidget(main_group)
        
        # Setup connections after all tabs are created
        self.setup_connections()
        
    def create_eeg_timeline_tab(self):
        """Create the EEG Timeline analysis tab"""
        self.eeg_timeline = EEGTimelineAnalysis()
        self.tab_widget.addTab(self.eeg_timeline, "📺 EEG Timeline")
        
    def create_band_power_tab(self):
        """Create the Band Power analysis tab with selectors"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(5, 5, 5, 5)
        
        # Controls header for Band Power tab
        controls_layout = QHBoxLayout()
        
        # Channel selector for Band Power
        from gui.analysis import ChannelSelector, BandSelector
        self.power_channel_selector = ChannelSelector()
        controls_layout.addWidget(self.power_channel_selector)
        
        # Band selector for Band Power
        self.power_band_selector = BandSelector()
        controls_layout.addWidget(self.power_band_selector)
        
        controls_layout.addStretch()
        
        tab_layout.addLayout(controls_layout)
        
        # Main content layout
        content_layout = QHBoxLayout()
        
        # Power plot (takes most space)
        self.power_plot = PowerPlot()
        content_layout.addWidget(self.power_plot, stretch=3)
        
        # Analysis controls
        self.analysis_controls = AnalysisControls()
        content_layout.addWidget(self.analysis_controls, stretch=1)
        
        tab_layout.addLayout(content_layout)
        
        self.tab_widget.addTab(tab_widget, "📊 Band Power")
        
    def create_band_spikes_tab(self):
        """Create the Band Spikes analysis tab with selectors"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(5, 5, 5, 5)
        
        # Controls header for Band Spikes tab
        controls_layout = QHBoxLayout()
        
        # Channel selector for Band Spikes
        from gui.analysis import ChannelSelector, BandSelector
        self.spikes_channel_selector = ChannelSelector()
        controls_layout.addWidget(self.spikes_channel_selector)
        
        # Band selector for Band Spikes
        self.spikes_band_selector = BandSelector()
        controls_layout.addWidget(self.spikes_band_selector)
        
        controls_layout.addStretch()
        
        tab_layout.addLayout(controls_layout)
        
        # Band spikes widget
        self.band_spikes = BandSpikes()
        tab_layout.addWidget(self.band_spikes)
        
        self.tab_widget.addTab(tab_widget, "⚡ Band Spikes")
        
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
        # Band Power tab connections
        if hasattr(self, 'power_channel_selector'):
            self.power_channel_selector.channel_changed.connect(self.on_power_channel_changed)
        if hasattr(self, 'power_band_selector'):
            self.power_band_selector.band_changed.connect(self.on_power_band_changed)
            # Relay band changed signal to main window
            self.power_band_selector.band_changed.connect(self.band_changed.emit)
        
        # Band Spikes tab connections  
        if hasattr(self, 'spikes_channel_selector'):
            self.spikes_channel_selector.channel_changed.connect(self.on_spikes_channel_changed)
        if hasattr(self, 'spikes_band_selector'):
            self.spikes_band_selector.band_changed.connect(self.on_spikes_band_changed)
            # Also relay from spikes band selector (when user switches to spikes tab)
            self.spikes_band_selector.band_changed.connect(self.band_changed.emit)
        
        # Analysis controls to power plot
        self.analysis_controls.window_size_changed.connect(self.on_analysis_params_changed)
        self.analysis_controls.step_size_changed.connect(self.on_analysis_params_changed)
        
        # Spike detection signal
        self.band_spikes.spike_detected.connect(self.spike_detected.emit)
        
    def on_power_channel_changed(self, channel_idx):
        """Handle channel changes for Band Power tab"""
        self.current_channel = channel_idx
        self.power_plot.set_channel(channel_idx)
        self.analysis_controls.set_channel(channel_idx)
        
    def on_power_band_changed(self, band_name):
        """Handle band changes for Band Power tab"""
        self.power_plot.set_band(band_name)
        
    def on_spikes_channel_changed(self, channel_idx):
        """Handle channel changes for Band Spikes tab"""
        self.band_spikes.set_channel(channel_idx)
        
    def on_spikes_band_changed(self, band_name):
        """Handle band changes for Band Spikes tab"""
        self.band_spikes.set_band(band_name)
        
    def on_analysis_params_changed(self):
        """Handle analysis parameter changes"""
        # Trigger plot updates when parameters change
        self.power_plot.update_plot()
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer for all components"""
        print(f"🔄 Tabbed Analysis Panel: Setting analyzer for all tabs...")
        self.analyzer = analyzer
        self.power_plot.set_analyzer(analyzer)
        self.band_spikes.set_analyzer(analyzer)
        self.all_bands_power.set_analyzer(analyzer)
        print(f"📺 Tabbed Analysis Panel: Setting analyzer for EEG Timeline...")
        self.eeg_timeline.set_analyzer(analyzer)
        self.dfa_analysis.set_analyzer(analyzer)
        print(f"✅ Tabbed Analysis Panel: All tabs updated with analyzer")
        
        # Initialize channel selectors with available channels
        if analyzer and analyzer.processor and hasattr(analyzer.processor, "get_channel_names"):
            channel_names = analyzer.processor.get_channel_names()
            if hasattr(self, 'power_channel_selector'):
                self.power_channel_selector.set_channels(channel_names)
            if hasattr(self, 'spikes_channel_selector'):
                self.spikes_channel_selector.set_channels(channel_names)
            # Set initial channel
            if len(channel_names) > 0:
                if hasattr(self, 'power_channel_selector'):
                    self.power_channel_selector.set_current_channel(0)
                if hasattr(self, 'spikes_channel_selector'):
                    self.spikes_channel_selector.set_current_channel(0)
                self.current_channel = 0
        elif analyzer and hasattr(analyzer, "raw") and analyzer.raw:
            # Fallback to direct raw access
            channel_names = analyzer.raw.ch_names
            if hasattr(self, 'power_channel_selector'):
                self.power_channel_selector.set_channels(channel_names)
            if hasattr(self, 'spikes_channel_selector'):
                self.spikes_channel_selector.set_channels(channel_names)
            # Set initial channel
            if len(channel_names) > 0:
                if hasattr(self, 'power_channel_selector'):
                    self.power_channel_selector.set_current_channel(0)
                if hasattr(self, 'spikes_channel_selector'):
                    self.spikes_channel_selector.set_current_channel(0)
                self.current_channel = 0
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        # Update channel selectors display
        if hasattr(self, 'power_channel_selector'):
            self.power_channel_selector.set_current_channel(channel_idx)
        if hasattr(self, 'spikes_channel_selector'):
            self.spikes_channel_selector.set_current_channel(channel_idx)
        # Update analysis controls display
        if hasattr(self, "analysis_controls"):
            self.analysis_controls.set_channel(channel_idx)
        # Update all plots
        self.power_plot.set_channel(channel_idx)
        self.band_spikes.set_channel(channel_idx)
        self.all_bands_power.set_channel(channel_idx)
        self.eeg_timeline.set_channel(channel_idx)
        self.dfa_analysis.set_channel(channel_idx)
        
    def set_time_window(self, current_time, total_duration):
        """Set the current time window"""
        self.current_time = current_time
        self.current_duration = total_duration
        self.power_plot.set_time_window(current_time, total_duration)
        self.band_spikes.set_time_window(current_time, total_duration)
        self.all_bands_power.set_time_window(current_time, total_duration)
        self.eeg_timeline.set_time_window(current_time, total_duration)
        self.dfa_analysis.set_timeframe(current_time, current_time + total_duration)
        
    def set_timeframe(self, start_time, end_time):
        """Set analysis timeframe for all tabs"""
        self.power_plot.set_timeframe(start_time, end_time)
        self.all_bands_power.set_timeframe(start_time, end_time)
        self.dfa_analysis.set_timeframe(start_time, end_time)
        
    def get_current_band(self):
        """Get currently selected frequency band"""
        if hasattr(self, "power_band_selector"):
            return self.power_band_selector.get_current_band()
        else:
            from eeg.frequency_bands import FrequencyBands
            return FrequencyBands().get_active_band()
        
    def get_current_channel(self):
        """Get current channel"""
        return self.current_channel
        
    def get_current_channel_name(self):
        """Get current channel name"""
        if hasattr(self, "power_channel_selector"):
            return self.power_channel_selector.get_current_channel_name()
        else:
            return f"Channel {self.current_channel}"
        
    def get_current_tab_index(self):
        """Get current tab index"""
        return self.tab_widget.currentIndex()
        
    def set_current_tab(self, index):
        """Set current tab by index"""
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
