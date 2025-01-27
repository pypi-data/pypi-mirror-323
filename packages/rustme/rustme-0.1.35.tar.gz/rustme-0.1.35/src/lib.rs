use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyAny, PyDict, PyList};

use numpy::{PyArray1, PyArray2};
use ndarray::{Array1, Array2, ArrayView1, ArrayView2};
use statrs::distribution::{Continuous, Normal, ContinuousCDF};

/// Add significance stars.
fn add_significance_stars(p: f64) -> &'static str {
    if p < 0.01 {
        "***"
    } else if p < 0.05 {
        "**"
    } else if p < 0.1 {
        "*"
    } else {
        ""
    }
}

/// Downcast a Python object to NumPy PyArray2<f64> => ndarray::ArrayView2<f64>.
///
/// Marked unsafe because .as_array() in pyo3-numpy is unsafe, trusting Python memory is valid.
fn as_array2_f64<'py>(obj: &'py PyAny) -> PyResult<ArrayView2<'py, f64>> {
    let pyarray = obj.downcast::<PyArray2<f64>>()?;
    let view = unsafe { pyarray.as_array() };
    Ok(view)
}

/// Similarly, for 1D arrays.
fn as_array1_f64<'py>(obj: &'py PyAny) -> PyResult<ArrayView1<'py, f64>> {
    let pyarray = obj.downcast::<PyArray1<f64>>()?;
    let view = unsafe { pyarray.as_array() };
    Ok(view)
}

/// Extracts (beta, cov_beta, exog_names, X) from the Python Probit model via direct bridging.
/// For zero-copy, params, cov_params(), and model.exog must be NumPy arrays, not Pandas.
fn extract_probit_model_components<'py>(
    _py: Python<'py>,
    probit_model: &'py PyAny,
) -> PyResult<(Array1<f64>, Array2<f64>, Vec<String>, Array2<f64>)> {
    // Beta (params)
    let params_obj = probit_model.getattr("params")?;
    let beta_view = as_array1_f64(params_obj)?;
    let beta = beta_view.to_owned(); // Owned Array1

    // Cov beta
    let cov_obj = probit_model.call_method0("cov_params")?;
    let cov_view = as_array2_f64(cov_obj)?;
    let cov_beta = cov_view.to_owned(); // Owned Array2

    // exog_names
    let exog_names_py: Vec<String> = probit_model
        .getattr("model")?
        .getattr("exog_names")?
        .extract()?;

    // X
    let x_obj = probit_model.getattr("model")?.getattr("exog")?;
    let x_view = as_array2_f64(x_obj)?;
    let X = x_view.to_owned(); // Owned Array2

    Ok((beta, cov_beta, exog_names_py, X))
}

/// A chunked AME function using vectorized ops in ndarray.
#[pyfunction]
fn ame<'py>(
    py: Python<'py>,
    probit_model: &'py PyAny,
    chunk_size: Option<usize>,
) -> PyResult<&'py PyAny> { // Changed return type to PyAny to return DataFrame
    // 1) Extract model components as owned arrays
    let (beta, cov_beta, exog_names, X) = extract_probit_model_components(py, probit_model)?;

    let (n, k) = (X.nrows(), X.ncols());
    let chunk = chunk_size.unwrap_or(n);

    // 2) Identify intercept indices
    let intercept_indices: Vec<usize> = exog_names
        .iter()
        .enumerate()
        .filter_map(|(i, nm)| {
            let ln = nm.to_lowercase();
            if ln == "const" || ln == "intercept" {
                Some(i)
            } else {
                None
            }
        })
        .collect();

    // Identify discrete columns (dummy variables)
    let is_discrete: Vec<usize> = exog_names
        .iter()
        .enumerate()
        .filter_map(|(j, _nm)| { // Renamed 'nm' to '_nm' to suppress warning
            if intercept_indices.contains(&j) {
                None
            } else {
                let col_j = X.column(j);
                if col_j.iter().all(|&v| v == 0.0 || v == 1.0) {
                    Some(j)
                } else {
                    None
                }
            }
        })
        .collect();

    // 3) Prepare accumulators
    let mut sum_ame = vec![0.0; k];
    let mut partial_jl_sums = vec![0.0; k * k];
    let normal = Normal::new(0.0, 1.0).unwrap();

    // Define an index function for [j][l]
    let index = |j: usize, l: usize| -> usize { j * k + l };

    // 4) Process data in chunks
    let mut idx_start = 0;
    while idx_start < n {
        let idx_end = (idx_start + chunk).min(n);

        let x_chunk = X.slice(ndarray::s![idx_start..idx_end, ..]); // shape (n_chunk, k)

        // Vectorized dot => z_chunk = x_chunk.dot(&beta)  => shape (n_chunk)
        let z_chunk = x_chunk.dot(&beta);
        let phi_vals = z_chunk.mapv(|z| normal.pdf(z)); // shape (n_chunk)

        // Processing discrete variables individually
        for &j in &is_discrete {
            // Create copies with only the j-th discrete variable altered
            let mut x_j1 = x_chunk.to_owned();
            let mut x_j0 = x_chunk.to_owned();
            x_j1.column_mut(j).fill(1.0);
            x_j0.column_mut(j).fill(0.0);

            // Compute z_j1 and z_j0
            let z_j1 = x_j1.dot(&beta); // shape (n_chunk)
            let z_j0 = x_j0.dot(&beta); // shape (n_chunk)

            // Compute CDFs
            let cdf_j1 = z_j1.mapv(|z| normal.cdf(z)); // shape (n_chunk)
            let cdf_j0 = z_j0.mapv(|z| normal.cdf(z)); // shape (n_chunk)

            // Compute discrete sum for variable j
            let disc_sum = cdf_j1.sum() - cdf_j0.sum();
            sum_ame[j] += disc_sum;

            // Compute gradients
            let pdf_j1 = z_j1.mapv(|z| normal.pdf(z)); // shape (n_chunk)
            let pdf_j0 = z_j0.mapv(|z| normal.pdf(z)); // shape (n_chunk)

            for l in 0..k {
                // Correct gradient calculation: sum over i of (pdf_j1[i] * X_j1[i, l] - pdf_j0[i] * X_j0[i, l])
                let grad = (&pdf_j1 * &x_j1.slice(ndarray::s![.., l])) - (&pdf_j0 * &x_j0.slice(ndarray::s![.., l]));
                partial_jl_sums[j * k + l] += grad.sum();
            }
        }

        // Processing continuous variables
        for j in 0..k {
            if intercept_indices.contains(&j) || is_discrete.contains(&j) {
                continue; // Skip intercepts and discrete variables
            }
            // Continuous variables
            let beta_j = beta[j];
            let sum_zphi = phi_vals.sum();
            sum_ame[j] += beta_j * sum_zphi;

            for l in 0..k {
                // Correct gradient calculation: beta[j] * sum(-z_i * x_i[l] * phi(z_i))
                let zx = &z_chunk * &x_chunk.slice(ndarray::s![.., l]);
                let grad = beta_j * (-zx.dot(&phi_vals));
                partial_jl_sums[index(j, l)] += grad;

                // Debug: Print grad and updated partial_jl_sums
                eprintln!(
                    "Continuous Variable j: {}, Parameter l: {}, grad: {}, partial_jl_sums[j * k + l]: {}",
                    j,
                    l,
                    grad,
                    partial_jl_sums[index(j, l)]
                );
            }

            // Update the diagonal
            partial_jl_sums[index(j, j)] += phi_vals.sum();
            eprintln!(
                "Continuous Variable j: {}, Updated partial_jl_sums[j * k + j]: {}",
                j,
                partial_jl_sums[index(j, j)]
            );
        }

        idx_start = idx_end;
    }

    // 5) Compute AME and Covariance
    let ame: Vec<f64> = sum_ame.iter().map(|v| v / n as f64).collect();

    // grad_ame => partial_jl_sums / n
    let mut grad_ame = Array2::<f64>::zeros((k, k));
    for j in 0..k {
        for l in 0..k {
            grad_ame[[j, l]] = partial_jl_sums[j * k + l] / (n as f64);
        }
    }

    // Debug: Print Gradient Matrix
    eprintln!("Gradient Matrix (grad_ame): \n{:?}", grad_ame);

    // Covariance of AME: grad_ame * cov_beta * grad_ame^T
    let cov_ame = grad_ame.dot(&cov_beta).dot(&grad_ame.t());

    // Debug: Print Covariance Matrix
    eprintln!("Covariance Matrix (cov_ame): \n{:?}", cov_ame);

    // Extract variances and standard errors
    let var_ame: Vec<f64> = cov_ame.diag().iter().map(|&v| if v < 0.0 { 0.0 } else { v }).collect();
    let se_ame: Vec<f64> = var_ame.iter().map(|v| v.sqrt()).collect();

    // Compute z-scores and p-values
    let mut z_vals = Vec::with_capacity(k);
    let mut p_vals = Vec::with_capacity(k);
    for i in 0..k {
        if se_ame[i].abs() < f64::EPSILON {
            z_vals.push(f64::NAN);
            p_vals.push(f64::NAN);
        } else {
            let z = ame[i] / se_ame[i];
            z_vals.push(z);
            let absz = z.abs();
            p_vals.push(2.0 * (1.0 - normal.cdf(absz)));
        }
    }

    // 6) Collect Data for DataFrame
    let mut dy_dx = Vec::new();
    let mut se_err = Vec::new();
    let mut z_vals_col = Vec::new();
    let mut p_vals_col = Vec::new();
    let mut significance_col = Vec::new();
    let mut param_names_filtered = Vec::new();

    for j in 0..k {
        if intercept_indices.contains(&j) {
            continue; // Skip intercepts
        }
        dy_dx.push(ame[j]);
        se_err.push(se_ame[j]);
        z_vals_col.push(z_vals[j]);
        p_vals_col.push(p_vals[j]);
        significance_col.push(add_significance_stars(p_vals[j]).to_string());
        param_names_filtered.push(exog_names[j].clone());
    }

    // 7) Build the DataFrame
    // Import pandas
    let pd = py.import("pandas")?;

    // Create Python lists for each column
    let dy_dx_py = PyList::new(py, &dy_dx);
    let se_err_py = PyList::new(py, &se_err);
    let z_py = PyList::new(py, &z_vals_col);
    let p_val_py = PyList::new(py, &p_vals_col);
    let significance_py = PyList::new(py, &significance_col);
    let index_py = PyList::new(py, &param_names_filtered);

    // Create a Python dictionary for the DataFrame data
    let data = PyDict::new(py);
    data.set_item("dy/dx", dy_dx_py)?;
    data.set_item("Std. Err", se_err_py)?;
    data.set_item("z", z_py)?;
    data.set_item("Pr(>|z|)", p_val_py)?;
    data.set_item("Significance", significance_py)?;

    // Create a Python dictionary for keyword arguments
    let kwargs = PyDict::new(py);
    kwargs.set_item("data", data)?;
    kwargs.set_item("index", index_py)?;

    // Construct the DataFrame
    let df = pd.call_method("DataFrame", (), Some(kwargs))?;

    // Optional: Print final AME results for debugging
    eprintln!("Final AME Results: {:?}", df);

    // 8) Return the DataFrame
    Ok(df)
}

/// Expose ame as part of the rustme Python module
#[pymodule]
fn rustme_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ame, m)?)?;
    Ok(())
}