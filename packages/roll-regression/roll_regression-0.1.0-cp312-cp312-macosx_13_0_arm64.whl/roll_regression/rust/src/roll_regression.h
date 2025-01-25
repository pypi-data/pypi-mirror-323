
int is_prime(const int n);

void linregress(
    const double* A, const double* y, int n_rows, int n_cols, 
    double* coefficients, double* fitted
);

void roll_linregress(
    const double* A, const double* y, int n_rows, int n_cols, int window,
    double* coefficients, double* fitted
);