import numpy as np
from scipy import stats
import pytest
from roll_regression import linregress, roll_linregress

def test_linear_regression_against_scipy():
    # ... existing test code ...
    pass

def test_linear_regression_edge_cases():
    # ... existing test code ...
    pass

def test_roll_linregress():
    # Generate sample data
    np.random.seed(42)
    n_samples = 100
    n_features = 2
    window = 20
    
    # Create features
    X = np.random.randn(n_samples, n_features)
    
    # True coefficients (including intercept)
    true_coefficients = np.array([2.0, 3.0, 4.0])
    
    # Generate target with some noise
    y = (true_coefficients[0] +  # intercept
         true_coefficients[1] * X[:, 0] +  # first feature
         true_coefficients[2] * X[:, 1] +  # second feature
         np.random.normal(0, 0.1, n_samples))  # noise
    
    # Get rolling regression results
    coefficients, fitted = roll_linregress(X, y, window)
    
    # Manual rolling regression for comparison
    n_windows = n_samples - window + 1
    manual_coefficients = np.zeros((n_windows, n_features + 1))
    manual_fitted = np.zeros((n_windows, window))
    
    for i in range(n_windows):
        X_window = X[i:i + window]
        y_window = y[i:i + window]
        
        # Add constant term to X for comparison
        X_with_const = np.column_stack([np.ones(window), X_window])
        
        # Calculate coefficients using numpy's least squares
        window_coefficients = np.linalg.lstsq(X_with_const, y_window, rcond=None)[0]
        window_fitted = X_with_const @ window_coefficients
        
        manual_coefficients[i] = window_coefficients
        manual_fitted[i] = window_fitted
    
    # Compare results
    np.testing.assert_allclose(coefficients, manual_coefficients, rtol=1e-10)
    np.testing.assert_allclose(fitted, manual_fitted, rtol=1e-10)

def test_roll_linregress_edge_cases():
    # Test minimum window size
    X = np.array([[1.0], [2.0], [3.0]])
    y = np.array([2.0, 4.0, 6.0])
    window = 2
    
    coefficients, fitted = roll_linregress(X, y, window)
    assert coefficients.shape == (2, 2)  # 2 windows, 2 coefficients (intercept + slope)
    assert fitted.shape == (2, 2)        # 2 windows, 2 fitted values per window
    
    # Test window size equal to sample size
    window = 3
    coefficients, fitted = roll_linregress(X, y, window)
    assert coefficients.shape == (1, 2)  # 1 window, 2 coefficients
    assert fitted.shape == (1, 3)        # 1 window, 3 fitted values
    
    # Test error cases
    with pytest.raises(RuntimeError):
        # Window size too large
        roll_linregress(X, y, 4)
    
    with pytest.raises(RuntimeError):
        # Window size too small
        roll_linregress(X, y, 0)

def test_roll_linregress_perfect_fit():
    # Test case with perfect linear relationship
    X = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]])
    y = 2 + 3 * X[:, 0]  # y = 2 + 3x
    window = 3
    
    coefficients, fitted = roll_linregress(X, y, window)
    
    # Should have 3 windows
    assert coefficients.shape == (3, 2)  # 3 windows, 2 coefficients
    
    # All windows should recover the true coefficients
    expected_coefficients = np.array([[2.0, 3.0]] * 3)  # [intercept, slope] for each window
    np.testing.assert_allclose(coefficients, expected_coefficients, rtol=1e-10)
    
    # Fitted values should exactly match original values within each window
    for i in range(3):
        window_y = y[i:i + window]
        np.testing.assert_allclose(fitted[i], window_y, rtol=1e-10) 