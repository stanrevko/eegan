"""
Frequency Bands Configuration
Configurable EEG frequency band definitions
"""

from typing import Dict, Tuple


class FrequencyBands:
    """Manages EEG frequency band definitions"""
    
    # Standard EEG frequency bands
    STANDARD_BANDS = {
        'Delta': (0.5, 4.0, '#ff4444'),      # Red
        'Theta': (4.0, 8.0, '#44ff44'),      # Green  
        'Alpha': (8.0, 13.0, '#ff9800'),     # Orange
        'Beta': (13.0, 30.0, '#8844ff'),     # Purple
        'Gamma': (30.0, 40.0, '#ff44ff')     # Magenta
    }
    
    def __init__(self):
        self.custom_bands = {}
        self.active_band = 'Alpha'
        
    def get_band_info(self, band_name: str) -> Tuple[float, float, str]:
        """
        Get frequency range and color for a band
        
        Args:
            band_name: Name of the frequency band
            
        Returns:
            Tuple of (low_freq, high_freq, color)
        """
        if band_name in self.STANDARD_BANDS:
            return self.STANDARD_BANDS[band_name]
        elif band_name in self.custom_bands:
            return self.custom_bands[band_name]
        else:
            return self.STANDARD_BANDS['Alpha']  # Default
            
    def get_available_bands(self) -> list:
        """Get list of all available band names"""
        bands = list(self.STANDARD_BANDS.keys())
        bands.extend(list(self.custom_bands.keys()))
        return sorted(bands)
        
    def add_custom_band(self, name: str, low_freq: float, high_freq: float, color: str = '#666666'):
        """Add a custom frequency band"""
        self.custom_bands[name] = (low_freq, high_freq, color)
        
    def get_band_range(self, band_name: str) -> Tuple[float, float]:
        """Get just the frequency range for a band"""
        low, high, _ = self.get_band_info(band_name)
        return low, high
        
    def get_band_color(self, band_name: str) -> str:
        """Get just the color for a band"""
        _, _, color = self.get_band_info(band_name)
        return color
        
    def set_active_band(self, band_name: str):
        """Set the currently active band for analysis"""
        if band_name in self.get_available_bands():
            self.active_band = band_name
            
    def get_active_band(self) -> str:
        """Get the currently active band"""
        return self.active_band
