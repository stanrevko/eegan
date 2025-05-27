#!/usr/bin/env python3
"""
Test script for the modular EEG Analysis Suite
"""

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        # Test GUI modules
        from gui.windows import MainWindow, WindowManager, LayoutManager
        print("✅ Window modules imported successfully")
        
        from gui.threading import EEGLoadThread, ThreadManager
        print("✅ Threading modules imported successfully")
        
        from gui.controls import ToolbarManager, ShortcutsManager
        print("✅ Control modules imported successfully")
        
        from gui.plots import EEGPlotWidget, TimelineControls, ChannelControls
        print("✅ Plot modules imported successfully")
        
        from gui.analysis import BandSelector, PowerPlot, AnalysisControls
        print("✅ Analysis modules imported successfully")
        
        # Test EEG modules
        from eeg.filters import BandpassFilter, NotchFilter, FilterManager
        print("✅ Filter modules imported successfully")
        
        from eeg.analysis import PowerAnalyzer
        print("✅ Analysis modules imported successfully")
        
        # Test main panels
        from gui.eeg_timeline_panel import EEGTimelinePanel
        from gui.analysis_panel import AnalysisPanel
        print("✅ Main panels imported successfully")
        
        print("\n🎉 All modular components imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_structure():
    """Test the modular structure"""
    print("\n📁 Testing modular structure...")
    
    import os
    
    # Check that all expected directories exist
    dirs_to_check = [
        'gui/windows',
        'gui/threading', 
        'gui/controls',
        'gui/plots',
        'gui/analysis',
        'eeg/filters',
        'eeg/analysis'
    ]
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            
    print("\n📊 File count by module:")
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            py_files = [f for f in os.listdir(dir_path) if f.endswith('.py')]
            print(f"   {dir_path}: {len(py_files)} Python files")

def main():
    """Run all tests"""
    print("🧠 Testing Modular EEG Analysis Suite")
    print("=" * 50)
    
    success = test_imports()
    test_structure()
    
    if success:
        print("\n🚀 Modular refactoring completed successfully!")
        print("   Ready to run: python main.py")
    else:
        print("\n❌ Some issues found. Check the errors above.")

if __name__ == "__main__":
    main()
