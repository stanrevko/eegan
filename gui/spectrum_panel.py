"""
Spectrum Panel Module
Power spectrum visualization with frequency band markers
"""

import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from eeg.frequency_bands import FrequencyBands
from utils.ui_helpers import setup_dark_plot


class SpectrumPanel(QWidget):
    """Power spectrum visualization panel"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.frequency_bands = FrequencyBands()
        self.current_channel = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the spectrum panel UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Power Spectrum")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196f3;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        scale_label = QLabel("Log Scale")
        scale_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        header_layout.addWidget(scale_label)
        
        layout.addLayout(header_layout)
        
        # Spectrum plot
        self.spectrum_plot = pg.PlotWidget(background='#2b2b2b')
        setup_dark_plot(self.spectrum_plot, 'Frequency (Hz)', 'Power (μV²)')
        self.spectrum_plot.setLogMode(False, True)
        self.spectrum_plot.setLimits(xMin=0, yMin=0.001)
        layout.addWidget(self.spectrum_plot)
        
        # Info panel
        info_group = QGroupBox("Frequency Band Analysis")
        info_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        info_layout = QVBoxLayout(info_group)
        
        self.bands_info_label = QLabel("Load file to see frequency band analysis")
        self.bands_info_label.setStyleSheet("color: #cccccc; font-size: 12px; padding: 4px;")
        info_layout.addWidget(self.bands_info_label)
        
        self.spectrum_stats_label = QLabel("Full signal power analysis")
        self.spectrum_stats_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 4px;")
        info_layout.addWidget(self.spectrum_stats_label)
        
        layout.addWidget(info_group)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        self.update_spectrum()
        
    def set_channel(self, channel_idx):
        """Set the channel for analysis"""
        self.current_channel = channel_idx
        self.update_spectrum()
        
    def update_spectrum(self):
        """Update the power spectrum display"""
        if not self.analyzer:
            return
            
        try:
            freqs, psd = self.analyzer.calculate_frequency_spectrum(self.current_channel)
            
            if freqs is not None and psd is not None:
                self.spectrum_plot.clear()
                self.spectrum_plot.plot(freqs, psd, pen=pg.mkPen(color='#2196f3', width=2))
                self.add_frequency_markers(freqs)
                self.spectrum_plot.setXRange(0, 40)
                self.update_band_powers()
                self.update_spectrum_stats(freqs, psd)
                
        except Exception as e:
            print(f"Error updating spectrum: {e}")
            
    def add_frequency_markers(self, freqs):
        """Add frequency band markers"""
        try:
            for band_name in self.frequency_bands.get_available_bands():
                low_freq, high_freq, color = self.frequency_bands.get_band_info(band_name)
                
                if low_freq >= freqs[0] and low_freq <= freqs[-1]:
                    line = pg.InfiniteLine(pos=low_freq, angle=90,
                                         pen=pg.mkPen(color=color, style=pg.QtCore.Qt.DashLine, width=2))
                    self.spectrum_plot.addItem(line)
                    
                if high_freq >= freqs[0] and high_freq <= freqs[-1]:
                    line = pg.InfiniteLine(pos=high_freq, angle=90,
                                         pen=pg.mkPen(color=color, style=pg.QtCore.Qt.DashLine, width=2))
                    self.spectrum_plot.addItem(line)
                    
        except Exception as e:
            print(f"Error adding markers: {e}")
            
    def update_band_powers(self):
        """Update frequency band powers"""
        if not self.analyzer:
            return
            
        try:
            bands_power = self.analyzer.get_frequency_bands_power(self.current_channel)
            
            if bands_power:
                total_power = sum(bands_power.values())
                band_texts = []
                
                for band_name, power in bands_power.items():
                    percentage = (power / total_power * 100) if total_power > 0 else 0
                    simple_name = band_name.split(' (')[0]
                    _, _, color = self.frequency_bands.get_band_info(simple_name)
                    
                    band_text = f"<span style='color: {color}; font-weight: bold;'>{simple_name}</span>: {power:.1f} μV² ({percentage:.1f}%)"
                    band_texts.append(band_text)
                
                self.bands_info_label.setText("<br>".join(band_texts))
                
        except Exception as e:
            print(f"Error updating band powers: {e}")
            
    def update_spectrum_stats(self, freqs, psd):
        """Update spectrum statistics"""
        try:
            total_power = np.sum(psd)
            peak_freq = freqs[np.argmax(psd)]
            peak_power = np.max(psd)
            
            stats_text = f"Total: {total_power:.1f} μV² | Peak: {peak_power:.1f} μV² @ {peak_freq:.1f} Hz"
            self.spectrum_stats_label.setText(stats_text)
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            
    def highlight_frequency_band(self, band_name):
        """Highlight a specific frequency band"""
        try:
            low_freq, high_freq, color = self.frequency_bands.get_band_info(band_name)
            region = pg.LinearRegionItem(values=[low_freq, high_freq], 
                                       brush=pg.mkBrush(color=color, alpha=50),
                                       movable=False)
            self.spectrum_plot.addItem(region)
        except Exception as e:
            print(f"Error highlighting band: {e}")
