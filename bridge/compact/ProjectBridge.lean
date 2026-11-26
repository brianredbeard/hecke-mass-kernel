import Minimal
import Lib.Adelic.Hecke.HeckeBasic
import Lib.Adelic.Hecke.ClassMean

namespace ResearchMass

def value (a : Fraction) : ℚ := (a.num : ℚ) / a.den

@[simp] theorem value_zero : value zero = 0 := by simp [value, zero]
@[simp] theorem clean_den_ne_zero (a : Fraction) : (clean a).den ≠ 0 := by
  simp only [clean, beq_iff_eq]
  split <;> simp_all [zero]
@[simp] theorem value_clean (a : Fraction) : value (clean a) = value a := by
  simp only [clean, beq_iff_eq]
  split <;> simp_all [value, zero]
@[simp] theorem value_add (a b : Fraction) : value (add a b) = value a + value b := by
  rw [← value_clean a, ← value_clean b]
  have ha : ((clean a).den : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr (clean_den_ne_zero a)
  have hb : ((clean b).den : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr (clean_den_ne_zero b)
  simp only [add, value, Int.cast_add, Int.cast_mul, Nat.cast_mul]
  field_simp
  simp_all
@[simp] theorem value_mul (a b : Fraction) : value (mul a b) = value a * value b := by
  rw [← value_clean a, ← value_clean b]
  simp [mul, value, div_mul_div_comm]
@[simp] theorem value_reciprocalNat (n : ℕ) : value (reciprocalNat n) = (n : ℚ)⁻¹ := by
  simp only [reciprocalNat, beq_iff_eq]
  split <;> simp_all [value, zero]

theorem mass_eq_list (orders : List ℕ) : value (mass orders) = (orders.map fun (n : ℕ) => (n : ℚ)⁻¹).sum := by
  induction orders with
  | nil => simp [mass]
  | cons n ns ih => simp [mass, ih]

theorem weightedSum_eq_list (xs : List (Fraction × Fraction)) :
    value (weightedSum xs) = (xs.map fun p => value p.1 * value p.2).sum := by
  induction xs with
  | nil => simp [weightedSum]
  | cons p ps ih => rcases p with ⟨a,b⟩; simp [weightedSum, ih]

theorem mass_ofFn {n : ℕ} (orders : Fin n → ℕ) :
    value (mass (List.ofFn orders)) = ∑ i, (orders i : ℚ)⁻¹ := by
  rw [mass_eq_list, List.map_ofFn, List.sum_ofFn]
  rfl

/-- Completeness and stabilizer cardinalities are certified inputs, not computed here. -/
theorem mass_classSum {G : Type*} [Group G] (Γ K : Subgroup G) {n : ℕ}
    (rep : Fin n → G) (orders : Fin n → ℕ)
    (complete : Function.Bijective fun i => (DoubleCoset.mk Γ K (rep i) : DoubleCosets Γ K))
    (correct : ∀ i, orders i = Nat.card (classAut Γ K (rep i))) :
    value (mass (List.ofFn orders)) = classSum Γ K (fun _ => (1 : ℚ)) := by
  rw [mass_ofFn, classSum]
  simp only [smul_eq_mul, mul_one]
  rw [← finsum_comp _ complete]
  rw [finsum_eq_sum_of_fintype]
  apply Finset.sum_congr rfl
  intro i _
  rw [correct, card_classAut_out]

/-- The same certified table, interpreted in the real-valued compact mass convention. -/
theorem mass_classSum_real {G : Type*} [Group G] (Γ K : Subgroup G) {n : ℕ}
    (rep : Fin n → G) (orders : Fin n → ℕ)
    (complete : Function.Bijective fun i => (DoubleCoset.mk Γ K (rep i) : DoubleCosets Γ K))
    (correct : ∀ i, orders i = Nat.card (classAut Γ K (rep i))) :
    (value (mass (List.ofFn orders)) : ℝ) = classSum Γ K (fun _ => (1 : ℝ)) := by
  rw [mass_ofFn, classSum]
  simp only [Rat.cast_sum, Rat.smul_def, mul_one]
  rw [← finsum_comp _ complete, finsum_eq_sum_of_fintype]
  apply Finset.sum_congr rfl
  intro i _
  rw [correct, card_classAut_out]

/-- The operator table retains distinct cosets even when their action values coincide. -/
theorem weightedSum_heckeFun {G : Type*} [Group G] (K : Subgroup G)
    {W : Type*} [AddCommMonoid W] [Module ℚ W]
    (π : Representation ℚ G W) (readout : W →ₗ[ℚ] ℚ) (f : G → ℚ) (v : W) {n : ℕ}
    (rep : Fin n → G) (weights samples : Fin n → Fraction)
    (rightInvariant : ∀ g (k : K), f (g * k) = f g)
    (fixed : v ∈ levelSpace π K)
    (distinct : Function.Injective fun i => (rep i : G ⧸ K))
    (covers : ∀ g, f g ≠ 0 → ∃ i, (rep i : G ⧸ K) = g)
    (weights_ok : ∀ i, value (weights i) = f (rep i))
    (samples_ok : ∀ i, value (samples i) = readout (π (rep i) v)) :
    value (weightedSum (List.ofFn fun i => (weights i, samples i))) = readout (heckeFun π K f v) := by
  rw [weightedSum_eq_list]
  simp only [List.map_ofFn, List.sum_ofFn]
  have h := heckeFun_eq_sum (π := π) (K := K) (f := f) (v := v) rightInvariant fixed
    (s := Finset.univ) (r := rep) distinct.injOn (by simpa using covers)
  rw [h.2]
  simp [weights_ok, samples_ok, smul_eq_mul, map_sum]

#print axioms mass_classSum
#print axioms mass_classSum_real
#print axioms weightedSum_heckeFun
#print axioms value_add
#print axioms value_mul
end ResearchMass
