"""
Test script for EEG analyzer
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from eeg.loader import EEGLoader
from eeg.processor import EEGProcessor
from eeg.analyzer import EEGAnalyzer

def test_analyzer():
    """Test the EEG analyzer with alpha power and spectrum analysis"""
    print("⚡ Testing EEG Analyzer...")
    
    # Load test file
    loader = EEGLoader()
    test_file = "/Users/stanrevko/projects/eegan/eeg_data/background-2m.edf"
    
    if not loader.load_edf(test_file):
        print("❌ Failed to load test file")
        return None
        
    print(f"✅ Loaded: {loader.get_file_info()['filename']}")
    
    # Process the data
    processor = EEGProcessor()
    processor.set_raw_data(loader.raw)
    processor.apply_bandpass_filter(l_freq=0.1, h_freq=40.0)
    
    # Create analyzer
    analyzer = EEGAnalyzer()
    analyzer.set_processor(processor)
    
    # Test alpha power analysis
    print("\n⚡ Testing Alpha Power Analysis...")
    times, alpha_powers = analyzer.calculate_alpha_power_sliding(channel_idx=0)
    
    if times is not None and alpha_powers is not None:
        print(f"✅ Alpha power calculated for {len(times)} windows")
        print(f"📊 Time range: {times[0]:.1f}s to {times[-1]:.1f}s")
        print(f"⚡ Power range: {min(alpha_powers):.3f} to {max(alpha_powers):.3f} μV²")
        
        # Show detailed statistics
        analyzer.print_alpha_statistics(channel_idx=0)
    else:
        print("❌ Alpha power calculation failed")
        
    # Test frequency spectrum analysis
    print("\n📊 Testing Frequency Spectrum Analysis...")
    freqs, psd = analyzer.calculate_frequency_spectrum(channel_idx=0)
    
    if freqs is not None and psd is not None:
        print(f"✅ Frequency spectrum calculated")
        print(f"🔊 Frequency range: {freqs[0]:.1f}Hz to {freqs[-1]:.1f}Hz")
        print(f"📈 {len(freqs)} frequency points")
        
        # Show frequency band analysis
        analyzer.print_frequency_bands(channel_idx=0)
    else:
        print("❌ Frequency spectrum calculation failed")
        
    return analyzer

if __name__ == "__main__":
    test_analyzer()
