# owl_ab_test

A Python package for A/B testing statistical analysis. This package provides tools for analyzing the results of A/B tests with a focus on proportion testing.

## Installation

```bash
pip install owl_ab_test
```

## Features

- Calculate proportion-based statistics for A/B tests including lift, p-values, and confidence intervals
- Process multiple metrics simultaneously
- Generate visualizations of confidence intervals using Plotly
- Handle control and multiple treatment groups
- Built-in error handling for invalid inputs

## Usage

### Basic Example

```python
from owl_ab_test import calculate_proportion_stats, process_proportion_stats, plot_confidence_intervals
import pandas as pd

# Calculate statistics for a single metric
stats = calculate_proportion_stats(
    success_count=150,    # Number of successes in treatment group
    total_count=1000,     # Total sample size in treatment group
    control_success=120,  # Number of successes in control group
    control_total=1000,   # Total sample size in control group
    confidence_level=0.95 # Optional confidence level (default: 0.95)
)

print(f"Lift: {stats['lift']:.2%}")
print(f"P-value: {stats['p_value']:.4f}")
print(f"95% CI: ({stats['ci_lower']:.2%}, {stats['ci_upper']:.2%})")
```

### Processing Multiple Metrics

```python
# Example DataFrame structure
data = {
    'variant': ['control', 'treatment_a', 'treatment_b'],
    'bucketed_visitors': [1000, 1000, 1000],
    'trial_starts': [120, 150, 140],
    'purchases': [60, 75, 70]
}
df = pd.DataFrame(data)

# Configure metrics to analyze
metrics_config = {
    'trial_conversion': {
        'success_col': 'trial_starts',
        'total_col': 'bucketed_visitors'
    },
    'purchase_conversion': {
        'success_col': 'purchases',
        'total_col': 'bucketed_visitors'
    }
}

# Process all metrics
results = process_proportion_stats(df, metrics_config)
```

### Visualizing Results

```python
# Create a confidence interval plot
metric_mapping = {
    'trial_conversion': 'Trial Conversion Rate',
    'purchase_conversion': 'Purchase Conversion Rate'
}

fig = plot_confidence_intervals(
    results,
    metric_mapping=metric_mapping,
    width=900,
    height=400
)
fig.show()
```

## API Reference

### calculate_proportion_stats

```python
calculate_proportion_stats(success_count, total_count, control_success, control_total, confidence_level=0.95)
```

Calculates statistical metrics for proportion-based A/B tests.

Parameters:
- `success_count` (int): Number of successes in treatment group
- `total_count` (int): Total sample size in treatment group
- `control_success` (int): Number of successes in control group
- `control_total` (int): Total sample size in control group
- `confidence_level` (float, optional): Confidence level for intervals (default: 0.95)

Returns:
- dict with keys:
  - `lift`: Relative improvement over control
  - `statistic`: Z-test statistic
  - `p_value`: Two-sided p-value
  - `ci_lower`: Lower bound of confidence interval for relative lift
  - `ci_upper`: Upper bound of confidence interval for relative lift

### process_proportion_stats

```python
process_proportion_stats(df, metrics_config)
```

Processes multiple metrics for A/B test analysis.

Parameters:
- `df` (pandas.DataFrame): DataFrame containing experiment data
  - Required columns: 'variant' plus columns specified in metrics_config
- `metrics_config` (dict): Configuration for metrics to analyze
  - Keys: metric names
  - Values: dict with 'success_col' and 'total_col' keys

Returns:
- pandas.DataFrame with columns:
  - `Metric`: Name of the metric
  - `Group`: Variant name
  - `Value`: Raw proportion
  - `Lift`: Relative lift vs control
  - `Statistic`: Z-test statistic
  - `P-Value`: Two-sided p-value
  - `CI_Lower`: Lower confidence interval
  - `CI_Upper`: Upper confidence interval

### plot_confidence_intervals

```python
plot_confidence_intervals(results, metric_mapping=None, width=900, height=400)
```

Creates a visualization of confidence intervals for experiment results.

Parameters:
- `results` (pandas.DataFrame): Results DataFrame from process_proportion_stats
- `metric_mapping` (dict, optional): Maps metric names to display names
- `width` (int, optional): Plot width in pixels (default: 900)
- `height` (int, optional): Plot height in pixels (default: 400)

Returns:
- plotly.graph_objects.Figure: Interactive confidence interval plot

## Requirements

- Python >=3.7
- numpy
- pandas
- scipy
- plotly

## Notes

- The package uses z-test statistics assuming large sample sizes
- Confidence intervals are calculated for relative lift over control
- The visualization uses Plotly for interactive plots
- Treatment groups are compared against the control group specified by 'variant' == 'control'

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.