//! Exercise the full Hecke normalization u⁻¹ · q^(-k · floor(rank / 2)) · Σ v_i
//! at odd higher rank (r = 5, k = 2, q = 3, nontrivial character u = -2/3).
//!
//! All five earlier examples call `hecke` with `k = 0`, which sets the power
//! factor to 1. This example uses `rank = 5` and `k = 2`, where
//! `k * floor(rank / 2) = 4` differs from the buggy order of operations
//! `floor((k * rank) / 2) = 5` by a factor of `q = 3`.

use hecke_mass_kernel::{hecke, BigRational, BigUint};
use hecke_mass_rust_example::rational;

fn main() {
    let q = BigUint::from(3u32);
    let k = BigUint::from(2u32);
    let rank = BigUint::from(5u32);
    let u = rational(-2, 3);

    // Six rational samples along a local double-coset decomposition, split into
    // two coset blocks to check additivity of the normalized Hecke readout.
    let block_a = [rational(1, 2), rational(-1, 6), rational(2, 3)];
    let block_b = [rational(5, 4), rational(-1, 12), rational(5, 6)];
    let all_samples: Vec<BigRational> = block_a.iter().chain(&block_b).cloned().collect();

    // Exact sum: (1/2 - 1/6 + 2/3) + (5/4 - 1/12 + 5/6) = 1 + 2 = 3.
    // Scaling: u⁻¹ = -3/2, q^(k * floor(5/2)) = 3^(2 * 2) = 81.
    // Expected readout: (-3/2) * (1/81) * 3 = -1/18.
    let readout = hecke(&u, &q, &k, &rank, &all_samples);
    let split_sum =
        hecke(&u, &q, &k, &rank, &block_a) + hecke(&u, &q, &k, &rank, &block_b);
    assert_eq!(readout, rational(-1, 18));
    assert_eq!(readout, split_sum);

    // Scaling every sample by u * q^(k * floor(rank / 2)) recovers the raw sum 3.
    let raw_sum = hecke(
        &rational(1, 1),
        &BigUint::from(1u32),
        &BigUint::from(0u32),
        &rank,
        &all_samples,
    );
    let scale = &u * BigRational::from_integer(3i64.pow(4).into());
    assert_eq!(&readout * &scale, raw_sum);
    println!("rank=5, k=2, q=3, u={u}: exact readout = {readout} (split sum = {split_sum})");

    // Bug 1: multiplying k * rank before dividing by 2 gives exponent 5 instead of 4.
    let buggy_exp = BigRational::from_integer(3i64.pow(5).into());
    let wrong_floor_readout = (&raw_sum / &u) / buggy_exp;
    assert_ne!(wrong_floor_readout, readout);
    assert_eq!(wrong_floor_readout, rational(-1, 54));
    println!(
        "Buggy floor((k * rank) / 2) = 5 gives {wrong_floor_readout} (off by factor q = 3)"
    );

    // Bug 2: dropping the central character factor u = -2/3 leaves only q^(-4).
    let missing_char_readout = hecke(&rational(1, 1), &q, &k, &rank, &all_samples);
    assert_ne!(missing_char_readout, readout);
    assert_eq!(missing_char_readout, rational(1, 27));
    println!("Dropping character u = {u} gives {missing_char_readout} instead of {readout}");
}
