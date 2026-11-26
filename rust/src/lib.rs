#![forbid(unsafe_code)]

//! Exact class mass, normalized Hecke arithmetic, and orbit audits on finite tables.
//!
//! The operations mirror the standalone Lean reference in
//! `lean/HeckeMassKernel/Finite.lean`:
//! - [`class_mass`] sums reciprocal stabilizer orders, with `0` contributing `0`.
//! - [`hecke`] sums rational samples and scales by `u⁻¹ * (q^(k * floor(rank / 2)))⁻¹`,
//!   using total inversion (`inv(0) = 0`) and `0^0 = 1`.
//! - [`orbit_completeness`] compares exact orbit coverage with a supplied total.

mod orbit;

pub use num_bigint::{BigInt, BigUint};
pub use num_rational::BigRational;
use num_traits::{One, Pow, Zero};
pub use orbit::{orbit_completeness, OrbitAccumulator, OrbitAudit, OrbitAuditError, OrbitOutcome};

fn reciprocal_order(order: BigUint) -> BigRational {
    if order.is_zero() {
        BigRational::zero()
    } else {
        // `1` and any positive integer are already coprime.
        BigRational::new_raw(BigInt::one(), BigInt::from(order))
    }
}

/// Balanced binary-splitting sum of reciprocal positive orders in `orders`.
fn sum_reciprocals(orders: &[BigUint]) -> BigRational {
    match orders {
        [] => BigRational::zero(),
        [order] => reciprocal_order(order.clone()),
        slice => {
            let mid = slice.len() / 2;
            sum_reciprocals(&slice[..mid]) + sum_reciprocals(&slice[mid..])
        }
    }
}

/// Balanced binary-splitting sum of `u64` reciprocal orders without heap
/// cloning intermediate `BigUint` inputs.
fn sum_reciprocals_u64(orders: &[u64]) -> BigRational {
    match orders {
        [] => BigRational::zero(),
        [0] => BigRational::zero(),
        [order] => BigRational::new_raw(BigInt::one(), BigInt::from(*order)),
        slice => {
            let mid = slice.len() / 2;
            sum_reciprocals_u64(&slice[..mid]) + sum_reciprocals_u64(&slice[mid..])
        }
    }
}

/// Balanced binary-splitting sum of rational samples.
fn sum_rationals(samples: &[BigRational]) -> BigRational {
    match samples {
        [] => BigRational::zero(),
        [sample] => sample.clone(),
        slice => {
            let mid = slice.len() / 2;
            sum_rationals(&slice[..mid]) + sum_rationals(&slice[mid..])
        }
    }
}

/// Sums the reciprocals of the stabilizer orders. A zero order contributes zero.
///
/// # Examples
///
/// ```
/// use hecke_mass_kernel::{class_mass, BigUint};
///
/// let mass = class_mass(&[BigUint::from(4u32), BigUint::from(6u32)]);
/// assert_eq!(mass.to_string(), "5/12");
/// ```
pub fn class_mass(orders: &[BigUint]) -> BigRational {
    sum_reciprocals(orders)
}

/// Convenience wrapper for [`class_mass`] on `u64` stabilizer orders.
///
/// # Examples
///
/// ```
/// use hecke_mass_kernel::class_mass_u64;
///
/// assert_eq!(class_mass_u64(&[4, 6]).to_string(), "5/12");
/// assert_eq!(class_mass_u64(&[0, 2, 0]).to_string(), "1/2");
/// ```
pub fn class_mass_u64(orders: &[u64]) -> BigRational {
    sum_reciprocals_u64(orders)
}

/// Sums the samples and scales by the inverses of `u` and `q^(k * floor(rank/2))`.
///
/// Inversion maps zero to zero, and `0^0` is one, matching the Lean reference.
/// Short-circuits before exponentiation when `u == 0`, `samples` is empty,
/// `q == 0` with positive exponent, or the sample sum vanishes.
///
/// # Examples
///
/// ```
/// use hecke_mass_kernel::{hecke, BigInt, BigRational, BigUint};
///
/// let u = BigRational::from_integer(BigInt::from(-1));
/// let samples = [
///     BigRational::from_integer(BigInt::from(2)),
///     BigRational::from_integer(BigInt::from(4)),
/// ];
/// let coeff = hecke(
///     &u,
///     &BigUint::from(3u32),
///     &BigUint::from(1u32),
///     &BigUint::from(3u32),
///     &samples,
/// );
/// assert_eq!(coeff.to_string(), "-2");
/// ```
pub fn hecke(
    u: &BigRational,
    q: &BigUint,
    k: &BigUint,
    rank: &BigUint,
    samples: &[BigRational],
) -> BigRational {
    if u.is_zero() || samples.is_empty() {
        return BigRational::zero();
    }
    let exponent = k * (rank >> 1usize);
    if q.is_zero() && !exponent.is_zero() {
        return BigRational::zero();
    }
    let sum = sum_rationals(samples);
    if sum.is_zero() {
        return sum;
    }
    let scaled = sum / u;
    if exponent.is_zero() || q.is_one() {
        return scaled;
    }
    let power = BigInt::from(Pow::pow(q, &exponent));
    scaled / power
}

/// Checks whether a square operator matrix satisfies detailed balance with
/// respect to positive stabilizer orders: `B[i][j] / orders[i] == B[j][i] / orders[j]`.
///
/// # Examples
///
/// ```
/// use hecke_mass_kernel::{check_detailed_balance, BigInt, BigRational, BigUint};
///
/// let r = |n: i64| BigRational::from_integer(BigInt::from(n));
/// let orders = [BigUint::from(4u32), BigUint::from(6u32)];
/// let b2 = vec![vec![r(1), r(2)], vec![r(3), r(0)]];
/// assert!(check_detailed_balance(&orders, &b2));
/// ```
pub fn check_detailed_balance(orders: &[BigUint], matrix: &[Vec<BigRational>]) -> bool {
    let n = orders.len();
    if matrix.len() != n || matrix.iter().any(|row| row.len() != n) {
        return false;
    }
    if orders.iter().any(Zero::is_zero) {
        return false;
    }
    for i in 0..n {
        let di = BigRational::from_integer(BigInt::from(orders[i].clone()));
        for j in (i + 1)..n {
            let dj = BigRational::from_integer(BigInt::from(orders[j].clone()));
            if &matrix[i][j] * &dj != &matrix[j][i] * &di {
                return false;
            }
        }
    }
    true
}

/// Internal integration probe used by repository build/RVV fixture checks.
#[doc(hidden)]
pub fn scaffold_probe(input: &[u32]) -> Vec<u32> {
    input.iter().map(|word| word ^ 0xa5a5_a5a5).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rat(n: i64, d: i64) -> BigRational {
        BigRational::new(BigInt::from(n), BigInt::from(d))
    }

    fn naive_hecke(
        u: &BigRational,
        q: u64,
        k: u64,
        rank: u64,
        samples: &[BigRational],
    ) -> BigRational {
        let mut sum = BigRational::zero();
        for s in samples {
            sum += s;
        }
        let u_inv = if u.is_zero() {
            BigRational::zero()
        } else {
            u.recip()
        };
        let exp = (k as u128) * ((rank / 2) as u128);
        let q_pow = if q == 0 {
            if exp == 0 {
                BigUint::one()
            } else {
                BigUint::zero()
            }
        } else if q == 1 {
            BigUint::one()
        } else {
            BigUint::from(q).pow(u32::try_from(exp).unwrap())
        };
        let pow_inv = if q_pow.is_zero() {
            BigRational::zero()
        } else {
            BigRational::new(BigInt::one(), BigInt::from(q_pow))
        };
        u_inv * pow_inv * sum
    }

    struct Lcg(u64);
    impl Lcg {
        fn next_u64(&mut self) -> u64 {
            self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            self.0
        }
        fn range(&mut self, bound: u64) -> u64 {
            self.next_u64() % bound
        }
    }

    #[test]
    fn short_circuits_on_huge_exponents() {
        let huge = (BigUint::one() << 64usize) + BigUint::one();
        assert_eq!(
            hecke(
                &BigRational::zero(),
                &BigUint::from(2u32),
                &huge,
                &BigUint::from(2u32),
                &[rat(1, 1)],
            ),
            BigRational::zero()
        );
        assert_eq!(
            hecke(
                &rat(1, 1),
                &BigUint::from(2u32),
                &huge,
                &BigUint::from(2u32),
                &[rat(1, 3), rat(-1, 3)],
            ),
            BigRational::zero()
        );
    }

    #[test]
    fn distinguishes_floor_order_of_operations() {
        // k = 2, rank = 5: k * floor(5/2) = 4, whereas floor(k * rank / 2) = 5.
        let res = hecke(
            &rat(1, 1),
            &BigUint::from(3u32),
            &BigUint::from(2u32),
            &BigUint::from(5u32),
            &[rat(1, 1)],
        );
        assert_eq!(res, rat(1, 81));
    }

    #[test]
    fn class_mass_algebraic_properties() {
        let orders_u64 = [4u64, 2, 6, 0, 12, 8];
        let orders: Vec<BigUint> = orders_u64.iter().map(|&x| BigUint::from(x)).collect();
        assert_eq!(class_mass(&orders), class_mass_u64(&orders_u64));

        // Doubling stabilizer orders halves the mass.
        let doubled: Vec<BigUint> = orders.iter().map(|d| d * 2u32).collect();
        assert_eq!(class_mass(&doubled) * rat(2, 1), class_mass(&orders));

        // Strict increase when adding any positive stabilizer order.
        let mut extended = orders.clone();
        extended.push(BigUint::from(1000u32));
        assert!(class_mass(&orders) < class_mass(&extended));
    }

    #[test]
    fn randomized_properties_and_reference_agreement() {
        let mut rng = Lcg(0x5eed_cafe_1234_5678);
        for _ in 0..500 {
            let n = rng.range(12) as usize;
            let mut orders_u64 = Vec::with_capacity(n);
            for _ in 0..n {
                orders_u64.push(rng.range(40));
            }
            let orders: Vec<BigUint> = orders_u64.iter().map(|&x| BigUint::from(x)).collect();
            let mut reversed = orders.clone();
            reversed.reverse();
            assert_eq!(class_mass(&orders), class_mass(&reversed));
            assert_eq!(class_mass(&orders), class_mass_u64(&orders_u64));

            let u_num = (rng.range(9) as i64) - 4;
            let u_den = (rng.range(6) + 1) as i64;
            let u = rat(u_num, u_den);
            let q = rng.range(8);
            let k = rng.range(5);
            let rank = rng.range(9);

            let mut samples = Vec::with_capacity(n);
            for _ in 0..n {
                let s_num = (rng.range(11) as i64) - 5;
                let s_den = (rng.range(7) + 1) as i64;
                samples.push(rat(s_num, s_den));
            }
            let got = hecke(
                &u,
                &BigUint::from(q),
                &BigUint::from(k),
                &BigUint::from(rank),
                &samples,
            );
            let expected = naive_hecke(&u, q, k, rank, &samples);
            assert_eq!(got, expected);

            // Permutation invariance.
            let mut rev_samples = samples.clone();
            rev_samples.reverse();
            assert_eq!(
                hecke(
                    &u,
                    &BigUint::from(q),
                    &BigUint::from(k),
                    &BigUint::from(rank),
                    &rev_samples,
                ),
                got
            );

            // Linearity under splitting.
            let split = n / 2;
            let left = hecke(
                &u,
                &BigUint::from(q),
                &BigUint::from(k),
                &BigUint::from(rank),
                &samples[..split],
            );
            let right = hecke(
                &u,
                &BigUint::from(q),
                &BigUint::from(k),
                &BigUint::from(rank),
                &samples[split..],
            );
            assert_eq!(left + right, got);
        }
    }
}
