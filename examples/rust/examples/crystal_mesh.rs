//! Audit an unshifted 2×2×2 reciprocal mesh for a simple cubic crystal.
//! A mask bit denotes a half-coordinate along one of the three axes.
use hecke_mass_kernel::{class_mass, BigRational, BigUint};
use hecke_mass_rust_example::{mean, rational};
use std::collections::BTreeMap;
use std::io::{self, BufRead};

fn generated_mesh() -> [usize; 8] {
    std::array::from_fn(|point: usize| (1 << point.count_ones()) - 1)
}

// The exporter can choose any point in an orbit as its representative.
fn read_mesh(input: impl BufRead) -> Result<[usize; 8], String> {
    let mut mesh = [usize::MAX; 8];
    for line in input.lines() {
        let line = line.map_err(|err| err.to_string())?;
        let mut fields = line.split_whitespace();
        let mut mask = || {
            fields
                .next()
                .and_then(|s| s.parse::<usize>().ok())
                .filter(|&n| n < 8)
                .ok_or("expected two point masks between 0 and 7")
        };
        let point = mask()?;
        let representative = mask()?;
        if fields.next().is_some() || mesh[point] != usize::MAX {
            return Err(format!("extra field or repeated point in {line:?}"));
        }
        mesh[point] = representative;
    }
    if mesh.contains(&usize::MAX) {
        return Err("expected one row for each of the eight mesh points".into());
    }
    Ok(mesh)
}

fn observable(point: usize) -> BigRational {
    let half_coordinates = i64::from(point.count_ones());
    rational(half_coordinates.pow(2), 1)
}

fn main() -> Result<(), String> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    let mesh = match args.as_slice() {
        [] => generated_mesh(),
        [flag] if flag == "--stdin" => read_mesh(io::stdin().lock())?,
        _ => return Err("usage: crystal_mesh [--stdin]".into()),
    };

    let mut counts = BTreeMap::new();
    for (point, &representative) in mesh.iter().enumerate() {
        if point.count_ones() != representative.count_ones()
            || mesh[representative] != representative
        {
            return Err(format!(
                "invalid orbit representative {representative} for {point}"
            ));
        }
        *counts.entry(representative).or_insert(0u32) += 1;
    }

    // All 8 sign choices fix 0 and 1/2 modulo 1. An axis permutation
    // fixes a point when it permutes only equal coordinates.
    let group_order = 48u32;
    let factorial = [1u32, 1, 2, 6];
    let mut orders = Vec::<BigUint>::new();
    let mut values = Vec::new();
    let mut weighted_sum = rational(0, 1);
    for (representative, multiplicity) in counts {
        let halves = representative.count_ones() as usize;
        let stabilizer = 8 * factorial[halves] * factorial[3 - halves];
        if multiplicity * stabilizer != group_order {
            return Err(format!(
                "incorrect multiplicity {multiplicity} for {representative}"
            ));
        }
        let value = observable(representative);
        weighted_sum += rational(i64::from(multiplicity), 8) * &value;
        values.push(value);
        orders.push(stabilizer.into());
        println!(
            "point {representative:03b}: multiplicity {multiplicity}, stabilizer {stabilizer}"
        );
    }
    let mass = class_mass(&orders);
    let full_mean = mean(&(0..8).map(observable).collect::<Vec<_>>());
    let equal_weight_mean = mean(&values);
    assert_eq!(&mass * rational(group_order.into(), 1), rational(8, 1));
    assert_eq!(weighted_sum, full_mean);
    assert_eq!(full_mean, rational(3, 1));
    assert_eq!(equal_weight_mean, rational(7, 2));
    println!("mass {mass}; weighted and full-grid means {full_mean}; equal-weight mean {equal_weight_mean}");
    Ok(())
}
