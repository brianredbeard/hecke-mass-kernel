import HeckeMassKernel.Finite
import Minimal
import ProjectBridge

namespace KernelCompact
open HeckeMassKernel

def val (a : Frac) : ℚ := (a.num : ℚ) / a.den

theorem eq_of_equiv {a b : Frac} (h : a ≈ b) : val a = val b := by
  unfold Frac.Equiv at h
  have h' : (a.num : ℚ) * (b.den : ℚ) = (b.num : ℚ) * (a.den : ℚ) := by exact_mod_cast h
  have ha : (a.den : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.ne_of_gt a.positive)
  have hb : (b.den : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.ne_of_gt b.positive)
  exact (div_eq_div_iff ha hb).2 h'

@[simp] theorem val_reduce (a : Frac) : val a.reduce = val a := eq_of_equiv (Frac.reduce_equiv a)

@[simp] theorem val_integer (n : ℤ) : val (Frac.integer n) = n := by simp [val, Frac.integer]

@[simp] theorem val_add (a b : Frac) : val (a.add b) = val a + val b := by
  unfold Frac.add
  rw [val_reduce]
  simp only [val, Int.cast_add, Int.cast_mul, Int.cast_natCast, Nat.cast_mul]
  have ha : (a.den : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.ne_of_gt a.positive)
  have hb : (b.den : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.ne_of_gt b.positive)
  field_simp

@[simp] theorem val_mul (a b : Frac) : val (a.mul b) = val a * val b := by
  unfold Frac.mul
  rw [val_reduce]
  simp [val, div_mul_div_comm]

theorem val_sum (xs : List Frac) : val (Frac.sum xs) = (xs.map val).sum := by
  rw [Frac.sum_eq_foldr]
  induction xs with
  | nil => simp
  | cons x xs ih => simp [ih]

@[simp] theorem val_inv (a : Frac) : val a.inv = (val a)⁻¹ := by
  rcases a with ⟨num, den, hp⟩
  cases num with
  | ofNat n =>
    cases n with
    | zero => simp [Frac.inv, Frac.integer, val]
    | succ n =>
      change val (Frac.reduce ⟨den, n+1, by omega⟩) = _
      rw [val_reduce]
      simp [val, div_eq_mul_inv, mul_comm]
  | negSucc n =>
    change val (Frac.reduce ⟨-(den : ℤ), n+1, by omega⟩) = _
    rw [val_reduce]
    simp only [val, Int.cast_neg, Int.cast_natCast, Nat.cast_add, Nat.cast_one, Int.cast_negSucc,
      neg_div, inv_div, inv_neg]

@[simp] theorem val_reciprocalNat (n : ℕ) : val (Frac.reciprocalNat n) = (n : ℚ)⁻¹ := by
  cases n with
  | zero => simp [Frac.reciprocalNat_zero]
  | succ n => simp [Frac.reciprocalNat_succ, val]

theorem hecke_value (u : Frac) (q k rank : ℕ) (xs : List Frac) :
    val (hecke u q k rank xs) = (val u)⁻¹ * ((q : ℚ) ^ (k * (rank / 2)))⁻¹ * (xs.map val).sum := by
  rw [hecke_formula]
  simp [val_sum, ← Frac.sum_eq_foldr]

theorem mass_eq (orders : List ℕ) : val (classMass orders) = ResearchMass.value (ResearchMass.mass orders) := by
  induction orders with
  | nil => simp [classMass_nil, ResearchMass.mass]
  | cons n ns ih => simp [classMass_cons, ResearchMass.mass, ih]

theorem mass_classSum_real {G : Type*} [Group G] (Γ K : Subgroup G) {n : ℕ}
    (rep : Fin n → G) (orders : Fin n → ℕ)
    (complete : Function.Bijective fun i => (DoubleCoset.mk Γ K (rep i) : DoubleCosets Γ K))
    (correct : ∀ i, orders i = Nat.card (classAut Γ K (rep i))) :
    (val (classMass (List.ofFn orders)) : ℝ) = classSum Γ K (fun _ => (1 : ℝ)) := by
  rw [mass_eq]
  exact ResearchMass.mass_classSum_real Γ K rep orders complete correct

#print axioms mass_eq
#print axioms mass_classSum_real
#print axioms hecke_value
end KernelCompact
