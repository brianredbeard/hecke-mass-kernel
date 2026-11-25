"""Emit a simple cubic 2×2×2 mesh for the crystal_mesh example's --stdin mode."""

import spglib


def mask(address):
    """Encode periodic half-coordinates as bits in x, y, z order."""
    return sum((int(x) % 2) << axis for axis, x in enumerate(address))


cell = ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 0, 0]], [1])
mapping, addresses = spglib.get_ir_reciprocal_mesh(
    [2, 2, 2], cell, is_shift=[0, 0, 0], is_time_reversal=False
)
for point, representative in enumerate(mapping):
    print(mask(addresses[point]), mask(addresses[representative]))
