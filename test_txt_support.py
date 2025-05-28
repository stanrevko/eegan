#!/usr/bin/env python3
"""
Test script to verify TXT file support works end-to-end
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_txt_loading():
    """Test the TXT file loading functionality"""
    print("🧪 Testing TXT File Support for EEG Analysis Suite")
    print("=" * 60)
    
    # Test 1: Import enhanced loader
    try:
        from eeg.loader import EEGLoader
        print("✅ Enhanced EEGLoader imported successfully")
    except Exception as e:
        print(f"❌ Failed to import EEGLoader: {e}")
        return False
    
    # Test 2: Load simple TXT file
    try:
        loader = EEGLoader()
        print("\n📊 Testing simple 3-channel TXT file...")
        if loader.load_file('eeg_data/sample_eeg.txt'):
            info = loader.get_file_info()
            print(f"   ✅ Loaded: {info['n_channels']} channels, {info['n_samples']} samples")
            print(f"   📈 Sampling rate: {info['sampling_rate']:.1f} Hz")
            print(f"   ⏱️  Duration: {info['duration']:.3f} seconds")
        else:
            print("   ❌ Failed to load simple TXT file")
            return False
    except Exception as e:
        print(f"   ❌ Error loading simple TXT: {e}")
        return False
    
    # Test 3: Load complex multi-channel TXT file
    try:
        loader2 = EEGLoader()
        print("\n🧠 Testing 21-channel TXT file...")
        if loader2.load_file('eeg_data/multi_channel_sample.txt'):
            info = loader2.get_file_info()
            print(f"   ✅ Loaded: {info['n_channels']} channels, {info['n_samples']} samples")
            print(f"   📈 Sampling rate: {info['sampling_rate']:.1f} Hz")
            print(f"   🎯 Channels: {', '.join(info['channel_names'][:5])}..." )
            
            # Test data extraction
            data, times = loader2.raw.get_data(return_times=True)
            print(f"   📊 Data shape: {data.shape}")
            print(f"   🔢 Value range: {data.min():.2f} to {data.max():.2f}")
        else:
            print("   ❌ Failed to load multi-channel TXT file")
            return False
    except Exception as e:
        print(f"   ❌ Error loading multi-channel TXT: {e}")
        return False
    
    # Test 4: Verify processor compatibility
    try:
        from eeg.processor import EEGProcessor
        print("\n🔧 Testing TXT data with EEG processor...")
        processor = EEGProcessor()
        processor.set_raw_data(loader2.raw)
        
        # Try applying a filter (but ignore the warning for short data)
        if processor.apply_bandpass_filter(l_freq=0.1, h_freq=40.0, verbose=False):
            print("   ✅ TXT data successfully processed with bandpass filter")
        else:
            print("   ❌ Failed to process TXT data")
            return False
    except Exception as e:
        print(f"   ❌ Error processing TXT data: {e}")
        return False
    
    # Test 5: Verify analyzer compatibility  
    try:
        from eeg.analyzer import EEGAnalyzer
        print("\n📈 Testing TXT data with EEG analyzer...")
        analyzer = EEGAnalyzer()
        analyzer.set_processor(processor)
        
        # Try power analysis
        results = analyzer.calculate_band_power("Alpha", 0)
        
        if results is not None:
            print(f"   ✅ Alpha band analysis successful: power = {results:.4f}")
        else:
            print("   ❌ Failed to analyze TXT data")
            return False
    except Exception as e:
        print(f"   ❌ Error analyzing TXT data: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! TXT file support is working correctly!")
    print("📁 The application now supports both EDF and TXT file formats")
    print("🧠 TXT files with EEG data can be loaded and analyzed just like EDF files")
    
    return True

def show_supported_formats():
    """Show information about supported file formats"""
    print("\n📋 SUPPORTED EEG FILE FORMATS:")
    print("=" * 60)
    
    print("1. 📄 EDF Files (.edf)")
    print("   • European Data Format - industry standard")
    print("   • Loaded using MNE library")
    print("   • Full metadata and channel information")
    print("   • Example: Biofeed05-1m.edf")
    
    print("\n2. 📊 TXT Files (.txt)")
    print("   • Tab-separated text format")
    print("   • First column: time (hh:mm:ss.mmm format)")
    print("   • Remaining columns: EEG channel data")
    print("   • Header row with channel names required")
    print("   • Example format:")
    print("     hh:mm:ss.mmm    Fp1    Fp2    F3")
    print("     0:0:0.000       5.27   4.12   3.98")
    print("     0:0:0.002       8.56   7.23   6.54")
    
    print("\n✨ Both formats work seamlessly with all analysis tools!")

if __name__ == "__main__":
    success = test_txt_loading()
    show_supported_formats()
    
    if success:
        print("\n🚀 Ready to test in the GUI application!")
        print("   Run: python main.py")
        print("   Look for 📊 icons next to TXT files in the file browser")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
        sys.exit(1)
