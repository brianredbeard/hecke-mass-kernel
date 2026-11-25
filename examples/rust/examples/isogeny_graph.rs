//! Check a supersingular 2-isogeny graph in characteristic 11.
//! The classical modular polynomial used below is given in Sage's reference:
//! https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/mod_poly.html

use hecke_mass_kernel::{class_mass, BigRational};
use hecke_mass_rust_example::{mean, rational};

fn neighbors(j: i64) -> Vec<i64> {
    // Phi_2(j,Y) modulo 11 is Y^3 + a*Y^2 + b*Y + c.
    let a = -j * j + 3 * j + 8;
    let b = 3 * j * j + 5 * j + 3;
    let c = j * j * j + 8 * j * j + 3 * j + 10;

    let mut roots = Vec::new();
    for y in 0..11 {
        if (((y + a) * y + b) * y + c) % 11 == 0 {
            roots.push(y);
            // A root is repeated precisely when the derivative also vanishes.
            if (3 * y * y + 2 * a * y + b) % 11 == 0 {
                roots.push(y);
                if (6 * y + 2 * a) % 11 == 0 {
                    roots.push(y);
                }
            }
        }
    }
    assert_eq!(roots.len(), 3, "all three isogenies must be accounted for");
    roots
}

fn transition_probability(destinations: &[i64], target: i64) -> BigRational {
    let hits: Vec<_> = destinations
        .iter()
        .map(|&j| rational(i64::from(j == target), 1))
        .collect();
    mean(&hits)
}

fn main() {
    // 1728 reduces to 1 mod 11. Its full automorphism group has order 4,
    // while the curve with j=0 has 6 automorphisms over the algebraic closure.
    let from_one = neighbors(1);
    let from_zero = neighbors(0);
    assert_eq!(from_one, [0, 0, 1]);
    assert_eq!(from_zero, [1, 1, 1]);
    let total_mass = class_mass(&[4u32.into(), 6u32.into()]);
    assert_eq!(total_mass, rational(5, 12));
    let weight_one = class_mass(&[4u32.into()]) / &total_mass;
    let weight_zero = class_mass(&[6u32.into()]) / &total_mass;

    let one_to_zero = transition_probability(&from_one, 0);
    let zero_to_one = transition_probability(&from_zero, 1);
    let forward_flow = &weight_one * &one_to_zero;
    let reverse_flow = &weight_zero * &zero_to_one;
    assert_eq!(one_to_zero, rational(2, 3));
    assert_eq!(zero_to_one, rational(1, 1));
    assert_eq!(forward_flow, reverse_flow);
    assert_eq!(forward_flow, rational(2, 5));
    println!("j=1 -> {from_one:?}, j=0 -> {from_zero:?}, class mass = {total_mass}");
    println!("P(1 -> 0) = {one_to_zero}, P(0 -> 1) = {zero_to_one}");
    println!("Stationary flow in each direction = {forward_flow}");

    // Model a graph exporter that keeps only distinct destinations.
    let mut unique_from_one = from_one;
    let mut unique_from_zero = from_zero;
    unique_from_one.dedup();
    unique_from_zero.dedup();
    let faulty_forward = weight_one * transition_probability(&unique_from_one, 0);
    let faulty_reverse = weight_zero * transition_probability(&unique_from_zero, 1);
    assert_ne!(faulty_forward, faulty_reverse);
    println!("Deduplicated export fails balance: {faulty_forward} versus {faulty_reverse}");
}
