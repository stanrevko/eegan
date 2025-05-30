"""
EEG Signal Processor Module
Handles filtering and preprocessing of EEG signals using MNE
"""

import mne
import numpy as np
from typing import Optional, Tuple


class EEGProcessor:
    def __init__(self):
        self.raw = None
        self.original_raw = None
        self.filter_applied = False
        
    def set_raw_data(self, raw_data):
        """
        Set the raw EEG data for processing
        
        Args:
            raw_data: MNE Raw object
        """
        self.raw = raw_data.copy()  # Work with a copy to preserve original
        self.original_raw = raw_data.copy()  # Keep original for comparison
        self.filter_applied = False
        
    def apply_bandpass_filter(self, l_freq=0.1, h_freq=40.0, method='fir', verbose=False):
        """
        Apply bandpass filter to the EEG data
        
        Args:
            l_freq (float): Low frequency cutoff (default: 0.1 Hz)
            h_freq (float): High frequency cutoff (default: 40.0 Hz)
            method (str): Filter method ('fir' or 'iir')
            verbose (bool): Print filtering info
            
        Returns:
            bool: True if filtering successful
        """
        if self.raw is None:
            print("❌ No EEG data loaded")
            return False
            
        try:
            print(f"🔧 Applying bandpass filter: {l_freq} - {h_freq} Hz")
            
            # Apply the bandpass filter
            self.raw.filter(l_freq=l_freq, h_freq=h_freq, method=method, verbose=verbose)
            self.filter_applied = True
            
            print("✅ Filter applied successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error applying filter: {e}")
            return False
    
    def get_filtered_data(self, start_time=None, stop_time=None):
        """
        Get filtered EEG data
        
        Args:
            start_time (float): Start time in seconds (optional)
            stop_time (float): Stop time in seconds (optional)
            
        Returns:
            tuple: (data, times) or (None, None) if error
        """
        if self.raw is None:
            return None, None
            
        try:
            # Convert time to samples if provided
            start_sample = None
            stop_sample = None
            
            if start_time is not None:
                start_sample = int(start_time * self.raw.info['sfreq'])
            if stop_time is not None:
                stop_sample = int(stop_time * self.raw.info['sfreq'])
            
            if start_sample is not None or stop_sample is not None:
                data, times = self.raw.get_data(start=start_sample, stop=stop_sample, return_times=True)
            else:
                data, times = self.raw.get_data(return_times=True)
            
            return data, times
            
        except Exception as e:
            print(f"❌ Error getting data: {e}")
            return None, None
    
    def get_original_data(self, start_time=None, stop_time=None):
        """
        Get original (unfiltered) EEG data for comparison
        
        Args:
            start_time (float): Start time in seconds (optional)
            stop_time (float): Stop time in seconds (optional)
            
        Returns:
            tuple: (data, times) or (None, None) if error
        """
        if self.original_raw is None:
            return None, None
            
        try:
            # Convert time to samples if provided
            start_sample = None
            stop_sample = None
            
            if start_time is not None:
                start_sample = int(start_time * self.original_raw.info['sfreq'])
            if stop_time is not None:
                stop_sample = int(stop_time * self.original_raw.info['sfreq'])
            
            if start_sample is not None or stop_sample is not None:
                data, times = self.original_raw.get_data(start=start_sample, stop=stop_sample, return_times=True)
            else:
                data, times = self.original_raw.get_data(return_times=True)
            
            return data, times
            
        except Exception as e:
            print(f"❌ Error getting original data: {e}")
            return None, None
    
    def get_signal_stats(self, channel_idx=0, time_window=5.0):
        """
        Get basic statistics about the signal before and after filtering
        
        Args:
            channel_idx (int): Channel index to analyze
            time_window (float): Time window in seconds for analysis
            
        Returns:
            dict: Signal statistics
        """
        if self.raw is None or self.original_raw is None:
            return None
        
        # Get a sample of data for statistics
        orig_data, times = self.get_original_data(start_time=0, stop_time=time_window)
        filt_data, _ = self.get_filtered_data(start_time=0, stop_time=time_window)
        
        if orig_data is None or filt_data is None:
            return None
        
        # Calculate statistics for the specified channel
        orig_signal = orig_data[channel_idx]
        filt_signal = filt_data[channel_idx]
        
        # Convert from Volts to microVolts (MNE default unit is Volts)
        orig_signal = orig_signal * 1e6  # Convert to μV
        filt_signal = filt_signal * 1e6  # Convert to μV
        
        stats = {
            'channel_name': self.raw.ch_names[channel_idx],
            'original': {
                'mean': np.mean(orig_signal),
                'std': np.std(orig_signal),
                'min': np.min(orig_signal),
                'max': np.max(orig_signal),
                'range': np.max(orig_signal) - np.min(orig_signal)
            },
            'filtered': {
                'mean': np.mean(filt_signal),
                'std': np.std(filt_signal),
                'min': np.min(filt_signal),
                'max': np.max(filt_signal),
                'range': np.max(filt_signal) - np.min(filt_signal)
            },
            'time_window': time_window,
            'filter_applied': self.filter_applied
        }
        
        return stats
    
    def print_signal_stats(self, channel_idx=0, time_window=5.0):
        """Print formatted signal statistics"""
        stats = self.get_signal_stats(channel_idx, time_window)
        if stats is None:
            print("No statistics available")
            return
        
        print("\n" + "="*60)
        print(f"📊 SIGNAL STATISTICS - {stats['channel_name']}")
        print(f"⏱️  Time Window: {stats['time_window']} seconds")
        print("="*60)
        
        print("📈 ORIGINAL SIGNAL:")
        print(f"   Mean: {stats['original']['mean']:.3f} μV")
        print(f"   Std:  {stats['original']['std']:.3f} μV")
        print(f"   Range: {stats['original']['min']:.3f} to {stats['original']['max']:.3f} μV")
        print(f"   Peak-to-Peak: {stats['original']['range']:.3f} μV")
        
        if stats['filter_applied']:
            print("\n🔧 FILTERED SIGNAL (0.1-40 Hz):")
            print(f"   Mean: {stats['filtered']['mean']:.3f} μV")
            print(f"   Std:  {stats['filtered']['std']:.3f} μV")
            print(f"   Range: {stats['filtered']['min']:.3f} to {stats['filtered']['max']:.3f} μV")
            print(f"   Peak-to-Peak: {stats['filtered']['range']:.3f} μV")
            
            # Calculate reduction in range (often indicates noise removal)
            range_reduction = ((stats['original']['range'] - stats['filtered']['range']) / stats['original']['range']) * 100
            print(f"   Range Reduction: {range_reduction:.1f}%")
        else:
            print("\n❌ No filter applied yet")
        
        print("="*60)
    
    def get_channel_names(self):
        """Get list of channel names"""
        if self.raw is None:
            return []
        return self.raw.ch_names
    
    def get_sampling_rate(self):
        """Get sampling rate"""
        if self.raw is None:
            return None
        return self.raw.info['sfreq']
    
    def get_duration(self):
        """Get signal duration in seconds"""
        if self.raw is None:
            return None
        return self.raw.times[-1]
