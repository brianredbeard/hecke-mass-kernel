fn main() {
    let output = hecke_mass_kernel::scaffold_probe(&[0]);
    assert_eq!(output, [0xa5a5_a5a5]);
}
