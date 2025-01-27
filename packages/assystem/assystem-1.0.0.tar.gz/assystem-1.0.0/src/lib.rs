use pyo3::{
    create_exception,
    exceptions::{PyFileNotFoundError, PyIOError, PyKeyError, PyPermissionError},
    prelude::*,
    types::{PyBytes, PyString},
};

#[pyclass]
struct ASS {
    inner: ::assystem::ASS<std::fs::File>,
}

create_exception!(assystem, Assless, pyo3::exceptions::PyException);

fn io_error_rust_to_python(err: std::io::Error) -> PyErr {
    let str = err.to_string();
    match err.kind() {
        std::io::ErrorKind::PermissionDenied => PyPermissionError::new_err(str),
        std::io::ErrorKind::NotFound => PyFileNotFoundError::new_err(str),
        _ => PyIOError::new_err(str),
    }
}

#[pymethods]
impl ASS {
    #[new]
    pub fn new(file_path: Bound<PyString>) -> PyResult<Self> {
        let file_path = file_path.to_str()?;
        let file = match std::fs::OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(&file_path)
        {
            Ok(file) => file,
            Err(err) => return Err(io_error_rust_to_python(err)),
        };
        let inner = match ::assystem::ASS::open(file) {
            Err(::assystem::OpeningError::IO(err)) => return Err(io_error_rust_to_python(err)),
            Err(::assystem::OpeningError::Assless()) => {
                return Err(Assless::new_err(format!(
                    "{} is not an ASS file of the needed version",
                    file_path
                )));
            }
            Ok(inner) => inner,
        };
        Ok(Self { inner })
    }

    pub fn get<'a>(&mut self, key: Bound<'a, PyBytes>) -> PyResult<Bound<'a, PyBytes>> {
        match self.inner.get(key.as_bytes()) {
            None => Err(PyKeyError::new_err(key.unbind())),
            Some(value) => Ok(PyBytes::new(key.py(), &value)),
        }
    }

    pub fn set<'a>(
        &mut self,
        key: Bound<'a, PyBytes>,
        value: Bound<'a, PyBytes>,
    ) -> PyResult<Option<Bound<'a, PyBytes>>> {
        match self.inner.set(key.as_bytes(), value.as_bytes()) {
            None => Ok(None),
            Some(old_value) => Ok(Some(PyBytes::new(key.py(), &old_value))),
        }
    }

    pub fn remove<'a>(&mut self, key: Bound<'a, PyBytes>) -> PyResult<Bound<'a, PyBytes>> {
        match self.inner.remove(key.as_bytes()) {
            None => Err(PyKeyError::new_err(key.unbind())),
            Some(value) => Ok(PyBytes::new(key.py(), &value)),
        }
    }
}

#[pymodule]
fn assystem(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ASS>()?;
    Ok(())
}
