# Phase 02 and 2.1 workbench review

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

## GoodTuple certificates and the rank-nine host

The upstream emitter compiled 12 rank-eight polynomial presentations with four local `IsGood` assertions per input, and its separate table replay compiled 13 certificates. It rejected six invalid raw inputs on their respective clauses. Every published host has odd rank. The rank-eight samples also share the bad prime 2, which violates the host disjointness premise.

Phase 2.1 adds two distinct local certificate families at rank nine, the least odd rank in the local degree window. Each uses $\mathbf F_{97}$ and $\mathbf F_{91249}$, verifies local `IsGood` in both character orientations, and has disjoint exceptional sets. The upstream receipt records compile times of 19.80 s and 21.91 s. The independent arithmetic replay reproduced all 72 root coordinates from the supplied polynomial data.

The upstream Lean theorem `host_prime_lower_bound` requires each selected prime of a published rank-nine host to exceed 4,700,224. This excludes both local certificate primes. A separate arithmetic replay confirmed that 279,354,519,121 and 279,379,969,937 satisfy the example's conductor congruences and disjointness. A full rank-nine host with compatible polynomial and character data remains open.

## PairGood

The upstream Lean obstruction proves that $(59,7079)$ fails the coupled `PairGood` windows at every admissible positive scale, even though the separate finite arithmetic window admits it. The interval prototype checks selected analytic examples. An effective uniform threshold and coverage of all relevant primitive-character strips remain open.

## Release verification

| Scope | Phase 02 | Phase 2.1 |
| --- | --- | --- |
| Artifact hashes and local links | 231 hashes, 406 links | 246 hashes, 432 links |
| Extracted executable gate | 24 generated table accessors used `propext` | Exit 0, all 350 extracted executables have empty transitive axiom lists |
| Historical helpers | 22 recorded exceptions | Four became axiom-free, 18 match the registered source and axiom footprints |
| All mathematical objectives | Exit 1, open | Exit 1, open |

The Phase 2.1 upstream workbench suite also exited 0. Its Lean audit covers 57 source files and 28,527 declarations. The stored declaration footprints contain only `propext`, `Classical.choice`, and `Quot.sound`. The all-objectives gate still records four open items covering the obstructed rank-eight host target, unconditional named-field mass identification, the effective analytic `PairGood` threshold and strip coverage, and the complete rank-nine host.

The original review matched all 109 local Phase 02 manifest entries. For Phase 2.1, all 124 entries under `proof_profile/research/phase-02/` match the current manifest, and the manifest hash matches the receipt. The historical manifests and receipts are preserved as `phase-02-manifest.json` and `phase-02-verification.json`. The current `manifest.json`, `verification.json`, and `lean-audit.json` are the upstream evidence for Phase 2.1. The local review checked those records and replayed the two rank-nine arithmetic scripts. The full upstream suite and Lean recompilation require the source checkout.

## Provenance and replay

The source is the Phase 02 workbench at revision `4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e`, built upstream with Lean 4.33.1. Under `proof_profile/research/phase-02/`, the compact Lean cases use `workbench-modular/{certificates,result}.json`, `workbench-hermitian/{singletons,determinant-five,result}.json`, and the products documented in `gaps/absolute-mass/review.md`.

The standalone kernel replay uses the repository's pinned Lean toolchain and checked-in cases.

```sh
mkdir -p build
(cd lean && lake exe kernel_vectors) > build/kernel.tsv
cmp build/kernel.tsv tests/vectors/kernel.tsv
```

With the ignored Phase 2.1 artifacts present, replay the rank-nine arithmetic from the repository root using Python with `sympy` installed.

```sh
rank_nine=proof_profile/research/phase-02/gaps/rank-nine
python3 -B "$rank_nine/check_conductor.py" | cmp - "$rank_nine/conductor_example.json"
python3 -B "$rank_nine/independent_replay.py" | cmp - "$rank_nine/independent_result.json"
```
