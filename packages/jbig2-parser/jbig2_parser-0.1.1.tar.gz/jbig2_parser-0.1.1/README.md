# jbig2_parser

`jbig2_parser` is a Python library powered by Rust, designed to decode JBIG2 images and convert them into formats like PNG that can be processed by Python libraries such as Pillow (PIL). 

This package leverages the Rust crate `jbig2dec` for efficient and accurate JBIG2 decoding, combined with `pyo3` to provide seamless Python bindings.

---

## Features

- Decode JBIG2-encoded images.
- Convert JBIG2 images to PNG buffers compatible with Python's `Pillow`.
- Easy-to-use API for integrating JBIG2 decoding in Python projects.

---

## Installation

### Prerequisites

1. **Rust Toolchain**:
   Install Rust by following the instructions at [rust-lang.org](https://rust-lang.org/tools/install).

2. **Python Environment**:
   Ensure you have Python 3.7 or higher installed. Set up a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
