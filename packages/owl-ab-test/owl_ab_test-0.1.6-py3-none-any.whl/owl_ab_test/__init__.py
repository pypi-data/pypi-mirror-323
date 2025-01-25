"""
owl_ab_test - A Python package for A/B testing statistical analysis
"""

from owl_ab_test.core import calculate_proportion_stats, process_proportion_stats, plot_confidence_intervals
from owl_ab_test.exceptions import InvalidInputError

__version__ = "0.1.6"
__all__ = ["calculate_proportion_stats", "InvalidInputError", "process_proportion_stats", "plot_confidence_intervals"]
