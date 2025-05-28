"""
File Panel Module
Enhanced file browser with folder selection and auto-loading
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog,
                             QComboBox, QCheckBox, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from utils.settings import AppSettings
from utils.ui_helpers import create_styled_button, create_collapsible_button


class FilePanel(QWidget):
    """Enhanced file browser panel with auto-loading and folder selection"""
    
    # Signals
    file_selected = pyqtSignal(str)  # Emitted when file is auto-loaded
    folder_changed = pyqtSignal(str)  # Emitted when folder changes
    
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.settings = settings
        self.current_folder = settings.get('eeg_data_folder')
        
        self.init_ui()
        self.load_file_list()
        
    def init_ui(self):
        """Initialize the file panel UI"""
        layout = QVBoxLayout(self)
        
        # Title with collapse button
        title_layout = QHBoxLayout()
        self.title_label = QLabel("📁 EEG Files")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        title_layout.addWidget(self.title_label)
        layout.addLayout(title_layout)
        
        # Folder selection
        folder_group = QGroupBox("Data Folder")
        folder_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        folder_layout = QVBoxLayout(folder_group)
        
        # Current folder display
        self.folder_label = QLabel(self.current_folder)
        self.folder_label.setStyleSheet("color: #cccccc; font-size: 10px; padding: 4px;")
        self.folder_label.setWordWrap(True)
        folder_layout.addWidget(self.folder_label)
        
        # Folder controls
        folder_controls = QHBoxLayout()
        
        self.browse_button = create_styled_button("📂 Browse", "secondary")
        self.browse_button.clicked.connect(self.browse_folder)
        folder_controls.addWidget(self.browse_button)
        
        # Recent folders dropdown
        self.recent_combo = QComboBox()
        self.recent_combo.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
            }
        """)
        self.recent_combo.currentTextChanged.connect(self.on_recent_folder_selected)
        self.update_recent_folders()
        folder_controls.addWidget(self.recent_combo)
        
        folder_layout.addLayout(folder_controls)
        layout.addWidget(folder_group)
        
        # File list
        file_group = QGroupBox("EDF Files (Click to Auto-Load)")
        file_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        file_layout = QVBoxLayout(file_group)
        
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
            }
        """)
        self.file_list.itemClicked.connect(self.on_file_clicked)
        file_layout.addWidget(self.file_list)
        
        # File info
        self.file_info_label = QLabel("Click any file to load automatically")
        self.file_info_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 4px;")
        file_layout.addWidget(self.file_info_label)
        
        layout.addWidget(file_group)
        
        # Filter info
        filter_info = QLabel("🔧 Filter: 0.1Hz - 40Hz")
        filter_info.setStyleSheet("background: #1e3a1e; padding: 8px; border-radius: 4px; color: #4caf50; border: 1px solid #4caf50; margin-top: 10px;")
        layout.addWidget(filter_info)
        
    def browse_folder(self):
        """Open folder browser dialog"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select EEG Data Folder (EDF or TXT)", 
            self.current_folder
        )
        
        if folder:
            self.set_folder(folder)
            
    def set_folder(self, folder_path: str):
        """Set the current EEG data folder"""
        if os.path.exists(folder_path):
            self.current_folder = folder_path
            self.folder_label.setText(folder_path)
            self.settings.set('eeg_data_folder', folder_path)
            self.settings.add_recent_folder(folder_path)
            self.update_recent_folders()
            self.load_file_list()
            self.folder_changed.emit(folder_path)
            
    def update_recent_folders(self):
        """Update the recent folders dropdown"""
        self.recent_combo.clear()
        self.recent_combo.addItem("Recent Folders...")
        
        for folder in self.settings.get_recent_folders():
            if os.path.exists(folder):
                folder_name = os.path.basename(folder) or folder
                self.recent_combo.addItem(folder_name, folder)
                
    def on_recent_folder_selected(self, text):
        """Handle recent folder selection"""
        if text != "Recent Folders...":
            data = self.recent_combo.currentData()
            if data:
                self.set_folder(data)
                
    def load_file_list(self):
        """Load EDF files from current folder"""
        self.file_list.clear()
        
        if not os.path.exists(self.current_folder):
            self.file_list.addItem("❌ Folder not found")
            return
            
        try:
            files = [f for f in os.listdir(self.current_folder) 
                    if f.lower().endswith(('.edf', '.txt'))]
            
            if not files:
                self.file_list.addItem("❌ No EEG files found (EDF or TXT)")
                return
                
            for file in sorted(files):
                # Determine file icon based on extension
                file_icon = "📊" if file.lower().endswith(".txt") else "📄"
                item = QListWidgetItem(f"{file_icon} {file}")
                item.setData(Qt.UserRole, os.path.join(self.current_folder, file))
                
                # Add file size info
                file_path = os.path.join(self.current_folder, file)
                try:
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    item.setToolTip(f"File: {file}\nSize: {size_mb:.1f} MB\nClick to auto-load")
                except:
                    pass
                    
                self.file_list.addItem(item)
                
            self.file_info_label.setText(f"Found {len(files)} EEG files (EDF/TXT) - Click any to auto-load")
            
        except Exception as e:
            self.file_list.addItem(f"❌ Error reading folder: {str(e)}")
            
    def on_file_clicked(self, item):
        """Handle file click - auto-load the file"""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            file_name = item.text().replace("📄 ", "")
            self.file_info_label.setText(f"🔄 Auto-loading: {file_name}")
            self.file_selected.emit(file_path)
            
    def refresh_file_list(self):
        """Refresh the file list"""
        self.load_file_list()
        
    def get_current_folder(self) -> str:
        """Get the current folder path"""
        return self.current_folder
