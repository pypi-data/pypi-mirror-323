use jbig2dec::Document;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::io::Cursor;

/// Parses a JBIG2 image buffer and returns a PNG buffer compatible with Python Imaging Library (PIL).
///
/// # Arguments
/// * `input_buffer` - A byte buffer containing the JBIG2 encoded data.
///
/// Returns:
/// A byte buffer representing the decoded image in PNG format.
#[pyfunction]
fn parse_jbig2(input_buffer: Vec<u8>) -> PyResult<Vec<u8>> {
    let mut cursor = Cursor::new(input_buffer);

    let document = Document::from_reader(&mut cursor).map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to decode JBIG2: {:?}", e))
    })?;

    let image = document
        .images()
        .get(0)
        .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("No images found in the document"))?;

    let png_data = image.to_png().map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to convert image to PNG: {:?}", e))
    })?;

    Ok(png_data)
}

#[pymodule]
fn jbig2_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_jbig2, m)?)?;
    Ok(())
}
