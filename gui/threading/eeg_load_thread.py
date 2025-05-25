"""
EEG Loading Thread
Background thread for loading and processing EEG files
"""

from PyQt5.QtCore import QThread, pyqtSignal
from eeg.loader import EEGLoader
from eeg.processor import EEGProcessor
from eeg.analyzer import EEGAnalyzer


class EEGLoadThread(QThread):
    """Background thread for loading and processing EEG files"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.loader = None
        self.processor = None
        self.analyzer = None
        
    def run(self):
        """Execute the loading process"""
        try:
            self.progress.emit("🔄 Loading EEG file...")
            self.loader = EEGLoader()
            
            if self.loader.load_edf(self.file_path):
                self.progress.emit("🔧 Applying 0.1-40Hz filter...")
                self.processor = EEGProcessor()
                self.processor.set_raw_data(self.loader.raw)
                self.processor.apply_bandpass_filter(l_freq=0.1, h_freq=40.0)
                
                self.progress.emit("⚡ Calculating frequency analysis...")
                self.analyzer = EEGAnalyzer()
                self.analyzer.set_processor(self.processor)
                
                self.finished.emit(True, "✅ Complete analysis ready!")
            else:
                self.finished.emit(False, "❌ Failed to load file")
                
        except Exception as e:
            self.finished.emit(False, f"❌ Error: {str(e)}")
            
    def get_results(self):
        """Get the loaded components"""
        return self.loader, self.processor, self.analyzer
