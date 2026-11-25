//! Exact arithmetic shared by the runnable examples.

use hecke_mass_kernel::{hecke, BigRational};

pub fn rational(numerator: i64, denominator: i64) -> BigRational {
    BigRational::new(numerator.into(), denominator.into())
}

/// With degree zero the Hecke formula divides the sample sum by `u`.
pub fn mean(samples: &[BigRational]) -> BigRational {
    assert!(!samples.is_empty(), "an average needs at least one sample");
    let count = BigRational::from_integer(samples.len().into());
    hecke(&count, &1u32.into(), &0u32.into(), &1u32.into(), samples)
}
