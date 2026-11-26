"""Export exact stabilizer orders for the simple cubic 2×2×2 reciprocal mesh."""

from collections import defaultdict
from itertools import permutations, product

import spglib


def main():
    cell = ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 0, 0]], [1])
    mapping, addresses = spglib.get_ir_reciprocal_mesh(
        [2, 2, 2], cell, is_shift=[0, 0, 0], is_time_reversal=False
    )
    points = [tuple(int(x) % 2 for x in address) for address in addresses]
    if len(mapping) != 8 or set(points) != set(product(range(2), repeat=3)):
        raise ValueError("expected all eight periodic grid points")

    fibers = defaultdict(set)
    for point, representative in zip(points, mapping, strict=True):
        representative = int(representative)
        if not 0 <= representative < len(points):
            raise ValueError(f"invalid representative index {representative}")
        fibers[representative].add(point)

    orders = []
    for representative, members in fibers.items():
        point = points[representative]
        # The 48 signed permutations act on the periodic integer addresses.
        images = [
            tuple(sign * point[axis] % 2 for sign, axis in zip(signs, axes))
            for axes in permutations(range(3))
            for signs in product((-1, 1), repeat=3)
        ]
        order = images.count(point)
        if members != set(images) or len(members) * order != 48:
            raise ValueError(f"incorrect orbit at {point}")
        orders.append(order)

    for order in orders:
        print(order)


if __name__ == "__main__":
    main()
