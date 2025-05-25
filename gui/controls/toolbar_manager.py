"""
Toolbar Manager
Manages the main toolbar and its actions
"""

from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import QObject, pyqtSignal


class ToolbarManager(QObject):
    """Manages toolbar actions and state"""
    
    # Signals
    sidebar_toggle_requested = pyqtSignal(bool)
    file_info_updated = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.toolbar = None
        self.sidebar_action = None
        self.file_info_action = None
        
    def create_toolbar(self):
        """Create the main toolbar"""
        self.toolbar = self.main_window.addToolBar("Main")
        self.toolbar.setMovable(False)
        
        # Sidebar toggle action
        self.sidebar_action = QAction("📁 Hide Sidebar", self.main_window)
        self.sidebar_action.setCheckable(True)
        self.sidebar_action.triggered.connect(self._on_sidebar_toggle)
        self.toolbar.addAction(self.sidebar_action)
        
        # Add separator
        self.toolbar.addSeparator()
        
        # File info action
        self.file_info_action = QAction("📄 No file loaded", self.main_window)
        self.file_info_action.setEnabled(False)
        self.toolbar.addAction(self.file_info_action)
        
        return self.toolbar
        
    def update_sidebar_action(self, sidebar_visible):
        """Update sidebar action state and text"""
        self.sidebar_action.setChecked(not sidebar_visible)
        if sidebar_visible:
            self.sidebar_action.setText("📁 Hide Sidebar")
        else:
            self.sidebar_action.setText("📁 Show Sidebar")
            
    def update_file_info(self, file_info):
        """Update file info in toolbar"""
        if self.file_info_action:
            self.file_info_action.setText(file_info)
            
    def set_loading_state(self, filename):
        """Set toolbar to loading state"""
        if self.file_info_action:
            self.file_info_action.setText(f"🔄 Loading: {filename}")
            
    def set_loaded_state(self, file_info):
        """Set toolbar to loaded state"""
        if self.file_info_action:
            filename = file_info['filename']
            duration = file_info['duration']
            self.file_info_action.setText(f"📄 {filename} ({duration:.1f}s)")
            
    def set_no_file_state(self):
        """Set toolbar to no file loaded state"""
        if self.file_info_action:
            self.file_info_action.setText("📄 No file loaded")
            
    def _on_sidebar_toggle(self, checked):
        """Handle sidebar toggle from toolbar"""
        self.sidebar_toggle_requested.emit(not checked)
