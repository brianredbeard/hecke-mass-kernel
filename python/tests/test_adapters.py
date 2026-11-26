from fractions import Fraction
from importlib.util import find_spec
import unittest
from unittest.mock import patch

from hecke_mass.adapters import (
    audit_mesh_mapping,
    audit_pynauty_graphs,
    audit_spglib_mesh,
)


IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
INVERSION = ((-1, 0, 0), (0, -1, 0), (0, 0, -1))
CUBIC = (IDENTITY, [(0, 0, 0)], [1])


class MeshMappingTests(unittest.TestCase):
    def test_shifted_mesh_audit_is_independent_of_spglib(self):
        result = audit_mesh_mapping(
            [0, 0, 2, 2],
            [(0, 0, 0), (-1, 0, 0), (1, 0, 0), (2, 0, 0)],
            (4, 1, 1),
            [IDENTITY, IDENTITY],
            shift=(1, 0, 0),
            time_reversal=True,
        )
        self.assertEqual(result.group_order, 2)
        self.assertEqual(result.audit.covered, 4)
        self.assertEqual(result.audit.status, "complete")
        self.assertEqual([orbit.stabilizer_order for orbit in result.orbits], [1, 1])
        self.assertEqual(
            [orbit.weight for orbit in result.orbits], [Fraction(1, 2)] * 2
        )
        self.assertEqual(result.weighted_average([Fraction(1, 3), 1]), Fraction(2, 3))
        with self.assertRaises(TypeError):
            result.weighted_average([0.5, 1])
        with self.assertRaises(ValueError):
            result.weighted_average([1])

    def test_detects_equal_size_wrong_partitions(self):
        with self.assertRaisesRegex(ValueError, "orbit"):
            audit_mesh_mapping(
                [0, 1, 0, 1],
                [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)],
                (4, 1, 1),
                [IDENTITY, INVERSION],
                shift=(1, 0, 0),
            )

    def test_rejects_bad_addresses_and_non_groups(self):
        with self.assertRaisesRegex(ValueError, "distinct"):
            audit_mesh_mapping([0, 0], [(0, 0, 0), (2, 0, 0)], (2, 1, 1), [IDENTITY])
        shear = ((1, 1, 0), (0, 1, 0), (0, 0, 1))
        with self.assertRaisesRegex(ValueError, "group"):
            audit_mesh_mapping([0], [(0, 0, 0)], (1, 1, 1), [IDENTITY, shear])


@unittest.skipUnless(find_spec("spglib"), "spglib extra not installed")
class SpglibTests(unittest.TestCase):
    def test_cubic_group_and_nonuniform_weights(self):
        import spglib

        result = audit_spglib_mesh(CUBIC, (2, 2, 2))
        self.assertEqual(result.group_order, 48)
        self.assertEqual([orbit.multiplicity for orbit in result.orbits], [1, 3, 3, 1])
        self.assertEqual(
            [orbit.stabilizer_order for orbit in result.orbits], [48, 16, 16, 48]
        )
        self.assertEqual(result.weighted_average([0, 1, 0, 0]), Fraction(3, 8))
        mapping, addresses = spglib.get_ir_reciprocal_mesh(
            (2, 2, 2), CUBIC, is_time_reversal=False
        )
        rotations = spglib.get_symmetry_dataset(CUBIC).rotations
        self.assertEqual(
            audit_mesh_mapping(mapping, addresses, (2, 2, 2), rotations), result
        )

    def test_shifted_unequal_mesh_and_hexagonal_and_triclinic_cells(self):
        hexagonal = (
            [(1, 0, 0), (-0.5, 3**0.5 / 2, 0), (0, 0, 1.6)],
            [(0, 0, 0)],
            [1],
        )
        triclinic = (
            [(1, 0, 0), (0.2, 1.1, 0), (0.35, 0.4, 1.8)],
            [(0, 0, 0)],
            [1],
        )
        for cell, mesh, shift, group_order in (
            (CUBIC, (2, 3, 4), (1, 0, 1), 8),
            (hexagonal, (3, 3, 2), (0, 0, 1), 24),
            (triclinic, (2, 3, 4), (1, 0, 1), 2),
        ):
            with self.subTest(mesh=mesh, group_order=group_order):
                result = audit_spglib_mesh(cell, mesh, shift=shift, time_reversal=True)
                self.assertEqual(result.group_order, group_order)
                self.assertEqual(result.audit.status, "complete")
                self.assertEqual(sum(orbit.weight for orbit in result.orbits), 1)


@unittest.skipUnless(find_spec("pynauty"), "pynauty extra not installed")
class PynautyTests(unittest.TestCase):
    def test_four_vertex_edge_slice_and_duplicate_and_missing(self):
        from pynauty import Graph

        paths = Graph(4, adjacency_dict={0: [1, 2]})
        matching = Graph(4, adjacency_dict={0: [1], 2: [3]})
        complete = audit_pynauty_graphs(iter([paths, matching]), 4, edge_count=2)
        self.assertEqual((complete.status, complete.covered), ("complete", 15))
        missing = audit_pynauty_graphs([paths], 4, edge_count=2)
        self.assertEqual((missing.status, missing.deficit), ("missing", Fraction(3)))
        excess = audit_pynauty_graphs([paths, matching, matching], 4, edge_count=2)
        self.assertEqual((excess.status, excess.deficit), ("excess", Fraction(-3)))

    def test_rejects_graph_outside_declared_family_and_inexact_orders(self):
        from pynauty import Graph

        with self.assertRaisesRegex(ValueError, "vertices"):
            audit_pynauty_graphs([Graph(5)], 4)
        with self.assertRaisesRegex(ValueError, "undirected"):
            audit_pynauty_graphs([Graph(4, directed=True)], 4)
        with self.assertRaisesRegex(ValueError, "loops"):
            audit_pynauty_graphs([Graph(4, adjacency_dict={0: [0]})], 4)
        with self.assertRaisesRegex(ValueError, "edge count"):
            audit_pynauty_graphs([Graph(4)], 4, edge_count=2)
        with self.assertRaisesRegex(ValueError, "exact"):
            audit_pynauty_graphs([], 14)
        with patch("pynauty.autgrp", return_value=([], 2.0, 10, [], 0)):
            with self.assertRaisesRegex(ValueError, "exact"):
                audit_pynauty_graphs([Graph(4)], 4)

    def test_largest_exact_factorial_case(self):
        from pynauty import Graph

        result = audit_pynauty_graphs([Graph(13)], 13, edge_count=0)
        self.assertEqual((result.status, result.covered), ("complete", Fraction(1)))
