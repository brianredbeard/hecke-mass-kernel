"""Check finite weight-two Brandt matrices with the exact kernel."""

from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from operator import index
from typing import SupportsIndex

from .. import check_detailed_balance, class_mass, hecke


@dataclass(frozen=True, slots=True)
class BrandtAudit:
    """Mass, row totals, and balance for a supplied Brandt table."""

    mass: Fraction
    row_sums: tuple[Fraction, ...]
    detailed_balance: bool
    expected_mass: Fraction | None
    expected_row_sum: int

    @property
    def ok(self) -> bool:
        """Whether the supplied table passed each requested check."""
        return (
            self.detailed_balance
            and (self.expected_mass is None or self.mass == self.expected_mass)
            and all(total == self.expected_row_sum for total in self.row_sums)
        )


def _integer(value: SupportsIndex, name: str) -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    try:
        return index(value)
    except TypeError as error:
        raise TypeError(f"{name} must be an integer") from error


def audit_brandt_matrix(
    stabilizer_orders: Iterable[SupportsIndex],
    matrix: Iterable[Iterable[SupportsIndex]],
    *,
    prime: SupportsIndex,
    expected_mass: Fraction | SupportsIndex | None = None,
) -> BrandtAudit:
    """Audit an unweighted Brandt table at a supplied good prime.

    Each row counts directed neighbors from one class to every target class.
    Use positive full stabilizer orders in the same basis as both matrix axes
    and a matching convention for the optional expected mass. The report
    checks the resulting mass, row totals of prime + 1, and detailed balance.
    The caller supplies a good prime and the geometric data.
    """
    prime = _integer(prime, "prime")
    if prime < 2:
        raise ValueError("prime must be at least 2")
    orders = tuple(_integer(d, "stabilizer order") for d in stabilizer_orders)
    if not orders or any(d <= 0 for d in orders):
        raise ValueError("expected at least one stabilizer order, each positive")

    rows = tuple(
        tuple(_integer(count, "matrix count") for count in row) for row in matrix
    )
    size = len(orders)
    if len(rows) != size or any(len(row) != size for row in rows):
        raise ValueError("matrix must be square with one row per stabilizer order")
    if any(count < 0 for row in rows for count in row):
        raise ValueError("matrix counts must be nonnegative")

    if expected_mass is not None:
        if not isinstance(expected_mass, Fraction):
            expected_mass = Fraction(_integer(expected_mass, "expected mass"))
        if expected_mass < 0:
            raise ValueError("expected mass must be nonnegative")

    return BrandtAudit(
        mass=class_mass(orders),
        row_sums=tuple(hecke(1, prime, 0, 2, row) for row in rows),
        detailed_balance=check_detailed_balance(orders, rows),
        expected_mass=expected_mass,
        expected_row_sum=prime + 1,
    )
