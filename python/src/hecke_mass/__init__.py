"""Exact arithmetic audits for finite tables."""

from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from . import _core
from ._core import check_detailed_balance, class_mass, hecke

__all__ = [
    "OrbitAudit",
    "check_detailed_balance",
    "class_mass",
    "hecke",
    "orbit_completeness",
]


@dataclass(frozen=True, slots=True)
class OrbitAudit:
    """Exact covered size, signed shortfall, and the corresponding status."""

    covered: Fraction
    deficit: Fraction
    status: Literal["complete", "missing", "excess"]


def orbit_completeness(
    group_order: int, stab_orders: Iterable[int], expected_total: int | Fraction
) -> OrbitAudit:
    """Compare exact orbit coverage with a nonnegative expected total.

    The group and stabilizer orders are positive integers. The orders can be
    supplied as a stream. The signed deficit is expected total minus coverage.
    """
    return OrbitAudit(
        *_core.orbit_completeness(group_order, stab_orders, expected_total)
    )
