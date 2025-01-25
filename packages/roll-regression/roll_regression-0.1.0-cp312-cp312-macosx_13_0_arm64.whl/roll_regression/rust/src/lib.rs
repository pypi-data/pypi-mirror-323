extern crate nalgebra;
use std::os::raw::c_int;
use nalgebra::{DMatrix, DVector};

#[allow(dead_code)]
#[no_mangle]
pub extern "C" fn spare() {
    // https://github.com/rust-lang/rust/issues/38281 😂
    println!("");
    //adding this (doesn't have to be named "spare") makes the compilation work.
    // you don't even need to add this function signature where you're using these functions.
}

#[no_mangle]
pub extern "C" fn linregress(
    a_ptr: *const f64,      // Pointer to matrix A
    y_ptr: *const f64,      // Pointer to array y
    n_rows: c_int,          // Number of rows in A and length of y
    n_cols: c_int,          // Number of columns in A
    coef_ptr: *mut f64,     // Pointer to store coefficients (intercept + betas)
    fitted_ptr: *mut f64    // Pointer to store fitted values
) -> c_int {
    // Safety checks
    if a_ptr.is_null() || y_ptr.is_null() || coef_ptr.is_null() || fitted_ptr.is_null() {
        return 0;
    }

    // Convert raw pointers to slices
    let a_slice = unsafe {
        std::slice::from_raw_parts(a_ptr, (n_rows * n_cols) as usize)
    };
    let y_slice = unsafe {
        std::slice::from_raw_parts(y_ptr, n_rows as usize)
    };

    // Convert to nalgebra types
    let x = DMatrix::from_row_slice(n_rows as usize, n_cols as usize, a_slice);
    let y = DVector::from_row_slice(y_slice);

    // Add constant term for intercept
    let mut x_with_intercept = DMatrix::from_element(n_rows as usize, (n_cols + 1) as usize, 1.0);
    x_with_intercept.slice_mut((0, 1), (n_rows as usize, n_cols as usize))
        .copy_from(&x);

    // Calculate β = (XᵀX)⁻¹Xᵀy
    match (x_with_intercept.transpose() * &x_with_intercept).try_inverse() {
        Some(xtx_inv) => {
            let coefficients = xtx_inv * x_with_intercept.transpose() * y;
            
            // Calculate fitted values: ŷ = Xβ
            let fitted = &x_with_intercept * &coefficients;
            
            // Copy coefficients to output pointer
            unsafe {
                std::ptr::copy_nonoverlapping(
                    coefficients.as_slice().as_ptr(),
                    coef_ptr,
                    (n_cols + 1) as usize
                );
                
                // Copy fitted values to output pointer
                std::ptr::copy_nonoverlapping(
                    fitted.as_slice().as_ptr(),
                    fitted_ptr,
                    n_rows as usize
                );
            }
            1
        },
        None => 0  // Matrix is singular
    }
}

#[no_mangle]
pub extern "C" fn roll_linregress(
    a_ptr: *const f64,
    y_ptr: *const f64,
    n_rows: c_int,
    n_cols: c_int,
    window: c_int,
    coef_ptr: *mut f64,
    fitted_ptr: *mut f64
) -> c_int {
    // Safety checks
    if a_ptr.is_null() || y_ptr.is_null() || coef_ptr.is_null() || fitted_ptr.is_null() {
        return 0;
    }
    if window <= 0 || window > n_rows {
        return 0;
    }

    // Convert raw pointers to slices
    let a_slice = unsafe {
        std::slice::from_raw_parts(a_ptr, (n_rows * n_cols) as usize)
    };
    let y_slice = unsafe {
        std::slice::from_raw_parts(y_ptr, n_rows as usize)
    };

    // Number of rolling windows
    let n_windows = (n_rows - window + 1) as usize;
    let n_cols = n_cols as usize;
    let window = window as usize;

    // For each window
    for i in 0..n_windows {
        // Extract window data
        let window_a = DMatrix::from_row_slice(
            window,
            n_cols,
            &a_slice[i * n_cols..(i + window) * n_cols]
        );
        let window_y = DVector::from_row_slice(
            &y_slice[i..i + window]
        );

        // Add constant term for intercept
        let mut x_with_intercept = DMatrix::from_element(window, n_cols + 1, 1.0);
        x_with_intercept.view_mut((0, 1), (window, n_cols))
            .copy_from(&window_a);

        // Calculate β = (XᵀX)⁻¹Xᵀy
        match (x_with_intercept.transpose() * &x_with_intercept).try_inverse() {
            Some(xtx_inv) => {
                let coefficients = xtx_inv * x_with_intercept.transpose() * window_y;
                let fitted = &x_with_intercept * &coefficients;
                
                unsafe {
                    // Copy coefficients for this window
                    std::ptr::copy_nonoverlapping(
                        coefficients.as_slice().as_ptr(),
                        coef_ptr.add(i * (n_cols + 1)),
                        n_cols + 1
                    );
                    
                    // Copy fitted values for this window
                    std::ptr::copy_nonoverlapping(
                        fitted.as_slice().as_ptr(),
                        fitted_ptr.add(i * window),
                        window
                    );
                }
            },
            None => return 0  // Matrix is singular
        }
    }

    1
}

#[test]
fn test_linregress() {
    // Test case: y = 2 + 3x₁ + 4x₂
    let a = vec![
        1.0, 2.0,  // First row
        2.0, 3.0,  // Second row
        3.0, 4.0,  // Third row
        4.0, 5.0   // Fourth row
    ];
    let y = vec![
        16.0,  // 2 + 3(1) + 4(2) = 13
        23.0,  // 2 + 3(2) + 4(3) = 20
        30.0,  // 2 + 3(3) + 4(4) = 27
        37.0   // 2 + 3(4) + 4(5) = 34
    ];
    
    let mut coefficients = vec![0.0; 3];  // Space for intercept and two coefficients
    let mut fitted = vec![0.0; 4];        // Space for fitted values
    
    let status = linregress(
        a.as_ptr(),
        y.as_ptr(),
        4,    // n_rows
        2,    // n_cols
        coefficients.as_mut_ptr(),
        fitted.as_mut_ptr()
    );
    
    assert_eq!(status, 1);
    
    // Check if coefficients are close to expected values
    assert!((coefficients[0] - 2.0).abs() < 1e-10);  // intercept ≈ 2
    assert!((coefficients[1] - 3.0).abs() < 1e-10);  // β₁ ≈ 3
    assert!((coefficients[2] - 4.0).abs() < 1e-10);  // β₂ ≈ 4
    
    // Check fitted values
    for i in 0..4 {
        let expected = 2.0 + 3.0 * (i as f64 + 1.0) + 4.0 * (i as f64 + 2.0);
        assert!((fitted[i] - expected).abs() < 1e-10);
    }
}

#[test]
fn test_roll_linregress() {
    // Test case: y = 2 + 3x₁ + 4x₂ with increasing trend
    let a = vec![
        1.0, 1.0,  // First row
        2.0, 2.0,  // Second row
        3.0, 3.0,  // Third row
        4.0, 4.0,  // Fourth row
        5.0, 5.0   // Fifth row
    ];
    let y = vec![
        9.0,   // 2 + 3(1) + 4(1) = 9
        16.0,  // 2 + 3(2) + 4(2) = 16
        23.0,  // 2 + 3(3) + 4(3) = 23
        30.0,  // 2 + 3(4) + 4(4) = 30
        37.0   // 2 + 3(5) + 4(5) = 37
    ];
    
    let window = 3;
    let n_windows = 3;  // 5 - 3 + 1 = 3 windows
    
    let mut coefficients = vec![0.0; n_windows * 3];  // 3 coefficients per window
    let mut fitted = vec![0.0; n_windows * window];   // window-size fitted values per window
    
    let status = roll_linregress(
        a.as_ptr(),
        y.as_ptr(),
        5,     // n_rows
        2,     // n_cols
        3,     // window
        coefficients.as_mut_ptr(),
        fitted.as_mut_ptr()
    );
    
    assert_eq!(status, 1);
    
    // Check results for each window
    for i in 0..n_windows {
        // The coefficients should be approximately the same for each window
        // since we generated the data with constant coefficients
        assert!((coefficients[i * 3] - 2.0).abs() < 1e-10);     // intercept ≈ 2
        assert!((coefficients[i * 3 + 1] - 3.0).abs() < 1e-10); // β₁ ≈ 3
        assert!((coefficients[i * 3 + 2] - 4.0).abs() < 1e-10); // β₂ ≈ 4
    }
}