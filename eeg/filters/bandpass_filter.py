"""
Bandpass Filter
Bandpass filtering for EEG signals
"""

import mne
import numpy as np


class BandpassFilter:
    """Bandpass filter for EEG signals"""
    
    def __init__(self, l_freq=0.1, h_freq=40.0):
        self.l_freq = l_freq
        self.h_freq = h_freq
        
    def apply(self, raw, l_freq=None, h_freq=None):
        """
        Apply bandpass filter to raw EEG data
        
        Args:
            raw: MNE Raw object
            l_freq: Low frequency (overrides default)
            h_freq: High frequency (overrides default)
            
        Returns:
            Filtered Raw object
        """
        if l_freq is None:
            l_freq = self.l_freq
        if h_freq is None:
            h_freq = self.h_freq
            
        try:
            print(f"🔧 Applying bandpass filter: {l_freq}-{h_freq} Hz")
            
            # Apply bandpass filter
            raw_filtered = raw.copy()
            raw_filtered.filter(l_freq=l_freq, h_freq=h_freq, fir_design='firwin')
            
            print(f"✅ Bandpass filter applied successfully")
            return raw_filtered
            
        except Exception as e:
            print(f"❌ Error applying bandpass filter: {e}")
            return raw
            
    def set_frequencies(self, l_freq, h_freq):
        """Set filter frequencies"""
        self.l_freq = l_freq
        self.h_freq = h_freq
        
    def get_frequencies(self):
        """Get current filter frequencies"""
        return self.l_freq, self.h_freq
        
    def validate_frequencies(self, l_freq, h_freq, sfreq):
        """Validate filter frequencies against sampling rate"""
        nyquist = sfreq / 2
        
        if l_freq <= 0:
            raise ValueError("Low frequency must be positive")
        if h_freq >= nyquist:
            raise ValueError(f"High frequency must be less than Nyquist frequency ({nyquist} Hz)")
        if l_freq >= h_freq:
            raise ValueError("Low frequency must be less than high frequency")
            
        return True
