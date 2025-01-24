#![cfg_attr(coverage_nightly, feature(coverage_attribute))]
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[cfg_attr(coverage_nightly, coverage(off))]
pub mod amplitudes;
#[cfg_attr(coverage_nightly, coverage(off))]
pub mod data;
#[cfg_attr(coverage_nightly, coverage(off))]
pub mod utils;

pub trait GetStrExtractObj {
    fn get_extract<T>(&self, key: &str) -> PyResult<Option<T>>
    where
        T: for<'py> FromPyObject<'py>;
}

#[cfg_attr(coverage_nightly, coverage(off))]
impl GetStrExtractObj for Bound<'_, PyDict> {
    fn get_extract<T>(&self, key: &str) -> PyResult<Option<T>>
    where
        T: for<'py> FromPyObject<'py>,
    {
        self.get_item(key)?
            .map(|value| value.extract::<T>())
            .transpose()
    }
}
