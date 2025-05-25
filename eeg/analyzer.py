"""
EEG Signal Analyzer Module
Handles spectral analysis including Alpha power and frequency spectrum
"""

import numpy as np
from scipy import signal
from scipy.signal import spectrogram, welch
import mne
from typing import Tuple, Optional


class EEGAnalyzer:
    def __init__(self):
        self.processor = None
        
    def set_processor(self, processor):
        """
        Set the EEG processor for analysis
        
        Args:
            processor: EEGProcessor instance with loaded and filtered data
        """
        self.processor = processor
        
    def calculate_alpha_power_sliding(self, channel_idx=0, window_length=2.0, overlap=0.5):
        """
        Calculate Alpha power (8-13 Hz) using sliding windows
        
        Args:
            channel_idx (int): Channel index to analyze
            window_length (float): Window length in seconds (default: 2.0)
            overlap (float): Overlap between windows in seconds (default: 0.5)
            
        Returns:
            tuple: (times, alpha_powers) or (None, None) if error
        """
        if self.processor is None or self.processor.raw is None:
            return None, None
            
        try:
            # Get filtered data - get all data without time limits
            data, times = self.processor.raw.get_data(return_times=True)
            if data is None:
                return None, None
                
            # Convert to microvolts
            data = data * 1e6
                
            # Get sampling rate
            sfreq = self.processor.get_sampling_rate()
            
            # Calculate window parameters
            window_samples = int(window_length * sfreq)
            overlap_samples = int(overlap * sfreq)
            step_samples = window_samples - overlap_samples
            
            # Get signal for the specified channel
            signal_data = data[channel_idx]
            
            # Calculate sliding window alpha power
            alpha_powers = []
            window_times = []
            
            for start_idx in range(0, len(signal_data) - window_samples + 1, step_samples):
                end_idx = start_idx + window_samples
                window_data = signal_data[start_idx:end_idx]
                
                # Calculate power spectral density for this window
                freqs, psd = welch(window_data, fs=sfreq, nperseg=window_samples)
                
                # Find alpha band (8-13 Hz) indices
                alpha_mask = (freqs >= 8) & (freqs <= 13)
                alpha_power = np.mean(psd[alpha_mask])
                
                alpha_powers.append(alpha_power)
                window_times.append(times[start_idx + window_samples // 2])  # Middle of window
                
            return np.array(window_times), np.array(alpha_powers)
            
        except Exception as e:
            print(f"❌ Error calculating alpha power: {e}")
            return None, None
    
    def calculate_frequency_spectrum(self, channel_idx=0, method='welch'):
        """
        Calculate full frequency spectrum for the entire signal
        
        Args:
            channel_idx (int): Channel index to analyze
            method (str): Method for spectrum calculation ('welch' or 'periodogram')
            
        Returns:
            tuple: (frequencies, power_spectrum) or (None, None) if error
        """
        if self.processor is None or self.processor.raw is None:
            return None, None
            
        try:
            # Get filtered data - get all data without time limits
            data, times = self.processor.raw.get_data(return_times=True)
            if data is None:
                return None, None
                
            # Convert to microvolts
            data = data * 1e6
                
            # Get sampling rate
            sfreq = self.processor.get_sampling_rate()
            
            # Get signal for the specified channel
            signal_data = data[channel_idx]
            
            if method == 'welch':
                # Use Welch's method for better frequency resolution
                freqs, psd = welch(signal_data, fs=sfreq, nperseg=min(len(signal_data)//4, int(4*sfreq)))
            else:
                # Use periodogram
                freqs, psd = signal.periodogram(signal_data, fs=sfreq)
            
            # Limit to the filtered frequency range (0.1-40 Hz)
            freq_mask = (freqs >= 0.1) & (freqs <= 40)
            
            return freqs[freq_mask], psd[freq_mask]
            
        except Exception as e:
            print(f"❌ Error calculating frequency spectrum: {e}")
            return None, None
    
    def get_frequency_bands_power(self, channel_idx=0):
        """
        Calculate power in standard EEG frequency bands
        
        Args:
            channel_idx (int): Channel index to analyze
            
        Returns:
            dict: Power values for each frequency band
        """
        freqs, psd = self.calculate_frequency_spectrum(channel_idx)
        if freqs is None or psd is None:
            return None
            
        # Define frequency bands
        bands = {
            'Delta (0.5-4 Hz)': (0.5, 4),
            'Theta (4-8 Hz)': (4, 8),
            'Alpha (8-13 Hz)': (8, 13),
            'Beta (13-30 Hz)': (13, 30),
            'Gamma (30-40 Hz)': (30, 40)
        }
        
        band_powers = {}
        for band_name, (low_freq, high_freq) in bands.items():
            band_mask = (freqs >= low_freq) & (freqs <= high_freq)
            if np.any(band_mask):
                band_powers[band_name] = np.mean(psd[band_mask])
            else:
                band_powers[band_name] = 0.0
                
        return band_powers
    
    def get_alpha_statistics(self, channel_idx=0):
        """
        Get detailed statistics about alpha power
        
        Args:
            channel_idx (int): Channel index to analyze
            
        Returns:
            dict: Alpha power statistics
        """
        times, alpha_powers = self.calculate_alpha_power_sliding(channel_idx)
        if times is None or alpha_powers is None:
            return None
            
        stats = {
            'channel_name': self.processor.get_channel_names()[channel_idx],
            'mean_alpha_power': np.mean(alpha_powers),
            'std_alpha_power': np.std(alpha_powers),
            'min_alpha_power': np.min(alpha_powers),
            'max_alpha_power': np.max(alpha_powers),
            'alpha_variability': np.std(alpha_powers) / np.mean(alpha_powers) if np.mean(alpha_powers) > 0 else 0,
            'n_windows': len(alpha_powers),
            'window_duration': times[1] - times[0] if len(times) > 1 else 0
        }
        
        return stats
    
    def print_alpha_statistics(self, channel_idx=0):
        """Print formatted alpha power statistics"""
        stats = self.get_alpha_statistics(channel_idx)
        if stats is None:
            print("No alpha statistics available")
            return
            
        print("\n" + "="*60)
        print(f"⚡ ALPHA POWER STATISTICS - {stats['channel_name']}")
        print("="*60)
        print(f"Mean Alpha Power: {stats['mean_alpha_power']:.3f} μV²")
        print(f"Standard Deviation: {stats['std_alpha_power']:.3f} μV²")
        print(f"Range: {stats['min_alpha_power']:.3f} to {stats['max_alpha_power']:.3f} μV²")
        print(f"Variability (CV): {stats['alpha_variability']:.3f}")
        print(f"Number of Windows: {stats['n_windows']}")
        print(f"Window Overlap: {stats['window_duration']:.3f} seconds")
        print("="*60)
        
    def print_frequency_bands(self, channel_idx=0):
        """Print frequency band power analysis"""
        bands = self.get_frequency_bands_power(channel_idx)
        if bands is None:
            print("No frequency band data available")
            return
            
        channel_name = self.processor.get_channel_names()[channel_idx]
        
        print("\n" + "="*60)
        print(f"📊 FREQUENCY BAND ANALYSIS - {channel_name}")
        print("="*60)
        
        total_power = sum(bands.values())
        
        for band_name, power in bands.items():
            percentage = (power / total_power * 100) if total_power > 0 else 0
            print(f"{band_name}: {power:.3f} μV² ({percentage:.1f}%)")
            
        print(f"\nTotal Power: {total_power:.3f} μV²")
        print("="*60)
