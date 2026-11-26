namespace HeckeMassKernel

private theorem positiveIntCast {n : Nat} (h : 0 < n) : (0 : Int) < (n : Int) := by omega

private theorem natAbsNatCast (n : Nat) : (n : Int).natAbs = n := rfl

/-- An exact fraction stored with a positive denominator. -/
structure Frac where
  num : Int
  den : Nat
  positive : 0 < den
  deriving DecidableEq

namespace Frac

/-- Rational equality by cross-multiplication. -/
def Equiv (a b : Frac) : Prop :=
  a.num * (b.den : Int) = b.num * (a.den : Int)

infix:50 " ≈ " => Frac.Equiv

/-- Strict rational order by cross-multiplication. -/
def Lt (a b : Frac) : Prop :=
  a.num * (b.den : Int) < b.num * (a.den : Int)

instance : LT Frac := ⟨Frac.Lt⟩

def integer (n : Int) : Frac := ⟨n, 1, by decide⟩

/-- Reduce a fraction to lowest terms with a positive denominator. -/
def reduce (a : Frac) : Frac :=
  let g := a.num.natAbs.gcd a.den
  have hgPos : 0 < g := Nat.gcd_pos_of_pos_right _ a.positive
  have hgLe : g ≤ a.den := Nat.le_of_dvd a.positive (Nat.gcd_dvd_right _ _)
  ⟨a.num / (g : Int), a.den / g, Nat.div_pos hgLe hgPos⟩

def add (a b : Frac) : Frac :=
  reduce ⟨a.num * (b.den : Int) + b.num * (a.den : Int), a.den * b.den,
    Nat.mul_pos a.positive b.positive⟩

def mul (a b : Frac) : Frac :=
  reduce ⟨a.num * b.num, a.den * b.den, Nat.mul_pos a.positive b.positive⟩

/-- Inversion is total, with `inv 0 = 0`. -/
def inv (a : Frac) : Frac :=
  match a.num with
  | .ofNat 0 => integer 0
  | .ofNat (n + 1) => reduce ⟨(a.den : Int), n + 1, Nat.zero_lt_succ n⟩
  | .negSucc n => reduce ⟨-(a.den : Int), n + 1, Nat.zero_lt_succ n⟩

def reciprocalNat (n : Nat) : Frac := (integer n).inv

def neg (a : Frac) : Frac := ⟨-a.num, a.den, a.positive⟩

def sub (a b : Frac) : Frac := a.add b.neg

private def sumPairs : List Frac → List Frac
  | [] => []
  | [x] => [x]
  | x :: y :: rest => add x y :: sumPairs rest

private def sumFuel : Nat → List Frac → Frac
  | 0, xs => xs.foldr add (integer 0)
  | _ + 1, [] => integer 0
  | _ + 1, [x] => x.reduce
  | fuel + 1, x :: y :: rest => sumFuel fuel (add x y :: sumPairs rest)

/-- Balanced pairwise rational sum, returning a reduced fraction. -/
def sum (values : List Frac) : Frac := sumFuel values.length values

/-- Render the fraction in lowest terms. -/
def render (a : Frac) : String :=
  let r := a.reduce
  if r.den == 1 then toString r.num else s!"{r.num}/{r.den}"

-- Basic properties of `Equiv` and `reduce`.

theorem Equiv.refl (a : Frac) : a ≈ a := rfl

theorem Equiv.symm {a b : Frac} (h : a ≈ b) : b ≈ a := Eq.symm h

theorem Equiv.trans {a b c : Frac} (hab : a ≈ b) (hbc : b ≈ c) : a ≈ c := by
  unfold Equiv at *
  have hbd : (b.den : Int) ≠ 0 := by
    have := b.positive
    omega
  apply Int.eq_of_mul_eq_mul_right hbd
  calc
    a.num * (c.den : Int) * (b.den : Int)
      = (a.num * (b.den : Int)) * (c.den : Int) := by
          rw [Int.mul_assoc, Int.mul_comm (c.den : Int) (b.den : Int), ← Int.mul_assoc]
    _ = (b.num * (a.den : Int)) * (c.den : Int) := by rw [hab]
    _ = (b.num * (c.den : Int)) * (a.den : Int) := by
          rw [Int.mul_assoc, Int.mul_comm (a.den : Int) (c.den : Int), ← Int.mul_assoc]
    _ = (c.num * (b.den : Int)) * (a.den : Int) := by rw [hbc]
    _ = c.num * (a.den : Int) * (b.den : Int) := by
          rw [Int.mul_assoc, Int.mul_comm (b.den : Int) (a.den : Int), ← Int.mul_assoc]

private theorem int_ediv_mul_cancel_of_nat_dvd {x : Int} {g : Nat} (h : g ∣ x.natAbs) :
    (x / (g : Int)) * (g : Int) = x := by
  have hdvd : (g : Int) ∣ x := Int.ofNat_dvd_left.mpr h
  exact Int.ediv_mul_cancel hdvd

theorem reduce_equiv (a : Frac) : a.reduce ≈ a := by
  unfold Equiv reduce
  dsimp only
  have hgn : (a.num / ((a.num.natAbs.gcd a.den : Nat) : Int)) *
      ((a.num.natAbs.gcd a.den : Nat) : Int) = a.num :=
    int_ediv_mul_cancel_of_nat_dvd (Nat.gcd_dvd_left _ _)
  have hgd_nat : (a.den / a.num.natAbs.gcd a.den) * a.num.natAbs.gcd a.den = a.den :=
    Nat.div_mul_cancel (Nat.gcd_dvd_right _ _)
  have hgd : ((a.den / a.num.natAbs.gcd a.den : Nat) : Int) *
      ((a.num.natAbs.gcd a.den : Nat) : Int) = (a.den : Int) := by
    rw [← Int.natCast_mul, hgd_nat]
  calc
    (a.num / ((a.num.natAbs.gcd a.den : Nat) : Int)) * (a.den : Int)
      = (a.num / ((a.num.natAbs.gcd a.den : Nat) : Int)) *
          (((a.den / a.num.natAbs.gcd a.den : Nat) : Int) *
            ((a.num.natAbs.gcd a.den : Nat) : Int)) := by rw [hgd]
    _ = ((a.num / ((a.num.natAbs.gcd a.den : Nat) : Int)) *
          ((a.num.natAbs.gcd a.den : Nat) : Int)) *
          ((a.den / a.num.natAbs.gcd a.den : Nat) : Int) := by
          rw [Int.mul_assoc, Int.mul_comm ((a.den / a.num.natAbs.gcd a.den : Nat) : Int),
              ← Int.mul_assoc]
    _ = a.num * ((a.den / a.num.natAbs.gcd a.den : Nat) : Int) := by rw [hgn]

private theorem natAbs_ediv_of_dvd {x : Int} {g : Nat} (hg : 0 < g) (h : g ∣ x.natAbs) :
    (x / (g : Int)).natAbs = x.natAbs / g := by
  have hm := int_ediv_mul_cancel_of_nat_dvd h
  have hnat : (x / (g : Int)).natAbs * g = x.natAbs := by
    have := congrArg Int.natAbs hm
    simpa [Int.natAbs_mul, natAbsNatCast] using this
  have hdiv : (x.natAbs / g) * g = x.natAbs := Nat.div_mul_cancel h
  exact Nat.eq_of_mul_eq_mul_right hg (hnat.trans hdiv.symm)

private theorem gcd_div_gcd_eq_one {m n : Nat} (hg : 0 < m.gcd n) :
    (m / m.gcd n).gcd (n / m.gcd n) = 1 := by
  have hm : (m / m.gcd n) * m.gcd n = m := Nat.div_mul_cancel (Nat.gcd_dvd_left m n)
  have hn : (n / m.gcd n) * m.gcd n = n := Nat.div_mul_cancel (Nat.gcd_dvd_right m n)
  have hmul : (m / m.gcd n).gcd (n / m.gcd n) * m.gcd n = 1 * m.gcd n := by
    rw [← Nat.gcd_mul_right, hm, hn, Nat.one_mul]
  exact Nat.eq_of_mul_eq_mul_right hg hmul

private theorem dvd_of_gcd_one_of_dvd_mul_left {a b c : Nat}
    (hcop : a.gcd c = 1) (hdvd : c ∣ a * b) : c ∣ b := by
  have h1 : c ∣ c * b := Nat.dvd_mul_right c b
  have h2 : c ∣ (a * b).gcd (c * b) := Nat.dvd_gcd hdvd h1
  rw [Nat.gcd_mul_right, hcop, Nat.one_mul] at h2
  exact h2

theorem reduce_gcd_one (a : Frac) : a.reduce.num.natAbs.gcd a.reduce.den = 1 := by
  unfold reduce
  dsimp only
  have hgPos : 0 < a.num.natAbs.gcd a.den := Nat.gcd_pos_of_pos_right _ a.positive
  rw [natAbs_ediv_of_dvd hgPos (Nat.gcd_dvd_left _ _)]
  exact gcd_div_gcd_eq_one hgPos

theorem eq_of_equiv_of_gcd_one {a b : Frac}
    (ha : a.num.natAbs.gcd a.den = 1)
    (hb : b.num.natAbs.gcd b.den = 1)
    (heq : a ≈ b) : a = b := by
  unfold Equiv at heq
  have hnat : a.num.natAbs * b.den = b.num.natAbs * a.den := by
    have := congrArg Int.natAbs heq
    simpa [Int.natAbs_mul, natAbsNatCast] using this
  have hdvd1 : a.den ∣ b.den := by
    have h1 : a.den ∣ b.num.natAbs * a.den := Nat.dvd_mul_left _ _
    rw [← hnat] at h1
    exact dvd_of_gcd_one_of_dvd_mul_left ha h1
  have hdvd2 : b.den ∣ a.den := by
    have h2 : b.den ∣ a.num.natAbs * b.den := Nat.dvd_mul_left _ _
    rw [hnat] at h2
    exact dvd_of_gcd_one_of_dvd_mul_left hb h2
  have hden : a.den = b.den := Nat.dvd_antisymm hdvd1 hdvd2
  have hden_ne : (b.den : Int) ≠ 0 := by
    have := b.positive
    omega
  have hnum : a.num = b.num := by
    rw [hden] at heq
    exact Int.eq_of_mul_eq_mul_right hden_ne heq
  cases a; cases b
  simp only at hnum hden
  subst hnum; subst hden
  rfl

theorem reduce_eq_of_equiv {a b : Frac} (h : a ≈ b) : a.reduce = b.reduce := by
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one a) (reduce_gcd_one b)
  exact (reduce_equiv a).trans (h.trans (reduce_equiv b).symm)

theorem reduce_idem (a : Frac) : a.reduce.reduce = a.reduce :=
  reduce_eq_of_equiv (reduce_equiv a)

theorem render_eq_of_equiv {a b : Frac} (h : a ≈ b) : a.render = b.render := by
  unfold render
  rw [reduce_eq_of_equiv h]

theorem reduce_integer (n : Int) : (integer n).reduce = integer n := by
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one (integer n))
  · simp [integer, Nat.gcd_one_right]
  · exact reduce_equiv (integer n)

-- Raw operational equivalences.

private theorem add_equiv_raw (a b : Frac) :
    (a.add b) ≈ ⟨a.num * (b.den : Int) + b.num * (a.den : Int), a.den * b.den,
      Nat.mul_pos a.positive b.positive⟩ :=
  reduce_equiv _

private theorem mul_equiv_raw (a b : Frac) :
    (a.mul b) ≈ ⟨a.num * b.num, a.den * b.den, Nat.mul_pos a.positive b.positive⟩ :=
  reduce_equiv _

-- Congruence lemmas.

theorem add_congr {a₁ a₂ b₁ b₂ : Frac} (ha : a₁ ≈ a₂) (hb : b₁ ≈ b₂) :
    a₁.add b₁ = a₂.add b₂ := by
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (add_equiv_raw a₁ b₁).trans
  apply Equiv.trans _ (add_equiv_raw a₂ b₂).symm
  unfold Equiv at ha hb ⊢
  dsimp only
  rw [Int.natCast_mul, Int.natCast_mul, Int.add_mul, Int.add_mul]
  have h1 : a₁.num * (b₁.den : Int) * ((a₂.den : Int) * (b₂.den : Int)) =
      a₂.num * (b₂.den : Int) * ((a₁.den : Int) * (b₁.den : Int)) := by
    calc
      a₁.num * (b₁.den : Int) * ((a₂.den : Int) * (b₂.den : Int))
        = (a₁.num * (a₂.den : Int)) * ((b₁.den : Int) * (b₂.den : Int)) := by
            rw [Int.mul_assoc, ← Int.mul_assoc (b₁.den : Int),
                Int.mul_comm (b₁.den : Int) (a₂.den : Int),
                Int.mul_assoc (a₂.den : Int), ← Int.mul_assoc]
      _ = (a₂.num * (a₁.den : Int)) * ((b₁.den : Int) * (b₂.den : Int)) := by rw [ha]
      _ = a₂.num * (b₂.den : Int) * ((a₁.den : Int) * (b₁.den : Int)) := by
            rw [Int.mul_assoc, ← Int.mul_assoc (a₁.den : Int),
                Int.mul_comm (a₁.den : Int) (b₁.den : Int),
                Int.mul_assoc (b₁.den : Int), Int.mul_comm (a₁.den : Int) (b₂.den : Int),
                ← Int.mul_assoc (b₁.den : Int), Int.mul_comm (b₁.den : Int) (b₂.den : Int),
                Int.mul_assoc (b₂.den : Int), ← Int.mul_assoc,
                Int.mul_comm (b₁.den : Int) (a₁.den : Int)]
  have h2 : b₁.num * (a₁.den : Int) * ((a₂.den : Int) * (b₂.den : Int)) =
      b₂.num * (a₂.den : Int) * ((a₁.den : Int) * (b₁.den : Int)) := by
    calc
      b₁.num * (a₁.den : Int) * ((a₂.den : Int) * (b₂.den : Int))
        = (b₁.num * (b₂.den : Int)) * ((a₁.den : Int) * (a₂.den : Int)) := by
            rw [Int.mul_assoc, Int.mul_comm (a₂.den : Int) (b₂.den : Int),
                ← Int.mul_assoc (a₁.den : Int), Int.mul_comm (a₁.den : Int) (b₂.den : Int),
                Int.mul_assoc (b₂.den : Int), ← Int.mul_assoc]
      _ = (b₂.num * (b₁.den : Int)) * ((a₁.den : Int) * (a₂.den : Int)) := by rw [hb]
      _ = b₂.num * (a₂.den : Int) * ((a₁.den : Int) * (b₁.den : Int)) := by
            rw [Int.mul_assoc, Int.mul_comm (a₁.den : Int) (a₂.den : Int),
                ← Int.mul_assoc (b₁.den : Int), Int.mul_comm (b₁.den : Int) (a₂.den : Int),
                Int.mul_assoc (a₂.den : Int), ← Int.mul_assoc,
                Int.mul_comm (b₁.den : Int) (a₁.den : Int)]
  rw [h1, h2]

theorem mul_congr {a₁ a₂ b₁ b₂ : Frac} (ha : a₁ ≈ a₂) (hb : b₁ ≈ b₂) :
    a₁.mul b₁ = a₂.mul b₂ := by
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (mul_equiv_raw a₁ b₁).trans
  apply Equiv.trans _ (mul_equiv_raw a₂ b₂).symm
  unfold Equiv at ha hb ⊢
  dsimp only
  rw [Int.natCast_mul, Int.natCast_mul]
  calc
    a₁.num * b₁.num * ((a₂.den : Int) * (b₂.den : Int))
      = (a₁.num * (a₂.den : Int)) * (b₁.num * (b₂.den : Int)) := by
          rw [Int.mul_assoc, ← Int.mul_assoc b₁.num, Int.mul_comm b₁.num (a₂.den : Int),
              Int.mul_assoc (a₂.den : Int), ← Int.mul_assoc]
    _ = (a₂.num * (a₁.den : Int)) * (b₂.num * (b₁.den : Int)) := by rw [ha, hb]
    _ = a₂.num * b₂.num * ((a₁.den : Int) * (b₁.den : Int)) := by
          rw [Int.mul_assoc, ← Int.mul_assoc (a₁.den : Int), Int.mul_comm (a₁.den : Int) b₂.num,
              Int.mul_assoc b₂.num, ← Int.mul_assoc]

theorem equiv_zero_iff (a : Frac) : a ≈ integer 0 ↔ a.num = 0 := by
  simp [Equiv, integer]

theorem inv_zero : (integer 0).inv = integer 0 := rfl

theorem inv_of_num_eq_zero {a : Frac} (h : a.num = 0) : a.inv = integer 0 := by
  unfold inv
  rw [h]

theorem inv_congr {a b : Frac} (h : a ≈ b) : a.inv = b.inv := by
  by_cases ha : a.num = 0
  · have hb : b.num = 0 := by
      have h' := h
      unfold Equiv at h'
      rw [ha, Int.zero_mul] at h'
      have hpos : (a.den : Int) ≠ 0 := by have := a.positive; omega
      exact (Int.mul_eq_zero.mp h'.symm).resolve_right hpos
    rw [inv_of_num_eq_zero ha, inv_of_num_eq_zero hb]
  · have hb : b.num ≠ 0 := by
      intro hb0
      have h' := h
      unfold Equiv at h'
      rw [hb0, Int.zero_mul] at h'
      have hpos : (b.den : Int) ≠ 0 := by have := b.positive; omega
      exact ha ((Int.mul_eq_zero.mp h').resolve_right hpos)
    have hinv_equiv : a.inv ≈ b.inv := by
      have aux : ∀ x : Frac, x.num ≠ 0 →
          x.inv.num * x.num = (x.den : Int) * (x.inv.den : Int) := by
        intro x hx
        cases hn : x.num with
        | ofNat m =>
          cases m with
          | zero => exact absurd hn hx
          | succ k =>
            have hred : x.inv ≈ ⟨(x.den : Int), k + 1, Nat.zero_lt_succ k⟩ := by
              unfold inv; rw [hn]; exact reduce_equiv _
            unfold Equiv at hred
            simpa [Int.mul_comm] using hred
        | negSucc k =>
          have hred : x.inv ≈ ⟨-(x.den : Int), k + 1, Nat.zero_lt_succ k⟩ := by
            unfold inv; rw [hn]; exact reduce_equiv _
          unfold Equiv at hred
          have hneg : Int.negSucc k = -((k + 1 : Nat) : Int) := rfl
          rw [hneg, Int.mul_neg, hred]
          simp [Int.neg_mul, Int.mul_comm]
      have hxa := aux a ha
      have hxb := aux b hb
      unfold Equiv at h ⊢
      have hprod_ne : a.num * b.num ≠ 0 := Int.mul_ne_zero ha hb
      apply Int.eq_of_mul_eq_mul_right hprod_ne
      calc
        a.inv.num * (b.inv.den : Int) * (a.num * b.num)
          = (a.inv.num * a.num) * ((b.inv.den : Int) * b.num) := by
              rw [Int.mul_assoc, ← Int.mul_assoc (b.inv.den : Int),
                  Int.mul_comm (b.inv.den : Int) a.num, Int.mul_assoc a.num, ← Int.mul_assoc]
        _ = ((a.den : Int) * (a.inv.den : Int)) * ((b.inv.den : Int) * b.num) := by rw [hxa]
        _ = (b.num * (a.den : Int)) * ((a.inv.den : Int) * (b.inv.den : Int)) := by
              rw [Int.mul_assoc, Int.mul_comm (b.inv.den : Int) b.num,
                  ← Int.mul_assoc (a.inv.den : Int), Int.mul_comm (a.inv.den : Int) b.num,
                  Int.mul_assoc b.num, ← Int.mul_assoc, Int.mul_comm (a.den : Int) b.num]
        _ = (a.num * (b.den : Int)) * ((a.inv.den : Int) * (b.inv.den : Int)) := by rw [← h]
        _ = ((b.den : Int) * (b.inv.den : Int)) * ((a.inv.den : Int) * a.num) := by
              rw [Int.mul_comm a.num (b.den : Int), Int.mul_assoc (b.den : Int),
                  Int.mul_comm (a.inv.den : Int) (b.inv.den : Int),
                  ← Int.mul_assoc a.num, Int.mul_comm a.num (b.inv.den : Int),
                  Int.mul_assoc (b.inv.den : Int), ← Int.mul_assoc,
                  Int.mul_comm a.num (a.inv.den : Int)]
        _ = (b.inv.num * b.num) * ((a.inv.den : Int) * a.num) := by rw [← hxb]
        _ = b.inv.num * (a.inv.den : Int) * (a.num * b.num) := by
              rw [Int.mul_assoc, ← Int.mul_assoc b.num, Int.mul_comm b.num (a.inv.den : Int),
                  Int.mul_assoc (a.inv.den : Int), ← Int.mul_assoc, Int.mul_comm b.num a.num]
    have hcop : ∀ x : Frac, x.num ≠ 0 → x.inv.num.natAbs.gcd x.inv.den = 1 := by
      intro x hx
      cases hn : x.num with
      | ofNat m =>
        cases m with
        | zero => exact absurd hn hx
        | succ k => unfold inv; rw [hn]; exact reduce_gcd_one _
      | negSucc k => unfold inv; rw [hn]; exact reduce_gcd_one _
    exact eq_of_equiv_of_gcd_one (hcop a ha) (hcop b hb) hinv_equiv

-- Algebraic laws (holding with literal equality on reduced outputs!).

theorem add_comm (a b : Frac) : a.add b = b.add a := by
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (add_equiv_raw a b).trans
  apply Equiv.trans _ (add_equiv_raw b a).symm
  unfold Equiv
  dsimp only
  rw [Int.add_comm, Nat.mul_comm]

theorem add_assoc (a b c : Frac) : (a.add b).add c = a.add (b.add c) := by
  have hab := add_equiv_raw a b
  have hbc := add_equiv_raw b c
  have h1 : (a.add b).add c =
      (Frac.mk (a.num * (b.den : Int) + b.num * (a.den : Int)) (a.den * b.den)
        (Nat.mul_pos a.positive b.positive)).add c :=
    add_congr hab (Equiv.refl c)
  have h2 : a.add (b.add c) =
      a.add (Frac.mk (b.num * (c.den : Int) + c.num * (b.den : Int)) (b.den * c.den)
        (Nat.mul_pos b.positive c.positive)) :=
    add_congr (Equiv.refl a) hbc
  rw [h1, h2]
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (add_equiv_raw _ _).trans
  apply Equiv.trans _ (add_equiv_raw _ _).symm
  unfold Equiv
  dsimp only
  simp only [Int.natCast_mul, Int.add_mul, Int.mul_add, Int.mul_assoc, Int.add_assoc]
  have hd : ((a.den : Int) * ((b.den : Int) * (c.den : Int))) =
      ((a.den : Int) * (b.den : Int)) * (c.den : Int) := (Int.mul_assoc _ _ _).symm
  have t1 : (b.den : Int) * ((c.den : Int) * ((a.den : Int) * ((b.den : Int) * (c.den : Int)))) =
      (b.den : Int) * ((c.den : Int) * ((a.den : Int) * ((b.den : Int) * (c.den : Int)))) := rfl
  have t2 : (a.den : Int) * ((c.den : Int) * ((a.den : Int) * ((b.den : Int) * (c.den : Int)))) =
      (c.den : Int) * ((a.den : Int) * ((a.den : Int) * ((b.den : Int) * (c.den : Int)))) := by
    rw [← Int.mul_assoc (a.den : Int) (c.den : Int), Int.mul_comm (a.den : Int) (c.den : Int),
        Int.mul_assoc]
  have t3 : (a.den : Int) * ((b.den : Int) * ((a.den : Int) * ((b.den : Int) * (c.den : Int)))) =
      (b.den : Int) * ((a.den : Int) * ((a.den : Int) * ((b.den : Int) * (c.den : Int)))) := by
    rw [← Int.mul_assoc (a.den : Int) (b.den : Int), Int.mul_comm (a.den : Int) (b.den : Int),
        Int.mul_assoc]
  rw [t2, t3]

theorem add_zero (a : Frac) : a.add (integer 0) = a.reduce := by
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (add_equiv_raw a (integer 0)).trans
  apply Equiv.trans _ (reduce_equiv a).symm
  simp [Equiv, integer]

theorem zero_add (a : Frac) : (integer 0).add a = a.reduce := by
  rw [add_comm, add_zero]

theorem mul_comm (a b : Frac) : a.mul b = b.mul a := by
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (mul_equiv_raw a b).trans
  apply Equiv.trans _ (mul_equiv_raw b a).symm
  unfold Equiv
  dsimp only
  rw [Int.mul_comm a.num b.num, Nat.mul_comm a.den b.den]

theorem mul_assoc (a b c : Frac) : (a.mul b).mul c = a.mul (b.mul c) := by
  have h1 : (a.mul b).mul c =
      (Frac.mk (a.num * b.num) (a.den * b.den) (Nat.mul_pos a.positive b.positive)).mul c :=
    mul_congr (mul_equiv_raw a b) (Equiv.refl c)
  have h2 : a.mul (b.mul c) =
      a.mul (Frac.mk (b.num * c.num) (b.den * c.den) (Nat.mul_pos b.positive c.positive)) :=
    mul_congr (Equiv.refl a) (mul_equiv_raw b c)
  rw [h1, h2]
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (mul_equiv_raw _ _).trans
  apply Equiv.trans _ (mul_equiv_raw _ _).symm
  unfold Equiv
  dsimp only
  simp only [Int.natCast_mul, Int.mul_assoc]

theorem mul_one (a : Frac) : a.mul (integer 1) = a.reduce := by
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (mul_equiv_raw a (integer 1)).trans
  apply Equiv.trans _ (reduce_equiv a).symm
  simp [Equiv, integer]

theorem one_mul (a : Frac) : (integer 1).mul a = a.reduce := by
  rw [mul_comm, mul_one]

theorem mul_zero (a : Frac) : a.mul (integer 0) = integer 0 := by
  rw [← reduce_integer 0]
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (mul_equiv_raw a (integer 0)).trans
  apply Equiv.trans _ (reduce_equiv (integer 0)).symm
  simp [Equiv, integer]

theorem zero_mul (a : Frac) : (integer 0).mul a = integer 0 := by
  rw [mul_comm, mul_zero]

theorem mul_of_left_zero {a b : Frac} (h : a.num = 0) : a.mul b = integer 0 := by
  have ha : a ≈ integer 0 := (equiv_zero_iff a).mpr h
  rw [mul_congr ha (Equiv.refl b), zero_mul]

theorem mul_of_right_zero {a b : Frac} (h : b.num = 0) : a.mul b = integer 0 := by
  rw [mul_comm, mul_of_left_zero h]

private theorem int_mul_4_comm (x y z w : Int) : x * (y * (z * w)) = y * (x * (z * w)) := by
  rw [← Int.mul_assoc x y, Int.mul_comm x y, Int.mul_assoc]

theorem left_distrib (a b c : Frac) : a.mul (b.add c) = (a.mul b).add (a.mul c) := by
  have h1 : a.mul (b.add c) =
      a.mul (Frac.mk (b.num * (c.den : Int) + c.num * (b.den : Int)) (b.den * c.den)
        (Nat.mul_pos b.positive c.positive)) :=
    mul_congr (Equiv.refl a) (add_equiv_raw b c)
  have h2 : (a.mul b).add (a.mul c) =
      (Frac.mk (a.num * b.num) (a.den * b.den) (Nat.mul_pos a.positive b.positive)).add
        (Frac.mk (a.num * c.num) (a.den * c.den) (Nat.mul_pos a.positive c.positive)) :=
    add_congr (mul_equiv_raw a b) (mul_equiv_raw a c)
  rw [h1, h2]
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (mul_equiv_raw _ _).trans
  apply Equiv.trans _ (add_equiv_raw _ _).symm
  unfold Equiv
  dsimp only
  simp only [Int.natCast_mul, Int.mul_add, Int.add_mul, Int.mul_assoc]
  have s1 : (c.den : Int) * ((a.den : Int) * ((b.den : Int) * ((a.den : Int) * (c.den : Int)))) =
      (a.den : Int) * ((c.den : Int) * ((a.den : Int) * ((b.den : Int) * (c.den : Int)))) := by
    rw [int_mul_4_comm (c.den : Int) (a.den : Int)]
    congr 1; congr 1
    rw [← Int.mul_assoc (b.den : Int) (a.den : Int), Int.mul_comm (b.den : Int) (a.den : Int),
        Int.mul_assoc]
  have s2 : (b.den : Int) * ((a.den : Int) * ((b.den : Int) * ((a.den : Int) * (c.den : Int)))) =
      (a.den : Int) * ((b.den : Int) * ((a.den : Int) * ((b.den : Int) * (c.den : Int)))) := by
    rw [int_mul_4_comm (b.den : Int) (a.den : Int)]
    congr 1
    rw [int_mul_4_comm (b.den : Int) (b.den : Int)]
    congr 1
    rw [← Int.mul_assoc (b.den : Int) (a.den : Int), Int.mul_comm (b.den : Int) (a.den : Int),
        Int.mul_assoc]
  rw [s1, s2]

theorem inv_mul_cancel {a : Frac} (h : a.num ≠ 0) : a.inv.mul a = integer 1 := by
  cases hn : a.num with
  | ofNat m =>
    cases m with
    | zero => exact absurd hn h
    | succ k =>
      have h1 : a.inv.mul a =
          (Frac.mk (a.den : Int) (k + 1) (Nat.zero_lt_succ k)).mul a := by
        apply mul_congr _ (Equiv.refl a)
        unfold inv; rw [hn]; exact reduce_equiv _
      rw [h1, ← reduce_integer 1]
      apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
      apply (mul_equiv_raw _ _).trans
      apply Equiv.trans _ (reduce_equiv (integer 1)).symm
      unfold Equiv integer
      dsimp only
      rw [hn]
      simp [Int.natCast_mul, Int.mul_comm]
  | negSucc k =>
    have h1 : a.inv.mul a =
        (Frac.mk (-(a.den : Int)) (k + 1) (Nat.zero_lt_succ k)).mul a := by
      apply mul_congr _ (Equiv.refl a)
      unfold inv; rw [hn]; exact reduce_equiv _
    rw [h1, ← reduce_integer 1]
    apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
    apply (mul_equiv_raw _ _).trans
    apply Equiv.trans _ (reduce_equiv (integer 1)).symm
    unfold Equiv integer
    dsimp only
    rw [hn]
    have hneg : Int.negSucc k = -((k + 1 : Nat) : Int) := rfl
    rw [hneg]
    simp [Int.natCast_mul, Int.neg_mul, Int.mul_neg, Int.mul_comm]

-- Properties of `sum` (equivalence with `foldr`, linearity, permutation invariance).

theorem reduce_foldr_add (xs : List Frac) :
    (xs.foldr add (integer 0)).reduce = xs.foldr add (integer 0) := by
  cases xs with
  | nil => exact reduce_integer 0
  | cons x rest => exact reduce_idem _

private theorem sumPairs_foldr : ∀ xs : List Frac,
    (sumPairs xs).foldr add (integer 0) = xs.foldr add (integer 0)
  | [] => rfl
  | [_] => rfl
  | x :: y :: rest => by
    simp only [sumPairs, List.foldr_cons]
    rw [sumPairs_foldr rest, add_assoc]

private theorem sumFuel_eq_foldr : ∀ (fuel : Nat) (xs : List Frac),
    sumFuel fuel xs = xs.foldr add (integer 0)
  | 0, _ => rfl
  | _ + 1, [] => rfl
  | _ + 1, [x] => by
    simp only [sumFuel, List.foldr_cons, List.foldr_nil, add_zero]
  | fuel + 1, x :: y :: rest => by
    simp only [sumFuel]
    rw [sumFuel_eq_foldr fuel (add x y :: sumPairs rest)]
    simp only [List.foldr_cons]
    rw [sumPairs_foldr rest, add_assoc]

theorem sum_eq_foldr (values : List Frac) :
    sum values = values.foldr add (integer 0) :=
  sumFuel_eq_foldr values.length values

theorem sum_nil : sum [] = integer 0 := rfl

theorem sum_cons (x : Frac) (xs : List Frac) : sum (x :: xs) = x.add (sum xs) := by
  rw [sum_eq_foldr, sum_eq_foldr, List.foldr_cons]

theorem sum_append (xs ys : List Frac) : sum (xs ++ ys) = (sum xs).add (sum ys) := by
  induction xs with
  | nil =>
    rw [List.nil_append, sum_nil, zero_add, sum_eq_foldr, reduce_foldr_add]
  | cons x xs ih =>
    rw [List.cons_append, sum_cons, sum_cons, ih, add_assoc]

theorem sum_perm {xs ys : List Frac} (h : xs.Perm ys) : sum xs = sum ys := by
  induction h with
  | nil => rfl
  | cons x _ ih => rw [sum_cons, sum_cons, ih]
  | swap x y zs =>
    rw [sum_cons, sum_cons, sum_cons, sum_cons, ← add_assoc, add_comm y x, add_assoc]
  | trans _ _ ih₁ ih₂ => exact ih₁.trans ih₂

theorem mul_sum (c : Frac) (xs : List Frac) :
    c.mul (sum xs) = sum (xs.map (c.mul ·)) := by
  induction xs with
  | nil => simp [sum_nil, mul_zero]
  | cons x xs ih =>
    rw [List.map_cons, sum_cons, sum_cons, left_distrib, ih]

-- Order / sign properties needed for the mass-stopping theorem.

theorem num_nonneg_of_equiv {a b : Frac} (h : a ≈ b) (ha : 0 ≤ a.num) : 0 ≤ b.num := by
  unfold Equiv at h
  have hposa : (0 : Int) < (a.den : Int) := positiveIntCast a.positive
  have hposb : (0 : Int) < (b.den : Int) := positiveIntCast b.positive
  have hmul : 0 ≤ b.num * (a.den : Int) := by
    rw [← h]
    exact Int.mul_nonneg ha (Int.le_of_lt hposb)
  apply Decidable.byContradiction
  intro hlt
  have hneg : b.num < 0 := by omega
  have : b.num * (a.den : Int) < 0 := Int.mul_neg_of_neg_of_pos hneg hposa
  omega

theorem num_pos_of_equiv {a b : Frac} (h : a ≈ b) (ha : 0 < a.num) : 0 < b.num := by
  unfold Equiv at h
  have hposa : (0 : Int) < (a.den : Int) := positiveIntCast a.positive
  have hposb : (0 : Int) < (b.den : Int) := positiveIntCast b.positive
  have hmul : 0 < b.num * (a.den : Int) := by
    rw [← h]
    exact Int.mul_pos ha hposb
  apply Decidable.byContradiction
  intro hle
  have hnonpos : b.num ≤ 0 := by omega
  have : b.num * (a.den : Int) ≤ 0 := Int.mul_nonpos_of_nonpos_of_nonneg hnonpos (Int.le_of_lt hposa)
  omega

theorem add_num_nonneg {a b : Frac} (ha : 0 ≤ a.num) (hb : 0 ≤ b.num) : 0 ≤ (a.add b).num := by
  apply num_nonneg_of_equiv (add_equiv_raw a b).symm
  dsimp only
  have hposa : (0 : Int) ≤ (a.den : Int) := Int.ofNat_nonneg a.den
  have hposb : (0 : Int) ≤ (b.den : Int) := Int.ofNat_nonneg b.den
  exact Int.add_nonneg (Int.mul_nonneg ha hposb) (Int.mul_nonneg hb hposa)

theorem add_num_pos_of_pos_nonneg {a b : Frac} (ha : 0 < a.num) (hb : 0 ≤ b.num) :
    0 < (a.add b).num := by
  apply num_pos_of_equiv (add_equiv_raw a b).symm
  dsimp only
  have hposa : (0 : Int) ≤ (a.den : Int) := Int.ofNat_nonneg a.den
  have hposb : (0 : Int) < (b.den : Int) := positiveIntCast b.positive
  have h1 : 0 < a.num * (b.den : Int) := Int.mul_pos ha hposb
  have h2 : 0 ≤ b.num * (a.den : Int) := Int.mul_nonneg hb hposa
  omega

theorem lt_add_of_pos {a b : Frac} (hb : 0 < b.num) : a < a.add b := by
  change a.num * ((a.add b).den : Int) < (a.add b).num * (a.den : Int)
  have hraw := add_equiv_raw a b
  unfold Equiv at hraw
  dsimp only at hraw
  have hpos_ab : (0 : Int) < ((a.den * b.den : Nat) : Int) :=
    positiveIntCast (Nat.mul_pos a.positive b.positive)
  have hpos_den : (0 : Int) < ((a.add b).den : Int) := positiveIntCast (a.add b).positive
  have hstrict : a.num * ((a.den * b.den : Nat) : Int) <
      (a.num * (b.den : Int) + b.num * (a.den : Int)) * (a.den : Int) := by
    rw [Int.natCast_mul, Int.add_mul]
    have ha_eq : a.num * ((a.den : Int) * (b.den : Int)) = a.num * (b.den : Int) * (a.den : Int) := by
      rw [Int.mul_comm (a.den : Int) (b.den : Int), ← Int.mul_assoc]
    have hpos_a : (0 : Int) < (a.den : Int) := positiveIntCast a.positive
    have hterm : 0 < b.num * (a.den : Int) * (a.den : Int) :=
      Int.mul_pos (Int.mul_pos hb hpos_a) hpos_a
    omega
  have hmul : a.num * ((a.add b).den : Int) * ((a.den * b.den : Nat) : Int) <
      (a.add b).num * (a.den : Int) * ((a.den * b.den : Nat) : Int) := by
    calc
      a.num * ((a.add b).den : Int) * ((a.den * b.den : Nat) : Int)
        = (a.num * ((a.den * b.den : Nat) : Int)) * ((a.add b).den : Int) := by
            rw [Int.mul_assoc, Int.mul_comm ((a.add b).den : Int), ← Int.mul_assoc]
      _ < ((a.num * (b.den : Int) + b.num * (a.den : Int)) * (a.den : Int)) * ((a.add b).den : Int) :=
            Int.mul_lt_mul_of_pos_right hstrict hpos_den
      _ = ((a.num * (b.den : Int) + b.num * (a.den : Int)) * ((a.add b).den : Int)) * (a.den : Int) := by
            rw [Int.mul_assoc, Int.mul_comm (a.den : Int) ((a.add b).den : Int), ← Int.mul_assoc]
      _ = ((a.add b).num * ((a.den * b.den : Nat) : Int)) * (a.den : Int) := by rw [← hraw]
      _ = (a.add b).num * (a.den : Int) * ((a.den * b.den : Nat) : Int) := by
            rw [Int.mul_assoc, Int.mul_comm ((a.den * b.den : Nat) : Int) (a.den : Int), ← Int.mul_assoc]
  apply Decidable.byContradiction
  intro hle
  have hge : (a.add b).num * (a.den : Int) ≤ a.num * ((a.add b).den : Int) := by omega
  have : (a.add b).num * (a.den : Int) * ((a.den * b.den : Nat) : Int) ≤
      a.num * ((a.add b).den : Int) * ((a.den * b.den : Nat) : Int) :=
    Int.mul_le_mul_of_nonneg_right hge (Int.le_of_lt hpos_ab)
  omega

theorem not_equiv_of_lt {a b : Frac} (h : a < b) : ¬ (a ≈ b) := by
  intro heq
  change a.num * (b.den : Int) < b.num * (a.den : Int) at h
  unfold Equiv at heq
  omega

theorem reciprocalNat_zero : reciprocalNat 0 = integer 0 := rfl

theorem reciprocalNat_succ (n : Nat) :
    reciprocalNat (n + 1) = ⟨1, n + 1, Nat.zero_lt_succ n⟩ := by
  unfold reciprocalNat integer inv reduce
  simp [Nat.gcd_one_left]

theorem reciprocalNat_num_nonneg (n : Nat) : 0 ≤ (reciprocalNat n).num := by
  cases n with
  | zero => simp [reciprocalNat_zero, integer]
  | succ k => simp [reciprocalNat_succ]

theorem reciprocalNat_num_pos {n : Nat} (h : 0 < n) : 0 < (reciprocalNat n).num := by
  cases n with
  | zero => omega
  | succ k => simp [reciprocalNat_succ]

theorem reciprocalNat_double (n : Nat) :
    reciprocalNat (2 * n) = (reciprocalNat 2).mul (reciprocalNat n) := by
  cases n with
  | zero =>
    simp [reciprocalNat_zero, mul_zero]
  | succ k =>
    have h2k : 2 * (k + 1) = (2 * k + 1) + 1 := by omega
    rw [h2k, reciprocalNat_succ, reciprocalNat_succ, reciprocalNat_succ]
    apply eq_of_equiv_of_gcd_one
    · simp [Nat.gcd_one_left]
    · exact reduce_gcd_one _
    · apply Equiv.trans _ (mul_equiv_raw _ _).symm
      unfold Equiv
      dsimp only
      have : (2 * k + 1) + 1 = 2 * (k + 1) := by omega
      rw [this]
      simp [Int.natCast_mul]

end Frac

/-- Sum reciprocal stabilizer orders. -/
def classMass (orders : List Nat) : Frac := Frac.sum (orders.map Frac.reciprocalNat)

/-- Handle bases zero and one without constructing a potentially huge power. -/
private def normalizationPower (q exponent : Nat) : Nat :=
  match q with
  | 0 => if exponent = 0 then 1 else 0
  | 1 => 1
  | q + 2 => (q + 2) ^ exponent

private theorem normalizationPower_eq (q exponent : Nat) :
    normalizationPower q exponent = q ^ exponent := by
  cases q with
  | zero => cases exponent <;> simp [normalizationPower]
  | succ q => cases q <;> simp [normalizationPower]

/-- Sum the samples and scale by the inverses of `u` and `q^(k * (rank / 2))`.
Short-circuits when `u = 0`, `q = 0` with positive exponent, or the sample sum is zero. -/
def hecke (u : Frac) (q k rank : Nat) (values : List Frac) : Frac :=
  if u.num == 0 then
    Frac.integer 0
  else
    let exp := k * (rank / 2)
    if q == 0 && exp != 0 then
      Frac.integer 0
    else
      let total := Frac.sum values
      if total.num == 0 then
        Frac.integer 0
      else
        (u.inv.mul (Frac.reciprocalNat (normalizationPower q exp))).mul total

-- Class mass theorems.

@[simp] theorem classMass_nil : classMass [] = Frac.integer 0 := rfl

theorem classMass_cons (n : Nat) (ns : List Nat) :
    classMass (n :: ns) = (Frac.reciprocalNat n).add (classMass ns) := by
  simp only [classMass, List.map_cons, Frac.sum_cons]

theorem classMass_append (xs ys : List Nat) :
    classMass (xs ++ ys) = (classMass xs).add (classMass ys) := by
  simp only [classMass, List.map_append, Frac.sum_append]

theorem classMass_zero_cons (ns : List Nat) :
    classMass (0 :: ns) = classMass ns := by
  rw [classMass_cons, Frac.reciprocalNat_zero, Frac.zero_add]
  simp only [classMass, Frac.sum_eq_foldr, Frac.reduce_foldr_add]

theorem classMass_perm {xs ys : List Nat} (h : xs.Perm ys) :
    classMass xs = classMass ys :=
  Frac.sum_perm (h.map Frac.reciprocalNat)

theorem classMass_nonneg (orders : List Nat) : 0 ≤ (classMass orders).num := by
  induction orders with
  | nil => simp [classMass_nil, Frac.integer]
  | cons n ns ih =>
    rw [classMass_cons]
    exact Frac.add_num_nonneg (Frac.reciprocalNat_num_nonneg n) ih

theorem classMass_pos_of_mem_pos {orders : List Nat} {d : Nat}
    (hmem : d ∈ orders) (hpos : 0 < d) : 0 < (classMass orders).num := by
  induction orders with
  | nil => cases hmem
  | cons n ns ih =>
    rw [classMass_cons]
    cases hmem with
    | head =>
      exact Frac.add_num_pos_of_pos_nonneg (Frac.reciprocalNat_num_pos hpos) (classMass_nonneg ns)
    | tail _ hmem' =>
      rw [Frac.add_comm]
      exact Frac.add_num_pos_of_pos_nonneg (ih hmem') (Frac.reciprocalNat_num_nonneg n)

/-- Mass-stopping inequality: any omitted class with positive stabilizer order strictly
increases the total mass. -/
theorem classMass_lt_append_of_pos {found extra : List Nat} {d : Nat}
    (hmem : d ∈ extra) (hpos : 0 < d) :
    classMass found < classMass (found ++ extra) := by
  rw [classMass_append]
  exact Frac.lt_add_of_pos (classMass_pos_of_mem_pos hmem hpos)

/-- Mass-stopping completeness: if all omitted classes have positive stabilizer orders and
`found` already matches the total mass of `found ++ extra`, then `extra` is empty. -/
theorem classMass_complete_of_eq {found extra : List Nat}
    (hpos : ∀ d ∈ extra, 0 < d)
    (heq : classMass found ≈ classMass (found ++ extra)) : extra = [] := by
  cases extra with
  | nil => rfl
  | cons d rest =>
    exfalso
    have hmem : d ∈ d :: rest := List.mem_cons_self
    have hlt := classMass_lt_append_of_pos (found := found) hmem (hpos d hmem)
    exact Frac.not_equiv_of_lt hlt heq

/-- Full-versus-projective stabilizer scaling: doubling every stabilizer order halves the mass. -/
theorem classMass_double_orders (orders : List Nat) :
    classMass (orders.map (2 * ·)) = (Frac.reciprocalNat 2).mul (classMass orders) := by
  unfold classMass
  rw [Frac.mul_sum, List.map_map, List.map_map]
  congr 1
  apply List.map_congr_left
  intro n _
  exact Frac.reciprocalNat_double n

-- Hecke theorems (including proof of equivalence for short-circuiting and linearity).

theorem hecke_formula (u : Frac) (q k rank : Nat) (values : List Frac) :
    hecke u q k rank values =
      (u.inv.mul (Frac.reciprocalNat (q ^ (k * (rank / 2))))).mul
        (values.foldr Frac.add (Frac.integer 0)) := by
  unfold hecke
  by_cases hu : u.num = 0
  · simp [hu, Frac.inv_of_num_eq_zero hu, Frac.zero_mul]
  · simp only [hu, beq_iff_eq, ↓reduceIte]
    by_cases hq : q = 0 ∧ k * (rank / 2) ≠ 0
    · rcases hq with ⟨rfl, hexp⟩
      have hpow : (0 : Nat) ^ (k * (rank / 2)) = 0 := Nat.zero_pow (Nat.pos_of_ne_zero hexp)
      simp [hexp, hpow, Frac.reciprocalNat_zero, Frac.mul_zero, Frac.zero_mul]
    · have hcond : ¬ (q == 0 && k * (rank / 2) != 0) = true := by
        simp only [Bool.and_eq_true, beq_iff_eq, bne_iff_ne]
        exact hq
      simp only [hcond, Bool.false_eq_true, ↓reduceIte]
      by_cases hsum : (Frac.sum values).num = 0
      · simp only [hsum, beq_iff_eq, ↓reduceIte]
        rw [← Frac.sum_eq_foldr, Frac.mul_of_right_zero hsum]
      · simp only [hsum, beq_iff_eq, ↓reduceIte]
        rw [normalizationPower_eq, Frac.sum_eq_foldr]

theorem hecke_nil (u : Frac) (q k rank : Nat) :
    hecke u q k rank [] = Frac.integer 0 := by
  rw [hecke_formula, List.foldr_nil, Frac.mul_zero]

theorem hecke_u_zero {u : Frac} (hu : u.num = 0) (q k rank : Nat) (values : List Frac) :
    hecke u q k rank values = Frac.integer 0 := by
  simp [hecke, hu]

theorem hecke_q_zero_of_exp_pos (u : Frac) {k rank : Nat} (hexp : 0 < k * (rank / 2))
    (values : List Frac) :
    hecke u 0 k rank values = Frac.integer 0 := by
  rw [hecke_formula, Nat.zero_pow hexp, Frac.reciprocalNat_zero, Frac.mul_zero, Frac.zero_mul]

theorem hecke_sum_zero (u : Frac) (q k rank : Nat) {values : List Frac}
    (hsum : (Frac.sum values).num = 0) :
    hecke u q k rank values = Frac.integer 0 := by
  rw [hecke_formula, ← Frac.sum_eq_foldr, Frac.mul_of_right_zero hsum]

theorem hecke_append (u : Frac) (q k rank : Nat) (xs ys : List Frac) :
    hecke u q k rank (xs ++ ys) = (hecke u q k rank xs).add (hecke u q k rank ys) := by
  rw [hecke_formula, hecke_formula, hecke_formula,
      ← Frac.sum_eq_foldr, ← Frac.sum_eq_foldr, ← Frac.sum_eq_foldr,
      Frac.sum_append, Frac.left_distrib]

theorem hecke_perm (u : Frac) (q k rank : Nat) {xs ys : List Frac} (h : xs.Perm ys) :
    hecke u q k rank xs = hecke u q k rank ys := by
  rw [hecke_formula, hecke_formula, ← Frac.sum_eq_foldr, ← Frac.sum_eq_foldr, Frac.sum_perm h]

-- Concrete exact evaluation theorems.

theorem mass_six : classMass [6] = ⟨1, 6, by decide⟩ := by decide

theorem mass_level_eleven : classMass [4, 6] = ⟨5, 12, by decide⟩ := by decide

theorem hecke_minus_two :
    hecke (Frac.integer (-1)) 3 1 3 [Frac.integer 2, Frac.integer 4] = Frac.integer (-2) := by
  decide

/-- Distinguishes `k * (rank / 2)` (= 4) from `(k * rank) / 2` (= 5) at odd rank 5, even k = 2. -/
theorem hecke_odd_rank_even_k :
    hecke (Frac.integer 1) 3 2 5 [Frac.integer 1] = ⟨1, 81, by decide⟩ := by
  decide

-- Audit primitives: orbit-stabilizer completeness, detailed balance, and matrix commutativity.

namespace Frac

theorem neg_equiv_neg {a b : Frac} (h : a ≈ b) : a.neg ≈ b.neg := by
  unfold Equiv neg at *
  dsimp only
  rw [Int.neg_mul, Int.neg_mul, h]

theorem sub_congr {a₁ a₂ b₁ b₂ : Frac} (ha : a₁ ≈ a₂) (hb : b₁ ≈ b₂) :
    a₁.sub b₁ = a₂.sub b₂ :=
  add_congr ha (neg_equiv_neg hb)

theorem sub_self (a : Frac) : a.sub a = integer 0 := by
  rw [← reduce_integer 0]
  unfold sub
  apply eq_of_equiv_of_gcd_one (reduce_gcd_one _) (reduce_gcd_one _)
  apply (add_equiv_raw a a.neg).trans
  apply Equiv.trans _ (reduce_equiv (integer 0)).symm
  unfold Equiv neg integer
  dsimp only
  rw [Int.neg_mul, Int.add_right_neg, Int.zero_mul, Int.zero_mul]

theorem equiv_of_sub_eq_zero {a b : Frac} (h : a.sub b = integer 0) : a ≈ b := by
  have hraw := add_equiv_raw a b.neg
  rw [show a.add b.neg = a.sub b from rfl, h] at hraw
  unfold Equiv at hraw ⊢
  dsimp only [integer, neg] at hraw
  rw [Int.zero_mul, Int.neg_mul] at hraw
  have h1 : (0 : Int) = a.num * (b.den : Int) + -(b.num * (a.den : Int)) := by
    simpa [Int.mul_one] using hraw
  omega

theorem sub_eq_zero_iff_equiv {a b : Frac} : a.sub b = integer 0 ↔ a ≈ b :=
  ⟨equiv_of_sub_eq_zero, fun h => by rw [sub_congr h (Equiv.refl b), sub_self]⟩

theorem lt_of_equiv_of_lt {a₁ a₂ b₁ b₂ : Frac}
    (ha : a₁ ≈ a₂) (hb : b₁ ≈ b₂) (hlt : a₂ < b₂) : a₁ < b₁ := by
  change a₁.num * (b₁.den : Int) < b₁.num * (a₁.den : Int)
  change a₂.num * (b₂.den : Int) < b₂.num * (a₂.den : Int) at hlt
  unfold Equiv at ha hb
  have hpos_a2 : (0 : Int) < (a₂.den : Int) := positiveIntCast a₂.positive
  have hpos_b2 : (0 : Int) < (b₂.den : Int) := positiveIntCast b₂.positive
  have hpos_a1 : (0 : Int) < (a₁.den : Int) := positiveIntCast a₁.positive
  have hpos_b1 : (0 : Int) < (b₁.den : Int) := positiveIntCast b₁.positive
  have hmul : (a₁.num * (b₁.den : Int)) * ((a₂.den : Int) * (b₂.den : Int)) <
      (b₁.num * (a₁.den : Int)) * ((a₂.den : Int) * (b₂.den : Int)) := by
    have lhs_eq : (a₁.num * (b₁.den : Int)) * ((a₂.den : Int) * (b₂.den : Int)) =
        (a₂.num * (b₂.den : Int)) * ((a₁.den : Int) * (b₁.den : Int)) := by
      calc
        (a₁.num * (b₁.den : Int)) * ((a₂.den : Int) * (b₂.den : Int))
          = (a₁.num * (a₂.den : Int)) * ((b₁.den : Int) * (b₂.den : Int)) := by
              rw [Int.mul_assoc, ← Int.mul_assoc (b₁.den : Int), Int.mul_comm (b₁.den : Int) (a₂.den : Int),
                  Int.mul_assoc (a₂.den : Int), ← Int.mul_assoc]
        _ = (a₂.num * (a₁.den : Int)) * ((b₁.den : Int) * (b₂.den : Int)) := by rw [ha]
        _ = (a₂.num * (b₂.den : Int)) * ((a₁.den : Int) * (b₁.den : Int)) := by
              rw [Int.mul_assoc, ← Int.mul_assoc (a₁.den : Int), Int.mul_comm (a₁.den : Int) (b₁.den : Int),
                  Int.mul_assoc (b₁.den : Int), Int.mul_comm (a₁.den : Int) (b₂.den : Int),
                  ← Int.mul_assoc (b₁.den : Int), Int.mul_comm (b₁.den : Int) (b₂.den : Int),
                  Int.mul_assoc (b₂.den : Int), ← Int.mul_assoc, Int.mul_comm (b₁.den : Int) (a₁.den : Int)]
    have rhs_eq : (b₁.num * (a₁.den : Int)) * ((a₂.den : Int) * (b₂.den : Int)) =
        (b₂.num * (a₂.den : Int)) * ((a₁.den : Int) * (b₁.den : Int)) := by
      calc
        (b₁.num * (a₁.den : Int)) * ((a₂.den : Int) * (b₂.den : Int))
          = (b₁.num * (b₂.den : Int)) * ((a₁.den : Int) * (a₂.den : Int)) := by
              rw [Int.mul_assoc, Int.mul_comm (a₂.den : Int) (b₂.den : Int),
                  ← Int.mul_assoc (a₁.den : Int), Int.mul_comm (a₁.den : Int) (b₂.den : Int),
                  Int.mul_assoc (b₂.den : Int), ← Int.mul_assoc]
        _ = (b₂.num * (b₁.den : Int)) * ((a₁.den : Int) * (a₂.den : Int)) := by rw [hb]
        _ = (b₂.num * (a₂.den : Int)) * ((a₁.den : Int) * (b₁.den : Int)) := by
              rw [Int.mul_assoc, Int.mul_comm (a₁.den : Int) (a₂.den : Int),
                  ← Int.mul_assoc (b₁.den : Int), Int.mul_comm (b₁.den : Int) (a₂.den : Int),
                  Int.mul_assoc (a₂.den : Int), ← Int.mul_assoc, Int.mul_comm (b₁.den : Int) (a₁.den : Int)]
    rw [lhs_eq, rhs_eq]
    exact Int.mul_lt_mul_of_pos_right hlt (Int.mul_pos hpos_a1 hpos_b1)
  apply Decidable.byContradiction
  intro hle
  have hge : b₁.num * (a₁.den : Int) ≤ a₁.num * (b₁.den : Int) := by omega
  have hge' := Int.mul_le_mul_of_nonneg_right hge (Int.le_of_lt (Int.mul_pos hpos_a2 hpos_b2))
  omega

end Frac

/-- Total labeled count covered by `orders` under a group of size `groupOrder`:
`|G| * classMass(orders)`. -/
def orbitCovered (groupOrder : Nat) (orders : List Nat) : Frac :=
  (Frac.integer groupOrder).mul (classMass orders)

/-- Exact rational deficit `expectedTotal - |G| * classMass(orders)`.
Zero iff the covered count matches `expectedTotal`. -/
def orbitDeficit (groupOrder : Nat) (orders : List Nat) (expectedTotal : Frac) : Frac :=
  expectedTotal.sub (orbitCovered groupOrder orders)

theorem orbitCovered_perm (groupOrder : Nat) {xs ys : List Nat} (h : xs.Perm ys) :
    orbitCovered groupOrder xs = orbitCovered groupOrder ys := by
  unfold orbitCovered
  rw [classMass_perm h]

theorem orbitDeficit_perm (groupOrder : Nat) {xs ys : List Nat} (h : xs.Perm ys)
    (expectedTotal : Frac) :
    orbitDeficit groupOrder xs expectedTotal = orbitDeficit groupOrder ys expectedTotal := by
  unfold orbitDeficit
  rw [orbitCovered_perm groupOrder h]

theorem orbitCovered_strict_lt_of_pos {groupOrder : Nat} (hg : 0 < groupOrder)
    {found extra : List Nat} {d : Nat} (hmem : d ∈ extra) (hpos : 0 < d) :
    orbitCovered groupOrder found < orbitCovered groupOrder (found ++ extra) := by
  unfold orbitCovered
  let raw1 : Frac := ⟨(groupOrder : Int) * (classMass found).num, (classMass found).den,
    (classMass found).positive⟩
  let raw2 : Frac := ⟨(groupOrder : Int) * (classMass (found ++ extra)).num,
    (classMass (found ++ extra)).den, (classMass (found ++ extra)).positive⟩
  have h1 : (Frac.integer groupOrder).mul (classMass found) ≈ raw1 := by
    have := Frac.reduce_equiv ⟨(Frac.integer groupOrder).num * (classMass found).num,
      (Frac.integer groupOrder).den * (classMass found).den,
      Nat.mul_pos (Frac.integer groupOrder).positive (classMass found).positive⟩
    simpa [Frac.mul, Frac.integer, raw1] using this
  have h2 : (Frac.integer groupOrder).mul (classMass (found ++ extra)) ≈ raw2 := by
    have := Frac.reduce_equiv ⟨(Frac.integer groupOrder).num * (classMass (found ++ extra)).num,
      (Frac.integer groupOrder).den * (classMass (found ++ extra)).den,
      Nat.mul_pos (Frac.integer groupOrder).positive (classMass (found ++ extra)).positive⟩
    simpa [Frac.mul, Frac.integer, raw2] using this
  apply Frac.lt_of_equiv_of_lt h1 h2
  change raw1.num * (raw2.den : Int) < raw2.num * (raw1.den : Int)
  dsimp only [raw1, raw2]
  have hlt := classMass_lt_append_of_pos (found := found) hmem hpos
  change (classMass found).num * ((classMass (found ++ extra)).den : Int) <
    (classMass (found ++ extra)).num * ((classMass found).den : Int) at hlt
  rw [Int.mul_assoc, Int.mul_assoc]
  exact Int.mul_lt_mul_of_pos_left hlt (positiveIntCast hg)

/-- Orbit-stabilizer completeness: if `0 < groupOrder`, every omitted orbit has positive
stabilizer order, and `orbitDeficit` vanishes against the full total, then `extra` is empty. -/
theorem orbitComplete_of_eq {groupOrder : Nat} (hg : 0 < groupOrder)
    {found extra : List Nat} (hpos : ∀ d ∈ extra, 0 < d)
    (heq : orbitDeficit groupOrder found (orbitCovered groupOrder (found ++ extra)) = Frac.integer 0) :
    extra = [] := by
  unfold orbitDeficit at heq
  rw [Frac.sub_eq_zero_iff_equiv] at heq
  cases extra with
  | nil => rfl
  | cons d rest =>
    exfalso
    have hmem : d ∈ d :: rest := List.mem_cons_self
    have hlt := orbitCovered_strict_lt_of_pos hg (found := found) hmem (hpos d hmem)
    exact Frac.not_equiv_of_lt hlt heq.symm

inductive OrbitStatus where
  | complete
  | missing (amount : Frac)
  | excess (amount : Frac)
  deriving DecidableEq

structure OrbitAudit where
  covered : Frac
  deficit : Frac
  deriving DecidableEq

/-- The status carries the positive magnitude when the signed deficit is nonzero. -/
def OrbitAudit.status (audit : OrbitAudit) : OrbitStatus :=
  if audit.deficit.num = 0 then .complete
  else if 0 < audit.deficit.num then .missing audit.deficit
  else .excess audit.deficit.neg

/-- Audit positive stabilizer orders against a nonnegative target. A positive
order need not divide the group order, so the deficit can expose fractional coverage. -/
def orbitCompleteness (groupOrder : Nat) (orders : List Nat) (expectedTotal : Frac) :
    Option OrbitAudit :=
  if 0 < groupOrder ∧ (∀ d ∈ orders, 0 < d) ∧ 0 ≤ expectedTotal.num then
    let covered := orbitCovered groupOrder orders
    some ⟨covered, expectedTotal.sub covered⟩
  else none

theorem OrbitAudit.status_complete_iff (audit : OrbitAudit) :
    audit.status = .complete ↔ audit.deficit.num = 0 := by
  unfold status
  split <;> rename_i h
  · simp [h]
  · split <;> simp [h]

theorem orbitCompleteness_eq_some_iff {groupOrder : Nat} {orders : List Nat}
    {expectedTotal : Frac} {audit : OrbitAudit} :
    orbitCompleteness groupOrder orders expectedTotal = some audit ↔
      (0 < groupOrder ∧ (∀ d ∈ orders, 0 < d) ∧ 0 ≤ expectedTotal.num) ∧
        audit = ⟨orbitCovered groupOrder orders, orbitDeficit groupOrder orders expectedTotal⟩ := by
  unfold orbitCompleteness orbitDeficit
  split <;> rename_i h
  · constructor
    · intro heq
      exact ⟨h, (Option.some.inj heq).symm⟩
    · rintro ⟨_, rfl⟩
      rfl
  · simp [h]

/-- A complete audit against the total of a list extended by positive orders
implies the extension was empty. This uses the strict mass-stopping theorem. -/
theorem orbitCompleteness_complete_of_extension {groupOrder : Nat} {found extra : List Nat}
    {audit : OrbitAudit} (hpos : ∀ d ∈ extra, 0 < d)
    (haudit : orbitCompleteness groupOrder found (orbitCovered groupOrder (found ++ extra)) =
      some audit) (hcomplete : audit.status = .complete) : extra = [] := by
  obtain ⟨⟨hg, _, _⟩, rfl⟩ := orbitCompleteness_eq_some_iff.mp haudit
  have hnum := (OrbitAudit.status_complete_iff _).mp hcomplete
  have hzero := Frac.reduce_eq_of_equiv ((Frac.equiv_zero_iff _).mpr hnum)
  rw [Frac.reduce_integer] at hzero
  exact orbitComplete_of_eq hg hpos (by
    unfold orbitDeficit Frac.sub Frac.add at hzero ⊢
    rw [Frac.reduce_idem] at hzero
    exact hzero)

/-- Check weighted detailed balance `d_j * B[i][j] = d_i * B[j][i]` for positive `orders`. -/
def detailedBalance (orders : List Nat) (matrix : List (List Frac)) : Bool :=
  let n := orders.length
  matrix.length == n &&
  orders.all (· > 0) &&
  matrix.all (fun row => row.length == n) &&
  (List.range n).all fun i =>
    let rowI := matrix.getD i []
    let dI := Frac.integer (orders.getD i 0)
    (List.range n).all fun j =>
      let rowJ := matrix.getD j []
      let dJ := Frac.integer (orders.getD j 0)
      let bij := rowI.getD j (Frac.integer 0)
      let bji := rowJ.getD i (Frac.integer 0)
      dJ.mul bij == dI.mul bji

/-- Exact rational matrix multiplication `A * B`. -/
def matMul (a b : List (List Frac)) : List (List Frac) :=
  let cols := (List.range b.length).map fun j =>
    b.map fun row => row.getD j (Frac.integer 0)
  a.map fun row =>
    cols.map fun col =>
      Frac.sum ((row.zip col).map fun (x, y) => x.mul y)

/-- Check exact rational matrix commutativity `A * B = B * A`. -/
def matricesCommute (a b : List (List Frac)) : Bool :=
  let n := a.length
  b.length == n &&
  a.all (fun row => row.length == n) &&
  b.all (fun row => row.length == n) &&
  matMul a b == matMul b a

end HeckeMassKernel
