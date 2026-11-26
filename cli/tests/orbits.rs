use std::io::Write;
use std::process::{Command, Output, Stdio};

fn audit(args: &[&str], orders: &str) -> Output {
    let mut child = Command::new(env!("CARGO_BIN_EXE_hecke-mass-audit"))
        .arg("orbits")
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(orders.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}

#[test]
fn reports_exact_complete_missing_and_excess_totals() {
    for (orders, status, report) in [
        ("2\n\n3\n", 0, "complete covered=5 deficit=0\n"),
        ("3\n", 1, "missing covered=2 deficit=3\n"),
        ("2\n3\n1\n", 1, "excess covered=11 deficit=-6\n"),
    ] {
        let result = audit(&["--group-order", "6", "--expected", "5", "-"], orders);
        assert_eq!(result.status.code(), Some(status));
        assert_eq!(result.stdout, report.as_bytes());
        assert!(result.stderr.is_empty());
    }
}

#[test]
fn accepts_large_decimal_values_and_reports_fractional_coverage() {
    let n = "18446744073709551616";
    let exact = audit(&["--group-order", n, "--expected", n], "1\n");
    assert_eq!(exact.status.code(), Some(0));
    assert_eq!(
        exact.stdout,
        format!("complete covered={n} deficit=0\n").as_bytes()
    );

    let fraction = audit(&["--group-order", "1", "--expected", "1"], "3\n");
    assert_eq!(fraction.status.code(), Some(1));
    assert_eq!(fraction.stdout, b"missing covered=1/3 deficit=2/3\n");
}

#[test]
fn treats_zero_and_non_decimal_orders_as_malformed_with_line_numbers() {
    for order in ["0", "-1", "2.0", "1 2"] {
        let result = audit(
            &["--group-order", "1", "--expected", "1"],
            &format!("1\n{order}\n"),
        );
        assert_eq!(result.status.code(), Some(2));
        assert!(result.stdout.is_empty());
        assert!(String::from_utf8(result.stderr).unwrap().contains("line 2"));
    }
}
