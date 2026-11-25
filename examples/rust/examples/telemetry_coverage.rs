//! Audit one simulated fault scenario per orbit of three interchangeable lanes.

use hecke_mass_kernel::{class_mass, BigRational, BigUint};
use hecke_mass_rust_example::rational;
use std::collections::BTreeSet;

#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
enum Lane {
    Healthy,
    Stale,
    Silent,
}

use Lane::*;
type Scenario = [Lane; 3];
const STATES: [Lane; 3] = [Healthy, Stale, Silent];
const RELABELINGS: [[usize; 3]; 6] = [
    [0, 1, 2],
    [0, 2, 1],
    [1, 0, 2],
    [1, 2, 0],
    [2, 0, 1],
    [2, 1, 0],
];

fn stabilizer_order(scenario: Scenario) -> BigUint {
    RELABELINGS
        .iter()
        .filter(|permutation| permutation.map(|lane| scenario[lane]) == scenario)
        .count()
        .into()
}

fn covered_scenarios(representatives: &BTreeSet<Scenario>) -> BigRational {
    let orders: Vec<_> = representatives
        .iter()
        .copied()
        .map(stabilizer_order)
        .collect();
    let group_order = BigRational::from_integer(RELABELINGS.len().into());
    group_order * class_mass(&orders)
}

fn main() {
    let mut campaign = BTreeSet::new();
    let mut labelled_count = 0;
    for first in STATES {
        for second in STATES {
            for third in STATES {
                labelled_count += 1;
                let mut scenario = [first, second, third];
                scenario.sort();
                campaign.insert(scenario);
            }
        }
    }

    let covered = covered_scenarios(&campaign);
    assert_eq!(campaign.len(), 10);
    assert_eq!(covered, rational(labelled_count, 1));
    println!(
        "{} representative scenarios cover {covered} labelled cases.",
        campaign.len()
    );

    assert!(campaign.remove(&[Healthy, Stale, Silent]));
    let incomplete = covered_scenarios(&campaign);
    assert_eq!(incomplete, rational(21, 1));
    println!(
        "Omitting the all-distinct scenario leaves {incomplete}/{labelled_count} cases covered."
    );
}
