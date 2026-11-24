use hecke_mass_kernel::scaffold_probe;

#[test]
fn matches_lean_reference_fixtures() {
    let (inputs, expected): (Vec<u32>, Vec<u32>) = include_str!("../../tests/vectors/scaffold.csv")
        .lines()
        .map(|line| {
            let (input, output) = line.split_once(',').expect("input,output pair");
            (
                input.parse::<u32>().expect("u32 input"),
                output.parse::<u32>().expect("u32 output"),
            )
        })
        .unzip();
    assert!(!inputs.is_empty());

    for length in 0..=inputs.len() {
        assert_eq!(scaffold_probe(&inputs[..length]), expected[..length]);
    }
}
