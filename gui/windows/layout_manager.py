"""
Layout Manager
Manages panel layout and splitter configurations
"""

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSplitter
from PyQt5.QtCore import Qt, QObject, pyqtSignal


class LayoutManager(QObject):
    """Manages the main window layout"""
    
    # Signals
    layout_changed = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.main_splitter = None
        self.analysis_splitter = None
        
    def setup_main_layout(self):
        """Setup the main window layout"""
        # Central widget
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        return self.main_splitter
        
    def setup_analysis_area(self):
        """Setup the analysis area with vertical splitter"""
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        analysis_layout.setContentsMargins(0, 0, 0, 0)
        
        # Vertical splitter for main analysis area
        self.analysis_splitter = QSplitter(Qt.Vertical)
        analysis_layout.addWidget(self.analysis_splitter)
        
        return analysis_widget, self.analysis_splitter
        
    def set_sidebar_proportions(self, sidebar_visible):
        """Set splitter proportions based on sidebar visibility"""
        if self.main_splitter:
            if sidebar_visible:
                self.main_splitter.setSizes([300, 1300])
            else:
                self.main_splitter.setSizes([0, 1600])
                
    def set_analysis_proportions(self):
        """Set analysis area proportions"""
        if self.analysis_splitter:
            # EEG timeline gets more space than analysis panel
            self.analysis_splitter.setSizes([700, 300])
            
    def add_sidebar_widget(self, widget):
        """Add widget to sidebar area"""
        if self.main_splitter:
            self.main_splitter.insertWidget(0, widget)
            
    def add_analysis_widget(self, widget):
        """Add widget to analysis area"""
        if self.main_splitter:
            self.main_splitter.addWidget(widget)
            
    def add_to_analysis_splitter(self, widget):
        """Add widget to analysis splitter"""
        if self.analysis_splitter:
            self.analysis_splitter.addWidget(widget)
