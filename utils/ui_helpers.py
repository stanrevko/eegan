"""
UI Helper Utilities
Common UI components and helper functions
"""

from PyQt5.QtWidgets import QStyle, QPushButton, QSlider, QLabel, QHBoxLayout, QVBoxLayout, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg


def create_styled_button(text: str, style_class: str = "primary") -> QPushButton:
    """Create a styled button with consistent appearance"""
    button = QPushButton(text)
    
    styles = {
        "primary": """
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """,
        "secondary": """
            QPushButton {
                background-color: #6c757d;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """,
        "toggle": """
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
            QPushButton:hover {
                border-color: #0078d4;
            }
        """
    }
    
    button.setStyleSheet(styles.get(style_class, styles["primary"]))
    return button


def create_labeled_slider(label_text: str, min_val: int, max_val: int, 
                         initial_val: int, unit: str = "") -> tuple:
    """Create a labeled slider with value display"""
    layout = QVBoxLayout()
    
    # Label
    label = QLabel(label_text)
    label.setStyleSheet("color: #ffffff; font-weight: bold;")
    layout.addWidget(label)
    
    # Slider
    slider = QSlider(Qt.Horizontal)
    slider.setRange(min_val, max_val)
    slider.setValue(initial_val)
    slider.setStyleSheet("""
        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 8px;
            background: #3c3c3c;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #0078d4;
            border: 1px solid #0078d4;
            width: 18px;
            border-radius: 9px;
            margin-top: -5px;
            margin-bottom: -5px;
        }
    """)
    layout.addWidget(slider)
    
    # Value label
    value_label = QLabel(f"{initial_val}{unit}")
    value_label.setStyleSheet("color: #cccccc; font-size: 11px;")
    layout.addWidget(value_label)
    
    # Connect slider to update value label
    slider.valueChanged.connect(lambda v: value_label.setText(f"{v}{unit}"))
    
    return layout, slider, value_label


def setup_dark_plot(plot_widget: pg.PlotWidget, x_label: str, y_label: str):
    """Setup dark theme for a plot widget"""
    plot_widget.setBackground('#2b2b2b')
    plot_widget.setLabel('bottom', x_label, color='white', size='12pt')
    plot_widget.setLabel('left', y_label, color='white', size='12pt')
    plot_widget.showGrid(True, True, 0.3)
    
    # Style axes
    for axis_name in ['bottom', 'left']:
        axis = plot_widget.getAxis(axis_name)
        axis.setPen(color='white')
        axis.setTextPen(color='white')
    
    return plot_widget


def create_collapsible_button(text_expanded: str, text_collapsed: str) -> QPushButton:
    """Create a button for collapsing/expanding panels"""
    button = QPushButton(text_expanded)
    button.setCheckable(True)
    button.setStyleSheet("""
        QPushButton {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 8px;
            font-weight: bold;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QPushButton:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
    """)
    
    def update_text(checked):
        button.setText(text_collapsed if checked else text_expanded)
        
    button.toggled.connect(update_text)
    return button


class ChannelVisibilityWidget:
    """Widget for managing channel visibility"""
    
    def __init__(self, channel_names: list):
        self.channel_names = channel_names
        self.checkboxes = {}
        self.layout = QVBoxLayout()
        
        # Create checkboxes for each channel
        for i, name in enumerate(channel_names):
            checkbox = create_styled_button(name, "toggle")
            checkbox.setCheckable(True)
            checkbox.setChecked(True)  # All visible by default
            self.checkboxes[i] = checkbox
            self.layout.addWidget(checkbox)
            
    def get_visible_channels(self) -> list:
        """Get list of indices for visible channels"""
        return [i for i, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        
    def set_channel_visibility(self, channel_idx: int, visible: bool):
        """Set visibility for a specific channel"""
        if channel_idx in self.checkboxes:
            self.checkboxes[channel_idx].setChecked(visible)


def create_dark_button(text, parent=None):
    """Create a dark-themed button"""
    button = QPushButton(text, parent)
    button.setStyleSheet("""
        QPushButton {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            color: #ffffff;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QPushButton:pressed {
            background-color: #2d2d2d;
        }
    """)
    return button


def create_dark_combobox(parent=None):
    """Create a dark-themed combobox"""
    combobox = QComboBox(parent)
    combobox.setStyleSheet("""
        QComboBox {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            color: #ffffff;
            padding: 2px 5px;
            border-radius: 3px;
            min-width: 100px;
        }
        QComboBox:hover {
            border: 1px solid #666666;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #3c3c3c;
            color: #ffffff;
            selection-background-color: #4a4a4a;
            selection-color: #ffffff;
            border: 1px solid #555555;
        }
    """)
    return combobox
