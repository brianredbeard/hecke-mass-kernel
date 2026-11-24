namespace HeckeMassKernel

/-- An exact fraction stored with a positive denominator. -/
structure Frac where
  num : Int
  den : Nat
  positive : 0 < den

namespace Frac

def integer (n : Int) : Frac := ⟨n, 1, by decide⟩

def add (a b : Frac) : Frac :=
  ⟨a.num * b.den + b.num * a.den, a.den * b.den, Nat.mul_pos a.positive b.positive⟩

def mul (a b : Frac) : Frac :=
  ⟨a.num * b.num, a.den * b.den, Nat.mul_pos a.positive b.positive⟩

/-- Inversion is total, with `inv 0 = 0`. -/
def inv (a : Frac) : Frac :=
  match a.num with
  | .ofNat 0 => integer 0
  | .ofNat (n + 1) => ⟨a.den, n + 1, Nat.zero_lt_succ n⟩
  | .negSucc n => ⟨-(a.den : Int), n + 1, Nat.zero_lt_succ n⟩

def reciprocalNat (n : Nat) : Frac := (integer n).inv

def sum (values : List Frac) : Frac := values.foldr add (integer 0)

/-- Render the fraction in lowest terms. -/
def render (a : Frac) : String :=
  let g := a.num.natAbs.gcd a.den
  let n := a.num / (g : Int)
  let d := a.den / g
  if d == 1 then toString n else s!"{n}/{d}"

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

/-- Sum the samples and scale by the inverses of `u` and `q^(k * (rank / 2))`. -/
def hecke (u : Frac) (q k rank : Nat) (values : List Frac) : Frac :=
  (u.inv.mul (Frac.reciprocalNat (normalizationPower q (k * (rank / 2))))).mul (Frac.sum values)

@[simp] theorem classMass_nil : classMass [] = Frac.integer 0 := rfl

theorem classMass_cons (n : Nat) (ns : List Nat) :
    classMass (n :: ns) = (Frac.reciprocalNat n).add (classMass ns) := rfl

theorem hecke_formula (u : Frac) (q k rank : Nat) (values : List Frac) :
    hecke u q k rank values =
      (u.inv.mul (Frac.reciprocalNat (q ^ (k * (rank / 2))))).mul
        (values.foldr Frac.add (Frac.integer 0)) := by
  simp [hecke, normalizationPower_eq, Frac.sum]

theorem mass_six : (classMass [6]).num * 6 = ((classMass [6]).den : Int) := by decide

theorem mass_level_eleven :
    let result := classMass [4, 6]
    result.num * 12 = 5 * (result.den : Int) := by decide

theorem hecke_minus_two :
    let result := hecke (Frac.integer (-1)) 3 1 3 [Frac.integer 2, Frac.integer 4]
    result.num = -2 * (result.den : Int) := by decide

end HeckeMassKernel
