import numpy as np
import pandas as pd
from scipy.stats import norm

def ame_chunk(probit_model, chunk_size=10_000):
    """
    Compute average marginal effects (AME) for a Probit model via a (potentially) chunked approach.
    Automatically detects dummy columns (0/1) and applies a discrete-difference approach for them.
    Excludes intercept terms from marginal effects computation.

    Parameters
    ----------
    probit_model : statsmodels.discrete.discrete_model.BinaryResults
        A fitted Probit model, e.g. sm.Probit(...).fit().
    chunk_size : int, optional
        Default is 10,000. The number of rows processed in each chunk.

    Returns
    -------
    results_df : pandas.DataFrame
        DataFrame with columns:
        - "dy/dx": the AME for each parameter
        - "Std. Err": standard error
        - "z": z-statistic
        - "Pr(>|z|)": p-value (two-sided)
        - "Significance": stars based on p-value
    """

    # Extract parameters & covariance
    beta_ = probit_model.params
    cov_beta_ = probit_model.cov_params()

    # Extract exogenous variable names from the model
    if hasattr(probit_model, 'model') and hasattr(probit_model.model, 'exog_names'):
        exog_names = list(probit_model.model.exog_names)
    else:
        # Fallback if exog_names are not available
        exog_names = list(beta_.index) if hasattr(beta_, 'index') else [f"var_{i}" for i in range(len(beta_))]

    # Extract X from the model
    if hasattr(probit_model, 'model') and hasattr(probit_model.model, 'exog'):
        X_values = probit_model.model.exog
    else:
        raise ValueError("Probit model does not have 'model.exog' attribute.")

    # Handle both pandas and numpy data types
    beta = beta_.values if hasattr(beta_, 'values') else np.asarray(beta_)
    param_names = exog_names
    cov_beta = cov_beta_.values if hasattr(cov_beta_, 'values') else np.asarray(cov_beta_)

    N, k = X_values.shape

    # Detect intercept columns
    intercept_indices = [i for i, name in enumerate(param_names) if name.lower() in ['const', 'intercept']]

    # Detect dummy columns
    def is_dummy_column(col):
        unique_vals = np.unique(col)
        return np.array_equal(unique_vals, [0., 1.]) or np.array_equal(unique_vals, [0.]) or np.array_equal(unique_vals, [1.])

    is_discrete = [j for j in range(k) if j not in intercept_indices and is_dummy_column(X_values[:, j])]

    # Remove intercept from computations
    keep_idx = [i for i in range(k) if i not in intercept_indices]

    # Prepare accumulators
    sum_ame = np.zeros(k, dtype=float)
    partial_jl_sums = np.zeros((k, k), dtype=float)

    # Process data in chunks
    idx_start = 0
    while idx_start < N:
        idx_end = min(idx_start + chunk_size, N)
        X_chunk = X_values[idx_start:idx_end, :]
        z_chunk = X_chunk @ beta
        phi_vals = norm.pdf(z_chunk)

        for j in keep_idx:  # Skip intercepts entirely
            if j in is_discrete:
                # Discrete difference
                X_j1, X_j0 = X_chunk.copy(), X_chunk.copy()
                X_j1[:, j] = 1.0
                X_j0[:, j] = 0.0
                z_j1, z_j0 = X_j1 @ beta, X_j0 @ beta
                cdf_j1, cdf_j0 = norm.cdf(z_j1), norm.cdf(z_j0)
                disc_chunk = cdf_j1 - cdf_j0
                sum_ame[j] += disc_chunk.sum()
                pdf_j1, pdf_j0 = norm.pdf(z_j1), norm.pdf(z_j0)
                grad_chunk = pdf_j1[:, None] * X_j1 - pdf_j0[:, None] * X_j0
                partial_jl_sums[j, :] += grad_chunk.sum(axis=0)
            else:
                # Continuous variables
                sum_ame[j] += (phi_vals * beta[j]).sum()
                zphi = -(z_chunk * phi_vals)[:, None] * X_chunk
                sum_zphi = zphi.sum(axis=0)
                sum_phi = phi_vals.sum()
                partial_jl_sums[j, :] += beta[j] * sum_zphi
                partial_jl_sums[j, j] += sum_phi

        idx_start = idx_end

    # Average & Delta-Method StdErr
    AME = sum_ame / N
    grad_AME = partial_jl_sums / N
    cov_AME = grad_AME @ cov_beta @ grad_AME.T
    var_AME = np.diag(cov_AME).copy()
    var_AME[var_AME < 0] = 0.0
    se_AME = np.sqrt(var_AME)
    z_vals = np.divide(AME, se_AME, out=np.full_like(AME, np.nan), where=(se_AME != 0))
    p_vals = 2 * (1 - norm.cdf(np.abs(z_vals)))

    # Significance stars
    def add_significance_stars(p):
        if p < 0.01:
            return "***"
        elif p < 0.05:
            return "**"
        elif p < 0.1:
            return "*"
        return ""

    significance = [add_significance_stars(p) for p in p_vals]
    p_vals_str = [f"{p:.3f}" for p in p_vals]

    # Build DataFrame excluding intercepts
    results_df = pd.DataFrame({
        "dy/dx": AME[keep_idx],
        "Std. Err": se_AME[keep_idx],
        "z": z_vals[keep_idx],
        "Pr(>|z|)": [p_vals_str[i] for i in keep_idx],
        "Significance": [significance[i] for i in keep_idx]
    }, index=[param_names[i] for i in keep_idx])

    return results_df