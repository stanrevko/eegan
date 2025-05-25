"""
Shortcuts Manager
Manages keyboard shortcuts for the application
"""

from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QObject, pyqtSignal


class ShortcutsManager(QObject):
    """Manages keyboard shortcuts"""
    
    # Signals
    sidebar_toggle_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.shortcuts = {}
        
    def setup_shortcuts(self):
        """Setup all keyboard shortcuts"""
        # Toggle sidebar
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+B"), self.main_window)
        toggle_shortcut.activated.connect(self.sidebar_toggle_requested.emit)
        self.shortcuts['toggle_sidebar'] = toggle_shortcut
        
        # Refresh file list
        refresh_shortcut = QShortcut(QKeySequence("F5"), self.main_window)
        refresh_shortcut.activated.connect(self.refresh_requested.emit)
        self.shortcuts['refresh'] = refresh_shortcut
        
        # Add more shortcuts as needed
        
    def add_shortcut(self, name, key_sequence, callback):
        """Add a new shortcut"""
        shortcut = QShortcut(QKeySequence(key_sequence), self.main_window)
        shortcut.activated.connect(callback)
        self.shortcuts[name] = shortcut
        
    def remove_shortcut(self, name):
        """Remove a shortcut"""
        if name in self.shortcuts:
            del self.shortcuts[name]
            
    def get_shortcuts_info(self):
        """Get information about all shortcuts"""
        info = {}
        for name, shortcut in self.shortcuts.items():
            info[name] = shortcut.key().toString()
        return info
