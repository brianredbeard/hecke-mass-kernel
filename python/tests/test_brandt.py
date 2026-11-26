import json
import unittest
from fractions import Fraction
from pathlib import Path

from hecke_mass.adapters.brandt import audit_brandt_matrix


REFERENCES = json.loads(
    (
        Path(__file__).resolve().parents[1] / "examples" / "brandt_reference.json"
    ).read_text()
)


class BrandtAuditTests(unittest.TestCase):
    def test_saved_brandt_matrices(self):
        for level, case in REFERENCES.items():
            with self.subTest(level=level):
                prime = case["prime"]
                expected_mass = Fraction(case["expected_mass"])
                orders = case["stabilizer_orders"]
                report = audit_brandt_matrix(
                    iter(orders),
                    map(iter, case["matrix"]),
                    prime=prime,
                    expected_mass=expected_mass,
                )
                self.assertTrue(report.ok)
                self.assertEqual(report.mass, expected_mass)
                self.assertEqual(report.row_sums, (prime + 1,) * len(orders))
                self.assertTrue(report.detailed_balance)

    def test_transposing_the_matrix_breaks_balance(self):
        case = REFERENCES["level_23"]
        report = audit_brandt_matrix(
            case["stabilizer_orders"], zip(*case["matrix"]), prime=case["prime"]
        )
        self.assertFalse(report.ok)
        self.assertFalse(report.detailed_balance)
        self.assertEqual(report.row_sums, (2, 6, 1))

    def test_projective_orders_change_mass_without_changing_balance(self):
        case = REFERENCES["level_11"]
        report = audit_brandt_matrix(
            (d // 2 for d in case["stabilizer_orders"]),
            case["matrix"],
            prime=case["prime"],
            expected_mass=Fraction(case["expected_mass"]),
        )
        self.assertTrue(report.detailed_balance)
        self.assertEqual(report.mass, Fraction(5, 6))
        self.assertFalse(report.ok)

    def test_arbitrary_precision_order(self):
        order = 2**240
        report = audit_brandt_matrix(
            [order], [[3]], prime=2, expected_mass=Fraction(1, order)
        )
        self.assertTrue(report.ok)
        self.assertEqual(report.mass, Fraction(1, order))

    def test_invalid_inputs(self):
        invalid = [
            ([], [], 2, None, ValueError),
            ([4, 6], [[3, 0]], 2, None, ValueError),
            ([4], [[3, 0]], 2, None, ValueError),
            ([0], [[3]], 2, None, ValueError),
            ([4], [[-3]], 2, None, ValueError),
            ([4], [[3.0]], 2, None, TypeError),
            ([4.0], [[3]], 2, None, TypeError),
            ([4], [[3]], 2, 0.25, TypeError),
            ([4], [[3]], 2, -1, ValueError),
            ([4], [[3]], 1, None, ValueError),
        ]
        for orders, matrix, prime, expected_mass, error in invalid:
            with self.subTest(
                orders=orders, matrix=matrix, prime=prime, expected_mass=expected_mass
            ):
                with self.assertRaises(error):
                    audit_brandt_matrix(
                        orders, matrix, prime=prime, expected_mass=expected_mass
                    )
