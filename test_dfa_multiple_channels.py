#!/usr/bin/env python3
"""
Test DFA calculation with multiple channel switches
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

print("🧠 Testing DFA Multiple Channel Calculation")
print("=" * 50)

try:
    from gui.analysis.dfa_analysis import DFAAnalysis
    from eeg.processor import EEGProcessor
    from eeg.analyzer import EEGAnalyzer
    import mne
    import numpy as np
    
    # Load EEG data
    eeg_file = "/Users/stanrevko/projects/eegan/eeg_data/background-3f.edf"
    raw = mne.io.read_raw_edf(eeg_file, preload=True, verbose=False)
    
    # Set up processor and analyzer
    processor = EEGProcessor()
    processor.set_raw_data(raw)
    analyzer = EEGAnalyzer()
    analyzer.set_processor(processor)
    
    print(f"📊 Loaded EEG: {len(raw.ch_names)} channels")
    
    # Test DFA component (without GUI)
    dfa = DFAAnalysis()
    dfa.analyzer = analyzer
    
    # Test multiple channels
    test_channels = [0, 5, 10]
    results = []
    
    for ch_idx in test_channels:
        print(f"\n🔌 Testing channel {ch_idx}: {raw.ch_names[ch_idx]}")
        
        # Set channel
        dfa.current_channel = ch_idx
        dfa.update_data()
        
        if dfa.current_data is not None:
