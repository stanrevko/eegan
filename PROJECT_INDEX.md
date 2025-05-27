# 🗂️ EEG Analysis Suite - Project File Index

*This index helps LLMs and developers quickly locate files for specific functionality updates.*

## 📁 Root Level Files

| File | Purpose | When to Modify |
|------|---------|----------------|
| `main.py` | **Application Entry Point** - Launches GUI application | Add new startup options, change application flow |
| `requirements.txt` | **Dependencies** - Python package requirements | Add new libraries, update versions |
| `README.md` | **Documentation** - Project overview and usage guide | Update features, installation instructions |
| `PROJECT_INDEX.md` | **File Index** - This navigation guide | Add new files, restructure project |

## 🧠 Core EEG Processing (`eeg/`)

### Main Processing
| File | Purpose | When to Modify |
|------|---------|----------------|
| `eeg/processor.py` | **EEG Data Processor** - Core data loading and processing | Fix data loading issues, add new file formats |
| `eeg/frequency_bands.py` | **Band Definitions** - Frequency ranges and band info | Modify frequency ranges, add new bands |

### Analysis Algorithms (`eeg/analysis/`)
| File | Purpose | When to Modify |
|------|---------|----------------|
| `eeg/analysis/power_analyzer.py` | **Power Analysis** - Band power calculations and algorithms | Improve power calculation methods, add new analysis types |
| `eeg/analysis/__init__.py` | **Analysis Module** - Exports analysis components | Add new analysis classes |

### Signal Filtering (`eeg/filters/`)
| File | Purpose | When to Modify |
|------|---------|----------------|
| `eeg/filters/bandpass_filter.py` | **Bandpass Filtering** - Butterworth filter implementations | Change filter parameters, add new filter types |
| `eeg/filters/__init__.py` | **Filter Module** - Exports filter components | Add new filter classes |

## 🖥️ User Interface (`gui/`)

### Main Windows
| File | Purpose | When to Modify |
|------|---------|----------------|
| `gui/main_window.py` | **Main Application Window** - Simplified layout with unified tabbed analysis interface | Change overall layout, modify window behavior |
| `gui/main_window_simple.py` | **Simplified Main Window** - Alternative simpler interface | Update simple interface variant |

### Analysis Interface (`gui/analysis/`) - **Primary Analysis Hub**
| File | Purpose | When to Modify |
|------|---------|----------------|
| `gui/analysis/tabbed_analysis_panel.py` | **Main Analysis Interface** - Clean tabbed analysis container with 5 analysis tools and individual tab selectors | Add new tabs, modify tab behavior, change layout |
| `gui/analysis/band_selector.py` | **Band Selection Widget** - Frequency band dropdown (now used per-tab) | Add new bands, change band colors, modify selection UI |
| `gui/analysis/channel_selector.py` | **Channel Selection Widget** - EEG channel dropdown (now used per-tab) | Add channel features, modify channel display |
| `gui/analysis/power_plot.py` | **Band Power Visualization** - Single band power plotting with integrated controls | Improve power plot features, add plot options |
| `gui/analysis/band_spikes.py` | **Spike Detection Tool** - Spike analysis with integrated controls | Modify spike detection algorithm, change threshold logic |
| `gui/analysis/all_bands_power.py` | **Multi-Band Comparison** - All bands comparative plot | Add band comparison features, modify normalization |
| `gui/analysis/eeg_timeline_analysis.py` | **EEG Timeline Tab** - 📺 **PRIMARY** Full EEG signal visualization (First Tab) | Modify signal display, add timeline features, change channel visibility |
| `gui/analysis/dfa_analysis.py` | **DFA Analysis Tab** - Detrended fluctuation analysis | Add new DFA features, modify analysis parameters |
| `gui/analysis/analysis_controls.py` | **Analysis Parameters** - Window size, step size controls (integrated into Band Power tab) | Add new analysis parameters, modify control ranges |
| `gui/analysis/__init__.py` | **Analysis UI Module** - Exports all analysis UI components | Add new analysis UI classes |

### Plotting Components (`gui/plots/`)
| File | Purpose | When to Modify |
|------|---------|----------------|
| `gui/plots/eeg_plot_widget.py` | **EEG Plot Widget** - ⚠️ **LEGACY** - Consider using EEGTimelineAnalysis instead | Migrate features to EEGTimelineAnalysis tab |
| `gui/plots/timeline_controls.py` | **Timeline Navigation** - Time navigation controls | Modify timeline behavior, add navigation features |
| `gui/plots/channel_controls.py` | **Channel Management** - Channel visibility and selection | Change channel display options, add channel features |
| `gui/plots/__init__.py` | **Plots Module** - Exports plotting components | Add new plot classes |

### UI Controls (`gui/controls/`)
| File | Purpose | When to Modify |
|------|---------|----------------|
| `gui/controls/shortcuts_manager.py` | **Keyboard Shortcuts** - Hotkey management | Add new shortcuts, modify key bindings |
| `gui/controls/toolbar_manager.py` | **Toolbar Management** - Toolbar creation and management | Add new toolbar buttons, modify toolbar layout |
| `gui/controls/__init__.py` | **Controls Module** - Exports control components | Add new control classes |

### Window Management (`gui/windows/`)
| File | Purpose | When to Modify |
|------|---------|----------------|
| `gui/windows/main_window.py` | **Window Framework** - Base window structure | Modify window framework, add window features |
| `gui/windows/layout_manager.py` | **Layout Management** - UI layout coordination | Change layout algorithms, add layout options |
| `gui/windows/window_manager.py` | **Window State** - Window state management | Modify window state handling, add state features |
| `gui/windows/__init__.py` | **Windows Module** - Exports window components | Add new window classes |

### Threading (`gui/threading/`)
| File | Purpose | When to Modify |
|------|---------|----------------|
| `gui/threading/thread_manager.py` | **Thread Coordination** - Multi-threading management | Fix threading issues, add new background tasks |
| `gui/threading/eeg_load_thread.py` | **EEG Loading Thread** - Background EEG data loading | Improve loading performance, fix loading issues |
| `gui/threading/__init__.py` | **Threading Module** - Exports threading components | Add new thread classes |

### Additional UI Files
| File | Purpose | When to Modify |
|------|---------|----------------|
| `gui/file_panel.py` | **File Browser** - EEG file selection and management | Improve file browser, add file operations |
| `gui/spectrum_panel.py` | **Spectrum Analysis** - Frequency spectrum visualization | Enhance spectrum display, add spectrum features |
| `gui/eeg_timeline_panel.py` | **EEG Timeline Panel** - ⚠️ **DEPRECATED** - Replaced by EEGTimelineAnalysis tab | Remove or migrate remaining features |
| `gui/ui_controls.py` | **General UI Controls** - Common UI components | Add new UI widgets, modify existing controls |

## 🛠️ Utilities (`utils/`)

| File | Purpose | When to Modify |
|------|---------|----------------|
| `utils/settings.py` | **Application Settings** - Configuration management | Add new settings, modify configuration options |
| `utils/ui_helpers.py` | **UI Helper Functions** - Common UI utilities and styling | Add new UI utilities, modify styling functions |
| `utils/__init__.py` | **Utils Module** - Exports utility components | Add new utility classes |

## 🧪 Testing Files

| File | Purpose | When to Modify |
|------|---------|----------------|
| `test_tabbed_analysis.py` | **Tabbed Panel Test** - Test script for tabbed analysis interface | Test new tab features, debug tab issues |
| `test_eeg_timeline_integration.py` | **EEG Timeline Integration Test** - Test script for timeline tab integration | Test timeline tab functionality, debug integration issues |
| `test_analyzer.py` | **Analysis Test** - Test script for analysis algorithms | Test analysis improvements, debug analysis issues |
| `test_gui.py` | **GUI Test** - Test script for GUI components | Test GUI changes, debug UI issues |
| `test_modular.py` | **Modular Test** - Test script for modular components | Test modular architecture, debug component issues |
| `test_processor.py` | **Processor Test** - Test script for EEG processing | Test processing improvements, debug processing issues |

## 📊 Data Directory (`eeg_data/`)

| Purpose | When to Modify |
|---------|----------------|
| **Sample EEG Data** - Contains example EEG files for testing | Add new sample data, update test datasets |

## 🔧 Configuration Files

| File | Purpose | When to Modify |
|------|---------|----------------|
| `eeg_settings.json` | **Application Configuration** - Runtime settings and preferences | Change default settings, add new configuration options |
| `.gitignore` | **Git Exclusions** - Files to ignore in version control | Add new file types to ignore |

---

## 🎯 Quick Reference by Functionality

### 🔍 **Need to modify analysis algorithms?**
- `eeg/analysis/power_analyzer.py` - Core analysis logic
- `gui/analysis/band_spikes.py` - Spike detection algorithm
- `eeg/filters/bandpass_filter.py` - Signal filtering

### 🎨 **Need to change UI appearance?**
- `utils/ui_helpers.py` - Styling and theming
- `gui/analysis/tabbed_analysis_panel.py` - Main clean tabbed analysis interface
- `gui/main_window.py` - Overall simplified window layout

### ⚡ **Need to add new analysis features?**
- `gui/analysis/` - Add new analysis tab or component
- `eeg/analysis/` - Add new analysis algorithm
- `gui/analysis/tabbed_analysis_panel.py` - Integrate new tab into clean interface

### 📊 **Need to modify plotting?**
- `gui/analysis/eeg_timeline_analysis.py` - **PRIMARY** EEG signal display and timeline (First Tab)
- `gui/analysis/power_plot.py` - Power analysis plots (with integrated controls)
- `gui/analysis/all_bands_power.py` - Multi-band plots

### 🔧 **Need to fix data loading issues?**
- `eeg/processor.py` - Core data processing
- `gui/threading/eeg_load_thread.py` - Background loading
- `gui/file_panel.py` - File browser

### 🎛️ **Need to add new controls?**
- `gui/controls/` - Control components
- Individual tabs now have integrated selectors (Band Power, Band Spikes)
- `gui/analysis/eeg_timeline_analysis.py` - Timeline navigation and display controls

### 🔊 **Need to add new frequency bands?**
- `eeg/frequency_bands.py` - Band definitions
- `gui/analysis/band_selector.py` - Band selection UI (used per-tab)
- `gui/analysis/all_bands_power.py` - Multi-band display

### 🧵 **Need to fix threading issues?**
- `gui/threading/thread_manager.py` - Thread coordination
- `gui/threading/eeg_load_thread.py` - EEG loading thread

### ⚙️ **Need to modify application settings?**
- `utils/settings.py` - Settings management
- `eeg_settings.json` - Configuration file
- `gui/main_window.py` - Settings integration

### 📺 **Need to modify EEG signal display?**
- `gui/analysis/eeg_timeline_analysis.py` - **PRIMARY** location for all EEG timeline functionality (First Tab)
- Timeline controls, channel visibility, Y-scale, time navigation
- Signal plotting and interaction

### 🎛️ **Need to modify individual tab controls?**
- `gui/analysis/power_plot.py` - Band Power tab with integrated Channel/Band selectors
- `gui/analysis/band_spikes.py` - Band Spikes tab with integrated Channel/Band selectors
- Each tab now has independent controls instead of global selectors

---

## 🆕 **Recent Architecture Changes**

### ✨ **Sprint 4 - Clean Tabbed Interface (Latest)**

**What Changed:**
- **Moved** EEG Timeline to **first tab position** (primary tab)
- **Relocated** Channel and Band selectors from global header to individual tabs
- **Removed** unnecessary tab borders for cleaner appearance
- **Added** independent selectors to Band Power and Band Spikes tabs
- **Maintained** signal compatibility with main window through relay connections

### 📋 **Current Tab Structure (5 Tabs)**

1. **📺 EEG Timeline** - **FIRST TAB** Full signal display with timeline controls
2. **📊 Band Power** - Individual frequency band analysis **with integrated Channel/Band selectors**
3. **⚡ Band Spikes** - Spike detection **with integrated Channel/Band selectors**
4. **📈 All Bands** - Multi-band comparative visualization  
5. **📊 DFA Analysis** - Detrended fluctuation analysis

### 🔄 **Migration Notes (Sprint 4)**

- **REMOVED**: Global Channel/Band selectors from main tabbed panel header
- **ADDED**: Individual selectors per tab (Band Power, Band Spikes)
- **IMPROVED**: Cleaner interface without unnecessary borders
- **MAINTAINED**: All signal connections through relay system
- **BENEFITS**: Independent tab controls, cleaner UI, better user experience

### ✨ **Sprint 3 - Major UI Enhancements**

**What Changed:**
- **Moved** timeline controls from top to bottom bar
- **Enhanced** EEG Timeline with full controls integration
- **Added** "Select All" and "None" buttons for channel visibility
- **Updated** Y-scale default to 50mV, spacing to 1x
- **Improved** display controls layout (vertical under channel visibility)

---

## 📝 File Naming Conventions

- **snake_case** for all Python files
- **PascalCase** for class names within files
- **Descriptive names** indicating functionality
- **Module `__init__.py`** files for package exports
- **Test files** prefixed with `test_`

## 🔄 Common Update Patterns

1. **Adding new analysis tab**: Modify `gui/analysis/tabbed_analysis_panel.py`
2. **Adding individual tab controls**: Update specific tab files (power_plot.py, band_spikes.py)
3. **Adding new frequency band**: Update `eeg/frequency_bands.py` and `gui/analysis/band_selector.py`
4. **Improving algorithms**: Update relevant files in `eeg/analysis/`
5. **UI improvements**: Update files in `gui/analysis/` (primary location)
6. **EEG display changes**: Modify `gui/analysis/eeg_timeline_analysis.py` (First Tab)
7. **New features**: Often requires updates to multiple related files

## 🏗️ **Current Architecture Summary**

```
Main Window (Simplified)
├── File Panel (Sidebar)
└── Analysis Area (Full)
    └── Clean Tabbed Analysis Panel (5 Tabs - No Borders)
        ├── 📺 EEG Timeline (PRIMARY - First Tab)
        ├── 📊 Band Power (+ Channel/Band Selectors)
        ├── ⚡ Band Spikes (+ Channel/Band Selectors)
        ├── 📈 All Bands
        └── 📊 DFA Analysis
```

This index should help you quickly locate the right files for any modifications! 🎯

---

**Last Updated**: January 2025 - **Version 2.2** (Sprint 4 - Clean Tabbed Interface)
