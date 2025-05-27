"""
Enhanced Main Window - Improved Layout
- Status bar moved to sidebar
- Timeline moved to topbar
- Added timeframe controls
- Fixed plot scrolling limits
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, 
                             QWidget, QSplitter, QMessageBox, QProgressBar, QToolBar,
                             QLabel, QDoubleSpinBox, QFrame, QPushButton)
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
from gui.analysis import TabbedAnalysisPanel
from gui.plots import TimelineControls


class TimeframeControls(QWidget):
    """Timeframe selector for analysis window"""
    
    timeframe_changed = pyqtSignal(float, float)  # start_time, end_time
    
    def __init__(self):
        super().__init__()
        self.total_duration = 0
        self.start_time = 0
        self.end_time = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize timeframe controls"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        
        # Timeframe label
        label = QLabel("📊 Analysis Window:")
        label.setStyleSheet("font-weight: bold; color: #ffffff;")
        layout.addWidget(label)
        
        # Start time
        layout.addWidget(QLabel("From:"))
        self.start_spin = QDoubleSpinBox()
        self.start_spin.setMinimum(0)
        self.start_spin.setMaximum(999)
        self.start_spin.setSuffix("s")
        self.start_spin.setDecimals(1)
        self.start_spin.valueChanged.connect(self.on_timeframe_changed)
        layout.addWidget(self.start_spin)
        
        # End time
        layout.addWidget(QLabel("To:"))
        self.end_spin = QDoubleSpinBox()
        self.end_spin.setMinimum(0)
        self.end_spin.setMaximum(999)
        self.end_spin.setSuffix("s")
        self.end_spin.setDecimals(1)
        self.end_spin.valueChanged.connect(self.on_timeframe_changed)
        layout.addWidget(self.end_spin)
        
        # Set full range button
        self.full_range_btn = QPushButton("Full Range")
        self.full_range_btn.clicked.connect(self.set_full_range)
        layout.addWidget(self.full_range_btn)
        
        # Apply dark styling
        self.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
                min-width: 60px;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
    def set_duration(self, duration):
        """Set total duration and update controls"""
        self.total_duration = duration
        
        # Update spinbox ranges
        self.start_spin.setMaximum(duration)
        self.end_spin.setMaximum(duration)
        
        # Set initial values to full range
        self.start_spin.setValue(0)
        self.end_spin.setValue(duration)
        
        self.start_time = 0
        self.end_time = duration
        
    def on_timeframe_changed(self):
        """Handle timeframe changes"""
        self.start_time = self.start_spin.value()
        self.end_time = self.end_spin.value()
        
        # Ensure start < end
        if self.start_time >= self.end_time:
            if self.sender() == self.start_spin:
                self.end_spin.setValue(self.start_time + 0.1)
                self.end_time = self.end_spin.value()
            else:
                self.start_spin.setValue(max(0, self.end_time - 0.1))
                self.start_time = self.start_spin.value()
                
        self.timeframe_changed.emit(self.start_time, self.end_time)
        
    def set_full_range(self):
        """Set timeframe to full range"""
        self.start_spin.setValue(0)
        self.end_spin.setValue(self.total_duration)
        
    def get_timeframe(self):
        """Get current timeframe"""
        return self.start_time, self.end_time


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


class EnhancedFilePanel(QWidget):
    """Enhanced file panel with status bar integrated"""
    
    file_selected = pyqtSignal(str)
    folder_changed = pyqtSignal(str)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize enhanced file panel with status"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # File panel
        self.file_panel = FilePanel(self.settings)
        self.file_panel.file_selected.connect(self.file_selected.emit)
        self.file_panel.folder_changed.connect(self.folder_changed.emit)
        layout.addWidget(self.file_panel)
        
        # Status section (moved from bottom status bar)
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Box)
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 5px;
            }
        """)
        
        status_layout = QVBoxLayout(status_frame)
        
        # Status label
        status_title = QLabel("📊 Status")
        status_title.setStyleSheet("font-weight: bold; color: #ffffff; padding: 5px;")
        status_layout.addWidget(status_title)
        
        # Status message
        self.status_label = QLabel("🧠 EEG Analysis Suite Ready")
        self.status_label.setStyleSheet("color: #ffffff; padding: 5px; font-size: 11px;")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                background-color: #2b2b2b;
                color: #ffffff;
                text-align: center;
                height: 15px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
        """)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_frame)
        
    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)
        
    def show_progress(self, show=True):
        """Show/hide progress bar"""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate


class MainWindow(QMainWindow):
    """Enhanced main window with improved layout"""
    
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
        """Initialize the enhanced user interface"""
        # Window setup
        self.setWindowTitle("🧠 EEG Analysis Suite - Enhanced Layout")
        
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
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Create panels
        self.create_sidebar()
        self.create_analysis_area()
        
        # Create bottom panel with timeline controls
        self.create_bottom_panel()
        main_layout.addWidget(self.bottom_panel)
        
        # Setup splitter proportions
        self.main_splitter.setSizes([300, 1300])
        
        # No status bar at bottom anymore (moved to sidebar)
        
    def create_bottom_panel(self):
        """Create bottom panel with timeline and timeframe controls"""
        self.bottom_panel = QWidget()
        self.bottom_panel.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
                border-top: 1px solid #555555;
                padding: 5px;
            }
        """)
        
        bottom_layout = QHBoxLayout(self.bottom_panel)
        bottom_layout.setContentsMargins(10, 5, 10, 5)
        
        # Timeline controls
        self.timeline_controls = TimelineControls()
        self.timeline_controls.position_changed.connect(self.on_timeline_changed)
        bottom_layout.addWidget(self.timeline_controls)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #555555;")
        bottom_layout.addWidget(separator)
        
        # Timeframe controls
        self.timeframe_controls = TimeframeControls()
        self.timeframe_controls.timeframe_changed.connect(self.on_timeframe_changed)
        bottom_layout.addWidget(self.timeframe_controls)
        
        bottom_layout.addStretch()
        
        # Sidebar toggle button
        self.sidebar_toggle_btn = QPushButton("📁 Hide Sidebar")
        self.sidebar_toggle_btn.setCheckable(True)
        self.sidebar_toggle_btn.setChecked(not self.sidebar_visible)
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                color: #ffffff;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
        """)
        bottom_layout.addWidget(self.sidebar_toggle_btn)

    def create_toolbar(self):
        """Create minimal toolbar (reserved for future use)"""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setVisible(False)  # Hide empty toolbar
        
    def create_sidebar(self):
        """Create enhanced sidebar with integrated status"""
        # Enhanced file panel with status
        self.file_panel = EnhancedFilePanel(self.settings)
        self.file_panel.file_selected.connect(self.auto_load_file)
        self.file_panel.folder_changed.connect(self.on_folder_changed)
        
        self.sidebar_widget = self.file_panel
        self.main_splitter.addWidget(self.file_panel)
        
        # Set initial visibility
        self.file_panel.setVisible(self.sidebar_visible)
        
    def create_analysis_area(self):
        """Create analysis area with tabbed analysis panel"""
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        analysis_layout.setContentsMargins(0, 0, 0, 0)
        
        # Analysis Panel (full area)
        self.analysis_panel = TabbedAnalysisPanel()
        self.analysis_panel.band_changed.connect(self.on_frequency_band_changed)
        self.analysis_panel.spike_detected.connect(self.on_spike_detected)
        analysis_layout.addWidget(self.analysis_panel)        
        
        
        
        self.main_splitter.addWidget(analysis_widget)
        
        # Ensure analysis panels are visible
        self.analysis_panel.show()
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Toggle sidebar
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        toggle_shortcut.activated.connect(self.toggle_sidebar_shortcut)
        
        # Refresh file list
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.file_panel.file_panel.refresh_file_list)
        
    def toggle_sidebar(self, checked):
        """Toggle sidebar via bottom panel button"""
        self.sidebar_visible = not checked
        self.file_panel.setVisible(self.sidebar_visible)
        self.settings.set('sidebar_visible', self.sidebar_visible)
        
        # Update splitter sizes
        if self.sidebar_visible:
            self.main_splitter.setSizes([300, 1300])
        else:
            self.main_splitter.setSizes([0, 1600])
            
        # Update button text
        self.update_sidebar_button_text()

    def update_sidebar_button_text(self):
        """Update the sidebar button text"""
        if hasattr(self, 'sidebar_toggle_btn'):
            if self.sidebar_visible:
                self.sidebar_toggle_btn.setText("📁 Hide Sidebar")
            else:
                self.sidebar_toggle_btn.setText("📁 Show Sidebar")

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
            
        # Sidebar action text update removed
        
    def toggle_sidebar_shortcut(self):
        """Toggle sidebar via keyboard shortcut"""
        if hasattr(self, 'sidebar_toggle_btn'):
            self.sidebar_toggle_btn.setChecked(not self.sidebar_toggle_btn.isChecked())
            self.toggle_sidebar(self.sidebar_toggle_btn.isChecked())
        

            
    def auto_load_file(self, file_path):
        """Auto-load selected file"""
        if not os.path.exists(file_path):
            self.file_panel.update_status("❌ File not found")
            return
            
        file_name = os.path.basename(file_path)
        
        # Update toolbar
        # File info removed from UI
        
        # Show progress in sidebar
        self.file_panel.show_progress(True)
        
        # Start background loading
        self.load_thread = EEGLoadThread(file_path)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.progress.connect(self.update_progress)
        self.load_thread.start()
        
        self.file_panel.update_status(f"🔄 Auto-loading: {file_name}")
        
    def update_progress(self, message):
        """Update progress message"""
        self.file_panel.update_status(message)
        
    def on_load_finished(self, success, message):
        """Handle file loading completion"""
        self.file_panel.show_progress(False)
        
        if success:
            # Store analysis components
            self.loader = self.load_thread.loader
            self.processor = self.load_thread.processor
            self.analyzer = self.load_thread.analyzer
            
            # Update toolbar
            file_info = self.loader.get_file_info()
            # File info removed from UI
            
            # Update timeline and timeframe controls
            duration = self.processor.get_duration()
            self.timeline_controls.set_duration(duration)
            self.timeframe_controls.set_duration(duration)
            
            # Update all panels
            self.update_all_panels()
            
            self.file_panel.update_status(message)
        else:
            # File info removed from UI
            self.file_panel.update_status(message)
            
    def update_all_panels(self):
        """Update analysis panels with new data"""
        if not self.processor or not self.analyzer:
            return
            
        try:
            
            # Update analysis panel
            print(f"🔄 Main Window: Setting analyzer for analysis panel...")
            self.analysis_panel.set_analyzer(self.analyzer)
            print(f"✅ Main Window: Analysis panel updated with analyzer")
            
            # Set initial channel to first channel
            initial_channel = 0
            self.analysis_panel.set_channel(initial_channel)
                
            self.file_panel.update_status("✅ EEG timeline and band analysis ready!")
            
        except Exception as e:
            error_msg = f"Error updating panels: {str(e)}"
            self.file_panel.update_status(error_msg)
            print(error_msg)
            
    def on_timeline_changed(self, position):
        """Handle timeline position changes - sync with analysis"""
        if self.analysis_panel and self.processor:
            # Get current time window from timeline controls
            current_time = position
            duration = self.processor.get_duration()
            
            # Update analysis panel to sync with timeline
            self.analysis_panel.set_time_window(current_time, duration)
            
            
    def on_timeframe_changed(self, start_time, end_time):
        """Handle timeframe changes for analysis window"""
        if self.analyzer:
            # Update analysis to use specific timeframe
            self.analysis_panel.set_timeframe(start_time, end_time)
            self.file_panel.update_status(f"📊 Analysis window: {start_time:.1f}s - {end_time:.1f}s")
            
            
    def on_frequency_band_changed(self, band_name):
        """Handle frequency band changes"""
        self.file_panel.update_status(f"📊 Switched to {band_name} band analysis")
        
    def on_spike_detected(self, spike_time, band_name):
        """Handle spike detection events"""
        try:
            print(f"🔥 Spike detected in {band_name} band at {spike_time:.2f}s")
            # You can add more spike handling logic here:
            # - Log to file
            # - Show notification  
            # - Jump to spike location
            # - Analyze spike patterns
        except Exception as e:
            print(f"Error handling spike detection: {e}")

    def on_folder_changed(self, folder_path):
        """Handle folder changes"""
        self.file_panel.update_status(f"📁 Folder changed to: {os.path.basename(folder_path)}")
        
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
    app.setApplicationVersion("2.2")
    app.setOrganizationName("EEG Research")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
