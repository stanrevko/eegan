"""
Tabbed Analysis Panel
Main analysis panel with tabs for different analysis tools
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QGroupBox
from PyQt5.QtCore import pyqtSignal

from gui.analysis import BandSelector, ChannelSelector, PowerPlot, AnalysisControls, DFAAnalysis, EEGTimelineAnalysis
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
        
        # Create main group box
        main_group = QGroupBox()
        main_group.setStyleSheet("""
            QGroupBox {
                
                
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
        """)
        main_layout = QVBoxLayout(main_group)
        
        # Header removed - channel and band selectors moved to individual tabs
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                
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
        
        # Tab 1: Band Power
        self.create_eeg_timeline_tab()
        
        # Tab 2: Band Spikes  
        self.create_band_spikes_tab()
        
        # Tab 3: All Band Powers
        self.create_all_bands_tab()
        
        # Tab 4: EEG Timeline
        self.create_band_power_tab()
        
        # Tab 5: DFA Analysis (moved to last)
        self.create_dfa_tab()
        
        main_layout.addWidget(self.tab_widget)
        layout.addWidget(main_group)
        
        # Setup connections after all tabs are created
        self.setup_connections()
        
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
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        
        # Controls header for Band Spikes tab
        controls_layout = QHBoxLayout()
        
        # Channel selector for Band Spikes
        self.spikes_channel_selector = ChannelSelector()
        controls_layout.addWidget(self.spikes_channel_selector)
        
        controls_layout.addStretch()
        
        # Band selector for Band Spikes
        self.spikes_band_selector = BandSelector()
        controls_layout.addWidget(self.spikes_band_selector)
        
        tab_layout.addLayout(controls_layout)
        
        # Band spikes widget
        self.band_spikes = BandSpikes()
        tab_layout.addWidget(self.band_spikes)
        
        self.tab_widget.addTab(tab_widget, "⚡ Band Spikes")
        
    def create_all_bands_tab(self):
        """Create the All Band Powers comparison tab"""
        self.all_bands_power = AllBandsPower()
        self.tab_widget.addTab(self.all_bands_power, "📈 All Bands")
        
    def create_eeg_timeline_tab(self):
        """Create the EEG Timeline analysis tab"""
        self.eeg_timeline = EEGTimelineAnalysis()
        self.tab_widget.addTab(self.eeg_timeline, "📺 EEG Timeline")
        
    def create_dfa_tab(self):
        """Create the DFA analysis tab"""
        self.dfa_analysis = DFAAnalysis()
        self.tab_widget.addTab(self.dfa_analysis, "📊 DFA Analysis")
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # Band Power tab connections
        if hasattr(self, 'channel_selector'):
            self.channel_selector.channel_changed.connect(self.on_channel_changed)
        if hasattr(self, 'band_selector'):
            self.band_selector.band_changed.connect(self.on_band_changed)
            self.band_selector.band_changed.connect(self.power_plot.set_band)
        
        # Band Spikes tab connections  
        if hasattr(self, 'spikes_channel_selector'):
            self.spikes_channel_selector.channel_changed.connect(self.on_spikes_channel_changed)
        if hasattr(self, 'spikes_band_selector'):
            self.spikes_band_selector.band_changed.connect(self.on_spikes_band_changed)
            self.spikes_band_selector.band_changed.connect(self.band_spikes.set_band)
        # Band changed signal connection removed - handled in individual tabs
        
        # Analysis controls to power plot
        self.analysis_controls.window_size_changed.connect(self.on_analysis_params_changed)
        self.analysis_controls.step_size_changed.connect(self.on_analysis_params_changed)
        self.analysis_controls.channel_changed.connect(self.on_channel_changed_from_controls)
        
        # Spike detection signal
        self.band_spikes.spike_detected.connect(self.spike_detected.emit)
        
    def on_band_changed(self, band_name):
        """Handle band selection changes"""
        # Get band info from frequency bands directly
        from eeg.frequency_bands import FrequencyBands
        freq_bands = FrequencyBands()
        band_info = freq_bands.get_band_info(band_name)
        if band_info:
            low_freq, high_freq, color = band_info
            channel_name = f"Channel {self.current_channel}"
            if channel_name:
                self.title_label.setText(f"⚡ {band_name} Power ({low_freq}-{high_freq}Hz) - Channel: {channel_name}")
            else:
                self.title_label.setText(f"⚡ {band_name} Power ({low_freq}-{high_freq}Hz)")
            self.title_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
            
    def on_channel_changed(self, channel_idx):
        """Handle channel selection changes"""
        self.current_channel = channel_idx
        
        # Update title to show current channel
        channel_name = f"Channel {self.current_channel}"
        from eeg.frequency_bands import FrequencyBands
        freq_bands = FrequencyBands()
        current_band = freq_bands.get_active_band()
        band_info = freq_bands.get_band_info(current_band)
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
        self.eeg_timeline.set_channel(channel_idx)
        self.dfa_analysis.set_channel(channel_idx)        
    def on_analysis_params_changed(self):
        """Handle analysis parameter changes"""
        # Trigger plot updates when parameters change
        self.power_plot.update_plot()
        
    def on_channel_changed_from_controls(self, channel_idx):
        """Handle channel changes from analysis controls - no recursion"""
        self.current_channel = channel_idx
        # Update channel selector display without triggering its signal
        if hasattr(self, 'channel_selector'):
            self.channel_selector.set_current_channel(channel_idx)
        # Update all plots directly without triggering analysis_controls again
        self.power_plot.set_channel(channel_idx)
        self.band_spikes.set_channel(channel_idx)
        self.all_bands_power.set_channel(channel_idx)
        self.eeg_timeline.set_channel(channel_idx)
        self.dfa_analysis.set_channel(channel_idx)        
    def on_spikes_channel_changed(self, channel_idx):
        """Handle channel changes for Band Spikes tab"""
        self.band_spikes.set_channel(channel_idx)
        
    def on_spikes_band_changed(self, band_name):
        """Handle band changes for Band Spikes tab"""
        self.band_spikes.set_band(band_name)
        
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
            if hasattr(self, 'channel_selector'):
                if hasattr(self, "channel_selector"):
                    self.channel_selector.set_channels(channel_names)
            if hasattr(self, 'spikes_channel_selector'):
                self.spikes_channel_selector.set_channels(channel_names)
            # Set initial channel
            if len(channel_names) > 0:
                if hasattr(self, 'channel_selector'):
                    if hasattr(self, "channel_selector"):
                        self.channel_selector.set_current_channel(0)
                if hasattr(self, 'spikes_channel_selector'):
                    self.spikes_channel_selector.set_current_channel(0)
                self.current_channel = 0
        elif analyzer and hasattr(analyzer, "raw") and analyzer.raw:
            # Fallback to direct raw access
            channel_names = analyzer.raw.ch_names
            if hasattr(self, "channel_selector"):
                self.channel_selector.set_channels(channel_names)
            # Set initial channel
            if len(channel_names) > 0:
                if hasattr(self, "channel_selector"):
                    self.channel_selector.set_current_channel(0)
                self.current_channel = 0
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        # Update channel selector display
        if hasattr(self, 'channel_selector'):
            self.channel_selector.set_current_channel(channel_idx)
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
        if hasattr(self, "band_selector"):
            return self.band_selector.get_current_band()
        else:
            from eeg.frequency_bands import FrequencyBands
            return FrequencyBands().get_active_band()
        
    def get_current_channel(self):
        """Get current channel"""
        return self.current_channel
        
    def get_current_channel_name(self):
        """Get current channel name"""
        if hasattr(self, "channel_selector"):
            return self.channel_selector.get_current_channel_name()
        else:
            return f"Channel {self.current_channel}"
        
    def get_current_tab_index(self):
        """Get current tab index"""
        return self.tab_widget.currentIndex()
        
    def set_current_tab(self, index):
        """Set current tab by index"""
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
