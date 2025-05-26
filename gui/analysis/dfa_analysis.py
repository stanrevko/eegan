"""
DFA Analysis
Detrended Fluctuation Analysis for EEG signals
"""

import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox,
                             QTextEdit, QProgressBar, QCheckBox)
from PyQt5.QtCore import pyqtSignal, QTimer
import pyqtgraph as pg
from scipy import signal
from sklearn.linear_model import LinearRegression


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
        
        # Parameters group
        params_group = QGroupBox("DFA Parameters")
        params_layout = QHBoxLayout(params_group)
        
        # Min scale
        params_layout.addWidget(QLabel("Min Scale:"))
        self.min_scale_spin = QSpinBox()
        self.min_scale_spin.setRange(2, 100)
        self.min_scale_spin.setValue(4)
        self.min_scale_spin.setToolTip("Minimum time scale for DFA (samples)")
        params_layout.addWidget(self.min_scale_spin)
        
        # Max scale
        params_layout.addWidget(QLabel("Max Scale:"))
        self.max_scale_spin = QSpinBox()
        self.max_scale_spin.setRange(10, 10000)
        self.max_scale_spin.setValue(1000)
        self.max_scale_spin.setToolTip("Maximum time scale for DFA (samples)")
        params_layout.addWidget(self.max_scale_spin)
        
        # Number of scales
        params_layout.addWidget(QLabel("N Scales:"))
        self.n_scales_spin = QSpinBox()
        self.n_scales_spin.setRange(10, 50)
        self.n_scales_spin.setValue(20)
        self.n_scales_spin.setToolTip("Number of scales to calculate")
        params_layout.addWidget(self.n_scales_spin)
        
        params_layout.addStretch()
        
        # Calculate button
        self.calculate_btn = QPushButton("🔬 Calculate DFA")
        self.calculate_btn.clicked.connect(self.calculate_dfa)
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        params_layout.addWidget(self.calculate_btn)
        
        layout.addWidget(params_group)
        
        
        # Results layout
        results_layout = QHBoxLayout()
        
        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'log₁₀(F(n))', color='white', size='12pt')
        self.plot_widget.setLabel('bottom', 'log₁₀(n)', color='white', size='12pt')
        self.plot_widget.setTitle('DFA - Fluctuation vs Scale', color='white', size='14pt')
        self.plot_widget.setBackground('#2b2b2b')
        self.plot_widget.showGrid(True, True, 0.3)
        
        # Style axes
        for axis_name in ['bottom', 'left']:
            axis = self.plot_widget.getAxis(axis_name)
            axis.setPen(color='white')
            axis.setTextPen(color='white')
            
        results_layout.addWidget(self.plot_widget, stretch=2)
        
        # Results panel
        results_panel = QGroupBox("DFA Results")
        results_panel_layout = QVBoxLayout(results_panel)
        results_panel.setMaximumWidth(300)
        
        # Alpha value display
        self.alpha_label = QLabel("DFA α: --")
        self.alpha_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00bfff;")
        results_panel_layout.addWidget(self.alpha_label)
        
        # Interpretation
        self.interpretation_label = QLabel("Interpretation: --")
        self.interpretation_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.interpretation_label.setWordWrap(True)
        results_panel_layout.addWidget(self.interpretation_label)
        
        # Statistics
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        results_panel_layout.addWidget(self.stats_text)
        
        results_panel_layout.addStretch()
        results_layout.addWidget(results_panel)
        
        layout.addLayout(results_layout)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 2px;
                border-radius: 3px;
            }
        """)
        
    def set_analyzer(self, analyzer):
        """Set the EEG analyzer"""
        self.analyzer = analyzer
        self.update_data()  # Update data immediately when analyzer is set
        
    def set_channel(self, channel_idx):
        """Set the channel to analyze"""
        self.current_channel = channel_idx
        # Re-enable calculate button if it was disabled
        self.calculate_btn.setEnabled(True)
        self.calculate_btn.setText("🔬 Calculate DFA")
            
    def calculate_dfa_direct(self, min_scale, max_scale, n_scales):
        """Calculate DFA directly without threading"""
        from sklearn.linear_model import LinearRegression
        
        # Integrate the signal
        integrated = np.cumsum(self.current_data - np.mean(self.current_data))
        
        # Create logarithmically spaced scales
        scales = np.logspace(
            np.log10(min_scale), 
            np.log10(max_scale), 
            n_scales
        ).astype(int)
        
        fluctuations = np.zeros(len(scales))
        
        for i, scale in enumerate(scales):
            # Divide integrated signal into non-overlapping segments
            n_segments = len(integrated) // scale
            
            if n_segments < 1:
                continue
                
            # Reshape data for vectorized processing
            segments = integrated[:n_segments * scale].reshape(n_segments, scale)
            
            # Create time array for each segment
            t = np.arange(scale)
            
            # Calculate local trends for each segment
            fluctuation_sum = 0
            for segment in segments:
                # Fit linear trend
                coeffs = np.polyfit(t, segment, 1)
                trend = np.polyval(coeffs, t)
                
                # Calculate fluctuation (RMS of detrended segment)
                fluctuation_sum += np.sum((segment - trend) ** 2)
            
            # Average fluctuation for this scale
            fluctuations[i] = np.sqrt(fluctuation_sum / (n_segments * scale))
        
        # Remove any zero fluctuations
        valid_indices = fluctuations > 0
        scales = scales[valid_indices]
        fluctuations = fluctuations[valid_indices]
        
        # Calculate scaling exponent (alpha) using linear regression in log-log space
        if len(scales) > 2:
            log_scales = np.log10(scales)
            log_fluctuations = np.log10(fluctuations)
            
            # Fit line to log-log plot
            reg = LinearRegression()
            reg.fit(log_scales.reshape(-1, 1), log_fluctuations)
            alpha = reg.coef_[0]
        else:
            alpha = np.nan
            
        return scales, fluctuations, alpha
        # Update data and clear results
        self.update_data()
        self.clear_results()
        
    def update_data(self):
        """Update current data from analyzer"""
        if self.analyzer and self.analyzer.processor:
            try:
                # Get all available data for the current channel
                data, times = self.analyzer.processor.get_filtered_data()
                if data is not None and len(data) > self.current_channel:
                    self.current_data = data[self.current_channel]
                    self.sfreq = self.analyzer.processor.get_sampling_rate()
                    
                    # Update max scale based on data length
                    max_possible = len(self.current_data) // 4
                    self.max_scale_spin.setMaximum(max_possible)
                    if self.max_scale_spin.value() > max_possible:
                        self.max_scale_spin.setValue(max_possible)
                else:
                    self.current_data = None
                        
            except Exception as e:
                print(f"Error updating DFA data: {e}")
                self.current_data = None
                
    def set_timeframe(self, start_time, end_time):
        """Set analysis timeframe"""
        # Update data based on timeframe
        if self.analyzer and self.analyzer.processor:
            try:
                data, times = self.analyzer.processor.get_filtered_data(start_time, end_time)
                if data is not None and len(data) > self.current_channel:
                    self.current_data = data[self.current_channel]
                    self.sfreq = self.analyzer.processor.get_sampling_rate()
                    
                    # Update max scale based on data length
                    max_possible = len(self.current_data) // 4
                    self.max_scale_spin.setMaximum(max_possible)
                    if self.max_scale_spin.value() > max_possible:
                        self.max_scale_spin.setValue(max_possible)
                else:
                    pass  # No data available for timeframe
                        
            except Exception as e:
                print(f"Error setting timeframe for DFA: {e}")
                
    def calculate_dfa(self):
        """Start DFA calculation"""
        # Check if we have data
        if self.current_data is None:
            self.stats_text.setText("❌ No data available. Please select a channel and ensure EEG data is loaded.")
            return
            
        if len(self.current_data) < 100:
            self.stats_text.setText(f"❌ Insufficient data length: {len(self.current_data)} samples. Need at least 100 samples.")
            return
            
        # Clear previous results
        self.clear_results()
        
        # Disable button during calculation
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.setText("🔄 Calculating...")
        
        # Get parameters
        min_scale = self.min_scale_spin.value()
        max_scale = min(self.max_scale_spin.value(), len(self.current_data) // 4)
        n_scales = self.n_scales_spin.value()
        
        try:
            # Calculate DFA directly (non-threaded for stability)
            scales, fluctuations, alpha = self.calculate_dfa_direct(min_scale, max_scale, n_scales)
            
            # Update results directly
            self.scales = scales
            self.fluctuations = fluctuations
            self.alpha = alpha
            
            # Update plot and results display
            self.update_plot()
            self.update_results()
            
            # Emit signal
            self.analysis_completed.emit(alpha)
            
        except Exception as e:
            self.stats_text.setText(f"❌ Error calculating DFA: {str(e)}")
        finally:
            # Always re-enable button
            self.calculate_btn.setEnabled(True)
            self.calculate_btn.setText("🔬 Calculate DFA")
            
    def calculate_dfa_direct(self, min_scale, max_scale, n_scales):
        """Calculate DFA directly without threading"""
        from sklearn.linear_model import LinearRegression
        
        # Integrate the signal
        integrated = np.cumsum(self.current_data - np.mean(self.current_data))
        
        # Create logarithmically spaced scales
        scales = np.logspace(
            np.log10(min_scale), 
            np.log10(max_scale), 
            n_scales
        ).astype(int)
        
        fluctuations = np.zeros(len(scales))
        
        for i, scale in enumerate(scales):
            # Divide integrated signal into non-overlapping segments
            n_segments = len(integrated) // scale
            
            if n_segments < 1:
                continue
                
            # Reshape data for vectorized processing
            segments = integrated[:n_segments * scale].reshape(n_segments, scale)
            
            # Create time array for each segment
            t = np.arange(scale)
            
            # Calculate local trends for each segment
            fluctuation_sum = 0
            for segment in segments:
                # Fit linear trend
                coeffs = np.polyfit(t, segment, 1)
                trend = np.polyval(coeffs, t)
                
                # Calculate fluctuation (RMS of detrended segment)
                fluctuation_sum += np.sum((segment - trend) ** 2)
            
            # Average fluctuation for this scale
            fluctuations[i] = np.sqrt(fluctuation_sum / (n_segments * scale))
        
        # Remove any zero fluctuations
        valid_indices = fluctuations > 0
        scales = scales[valid_indices]
        fluctuations = fluctuations[valid_indices]
        
        # Calculate scaling exponent (alpha) using linear regression in log-log space
        if len(scales) > 2:
            log_scales = np.log10(scales)
            log_fluctuations = np.log10(fluctuations)
            
            # Fit line to log-log plot
            reg = LinearRegression()
            reg.fit(log_scales.reshape(-1, 1), log_fluctuations)
            alpha = reg.coef_[0]
        else:
            alpha = np.nan
            
        return scales, fluctuations, alpha
        
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
        
    def clear_results(self):
        """Clear all results"""
        self.scales = None
        self.fluctuations = None
        self.alpha = None
        self.plot_widget.clear()
        self.alpha_label.setText("DFA α: --")
        self.interpretation_label.setText("Interpretation: --")
        self.interpretation_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.stats_text.clear()
        
    def get_alpha_value(self):
        """Get current alpha value"""
        return self.alpha
