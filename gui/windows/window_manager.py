"""
Window Manager
Handles window state, geometry, and UI theme
"""

from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QObject, pyqtSignal


class WindowManager(QObject):
    """Manages window state and appearance"""
    
    # Signals
    sidebar_toggled = pyqtSignal(bool)
    progress_updated = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = main_window.settings
        self.sidebar_visible = self.settings.get('sidebar_visible', True)
        
        self.setup_progress_bar()
        
    def setup_progress_bar(self):
        """Setup the progress bar"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                background-color: #3c3c3c;
                color: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
        """)
        self.progress_bar.setVisible(False)
        self.main_window.statusBar().addPermanentWidget(self.progress_bar)
        
    def apply_dark_theme(self):
        """Apply dark theme to the main window"""
        self.main_window.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QSplitter::handle {
                background-color: #555555;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
            QSplitter::handle:vertical {
                height: 3px;
            }
            QToolBar {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                spacing: 10px;
                padding: 5px;
            }
            QToolBar QToolButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 12px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 80px;
            }
            QToolBar QToolButton:hover {
                background-color: #106ebe;
            }
            QToolBar QToolButton:pressed {
                background-color: #005a9e;
            }
            QToolBar QToolButton:checked {
                background-color: #005a9e;
            }
        """)
        
    def toggle_sidebar(self, visible=None):
        """Toggle sidebar visibility"""
        if visible is None:
            self.sidebar_visible = not self.sidebar_visible
        else:
            self.sidebar_visible = visible
            
        self.settings.set('sidebar_visible', self.sidebar_visible)
        self.sidebar_toggled.emit(self.sidebar_visible)
        
    def show_progress(self, message="Loading..."):
        """Show progress bar with message"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.main_window.statusBar().showMessage(message)
        
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)
        
    def update_status(self, message):
        """Update status bar message"""
        self.main_window.statusBar().showMessage(message)
        
    def restore_geometry(self):
        """Restore window geometry from settings"""
        geometry = self.settings.get('window_geometry')
        if geometry:
            self.main_window.setGeometry(
                geometry['x'], geometry['y'], 
                geometry['width'], geometry['height']
            )
        else:
            self.main_window.setGeometry(50, 50, 1600, 1000)
            
    def save_geometry(self):
        """Save current window geometry"""
        geometry = self.main_window.geometry()
        self.settings.set('window_geometry', {
            'x': geometry.x(),
            'y': geometry.y(),
            'width': geometry.width(),
            'height': geometry.height()
        })
