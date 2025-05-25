"""
Settings Management
Handles user preferences and application configuration
"""

import json
import os
from typing import Any, Dict


class AppSettings:
    """Manages application settings and user preferences"""
    
    def __init__(self, settings_file: str = "eeg_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            'eeg_data_folder': '/Users/stanrevko/projects/eegan/eeg_data',
            'recent_folders': [],
            'sidebar_visible': True,
            'eeg_scale': 200,  # μV
            'eeg_window_size': 10,  # seconds
            'active_frequency_band': 'Alpha',
            'visible_channels': 'all',  # 'all' or list of channel indices
            'channel_spacing': 3,
            'window_geometry': {'x': 50, 'y': 50, 'width': 1600, 'height': 1000},
            'plot_colors': ['#00bfff', '#ff4444', '#44ff44', '#ff8800', '#8844ff', '#ff44ff', '#ffff44', '#88ffff']
        }
        self.settings = self.load_settings()
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or use defaults"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                # Merge with defaults to handle new settings
                settings = self.default_settings.copy()
                settings.update(loaded)
                return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
            
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
        
    def set(self, key: str, value: Any):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save_settings()
        
    def add_recent_folder(self, folder_path: str):
        """Add folder to recent folders list"""
        recent = self.settings.get('recent_folders', [])
        if folder_path in recent:
            recent.remove(folder_path)
        recent.insert(0, folder_path)
        recent = recent[:5]  # Keep only 5 recent folders
        self.set('recent_folders', recent)
        
    def get_recent_folders(self) -> list:
        """Get list of recent folders"""
        return self.settings.get('recent_folders', [])
