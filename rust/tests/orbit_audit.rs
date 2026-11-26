use hecke_mass_kernel::{
    orbit_completeness, BigRational, BigUint, OrbitAccumulator, OrbitAuditError, OrbitOutcome,
};

fn integer(value: u32) -> BigUint {
    value.into()
}

fn rational(value: &str) -> BigRational {
    value.parse().unwrap()
}

#[test]
fn slice_and_stream_match_lean_orbit_vectors() {
    for (index, line) in include_str!("../../tests/vectors/orbit.tsv")
        .lines()
        .enumerate()
    {
        let fields: Vec<_> = line.split('\t').collect();
        let [group, expected, orders, covered, deficit, status] = fields.as_slice() else {
            panic!("invalid fixture line {}", index + 1);
        };
        let group: BigUint = group.parse().unwrap();
        let expected = rational(expected);
        let orders: Vec<BigUint> = if *orders == "-" {
            Vec::new()
        } else {
            orders
                .split(',')
                .map(|order| order.parse().unwrap())
                .collect()
        };
        let mut stream = OrbitAccumulator::new(group.clone(), expected.clone()).unwrap();
        for order in &orders {
            stream.push(order.clone()).unwrap();
        }
        let audit = orbit_completeness(&group, &orders, &expected).unwrap();
        assert_eq!(stream.finish(), audit, "{line}");
        assert_eq!(*covered, audit.covered().to_string(), "{line}");
        assert_eq!(*deficit, audit.deficit().to_string(), "{line}");
        let outcome = match audit.outcome() {
            OrbitOutcome::Complete => "complete",
            OrbitOutcome::Missing(amount) => {
                assert_eq!(&amount, audit.deficit(), "{line}");
                "missing"
            }
            OrbitOutcome::Excess(amount) => {
                assert_eq!(amount, -audit.deficit(), "{line}");
                "excess"
            }
        };
        assert_eq!(*status, outcome, "{line}");
    }
}

#[test]
fn classifies_complete_missing_and_excess_with_exact_values() {
    let orders = [integer(2), integer(3)];
    for (expected, deficit, outcome) in [
        ("5/6", "0", OrbitOutcome::Complete),
        ("1", "1/6", OrbitOutcome::Missing(rational("1/6"))),
        ("0", "-5/6", OrbitOutcome::Excess(rational("5/6"))),
    ] {
        let audit = orbit_completeness(&integer(1), &orders, &rational(expected)).unwrap();
        assert_eq!(audit.covered(), &rational("5/6"));
        assert_eq!(audit.deficit(), &rational(deficit));
        assert_eq!(audit.outcome(), outcome);
    }
}

#[test]
fn rejects_invalid_inputs_and_keeps_the_stream_valid_after_an_invalid_order() {
    assert_eq!(
        orbit_completeness(&integer(0), &[], &rational("0")),
        Err(OrbitAuditError::ZeroGroupOrder)
    );
    assert_eq!(
        orbit_completeness(&integer(1), &[], &rational("-1/3")),
        Err(OrbitAuditError::NegativeExpectedTotal)
    );
    assert_eq!(
        orbit_completeness(&integer(1), &[integer(0)], &rational("0")),
        Err(OrbitAuditError::ZeroStabilizerOrder)
    );
    for denominator in [0, -1] {
        let malformed = BigRational::new_raw(1.into(), denominator.into());
        assert!(orbit_completeness(&integer(1), &[], &malformed).is_err());
        assert!(OrbitAccumulator::new(integer(1), malformed).is_err());
    }

    let mut stream = OrbitAccumulator::new(integer(12), rational("6")).unwrap();
    stream.push(integer(2)).unwrap();
    assert_eq!(
        stream.push(integer(0)),
        Err(OrbitAuditError::ZeroStabilizerOrder)
    );
    assert_eq!(stream.finish().outcome(), OrbitOutcome::Complete);
}

#[test]
fn streaming_matches_slice_for_arbitrary_precision_orders_and_uneven_batches() {
    let group = "24329020081766400000000000".parse().unwrap();
    let group: BigUint = group;
    let orders: Vec<_> = (1u32..=73).map(|factor| &group * factor).collect();
    let expected = rational("5");
    let mut stream = OrbitAccumulator::new(group.clone(), expected.clone()).unwrap();
    for order in &orders {
        stream.push(order.clone()).unwrap();
    }
    assert_eq!(
        stream.finish(),
        orbit_completeness(&group, &orders, &expected).unwrap()
    );
}
