# Verification

## Lean

`HeckeMassKernel.Scaffold.probeSpec` specifies the scaffold operation on one `UInt32`. The executable reference maps the operation over a list. Lean checks that the reference preserves length and agrees with the specification at every index, including indexes outside the list.

```sh
cd lean
lake build
```

## Shared fixtures

`tests/vectors/scaffold.csv` contains `input,output` pairs in order, one pair of decimal `UInt32` values per line. The cases include zero, the maximum `UInt32`, high-bit boundaries, alternating bit patterns, and a deterministic sequence long enough to exercise multiple vector chunks. To regenerate the file from the repository root after updating the Lean reference or inputs, run the following commands.

```sh
mkdir -p build
(cd lean && lake exe scaffold_vectors) > build/scaffold.csv &&
  cp build/scaffold.csv tests/vectors/scaffold.csv
```

CI compares freshly generated fixtures with the checked-in file. The C and Rust tests use the shared fixtures across a range of batch lengths. The C test also covers in-place operation. The RVV job runs the C test under QEMU at two vector lengths. Agreement across the compiled libraries is established for those test cases. The Lean theorems apply to the Lean reference.
