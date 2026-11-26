import Init

namespace ResearchMass

/-- Unreduced rational representation. A zero denominator is interpreted as zero. -/
structure Fraction where
  num : Int
  den : Nat

def zero : Fraction := ⟨0, 1⟩
def clean (a : Fraction) : Fraction := if a.den == 0 then zero else a
def add (a b : Fraction) : Fraction :=
  let a := clean a
  let b := clean b
  ⟨a.num * Int.ofNat b.den + b.num * Int.ofNat a.den, a.den * b.den⟩
def mul (a b : Fraction) : Fraction :=
  let a := clean a
  let b := clean b
  ⟨a.num * b.num, a.den * b.den⟩
def reciprocalNat (n : Nat) : Fraction := if n == 0 then zero else ⟨1, n⟩
def mass : List Nat → Fraction
  | [] => zero
  | n :: ns => add (reciprocalNat n) (mass ns)
def weightedSum : List (Fraction × Fraction) → Fraction
  | [] => zero
  | (a, b) :: xs => add (mul a b) (weightedSum xs)

#print axioms clean
#print axioms add
#print axioms mul
#print axioms reciprocalNat
#print axioms mass
#print axioms weightedSum
end ResearchMass
