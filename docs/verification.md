# Verification

## Lean

`HeckeMassKernel.Finite` proves the recursive mass equations, the finite Hecke formula and selected exact outputs. These theorems concern the arithmetic on supplied tables. The upstream interpretation of a table as a global mass or Hecke coefficient uses separate bridge theorems and certificates.

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
(cd lean && lake exe kernel_vectors) > build/kernel.tsv &&
  cp build/kernel.tsv tests/vectors/kernel.tsv
```

`tests/vectors/kernel.tsv` has three tab-separated columns for the operation, space-separated inputs and reduced rational output. For `mass` the inputs are the orders. For `hecke` the first four inputs are `u q k rank`, followed by the samples. The C and Rust integration tests run every row against their public APIs.

CI compares freshly generated fixtures with the checked-in files. The C and Rust scaffold tests use the probe fixtures across a range of batch lengths. The C probe test also covers in-place operation. The RVV job runs that test under QEMU at two vector lengths. The Lean theorems apply to the Lean reference.
