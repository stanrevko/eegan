"""
Band Selector
Frequency band selection widget
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import pyqtSignal
from eeg.frequency_bands import FrequencyBands


class BandSelector(QWidget):
    """Frequency band selection widget"""
    
    # Signals
    band_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.frequency_bands = FrequencyBands()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the band selector UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Band selection label
        band_label = QLabel("📊 Band:")
        band_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        layout.addWidget(band_label)
        
        # Band dropdown
        self.band_combo = QComboBox()
        self.band_combo.addItems(list(self.frequency_bands.STANDARD_BANDS.keys()))
        self.band_combo.setCurrentText(self.frequency_bands.active_band)
        self.band_combo.currentTextChanged.connect(self.on_band_changed)
        self.band_combo.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 5px;
                border-radius: 3px;
                min-width: 80px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                selection-background-color: #0078d4;
            }
        """)
        layout.addWidget(self.band_combo)
        
        # Frequency range display
        self.freq_label = QLabel()
        self.freq_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(self.freq_label)
        
        # Update initial frequency display
        self.update_frequency_display()
        
    def on_band_changed(self, band_name):
        """Handle band selection changes"""
        self.frequency_bands.active_band = band_name
        self.update_frequency_display()
        self.band_changed.emit(band_name)
        
    def update_frequency_display(self):
        """Update frequency range display"""
        band_info = self.frequency_bands.get_band_info(self.frequency_bands.active_band)
        if band_info:
            low_freq, high_freq, _ = band_info
            self.freq_label.setText(f"({low_freq}-{high_freq}Hz)")
            
    def get_current_band(self):
        """Get currently selected band"""
        return self.band_combo.currentText()
        
    def set_current_band(self, band_name):
        """Set current band selection"""
        if band_name in self.frequency_bands.STANDARD_BANDS:
            self.band_combo.setCurrentText(band_name)
            
    def get_band_info(self, band_name=None):
        """Get frequency band information"""
        if band_name is None:
            band_name = self.get_current_band()
        return self.frequency_bands.get_band_info(band_name)
