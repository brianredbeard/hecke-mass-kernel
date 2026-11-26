use hecke_mass_kernel::{
    self as kernel, BigInt, BigRational, BigUint, OrbitAccumulator, OrbitOutcome,
};
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyInt, PyModule};

fn integer(value: &Bound<'_, PyAny>, name: &str) -> PyResult<BigInt> {
    if !value.is_instance_of::<PyInt>() || value.is_instance_of::<PyBool>() {
        return Err(PyTypeError::new_err(format!("{name} must be an int")));
    }
    value.extract()
}

fn natural(value: &Bound<'_, PyAny>, name: &str) -> PyResult<BigUint> {
    BigUint::try_from(integer(value, name)?)
        .map_err(|_| PyValueError::new_err(format!("{name} must be nonnegative")))
}

fn fraction_class(py: Python<'_>) -> PyResult<Bound<'_, PyAny>> {
    PyModule::import(py, "fractions")?.getattr("Fraction")
}

fn rational(
    value: &Bound<'_, PyAny>,
    fraction: &Bound<'_, PyAny>,
    name: &str,
) -> PyResult<BigRational> {
    if value.is_instance_of::<PyInt>() {
        return Ok(BigRational::from_integer(integer(value, name)?));
    }
    if !value.is_instance(fraction)? {
        return Err(PyTypeError::new_err(format!(
            "{name} must be an int or fractions.Fraction"
        )));
    }
    let numerator = integer(&value.getattr("numerator")?, "Fraction numerator")?;
    let denominator = integer(&value.getattr("denominator")?, "Fraction denominator")?;
    if denominator <= BigInt::from(0) {
        return Err(PyValueError::new_err(
            "Fraction denominator must be positive",
        ));
    }
    Ok(BigRational::new(numerator, denominator))
}

fn to_fraction(fraction: &Bound<'_, PyAny>, value: &BigRational) -> PyResult<Py<PyAny>> {
    Ok(fraction.call1((value.numer(), value.denom()))?.unbind())
}

fn collect_iterable<T>(
    values: &Bound<'_, PyAny>,
    mut parse: impl FnMut(&Bound<'_, PyAny>) -> PyResult<T>,
) -> PyResult<Vec<T>> {
    values.try_iter()?.map(|value| parse(&value?)).collect()
}

/// Return the exact reciprocal sum of integer stabilizer orders.
///
/// Orders are nonnegative. A zero order contributes zero.
#[pyfunction]
fn class_mass(py: Python<'_>, orders: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    let orders = collect_iterable(orders, |value| natural(value, "stabilizer order"))?;
    let result = py.detach(|| kernel::class_mass(&orders));
    to_fraction(&fraction_class(py)?, &result)
}

/// Return the exact normalized Hecke sum as a fractions.Fraction.
///
/// q, k, and rank are nonnegative integers. u and the samples are integers or
/// fractions.Fraction values. A zero inverse contributes zero.
#[pyfunction]
fn hecke(
    py: Python<'_>,
    u: &Bound<'_, PyAny>,
    q: &Bound<'_, PyAny>,
    k: &Bound<'_, PyAny>,
    rank: &Bound<'_, PyAny>,
    samples: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let fraction = fraction_class(py)?;
    let u = rational(u, &fraction, "u")?;
    let q = natural(q, "q")?;
    let k = natural(k, "k")?;
    let rank = natural(rank, "rank")?;
    let samples = collect_iterable(samples, |value| rational(value, &fraction, "sample"))?;
    let result = py.detach(|| kernel::hecke(&u, &q, &k, &rank, &samples));
    to_fraction(&fraction, &result)
}

/// Check detailed balance of an exact square matrix with positive stabilizer orders.
#[pyfunction]
fn check_detailed_balance(
    py: Python<'_>,
    orders: &Bound<'_, PyAny>,
    matrix: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    let fraction = fraction_class(py)?;
    let orders = collect_iterable(orders, |value| natural(value, "stabilizer order"))?;
    let matrix = collect_iterable(matrix, |row| {
        collect_iterable(row, |value| rational(value, &fraction, "matrix entry"))
    })?;
    Ok(py.detach(|| kernel::check_detailed_balance(&orders, &matrix)))
}

#[pyfunction]
fn orbit_completeness(
    py: Python<'_>,
    group_order: &Bound<'_, PyAny>,
    stab_orders: &Bound<'_, PyAny>,
    expected_total: &Bound<'_, PyAny>,
) -> PyResult<(Py<PyAny>, Py<PyAny>, &'static str)> {
    let fraction = fraction_class(py)?;
    let group_order = natural(group_order, "group order")?;
    let expected_total = rational(expected_total, &fraction, "expected total")?;
    let mut accumulator = OrbitAccumulator::new(group_order, expected_total)
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    for value in stab_orders.try_iter()? {
        let order = natural(&value?, "stabilizer order")?;
        accumulator
            .push(order)
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
    }
    let audit = py.detach(move || accumulator.finish());
    let status = match audit.outcome() {
        OrbitOutcome::Complete => "complete",
        OrbitOutcome::Missing(_) => "missing",
        OrbitOutcome::Excess(_) => "excess",
    };
    Ok((
        to_fraction(&fraction, audit.covered())?,
        to_fraction(&fraction, audit.deficit())?,
        status,
    ))
}

#[pymodule]
fn _core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(class_mass, module)?)?;
    module.add_function(wrap_pyfunction!(hecke, module)?)?;
    module.add_function(wrap_pyfunction!(check_detailed_balance, module)?)?;
    module.add_function(wrap_pyfunction!(orbit_completeness, module)?)?;
    Ok(())
}
