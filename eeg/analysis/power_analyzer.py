"""
Power Analyzer
Frequency band power analysis
"""

import numpy as np
from scipy import signal
from eeg.frequency_bands import FrequencyBands


class PowerAnalyzer:
    """Analyzes power in specific frequency bands"""
    
    def __init__(self):
        self.frequency_bands = FrequencyBands()
        
    def calculate_band_power(self, data, sfreq, band_name, method='welch'):
        """
        Calculate power in a specific frequency band
        
        Args:
            data: EEG data (samples,)
            sfreq: Sampling frequency
            band_name: Name of frequency band
            method: Method for PSD calculation ('welch' or 'periodogram')
            
        Returns:
            Power value in the specified band
        """
        try:
            band_info = self.frequency_bands.get_band_info(band_name)
            if not band_info:
                return 0.0
                
            low_freq, high_freq, _ = band_info
            
            # Calculate power spectral density
            if method == 'welch':
                freqs, psd = signal.welch(data, sfreq, nperseg=min(len(data), 512))
            else:
                freqs, psd = signal.periodogram(data, sfreq)
                
            # Find frequency indices for the band
            freq_mask = (freqs >= low_freq) & (freqs <= high_freq)
            
            # Calculate power in the band
            band_power = np.trapz(psd[freq_mask], freqs[freq_mask])
            
            return band_power
            
        except Exception as e:
            print(f"Error calculating band power: {e}")
            return 0.0
            
    def calculate_relative_power(self, data, sfreq, band_name, total_range=(0.5, 40.0)):
        """
        Calculate relative power (band power / total power)
        
        Args:
            data: EEG data
            sfreq: Sampling frequency
            band_name: Name of frequency band
            total_range: Frequency range for total power calculation
            
        Returns:
            Relative power (0-1)
        """
        try:
            # Calculate band power
            band_power = self.calculate_band_power(data, sfreq, band_name)
            
            # Calculate total power in specified range
            freqs, psd = signal.welch(data, sfreq, nperseg=min(len(data), 512))
            total_mask = (freqs >= total_range[0]) & (freqs <= total_range[1])
            total_power = np.trapz(psd[total_mask], freqs[total_mask])
            
            if total_power > 0:
                return band_power / total_power
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error calculating relative power: {e}")
            return 0.0
            
    def calculate_power_over_time(self, data, sfreq, band_name, window_size=2.0, step_size=0.5):
        """
        Calculate power over time using sliding windows
        
        Args:
            data: EEG data (samples,)
            sfreq: Sampling frequency
            band_name: Name of frequency band
            window_size: Window size in seconds
            step_size: Step size in seconds
            
        Returns:
            Array of power values over time
        """
        try:
            window_samples = int(window_size * sfreq)
            step_samples = int(step_size * sfreq)
            
            n_samples = len(data)
            power_values = []
            
            for start in range(0, n_samples - window_samples + 1, step_samples):
                end = start + window_samples
                window_data = data[start:end]
                
                power = self.calculate_band_power(window_data, sfreq, band_name)
                power_values.append(power)
                
            return np.array(power_values)
            
        except Exception as e:
            print(f"Error calculating power over time: {e}")
            return np.array([])
            
    def calculate_all_bands_power(self, data, sfreq):
        """
        Calculate power for all standard frequency bands
        
        Args:
            data: EEG data
            sfreq: Sampling frequency
            
        Returns:
            Dictionary with band names and power values
        """
        powers = {}
        
        for band_name in self.frequency_bands.STANDARD_BANDS.keys():
            powers[band_name] = self.calculate_band_power(data, sfreq, band_name)
            
        return powers
        
    def get_dominant_frequency(self, data, sfreq, freq_range=(1, 40)):
        """
        Get the dominant frequency in a given range
        
        Args:
            data: EEG data
            sfreq: Sampling frequency
            freq_range: Frequency range to analyze
            
        Returns:
            Dominant frequency in Hz
        """
        try:
            freqs, psd = signal.welch(data, sfreq, nperseg=min(len(data), 512))
            
            # Find frequencies in range
            freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
            
            if np.any(freq_mask):
                # Find peak frequency
                peak_idx = np.argmax(psd[freq_mask])
                dominant_freq = freqs[freq_mask][peak_idx]
                return dominant_freq
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error finding dominant frequency: {e}")
            return 0.0
