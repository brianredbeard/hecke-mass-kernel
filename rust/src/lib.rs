#![forbid(unsafe_code)]

//! Exact class mass and normalized Hecke arithmetic on finite tables.

pub use num_bigint::{BigInt, BigUint};
pub use num_rational::BigRational;
use num_traits::{Pow, Zero};

/// Sums the reciprocals of the stabilizer orders. A zero order contributes zero.
pub fn class_mass(orders: &[BigUint]) -> BigRational {
    orders
        .iter()
        .filter(|order| !order.is_zero())
        .map(|order| BigRational::new(BigInt::from(1), BigInt::from(order.clone())))
        .sum()
}

/// Sums the samples and scales by the inverses of `u` and `q^(k * floor(rank/2))`.
///
/// Use normalized rationals with positive denominators. Inversion maps zero to
/// zero, and `0^0` is one, as in the Lean reference.
pub fn hecke(
    u: &BigRational,
    q: &BigUint,
    k: &BigUint,
    rank: &BigUint,
    samples: &[BigRational],
) -> BigRational {
    let exponent = k * (rank >> 1usize);
    if u.is_zero() || (q.is_zero() && !exponent.is_zero()) {
        return BigRational::zero();
    }
    let sum: BigRational = samples.iter().sum();
    if sum.is_zero() {
        return sum;
    }
    let power = BigInt::from(Pow::pow(q, &exponent));
    (sum / u) / power
}

/// Smoke tests library integration by XORing each input word with `0xa5a5a5a5`.
pub fn scaffold_probe(input: &[u32]) -> Vec<u32> {
    input.iter().map(|word| word ^ 0xa5a5_a5a5).collect()
}
