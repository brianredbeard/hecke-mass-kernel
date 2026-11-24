#![forbid(unsafe_code)]

//! Native Rust library scaffold for the Hecke mass kernel.

/// Smoke tests library integration by XORing each input word with `0xa5a5a5a5`.
pub fn scaffold_probe(input: &[u32]) -> Vec<u32> {
    input.iter().map(|word| word ^ 0xa5a5_a5a5).collect()
}
