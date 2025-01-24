"""
Core statistical functions for A/B testing analysis
"""

import pandas as pd
import numpy as np
from scipy.stats import norm, t as t_dist
from scipy.stats import ttest_ind_from_stats

def calculate_proportion_stats(success_count, total_count, 
                             control_success, control_total,
                             confidence_level=0.95):
    # Calculate proportions
    p1 = success_count / total_count  # treatment proportion
    p2 = control_success / control_total  # control proportion
    
    # Calculate lift
    lift = (p1 - p2) / p2
    
    # Pooled proportion for standard error
    p_pooled = (success_count + control_success) / (total_count + control_total)
    
    # Standard error
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/total_count + 1/control_total))
    
    # Z-test statistic
    z_stat = (p1 - p2) / se
    
    # P-value
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    
    # Confidence interval for difference in proportions
    alpha = 1 - confidence_level
    z_crit = norm.ppf(1 - alpha/2)
    
    # Calculate CI for absolute difference
    margin_of_error = z_crit * se
    diff = p1 - p2
    ci_lower_abs = diff - margin_of_error
    ci_upper_abs = diff + margin_of_error
    
    # Convert to relative lift confidence intervals
    ci_lower = ci_lower_abs / p2
    ci_upper = ci_upper_abs / p2
    
    return {
        'lift': lift,
        'statistic': z_stat,
        'p_value': p_value,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper
    }