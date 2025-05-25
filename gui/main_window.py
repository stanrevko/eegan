"""
Main Window for EEG Analysis Application
Quick minimal GUI implementation
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, 
                             QWidget, QListWidget, QListWidgetItem, QPushButton, 
                             QLabel, QComboBox, QSplitter, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pyqtgraph as pg
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from eeg.loader import EEGLoader
from eeg.processor import EEGProcessor


class EEGLoadThread(QThread):
    """Thread for loading EEG files without blocking GUI"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            self.progress.emit("Loading EEG file...")
            loader = EEGLoader()
            
            if loader.load_edf(self.file_path):
                self.progress.emit("Applying filter...")
                processor = EEGProcessor()
                processor.set_raw_data(loader.raw)
                processor.apply_bandpass_filter(l_freq=0.1, h_freq=40.0)
                
                # Store in parent thread
                self.loader = loader
                self.processor = processor
                self.finished.emit(True, "File loaded successfully!")
            else:
                self.finished.emit(False, "Failed to load file")
                
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loader = None
        self.processor = None
        self.current_data = None
        self.current_times = None
        
        self.setWindowTitle("EEG Analysis Application - Minimal GUI")
        self.setGeometry(100, 100, 1400, 800)
        
        self.init_ui()
        self.load_file_list()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - File browser
        self.create_file_panel(splitter)
        
        # Right panel - EEG visualization
        self.create_plot_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([300, 1000])
        
        # Status bar
        self.statusBar().showMessage("Ready - Select an EEG file to begin")
        
    def create_file_panel(self, parent):
        """Create file browser panel"""
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        
        # Title
        title_label = QLabel("📁 EEG Files")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        file_layout.addWidget(title_label)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_selected)
        file_layout.addWidget(self.file_list)
        
        # Controls
        controls_layout = QVBoxLayout()
        
        # Filter info
        filter_label = QLabel("🔧 Filter: 0.1Hz - 40Hz")
        filter_label.setStyleSheet("background: #e8f5e8; padding: 8px; border-radius: 4px; color: #2e7d32;")
        controls_layout.addWidget(filter_label)
        
        # Scale control
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale:"))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["50 μV", "100 μV", "200 μV", "500 μV"])
        self.scale_combo.setCurrentText("200 μV")
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(self.scale_combo)
        controls_layout.addLayout(scale_layout)
        
        # Time window control
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time Window:"))
        self.time_combo = QComboBox()
        self.time_combo.addItems(["5 sec", "10 sec", "30 sec", "60 sec"])
        self.time_combo.setCurrentText("10 sec")
        self.time_combo.currentTextChanged.connect(self.on_time_window_changed)
        time_layout.addWidget(self.time_combo)
        controls_layout.addLayout(time_layout)
        
        # Load button
        self.load_button = QPushButton("📂 Load Selected File")
        self.load_button.clicked.connect(self.load_selected_file)
        self.load_button.setStyleSheet("QPushButton { background: #1976d2; color: white; padding: 10px; border-radius: 4px; font-weight: bold; }")
        controls_layout.addWidget(self.load_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        file_layout.addLayout(controls_layout)
        parent.addWidget(file_widget)
        
    def create_plot_panel(self, parent):
        """Create EEG plotting panel"""
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        
        # Title
        title_label = QLabel("🧠 EEG Signal Visualization")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        plot_layout.addWidget(title_label)
        
        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('white')
        self.plot_widget.setLabel('left', 'Channels')
        self.plot_widget.setLabel('bottom', 'Time (seconds)')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.plot_widget)
        
        # Info panel
        self.info_label = QLabel("Select and load an EEG file to view signals")
        self.info_label.setStyleSheet("padding: 10px; background: #f5f5f5; border-radius: 4px;")
        plot_layout.addWidget(self.info_label)
        
        parent.addWidget(plot_widget)
        
    def load_file_list(self):
        """Load EDF files into the file list"""
        eeg_data_path = "/Users/stanrevko/projects/eegan/eeg_data"
        
        if not os.path.exists(eeg_data_path):
            self.file_list.addItem("❌ EEG data directory not found")
            return
            
        edf_files = [f for f in os.listdir(eeg_data_path) if f.endswith('.edf')]
        
        if not edf_files:
            self.file_list.addItem("❌ No EDF files found")
            return
            
        for file in sorted(edf_files):
            item = QListWidgetItem(f"📄 {file}")
            item.setData(Qt.UserRole, os.path.join(eeg_data_path, file))
            self.file_list.addItem(item)
            
    def on_file_selected(self, item):
        """Handle file selection"""
        file_name = item.text().replace("📄 ", "")
        self.statusBar().showMessage(f"Selected: {file_name}")
        
    def load_selected_file(self):
        """Load the selected EEG file"""
        current_item = self.file_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
            
        file_path = current_item.data(Qt.UserRole)
        if not file_path:
            return
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.load_button.setEnabled(False)
        
        # Start loading in background thread
        self.load_thread = EEGLoadThread(file_path)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.progress.connect(self.on_load_progress)
        self.load_thread.start()
        
    def on_load_progress(self, message):
        """Update progress message"""
        self.statusBar().showMessage(message)
        
    def on_load_finished(self, success, message):
        """Handle loading completion"""
        self.progress_bar.setVisible(False)
        self.load_button.setEnabled(True)
        
        if success:
            # Get data from thread
            self.loader = self.load_thread.loader
            self.processor = self.load_thread.processor
            
            # Update display
            self.update_eeg_plot()
            self.update_info_panel()
            self.statusBar().showMessage(f"✅ {message}")
        else:
            QMessageBox.critical(self, "Error", message)
            self.statusBar().showMessage(f"❌ {message}")
            
    def update_eeg_plot(self):
        """Update the EEG plot with current data"""
        if not self.processor:
            return
            
        try:
            # Get time window
            time_window = float(self.time_combo.currentText().split()[0])
            
            # Get filtered data for the time window
            data, times = self.processor.get_filtered_data(start_time=0, stop_time=time_window)
            
            if data is None:
                return
                
            self.current_data = data
            self.current_times = times
            
            # Clear previous plots
            self.plot_widget.clear()
            
            # Get scale value
            scale_text = self.scale_combo.currentText()
            scale_value = float(scale_text.split()[0])
            
            # Convert data to microvolts
            data_uv = data * 1e6
            
            # Plot channels with vertical spacing
            channel_names = self.processor.get_channel_names()
            n_channels = min(len(channel_names), data.shape[0])
            
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
            
            for i in range(min(10, n_channels)):  # Show first 10 channels
                # Normalize data to scale and add vertical offset
                normalized_data = (data_uv[i] / scale_value) + i * 2
                
                # Plot the signal
                color = colors[i % len(colors)]
                self.plot_widget.plot(times, normalized_data, pen=pg.mkPen(color=color, width=1), name=channel_names[i])
                
                # Add channel label
                self.plot_widget.addItem(pg.TextItem(channel_names[i], color=color, anchor=(0, 0.5)), pos=(times[0], i * 2))
            
            # Set plot properties
            self.plot_widget.setYRange(-1, n_channels * 2 + 1)
            self.plot_widget.setXRange(times[0], times[-1])
            
        except Exception as e:
            self.statusBar().showMessage(f"Error plotting: {str(e)}")
            
    def update_info_panel(self):
        """Update the info panel with file details"""
        if not self.loader:
            return
            
        info = self.loader.get_file_info()
        if info:
            info_text = f"""
            📄 File: {info['filename']}
            📊 Channels: {info['n_channels']}
            ⚡ Sampling Rate: {info['sampling_rate']} Hz
            ⏱️ Duration: {info['duration']:.1f} seconds
            🔧 Filter: 0.1Hz - 40Hz applied
            """
            self.info_label.setText(info_text)
            
    def on_scale_changed(self):
        """Handle scale change"""
        if self.current_data is not None:
            self.update_eeg_plot()
            
    def on_time_window_changed(self):
        """Handle time window change"""
        if self.current_data is not None:
            self.update_eeg_plot()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
