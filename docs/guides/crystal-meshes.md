# Audit a spglib reciprocal mesh

## 1. The bug this catches

A simple cubic $2\times2\times2$ mesh has four symmetry orbits with
multiplicities $1,3,3,1$. Dropping one three-point orbit leaves a deficit of
exactly 3. The corresponding weights are $1/8,3/8,3/8,1/8$.

## 2. Export the stabilizer orders

The example uses spglib's mesh mapping and independently enumerates the 48
signed axis permutations for this cell. It checks each reported orbit's
members and exports the order of the subgroup fixing its representative.
Use Python 3.10 or later, install `spglib==2.7.0` in a virtual environment,
and run from the repository root. [spglib reciprocal-mesh API](https://spglib.readthedocs.io/en/v2.7.0/api.html#kpoints)

```bash
set -euo pipefail
python examples/audit/spglib_orders.py |
  cargo run --quiet --locked --manifest-path cli/Cargo.toml -- +    orbits --group-order 48 --expected 8
```

Expected output is `complete covered=8 deficit=0`.

## 3. Put it in CI

Run the pipe above in a Bash step after installing spglib. To simulate a
lost representative, insert `awk 'NR != 2'` between the exporter and the
CLI. This drops the first order-16 stabilizer. Expect exit code 1 and
`missing covered=5 deficit=3`.

## 4. Interpret the result

The example checks the mesh partition for a known group action, and the CLI
checks its exact total using the supplied stabilizers. In other cells,
derive the group from the reciprocal actions that preserve the specific
mesh and shift. The number of crystallographic space-group operations can
include translations that act identically on reciprocal points. Decide
whether time reversal belongs to the action before comparing weights.

## 5. Scaling and precision

Compute a representative's exact weight as its orbit size divided by the
total number of grid points. With the observable $1$ on a three-point orbit
and $0$ elsewhere, its exact mean is $3/8$. Equal weights give $1/4$, an
error of $1/8$. The audit uses integer orders and exact rational sums, while
the cost of finding the orbits depends on the symmetry tool and mesh size.
