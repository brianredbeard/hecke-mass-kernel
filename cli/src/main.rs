#![forbid(unsafe_code)]

use std::ffi::{OsStr, OsString};
use std::fs::File;
use std::io::{self, BufRead, BufReader, Write};
use std::path::PathBuf;
use std::process::ExitCode;

use hecke_mass_kernel::{BigInt, BigRational, BigUint, OrbitAccumulator, OrbitAudit, OrbitOutcome};

const USAGE: &str = "Usage: hecke-mass-audit orbits --group-order G --expected N [ORDERS_FILE|-]\n\
    Read one positive decimal stabilizer order per nonblank line.\n\
    Omit ORDERS_FILE or use - to read standard input.\n\
    Exit status: 0 complete, 1 missing or excess, 2 invalid input or I/O error.";

fn decimal(value: &str) -> Option<BigUint> {
    if value.is_empty() || !value.bytes().all(|byte| byte.is_ascii_digit()) {
        return None;
    }
    value.parse().ok()
}

fn read_orders(mut reader: impl BufRead, accumulator: &mut OrbitAccumulator) -> Result<(), String> {
    let mut line = String::new();
    let mut line_number = 1;
    loop {
        line.clear();
        let bytes = reader
            .read_line(&mut line)
            .map_err(|error| format!("reading line {line_number}: {error}"))?;
        if bytes == 0 {
            return Ok(());
        }
        let order = line.trim();
        if !order.is_empty() {
            let order = decimal(order).ok_or_else(|| {
                format!("line {line_number}: stabilizer order must be a positive decimal integer")
            })?;
            accumulator
                .push(order)
                .map_err(|error| format!("line {line_number}: {error}"))?;
        }
        line_number += 1;
    }
}

fn orbits(mut args: impl Iterator<Item = OsString>) -> Result<OrbitAudit, String> {
    let mut group_order = None;
    let mut expected_total = None;
    let mut path = None;

    while let Some(arg) = args.next() {
        match arg.to_str() {
            Some(flag @ ("--group-order" | "--expected")) => {
                let slot = if flag == "--group-order" {
                    &mut group_order
                } else {
                    &mut expected_total
                };
                if slot.is_some() {
                    return Err(format!("repeated argument {flag}"));
                }
                let value = args.next().ok_or_else(|| format!("{flag} needs a value"))?;
                *slot = Some(
                    value
                        .to_str()
                        .and_then(decimal)
                        .ok_or_else(|| format!("{flag} must be a nonnegative decimal integer"))?,
                );
            }
            Some(flag) if flag.starts_with('-') && flag != "-" => {
                return Err(format!("unknown argument {flag}"));
            }
            _ if path.is_none() => path = Some(PathBuf::from(arg)),
            _ => return Err("expected exactly one orders file or standard input".into()),
        }
    }

    let group_order = group_order.ok_or("missing --group-order")?;
    let expected_total = expected_total.ok_or("missing --expected")?;
    let expected_total = BigRational::from_integer(BigInt::from(expected_total));
    let mut accumulator =
        OrbitAccumulator::new(group_order, expected_total).map_err(|error| error.to_string())?;

    match path {
        Some(path) if path.as_os_str() != "-" => {
            let file = File::open(&path)
                .map_err(|error| format!("opening {}: {error}", path.display()))?;
            read_orders(BufReader::new(file), &mut accumulator)
                .map_err(|error| format!("{}: {error}", path.display()))?;
        }
        _ => read_orders(io::stdin().lock(), &mut accumulator)?,
    }
    Ok(accumulator.finish())
}

fn run() -> Result<u8, String> {
    let mut args = std::env::args_os().skip(1).peekable();
    match args.next().as_deref().and_then(OsStr::to_str) {
        Some("-h" | "--help") if args.peek().is_none() => {
            println!("{USAGE}");
            Ok(0)
        }
        Some("--version") if args.peek().is_none() => {
            println!("hecke-mass-audit {}", env!("CARGO_PKG_VERSION"));
            Ok(0)
        }
        Some("orbits") => {
            if args
                .peek()
                .is_some_and(|arg| arg == "-h" || arg == "--help")
            {
                println!("{USAGE}");
                return Ok(0);
            }
            let audit = orbits(args)?;
            let (label, status) = match audit.outcome() {
                OrbitOutcome::Complete => ("complete", 0),
                OrbitOutcome::Missing(_) => ("missing", 1),
                OrbitOutcome::Excess(_) => ("excess", 1),
            };
            writeln!(
                io::stdout().lock(),
                "{label} covered={} deficit={}",
                audit.covered(),
                audit.deficit()
            )
            .map_err(|error| format!("writing audit result: {error}"))?;
            Ok(status)
        }
        _ => Err(USAGE.into()),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => ExitCode::from(code),
        Err(error) => {
            eprintln!("hecke-mass-audit: {error}");
            ExitCode::from(2)
        }
    }
}
