"""
Core statistical functions for A/B testing analysis
"""

from typing import Dict, Union, Optional
import numpy as np
from scipy import stats
import pandas as pd
from .exceptions import InvalidInputError

def calculate_proportion_stats(
    success_count: int,
    total_count: int,
    control_success: int,
    control_total: int,
    confidence_level: float = 0.95
) -> Dict[str, Union[float, bool]]:
    """
    Calculate statistical metrics for A/B test proportion comparison.

    Args:
        success_count (int): Number of successes in treatment group
        total_count (int): Total number of samples in treatment group
        control_success (int): Number of successes in control group
        control_total (int): Total number of samples in control group
        confidence_level (float): Confidence level (default: 0.95)

    Returns:
        Dict containing:
            - p_value: p-value of the test
            - confidence_interval: tuple of (lower, upper) bounds
            - relative_uplift: relative improvement over control
            - significant: boolean indicating statistical significance
            - power: statistical power of the test

    Raises:
        InvalidInputError: If input parameters are invalid
    """
    # Input validation
    if any(x < 0 for x in [success_count, total_count, control_success, control_total]):
        raise InvalidInputError("Counts cannot be negative")

    if success_count > total_count or control_success > control_total:
        raise InvalidInputError("Success count cannot exceed total count")

    if not 0 < confidence_level < 1:
        raise InvalidInputError("Confidence level must be between 0 and 1")

    if total_count == 0 or control_total == 0:
        raise InvalidInputError("Total counts must be greater than 0")

    # Calculate proportions
    p1 = success_count / total_count
    p2 = control_success / control_total

    # Pooled proportion for standard error
    p_pooled = (success_count + control_success) / (total_count + control_total)

    # Standard error
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/total_count + 1/control_total))

    # Z-score for confidence interval
    z_score = stats.norm.ppf((1 + confidence_level) / 2)

    # Calculate confidence interval
    diff = p1 - p2
    ci_lower = diff - z_score * se
    ci_upper = diff + z_score * se

    # Calculate z-statistic for p-value
    if se == 0:
        p_value = 1.0
    else:
        z_stat = (p1 - p2) / se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    # Calculate relative uplift
    relative_uplift = ((p1 - p2) / p2) * 100 if p2 != 0 else float('inf')

    # Calculate power
    effect_size = abs(p1 - p2)
    power = stats.power_divergence([success_count, total_count - success_count,
                                  control_success, control_total - control_success],
                                 lambda_="log-likelihood")[1]

    return {
        'p_value': float(p_value),
        'confidence_interval': (float(ci_lower), float(ci_upper)),
        'relative_uplift': float(relative_uplift),
        'significant': bool(p_value < (1 - confidence_level)),  # Explicit conversion to Python bool
        'power': float(power)
    }