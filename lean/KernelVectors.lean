import HeckeMassKernel.Finite

open HeckeMassKernel

private def massCases : List (List Nat) :=
  [[], [6], [4, 6], [0, 2, 0], [2, 3, 7, 43], [18446744073709551617]]

private def heckeCases : List (Frac × Nat × Nat × Nat × List Frac) :=
  [ (Frac.integer (-1), 3, 1, 3, [Frac.integer 2, Frac.integer 4]),
    (Frac.integer 1, 2, 1, 2, []),
    (Frac.integer 1, 3, 2, 5, [⟨-1, 3, by decide⟩, ⟨1, 3, by decide⟩]),
    (⟨2, 3, by decide⟩, 7, 0, 4, [⟨1, 2, by decide⟩, ⟨-2, 3, by decide⟩]),
    (Frac.integer 0, 3, 1, 3, [Frac.integer 1]),
    (Frac.integer 1, 0, 1, 2, [Frac.integer 5]),
    (Frac.integer 1, 0, 1, 1, [Frac.integer 5]),
    (Frac.integer 1, 2, 70, 2, [Frac.integer 1]),
    (Frac.integer 1, 0, 18446744073709551617, 2, [Frac.integer 3]),
    (Frac.integer 1, 1, 18446744073709551617, 2, [Frac.integer 3]) ]

def main : IO Unit := do
  for orders in massCases do
    let arguments := String.intercalate " " (orders.map toString)
    IO.println s!"mass\t{arguments}\t{(classMass orders).render}"
  for (u, q, k, rank, values) in heckeCases do
    let arguments := String.intercalate " " ([u.render, toString q, toString k, toString rank] ++
      values.map Frac.render)
    IO.println s!"hecke\t{arguments}\t{(hecke u q k rank values).render}"
