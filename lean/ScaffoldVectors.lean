import HeckeMassKernel

open HeckeMassKernel.Scaffold

def inputs : List UInt32 :=
  [0, 1, 0x7fffffff, 0x80000000, 0xffffffff, 0xaaaaaaaa, 0x55555555] ++
    (List.range 64).map (fun index => UInt32.ofNat (index + 1) * 0x9e3779b9)

def main : IO Unit := do
  for (input, output) in inputs.zip (reference inputs) do
    IO.println s!"{input.toNat},{output.toNat}"
