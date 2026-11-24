use hecke_mass_kernel::{class_mass, hecke, BigRational, BigUint};

#[test]
fn matches_lean_kernel_reference() {
    let mut counts = [0, 0];
    for (line_number, line) in include_str!("../../tests/vectors/kernel.tsv")
        .lines()
        .enumerate()
    {
        let mut fields = line.split('\t');
        let operation = fields.next().unwrap();
        let mut inputs = fields.next().unwrap().split_whitespace();
        let expected = fields.next().unwrap();
        assert!(fields.next().is_none());

        let result = match operation {
            "mass" => {
                counts[0] += 1;
                let orders: Vec<BigUint> = inputs.map(|input| input.parse().unwrap()).collect();
                class_mass(&orders)
            }
            "hecke" => {
                counts[1] += 1;
                let u = inputs.next().unwrap().parse().unwrap();
                let q = inputs.next().unwrap().parse().unwrap();
                let k = inputs.next().unwrap().parse().unwrap();
                let rank = inputs.next().unwrap().parse().unwrap();
                let samples: Vec<BigRational> =
                    inputs.map(|input| input.parse().unwrap()).collect();
                hecke(&u, &q, &k, &rank, &samples)
            }
            _ => panic!("unknown operation {operation}"),
        };
        assert_eq!(
            result.to_string(),
            expected,
            "fixture line {}",
            line_number + 1
        );
    }
    assert!(counts.into_iter().all(|count| count > 0));
}
