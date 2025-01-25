import numpy as np
from scipy import stats
import pytest
from roll_regression import linregress

def test_linear_regression_against_scipy():
    # Generate sample data
    np.random.seed(42)
    n_samples = 100
    n_features = 2
    
    # Create features
    X = np.random.randn(n_samples, n_features)
    
    # True coefficients (including intercept)
    true_coefficients = np.array([2.0, 3.0, 4.0])
    
    # Generate target with some noise
    y = (true_coefficients[0] +  # intercept
         true_coefficients[1] * X[:, 0] +  # first feature
         true_coefficients[2] * X[:, 1] +  # second feature
         np.random.normal(0, 0.1, n_samples))  # noise
    
    # Our implementation
    coefficients, fitted = linregress(X, y)
    
    # Scipy implementation
    # Add constant term to X for statsmodels-style comparison
    X_with_intercept = np.column_stack([np.ones(n_samples), X])
    scipy_coefficients = np.linalg.lstsq(X_with_intercept, y, rcond=None)[0]
    scipy_fitted = X_with_intercept @ scipy_coefficients
    
    # Compare results
    np.testing.assert_allclose(coefficients, scipy_coefficients, rtol=1e-10)
    np.testing.assert_allclose(fitted, scipy_fitted, rtol=1e-10)
    
    # Also verify that coefficients are close to true values
    np.testing.assert_allclose(coefficients, true_coefficients, rtol=1e-1)

def test_linear_regression_edge_cases():
    # Test with minimal data
    X = np.array([[1.0], [2.0]])
    y = np.array([2.0, 4.0])
    coefficients, fitted = linregress(X, y)
    assert len(coefficients) == 2  # intercept + 1 feature
    assert len(fitted) == 2
    
    # Test perfect fit case
    X = np.array([[1.0], [2.0], [3.0]])
    y = 2 + 3 * X[:, 0]  # y = 2 + 3x
    coefficients, fitted = linregress(X, y)
    np.testing.assert_allclose(coefficients, [2, 3], rtol=1e-10)
    np.testing.assert_allclose(fitted, y, rtol=1e-10) 