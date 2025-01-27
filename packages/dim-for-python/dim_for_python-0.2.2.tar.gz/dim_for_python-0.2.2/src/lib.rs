mod operations;

use pyo3::prelude::*;
use pyo3::types::PyModule;

/// dim-python: A Python module for text and image vectorization using OpenAI models
/// 
/// This module provides functions to vectorize text and images into fixed-length
/// feature vectors using OpenAI's embedding and vision models.
///
/// Functions:
///   - vectorize_string: Convert text into a feature vector using text embeddings
///   - vectorize_image: Convert an image into a feature vector using vision models
#[pymodule]
fn dim_python(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(operations::vectorize_string, m)?)?;
    m.add_function(wrap_pyfunction!(operations::vectorize_image, m)?)?;
    Ok(())
}
