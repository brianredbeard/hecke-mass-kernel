/-!
Formal bridge between the standalone rational kernel formulas and the pinned
upstream declarations in Levent Alpöge's Lean 4.33.1 formalization
(commit `4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e`).

Check from a compiled checkout of that repository with:
  `lake env lean /path/to/hecke-mass-kernel/bridge/UpstreamEquivalence.lean`
-/

import Development.AbelianVarietyTheory.Definitions.Foundations.ClassMassEqSumOfBijective
import Development.AbelianVarietyTheory.Definitions.NonGaloisDescent.AdmQAdmissibleConjugatePairPlaces

namespace HeckeMassBridge

section ClassMass

open Formalism.UG GlobalTheory.Mass

/-- Rational class mass on a finite table of stabilizer orders. -/
def rationalMass {n : ℕ} (orders : Fin n → ℕ) : ℚ :=
  ∑ i, (orders i : ℚ)⁻¹

/-- Given a complete bijective set of double-coset representatives and their
true stabilizer orders, casting `rationalMass` to `ℝ` equals `classMass`. -/
theorem rationalMass_correct {G : Type} [Group G] (Γ K : Subgroup G) {n : ℕ}
    (g : Fin n → G) (orders : Fin n → ℕ)
    (complete : Function.Bijective fun i => (DoubleCoset.mk Γ K (g i) : ClassSet Γ K))
    (correct : ∀ i, orders i = Nat.card (stabAt Γ K (g i))) :
    (rationalMass orders : ℝ) = classMass Γ K := by
  rw [classMass_eq_sum_of_bijective g complete]
  simp [rationalMass, correct, Rat.cast_sum]

end ClassMass

section HeckeOperator

open Formalism.BasicNotions Formalism.BasicNotions.TH Formalism.IndefR Formalism.IndefR.Datum
  GlobalTheory.ExportSeries GlobalTheory.SeriesTie
open Formalism.IndefR.Links (Vc Wc)
open Formalism.MainNotions.GlobalTheoryTheory.GenusMassVolumes Formalism.MainNotions.StandardLattice
  Formalism.L2.Theta Formalism.L2.DIV IsDedekindDomain NumberField Formalism.ConjugateSelfDual
  ReciprocityTheory.Gal

/-- Rational normalized Hecke coefficient on a finite table of samples. -/
def rationalCoefficient {n : ℕ} (u : ℚ) (q k rank : ℕ) (v : Fin n → ℚ) : ℚ :=
  u⁻¹ * ((q : ℚ) ^ (k * (rank / 2)))⁻¹ * ∑ a, v a

variable {D : D7} {N : NData D.R D.host D.what₂} {X : NTw D.R D.host D.what₂ D.LL0 N}

/-- Given an injective enumeration of `R`, a matching character value `u`, and
matching rational samples `v`, casting `rationalCoefficient` to `ℂ` equals
`Setup.hecke`. -/
theorem rationalCoefficient_correct
    (ρ : Setup X) (i : X.Tw) (j : Fin D.R.m) (b : Bool)
    (k : ℕ) (P : Pl D.host.E) (R : Finset (GA D (Wc D j))) (z : (AE D)ˣ)
    (F : GA D (Wc D j) → ℂ) (x : GA D (Wc D j))
    {n : ℕ} (rep : Fin n ↪ GA D (Wc D j)) (complete : R = Finset.univ.map rep)
    (u : ℚ) (v : Fin n → ℚ) (char_ok : (u : ℂ) = (((ρ.B i j b).mu z : Circle) : ℂ))
    (values_ok : ∀ a, (v a : ℂ) = F (x * rep a)) :
    (rationalCoefficient u (normV P) k (Vc D j).rank v : ℂ) =
      ρ.hecke i j b k P R z F x := by
  rw [ρ.hecke_apply, complete]
  simp [rationalCoefficient, Rat.cast_sum, char_ok, values_ok]

/-- Under `HeckeAt` and a certified Hecke datum, `rationalCoefficient` equals
the target form readout `rd g x`. -/
theorem rationalCoefficient_reads
    {ρ : Setup X} {Y : NExp D.R D.host D.what₂ D.LL0 N X} {i : X.Tw} {j : Fin D.R.m} {b : Bool}
    (rd : Rd ρ Y i j b) {k P α R z} (datum : ρ.IsHeckeDatum i j b k P α R z)
    {f g : Y.Fm i ((j : ℕ) + 1) b} (reads : HeckeAt rd k P f g)
    (x : GA D (Wc D j)) {n : ℕ} (rep : Fin n ↪ GA D (Wc D j))
    (complete : R = Finset.univ.map rep) (u : ℚ) (v : Fin n → ℚ)
    (char_ok : (u : ℂ) = (((ρ.B i j b).mu z : Circle) : ℂ))
    (values_ok : ∀ a, (v a : ℂ) = rd f (x * rep a)) :
    (rationalCoefficient u (normV P) k (Vc D j).rank v : ℂ) = rd g x :=
  (rationalCoefficient_correct ρ i j b k P R z (rd f) x rep complete u v char_ok values_ok).trans
    (congrFun (reads α R z datum) x).symm

end HeckeOperator

end HeckeMassBridge
