# Verification

## Lean

`HeckeMassKernel.Finite` proves canonical lowest-terms reduction (`reduce_gcd_one`, `reduce_eq_of_equiv`, `render_eq_of_equiv`), rational ring/inversion laws, balanced pairwise summation equivalence (`sum_eq_foldr`), recursive mass equations, permutation invariance (`classMass_perm`, `hecke_perm`), additivity and linearity (`classMass_append`, `hecke_append`), full-versus-projective stabilizer scaling (`classMass_double_orders`), the mass-stopping completeness theorem (`classMass_complete_of_eq`), equivalence of the short-circuiting Hecke implementation with the direct formula (`hecke_formula`), and concrete exact outputs (`mass_six`, `mass_level_eleven`, `hecke_minus_two`, `hecke_odd_rank_even_k`). All theorems in `lean/` use zero external dependencies and only Lean’s standard axioms.

The separate [`bridge/UpstreamEquivalence.lean`](../bridge/README.md) module connects the rational formulas to Alpöge’s `GlobalTheory.Mass.classMass` and `GlobalTheory.SeriesTie.Setup.hecke` (including `HeckeAt`) when checked against the pinned parent formalization.

`HeckeMassKernel.Scaffold.probeSpec` specifies the scaffold operation on one `UInt32`. The executable reference maps the operation over a list. Lean checks that the reference preserves length and agrees with the specification at every index, including indexes outside the list.

```sh
cd lean
lake build
```

`lake build` builds the library and the three vector-generator executables.

The orbit audit computes exact covered count and signed deficit for positive
group and stabilizer orders. `orbitCompleteness_eq_some_iff` states the
validation rules and arithmetic result. `orbitCompleteness_complete_of_extension`
proves that matching the full count rules out a nonempty extension by orbits
with positive stabilizer orders. Applying that theorem to a generator
requires evidence that its inputs describe distinct orbits and that its
expected count describes the same family of labeled objects.

## Shared fixtures

`tests/vectors/scaffold.csv` contains `input,output` pairs in order, one pair of decimal `UInt32` values per line. The cases include zero, the maximum `UInt32`, high-bit boundaries, alternating bit patterns, and a deterministic sequence long enough to exercise multiple vector chunks. To regenerate the file from the repository root after updating the Lean reference or inputs, run the following commands.

```sh
mkdir -p build
(cd lean && lake exe scaffold_vectors) > build/scaffold.csv &&
  cp build/scaffold.csv tests/vectors/scaffold.csv
(cd lean && lake exe kernel_vectors) > build/kernel.tsv &&
  cp build/kernel.tsv tests/vectors/kernel.tsv
(cd lean && lake exe orbit_vectors) > build/orbit.tsv &&
  cp build/orbit.tsv tests/vectors/orbit.tsv
```

`tests/vectors/kernel.tsv` has three tab-separated columns for the operation, space-separated inputs and reduced rational output. For `mass` the inputs are the orders. For `hecke` the first four inputs are `u q k rank`, followed by the samples. The synthetic cases cover edge semantics including odd higher rank with even $k$ (distinguishing $k\lfloor r/2\rfloor$ from $\lfloor kr/2\rfloor$), fractional characters and samples with $q^e > 1$, $0^0 = 1$ via both $k=0$ and $\text{rank}=1$, arbitrary-precision $k$ and $\text{rank} > 2^{64}$, and zero-short-circuiting on huge exponents. The C and Rust integration tests run every row against their public APIs.

[Replayed cases](replayed-cases.md) identifies the recorded masses and matrices included in these fixtures and what the replay does and does not establish.

`tests/vectors/orbit.tsv` records the group order, expected total, stabilizer
orders, covered count, signed deficit, and status. It includes matching
tables, missing and extra entries, fractional coverage, and integers beyond
machine and binary64 precision. The C and Rust suites replay every row.

CI compares freshly generated fixtures with the checked-in files. The C suite tests both Release and ASan/UBSan builds (with `-Wall -Wextra -Werror`), exercises checked invalid-input rejection, pointer aliasing, and permutation invariance, and builds the installed CMake consumer requiring `COMPONENTS FiniteKernel`. The Rust suite runs unit tests, doctests, randomized property checks, fixture replay, and all six worked examples. The RVV job runs the scaffold and exact Brandt count tests under QEMU at vector lengths of 128, 256, and 512 bits. The Brandt test replays the level-11 and level-23 degree-two rows and compares vector tails against a scalar count. The Lean theorems apply to the Lean reference.
