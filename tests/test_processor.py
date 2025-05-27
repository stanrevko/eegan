"""
Test script for EEG processor
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from eeg.loader import EEGLoader
from eeg.processor import EEGProcessor

def test_processor():
    """Test the EEG processor with filtering"""
    print("🔧 Testing EEG Processor...")
    
    # Load a test file
    loader = EEGLoader()
    test_file = "/Users/stanrevko/projects/eegan/eeg_data/background-2m.edf"
    
    if not loader.load_edf(test_file):
        print("❌ Failed to load test file")
        return None
    
    print(f"✅ Loaded: {loader.get_file_info()['filename']}")
    
    # Create processor and set data
    processor = EEGProcessor()
    processor.set_raw_data(loader.raw)
    
    # Show original signal stats
    print("\n📊 Analyzing original signal...")
    processor.print_signal_stats(channel_idx=0, time_window=10.0)
    
    # Apply bandpass filter
    print("\n🔧 Applying 0.1-40 Hz bandpass filter...")
    if processor.apply_bandpass_filter(l_freq=0.1, h_freq=40.0):
        # Show filtered signal stats
        print("\n📊 Analyzing filtered signal...")
        processor.print_signal_stats(channel_idx=0, time_window=10.0)
        
        # Test different channels
        print(f"\n🧠 Testing different channels:")
        for i in range(min(3, len(processor.raw.ch_names))):
            stats = processor.get_signal_stats(channel_idx=i, time_window=5.0)
            if stats:
                print(f"   {stats['channel_name']}: Range reduction {((stats['original']['range'] - stats['filtered']['range']) / stats['original']['range']) * 100:.1f}%")
        
        return processor
    else:
        print("❌ Filtering failed")
        return None

if __name__ == "__main__":
    test_processor()
