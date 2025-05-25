"""
Main Window for EEG Analysis Application
Fixed plot axes - Zero point anchored, EEG scrollable
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, 
                             QWidget, QListWidget, QListWidgetItem, QPushButton, 
                             QLabel, QComboBox, QSplitter, QMessageBox, QProgressBar,
                             QSlider, QSpinBox)
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
        self.current_time_start = 0  # For EEG scrolling
        self.time_window = 10  # Default 10-second window
        
        self.setWindowTitle("🧠 EEG Analysis - Fixed Axes & Scrollable Timeline")
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
            QComboBox, QSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 8px;
                background: #3c3c3c;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #0078d4;
                width: 18px;
                border-radius: 9px;
                margin-top: -5px;
                margin-bottom: -5px;
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
        """)
        
        self.init_ui()
        self.load_file_list()
        
    def init_ui(self):
        """Initialize the UI with fixed axes"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left: File browser with controls
        self.create_file_panel(main_splitter)
        
        # Right: 3-panel analysis area
        self.create_analysis_area(main_splitter)
        
        main_splitter.setSizes([300, 1200])
        self.statusBar().showMessage("🧠 Ready - Load an EEG file for scrollable timeline analysis")
        
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
        
        # Time window control
        layout.addWidget(QLabel("EEG Window (seconds):"))
        self.time_window_spin = QSpinBox()
        self.time_window_spin.setRange(5, 60)
        self.time_window_spin.setValue(10)
        self.time_window_spin.valueChanged.connect(self.on_time_window_changed)
        layout.addWidget(self.time_window_spin)
        
        # Timeline scroll
        layout.addWidget(QLabel("Timeline Position:"))
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.setValue(0)
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)
        self.timeline_slider.setEnabled(False)
        layout.addWidget(self.timeline_slider)
        
        self.timeline_label = QLabel("0.0s / 0.0s")
        self.timeline_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        layout.addWidget(self.timeline_label)
        
        # Channel selection
        layout.addWidget(QLabel("Analysis Channel:"))
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
        """Create the 3-panel analysis area with fixed axes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Vertical splitter
        v_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(v_splitter)
        
        # TOP PANEL: EEG Signal Display (Scrollable)
        eeg_widget = QWidget()
        eeg_layout = QVBoxLayout(eeg_widget)
        
        eeg_title = QLabel("🧠 EEG Signal Visualization (Scrollable Timeline)")
        eeg_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background: #1e1e2e; border-radius: 4px; color: #ffffff; border: 1px solid #444444;")
        eeg_layout.addWidget(eeg_title)
        
        # EEG plot with fixed axes
        self.eeg_plot = pg.PlotWidget(background='#2b2b2b')
        self.eeg_plot.setLabel('bottom', 'Time (seconds)', color='white', size='12pt')
        self.eeg_plot.setLabel('left', 'Channels', color='white', size='12pt')
        self.eeg_plot.showGrid(True, True, 0.3)
        
        # Configure axes to prevent negative values
        self.eeg_plot.setLimits(xMin=0, yMin=0)  # Prevent scrolling below 0,0
        self.eeg_plot.getViewBox().setRange(xRange=[0, 10], yRange=[0, 25], padding=0)
        
        # Style axes
        self.eeg_plot.getAxis('bottom').setPen(color='white')
        self.eeg_plot.getAxis('left').setPen(color='white')
        self.eeg_plot.getAxis('bottom').setTextPen(color='white')
        self.eeg_plot.getAxis('left').setTextPen(color='white')
        eeg_layout.addWidget(self.eeg_plot)
        
        self.eeg_info = QLabel("Load an EEG file to view scrollable multi-channel signals")
        self.eeg_info.setStyleSheet("padding: 8px; background: #3c3c3c; border-radius: 4px; color: #cccccc; border: 1px solid #555555;")
        eeg_layout.addWidget(self.eeg_info)
        
        v_splitter.addWidget(eeg_widget)
        
        # BOTTOM AREA: Alpha + Spectrum
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        h_splitter = QSplitter(Qt.Horizontal)
        bottom_layout.addWidget(h_splitter)
        
        # BOTTOM-LEFT: Alpha Power (Fixed axes)
        alpha_widget = QWidget()
        alpha_layout = QVBoxLayout(alpha_widget)
        
        alpha_title = QLabel("⚡ Alpha Power (8-13Hz)")
        alpha_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background: #2e1e0f; border-radius: 4px; color: #ff9800; border: 1px solid #ff9800;")
        alpha_layout.addWidget(alpha_title)
        
        self.alpha_plot = pg.PlotWidget(background='#2b2b2b')
        self.alpha_plot.setLabel('bottom', 'Time (seconds)', color='white', size='12pt')
        self.alpha_plot.setLabel('left', 'Alpha Power (μV²)', color='white', size='12pt')
        self.alpha_plot.showGrid(True, True, 0.3)
        
        # Fix alpha plot axes - no negative values
        self.alpha_plot.setLimits(xMin=0, yMin=0)
        
        # Style axes
        self.alpha_plot.getAxis('bottom').setPen(color='white')
        self.alpha_plot.getAxis('left').setPen(color='white')
        self.alpha_plot.getAxis('bottom').setTextPen(color='white')
        self.alpha_plot.getAxis('left').setTextPen(color='white')
        alpha_layout.addWidget(self.alpha_plot)
        
        self.alpha_info = QLabel("Window: 2s, Overlap: 0.5s")
        self.alpha_info.setStyleSheet("padding: 8px; background: #3c3c3c; border-radius: 4px; font-size: 12px; color: #cccccc; border: 1px solid #555555;")
        alpha_layout.addWidget(self.alpha_info)
        
        h_splitter.addWidget(alpha_widget)
        
        # BOTTOM-RIGHT: Frequency Spectrum (Fixed axes)
        spectrum_widget = QWidget()
        spectrum_layout = QVBoxLayout(spectrum_widget)
        
        spectrum_title = QLabel("📊 Power Spectrum")
        spectrum_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background: #1e2a3a; border-radius: 4px; color: #2196f3; border: 1px solid #2196f3;")
        spectrum_layout.addWidget(spectrum_title)
        
        self.spectrum_plot = pg.PlotWidget(background='#2b2b2b')
        self.spectrum_plot.setLabel('bottom', 'Frequency (Hz)', color='white', size='12pt')
        self.spectrum_plot.setLabel('left', 'Power (μV²)', color='white', size='12pt')
        self.spectrum_plot.setLogMode(False, True)
        self.spectrum_plot.showGrid(True, True, 0.3)
        
        # Fix spectrum plot axes - no negative values
        self.spectrum_plot.setLimits(xMin=0, yMin=0.001)  # Min power = 0.001 for log scale
        
        # Style axes
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
        h_splitter.setSizes([600, 600])
        v_splitter.addWidget(bottom_widget)
        v_splitter.setSizes([500, 350])
        
        parent.addWidget(widget)
        
    def load_file_list(self):
        """Load EDF files"""
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
        self.statusBar().showMessage(f"Selected: {file_name}")
        
    def load_selected_file(self):
        """Load and analyze file"""
        item = self.file_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
            
        file_path = item.data(Qt.UserRole)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.load_button.setEnabled(False)
        
        # Start background loading
        self.load_thread = EEGLoadThread(file_path)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.progress.connect(lambda msg: self.statusBar().showMessage(msg))
        self.load_thread.start()
        
    def on_load_finished(self, success, message):
        """Handle loading completion"""
        self.progress_bar.setVisible(False)
        self.load_button.setEnabled(True)
        
        if success:
            self.loader = self.load_thread.loader
            self.processor = self.load_thread.processor
            self.analyzer = self.load_thread.analyzer
            
            # Setup timeline slider
            total_duration = self.processor.get_duration()
            self.timeline_slider.setEnabled(True)
            self.timeline_slider.setRange(0, int(total_duration - self.time_window))
            self.timeline_slider.setValue(0)
            self.current_time_start = 0
            
            # Update channel list
            self.update_channel_list()
            
            # Update all panels
            self.update_all_panels()
            
            self.statusBar().showMessage(f"✅ {message}")
        else:
            QMessageBox.critical(self, "Error", message)
            
    def update_channel_list(self):
        """Update channel dropdown"""
        self.channel_combo.clear()
        if self.processor:
            channels = self.processor.get_channel_names()
            for i, name in enumerate(channels):
                self.channel_combo.addItem(name, i)
                
    def on_time_window_changed(self):
        """Handle time window change"""
        self.time_window = self.time_window_spin.value()
        if self.processor:
            # Update slider range
            total_duration = self.processor.get_duration()
            self.timeline_slider.setRange(0, max(0, int(total_duration - self.time_window)))
            # Update EEG display
            self.update_eeg_panel()
            
    def on_timeline_changed(self):
        """Handle timeline scroll"""
        if self.processor:
            self.current_time_start = self.timeline_slider.value()
            self.update_eeg_panel()
            
            # Update timeline label
            total_duration = self.processor.get_duration()
            current_end = min(self.current_time_start + self.time_window, total_duration)
            self.timeline_label.setText(f"{self.current_time_start:.1f}s / {total_duration:.1f}s")
            
    def update_all_panels(self):
        """Update all panels"""
        if not self.processor or not self.analyzer:
            return
            
        try:
            self.update_eeg_panel()
            self.update_analysis_plots()
            
            # Update file info
            info = self.loader.get_file_info()
            info_text = f"📄 {info['filename']} | 📊 {info['n_channels']} channels | ⚡ {info['sampling_rate']} Hz | ⏱️ {info['duration']:.1f}s"
            self.eeg_info.setText(info_text)
            
        except Exception as e:
            self.statusBar().showMessage(f"Display error: {e}")
            
    def update_eeg_panel(self):
        """Update EEG display with scrollable timeline"""
        if not self.processor:
            return
            
        try:
            # Get data for current time window
            start_time = self.current_time_start
            end_time = start_time + self.time_window
            
            data, times = self.processor.get_filtered_data(start_time=start_time, stop_time=end_time)
            if data is None:
                return
                
            self.eeg_plot.clear()
            data_uv = data * 1e6  # Convert to microvolts
            
            # Plot channels with fixed positioning (no negative Y values)
            colors = ['#00bfff', '#ff4444', '#44ff44', '#ff8800', '#8844ff', '#ff44ff', '#ffff44', '#88ffff']
            channel_names = self.processor.get_channel_names()
            
            for i in range(min(8, data.shape[0])):
                # Normalize and position channels starting from Y=0
                normalized = (data_uv[i] / 200) + (i + 1) * 3  # Start from Y=3, not Y=0
                
                # Plot signal
                color = colors[i % len(colors)]
                self.eeg_plot.plot(times, normalized, pen=pg.mkPen(color=color, width=1))
                
                # Add channel label
                text = pg.TextItem(channel_names[i], color=color, anchor=(0, 0.5))
                self.eeg_plot.addItem(text)
                text.setPos(times[0], (i + 1) * 3)
                
            # Set plot ranges - fixed at 0,0 minimum
            self.eeg_plot.setXRange(times[0], times[-1])
            self.eeg_plot.setYRange(0, min(8, data.shape[0]) * 3 + 3)
            
        except Exception as e:
            print(f"EEG panel error: {e}")
            
    def update_analysis_plots(self):
        """Update alpha and spectrum with fixed axes"""
        if not self.analyzer:
            return
            
        try:
            channel_idx = self.channel_combo.currentData() or 0
                
            # Alpha Power Plot - fixed axes (no negative values)
            times, alpha_powers = self.analyzer.calculate_alpha_power_sliding(channel_idx)
            if times is not None and alpha_powers is not None:
                self.alpha_plot.clear()
                self.alpha_plot.plot(times, alpha_powers, 
                                   pen=pg.mkPen(color='#ff9800', width=2),
                                   symbol='o', symbolSize=4, symbolBrush='#ff9800')
                
                # Set range starting from 0,0
                self.alpha_plot.setXRange(0, times[-1])
                self.alpha_plot.setYRange(0, np.max(alpha_powers) * 1.1)
                
                # Update stats
                stats = self.analyzer.get_alpha_statistics(channel_idx)
                if stats:
                    alpha_text = f"Mean: {stats['mean_alpha_power']:.2f} μV² | Max: {stats['max_alpha_power']:.2f} μV² | {stats['n_windows']} windows"
                    self.alpha_info.setText(alpha_text)
                    
            # Spectrum Plot - fixed axes
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
                
                # Set range starting from 0,0
                self.spectrum_plot.setXRange(0, 40)
                
                # Update band info
                bands_power = self.analyzer.get_frequency_bands_power(channel_idx)
                if bands_power:
                    total_power = sum(bands_power.values())
                    alpha_pct = (bands_power['Alpha (8-13 Hz)'] / total_power) * 100 if total_power > 0 else 0
                    spectrum_text = f"Alpha: {alpha_pct:.1f}% | Total: {total_power:.1f} μV²"
                    self.spectrum_info.setText(spectrum_text)
                    
        except Exception as e:
            print(f"Analysis plots error: {e}")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
