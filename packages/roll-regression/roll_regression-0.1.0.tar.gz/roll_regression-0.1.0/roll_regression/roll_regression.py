# -*- coding: utf-8 -*-
import os.path
import os
import sys
from cffi import FFI
import numpy as np
from ctypes import CDLL, c_double, c_int, POINTER

# See https://github.com/SimonSapin/hello-pyrust


if sys.platform == 'win32':
    DYNAMIC_LIB_FORMAT = '%s.dll'
elif sys.platform == 'darwin':
    DYNAMIC_LIB_FORMAT = 'lib%s.dylib'
elif "linux" in sys.platform:
    DYNAMIC_LIB_FORMAT = 'lib%s.so'
else:
    raise NotImplementedError('No implementation for "{}".'
                              ' Supported platforms are '
                              '"win32", "darwin", and "linux"'
                              ''.format(sys.platform))
ffi = FFI()
(file_path, _) = os.path.split(__file__)
cwd = os.getcwd()

h_path = os.path.join(file_path, 'rust', 'src', 'roll_regression.h',)
h_rel_path = os.path.join(os.curdir, os.path.relpath(h_path, cwd))

dlib_path = os.path.join(file_path, 'rust', 'target', 'release', 
                         DYNAMIC_LIB_FORMAT % 'roll_regression')
dlib_rel_path = os.path.join(os.curdir, os.path.relpath(dlib_path, cwd))

with open(h_rel_path) as h:
    ffi.cdef(h.read())

# Get the absolute path to the shared library
lib_path = os.path.join(os.path.dirname(__file__), "rust", "target", "release")
if sys.platform == "darwin":
    lib_name = "libroll_regression.dylib"
elif sys.platform == "win32":
    lib_name = "roll_regression.dll"
else:
    lib_name = "libroll_regression.so"

rust_lib = CDLL(os.path.join(lib_path, lib_name))

# Define argument types for linregress
rust_lib.linregress.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64),  # A
    np.ctypeslib.ndpointer(dtype=np.float64),  # y
    c_int,                                     # n_rows
    c_int,                                     # n_cols
    np.ctypeslib.ndpointer(dtype=np.float64),  # coefficients
    np.ctypeslib.ndpointer(dtype=np.float64)   # fitted
]
rust_lib.linregress.restype = c_int

# Define argument types for roll_linregress
rust_lib.roll_linregress.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float64),  # A
    np.ctypeslib.ndpointer(dtype=np.float64),  # y
    c_int,                                     # n_rows
    c_int,                                     # n_cols
    c_int,                                     # window
    np.ctypeslib.ndpointer(dtype=np.float64),  # coefficients
    np.ctypeslib.ndpointer(dtype=np.float64)   # fitted
]
rust_lib.roll_linregress.restype = c_int

def linregress(A: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Perform linear regression.
    
    Args:
        A: Input matrix of shape (n_samples, n_features)
        y: Target vector of shape (n_samples,)
        
    Returns:
        tuple: (coefficients, fitted_values)
            - coefficients: array of shape (n_features + 1,) containing regression coefficients
            - fitted_values: array of shape (n_samples,) containing fitted values
    """
    A = np.ascontiguousarray(A, dtype=np.float64)
    y = np.ascontiguousarray(y, dtype=np.float64)
    
    n_rows, n_cols = A.shape
    coefficients = np.zeros(n_cols + 1, dtype=np.float64)
    fitted = np.zeros(n_rows, dtype=np.float64)
    
    status = rust_lib.linregress(
        A, y, n_rows, n_cols,
        coefficients, fitted
    )
    
    if status == 0:
        raise RuntimeError("Linear regression failed")
        
    return coefficients, fitted

def roll_linregress(A: np.ndarray, y: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Perform rolling linear regression with specified window size.
    
    Args:
        A: Input matrix of shape (n_samples, n_features)
        y: Target vector of shape (n_samples,)
        window: Size of the rolling window
        
    Returns:
        tuple: (coefficients, fitted_values)
            - coefficients: array of shape (n_windows, n_features + 1) containing regression coefficients
            - fitted_values: array of shape (n_windows, window) containing fitted values
    """
    A = np.ascontiguousarray(A, dtype=np.float64)
    y = np.ascontiguousarray(y, dtype=np.float64)
    
    n_rows, n_cols = A.shape
    n_windows = n_rows - window + 1
    
    coefficients = np.zeros((n_windows, n_cols + 1), dtype=np.float64)
    fitted = np.zeros((n_windows, window), dtype=np.float64)
    
    status = rust_lib.roll_linregress(
        A, y, n_rows, n_cols, window,
        coefficients.ravel(), fitted.ravel()
    )
    
    if status == 0:
        raise RuntimeError("Rolling regression failed")
        
    return coefficients, fitted
