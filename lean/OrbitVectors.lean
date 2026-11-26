import HeckeMassKernel.Finite

open HeckeMassKernel

private def cases : List (Nat × Frac × List Nat) :=
  [ (24, Frac.integer 64, [24, 4, 2, 6, 8, 2, 6, 2, 8, 4, 24]),
    (24, Frac.integer 64, [4, 2, 6, 8, 2, 6, 2, 8, 4, 24]),
    (48, Frac.integer 8, [48, 16, 16, 48]),
    (48, Frac.integer 8, [48, 16, 48]),
    (48, Frac.integer 8, [48, 16, 16, 16, 48]),
    (10, Frac.integer 4, [3]),
    (10, ⟨2, 3, by decide⟩, [5]),
    (1, Frac.integer 0, []),
    (2432902008176640000, Frac.integer 2432902008176640001, [1]),
    (36893488147419103234, Frac.integer 3, [18446744073709551617]) ]

def main : IO Unit := do
  for (groupOrder, expected, orders) in cases do
    let some audit := orbitCompleteness groupOrder orders expected
      | throw (IO.userError "invalid orbit fixture")
    let status := match audit.status with
      | .complete => "complete"
      | .missing _ => "missing"
      | .excess _ => "excess"
    let encodedOrders := if orders.isEmpty then "-" else String.intercalate "," (orders.map toString)
    IO.println s!"{groupOrder}\t{expected.render}\t{encodedOrders}\t{audit.covered.render}\t{audit.deficit.render}\t{status}"

example : orbitCompleteness 1 [0] (Frac.integer 1) = none := by decide
example : orbitCompleteness 0 [] (Frac.integer 1) = none := by decide
example : orbitCompleteness 1 [] (Frac.integer (-1)) = none := by decide
