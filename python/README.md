# hecke-mass

Exact rational arithmetic for finite class masses, normalized Hecke sums,
and orbit audits. The Python package wraps the Rust kernel. Inputs use
Python integers and `fractions.Fraction`, including integers larger than
machine words. The core wheel has no Python runtime dependencies.

## Install

Install a published wheel with `python -m pip install hecke-mass`. To build
from this repository, use CPython 3.10 or newer and a Rust toolchain.
From the repository root, run

```sh
python -m pip install ./python
```

Use `./python[crystal]` for spglib or `./python[graphs]` for pynauty.
The graph adapter supports simple uncolored undirected graphs through
13 vertices, where automorphism orders are within nauty's exact integer
range. The core orbit audit also accepts arbitrary-size exact integer
orders from other exporters.

## Exact arithmetic

```python
from fractions import Fraction

from hecke_mass import class_mass, hecke, orbit_completeness

assert class_mass([4, 6]) == Fraction(5, 12)
assert hecke(1, 3, 2, 5, [1]) == Fraction(1, 81)

report = orbit_completeness(12, [4, 6], 6)
assert (report.status, report.covered, report.deficit) == ("missing", 5, 1)
```

`check_detailed_balance(orders, matrix)` tests the row-oriented condition
$B_{ij}/d_i=B_{ji}/d_j$. Orbit coverage uses $|G|\sum_i 1/d_i$.
Inferring that every orbit is represented requires correct stabilizer
orders, distinct orbits, and an independent target for the same group action.

## Cookbooks

- Audit reciprocal mesh partitions and compute exact weights from
  crystallographic rotations. [spglib notebook](https://github.com/brianredbeard/hecke-mass-kernel/blob/main/python/examples/spglib_mesh.ipynb)
- Replay the automorphism orders of unlabeled graphs, then remove one
  orbit and measure the deficit. [pynauty notebook](https://github.com/brianredbeard/hecke-mass-kernel/blob/main/python/examples/pynauty_orbits.ipynb)
- Audit a SageMath Brandt matrix and compare a Hecke eigenvalue with an
  LMFDB record. [Sage and LMFDB notebook](https://github.com/brianredbeard/hecke-mass-kernel/blob/main/python/examples/sage_lmfdb.ipynb)

## Build and publish

The Python distributions workflow builds ABI3 wheels and a source archive,
then tests the installed wheels. Run it manually with publishing disabled
to obtain the artifacts. To enable PyPI Trusted Publishing, register the
pending publisher for `hecke-mass` with repository
`brianredbeard/hecke-mass-kernel`, workflow `python.yml`, and environment
`pypi`. The workflow publishes from `main` when dispatched with
`publish` enabled. [PyPI setup instructions](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
