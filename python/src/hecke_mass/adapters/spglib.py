"""Audit reciprocal-mesh partitions under exact integer point-group actions."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from math import prod
from operator import index

from .. import OrbitAudit, hecke, orbit_completeness

Vector = tuple[int, int, int]
Matrix = tuple[Vector, Vector, Vector]
MeshActions = dict[Matrix, tuple[Matrix, Vector]]

_IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
_UNSHIFTED = (0, 0, 0)


@dataclass(frozen=True, slots=True)
class MeshOrbit:
    """A mesh orbit with its address reduced modulo the grid dimensions."""

    representative: int
    address: Vector
    multiplicity: int
    stabilizer_order: int
    weight: Fraction


@dataclass(frozen=True, slots=True)
class MeshAudit:
    """A checked partition and its group order and orbit coverage."""

    group_order: int
    orbits: tuple[MeshOrbit, ...]
    audit: OrbitAudit

    def weighted_average(self, values: Iterable[int | Fraction]) -> Fraction:
        """Average one exact observable per orbit in representative order."""

        def weighted_values():
            for orbit, value in zip(self.orbits, values, strict=True):
                if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
                    raise TypeError("observable values must be integers or Fractions")
                yield orbit.weight * value

        return hecke(1, 1, 0, 0, weighted_values())


def _triple(values: Iterable[int], name: str) -> Vector:
    try:
        x, y, z = map(index, values)
    except TypeError as error:
        raise TypeError(f"{name} must contain integers") from error
    except ValueError as error:
        raise ValueError(f"{name} must have length 3") from error
    return x, y, z


def _mesh_parameters(
    mesh: Iterable[int], shift: Iterable[int]
) -> tuple[Vector, Vector]:
    shape = _triple(mesh, "mesh")
    offsets = _triple(shift, "shift")
    if min(shape) <= 0:
        raise ValueError("mesh dimensions must be positive")
    if any(coordinate not in (0, 1) for coordinate in offsets):
        raise ValueError("shift components must be 0 or 1")
    return shape, offsets


def _rotation(rows: Iterable[Iterable[int]]) -> Matrix:
    try:
        a, b, c = (_triple(row, "rotation row") for row in rows)
    except ValueError as error:
        raise ValueError("rotations must be 3 by 3 matrices") from error
    determinant = (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        + a[1] * (b[2] * c[0] - b[0] * c[2])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )
    if abs(determinant) != 1:
        raise ValueError("rotation matrices must have determinant 1 or -1")
    return a, b, c


def _dot(left: Vector, right: Vector) -> int:
    return sum(x * y for x, y in zip(left, right))


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    columns = tuple(zip(*right))
    return tuple(tuple(_dot(row, col) for col in columns) for row in left)


def _mesh_actions(
    rotations: Iterable[Iterable[Iterable[int]]],
    mesh: Vector,
    shift: Vector,
    time_reversal: bool,
) -> MeshActions:
    direct = {_rotation(rows) for rows in rotations}
    if _IDENTITY not in direct or any(
        _multiply(left, right) not in direct for left in direct for right in direct
    ):
        raise ValueError("rotations must form a group with the identity")

    if time_reversal:
        direct |= {
            tuple(tuple(-entry for entry in row) for row in matrix) for matrix in direct
        }

    # Using transposes gives the same reciprocal group as using inverse
    # transposes. Work in grid coordinates with the rescaled matrix D R^T D^-1,
    # where D has the positive mesh sizes on its diagonal.
    actions = {}
    for rotation in sorted(direct):
        rows = []
        for i in range(3):
            coefficients = [divmod(mesh[i] * rotation[j][i], mesh[j]) for j in range(3)]
            if any(remainder for _, remainder in coefficients):
                break
            rows.append(tuple(coefficient for coefficient, _ in coefficients))
        if len(rows) != 3:
            continue

        # A half-grid shift contributes (A shift - shift)/2 in grid coordinates.
        doubled_offset = tuple(_dot(row, shift) - s for row, s in zip(rows, shift))
        if all(coordinate % 2 == 0 for coordinate in doubled_offset):
            actions[rotation] = (
                tuple(rows),
                tuple(coordinate // 2 for coordinate in doubled_offset),
            )
    return actions


def _audit_mapping(
    mapping: Iterable[int],
    addresses: Iterable[Iterable[int]],
    mesh: Vector,
    actions: MeshActions,
) -> MeshAudit:
    total_points = prod(mesh)
    points = [
        tuple(x % size for x, size in zip(_triple(address, "address"), mesh))
        for address in addresses
    ]
    if len(points) != total_points or len(set(points)) != total_points:
        raise ValueError(f"expected {total_points} distinct periodic grid addresses")
    representatives = list(map(index, mapping))
    if len(representatives) != total_points:
        raise ValueError("mapping must contain one representative index per grid point")

    fibers = defaultdict(set)
    for representative, point in zip(representatives, points):
        if not 0 <= representative < total_points:
            raise ValueError(f"representative index {representative} is out of range")
        fibers[representative].add(point)

    orbits = []
    group_order = len(actions)
    for representative, members in sorted(fibers.items()):
        point = points[representative]
        images = [
            tuple(
                (_dot(row, point) + delta) % size
                for row, delta, size in zip(matrix, offset, mesh)
            )
            for matrix, offset in actions.values()
        ]
        if set(images) != members:
            raise ValueError(
                f"mapping has an incorrect orbit at representative {representative}"
            )
        stabilizer_order = images.count(point)
        multiplicity = len(members)
        orbits.append(
            MeshOrbit(
                representative,
                point,
                multiplicity,
                stabilizer_order,
                Fraction(multiplicity, total_points),
            )
        )

    audit = orbit_completeness(
        group_order, (orbit.stabilizer_order for orbit in orbits), total_points
    )
    return MeshAudit(group_order, tuple(orbits), audit)


def audit_mesh_mapping(
    mapping: Iterable[int],
    addresses: Iterable[Iterable[int]],
    mesh: Iterable[int],
    rotations: Iterable[Iterable[Iterable[int]]],
    *,
    shift: Iterable[int] = _UNSHIFTED,
    time_reversal: bool = False,
) -> MeshAudit:
    """Check whether the supplied mapping partitions the full mesh into orbits.

    Pass the full group of direct-space rotation matrices in the mesh lattice
    basis. Repeated matrices, including those from space-group translations,
    are deduplicated. Filter to rotations preserving the entire shifted mesh
    and use that group's cardinality, including operations acting trivially on
    this mesh. Compute stabilizer orders by counting operations fixing each
    representative. A mismatched orbit or malformed input raises ValueError
    or TypeError.
    """
    shape, offsets = _mesh_parameters(mesh, shift)
    return _audit_mapping(
        mapping,
        addresses,
        shape,
        _mesh_actions(rotations, shape, offsets, time_reversal),
    )


def audit_spglib_mesh(
    cell,
    mesh: Iterable[int],
    *,
    shift: Iterable[int] = _UNSHIFTED,
    time_reversal: bool = False,
    symprec: float = 1e-5,
) -> MeshAudit:
    """Audit a spglib cell using the subgroup preserving the whole mesh.

    spglib determines the crystal symmetry at the supplied tolerance. On a
    distorted grid, only the resulting global mesh-preserving subgroup
    generates the mapping. The audit checks that mapping against the subgroup
    with integer arithmetic.
    """
    import spglib

    shape, offsets = _mesh_parameters(mesh, shift)
    dataset = spglib.get_symmetry_dataset(cell, symprec=symprec)
    if dataset is None:
        raise ValueError("spglib could not determine the cell symmetry")
    actions = _mesh_actions(dataset.rotations, shape, offsets, time_reversal)
    mesh_data = spglib.get_stabilized_reciprocal_mesh(
        shape,
        tuple(actions),
        is_shift=offsets,
        is_time_reversal=False,
        is_dense=True,
    )
    if mesh_data is None:
        raise ValueError("spglib could not construct the reciprocal mesh")
    return _audit_mapping(*mesh_data, shape, actions)
