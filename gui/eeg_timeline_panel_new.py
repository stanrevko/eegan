"""
EEG Timeline Panel - Simplified and Modular
Uses separate components for plot, timeline, and channel controls
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

from gui.plots import EEGPlotWidget, TimelineControls, ChannelControls


class EEGTimelinePanel(QWidget):
    """Simplified EEG timeline panel using modular components"""
    
    # Signals
    timeline_changed = pyqtSignal(float)
    channel_visibility_changed = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.processor = None
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the UI with modular components"""
        layout = QVBoxLayout(self)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left: EEG plot (takes most space)
        self.eeg_plot = EEGPlotWidget()
        content_layout.addWidget(self.eeg_plot, stretch=3)
        
        # Right: Channel controls
        self.channel_controls = ChannelControls()
        content_layout.addWidget(self.channel_controls, stretch=1)
        
        layout.addLayout(content_layout)
        
        # Bottom: Timeline controls
        self.timeline_controls = TimelineControls()
        layout.addWidget(self.timeline_controls)
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # Timeline controls to plot
        self.timeline_controls.position_changed.connect(
            self.eeg_plot.set_current_position
        )
        self.timeline_controls.position_changed.connect(
            self.timeline_changed.emit
        )
        
        # Channel controls to plot
        self.channel_controls.visibility_changed.connect(
            self.eeg_plot.set_visible_channels
        )
        self.channel_controls.visibility_changed.connect(
            self.channel_visibility_changed.emit
        )
        self.channel_controls.scale_changed.connect(
            self.eeg_plot.set_scale
        )
        self.channel_controls.spacing_changed.connect(
            self.eeg_plot.set_spacing
        )
        
        # Plot to timeline (for updates)
        self.eeg_plot.position_changed.connect(
            self.timeline_controls.set_position
        )
        
    def set_processor(self, processor):
        """Set the EEG processor for all components"""
        self.processor = processor
        
        if processor:
            # Update plot
            self.eeg_plot.set_processor(processor)
            
            # Update timeline
            duration = processor.get_duration()
            self.timeline_controls.set_duration(duration)
            
            # Update channel controls
            channel_names = processor.get_channel_names()
            self.channel_controls.set_channels(channel_names)
            
    def get_visible_channels(self):
        """Get currently visible channels"""
        return self.channel_controls.get_visible_channels()
        
    def get_current_position(self):
        """Get current timeline position"""
        return self.timeline_controls.get_current_position()
        
    def set_current_position(self, position):
        """Set current timeline position"""
        self.timeline_controls.set_position(position)
