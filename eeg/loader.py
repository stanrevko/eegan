"""
EEG File Loader Module
Handles loading and basic info extraction from EEG files using MNE
"""

import mne
import os
from pathlib import Path


class EEGLoader:
    def __init__(self):
        self.raw = None
        self.file_path = None
        
    def load_edf(self, file_path):
        """
        Load an EDF file using MNE
        
        Args:
            file_path (str): Path to the EDF file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            print(f"Loading EDF file: {file_path}")
            
            # Load the EDF file
            self.raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
            self.file_path = file_path
            
            print("✅ File loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            self.raw = None
            self.file_path = None
            return False
    
    def get_file_info(self):
        """
        Get basic information about the loaded EEG file
        
        Returns:
            dict: File information or None if no file loaded
        """
        if self.raw is None:
            return None
        
        info = {
            'filename': os.path.basename(self.file_path),
            'n_channels': self.raw.info['nchan'],
            'sampling_rate': self.raw.info['sfreq'],
            'duration': self.raw.times[-1],  # Duration in seconds
            'channel_names': self.raw.ch_names,
            'n_samples': len(self.raw.times)
        }
        
        return info
    
    def print_file_info(self):
        """Print formatted file information"""
        info = self.get_file_info()
        if info is None:
            print("No file loaded")
            return
        
        print("\n" + "="*50)
        print("📄 EEG FILE INFORMATION")
        print("="*50)
        print(f"File: {info['filename']}")
        print(f"Channels: {info['n_channels']}")
        print(f"Sampling Rate: {info['sampling_rate']} Hz")
        print(f"Duration: {info['duration']:.2f} seconds ({info['duration']/60:.2f} minutes)")
        print(f"Total Samples: {info['n_samples']:,}")
        print(f"Channel Names: {', '.join(info['channel_names'][:5])}{'...' if len(info['channel_names']) > 5 else ''}")
        print("="*50)


def test_loader(eeg_data_path="/Users/stanrevko/projects/eegan/eeg_data"):
    """
    Test the EEG loader with the available EDF files
    
    Args:
        eeg_data_path (str): Path to the directory containing EDF files
    """
    print("🧠 Testing EEG Loader...")
    
    # Get list of EDF files
    edf_files = []
    if os.path.exists(eeg_data_path):
        edf_files = [f for f in os.listdir(eeg_data_path) if f.endswith('.edf')]
    
    if not edf_files:
        print(f"❌ No EDF files found in {eeg_data_path}")
        return
    
    print(f"📁 Found {len(edf_files)} EDF files:")
    for i, file in enumerate(edf_files, 1):
        print(f"  {i}. {file}")
    
    # Test loading the first file
    test_file = os.path.join(eeg_data_path, edf_files[0])
    print(f"\n🔍 Testing with first file: {edf_files[0]}")
    
    loader = EEGLoader()
    if loader.load_edf(test_file):
        loader.print_file_info()
        
        # Test getting raw data
        data, times = loader.raw.get_data(return_times=True)
        print(f"\n📊 Data shape: {data.shape} (channels x samples)")
        print(f"⏱️  Time range: {times[0]:.3f}s to {times[-1]:.3f}s")
        
        return loader
    else:
        print("❌ Failed to load the test file")
        return None


if __name__ == "__main__":
    # Run the test when this module is executed directly
    test_loader()
