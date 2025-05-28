"""
Tabbed Analysis Panel
Main analysis panel with tabs for different analysis tools
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
                            QPushButton, QFrame, QLabel, QComboBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon

from gui.analysis import AnalysisControls, DFAAnalysis, EEGTimelineAnalysis
from gui.analysis.band_spikes import BandSpikes
from gui.analysis.all_bands_power import AllBandsPower
from utils.ui_helpers import create_dark_button, create_dark_combobox


class CollapsibleSidebar(QWidget):
    """Collapsible sidebar widget for controls"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_expanded = True
        self.init_ui()
        
    def init_ui(self):
        """Initialize the sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toggle button
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedWidth(20)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                border: none;
                color: #ffffff;
                padding: 2px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle)
        
        # Content container
        self.content = QWidget()
        self.content.setFixedWidth(250)
        self.content.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-left: 1px solid #555555;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(self.toggle_btn, alignment=Qt.AlignRight)
        layout.addWidget(self.content)
        
    def toggle(self):
        """Toggle sidebar visibility"""
        self.is_expanded = not self.is_expanded
        self.content.setVisible(self.is_expanded)
        self.toggle_btn.setText("▶" if not self.is_expanded else "◀")
        
    def set_content_layout(self, layout):
        """Set the content layout"""
        # Remove old layout if exists
        if self.content.layout():
            QWidget().setLayout(self.content.layout())
        self.content.setLayout(layout)

    def show_threshold_controls(self, show=True):
        """Show or hide threshold controls - for Band Spikes tab"""
        # This is handled by tab switching - no specific implementation needed
        pass

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
        self.current_band = 'Alpha'
        
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
        
        # Tab 2: Band Spikes (with selectors moved here)
        self.create_band_spikes_tab()
        
        # Tab 3: All Band Powers
        self.create_all_bands_tab()
        
        # Tab 4: DFA Analysis
        self.create_dfa_tab()
        
        main_layout.addWidget(self.tab_widget)
        layout.addWidget(main_group)
        
        # Setup connections after all tabs are created
        self.setup_connections()
        
    def create_eeg_timeline_tab(self):
        """Create the EEG Timeline analysis tab"""
        self.eeg_timeline = EEGTimelineAnalysis()
        self.tab_widget.addTab(self.eeg_timeline, "📺 EEG Timeline")
        
    def create_band_spikes_tab(self):
        """Create the Band Spikes analysis tab with selectors"""
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Band spikes widget
        self.band_spikes = BandSpikes()
        # Set initial threshold from spinbox (will be created later)
        # This will be synchronized in setup_connections()
        content_layout.addWidget(self.band_spikes)
        
        # Create sidebar
        self.spikes_sidebar = CollapsibleSidebar()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(10)  # Add spacing between widgets
        
        # Controls header for Band Spikes tab
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)  # Add spacing between widgets
        
        # Channel selector for Band Spikes
        from gui.analysis import ChannelSelector, BandSelector
        self.spikes_channel_selector = ChannelSelector()
        controls_layout.addWidget(self.spikes_channel_selector)
        
        # Band selector for Band Spikes
        self.spikes_band_selector = BandSelector()
        controls_layout.addWidget(self.spikes_band_selector)
        
        # Add spacer before threshold controls
        controls_layout.addSpacing(20)  # Add 20 pixels of space
        
        # Threshold controls
        threshold_group = QGroupBox("Threshold Controls")
        threshold_group.setStyleSheet("""
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
        threshold_layout = QVBoxLayout()
        threshold_layout.setSpacing(8)  # Add spacing between threshold controls
        
        threshold_layout.addWidget(QLabel("Spike Threshold (Standard Deviations):"))
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(1.0, 5.0)
        self.threshold_spinbox.setValue(2.0)  # Default 2.0σ standard deviations
        self.threshold_spinbox.setSuffix("σ")
        self.threshold_spinbox.setDecimals(1)  # Show 1 decimal place
        self.threshold_spinbox.setToolTip(
            "Number of standard deviations above the mean power.\n"
            "Higher values = less sensitive (fewer spikes detected)\n"
            "Lower values = more sensitive (more spikes detected)\n"
            "Typical range: 1.5σ (very sensitive) to 3.0σ (conservative)")
        self.threshold_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px;
                border-radius: 3px;
                min-width: 60px;
            }
        """)
        threshold_layout.addWidget(self.threshold_spinbox)
        
        self.detect_button = create_dark_button("Detect Spikes")
        self.detect_button.clicked.connect(self.on_detect_spikes)
        threshold_layout.addWidget(self.detect_button)
        
        self.spike_count_label = QLabel("Spikes: 0")
        self.spike_count_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        threshold_layout.addWidget(self.spike_count_label)
        
        threshold_group.setLayout(threshold_layout)
        controls_layout.addWidget(threshold_group)
        
        controls_layout.addStretch()
        self.spikes_sidebar.set_content_layout(controls_layout)
        
        # Add widgets to tab layout
        tab_layout.addWidget(content_widget, stretch=1)
        tab_layout.addWidget(self.spikes_sidebar)
        
        self.tab_widget.addTab(tab_widget, "⚡ Band Spikes")
        
    def create_all_bands_tab(self):
        """Create the All Band Powers comparison tab"""
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # All bands power widget
        self.all_bands_power = AllBandsPower()
        content_layout.addWidget(self.all_bands_power)
        
        # Create sidebar
        self.all_bands_sidebar = CollapsibleSidebar()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(10)
        
        # Controls header for All Bands tab
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)
        
        # Channel selector for All Bands
        from gui.analysis import ChannelSelector
        self.all_bands_channel_selector = ChannelSelector()
        controls_layout.addWidget(self.all_bands_channel_selector)
        
        # Add band visibility controls
        band_controls = self.all_bands_power.create_band_controls()
        controls_layout.addWidget(band_controls)
        
        controls_layout.addStretch()
        self.all_bands_sidebar.set_content_layout(controls_layout)
        
        # Add widgets to tab layout
        tab_layout.addWidget(content_widget, stretch=1)
        tab_layout.addWidget(self.all_bands_sidebar)
        
        self.tab_widget.addTab(tab_widget, "📈 All Bands")
        
    def create_dfa_tab(self):
        """Create the DFA analysis tab"""
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # DFA analysis widget
        self.dfa_analysis = DFAAnalysis()
        content_layout.addWidget(self.dfa_analysis)
        
        # Create sidebar
        self.dfa_sidebar = CollapsibleSidebar()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(10)
        
        # Add DFA controls to sidebar
        dfa_controls = self.dfa_analysis.create_controls()
        sidebar_layout.addWidget(dfa_controls)
        
        sidebar_layout.addStretch()
        self.dfa_sidebar.set_content_layout(sidebar_layout)
        
        # Add widgets to tab layout
        tab_layout.addWidget(content_widget, stretch=1)
        tab_layout.addWidget(self.dfa_sidebar)
        
        self.tab_widget.addTab(tab_widget, "📊 DFA")
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # Band Spikes tab connections  
        if hasattr(self, 'spikes_channel_selector'):
            self.spikes_channel_selector.channel_changed.connect(self.on_spikes_channel_changed)
        if hasattr(self, 'spikes_band_selector'):
            self.spikes_band_selector.band_changed.connect(self.on_spikes_band_changed)
            # Also relay from spikes band selector (when user switches to spikes tab)
            self.spikes_band_selector.band_changed.connect(self.band_changed.emit)
            
        # All Bands tab connections
        if hasattr(self, 'all_bands_channel_selector'):
            self.all_bands_channel_selector.channel_changed.connect(self.on_all_bands_channel_changed)
        
        # Connect tab change handler
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        # Connect threshold spinbox
        # Initialize band selector with current band
        if hasattr(self, 'spikes_band_selector') and hasattr(self, 'band_spikes'):
            self.spikes_band_selector.set_current_band(self.current_band)
            self.band_spikes.set_band(self.current_band)
                # Initialize threshold value
        if hasattr(self, 'threshold_spinbox') and hasattr(self, 'band_spikes'):
            initial_threshold = self.threshold_spinbox.value()
            self.band_spikes.set_threshold(initial_threshold)
        
        # Connect threshold spinbox
        if hasattr(self, 'threshold_spinbox'):
            self.threshold_spinbox.valueChanged.connect(self.on_threshold_changed)
        
        # Spike detection signal
        self.band_spikes.spike_detected.connect(self.spike_detected.emit)
        
    def on_spikes_channel_changed(self, channel_idx):
        """Handle channel changes for Band Spikes tab"""
        self.band_spikes.set_channel(channel_idx)
        
    def on_spikes_band_changed(self, band_name):
        """Handle band changes for Band Spikes tab"""
        print(f"🎨 TabbedPanel: Band changed to {band_name} for Band Spikes")
        self.band_spikes.set_band(band_name)
        self.current_band = band_name
        
    def on_threshold_changed(self, value):
        """Handle threshold changes"""
        print(f"🎛️ TabbedPanel: Threshold changed to {value}, current tab: {self.tab_widget.currentIndex()}")
        if self.tab_widget.currentIndex() == 1:  # Band Spikes tab
            self.band_spikes.set_threshold(value)
            self.band_spikes.update_plot()  # Force plot update
            
    def on_detect_spikes(self):
        """Handle spike detection"""
        print(f"🔍 TabbedPanel: Detect spikes clicked, current tab: {self.tab_widget.currentIndex()}")
        if self.tab_widget.currentIndex() == 1:  # Band Spikes tab
            self.band_spikes.detect_spikes()
            self.spike_count_label.setText(f"Spikes: {self.band_spikes.get_spike_count()}")
            self.band_spikes.update_plot()  # Force plot update
            
    def on_all_bands_channel_changed(self, channel_idx):
        """Handle channel changes for All Bands tab"""
        self.all_bands_power.set_channel(channel_idx)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer for all components"""
        print(f"🔄 Tabbed Analysis Panel: Setting analyzer for all tabs...")
        self.analyzer = analyzer
        self.band_spikes.set_analyzer(analyzer)
        self.all_bands_power.set_analyzer(analyzer)
        print(f"📺 Tabbed Analysis Panel: Setting analyzer for EEG Timeline...")
        self.eeg_timeline.set_analyzer(analyzer)
        self.dfa_analysis.set_analyzer(analyzer)
        print(f"✅ Tabbed Analysis Panel: All tabs updated with analyzer")
        
        # Initialize channel selectors with available channels
        if analyzer and analyzer.processor and hasattr(analyzer.processor, "get_channel_names"):
            channel_names = analyzer.processor.get_channel_names()
            if hasattr(self, 'spikes_channel_selector'):
                self.spikes_channel_selector.set_channels(channel_names)
            if hasattr(self, 'all_bands_channel_selector'):
                self.all_bands_channel_selector.set_channels(channel_names)
            # Set initial channel
            if len(channel_names) > 0:
                if hasattr(self, 'spikes_channel_selector'):
                    self.spikes_channel_selector.set_current_channel(0)
                if hasattr(self, 'all_bands_channel_selector'):
                    self.all_bands_channel_selector.set_current_channel(0)
                self.current_channel = 0
        elif analyzer and hasattr(analyzer, "raw") and analyzer.raw:
            # Fallback to direct raw access
            channel_names = analyzer.raw.ch_names
            if hasattr(self, 'spikes_channel_selector'):
                self.spikes_channel_selector.set_channels(channel_names)
            if hasattr(self, 'all_bands_channel_selector'):
                self.all_bands_channel_selector.set_channels(channel_names)
            # Set initial channel
            if len(channel_names) > 0:
                if hasattr(self, 'spikes_channel_selector'):
                    self.spikes_channel_selector.set_current_channel(0)
                if hasattr(self, 'all_bands_channel_selector'):
                    self.all_bands_channel_selector.set_current_channel(0)
                self.current_channel = 0
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        # Update channel selectors display
        if hasattr(self, 'spikes_channel_selector'):
            self.spikes_channel_selector.set_current_channel(channel_idx)
        if hasattr(self, 'all_bands_channel_selector'):
            self.all_bands_channel_selector.set_current_channel(channel_idx)
        # Update all plots
        self.band_spikes.set_channel(channel_idx)
        self.all_bands_power.set_channel(channel_idx)
        self.eeg_timeline.set_channel(channel_idx)
        self.dfa_analysis.set_channel(channel_idx)
        
    def set_time_window(self, current_time, total_duration):
        """Set the current time window"""
        print(f"⏱️ TabbedPanel: Setting time window - current: {current_time}, duration: {total_duration}")
        self.current_time = current_time
        self.current_duration = total_duration
        
        # Update all analysis tabs with current time position
        if hasattr(self, 'band_spikes'):
            self.band_spikes.set_time_window(current_time, total_duration)
        if hasattr(self, 'all_bands_power'):
            self.all_bands_power.set_time_window(current_time, total_duration)
        if hasattr(self, 'eeg_timeline'):
            self.eeg_timeline.set_time_window(current_time, total_duration)
        if hasattr(self, 'dfa_analysis'):
            self.dfa_analysis.set_timeframe(current_time, current_time + total_duration)
        
    def set_timeframe(self, start_time, end_time):
        """Set analysis timeframe for all tabs"""
        print(f"⏱️ TabbedPanel: Setting timeframe - start: {start_time}, end: {end_time}")
        
        # Update EEG Timeline tab (primary tab)
        if hasattr(self, 'eeg_timeline'):
            self.eeg_timeline.set_timeframe(start_time, end_time)
            print(f"✅ TabbedPanel: Updated EEG Timeline X-axis range to {start_time:.1f}s - {end_time:.1f}s")
        
        # Update Band Spikes tab
        if hasattr(self, 'band_spikes'):
            self.band_spikes.set_timeframe(start_time, end_time)
            print(f"✅ TabbedPanel: Updated Band Spikes X-axis range to {start_time:.1f}s - {end_time:.1f}s")        # Update other analysis tabs
        if hasattr(self, 'all_bands_power'):
            self.all_bands_power.set_timeframe(start_time, end_time)
        if hasattr(self, 'dfa_analysis'):
            self.dfa_analysis.set_timeframe(start_time, end_time)
        
    def get_current_band(self):
        """Get currently selected frequency band"""
        if hasattr(self, "spikes_band_selector"):
            return self.spikes_band_selector.get_current_band()
        else:
            from eeg.frequency_bands import FrequencyBands
            return FrequencyBands().get_active_band()
        
    def get_current_channel(self):
        """Get current channel"""
        return self.current_channel
        
    def get_current_channel_name(self):
        """Get current channel name"""
        if hasattr(self, "spikes_channel_selector"):
            return self.spikes_channel_selector.get_current_channel_name()
        else:
            return f"Channel {self.current_channel}"
        
    def get_current_tab_index(self):
        """Get current tab index"""
        return self.tab_widget.currentIndex()
        
    def set_current_tab(self, index):
        """Set current tab by index"""
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)

    def on_tab_changed(self, index):
        """Handle tab changes"""
        # Show/hide threshold controls based on current tab
        self.spikes_sidebar.show_threshold_controls(index == 1)  # Band Spikes tab
        
        # Handle Band Spikes tab specially (it's wrapped in a container)
        if index == 1:  # Band Spikes tab
            if hasattr(self, 'band_spikes'):
                self.band_spikes.set_channel(self.current_channel)
                self.band_spikes.set_band(self.current_band)
        else:
            # Update other tabs normally
            current_widget = self.tab_widget.currentWidget()
            if current_widget:
                if hasattr(current_widget, 'set_channel'):
                    current_widget.set_channel(self.current_channel)
                if hasattr(current_widget, 'set_band'):
                    current_widget.set_band(self.current_band)
                
    def on_channel_changed(self, index):
        """Handle channel selection changes"""
        self.current_channel = index
        
        # Handle Band Spikes tab specially
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 1:  # Band Spikes tab
            if hasattr(self, 'band_spikes'):
                self.band_spikes.set_channel(index)
        else:
            current_widget = self.tab_widget.currentWidget()
            if current_widget:
                if hasattr(current_widget, 'set_channel'):
                    current_widget.set_channel(index)
            
    def on_band_changed(self, band):
        """Handle band selection changes"""
        self.current_band = band
        
        # Handle Band Spikes tab specially
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 1:  # Band Spikes tab
            if hasattr(self, 'band_spikes'):
                self.band_spikes.set_band(band)
        else:
            current_widget = self.tab_widget.currentWidget()
            if current_widget and hasattr(current_widget, 'set_band'):
                current_widget.set_band(band)
            
    def on_show_all(self):
        """Handle show all channels"""
        if isinstance(self.tab_widget.currentWidget(), EEGTimelineAnalysis):
            self.tab_widget.currentWidget().show_all_channels()
            
    def on_hide_all(self):
        """Handle hide all channels"""
        if isinstance(self.tab_widget.currentWidget(), EEGTimelineAnalysis):
            self.tab_widget.currentWidget().hide_all_channels()
            
    def show_threshold_controls(self, show=True):
        """Show or hide threshold controls"""
        self.spikes_sidebar.show_threshold_controls(show)
        
    def get_threshold_value(self):
        """Get the current threshold value"""
        return self.threshold_spinbox.value()
        
    def update_spike_count(self, count):
        """Update the spike count label"""
        self.spike_count_label.setText(f"Spikes: {count}")
