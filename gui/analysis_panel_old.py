"""
Analysis Panel Module - Synced with EEG timeline
Configurable frequency band analysis synchronized with EEG visualization
"""

import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg
from eeg.frequency_bands import FrequencyBands
from utils.ui_helpers import setup_dark_plot


class AnalysisPanel(QWidget):
    """Configurable frequency band analysis panel synced with EEG timeline"""
    
    # Signals
    band_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.frequency_bands = FrequencyBands()
        self.current_channel = 0
        self.current_time_start = 0
        self.current_duration = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the analysis panel UI"""
        layout = QVBoxLayout(self)
        
        # Header with band selection
        header_layout = QHBoxLayout()
        
        # Title
        self.title_label = QLabel("⚡ Alpha Power (8-13Hz)")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ff9800;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Frequency band selector
        band_label = QLabel("Band:")
        band_label.setStyleSheet("color: #ffffff; font-weight: bold; margin-right: 5px;")
        header_layout.addWidget(band_label)
        
        self.band_combo = QComboBox()
        self.band_combo.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px 8px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        
        # Populate frequency bands
        for band_name in self.frequency_bands.get_available_bands():
            self.band_combo.addItem(band_name)
            
        self.band_combo.setCurrentText(self.frequency_bands.get_active_band())
        self.band_combo.currentTextChanged.connect(self.on_band_changed)
        header_layout.addWidget(self.band_combo)
        
        layout.addLayout(header_layout)
        
        # Analysis plot
        self.analysis_plot = pg.PlotWidget(background='#2b2b2b')
        setup_dark_plot(self.analysis_plot, 'Time (seconds)', 'Power (μV²)')
        
        # Configure plot for analysis data - no negative values, sync with EEG timeline
        self.analysis_plot.setLimits(xMin=0, yMin=0)
        
        layout.addWidget(self.analysis_plot)
        
        # Info and statistics
        self.create_info_panel(layout)
        
    def create_info_panel(self, parent_layout):
        """Create information and statistics panel"""
        info_group = QGroupBox("Band Analysis Statistics")
        info_group.setStyleSheet("""
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
        
        info_layout = QVBoxLayout(info_group)
        
        # Analysis parameters
        self.params_label = QLabel("Window: 2s, Overlap: 0.5s | Time frame: Full recording")
        self.params_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 4px;")
        info_layout.addWidget(self.params_label)
        
        # Statistics
        self.stats_label = QLabel("Load file to see analysis statistics")
        self.stats_label.setStyleSheet("color: #cccccc; font-size: 12px; padding: 4px;")
        info_layout.addWidget(self.stats_label)
        
        # Band info
        self.band_info_label = QLabel("Alpha band: 8.0 - 13.0 Hz")
        self.band_info_label.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 11px; padding: 4px;")
        info_layout.addWidget(self.band_info_label)
        
        parent_layout.addWidget(info_group)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        if analyzer and analyzer.processor:
            self.current_duration = analyzer.processor.get_duration()
            self.update_params_label()
        self.update_analysis()
        
    def set_channel(self, channel_idx: int):
        """Set the channel for analysis"""
        self.current_channel = channel_idx
        self.update_analysis()
        
    def set_time_window(self, start_time: float, total_duration: float):
        """Set the time window for analysis (synced with EEG timeline)"""
        self.current_time_start = start_time
        self.current_duration = total_duration
        self.update_params_label()
        
    def update_params_label(self):
        """Update the parameters label with current time frame"""
        if self.current_duration > 0:
            self.params_label.setText(f"Window: 2s, Overlap: 0.5s | Time frame: 0 - {self.current_duration:.1f}s (Full recording)")
        
    def on_band_changed(self, band_name: str):
        """Handle frequency band change"""
        self.frequency_bands.set_active_band(band_name)
        
        # Update title and styling
        low_freq, high_freq, color = self.frequency_bands.get_band_info(band_name)
        self.title_label.setText(f"⚡ {band_name} Power ({low_freq}-{high_freq}Hz)")
        self.title_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
        
        # Update band info
        self.band_info_label.setText(f"{band_name} band: {low_freq} - {high_freq} Hz")
        self.band_info_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px; padding: 4px;")
        
        # Update analysis
        self.update_analysis()
        self.band_changed.emit(band_name)
        
    def update_analysis(self):
        """Update the frequency band analysis for full recording"""
        if not self.analyzer:
            self.analysis_plot.clear()
            return
            
        try:
            active_band = self.frequency_bands.get_active_band()
            low_freq, high_freq, color = self.frequency_bands.get_band_info(active_band)
            
            # Calculate power for the selected frequency band across full recording
            times, powers = self.calculate_band_power(low_freq, high_freq)
            
            if times is not None and powers is not None:
                # Clear and plot
                self.analysis_plot.clear()
                self.analysis_plot.plot(times, powers,
                                      pen=pg.mkPen(color=color, width=2),
                                      symbol='o', symbolSize=3, symbolBrush=color)
                
                # Set plot ranges to match EEG timeline (0 to recording duration)
                if self.current_duration > 0:
                    self.analysis_plot.setXRange(0, self.current_duration)
                    # Set plot limits to match recording duration
                    self.analysis_plot.setLimits(xMin=0, xMax=self.current_duration, yMin=0)
                else:
                    self.analysis_plot.setXRange(0, times[-1] if len(times) > 0 else 10)
                    
                self.analysis_plot.setYRange(0, np.max(powers) * 1.1 if len(powers) > 0 else 1)
                
                # Update statistics
                self.update_statistics(times, powers, active_band)
            else:
                self.stats_label.setText("Error calculating band power")
                
        except Exception as e:
            print(f"Error updating analysis: {e}")
            self.stats_label.setText(f"Analysis error: {str(e)}")
            
    def calculate_band_power(self, low_freq: float, high_freq: float):
        """Calculate power for a specific frequency band across full recording"""
        if not self.analyzer or not self.analyzer.processor:
            return None, None
            
        try:
            # Get the raw data for full recording
            data, times = self.analyzer.processor.raw.get_data(return_times=True)
            if data is None:
                return None, None
                
            # Get sampling rate
            sfreq = self.analyzer.processor.get_sampling_rate()
            
            # Parameters for sliding window
            window_length = 2.0  # seconds
            overlap = 0.5  # seconds
            
            window_samples = int(window_length * sfreq)
            overlap_samples = int(overlap * sfreq)
            step_samples = window_samples - overlap_samples
            
            # Get signal for current channel
            signal_data = data[self.current_channel] * 1e6  # Convert to μV
            
            # Calculate sliding window power for specific band across full recording
            from scipy.signal import welch
            
            band_powers = []
            window_times = []
            
            for start_idx in range(0, len(signal_data) - window_samples + 1, step_samples):
                end_idx = start_idx + window_samples
                window_data = signal_data[start_idx:end_idx]
                
                # Calculate power spectral density
                freqs, psd = welch(window_data, fs=sfreq, nperseg=window_samples)
                
                # Find band indices
                band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                band_power = np.mean(psd[band_mask]) if np.any(band_mask) else 0.0
                
                band_powers.append(band_power)
                window_times.append(times[start_idx + window_samples // 2])
                
            return np.array(window_times), np.array(band_powers)
            
        except Exception as e:
            print(f"Error calculating band power: {e}")
            return None, None
            
    def update_statistics(self, times, powers, band_name):
        """Update statistics display for full recording"""
        try:
            mean_power = np.mean(powers)
            std_power = np.std(powers)
            max_power = np.max(powers)
            min_power = np.min(powers)
            n_windows = len(powers)
            
            # Calculate time coverage
            time_span = times[-1] - times[0] if len(times) > 1 else 0
            
            stats_text = (f"Mean: {mean_power:.2f} μV² | "
                         f"Max: {max_power:.2f} μV² | "
                         f"Std: {std_power:.2f} μV² | "
                         f"Windows: {n_windows} | "
                         f"Coverage: {time_span:.1f}s")
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            self.stats_label.setText(f"Statistics error: {str(e)}")
            
    def get_active_band(self) -> str:
        """Get the currently active frequency band"""
        return self.frequency_bands.get_active_band()
        
    def set_active_band(self, band_name: str):
        """Set the active frequency band"""
        if band_name in self.frequency_bands.get_available_bands():
            self.band_combo.setCurrentText(band_name)
            
    def get_band_info(self) -> tuple:
        """Get current band information (low_freq, high_freq, color)"""
        return self.frequency_bands.get_band_info(self.frequency_bands.get_active_band())
