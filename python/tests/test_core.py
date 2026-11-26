"""Conformance of the installed Python wheel with the Lean fixture generators."""

from dataclasses import FrozenInstanceError
from fractions import Fraction
from pathlib import Path
import unittest

import hecke_mass


VECTORS = Path(__file__).resolve().parents[2] / "tests" / "vectors"


class CoreTests(unittest.TestCase):
    def test_mass_and_hecke_match_lean(self):
        for line in (VECTORS / "kernel.tsv").read_text().splitlines():
            operation, arguments, expected = line.split("\t")
            with self.subTest(line=line):
                if operation == "mass":
                    actual = hecke_mass.class_mass(map(int, arguments.split()))
                else:
                    self.assertEqual(operation, "hecke")
                    u, q, k, rank, *samples = arguments.split()
                    actual = hecke_mass.hecke(
                        Fraction(u), int(q), int(k), int(rank), map(Fraction, samples)
                    )
                self.assertIsInstance(actual, Fraction)
                self.assertEqual(actual, Fraction(expected))

    def test_orbit_audit_matches_lean(self):
        for line in (VECTORS / "orbit.tsv").read_text().splitlines():
            group_order, expected, orders, covered, deficit, status = line.split("\t")
            with self.subTest(line=line):
                orders = () if orders == "-" else map(int, orders.split(","))
                audit = hecke_mass.orbit_completeness(
                    int(group_order), orders, Fraction(expected)
                )
                self.assertEqual(
                    audit,
                    hecke_mass.OrbitAudit(Fraction(covered), Fraction(deficit), status),
                )
        with self.assertRaises(FrozenInstanceError):
            audit.status = "changed"

    def test_arbitrary_precision_conversions_do_not_need_decimal_strings(self):
        huge = 1 << 16000
        self.assertEqual(hecke_mass.class_mass([huge]), Fraction(1, huge))
        self.assertEqual(hecke_mass.hecke(1, 1, 0, 0, [huge]), Fraction(huge))
        self.assertEqual(
            hecke_mass.orbit_completeness(huge, [1], huge + 1).deficit,
            Fraction(1),
        )

    def test_detailed_balance_accepts_exact_iterable_rows(self):
        self.assertTrue(
            hecke_mass.check_detailed_balance(
                iter([4, 6]),
                (iter(row) for row in [[1, Fraction(1, 2)], [Fraction(3, 4), 0]]),
            )
        )
        self.assertFalse(hecke_mass.check_detailed_balance([4, 6], [[1, 2], [2, 0]]))
        self.assertFalse(hecke_mass.check_detailed_balance([1], [[1, 2]]))
        self.assertFalse(hecke_mass.check_detailed_balance([0], [[1]]))

    def test_invalid_inputs_have_value_or_type_errors(self):
        for invalid in (True, 1.0, "1", Fraction(1)):
            with self.subTest(order=invalid), self.assertRaises(TypeError):
                hecke_mass.class_mass([invalid])
        for invalid in (True, 1.0, "1/3"):
            with self.subTest(value=invalid), self.assertRaises(TypeError):
                hecke_mass.hecke(invalid, 1, 0, 0, [1])
            with self.subTest(sample=invalid), self.assertRaises(TypeError):
                hecke_mass.hecke(1, 1, 0, 0, [invalid])
        for args in ((0, [1], 0), (1, [0], 0), (1, [-1], 0), (1, [1], -1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                hecke_mass.orbit_completeness(*args)
        with self.assertRaises(ValueError):
            hecke_mass.hecke(1, -1, 0, 0, [1])
        with self.assertRaises(TypeError):
            hecke_mass.orbit_completeness(1, [1], 1.0)

    def test_iterable_exceptions_propagate(self):
        def broken_orders():
            yield 1
            raise LookupError("input stream stopped unexpectedly")

        with self.assertRaisesRegex(LookupError, "stopped unexpectedly"):
            hecke_mass.orbit_completeness(1, broken_orders(), 1)
