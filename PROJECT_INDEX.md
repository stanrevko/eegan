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
| `gui/main_window.py` | **Main Application Window** - Simplified layout with unified tabbed analysis interface and **Analysis Window controls** | Change overall layout, modify Analysis Window timeframe controls |
| `gui/main_window_simple.py` | **Simplified Main Window** - Alternative simpler interface | Update simple interface variant |

### Analysis Interface (`gui/analysis/`) - **Primary Analysis Hub**
| File | Purpose | When to Modify |
|------|---------|----------------|
| `gui/analysis/tabbed_analysis_panel.py` | **Main Analysis Interface** - Clean tabbed analysis container with 4 analysis tools and **timeframe synchronization** | Add new tabs, modify tab behavior, change timeframe handling |
| `gui/analysis/band_selector.py` | **Band Selection Widget** - Frequency band dropdown (used per-tab) | Add new bands, change band colors, modify selection UI |
| `gui/analysis/channel_selector.py` | **Channel Selection Widget** - EEG channel dropdown (used per-tab) | Add channel features, modify channel display |
| `gui/analysis/eeg_timeline_analysis.py` | **EEG Timeline Tab** - 📺 **PRIMARY** Full EEG signal visualization (First Tab) with **Analysis Window X-axis control** | Modify signal display, add timeline features, change timeframe handling |
| `gui/analysis/band_spikes.py` | **Band Spikes Analysis** - Statistical spike detection with integrated controls and **Analysis Window X-axis control** | Modify spike detection algorithm, change threshold logic, add statistical features |
| `gui/analysis/all_bands_power.py` | **Multi-Band Comparison** - All bands comparative plot | Add band comparison features, modify normalization |
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
| `tests/test_tabbed_analysis.
