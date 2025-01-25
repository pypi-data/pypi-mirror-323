"""
Core statistical functions for A/B testing analysis
"""

import pandas as pd
import numpy as np
from scipy.stats import norm


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


def process_proportion_stats(df, metrics_config):
    """
    Calculate proportion statistics for different metrics and return results as DataFrame.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing all data including control group
    metrics_config : dict
        Dictionary containing metric configurations with column names
        Example format:
        {
            'trial_conversion': {
                'success_col': 'trial_starts',
                'total_col': 'bucketed_visitors'
            }
        }
    
    Returns:
    --------
    pandas.DataFrame
        Results DataFrame with columns:
        ['Metric', 'Group', 'Value', 'Lift', 'Statistic', 'P-Value', 'CI_Lower', 'CI_Upper']
    """
    # Get control data
    control_data = df[df['variant'] == 'control'].iloc[0]
    
    # Initialize lists for DataFrame construction
    results_data = {
        'Metric': [],
        'Group': [],
        'Value': [],
        'Lift': [],
        'Statistic': [],
        'P-Value': [],
        'CI_Lower': [],
        'CI_Upper': []
    }
    
    # Process each metric
    for metric_name, metric_config in metrics_config.items():
        success_col = metric_config['success_col']
        total_col = metric_config['total_col']
        
        # Add control row
        control_value = control_data[success_col] / control_data[total_col]
        results_data['Metric'].append(metric_name)
        results_data['Group'].append('Control')
        results_data['Value'].append(control_value)
        results_data['Lift'].append(None)
        results_data['Statistic'].append(None)
        results_data['P-Value'].append(None)
        results_data['CI_Lower'].append(None)
        results_data['CI_Upper'].append(None)
        
        # Process treatment groups
        treatment_data = df[(df['variant'] != 'control') & (df['variant'] != 'holdout')]
        for _, row in treatment_data.iterrows():
            # Calculate statistics
            stats = calculate_proportion_stats(
                success_count=row[success_col],
                total_count=row[total_col],
                control_success=control_data[success_col],
                control_total=control_data[total_col]
            )
            
            # Add treatment row
            results_data['Metric'].append(metric_name)
            results_data['Group'].append(row['variant'])
            results_data['Value'].append(row[success_col] / row[total_col])
            results_data['Lift'].append(stats['lift'])
            results_data['Statistic'].append(stats['statistic'])
            results_data['P-Value'].append(stats['p_value'])
            results_data['CI_Lower'].append(stats['ci_lower'])
            results_data['CI_Upper'].append(stats['ci_upper'])
    
    return pd.DataFrame(results_data)


def plot_confidence_intervals(results, metric_mapping=None, width=900, height=400):
    """
    Create a confidence interval plot from experiment results.
    
    Parameters:
    -----------
    results : pandas.DataFrame
        DataFrame containing experiment results with columns:
        'Group', 'Metric', 'Lift', 'CI_Lower', 'CI_Upper'
    metric_mapping : dict, optional
        Dictionary mapping metric names to display names
        Example: {'trial_starts': 'Trial Starts'}
    width : int, optional
        Width of the plot in pixels (default: 900)
    height : int, optional
        Height of the plot in pixels (default: 400)
    
    Returns:
    --------
    plotly.graph_objects.Figure
        The confidence interval plot
    """
    import plotly.graph_objects as go
    
    # Prepare the data
    plot_data = results[results['Group'] != 'Control'].copy()
    
    # Apply metric mapping if provided
    if metric_mapping:
        plot_data['Metric'] = plot_data['Metric'].map(metric_mapping)
    
    # Create DataFrame for plotting
    data = pd.DataFrame({
        'metric': plot_data['Metric'],
        'relativeDelta': plot_data['Lift'],
        'ciLower': plot_data['CI_Lower'],
        'ciUpper': plot_data['CI_Upper']
    })
    
    def get_bar_color(row):
        """Determine bar color based on confidence interval position"""
        if row['ciLower'] <= 0 and row['ciUpper'] >= 0:
            return '#9CA3AF'  # gray for overlap with 0
        elif row['ciUpper'] < 0:
            return '#FCA5A5'  # light red for negative
        elif row['ciLower'] > 0:
            return '#86EFAC'  # light green for positive
        return '#9CA3AF'      # default gray
    
    # Create the figure
    fig = go.Figure()
    
    # Add confidence interval bars
    for i, row in data.iterrows():
        fig.add_trace(go.Bar(
            x=[row['ciUpper'] - row['ciLower']],
            base=[row['ciLower']],
            y=[row['metric']],
            orientation='h',
            marker_color=get_bar_color(row),
            width=0.15,
            showlegend=False
        ))
    
    # Add mean value points with labels
    fig.add_trace(go.Scatter(
        x=data['relativeDelta'],
        y=data['metric'],
        mode='markers+text',
        marker=dict(
            color='black',
            size=12,
            symbol='circle'
        ),
        text=[f'{x:.1%}' for x in data['relativeDelta']],
        textposition='top center',
        textfont=dict(size=16),
        showlegend=False
    ))
    
    # Add reference line at x=0
    fig.add_vline(x=0, line_width=1, line_color='#666666')
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='Confidence Intervals (Relative Lift)',
            font=dict(size=18)
        ),
        xaxis_title=dict(
            text='Relative Change',
            font=dict(size=18)
        ),
        yaxis_title=dict(
            text='Metrics',
            font=dict(size=18)
        ),
        xaxis=dict(
            tickformat=',.1%',
            zeroline=False,
            range=[min(data['ciLower']) * 1.1, max(data['ciUpper']) * 1.1],
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            autorange='reversed',
            tickfont=dict(size=16)
        ),
        plot_bgcolor='white',
        width=width,
        height=height,
        margin=dict(l=200, r=60, t=40, b=40)
    )
    
    # Add grid lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig
