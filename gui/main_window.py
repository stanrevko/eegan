"""
Main Window for EEG Analysis Application
Complete 3-panel layout with dark mode friendly styling
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
from eeg.analyzer import EEGAnalyzer


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
                self.progress.emit("Applying 0.1-40Hz filter...")
                processor = EEGProcessor()
                processor.set_raw_data(loader.raw)
                processor.apply_bandpass_filter(l_freq=0.1, h_freq=40.0)
                
                self.progress.emit("Calculating alpha power and spectrum...")
                analyzer = EEGAnalyzer()
                analyzer.set_processor(processor)
                
                # Store results
                self.loader = loader
                self.processor = processor
                self.analyzer = analyzer
                self.finished.emit(True, "Complete analysis ready!")
            else:
                self.finished.emit(False, "Failed to load file")
                
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loader = None
        self.processor = None
        self.analyzer = None
        
        self.setWindowTitle("🧠 EEG Analysis - Complete Suite (3-Panel Layout)")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Set dark mode styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border: none;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QProgressBar {
                border: 1px solid #555555;
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        
        self.init_ui()
        self.load_file_list()
        
    def init_ui(self):
        """Initialize the 3-panel user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left: File browser
        self.create_file_panel(main_splitter)
        
        # Right: 3-panel analysis area
        self.create_analysis_area(main_splitter)
        
        main_splitter.setSizes([300, 1200])
        self.statusBar().showMessage("🧠 Ready - Load an EEG file to see complete analysis")
        
    def create_file_panel(self, parent):
        """Create file browser and controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("📁 EEG Files")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; color: #ffffff;")
        layout.addWidget(title)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_selected)
        layout.addWidget(self.file_list)
        
        # Filter info
        filter_info = QLabel("🔧 Filter: 0.1Hz - 40Hz")
        filter_info.setStyleSheet("background: #1e3a1e; padding: 8px; border-radius: 4px; color: #4caf50; border: 1px solid #4caf50;")
        layout.addWidget(filter_info)
        
        # Alpha info
        alpha_info = QLabel("⚡ Alpha: 8-13Hz (2s windows)")
        alpha_info.setStyleSheet("background: #2e1e0f; padding: 8px; border-radius: 4px; color: #ff9800; border: 1px solid #ff9800;")
        layout.addWidget(alpha_info)
        
        # Channel selection
        channel_label = QLabel("Analysis Channel:")
        channel_label.setStyleSheet("color: #ffffff; margin-top: 10px;")
        layout.addWidget(channel_label)
        
        self.channel_combo = QComboBox()
        self.channel_combo.currentIndexChanged.connect(self.update_analysis_plots)
        layout.addWidget(self.channel_combo)
        
        # Load button
        self.load_button = QPushButton("📂 Load & Analyze File")
        self.load_button.clicked.connect(self.load_selected_file)
        layout.addWidget(self.load_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        parent.addWidget(widget)
        
    def create_analysis_area(self, parent):
        """Create the 3-panel analysis area"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Vertical splitter: EEG signals (top) vs Analysis panels (bottom)
        v_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(v_splitter)
        
        # TOP PANEL: EEG Signal Display
        eeg_widget = QWidget()
        eeg_layout = QVBoxLayout(eeg_widget)
        
        eeg_title = QLabel("🧠 EEG Signal Visualization (Filtered 0.1-40Hz)")
        eeg_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background: #1e1e2e; border-radius: 4px; color: #ffffff; border: 1px solid #444444;")
        eeg_layout.addWidget(eeg_title)
        
        self.eeg_plot = pg.PlotWidget(background='#2b2b2b')
        self.eeg_plot.setLabel('bottom', 'Time (seconds)', color='white', size='12pt')
        self.eeg_plot.setLabel('left', 'Channels', color='white', size='12pt')
        self.eeg_plot.showGrid(True, True, 0.3)
        self.eeg_plot.getAxis('bottom').setPen(color='white')
        self.eeg_plot.getAxis('left').setPen(color='white')
        self.eeg_plot.getAxis('bottom').setTextPen(color='white')
        self.eeg_plot.getAxis('left').setTextPen(color='white')
        eeg_layout.addWidget(self.eeg_plot)
        
        self.eeg_info = QLabel("Load an EEG file to view multi-channel signals")
        self.eeg_info.setStyleSheet("padding: 8px; background: #3c3c3c; border-radius: 4px; color: #cccccc; border: 1px solid #555555;")
        eeg_layout.addWidget(self.eeg_info)
        
        v_splitter.addWidget(eeg_widget)
        
        # BOTTOM AREA: Alpha Power (left) + Frequency Spectrum (right)
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        h_splitter = QSplitter(Qt.Horizontal)
        bottom_layout.addWidget(h_splitter)
        
        # BOTTOM-LEFT: Alpha Power Analysis
        alpha_widget = QWidget()
        alpha_layout = QVBoxLayout(alpha_widget)
        
        alpha_title = QLabel("⚡ Alpha Power (8-13Hz)")
        alpha_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background: #2e1e0f; border-radius: 4px; color: #ff9800; border: 1px solid #ff9800;")
        alpha_layout.addWidget(alpha_title)
        
        self.alpha_plot = pg.PlotWidget(background='#2b2b2b')
        self.alpha_plot.setLabel('bottom', 'Time (seconds)', color='white', size='12pt')
        self.alpha_plot.setLabel('left', 'Alpha Power (μV²)', color='white', size='12pt')
        self.alpha_plot.showGrid(True, True, 0.3)
        self.alpha_plot.getAxis('bottom').setPen(color='white')
        self.alpha_plot.getAxis('left').setPen(color='white')
        self.alpha_plot.getAxis('bottom').setTextPen(color='white')
        self.alpha_plot.getAxis('left').setTextPen(color='white')
        alpha_layout.addWidget(self.alpha_plot)
        
        self.alpha_info = QLabel("Window: 2s, Overlap: 0.5s")
        self.alpha_info.setStyleSheet("padding: 8px; background: #3c3c3c; border-radius: 4px; font-size: 12px; color: #cccccc; border: 1px solid #555555;")
        alpha_layout.addWidget(self.alpha_info)
        
        h_splitter.addWidget(alpha_widget)
        
        # BOTTOM-RIGHT: Frequency Spectrum
        spectrum_widget = QWidget()
        spectrum_layout = QVBoxLayout(spectrum_widget)
        
        spectrum_title = QLabel("📊 Power Spectrum")
        spectrum_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background: #1e2a3a; border-radius: 4px; color: #2196f3; border: 1px solid #2196f3;")
        spectrum_layout.addWidget(spectrum_title)
        
        self.spectrum_plot = pg.PlotWidget(background='#2b2b2b')
        self.spectrum_plot.setLabel('bottom', 'Frequency (Hz)', color='white', size='12pt')
        self.spectrum_plot.setLabel('left', 'Power (μV²)', color='white', size='12pt')
        self.spectrum_plot.setLogMode(False, True)  # Log scale for power
        self.spectrum_plot.showGrid(True, True, 0.3)
        self.spectrum_plot.getAxis('bottom').setPen(color='white')
        self.spectrum_plot.getAxis('left').setPen(color='white')
        self.spectrum_plot.getAxis('bottom').setTextPen(color='white')
        self.spectrum_plot.getAxis('left').setTextPen(color='white')
        spectrum_layout.addWidget(self.spectrum_plot)
        
        self.spectrum_info = QLabel("Full signal power analysis")
        self.spectrum_info.setStyleSheet("padding: 8px; background: #3c3c3c; border-radius: 4px; font-size: 12px; color: #cccccc; border: 1px solid #555555;")
        spectrum_layout.addWidget(self.spectrum_info)
        
        h_splitter.addWidget(spectrum_widget)
        
        # Set splitter proportions
        h_splitter.setSizes([600, 600])  # Equal split for alpha and spectrum
        v_splitter.addWidget(bottom_widget)
        v_splitter.setSizes([500, 350])  # More space for EEG signals
        
        parent.addWidget(widget)
        
    def load_file_list(self):
        """Load EDF files into the file browser"""
        eeg_path = "/Users/stanrevko/projects/eegan/eeg_data"
        
        if os.path.exists(eeg_path):
            files = [f for f in os.listdir(eeg_path) if f.endswith('.edf')]
            for file in sorted(files):
                item = QListWidgetItem(f"📄 {file}")
                item.setData(Qt.UserRole, os.path.join(eeg_path, file))
                self.file_list.addItem(item)
                
    def on_file_selected(self, item):
        """Handle file selection"""
        file_name = item.text().replace("📄 ", "")
        self.statusBar().showMessage(f"Selected: {file_name} - Click 'Load & Analyze' to process")
        
    def load_selected_file(self):
        """Load and analyze the selected EEG file"""
        item = self.file_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
            
        file_path = item.data(Qt.UserRole)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.load_button.setEnabled(False)
        
        # Start background loading
        self.load_thread = EEGLoadThread(file_path)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.progress.connect(lambda msg: self.statusBar().showMessage(msg))
        self.load_thread.start()
        
    def on_load_finished(self, success, message):
        """Handle loading and analysis completion"""
        self.progress_bar.setVisible(False)
        self.load_button.setEnabled(True)
        
        if success:
            # Store analysis results
            self.loader = self.load_thread.loader
            self.processor = self.load_thread.processor
            self.analyzer = self.load_thread.analyzer
            
            # Update channel selection
            self.update_channel_list()
            
            # Update all 3 panels
            self.update_all_panels()
            
            self.statusBar().showMessage(f"✅ {message}")
        else:
            QMessageBox.critical(self, "Error", message)
            self.statusBar().showMessage(f"❌ {message}")
            
    def update_channel_list(self):
        """Update the channel selection dropdown"""
        self.channel_combo.clear()
        if self.processor:
            channels = self.processor.get_channel_names()
            for i, name in enumerate(channels):
                self.channel_combo.addItem(name, i)
                
    def update_all_panels(self):
        """Update all 3 visualization panels"""
        if not self.processor or not self.analyzer:
            return
            
        try:
            # Update EEG signals (top panel)
            self.update_eeg_panel()
            
            # Update analysis panels (bottom)
            self.update_analysis_plots()
            
            # Update file info
            info = self.loader.get_file_info()
            info_text = f"📄 {info['filename']} | 📊 {info['n_channels']} channels | ⚡ {info['sampling_rate']} Hz | ⏱️ {info['duration']:.1f}s"
            self.eeg_info.setText(info_text)
            
        except Exception as e:
            self.statusBar().showMessage(f"Display error: {e}")
            
    def update_eeg_panel(self):
        """Update the EEG signal display (top panel)"""
        try:
            # Get 10 seconds of filtered data
            data, times = self.processor.get_filtered_data(start_time=0, stop_time=10)
            if data is None:
                return
                
            self.eeg_plot.clear()
            data_uv = data * 1e6  # Convert to microvolts
            
            # Plot first 8 channels with vertical spacing
            colors = ['#00bfff', '#ff4444', '#44ff44', '#ff8800', '#8844ff', '#ff44ff', '#ffff44', '#88ffff']
            channel_names = self.processor.get_channel_names()
            
            for i in range(min(8, data.shape[0])):
                # Normalize to 200μV scale and add vertical offset
                normalized = (data_uv[i] / 200) + i * 3
                
                # Plot signal
                color = colors[i % len(colors)]
                self.eeg_plot.plot(times, normalized, pen=pg.mkPen(color=color, width=1))
                
                # Add channel label
                text = pg.TextItem(channel_names[i], color=color, anchor=(0, 0.5))
                self.eeg_plot.addItem(text)
                text.setPos(times[0], i * 3)
                
            # Set plot ranges
            self.eeg_plot.setXRange(times[0], times[-1])
            self.eeg_plot.setYRange(-1, min(8, data.shape[0]) * 3)
            
        except Exception as e:
            print(f"EEG panel error: {e}")
            
    def update_analysis_plots(self):
        """Update alpha power and frequency spectrum (bottom panels)"""
        if not self.analyzer:
            return
            
        try:
            # Get selected channel
            channel_idx = self.channel_combo.currentData()
            if channel_idx is None:
                channel_idx = 0
                
            # Update Alpha Power Plot (bottom-left)
            times, alpha_powers = self.analyzer.calculate_alpha_power_sliding(channel_idx)
            if times is not None and alpha_powers is not None:
                self.alpha_plot.clear()
                self.alpha_plot.plot(times, alpha_powers, 
                                   pen=pg.mkPen(color='#ff9800', width=2),
                                   symbol='o', symbolSize=4, symbolBrush='#ff9800')
                
                self.alpha_plot.setXRange(times[0], times[-1])
                self.alpha_plot.setYRange(np.min(alpha_powers) * 0.9, np.max(alpha_powers) * 1.1)
                
                # Update alpha statistics
                stats = self.analyzer.get_alpha_statistics(channel_idx)
                if stats:
                    alpha_text = f"Mean: {stats['mean_alpha_power']:.2f} μV² | Std: {stats['std_alpha_power']:.2f} μV² | {stats['n_windows']} windows"
                    self.alpha_info.setText(alpha_text)
                    
            # Update Frequency Spectrum Plot (bottom-right)
            freqs, psd = self.analyzer.calculate_frequency_spectrum(channel_idx)
            if freqs is not None and psd is not None:
                self.spectrum_plot.clear()
                self.spectrum_plot.plot(freqs, psd, pen=pg.mkPen(color='#2196f3', width=2))
                
                # Add frequency band markers
                bands = [
                    (0.5, 4, 'Delta', '#ff4444'),
                    (4, 8, 'Theta', '#44ff44'), 
                    (8, 13, 'Alpha', '#ff9800'),
                    (13, 30, 'Beta', '#8844ff')
                ]
                
                for low, high, name, color in bands:
                    if low >= freqs[0] and low <= freqs[-1]:
                        line = pg.InfiniteLine(pos=low, angle=90, 
                                             pen=pg.mkPen(color=color, style=pg.QtCore.Qt.DashLine, width=2))
                        self.spectrum_plot.addItem(line)
                        
                    if high >= freqs[0] and high <= freqs[-1]:
                        line = pg.InfiniteLine(pos=high, angle=90, 
                                             pen=pg.mkPen(color=color, style=pg.QtCore.Qt.DashLine, width=2))
                        self.spectrum_plot.addItem(line)
                
                self.spectrum_plot.setXRange(0.5, 40)
                
                # Update frequency band info
                bands_power = self.analyzer.get_frequency_bands_power(channel_idx)
                if bands_power:
                    total_power = sum(bands_power.values())
                    alpha_pct = (bands_power['Alpha (8-13 Hz)'] / total_power) * 100 if total_power > 0 else 0
                    beta_pct = (bands_power['Beta (13-30 Hz)'] / total_power) * 100 if total_power > 0 else 0
                    spectrum_text = f"Alpha: {alpha_pct:.1f}% | Beta: {beta_pct:.1f}% | Total: {total_power:.1f} μV²"
                    self.spectrum_info.setText(spectrum_text)
                    
        except Exception as e:
            print(f"Analysis plots error: {e}")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern appearance
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
