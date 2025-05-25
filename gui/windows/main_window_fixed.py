"""
Main Window - Fixed Layout Issues
Clean main window with proper widget visibility
"""

import sys
import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.settings import AppSettings
from gui.file_panel import FilePanel
from gui.eeg_timeline_panel import EEGTimelinePanel
from gui.analysis_panel import AnalysisPanel
from gui.threading import EEGLoadThread
from gui.windows.window_manager import WindowManager
from gui.windows.layout_manager import LayoutManager
from gui.controls.toolbar_manager import ToolbarManager
from gui.controls.shortcuts_manager import ShortcutsManager


class MainWindow(QMainWindow):
    """Enhanced main window - modular and fixed layout"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.settings = AppSettings()
        self.loader = None
        self.processor = None
        self.analyzer = None
        
        # Initialize managers
        self.window_manager = WindowManager(self)
        self.layout_manager = LayoutManager(self)
        self.toolbar_manager = ToolbarManager(self)
        self.shortcuts_manager = ShortcutsManager(self)
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Window setup
        self.setWindowTitle("🧠 EEG Analysis Suite - Timeline + Band Analysis")
        
        # Apply theme first
        self.window_manager.apply_dark_theme()
        
        # Setup layout components
        self.setup_layout()
        self.setup_toolbar()
        self.setup_shortcuts()
        self.setup_status_bar()
        
        # Restore window state
        self.window_manager.restore_geometry()
        
        # Force show all components
        self.show_all_components()
        
    def setup_layout(self):
        """Setup the main layout"""
        print("🔧 Setting up main layout...")
        
        # Create main layout
        main_splitter = self.layout_manager.setup_main_layout()
        
        # Create sidebar
        self.file_panel = FilePanel(self.settings)
        self.layout_manager.add_sidebar_widget(self.file_panel)
        
        # Create analysis area
        analysis_widget, analysis_splitter = self.layout_manager.setup_analysis_area()
        
        # Create EEG timeline panel
        self.eeg_panel = EEGTimelinePanel()
        self.layout_manager.add_to_analysis_splitter(self.eeg_panel)
        
        # Create band analysis panel
        self.analysis_panel = AnalysisPanel()
        self.layout_manager.add_to_analysis_splitter(self.analysis_panel)
        
        # Add analysis area to main layout
        self.layout_manager.add_analysis_widget(analysis_widget)
        
        # Set proportions
        self.layout_manager.set_sidebar_proportions(
            self.window_manager.sidebar_visible
        )
        self.layout_manager.set_analysis_proportions()
        
        print("✅ Main layout setup complete")
        
    def show_all_components(self):
        """Force show all components and set proper sizes"""
        print("👁️ Showing all components...")
        
        # Show main panels
        self.file_panel.show()
        self.eeg_panel.show() 
        self.analysis_panel.show()
        
        # Force visibility based on sidebar setting
        sidebar_visible = self.window_manager.sidebar_visible
        self.file_panel.setVisible(sidebar_visible)
        
        # Set minimum sizes
        self.eeg_panel.setMinimumSize(400, 200)
        self.analysis_panel.setMinimumSize(400, 150)
        
        if sidebar_visible:
            self.file_panel.setMinimumSize(250, 200)
        
        # Force splitter sizes
        if self.layout_manager.main_splitter:
            if sidebar_visible:
                self.layout_manager.main_splitter.setSizes([300, 900])
            else:
                self.layout_manager.main_splitter.setSizes([0, 1200])
                
        if self.layout_manager.analysis_splitter:
            self.layout_manager.analysis_splitter.setSizes([500, 250])
            
        print(f"✅ Components shown, sidebar visible: {sidebar_visible}")
        
    def setup_toolbar(self):
        """Setup the toolbar"""
        self.toolbar_manager.create_toolbar()
        self.toolbar_manager.update_sidebar_action(
            self.window_manager.sidebar_visible
        )
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.shortcuts_manager.setup_shortcuts()
        
    def setup_status_bar(self):
        """Setup the status bar"""
        self.statusBar().setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        self.statusBar().showMessage("🧠 EEG Analysis Suite - Timeline + Band Analysis")
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # File panel connections
        self.file_panel.file_selected.connect(self.auto_load_file)
        self.file_panel.folder_changed.connect(self.on_folder_changed)
        
        # EEG panel connections
        self.eeg_panel.timeline_changed.connect(self.on_timeline_changed)
        self.eeg_panel.channel_visibility_changed.connect(self.on_channel_visibility_changed)
        
        # Analysis panel connections
        self.analysis_panel.band_changed.connect(self.on_frequency_band_changed)
        
        # Window manager connections
        self.window_manager.sidebar_toggled.connect(self.on_sidebar_toggled)
        
        # Toolbar connections
        self.toolbar_manager.sidebar_toggle_requested.connect(
            self.window_manager.toggle_sidebar
        )
        
        # Shortcuts connections
        self.shortcuts_manager.sidebar_toggle_requested.connect(
            self.toggle_sidebar_shortcut
        )
        self.shortcuts_manager.refresh_requested.connect(
            self.file_panel.refresh_file_list
        )
        
    def auto_load_file(self, file_path):
        """Auto-load selected file"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "File not found")
            return
            
        file_name = os.path.basename(file_path)
        
        # Update UI for loading state
        self.toolbar_manager.set_loading_state(file_name)
        self.window_manager.show_progress(f"🔄 Auto-loading: {file_name}")
        
        # Start background loading
        self.load_thread = EEGLoadThread(file_path)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.progress.connect(self.window_manager.update_status)
        self.load_thread.start()
        
    def on_load_finished(self, success, message):
        """Handle file loading completion"""
        self.window_manager.hide_progress()
        
        if success:
            # Store analysis components
            self.loader, self.processor, self.analyzer = self.load_thread.get_results()
            
            # Update toolbar with file info
            file_info = self.loader.get_file_info()
            self.toolbar_manager.set_loaded_state(file_info)
            
            # Update all panels
            self.update_all_panels()
            
            self.window_manager.update_status(message)
        else:
            self.toolbar_manager.set_no_file_state()
            QMessageBox.critical(self, "Loading Error", message)
            self.window_manager.update_status(message)
            
    def update_all_panels(self):
        """Update analysis panels with new data"""
        if not self.processor or not self.analyzer:
            return
            
        try:
            print("🔄 Updating all panels with new data...")
            
            # Update EEG timeline panel
            self.eeg_panel.set_processor(self.processor)
            
            # Update analysis panel
            self.analysis_panel.set_analyzer(self.analyzer)
            
            # Set initial channel (first visible channel)
            visible_channels = self.eeg_panel.get_visible_channels()
            if visible_channels:
                initial_channel = visible_channels[0]
                self.analysis_panel.set_channel(initial_channel)
                
            # Force refresh display
            self.eeg_panel.update()
            self.analysis_panel.update()
            
            print("✅ All panels updated successfully")
            self.window_manager.update_status(
                "✅ EEG timeline and band analysis ready!"
            )
            
        except Exception as e:
            error_msg = f"Error updating panels: {str(e)}"
            self.window_manager.update_status(error_msg)
            print(error_msg)
            import traceback
            traceback.print_exc()
            
    def on_timeline_changed(self, position):
        """Handle timeline position changes"""
        if self.analysis_panel and self.processor:
            current_time = self.eeg_panel.get_current_position()
            duration = self.processor.get_duration()
            self.analysis_panel.set_time_window(current_time, duration)
            
    def on_channel_visibility_changed(self, visible_channels):
        """Handle channel visibility changes"""
        if visible_channels and self.analyzer:
            self.analysis_panel.set_channel(visible_channels[0])
            
    def on_frequency_band_changed(self, band_name):
        """Handle frequency band changes"""
        self.window_manager.update_status(
            f"📊 Switched to {band_name} band analysis"
        )
        
    def on_folder_changed(self, folder_path):
        """Handle folder changes"""
        folder_name = os.path.basename(folder_path)
        self.window_manager.update_status(f"📁 Folder changed to: {folder_name}")
        
    def on_sidebar_toggled(self, visible):
        """Handle sidebar visibility changes"""
        self.file_panel.setVisible(visible)
        self.layout_manager.set_sidebar_proportions(visible)
        self.toolbar_manager.update_sidebar_action(visible)
        
    def toggle_sidebar_shortcut(self):
        """Toggle sidebar via keyboard shortcut"""
        self.window_manager.toggle_sidebar()
        
    def closeEvent(self, event):
        """Handle application close"""
        self.window_manager.save_geometry()
        super().closeEvent(event)
