# Phase 02 workbench review

The standalone kernel replays the finite arithmetic for the level-23 and level-37 Brandt operators and four definite Hermitian genera. It uses the supplied stabilizer lists and neighbor destinations as inputs. The upstream workbench supplies the geometric interpretation of those inputs.

## Integrated arithmetic

| Case | Full stabilizer orders | Full mass | Operators | Directed edges |
| --- | --- | --- | ---: | ---: |
| Modular level 23 | 4, 2, 6 | 11/12 | 14 | 957 |
| Modular level 37 | 2, 2, 2 | 3/2 | 14 | 915 |
| Gaussian rank 2 | 32 | 1/32 | 3 | 24 |
| Gaussian rank 3 | 384 | 1/384 | 3 | 146 |
| Cyclotomic rank 2 over $\mathbf Z[\zeta_{12}]$ | 288 | 1/288 | 4 | 70 |
| Gaussian determinant 5 | 16, 8 | 3/16 | 2 | 64 |

The modular projective convention divides the full stabilizer orders by two, giving masses $11/6$ and $3$. Both conventions are covered by the generated fixtures. Each operator entry comes from the indicator of its target class evaluated on the recorded destinations, with character $1$ and degree $0$. `Phase02Cases.lean` also checks each entry against its recorded matrix before emitting the fixture. The C and Rust APIs replay all 270 matrix entries and all eight mass values.

The integration review independently recomputed the 28 modular cuspidal polynomials from the reported matrices and checked them against the recorded curve counts. The modular matrices passed the row-sum, weighted-adjoint and pairwise commutation checks. The two determinant-five operators passed the weighted-adjoint and commutation checks with weights $1/16,1/8$. These review checks use the supplied matrices and counts. The upstream Python workbench replays the lattice witnesses and carries out the point counts.

The Lean fixture generator also checks the five supplied absolute-mass products. For the cyclotomic genera the base mass is $1/12$ and the rank increments multiply it by $1/24$ and $1/36$. The Gaussian products give $1/32$ at rank two and $1/384$ at rank three, with the rank-two dyadic factor $3/4$. Upstream Lean identifications with actual genus masses require the named-field and mass-formula premises. Upstream stopping theorems also require membership, distinct classes and true positive stabilizer orders.

## GoodTuple and PairGood

The upstream emitter compiled 12 raw polynomial presentations with four local `IsGood` assertions per input, and its separate table replay compiled 13 certificates. The six invalid raw inputs were rejected on their respective clauses. The sampled rank is even, while the published host rank is odd. The sampled bad-prime sets also overlap at 2, which violates the host disjointness premise. The certificates therefore apply to the local predicates and table acceptance.

The upstream Lean obstruction proves that $(59,7079)$ fails the coupled `PairGood` windows at every admissible positive scale, even though the separate finite arithmetic window admits it. The interval prototype checks selected analytic examples. An effective uniform threshold and coverage of all relevant primitive-character strips remain open.

## Provenance and replay

The source is the Phase 02 workbench at revision `4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e`, built upstream with Lean 4.33.1. Under `proof_profile/research/phase-02/`, the compact Lean cases use `workbench-modular/{certificates,result}.json`, `workbench-hermitian/{singletons,determinant-five,result}.json`, and the products documented in `gaps/absolute-mass/review.md`.

The integration review matched the SHA-256 digests of all 109 locally available Phase 02 files listed in the upstream manifest. The upstream verified-subset record covers 231 files and 406 links, and the strict release check records four open objectives. The axiom ledger lists 22 inherited executable exceptions and 24 generated table accessors using `propext`. The standalone replay uses the repository's pinned Lean toolchain and checked-in cases and runs independently of the ignored upstream checkout.

```sh
mkdir -p build
(cd lean && lake exe kernel_vectors) > build/kernel.tsv
cmp build/kernel.tsv tests/vectors/kernel.tsv
```
