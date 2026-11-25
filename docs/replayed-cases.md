# Replayed cases

Beyond the level-11 example, the fixtures replay the finite arithmetic for the level-23 and level-37 Brandt matrices and for four definite Hermitian genera. The stabilizer orders, neighbour destinations and expected matrices are checked in as data in `lean/HeckeMassKernel/Phase02Cases.lean`.

| Case | Full stabilizer orders | Full mass | Operators | Directed edges |
| --- | --- | --- | ---: | ---: |
| Modular level 23 | 4, 2, 6 | 11/12 | 14 | 957 |
| Modular level 37 | 2, 2, 2 | 3/2 | 14 | 915 |
| Gaussian rank 2 | 32 | 1/32 | 3 | 24 |
| Gaussian rank 3 | 384 | 1/384 | 3 | 146 |
| Cyclotomic rank 2 over $\mathbf Z[\zeta_{12}]$ | 288 | 1/288 | 4 | 70 |
| Gaussian determinant 5 | 16, 8 | 3/16 | 2 | 64 |

The modular projective convention divides the full stabilizer orders by two, giving masses $11/6$ and $3$. Both conventions are in the fixtures.

## What the replay establishes

For each operator, the Lean fixture generator takes the recorded destination class of every neighbour, forms the indicator of each target class, and evaluates `hecke` on it with character $1$ and degree $0$. It stops with an error unless every result equals the recorded matrix entry. It evaluates `classMass` on each list of orders the same way. The C and Rust tests then replay all 270 matrix entries and all eight mass values from the generated fixtures.

This shows that the three implementations agree with each other and with the recorded tables. It does not show that the recorded tables are the true Brandt matrices or genus masses. The neighbour computations that produced them are not part of this repository.

## Comparing the data with public sources

The recorded values can be compared with published ones.

- **Level 37.** The eigenvalues of each matrix should be $p+1$ and the coefficients $a_p$ of the two rational newforms of level 37. They are, for all 14 primes, when $a_p$ is computed by counting points on $y^2+y=x^3-x$ and $y^2+y=x^3+x^2-23x-50$. [LMFDB 37.2.a.a](https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/37/2/a/a/) · [LMFDB 37.2.a.b](https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/37/2/a/b/)
- **Level 23.** Every row sums to $p+1$, and the remaining two eigenvalues are conjugate in $\mathbf Q(\sqrt5)$, the coefficient field of the newform of level 23. [LMFDB 23.2.a.a](https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/23/2/a/a/)
- **Hermitian genera.** The [prior-art report](../reports/Prior%20Art%20for%20Finite%20Arithmetic.md) matches the Gaussian masses $1/32$ and $1/384$ to Schiemann's tables and derives the cyclotomic value from earlier mass formulas.

## Regenerating the fixtures

```sh
mkdir -p build
(cd lean && lake exe kernel_vectors) > build/kernel.tsv
cmp build/kernel.tsv tests/vectors/kernel.tsv
```
