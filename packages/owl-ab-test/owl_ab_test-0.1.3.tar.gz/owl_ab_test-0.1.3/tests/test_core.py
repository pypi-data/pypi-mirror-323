"""
Unit tests for owl_ab_test core functionality
"""

import pytest
from owl_ab_test import calculate_proportion_stats
from owl_ab_test.exceptions import InvalidInputError

def test_basic_calculation():
    result = calculate_proportion_stats(
        success_count=100,
        total_count=1000,
        control_success=90,
        control_total=1000,
        confidence_level=0.95
    )
    
    assert isinstance(result, dict)
    assert all(key in result for key in [
        'p_value', 'confidence_interval', 'relative_uplift',
        'significant', 'power'
    ])
    assert isinstance(result['p_value'], float)
    assert isinstance(result['confidence_interval'], tuple)
    assert isinstance(result['relative_uplift'], float)
    assert isinstance(result['significant'], bool)
    assert isinstance(result['power'], float)

def test_invalid_inputs():
    # Test negative counts
    with pytest.raises(InvalidInputError):
        calculate_proportion_stats(-1, 100, 50, 100)
    
    # Test success > total
    with pytest.raises(InvalidInputError):
        calculate_proportion_stats(200, 100, 50, 100)
    
    # Test invalid confidence level
    with pytest.raises(InvalidInputError):
        calculate_proportion_stats(50, 100, 50, 100, confidence_level=1.5)
    
    # Test zero total count
    with pytest.raises(InvalidInputError):
        calculate_proportion_stats(0, 0, 50, 100)

def test_edge_cases():
    # Test identical results
    result = calculate_proportion_stats(50, 100, 50, 100)
    assert not result['significant']
    assert result['p_value'] > 0.05
    
    # Test perfect conversion
    result = calculate_proportion_stats(100, 100, 100, 100)
    assert not result['significant']
    assert result['relative_uplift'] == 0.0

def test_significant_difference():
    result = calculate_proportion_stats(180, 200, 140, 200)
    assert result['significant']
    assert result['p_value'] < 0.05
