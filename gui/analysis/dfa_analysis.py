"""
DFA Analysis
Detrended Fluctuation Analysis for EEG signals
"""

import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox,
                             QTextEdit, QProgressBar, QCheckBox)
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
import pyqtgraph as pg
from scipy import signal
from sklearn.linear_model import LinearRegression
from utils.ui_helpers import setup_dark_plot


class DFAAnalysis(QWidget):
    """DFA Analysis widget for EEG signals"""
    
    # Signals
    analysis_completed = pyqtSignal(float)  # alpha value
    
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.current_channel = 0
        self.current_data = None
        self.sfreq = 500  # Default sampling frequency
        
        # DFA results
        self.scales = None
        self.fluctuations = None
        self.alpha = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the DFA analysis UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        setup_dark_plot(self.plot_widget, "log₁₀(Scale)", "log₁₀(Fluctuation)")
        
        # Configure plot
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        layout.addWidget(self.plot_widget)
        
    def create_controls(self):
        """Create DFA controls for the sidebar"""
        controls_group = QGroupBox("DFA Controls")
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)
        
        # Add spacer before controls
        controls_layout.addSpacing(20)  # Add 20 pixels of space
        
        # Scale range controls
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Min Scale:"))
        self.min_scale_spin = QSpinBox()
        self.min_scale_spin.setRange(4, 1000)
        self.min_scale_spin.setValue(4)
        scale_layout.addWidget(self.min_scale_spin)
        
        scale_layout.addWidget(QLabel("Max Scale:"))
        self.max_scale_spin = QSpinBox()
        self.max_scale_spin.setRange(4, 1000)
        self.max_scale_spin.setValue(100)
        scale_layout.addWidget(self.max_scale_spin)
        
        scale_layout.addWidget(QLabel("Number of Scales:"))
        self.n_scales_spin = QSpinBox()
        self.n_scales_spin.setRange(4, 50)
        self.n_scales_spin.setValue(20)
        scale_layout.addWidget(self.n_scales_spin)
        
        controls_layout.addLayout(scale_layout)
        
        # Add spacer before analysis button
        controls_layout.addSpacing(10)  # Add 10 pixels of space
        
        # Analysis button
        self.analyze_button = QPushButton("Run DFA Analysis")
        self.analyze_button.clicked.connect(self.run_analysis)
        controls_layout.addWidget(self.analyze_button)
        
        # Add spacer before results
        controls_layout.addSpacing(20)  # Add 20 pixels of space
        
        # Results display
        results_layout = QVBoxLayout()
        
        self.alpha_label = QLabel("DFA α: --")
        self.alpha_label.setStyleSheet("font-weight: bold; color: #ff9800;")
        results_layout.addWidget(self.alpha_label)
        
        self.interpretation_label = QLabel("Interpretation: --")
        results_layout.addWidget(self.interpretation_label)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        results_layout.addWidget(self.stats_text)
        
        controls_layout.addLayout(results_layout)
        controls_group.setLayout(controls_layout)
        return controls_group
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        self.update_data()
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        self.update_data()
        
    def set_timeframe(self, start_time, end_time):
        """Set analysis timeframe"""
        if self.analyzer and self.analyzer.processor:
            try:
                # Limit maximum analysis time to 5 minutes
                max_analysis_time = 300  # 5 minutes in seconds
                if end_time - start_time > max_analysis_time:
                    print(f"📊 DFA: Limiting analysis to {max_analysis_time} seconds for performance")
                    # Center the analysis window around the middle of the selected range
                    mid_time = (start_time + end_time) / 2
                    start_time = mid_time - max_analysis_time / 2
                    end_time = mid_time + max_analysis_time / 2
                
                data, _ = self.analyzer.processor.get_filtered_data(start_time, end_time)
                if data is not None and len(data) > self.current_channel:
                    self.current_data = data[self.current_channel]
                    self.sfreq = self.analyzer.processor.get_sampling_rate()
                    
                    # Update max scale based on data length
                    max_possible = len(self.current_data) // 4
                    self.max_scale_spin.setMaximum(max_possible)
                    if self.max_scale_spin.value() > max_possible:
                        self.max_scale_spin.setValue(max_possible)
                else:
                    print("Error: No valid data available for the selected channel")
                    self.current_data = None
                    
            except Exception as e:
                print(f"Error setting timeframe for DFA: {e}")
                import traceback
                traceback.print_exc()
                self.current_data = None
                
    def update_data(self):
        """Update current data from analyzer"""
        if self.analyzer and self.analyzer.processor:
            try:
                # Get all available data for the current channel
                data, _ = self.analyzer.processor.get_filtered_data()
                if data is not None and len(data) > self.current_channel:
                    # Limit to 5 minutes of data for performance
                    max_samples = int(5 * 60 * self.analyzer.processor.get_sampling_rate())
                    channel_data = data[self.current_channel]
                    
                    if len(channel_data) > max_samples:
                        print(f"📊 DFA: Limiting analysis to 5 minutes for performance")
                        # Take data from the middle of the recording
                        mid_point = len(channel_data) // 2
                        start_idx = int(mid_point - max_samples // 2)
                        end_idx = int(mid_point + max_samples // 2)
                        self.current_data = channel_data[start_idx:end_idx]
                    else:
                        self.current_data = channel_data
                        
                    self.sfreq = self.analyzer.processor.get_sampling_rate()
                    
                    # Update max scale based on data length
                    max_possible = len(self.current_data) // 4
                    self.max_scale_spin.setMaximum(max_possible)
                    if self.max_scale_spin.value() > max_possible:
                        self.max_scale_spin.setValue(max_possible)
                else:
                    print("Error: No valid data available for the selected channel")
                    self.current_data = None
                    
            except Exception as e:
                print(f"Error updating DFA data: {e}")
                import traceback
                traceback.print_exc()
                self.current_data = None
                
    def run_analysis(self):
        """Run DFA analysis on current data"""
        if self.current_data is None:
            print("Error: No data available for analysis")
            return
            
        try:
            # Get parameters
            min_scale = self.min_scale_spin.value()
            max_scale = self.max_scale_spin.value()
            n_scales = self.n_scales_spin.value()
            
            # Validate parameters
            if min_scale <= 0 or max_scale <= 0 or n_scales <= 0:
                print("Error: Scale parameters must be positive")
                return
                
            if min_scale >= max_scale:
                print("Error: Min scale must be less than max scale")
                return
                
            # Calculate DFA
            result = self.calculate_dfa_direct(min_scale, max_scale, n_scales)
            if result is None:
                return
                
            self.scales, self.fluctuations, self.alpha = result
            
            # Update plot
            self.update_plot()
            
            # Update results display
            self.update_results()
            
            # Only emit completion signal if we have a valid alpha
            if self.alpha is not None and not np.isnan(self.alpha):
                self.analysis_completed.emit(self.alpha)
            
        except Exception as e:
            print(f"Error running DFA analysis: {e}")
            import traceback
            traceback.print_exc()
            
    def calculate_dfa_direct(self, min_scale, max_scale, n_scales):
        """Calculate DFA directly without threading"""
        if self.current_data is None:
            print("Error: No data available for analysis")
            return None
            
        try:
            # Validate input parameters
            if min_scale <= 0 or max_scale <= 0 or n_scales <= 0:
                print("Error: Scale parameters must be positive")
                return None
                
            if min_scale >= max_scale:
                print("Error: Min scale must be less than max scale")
                return None
                
            # Ensure minimum scale is at least 4 samples
            min_scale = max(4, min_scale)
            
            # Generate logarithmically spaced scales
            scales = np.logspace(np.log10(min_scale), np.log10(max_scale), n_scales)
            scales = np.round(scales).astype(int)
            
            # Calculate fluctuations for each scale
            fluctuations = []
            valid_scales = []
            
            # Pre-calculate cumulative sum for faster processing
            cumsum = np.cumsum(self.current_data - np.mean(self.current_data))
            
            for scale in scales:
                # Divide signal into non-overlapping segments
                n_segments = len(self.current_data) // scale
                if n_segments < 2:
                    continue
                    
                # Reshape data into segments
                segments = cumsum[:n_segments * scale].reshape(n_segments, scale)
                
                # Calculate local trends using vectorized operations
                x = np.arange(scale)
                x_centered = x - np.mean(x)
                x_centered_squared = np.sum(x_centered ** 2)
                
                # Calculate trends for all segments at once
                y_centered = segments - np.mean(segments, axis=1, keepdims=True)
                slope = np.sum(x_centered * y_centered, axis=1) / x_centered_squared
                intercept = np.mean(segments, axis=1) - slope * np.mean(x)
                
                # Calculate trends using broadcasting
                trends = slope[:, np.newaxis] * x + intercept[:, np.newaxis]
                
                # Detrend segments
                detrended = segments - trends
                
                # Calculate root mean square fluctuation
                rms = np.sqrt(np.mean(detrended ** 2, axis=1))
                mean_rms = np.mean(rms)
                
                # Only include valid fluctuations
                if np.isfinite(mean_rms) and mean_rms > 0:
                    fluctuations.append(mean_rms)
                    valid_scales.append(scale)
            
            # Check if we have enough valid points for analysis
            if len(valid_scales) < 2:
                print("Error: Not enough valid fluctuation values for analysis")
                return None
                
            # Calculate scaling exponent (alpha) using linear regression in log-log space
            log_scales = np.log10(valid_scales)
            log_fluctuations = np.log10(fluctuations)
            
            # Verify that we have valid log values
            if not np.all(np.isfinite(log_scales)) or not np.all(np.isfinite(log_fluctuations)):
                print("Error: Invalid values in log calculations")
                return None
            
            # Fit line to log-log plot
            reg = LinearRegression()
            reg.fit(log_scales.reshape(-1, 1), log_fluctuations)
            alpha = reg.coef_[0]
            
            return np.array(valid_scales), np.array(fluctuations), alpha
            
        except Exception as e:
            print(f"Error calculating DFA: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def update_plot(self):
        """Update the DFA plot"""
        self.plot_widget.clear()
        
        if self.scales is None or self.fluctuations is None:
            return
            
        # Plot fluctuations vs scales in log-log space
        log_scales = np.log10(self.scales)
        log_fluctuations = np.log10(self.fluctuations)
        
        # Plot data points
        self.plot_widget.plot(log_scales, log_fluctuations, 
                            pen=None, symbol='o', symbolSize=6, 
                            symbolBrush='#00bfff', symbolPen='#00bfff')
        
        # Plot fitted line
        if not np.isnan(self.alpha):
            # Calculate fitted line
            fitted_line = self.alpha * log_scales + (np.mean(log_fluctuations) - self.alpha * np.mean(log_scales))
            self.plot_widget.plot(log_scales, fitted_line, 
                                pen={'color': '#ff4444', 'width': 2}, 
                                name=f'α = {self.alpha:.3f}')
            
        # Set axis ranges
        if len(log_scales) > 0 and len(log_fluctuations) > 0:
            x_min = np.min(log_scales)
            x_max = np.max(log_scales)
            y_min = np.min(log_fluctuations)
            y_max = np.max(log_fluctuations)
            
            # Add margins
            x_range = x_max - x_min
            y_range = y_max - y_min
            
            self.plot_widget.setXRange(x_min - x_range * 0.05, x_max + x_range * 0.05, padding=0)
            self.plot_widget.setYRange(y_min - y_range * 0.05, y_max + y_range * 0.5, padding=0)
            
    def update_results(self):
        """Update results display"""
        if self.alpha is None:
            return
            
        # Update alpha display
        self.alpha_label.setText(f"DFA α: {self.alpha:.3f}")
        
        # Interpretation
        if np.isnan(self.alpha):
            interpretation = "Invalid result"
            color = "#ff4444"
        elif self.alpha < 0.5:
            interpretation = "Anti-correlated"
            color = "#ff8800"
        elif 0.5 <= self.alpha < 1.0:
            interpretation = "Short-range correlated"
            color = "#44ff44"
        elif 1.0 <= self.alpha < 1.5:
            interpretation = "Long-range correlated"
            color = "#00bfff"
        else:
            interpretation = "Non-stationary"
            color = "#ff44ff"
            
        self.interpretation_label.setText(f"Interpretation: {interpretation}")
        self.interpretation_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Statistics
        stats_text = f"""DFA Statistics:
        
α (Scaling exponent): {self.alpha:.4f}
        
Scale range: {self.scales[0]} - {self.scales[-1]} samples
Time range: {self.scales[0]/self.sfreq:.3f} - {self.scales[-1]/self.sfreq:.3f} s
        
Number of scales: {len(self.scales)}
Data length: {len(self.current_data)} samples
Sampling rate: {self.sfreq:.1f} Hz

Interpretation Guide:
• α < 0.5: Anti-correlated (pink noise)
• α ≈ 0.5: Uncorrelated (white noise)  
• 0.5 < α < 1.0: Short-range correlated
• α ≈ 1.0: 1/f noise (pink noise)
• 1.0 < α < 1.5: Long-range correlated
• α ≈ 1.5: Brownian motion
• α > 1.5: Non-stationary"""
        
        self.stats_text.setText(stats_text)
