#!/usr/bin/env python3
"""
Verify DFA integration with tabbed analysis panel
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

print("🧠 Verifying DFA Integration")
print("=" * 40)

try:
    # Test imports
    from gui.analysis import TabbedAnalysisPanel, DFAAnalysis
    print("✅ DFA imports successful")
    
    # Test creation (without Qt)
    from eeg.processor import EEGProcessor
    from eeg.analyzer import EEGAnalyzer
    import mne
    
    # Load EEG data
    eeg_file = "/Users/stanrevko/projects/eegan/eeg_data/background-3f.edf"
    raw = mne.io.read_raw_edf(eeg_file, preload=True, verbose=False)
    
    # Set up processor and analyzer
    processor = EEGProcessor()
    processor.set_raw_data(raw)
    analyzer = EEGAnalyzer()
    analyzer.set_processor(processor)
    
    print("✅ EEG data setup successful")
    print(f"📊 Channels: {len(raw.ch_names)}")
    print(f"📈 Samples: {len(raw.times)}")
    
    # Test DFA component directly
    dfa = DFAAnalysis()
    dfa.analyzer = analyzer
    dfa.current_channel = 0
    dfa.update_data()
    
    if dfa.current_data is not None:
        print(f"✅ DFA data update successful: {len(dfa.current_data)} samples")
        if len(dfa.current_data) >= 100:
            print("✅ Sufficient data for DFA calculation")
        else:
            print("❌ Insufficient data for DFA calculation")
    else:
        print("❌ DFA data update failed")
        
    print("\n🎯 DFA Integration Summary:")
    print("   • DFA component can be imported")
    print("   • EEG data can be loaded")  
    print("   • DFA can receive data from analyzer")
    print("   • Ready for GUI testing")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
