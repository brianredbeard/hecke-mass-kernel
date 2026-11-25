# Upstream equivalence bridge

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
