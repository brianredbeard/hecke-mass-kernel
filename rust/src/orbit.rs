use std::fmt;

use num_traits::{Signed, Zero};

use crate::{class_mass, reciprocal_order, BigInt, BigRational, BigUint};

/// Mathematical outcome of comparing orbit coverage with an expected total.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OrbitOutcome {
    /// The covered and expected totals are equal.
    Complete,
    /// Positive amount by which the expected total exceeds the covered total.
    Missing(BigRational),
    /// Positive amount by which the covered total exceeds the expected total.
    Excess(BigRational),
}

/// Exact coverage and signed deficit for a supplied table of stabilizer orders.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OrbitAudit {
    covered: BigRational,
    deficit: BigRational,
}

impl OrbitAudit {
    fn from_mass(group_order: &BigUint, expected_total: &BigRational, mass: BigRational) -> Self {
        let covered = mass * BigInt::from(group_order.clone());
        let deficit = expected_total - &covered;
        Self { covered, deficit }
    }

    /// Returns the group order times the sum of reciprocal stabilizer orders.
    pub fn covered(&self) -> &BigRational {
        &self.covered
    }

    /// Returns the expected total minus the covered total.
    pub fn deficit(&self) -> &BigRational {
        &self.deficit
    }

    /// Classifies the signed deficit and gives its positive magnitude when nonzero.
    pub fn outcome(&self) -> OrbitOutcome {
        if self.deficit.is_positive() {
            OrbitOutcome::Missing(self.deficit.clone())
        } else if self.deficit.is_negative() {
            OrbitOutcome::Excess(-&self.deficit)
        } else {
            OrbitOutcome::Complete
        }
    }
}

/// Invalid arithmetic input to the orbit audit.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OrbitAuditError {
    /// The group order must be positive.
    ZeroGroupOrder,
    /// Each stabilizer order must be positive.
    ZeroStabilizerOrder,
    /// The expected total must be nonnegative.
    NegativeExpectedTotal,
    /// A raw rational expected total must have a positive denominator.
    NonPositiveExpectedDenominator,
}

impl fmt::Display for OrbitAuditError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Self::ZeroGroupOrder => "group order must be positive",
            Self::ZeroStabilizerOrder => "stabilizer order must be positive",
            Self::NegativeExpectedTotal => "expected total must be nonnegative",
            Self::NonPositiveExpectedDenominator => {
                "expected total must have a positive denominator"
            }
        })
    }
}

impl std::error::Error for OrbitAuditError {}

fn validate_totals(
    group_order: &BigUint,
    expected_total: &BigRational,
) -> Result<(), OrbitAuditError> {
    if group_order.is_zero() {
        return Err(OrbitAuditError::ZeroGroupOrder);
    }
    if !expected_total.denom().is_positive() {
        return Err(OrbitAuditError::NonPositiveExpectedDenominator);
    }
    if expected_total.is_negative() {
        return Err(OrbitAuditError::NegativeExpectedTotal);
    }
    Ok(())
}

/// Compares the exact coverage of a finite table with the expected total.
///
/// Positive orders that do not divide the group order are included in the exact
/// sum, which may yield fractional coverage. A complete outcome establishes
/// equality of totals. Distinct orbit representatives and correct stabilizer
/// orders are assumptions supplied by the caller.
///
/// # Errors
///
/// Returns an error for a zero group or stabilizer order, a negative expected
/// total, or a raw expected total with a nonpositive denominator.
///
/// # Examples
///
/// ```
/// use hecke_mass_kernel::{orbit_completeness, BigUint, OrbitOutcome};
/// let orders = [BigUint::from(4u32), BigUint::from(6u32)];
/// let audit = orbit_completeness(&12u32.into(), &orders, &"5".parse().unwrap()).unwrap();
/// assert_eq!(audit.outcome(), OrbitOutcome::Complete);
/// ```
pub fn orbit_completeness(
    group_order: &BigUint,
    stabilizer_orders: &[BigUint],
    expected_total: &BigRational,
) -> Result<OrbitAudit, OrbitAuditError> {
    validate_totals(group_order, expected_total)?;
    if stabilizer_orders.iter().any(Zero::is_zero) {
        return Err(OrbitAuditError::ZeroStabilizerOrder);
    }
    Ok(OrbitAudit::from_mass(
        group_order,
        expected_total,
        class_mass(stabilizer_orders),
    ))
}

/// Streaming form of [`orbit_completeness`] that retains at most one partial
/// sum per power-of-two block size.
///
/// ```
/// use hecke_mass_kernel::{OrbitAccumulator, OrbitOutcome};
/// let mut audit = OrbitAccumulator::new(12u32.into(), "3".parse().unwrap()).unwrap();
/// audit.push(4u32.into()).unwrap();
/// assert_eq!(audit.finish().outcome(), OrbitOutcome::Complete);
/// ```
pub struct OrbitAccumulator {
    group_order: BigUint,
    expected_total: BigRational,
    blocks: Vec<Option<BigRational>>,
}

impl OrbitAccumulator {
    /// Starts an audit with a positive group order and nonnegative expected total.
    ///
    /// # Errors
    ///
    /// Returns an error for a zero group order, a negative expected total,
    /// or a raw expected total with a nonpositive denominator.
    pub fn new(group_order: BigUint, expected_total: BigRational) -> Result<Self, OrbitAuditError> {
        validate_totals(&group_order, &expected_total)?;
        Ok(Self {
            group_order,
            expected_total,
            blocks: Vec::new(),
        })
    }

    /// Adds one stabilizer order by merging blocks of equal size.
    ///
    /// # Errors
    ///
    /// Returns an error for a zero order, leaving the current sum intact.
    pub fn push(&mut self, order: BigUint) -> Result<(), OrbitAuditError> {
        if order.is_zero() {
            return Err(OrbitAuditError::ZeroStabilizerOrder);
        }
        let mut sum = reciprocal_order(order);
        for block in &mut self.blocks {
            match block.take() {
                Some(previous) => sum = previous + sum,
                None => {
                    *block = Some(sum);
                    return Ok(());
                }
            }
        }
        self.blocks.push(Some(sum));
        Ok(())
    }

    /// Consumes the stream and compares its exact coverage with the expected total.
    pub fn finish(self) -> OrbitAudit {
        let mass = self.blocks.into_iter().flatten().sum();
        OrbitAudit::from_mass(&self.group_order, &self.expected_total, mass)
    }
}
