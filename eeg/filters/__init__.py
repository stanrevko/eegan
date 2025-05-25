"""
Filters Module
EEG signal filtering components
"""

from .bandpass_filter import BandpassFilter
from .notch_filter import NotchFilter
from .filter_manager import FilterManager

__all__ = ['BandpassFilter', 'NotchFilter', 'FilterManager']
