# Upstream equivalence bridge

The [compact GRH bridge](compact/) checks the current finite kernel against
the compact edition under Lean 4.35.0. The original RH bridge below uses
Lean 4.33.1.

The standalone [`lean/`](../lean/) package intentionally has zero external
dependencies (Lean 4.19.0 `Init` only) so readers can build and inspect the
rational kernel without fetching Mathlib or the 17-million-line parent proof.

This directory provides the formal bridge theorems linking the rational finite
sums back to the exact declarations in Alpöge’s frozen formalization:

- `HeckeMassBridge.rationalMass_correct`: casts the rational reciprocal sum
  `∑ i, (orders i : ℚ)⁻¹` to `ℝ` and proves equality with
  `GlobalTheory.Mass.classMass Γ K`, given a complete bijective set of
  double-coset representatives and matching stabilizer cardinalities.
- `HeckeMassBridge.rationalCoefficient_correct`: casts the rational normalized
  Hecke sum `u⁻¹ * (q ^ (k * (rank / 2)))⁻¹ * ∑ a, v a` to `ℂ` and proves
  equality with `GlobalTheory.SeriesTie.Setup.hecke`, given an injective
  enumeration of `R`, matching character value `u`, and matching samples `v`.
- `HeckeMassBridge.rationalCoefficient_reads`: combines
  `rationalCoefficient_correct` with `GlobalTheory.SeriesTie.HeckeAt` to show
  the rational evaluation equals the target form readout `rd g x`.

## How to check

Run inside a compiled checkout of the frozen mirror at commit
`4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e` (Lean `4.33.1`):

```sh
lake env lean /path/to/hecke-mass-kernel/bridge/UpstreamEquivalence.lean
```

Each bridge theorem depends only on Lean’s three standard axioms
(`propext`, `Classical.choice`, `Quot.sound`), and the executable rational
definitions `rationalMass` and `rationalCoefficient` use no extra axioms.

## Compact GRH bridge

From the kernel repository, point the checker at the compiled compact package
directory containing its `lake-manifest.json`.

```sh
bash bridge/compact/check.sh /path/to/grh-compact
```

The checker requires Bash, Git, Python 3 and a compiled checkout at
`72fead102f663d5c7a407964a13dc0cf9d977207` with Mathlib at
`56a005855ea17e0b0958f73ec801ae140b0a1679`. It uses the package's
`.lake/research-toolchain/bin` when available, or Lake on `PATH`.
It compiles the standalone package's current `HeckeMassKernel/Finite.lean`
and the three bridge modules into a fresh temporary directory. It checks the
axiom reports for these results against `propext`, `Classical.choice` and
`Quot.sound`.

- `KernelCompact.mass_eq` identifies the kernel's mass with the compact
  extraction's rational sum for every list of orders.
- `KernelCompact.mass_classSum_real` identifies that value with compact
  `classSum` given a bijection of representatives and their stabilizer orders.
- `KernelCompact.hecke_value` evaluates the kernel's normalized rational
  Hecke formula, including inputs with zero inverses.
- `ResearchMass.weightedSum_heckeFun` relates a certified coset table to a
  linear readout of compact `heckeFun`. Identifying that readout with the
  normalized kernel formula still requires matching the weights and normalization.

The original contribution records its source snapshot, hashes and axiom
report against the earlier kernel revision. [Contribution evidence](../proof_profile/contributions/hecke/)
