"""
Enhanced EEG File Loader Module
Handles loading EEG files from both EDF and TXT formats
"""

import mne
import numpy as np
import pandas as pd
import os
from pathlib import Path
from datetime import datetime, timedelta


class EEGLoader:
    def __init__(self):
        self.raw = None
        self.file_path = None
        self.file_type = None
        
    def load_file(self, file_path):
        """
        Load an EEG file (auto-detect format: EDF or TXT)
        
        Args:
            file_path (str): Path to the EEG file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.edf':
            return self.load_edf(file_path)
        elif file_extension == '.txt':
            return self.load_txt(file_path)
        else:
            print(f"❌ Unsupported file format: {file_extension}")
            print("Supported formats: .edf, .txt")
            return False
    
    def load_edf(self, file_path):
        """
        Load an EDF file using MNE
        
        Args:
            file_path (str): Path to the EDF file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            print(f"Loading EDF file: {file_path}")
            
            # Load the EDF file
            self.raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
            self.file_path = file_path
            self.file_type = 'EDF'
            
            print("✅ EDF file loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading EDF file: {e}")
            self.raw = None
            self.file_path = None
            self.file_type = None
            return False
    
    def load_txt(self, file_path):
        """
        Load a TXT file with EEG data
        Expected format: time_column (hh:mm:ss.mmm) + channel columns
        
        Args:
            file_path (str): Path to the TXT file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            print(f"Loading TXT file: {file_path}")
            
            # Read the file line by line to handle trailing tabs properly
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if len(lines) < 2:
                print("❌ TXT file too short (need at least header + data)")
                return False
            
            # Parse header line and remove trailing tabs/spaces
            header_line = lines[0].strip()
            columns = [col.strip() for col in header_line.split('	') if col.strip()]
            
            if len(columns) < 2:
                print("❌ TXT file must have at least 2 columns (time + channel)")
                return False
            
            # First column is time, rest are channels
            time_col = columns[0]
            channel_names = columns[1:]
            
            print(f"📊 Found {len(channel_names)} channels: {channel_names}")
            
            # Parse data lines
            time_values = []
            channel_data = [[] for _ in channel_names]
            
            for line_num, line in enumerate(lines[1:], 2):  # Start from line 2
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                # Split by tab and remove empty fields (from trailing tabs)
                fields = [field.strip() for field in line.split('	') if field.strip()]
                
                if len(fields) < len(columns):
                    print(f"   ⚠️  Line {line_num}: Expected {len(columns)} fields, got {len(fields)} - skipping")
                    continue
                
                try:
                    # Parse time (first field)
                    time_str = fields[0]
                    if ':' in time_str:
                        parts = time_str.split(':')
                        if len(parts) >= 3:
                            hours = float(parts[0])
                            minutes = float(parts[1])
                            seconds = float(parts[2])
                            total_seconds = hours * 3600 + minutes * 60 + seconds
                        else:
                            minutes = float(parts[0])
                            seconds = float(parts[1])
                            total_seconds = minutes * 60 + seconds
                    else:
                        total_seconds = float(time_str)
                    
                    time_values.append(total_seconds)
                    
                    # Parse channel values
                    for i, ch_name in enumerate(channel_names):
                        field_idx = i + 1  # Skip time field
                        if field_idx < len(fields):
                            try:
                                value = float(fields[field_idx])
                                channel_data[i].append(value)
                            except ValueError:
                                print(f"   ⚠️  Line {line_num}: Invalid value '{fields[field_idx]}' for channel {ch_name}")
                                channel_data[i].append(0.0)  # Fill with 0
                        else:
                            channel_data[i].append(0.0)  # Missing value, fill with 0
                            
                except (ValueError, IndexError) as e:
                    print(f"   ⚠️  Line {line_num}: Error parsing - {e}")
                    continue
            
            # Validate data
            if not time_values:
                print("❌ No valid time values found")
                return False
            
            valid_channels = []
            valid_channel_data = []
            
            for i, ch_name in enumerate(channel_names):
                ch_data = channel_data[i]
                if len(ch_data) == len(time_values):
                    valid_channels.append(ch_name)
                    valid_channel_data.append(np.array(ch_data))
                    print(f"   ✅ Channel {ch_name}: {len(ch_data)} samples")
                else:
                    print(f"   ⚠️  Skipping channel {ch_name}: {len(ch_data)} samples vs {len(time_values)} time points")
            
            if not valid_channel_data:
                print("❌ No valid channel data found")
                return False
            
            # Convert to numpy array (channels x samples)
            data_array = np.array(valid_channel_data)
            time_array = np.array(time_values)
            
            # Calculate sampling rate
            if len(time_values) > 1:
                time_diffs = np.diff(time_array)
                avg_time_diff = np.mean(time_diffs[time_diffs > 0])  # Ignore zero diffs
                sampling_rate = 1.0 / avg_time_diff if avg_time_diff > 0 else 500.0
            else:
                sampling_rate = 500.0  # Default sampling rate
            
            print(f"📈 Calculated sampling rate: {sampling_rate:.2f} Hz")
            
            # Create MNE Info object
            info = mne.create_info(
                ch_names=valid_channels,
                sfreq=sampling_rate,
                ch_types="eeg"
            )
            
            # Create Raw object from numpy array
            self.raw = mne.io.RawArray(data_array, info, verbose=False)
            self.file_path = file_path
            self.file_type = "TXT"
            
            print(f"✅ TXT file loaded successfully! ({len(valid_channels)} channels, {len(time_values)} samples)")
            return True
            
        except Exception as e:
            print(f"❌ Error loading TXT file: {e}")
            print(f"   File: {file_path}")
            self.raw = None
            self.file_path = None
            self.file_type = None
            return False
            
            # First column should be time, rest are channels
            time_col = df.columns[0]
            channel_names = df.columns[1:].tolist()
            
            print(f"📊 Found {len(channel_names)} channels: {channel_names}")
            
            # Convert time column to seconds
            time_values = self._parse_time_column(df.iloc[:, 0])
            
            # Extract channel data
            channel_data = []
            valid_channels = []
            
            for i, ch_name in enumerate(channel_names):
                col_idx = i + 1  # Skip time column
                if col_idx < len(df.columns):
                    # Get channel data and convert to numeric
                    ch_data = pd.to_numeric(df.iloc[:, col_idx], errors="coerce")
                    
                    # Check for valid data (at least 50% non-NaN)
                    valid_ratio = ch_data.notna().sum() / len(ch_data)
                    
                    if valid_ratio > 0.5:
                        # Fill remaining NaN values with 0
                        channel_data.append(ch_data.fillna(0).values)
                        valid_channels.append(ch_name)
                        print(f"   ✅ Channel {ch_name}: {valid_ratio:.1%} valid data")
                    else:
                        print(f"   ⚠️  Skipping channel {ch_name} ({valid_ratio:.1%} valid data - need >50%)")
                else:
                    print(f"   ❌ Column index {col_idx} not found for channel {ch_name}")
            
            if not channel_data:
                print("❌ No valid channel data found")
                # Debug information
                print(f"   📊 DataFrame shape: {df.shape}")
                print(f"   📋 Column names: {df.columns.tolist()}")
                print(f"   🔢 Sample values from column 1:")
                if len(df.columns) > 1:
                    sample_vals = df.iloc[:5, 1]
                    print(f"      {sample_vals.tolist()}")
                    print(f"   🧪 Data types: {df.dtypes.tolist()}")
                return False
            
            # Convert to numpy array (channels x samples)
            data_array = np.array(channel_data)
            
            # Calculate sampling rate
            if len(time_values) > 1:
                time_diffs = np.diff(time_values)
                avg_time_diff = np.mean(time_diffs[time_diffs > 0])  # Ignore zero diffs
                sampling_rate = 1.0 / avg_time_diff if avg_time_diff > 0 else 500.0  # Default 500 Hz
            else:
                sampling_rate = 500.0  # Default sampling rate
            
            print(f"📈 Calculated sampling rate: {sampling_rate:.2f} Hz")
            
            # Create MNE Info object
            info = mne.create_info(
                ch_names=valid_channels,
                sfreq=sampling_rate,
                ch_types="eeg"
            )
            
            # Create Raw object from numpy array
            self.raw = mne.io.RawArray(data_array, info, verbose=False)
            self.file_path = file_path
            self.file_type = "TXT"
            
            print(f"✅ TXT file loaded successfully! ({len(valid_channels)} channels, {len(time_values)} samples)")
            return True
            
        except Exception as e:
            print(f"❌ Error loading TXT file: {e}")
            print(f"   File: {file_path}")
            # Additional debug info
            try:
                df_debug = pd.read_csv(file_path, sep="	", nrows=5)
                print(f"   🔍 Debug - Raw DataFrame shape: {df_debug.shape}")
                print(f"   🔍 Debug - Raw columns: {df_debug.columns.tolist()}")
                print(f"   🔍 Debug - First few rows:")
                print(df_debug.head())
            except:
                pass
            self.raw = None
            self.file_path = None
            self.file_type = None
            return False
            
            # Parse header to get channel names
            header_line = lines[0].strip()
            columns = header_line.split('\t')
            
            if len(columns) < 2:
                print("❌ TXT file must have at least 2 columns (time + channel)")
                return False
            
            # First column should be time, rest are channels
            time_col = columns[0]
            channel_names = columns[1:]
            
            print(f"📊 Found {len(channel_names)} channels: {channel_names}")
            
            # Read the data
            df = pd.read_csv(file_path, sep='\t', skiprows=0)
            
            # Convert time column to seconds
            time_values = self._parse_time_column(df.iloc[:, 0])
            
            # Extract channel data
            channel_data = []
            valid_channels = []
            
            for i, ch_name in enumerate(channel_names, 1):
                if i < len(df.columns):
                    # Convert to numeric, handling any non-numeric values
                    ch_data = pd.to_numeric(df.iloc[:, i], errors='coerce')
                    
                    # Skip channels with too many NaN values
                    if ch_data.notna().sum() / len(ch_data) > 0.5:  # At least 50% valid data
                        channel_data.append(ch_data.fillna(0).values)  # Fill NaN with 0
                        valid_channels.append(ch_name)
                    else:
                        print(f"⚠️  Skipping channel {ch_name} (too many invalid values)")
            
            if not channel_data:
                print("❌ No valid channel data found")
                return False
            
            # Convert to numpy array (channels x samples)
            data_array = np.array(channel_data)
            
            # Calculate sampling rate
            if len(time_values) > 1:
                time_diffs = np.diff(time_values)
                avg_time_diff = np.mean(time_diffs[time_diffs > 0])  # Ignore zero diffs
                sampling_rate = 1.0 / avg_time_diff if avg_time_diff > 0 else 500.0  # Default 500 Hz
            else:
                sampling_rate = 500.0  # Default sampling rate
            
            print(f"📈 Calculated sampling rate: {sampling_rate:.2f} Hz")
            
            # Create MNE Info object
            info = mne.create_info(
                ch_names=valid_channels,
                sfreq=sampling_rate,
                ch_types='eeg'
            )
            
            # Create Raw object from numpy array
            self.raw = mne.io.RawArray(data_array, info, verbose=False)
            self.file_path = file_path
            self.file_type = 'TXT'
            
            print(f"✅ TXT file loaded successfully! ({len(valid_channels)} channels, {len(time_values)} samples)")
            return True
            
        except Exception as e:
            print(f"❌ Error loading TXT file: {e}")
            print(f"   File: {file_path}")
            self.raw = None
            self.file_path = None
            self.file_type = None
            return False
    
    def _parse_time_column(self, time_series):
        """
        Parse time column from various formats to seconds
        Supports: hh:mm:ss.mmm, seconds, etc.
        
        Args:
            time_series: Pandas series with time values
            
        Returns:
            numpy array: Time values in seconds
        """
        time_values = []
        
        for time_str in time_series:
            try:
                time_str = str(time_str).strip()
                
                # Try to parse as hh:mm:ss.mmm format
                if ':' in time_str:
                    parts = time_str.split(':')
                    if len(parts) >= 3:
                        hours = float(parts[0])
                        minutes = float(parts[1])
                        seconds = float(parts[2])
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                        time_values.append(total_seconds)
                    else:
                        # Try mm:ss.mmm format
                        minutes = float(parts[0])
                        seconds = float(parts[1])
                        total_seconds = minutes * 60 + seconds
                        time_values.append(total_seconds)
                else:
                    # Try to parse as direct seconds
                    time_values.append(float(time_str))
                    
            except (ValueError, IndexError):
                # If parsing fails, use index as time (assuming regular sampling)
                time_values.append(len(time_values) * 0.002)  # 500 Hz default
        
        return np.array(time_values)
    
    def get_file_info(self):
        """
        Get basic information about the loaded EEG file
        
        Returns:
            dict: File information or None if no file loaded
        """
        if self.raw is None:
            return None
        
        info = {
            'filename': os.path.basename(self.file_path),
            'file_type': self.file_type,
            'n_channels': self.raw.info['nchan'],
            'sampling_rate': self.raw.info['sfreq'],
            'duration': self.raw.times[-1],  # Duration in seconds
            'channel_names': self.raw.ch_names,
            'n_samples': len(self.raw.times)
        }
        
        return info
    
    def print_file_info(self):
        """Print formatted file information"""
        info = self.get_file_info()
        if info is None:
            print("No file loaded")
            return
        
        print("\n" + "="*50)
        print("📄 EEG FILE INFORMATION")
        print("="*50)
        print(f"File: {info['filename']}")
        print(f"Format: {info['file_type']}")
        print(f"Channels: {info['n_channels']}")
        print(f"Sampling Rate: {info['sampling_rate']:.2f} Hz")
        print(f"Duration: {info['duration']:.2f} seconds ({info['duration']/60:.2f} minutes)")
        print(f"Total Samples: {info['n_samples']:,}")
        print(f"Channel Names: {', '.join(info['channel_names'][:5])}{'...' if len(info['channel_names']) > 5 else ''}")
        print("="*50)
    
    def load_multiple_txt_files(self, file_paths):
        """
        Load multiple TXT files and combine them as multi-channel data
        Useful when each channel is in a separate file
        
        Args:
            file_paths (list): List of TXT file paths
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            print(f"Loading {len(file_paths)} TXT files as multi-channel data...")
            
            all_data = []
            all_channels = []
            time_values = None
            sampling_rate = None
            
            for i, file_path in enumerate(file_paths):
                print(f"  Processing file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
                
                # Create temporary loader for this file
                temp_loader = EEGLoader()
                if not temp_loader.load_txt(file_path):
                    print(f"    ❌ Failed to load {file_path}")
                    continue
                
                # Get data from this file
                data, times = temp_loader.raw.get_data(return_times=True)
                
                # Use first file's timing as reference
                if time_values is None:
                    time_values = times
                    sampling_rate = temp_loader.raw.info['sfreq']
                
                # Add all channels from this file
                for ch_idx, ch_name in enumerate(temp_loader.raw.ch_names):
                    # Create unique channel name if multiple files have same channel names
                    unique_ch_name = f"{ch_name}_{i+1}" if len(file_paths) > 1 else ch_name
                    all_channels.append(unique_ch_name)
                    all_data.append(data[ch_idx])
            
            if not all_data:
                print("❌ No valid data found in any files")
                return False
            
            # Combine all channel data
            combined_data = np.array(all_data)
            
            # Create MNE Info object
            info = mne.create_info(
                ch_names=all_channels,
                sfreq=sampling_rate,
                ch_types='eeg'
            )
            
            # Create Raw object
            self.raw = mne.io.RawArray(combined_data, info, verbose=False)
            self.file_path = f"Multiple TXT files ({len(file_paths)} files)"
            self.file_type = 'TXT_Multi'
            
            print(f"✅ Combined TXT files loaded! ({len(all_channels)} channels total)")
            return True
            
        except Exception as e:
            print(f"❌ Error loading multiple TXT files: {e}")
            return False


def test_loader(eeg_data_path="/Users/stanrevko/projects/eegan/eeg_data"):
    """
    Test the enhanced EEG loader with both EDF and TXT files
    
    Args:
        eeg_data_path (str): Path to the directory containing EEG files
    """
    print("🧠 Testing Enhanced EEG Loader...")
    
    # Get list of supported files
    supported_files = []
    if os.path.exists(eeg_data_path):
        all_files = os.listdir(eeg_data_path)
        supported_files = [f for f in all_files if f.endswith(('.edf', '.txt'))]
    
    if not supported_files:
        print(f"❌ No supported EEG files found in {eeg_data_path}")
        print("Supported formats: .edf, .txt")
        return
    
    print(f"📁 Found {len(supported_files)} supported files:")
    edf_files = [f for f in supported_files if f.endswith('.edf')]
    txt_files = [f for f in supported_files if f.endswith('.txt')]
    
    if edf_files:
        print(f"  EDF files ({len(edf_files)}): {', '.join(edf_files[:3])}{'...' if len(edf_files) > 3 else ''}")
    if txt_files:
        print(f"  TXT files ({len(txt_files)}): {', '.join(txt_files[:3])}{'...' if len(txt_files) > 3 else ''}")
    
    # Test loading the first available file
    test_file = os.path.join(eeg_data_path, supported_files[0])
    print(f"\n🔍 Testing with first file: {supported_files[0]}")
    
    loader = EEGLoader()
    if loader.load_file(test_file):
        loader.print_file_info()
        
        # Test getting raw data
        data, times = loader.raw.get_data(return_times=True)
        print(f"\n📊 Data shape: {data.shape} (channels x samples)")
        print(f"⏱️  Time range: {times[0]:.3f}s to {times[-1]:.3f}s")
        print(f"📈 Sample values from first channel: {data[0][:5]}")
        
        return loader
    else:
        print("❌ Failed to load the test file")
        return None


if __name__ == "__main__":
    # Run the test when this module is executed directly
    test_loader()
