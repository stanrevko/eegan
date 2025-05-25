# EEG Analysis Application

## 🚀 How to Start the Script

### Quick Start (GUI Application Ready!)
```bash
# Navigate to project directory
cd /Users/stanrevko/projects/eegan

# Activate virtual environment
source venv/bin/activate

# Run the EEG Analysis Application
python main.py
```

### First Time Setup
```bash
# 1. Navigate to project directory
cd /Users/stanrevko/projects/eegan

# 2. Create virtual environment (if not already created)
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python main.py
```

### Testing Individual Components
```bash
# Test EEG loading and filtering (command line)
python test_processor.py

# Test file loading only
python eeg/loader.py
```

---

## 📋 Application Features

### 🎯 Current Working Features
- **📁 File Browser**: Browse and select EEG files (.edf format)
- **🔧 Signal Filtering**: Automatic 0.1Hz - 40Hz bandpass filter
- **🧠 EEG Visualization**: Multi-channel signal plotting (up to 10 channels)
- **⚖️ Scale Control**: Adjustable amplitude scaling (50-500 μV)
- **⏱️ Time Window**: Configurable time display (5-60 seconds)
- **📊 Real-time Display**: Interactive signal visualization with pyqtgraph
- **🔄 Background Loading**: Non-blocking file loading with progress indication
- **ℹ️ File Information**: Channel count, sampling rate, duration display

### 🚧 Planned Features (Future Updates)
- [ ] Alpha Power Analysis (8-13Hz sliding windows)
- [ ] Full Spectrum Power Display
- [ ] Signal Annotation Tools
- [ ] Export Functionality
- [ ] Advanced Filtering Options
- [ ] Signal Quality Assessment

## 🏗️ Project Structure

```
eegan/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                   # ✅ Main application entry point
├── test_processor.py         # Test script for signal processing
├── venv/                     # Virtual environment
├── eeg_data/                 # EEG files directory
│   ├── background-1m.edf
│   ├── background-2m.edf
│   ├── biofeed-1m.edf
│   └── ... (other EDF files)
├── eeg/                      # EEG processing modules
│   ├── __init__.py
│   ├── loader.py            # ✅ EEG file loading (MNE)
│   ├── processor.py         # ✅ Signal filtering and preprocessing
│   └── analyzer.py          # 🚧 Spectral analysis (planned)
└── gui/                      # GUI components
    ├── __init__.py
    ├── main_window.py       # ✅ Main application window
    └── file_browser.py      # 🚧 Enhanced file browser (planned)
```

## 🧠 EEG Data

**Location**: `/Users/stanrevko/projects/eegan/eeg_data/`

**Available Files**:
- `background-1m.edf`, `background-2m.edf`, `background-3f.edf`, `background-4f.edf`
- `biofeed-1m.edf`, `biofeed-2m.edf`, `biofeed-3f.edf`, `biofedd-4f.edf`

**File Specifications**:
- Format: European Data Format (.edf)
- Channels: 21 EEG electrodes
- Sampling Rate: 500 Hz
- Duration: ~1-10 minutes per file
- Channel Names: Standard 10-20 system (Fp1, Fp2, F3, F4, F7, etc.)

## 🖥️ GUI Interface

### Left Panel - File Browser
- **📁 File List**: All available EDF files in your data directory
- **🔧 Filter Status**: Shows active 0.1-40Hz bandpass filter
- **⚖️ Scale Control**: Dropdown for signal amplitude (50, 100, 200, 500 μV)
- **⏱️ Time Window**: Choose display duration (5, 10, 30, 60 seconds)
- **📂 Load Button**: Load selected file with progress indication

### Right Panel - EEG Visualization
- **🧠 Signal Display**: Real-time multi-channel EEG plotting
- **📊 Channel View**: First 10 channels displayed with color coding
- **📈 Interactive Plot**: Zoom, pan, and scale functionality
- **ℹ️ File Information**: Displays loaded file details and statistics

### How to Use
1. **Select File**: Click on any EDF file in the left panel
2. **Load File**: Click "📂 Load Selected File" button
3. **View Signals**: EEG channels appear in the right panel
4. **Adjust View**: Use Scale and Time Window controls
5. **Explore**: Try different files and settings

## 🔧 Technical Requirements

### Dependencies
- **mne >= 1.5.0**: EEG data processing and analysis
- **PyQt5 >= 5.15.0**: GUI framework
- **pyqtgraph >= 0.13.0**: Real-time plotting
- **numpy >= 1.21.0**: Numerical computations
- **matplotlib >= 3.5.0**: Additional plotting support
- **scipy >= 1.9.0**: Signal processing

### System Requirements
- Python 3.8+
- macOS/Linux/Windows
- 4GB+ RAM (for processing EEG data)
- Display resolution: 1400x800 minimum recommended

## 🧪 Testing & Validation

### Application Testing
```bash
# Run the full GUI application
python main.py

# Expected: PyQt5 window opens with file browser and plot area
```

### Component Testing
```bash
# Test signal processing pipeline
python test_processor.py

# Expected output:
# ✅ File loaded successfully
# 📊 Signal statistics (before/after filtering)
# 🔧 0.1-40Hz bandpass filter applied
# Range reduction indicating noise removal
```

### Individual Module Testing
```bash
# Test EEG file loading
python eeg/loader.py

# Test in Python console
python -c "from eeg.loader import EEGLoader; from eeg.processor import EEGProcessor; print('✅ All modules working!')"
```

## 📊 Signal Processing Pipeline

1. **File Selection**: User selects EDF file from browser
2. **Background Loading**: File loads in separate thread (non-blocking)
3. **Automatic Filtering**: 0.1-40Hz bandpass filter applied
4. **Data Conversion**: Signals converted to microvolts (μV)
5. **Multi-channel Display**: First 10 channels plotted with color coding
6. **Interactive Controls**: Real-time scale and time window adjustment

## 🎯 Development Status

### ✅ Completed (Fully Working)
- [x] Project structure and virtual environment
- [x] EEG file loading with MNE-Python integration
- [x] Signal filtering (0.1-40Hz bandpass)
- [x] **PyQt5 GUI application with file browser**
- [x] **Real-time EEG signal visualization**
- [x] **Interactive scale and time controls**
- [x] **Background file loading with progress**
- [x] **Multi-channel signal display**
- [x] **File information and statistics**

### 🚧 Future Enhancements
- [ ] Alpha power analyzer (8-13Hz sliding windows)
- [ ] Power spectrum frequency analysis
- [ ] Signal annotation and marking tools
- [ ] Data export functionality (CSV, images)
- [ ] Advanced filtering options
- [ ] Signal quality indicators
- [ ] Multiple file comparison
- [ ] Configuration settings

## 🐛 Troubleshooting

### Common Issues

**GUI Won't Start**:
```bash
# Check virtual environment
source venv/bin/activate
python --version

# Reinstall PyQt5 if needed
pip install --force-reinstall PyQt5
```

**"No EDF files found"**:
- Verify files are in `/Users/stanrevko/projects/eegan/eeg_data/`
- Check file permissions: `ls -la eeg_data/`
- Ensure files have `.edf` extension

**Import Errors**:
```bash
# Make sure you're in the project directory
cd /Users/stanrevko/projects/eegan

# Activate virtual environment
source venv/bin/activate

# Check installation
pip list | grep -E "(mne|PyQt5|pyqtgraph)"
```

**Plot Display Issues**:
- Try different scale settings (50-500 μV)
- Adjust time window (5-60 seconds)
- Check if file loaded successfully (status bar message)

## 🚀 Performance Notes

- **Loading Time**: 2-5 seconds per EDF file (background loading)
- **Memory Usage**: ~100-200MB per loaded file
- **Display**: Smooth real-time plotting up to 10 channels
- **Filtering**: Real-time 0.1-40Hz bandpass processing

## 📝 Usage Examples

### Basic Workflow
```bash
# 1. Start application
python main.py

# 2. Select "background-1m.edf" from file list
# 3. Click "Load Selected File"
# 4. Wait for loading progress
# 5. View filtered EEG signals
# 6. Adjust scale to 100 μV if signals are too small
# 7. Try 30-second time window for longer view
```

### Comparing Files
```bash
# Load different files to compare:
# - background files (resting state)
# - biofeed files (active tasks)
# Notice differences in signal patterns and amplitudes
```

---

## 📧 Contact & Development

This is a working EEG analysis application built with:
- **Backend**: MNE-Python for signal processing
- **Frontend**: PyQt5 + pyqtgraph for real-time visualization
- **Architecture**: Modular design for easy extension

**Ready for immediate use** - select files, view signals, and explore your EEG data!

**Last Updated**: May 25, 2025 - Minimal GUI Version Complete ✅
