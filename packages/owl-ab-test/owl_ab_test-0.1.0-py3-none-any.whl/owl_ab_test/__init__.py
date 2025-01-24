"""
owl_ab_test - A Python package for A/B testing statistical analysis
"""

from owl_ab_test.core import calculate_proportion_stats
from owl_ab_test.exceptions import InvalidInputError

__version__ = "0.1.0"
__all__ = ["calculate_proportion_stats", "InvalidInputError"]
