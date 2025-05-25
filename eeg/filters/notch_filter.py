"""
Notch Filter
Notch filtering for removing power line interference
"""

import mne
import numpy as np


class NotchFilter:
    """Notch filter for removing power line interference"""
    
    def __init__(self, freqs=50.0):
        """
        Initialize notch filter
        
        Args:
            freqs: Frequency or list of frequencies to remove (default: 50Hz)
        """
        if isinstance(freqs, (int, float)):
            self.freqs = [freqs]
        else:
            self.freqs = list(freqs)
            
    def apply(self, raw, freqs=None):
        """
        Apply notch filter to raw EEG data
        
        Args:
            raw: MNE Raw object
            freqs: Frequencies to filter (overrides default)
            
        Returns:
            Filtered Raw object
        """
        if freqs is None:
            freqs = self.freqs
        elif isinstance(freqs, (int, float)):
            freqs = [freqs]
            
        try:
            print(f"🔧 Applying notch filter: {freqs} Hz")
            
            # Apply notch filter
            raw_filtered = raw.copy()
            raw_filtered.notch_filter(freqs=freqs, fir_design='firwin')
            
            print(f"✅ Notch filter applied successfully")
            return raw_filtered
            
        except Exception as e:
            print(f"❌ Error applying notch filter: {e}")
            return raw
            
    def set_frequencies(self, freqs):
        """Set notch frequencies"""
        if isinstance(freqs, (int, float)):
            self.freqs = [freqs]
        else:
            self.freqs = list(freqs)
            
    def get_frequencies(self):
        """Get current notch frequencies"""
        return self.freqs
        
    def add_frequency(self, freq):
        """Add a frequency to the notch filter"""
        if freq not in self.freqs:
            self.freqs.append(freq)
            
    def remove_frequency(self, freq):
        """Remove a frequency from the notch filter"""
        if freq in self.freqs:
            self.freqs.remove(freq)
