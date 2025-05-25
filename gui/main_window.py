"""
Enhanced Main Window - Simplified layout
EEG timeline + Alpha analysis only (spectrum hidden)
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, 
                             QWidget, QSplitter, QMessageBox, QProgressBar, QToolBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut, QAction

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from eeg.loader import EEGLoader
from eeg.processor import EEGProcessor
from eeg.analyzer import EEGAnalyzer
from utils.settings import AppSettings
from utils.ui_helpers import create_styled_button, create_collapsible_button
from gui.file_panel import FilePanel
from gui.eeg_timeline_panel import EEGTimelinePanel
from gui.analysis_panel import AnalysisPanel


class EEGLoadThread(QThread):
    """Background thread for loading and processing EEG files"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            self.progress.emit("🔄 Loading EEG file...")
            loader = EEGLoader()
            
            if loader.load_edf(self.file_path):
                self.progress.emit("🔧 Applying 0.1-40Hz filter...")
                processor = EEGProcessor()
                processor.set_raw_data(loader.raw)
                processor.apply_bandpass_filter(l_freq=0.1, h_freq=40.0)
                
                self.progress.emit("⚡ Calculating frequency analysis...")
                analyzer = EEGAnalyzer()
                analyzer.set_processor(processor)
                
                # Store results
                self.loader = loader
                self.processor = processor
                self.analyzer = analyzer
                self.finished.emit(True, "✅ Complete analysis ready!")
            else:
                self.finished.emit(False, "❌ Failed to load file")
                
        except Exception as e:
            self.finished.emit(False, f"❌ Error: {str(e)}")


class MainWindow(QMainWindow):
    """Enhanced main window - simplified layout"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.settings = AppSettings()
        self.loader = None
        self.processor = None
        self.analyzer = None
        
        # UI state
        self.sidebar_visible = self.settings.get('sidebar_visible', True)
        
        self.init_ui()
        self.create_toolbar()
        self.setup_shortcuts()
        self.restore_window_state()
        
    def init_ui(self):
        """Initialize the simplified user interface"""
        # Window setup
        self.setWindowTitle("🧠 EEG Analysis Suite - Timeline + Band Analysis")
        
        # Apply dark theme
        self.setStyleSheet("""
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
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Create panels
        self.create_sidebar()
        self.create_analysis_area()
        
        # Setup splitter proportions
        self.main_splitter.setSizes([300, 1300])
        
        # Status bar
        self.statusBar().setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        self.statusBar().showMessage("🧠 EEG Analysis Suite - Timeline + Band Analysis")
        
        # Progress bar (initially hidden)
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
        self.statusBar().addPermanentWidget(self.progress_bar)
        
    def create_toolbar(self):
        """Create toolbar with sidebar toggle"""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        
        # Sidebar toggle action
        self.sidebar_action = QAction("📁 Hide Sidebar", self)
        self.sidebar_action.setCheckable(True)
        self.sidebar_action.setChecked(not self.sidebar_visible)
        self.sidebar_action.triggered.connect(self.toggle_sidebar_action)
        toolbar.addAction(self.sidebar_action)
        
        # Add separator
        toolbar.addSeparator()
        
        # File info action
        self.file_info_action = QAction("📄 No file loaded", self)
        self.file_info_action.setEnabled(False)
        toolbar.addAction(self.file_info_action)
        
        # Update sidebar toggle text
        self.update_sidebar_action_text()
        
    def create_sidebar(self):
        """Create collapsible sidebar with file panel"""
        # File panel
        self.file_panel = FilePanel(self.settings)
        self.file_panel.file_selected.connect(self.auto_load_file)
        self.file_panel.folder_changed.connect(self.on_folder_changed)
        
        self.sidebar_widget = self.file_panel
        self.main_splitter.addWidget(self.file_panel)
        
        # Set initial visibility
        self.file_panel.setVisible(self.sidebar_visible)
        
    def create_analysis_area(self):
        """Create simplified 2-panel analysis area (EEG + Band Analysis only)"""
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        analysis_layout.setContentsMargins(0, 0, 0, 0)
        
        # Vertical splitter for main analysis area
        self.analysis_splitter = QSplitter(Qt.Vertical)
        analysis_layout.addWidget(self.analysis_splitter)
        
        # TOP: EEG Timeline Panel (larger portion)
        self.eeg_panel = EEGTimelinePanel()
        self.eeg_panel.timeline_changed.connect(self.on_timeline_changed)
        self.eeg_panel.channel_visibility_changed.connect(self.on_channel_visibility_changed)
        self.analysis_splitter.addWidget(self.eeg_panel)
        
        # BOTTOM: Band Analysis Panel (smaller portion)
        self.analysis_panel = AnalysisPanel()
        self.analysis_panel.band_changed.connect(self.on_frequency_band_changed)
        self.analysis_splitter.addWidget(self.analysis_panel)
        
        # Set vertical splitter proportions (EEG gets more space)
        self.analysis_splitter.setSizes([700, 300])
        
        self.main_splitter.addWidget(analysis_widget)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Toggle sidebar
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        toggle_shortcut.activated.connect(self.toggle_sidebar_shortcut)
        
        # Refresh file list
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.file_panel.refresh_file_list)
        
    def toggle_sidebar_action(self, checked):
        """Toggle sidebar via toolbar action"""
        self.sidebar_visible = not checked
        self.file_panel.setVisible(self.sidebar_visible)
        self.settings.set('sidebar_visible', self.sidebar_visible)
        
        # Update splitter sizes
        if self.sidebar_visible:
            self.main_splitter.setSizes([300, 1300])
        else:
            self.main_splitter.setSizes([0, 1600])
            
        self.update_sidebar_action_text()
        
    def toggle_sidebar_shortcut(self):
        """Toggle sidebar via keyboard shortcut"""
        self.sidebar_action.setChecked(not self.sidebar_action.isChecked())
        self.toggle_sidebar_action(self.sidebar_action.isChecked())
        
    def update_sidebar_action_text(self):
        """Update the sidebar action text"""
        if self.sidebar_visible:
            self.sidebar_action.setText("📁 Hide Sidebar")
        else:
            self.sidebar_action.setText("📁 Show Sidebar")
            
    def auto_load_file(self, file_path):
        """Auto-load selected file"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "File not found")
            return
            
        file_name = os.path.basename(file_path)
        
        # Update toolbar
        self.file_info_action.setText(f"🔄 Loading: {file_name}")
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Start background loading
        self.load_thread = EEGLoadThread(file_path)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.progress.connect(self.update_progress)
        self.load_thread.start()
        
        self.statusBar().showMessage(f"🔄 Auto-loading: {file_name}")
        
    def update_progress(self, message):
        """Update progress message"""
        self.statusBar().showMessage(message)
        
    def on_load_finished(self, success, message):
        """Handle file loading completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            # Store analysis components
            self.loader = self.load_thread.loader
            self.processor = self.load_thread.processor
            self.analyzer = self.load_thread.analyzer
            
            # Update toolbar
            file_info = self.loader.get_file_info()
            self.file_info_action.setText(f"📄 {file_info['filename']} ({file_info['duration']:.1f}s)")
            
            # Update all panels
            self.update_all_panels()
            
            self.statusBar().showMessage(message)
        else:
            self.file_info_action.setText("📄 No file loaded")
            QMessageBox.critical(self, "Loading Error", message)
            self.statusBar().showMessage(message)
            
    def update_all_panels(self):
        """Update analysis panels with new data"""
        if not self.processor or not self.analyzer:
            return
            
        try:
            # Update EEG timeline panel
            self.eeg_panel.set_processor(self.processor)
            
            # Update analysis panel
            self.analysis_panel.set_analyzer(self.analyzer)
            
            # Set initial channel (first visible channel)
            visible_channels = self.eeg_panel.get_visible_channels()
            if visible_channels:
                initial_channel = visible_channels[0]
                self.analysis_panel.set_channel(initial_channel)
                
            self.statusBar().showMessage("✅ EEG timeline and band analysis ready!")
            
        except Exception as e:
            error_msg = f"Error updating panels: {str(e)}"
            self.statusBar().showMessage(error_msg)
            print(error_msg)
            
    def on_timeline_changed(self, position):
        """Handle timeline position changes - sync with analysis"""
        if self.analysis_panel and self.processor:
            # Get current time window from EEG panel
            current_time = self.eeg_panel.get_current_position()
            duration = self.processor.get_duration()
            
            # Update analysis panel to sync with timeline
            self.analysis_panel.set_time_window(current_time, duration)
            
    def on_channel_visibility_changed(self, visible_channels):
        """Handle channel visibility changes"""
        if visible_channels and self.analyzer:
            # Update analysis panel to use first visible channel
            self.analysis_panel.set_channel(visible_channels[0])
            
    def on_frequency_band_changed(self, band_name):
        """Handle frequency band changes"""
        self.statusBar().showMessage(f"📊 Switched to {band_name} band analysis")
        
    def on_folder_changed(self, folder_path):
        """Handle folder changes"""
        self.statusBar().showMessage(f"📁 Folder changed to: {os.path.basename(folder_path)}")
        
    def restore_window_state(self):
        """Restore window geometry from settings"""
        geometry = self.settings.get('window_geometry')
        if geometry:
            self.setGeometry(geometry['x'], geometry['y'], geometry['width'], geometry['height'])
        else:
            self.setGeometry(50, 50, 1600, 1000)
            
    def save_window_state(self):
        """Save current window state"""
        geometry = self.geometry()
        self.settings.set('window_geometry', {
            'x': geometry.x(),
            'y': geometry.y(),
            'width': geometry.width(),
            'height': geometry.height()
        })
        
    def closeEvent(self, event):
        """Handle application close"""
        self.save_window_state()
        super().closeEvent(event)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Set application properties
    app.setApplicationName("EEG Analysis Suite")
    app.setApplicationVersion("2.1")
    app.setOrganizationName("EEG Research")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
