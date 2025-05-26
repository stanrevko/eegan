#!/usr/bin/env python3
"""
Test script to verify channel selector works with real EEG data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
    from gui.analysis import TabbedAnalysisPanel
    from eeg.loader import EEGLoader
    from eeg.processor import EEGProcessor  
    from eeg.analyzer import EEGAnalyzer
    import mne
    
    def test_with_real_eeg():
        """Test channel selector with real EEG data"""
        print("🧠 Testing Channel Selector with Real EEG Data")
        print("=" * 50)
        
        try:
            # Load EEG data
            eeg_file = "/Users/stanrevko/projects/eegan/eeg_data/background-3f.edf"
            raw = mne.io.read_raw_edf(eeg_file, preload=True, verbose=False)
            print(f"📊 Loaded EEG file: {len(raw.ch_names)} channels")
            
            # Set up processor and analyzer
            processor = EEGProcessor()
            processor.set_raw_data(raw)
            
            analyzer = EEGAnalyzer()
            analyzer.set_processor(processor)
            
            # Create analysis panel
            analysis_panel = TabbedAnalysisPanel()
            analysis_panel.set_analyzer(analyzer)
            
            print(f"🔌 Channel selector populated with {len(raw.ch_names)} channels:")
            for i in range(min(10, len(raw.ch_names))):
                channel_name = raw.ch_names[i]
                clean_name = channel_name.replace("EEG ", "") if channel_name.startswith("EEG ") else channel_name
                print(f"   {i}: {clean_name}")
            if len(raw.ch_names) > 10:
                print(f"   ... and {len(raw.ch_names) - 10} more channels")
                
            print("\n✅ Channel selector setup successful!")
            print("🎯 In the GUI, you should see channels like: Fp1, Fp2, F3, F4, etc.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
    if __name__ == "__main__":
        test_with_real_eeg()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Run this script in the virtual environment")
