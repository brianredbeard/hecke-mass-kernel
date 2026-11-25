use hecke_mass_kernel::BigRational;
use hecke_mass_rust_example::{mean, rational};

// A frame records where conjugation sends X, Y, Z, including their signs.
const IDENTITY: [i8; 3] = [1, 2, 3];
const HADAMARD: [i8; 3] = [3, -2, 1];
const PHASE: [i8; 3] = [2, -1, 3];

fn clifford_frames() -> Vec<[i8; 3]> {
    let mut frames = vec![IDENTITY];
    let mut cursor = 0;
    while cursor < frames.len() {
        let frame = frames[cursor];
        for gate in [HADAMARD, PHASE] {
            let next = frame.map(|axis| {
                let index = usize::from(axis.unsigned_abs()) - 1;
                axis.signum() * gate[index]
            });
            if !frames.contains(&next) {
                frames.push(next);
            }
        }
        cursor += 1;
    }
    frames
}

fn twirled_probabilities(frames: &[[i8; 3]]) -> [BigRational; 4] {
    // An I error stays I. A Z error follows the third entry of each frame.
    // Opposite signs give the same error channel.
    [0, 1, 2, 3].map(|target| {
        let samples = frames
            .iter()
            .map(|frame| {
                if target == 0 {
                    rational(7, 8)
                } else if frame[2].abs() == target {
                    rational(1, 8)
                } else {
                    rational(0, 1)
                }
            })
            .collect::<Vec<_>>();
        mean(&samples)
    })
}

fn main() {
    let mut frames = clifford_frames();
    assert_eq!(frames.len(), 24);

    let uniform = twirled_probabilities(&frames);
    let expected = [
        rational(7, 8),
        rational(1, 24),
        rational(1, 24),
        rational(1, 24),
    ];
    assert_eq!(uniform, expected);
    println!(
        "Uniform frames (I, X, Y, Z): {}",
        uniform.map(|p| p.to_string()).join(", ")
    );

    // Duplicate the identity in place of H. The frame count stays 24, but
    // one error that would have landed on X now lands on Z.
    let hadamard_index = frames.iter().position(|&frame| frame == HADAMARD).unwrap();
    frames[hadamard_index] = IDENTITY;
    let biased = twirled_probabilities(&frames);
    assert_ne!(biased, expected);
    assert_eq!(
        biased,
        [
            rational(7, 8),
            rational(7, 192),
            rational(1, 24),
            rational(3, 64)
        ]
    );
    println!(
        "Biased frames (I, X, Y, Z):  {}",
        biased.map(|p| p.to_string()).join(", ")
    );
}
