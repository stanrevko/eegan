"""
Thread Manager
Manages background threads and their lifecycle
"""

from PyQt5.QtCore import QObject, pyqtSignal


class ThreadManager(QObject):
    """Manages background threads for the application"""
    
    # Signals
    thread_started = pyqtSignal(str)
    thread_finished = pyqtSignal(str, bool)
    
    def __init__(self):
        super().__init__()
        self.active_threads = {}
        
    def start_thread(self, thread_id, thread):
        """Start a managed thread"""
        if thread_id in self.active_threads:
            self.stop_thread(thread_id)
            
        self.active_threads[thread_id] = thread
        thread.finished.connect(lambda success, msg: self._on_thread_finished(thread_id, success, msg))
        thread.start()
        self.thread_started.emit(thread_id)
        
    def stop_thread(self, thread_id):
        """Stop a specific thread"""
        if thread_id in self.active_threads:
            thread = self.active_threads[thread_id]
            if thread.isRunning():
                thread.terminate()
                thread.wait()
            del self.active_threads[thread_id]
            
    def stop_all_threads(self):
        """Stop all active threads"""
        for thread_id in list(self.active_threads.keys()):
            self.stop_thread(thread_id)
            
    def _on_thread_finished(self, thread_id, success, message):
        """Handle thread completion"""
        if thread_id in self.active_threads:
            del self.active_threads[thread_id]
        self.thread_finished.emit(thread_id, success)
        
    def is_thread_running(self, thread_id):
        """Check if a thread is currently running"""
        return thread_id in self.active_threads
