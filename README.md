# 🧠 EEG Analysis Suite

A comprehensive Python-based application for electroencephalogram (EEG) data analysis with advanced visualization and real-time processing capabilities.

## ✨ Features

### 📊 Core Analysis Tools
- **Multi-Band Analysis**: Alpha, Beta, Theta, Delta, and Gamma frequency bands
- **Real-time Visualization**: Interactive EEG timeline with channel controls
- **Power Spectral Analysis**: Sliding window power calculations
- **Advanced Filtering**: Butterworth bandpass filters for each frequency band

### 🎛️ Clean Tabbed Analysis Interface
- **📺 EEG Timeline**: PRIMARY tab with full signal visualization and timeline controls
- **📊 Band Power**: Enhanced single-band power analysis with integrated channel/band selectors
- **⚡ Band Spikes**: Spike detection with configurable thresholds and integrated controls
- **📈 All Bands**: Comparative visualization of all frequency bands simultaneously
- **📊 DFA Analysis**: Detrended fluctuation analysis

### 🖥️ User Interface
- **Dark Theme**: Professional dark interface optimized for long analysis sessions
- **Clean Design**: Borderless tabs and streamlined controls for maximum space efficiency
- **Interactive Controls**: Channel visibility toggles, Y-axis scaling, timeline navigation
- **File Browser**: Automatic EEG data loading with folder management
- **Individual Tab Controls**: Channel and band selectors integrated directly into relevant tabs

### 📈 Visualization Features
- **Timeline View**: Scrollable EEG signal display with time markers
- **Spectrum Analysis**: Real-time frequency domain visualization
- **Power Plots**: Time-series power analysis for each frequency band
- **Multi-Channel Support**: Independent channel analysis and comparison

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd eegan

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Launch the EEG Analysis Suite
python main.py
```

## 📋 Usage Guide

### Getting Started
1. **Launch Application**: Run `python main.py` to open the main interface
2. **Load Data**: Use the file browser to navigate to your EEG data directory
3. **Select File**: Click on any EEG file to load it automatically
4. **Analyze**: Switch between analysis tabs to explore different perspectives

### Analysis Tabs

#### 📺 EEG Timeline Tab (Primary)
- **First tab position** for immediate access to signal visualization
- View complete EEG signal with full timeline controls
- Adjust channel visibility using "Select All" and "None" buttons
- Control Y-scale (default: 50mV) and spacing (default: 1x)
- Navigate through time using integrated timeline controls

#### 📊 Band Power Tab
- **Integrated Controls**: Channel and Band selectors built into the tab
- Select frequency band using the dropdown selector
- Choose channel for analysis from the channel dropdown
- Adjust analysis window and step size with controls
- View real-time power calculations over time
- Set custom timeframes for focused analysis

#### ⚡ Band Spikes Tab
- **Integrated Controls**: Channel and Band selectors built into the tab
- Choose frequency band and channel for spike analysis
- Adjust detection threshold (1.0x - 5.0x standard deviation)
- Click "Detect Spikes" to identify and mark spike events
- View spike count and timestamps in console

#### 📈 All Bands Tab
- Toggle individual frequency bands using checkboxes
- Compare normalized power levels across all bands
- Identify dominant frequency patterns
- Analyze relative band activity

#### 📊 DFA Analysis Tab
- Perform detrended fluctuation analysis
- Configure analysis parameters
- Visualize scaling relationships

### Interface Features
- **Clean Tab Design**: No unnecessary borders for maximum space efficiency
- **Independent Tab Controls**: Each analysis tab has its own relevant selectors
- **Responsive Layout**: Resizable panels with optimized space allocation
- **Dark Theme**: Professional appearance optimized for extended use

## 🏗️ Architecture

### Project Structure
```
eegan/
├── main.py                 # Application entry point
├── gui/                    # User interface components
│   ├── analysis/          # Analysis panel components
│   │   ├── tabbed_analysis_panel.py  # Main clean tabbed interface
│   │   ├── eeg_timeline_analysis.py  # EEG Timeline (Primary Tab)
│   │   ├── power_plot.py            # Band Power (+ selectors)
│   │   ├── band_spikes.py           # Band Spikes (+ selectors)
│   │   ├── all_bands_power.py       # Multi-band comparison
│   │   └── dfa_analysis.py          # DFA Analysis
│   ├── plots/             # Visualization widgets
│   ├── controls/          # UI control components
│   └── main_window.py     # Main application window
├── eeg/                   # EEG processing core
│   ├── analysis/          # Analysis algorithms
│   ├── filters/           # Signal filtering
│   └── frequency_bands.py # Band definitions
├── utils/                 # Utility functions
└── requirements.txt       # Python dependencies
```

### Key Components
- **EEG Processor**: Core signal processing and data management
- **Power Analyzer**: Frequency band power calculation algorithms
- **Filter Bank**: Butterworth bandpass filters for each frequency band
- **Visualization Engine**: PyQtGraph-based real-time plotting
- **Clean UI Framework**: PyQt5-based modern borderless interface

## 🔧 Technical Details

### Frequency Bands
- **Delta**: 0.5-4 Hz (Deep sleep, unconscious processes)
- **Theta**: 4-8 Hz (REM sleep, meditation, creativity)
- **Alpha**: 8-13 Hz (Relaxed awareness, eyes closed)
- **Beta**: 13-30 Hz (Active thinking, concentration)
- **Gamma**: 30-100 Hz (High-level cognitive functions)

### Analysis Methods
- **Sliding Window Analysis**: Configurable window sizes (1-10 seconds)
- **Power Spectral Density**: Welch's method for power calculation
- **Spike Detection**: Statistical threshold-based detection (mean + n×std)
- **Real-time Processing**: Efficient algorithms for live data analysis

### Signal Processing
- **Sampling Rate**: Adaptive to input data
- **Filtering**: 4th-order Butterworth bandpass filters
- **Artifact Handling**: Robust processing with error handling
- **Memory Management**: Efficient data structures for large datasets

## 🧪 Testing

### Run Tests
```bash
# Test tabbed analysis panel
python test_tabbed_analysis.py

# Test core components
python test_analyzer.py
python test_gui.py
```

### Validation
- Import validation for all components
- Signal connection verification
- UI responsiveness testing
- Analysis algorithm accuracy checks

## 📦 Dependencies

### Core Libraries
- **PyQt5**: GUI framework and widgets
- **PyQtGraph**: High-performance scientific plotting
- **NumPy**: Numerical computing and array operations
- **SciPy**: Scientific computing and signal processing
- **MNE**: EEG/MEG data processing (if available)

### Optional Enhancements
- **Matplotlib**: Additional plotting capabilities
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning algorithms

## 🎯 Use Cases

### Clinical Applications
- **Sleep Studies**: Delta and theta wave analysis
- **Attention Research**: Beta band monitoring
- **Meditation Studies**: Alpha wave tracking
- **Cognitive Load**: Gamma activity assessment

### Research Applications
- **Neurofeedback**: Real-time brain state monitoring
- **BCI Development**: Brain-computer interface research
- **Cognitive Studies**: Attention and focus analysis
- **Sleep Research**: Sleep stage classification

### Educational Use
- **Neuroscience Education**: Interactive EEG exploration
- **Signal Processing**: Hands-on filtering and analysis
- **Data Visualization**: Scientific plotting techniques
- **Brain Physiology**: Understanding brainwave patterns

## 🔄 Recent Updates

### Version 2.2 - Clean Tabbed Interface (Sprint 4)
- **NEW**: EEG Timeline moved to first tab position for primary access
- **NEW**: Channel and Band selectors integrated directly into relevant tabs
- **NEW**: Borderless tab design for cleaner appearance and maximum space
- **IMPROVED**: Independent controls per tab (Band Power, Band Spikes)
- **ENHANCED**: Streamlined user experience with focused workflows
- **MAINTAINED**: Full backward compatibility and signal connections

### Version 2.1 - Major UI Enhancements (Sprint 3)
- **NEW**: Timeline controls moved to bottom bar
- **NEW**: "Select All" and "None" buttons for channel visibility
- **NEW**: Y-scale default set to 50mV, spacing to 1x
- **IMPROVED**: Display controls layout (vertical under channel visibility)
- **ENHANCED**: EEG Timeline integration and functionality

### Version 2.0 - Tabbed Analysis Panel
- **NEW**: Five-tab analysis interface
- **NEW**: Spike detection with configurable thresholds
- **NEW**: Multi-band comparative visualization
- **ENHANCED**: Original band power analysis
- **FIXED**: Recursion errors and signal handling
- **IMPROVED**: User experience and workflow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **MNE-Python**: Inspiration for EEG processing workflows
- **PyQtGraph**: Excellent real-time plotting capabilities
- **Scientific Python Community**: Foundation libraries and tools
- **Neuroscience Community**: Domain knowledge and requirements

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check the documentation and examples
- Review the test scripts for usage patterns

---

*Built with ❤️ for the neuroscience and EEG analysis community*

**Current Version**: 2.2 (Sprint 4 - Clean Tabbed Interface)
