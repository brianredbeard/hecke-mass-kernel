//! Check a commutative integer-add pattern generator against ordered operands.

use hecke_mass_kernel::{class_mass, BigRational, BigUint};
use hecke_mass_rust_example::rational;
use std::collections::BTreeSet;

type Pattern = (u8, u8);
const REGISTERS: [u8; 3] = [0, 1, 2];

fn audit(patterns: &[Pattern], all_operands: &BTreeSet<Pattern>) -> (BigRational, Vec<Pattern>) {
    let mut expanded = BTreeSet::new();
    let mut orders: Vec<BigUint> = Vec::new();
    for &(left, right) in patterns {
        // The swap fixes add(r, r). Every other pair has two orientations.
        let order = if left == right { 2u32 } else { 1u32 };
        orders.push(order.into());
        expanded.insert((left, right));
        expanded.insert((right, left));
    }
    let covered = rational(2, 1) * class_mass(&orders);
    assert!(expanded.is_subset(all_operands));
    assert_eq!(covered, BigRational::from_integer(expanded.len().into()));
    let missing = all_operands.difference(&expanded).copied().collect();
    (covered, missing)
}

fn main() {
    let all_operands: BTreeSet<_> = REGISTERS
        .into_iter()
        .flat_map(|left| REGISTERS.map(|right| (left, right)))
        .collect();
    let mut patterns: Vec<_> = all_operands
        .iter()
        .copied()
        .filter(|(left, right)| left <= right)
        .collect();
    let (covered, missing) = audit(&patterns, &all_operands);
    assert_eq!(patterns.len(), 6);
    assert_eq!(covered, rational(9, 1));
    assert!(missing.is_empty());
    println!(
        "{} canonical add patterns cover {covered} ordered register pairs.",
        patterns.len()
    );

    patterns.retain(|&pair| pair != (0, 1));
    let (covered, missing) = audit(&patterns, &all_operands);
    assert_eq!(covered, rational(7, 1));
    assert_eq!(missing, [(0, 1), (1, 0)]);
    println!(
        "Dropping add(r0, r1) leaves {covered}/9 pairs covered. Missing operands: {missing:?}."
    );
}
