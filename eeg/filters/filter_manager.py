"""
Filter Manager
Manages multiple filters and filter chains
"""

from .bandpass_filter import BandpassFilter
from .notch_filter import NotchFilter


class FilterManager:
    """Manages EEG filters and filter chains"""
    
    def __init__(self):
        self.filters = {}
        self.filter_chain = []
        
    def add_bandpass_filter(self, name, l_freq=0.1, h_freq=40.0):
        """Add a bandpass filter"""
        self.filters[name] = BandpassFilter(l_freq, h_freq)
        
    def add_notch_filter(self, name, freqs=50.0):
        """Add a notch filter"""
        self.filters[name] = NotchFilter(freqs)
        
    def remove_filter(self, name):
        """Remove a filter"""
        if name in self.filters:
            del self.filters[name]
            
    def set_filter_chain(self, filter_names):
        """Set the order of filters to apply"""
        self.filter_chain = filter_names
        
    def apply_filter_chain(self, raw):
        """Apply all filters in the chain"""
        filtered_raw = raw.copy()
        
        for filter_name in self.filter_chain:
            if filter_name in self.filters:
                filter_obj = self.filters[filter_name]
                filtered_raw = filter_obj.apply(filtered_raw)
            else:
                print(f"⚠️ Filter '{filter_name}' not found, skipping")
                
        return filtered_raw
        
    def apply_single_filter(self, raw, filter_name):
        """Apply a single filter"""
        if filter_name in self.filters:
            return self.filters[filter_name].apply(raw)
        else:
            print(f"⚠️ Filter '{filter_name}' not found")
            return raw
            
    def get_filter(self, name):
        """Get a specific filter"""
        return self.filters.get(name)
        
    def list_filters(self):
        """List all available filters"""
        return list(self.filters.keys())
        
    def get_filter_chain(self):
        """Get current filter chain"""
        return self.filter_chain.copy()
        
    def create_default_chain(self):
        """Create a default filter chain"""
        # Add standard filters
        self.add_bandpass_filter('bandpass', l_freq=0.1, h_freq=40.0)
        self.add_notch_filter('notch_50', freqs=50.0)
        
        # Set default chain
        self.set_filter_chain(['bandpass', 'notch_50'])
