# Hecke mass kernel

This repository implements exact arithmetic for class masses and
normalized Hecke coefficients from finite tables. Lean defines both
operations and generates shared test fixtures for the native C and Rust
libraries. [Lean definitions](lean/HeckeMassKernel/Finite.lean) ·
[Upstream bridge](bridge/README.md) ·
[C API](c/include/hecke_mass/kernel.h) · [Rust API](rust/src/lib.rs) ·
[Shared fixtures](tests/vectors/kernel.tsv)

Audit the coverage of a finite orbit table by supplying its group order,
the expected labeled count, and one stabilizer order per line. This example
covers five labeled objects with two orbits under a group of order 12.

```sh
printf '4\n6\n' | cargo run --quiet --locked --manifest-path cli/Cargo.toml -- \
  orbits --group-order 12 --expected 5
```

The CLI prints `complete covered=5 deficit=0`. A missing or extra count
returns exit code 1 with the exact difference. Malformed input returns
exit code 2. [Graph generators](docs/guides/graph-orbits.md) ·
[Crystal meshes](docs/guides/crystal-meshes.md)

Python callers can install the package from this checkout with
`python -m pip install ./python` and get exact `Fraction` results.
The cookbooks cover spglib, pynauty, and SageMath with LMFDB data.
[Python package and cookbooks](python/README.md)

## Quick start

Run each check from the repository root. Use Elan with the checked-in
toolchain for Lean, CMake 3.16 or newer with a C compiler and GMP
development files for C, and Cargo for Rust.

```sh
(cd lean && lake build)

cmake -S c -B build/c
cmake --build build/c
(cd build/c && ctest --output-on-failure)

cargo test --manifest-path rust/Cargo.toml
```

[Library installation and integration](docs/integration.md) · [Verification scope](docs/verification.md)

## RISC-V hardware results

| Native benchmark | Scalar | Hardware backend | Same-board speedup |
| --- | ---: | ---: | ---: |
| SpacemiT K3 X100, exact Brandt destination count | 990 million labels/s | 1.95 billion labels/s (RVV) | **1.97×** |
| SiFive P550, same destination count | 595 million labels/s | — | Scalar only |
| SpacemiT K3 X100, packed INT8 matrix tile | 99.13 ns/tile | 7.01 ns/tile (base IME) | **14.1×** |

RVV compares destination labels in chunks and counts the matching mask
bits. The K3 matrix demo uses one signed INT8 `smt.vmadot` per packed
product to reproduce the level-23 Brandt products exactly. These are
single-core measurements on a fixed input buffer or prepared tiles.
[Hardware walkthrough and reproduction commands](docs/benchmarks.md) ·
[K3 matrix demo](examples/k3-ime/README.md)

The binary64 benchmark compares scalar and RVV reductions against
exact rational sums. On Pico, unordered RVV was **1.85×** as fast on the
signed weighted workload, while cancellation erased the exact result.
[Floating-point throughput and error](docs/benchmarks.md#floating-point-reductions)

## Worked examples

The [six runnable examples](examples/rust/README.md) apply the two
operations to small cases with independently known answers: a supersingular
isogeny graph, a higher-rank normalized Hecke readout, crystal-mesh weights,
telemetry fault scenarios, quantum noise averages, and compiler patterns.
The first two are the kernel's own subject (including the full
$u^{-1}q^{-k\lfloor r/2\rfloor}$ normalization at odd rank 5). The other
four use the same arithmetic outside number theory, as orbit counting and
exact averaging. Each runs a correct case and shows the result of
introducing one or more bugs. Try the isogeny graph from the repository root
with Cargo:

```sh
cargo run --locked --manifest-path examples/rust/Cargo.toml --example isogeny_graph
```

## Explainer videos

| What the kernel computes (8:48) | Where the proof uses it (2:48) |
| :---: | :---: |
| [![Frame from the first explainer](docs/manim/what_the_kernel_computes.png)](docs/manim/what_the_kernel_computes.mp4) | [![Frame from the second explainer](docs/manim/where_the_proof_uses_it.png)](docs/manim/where_the_proof_uses_it.mp4) |
| The two sums, worked on the level-11 example. [Transcript](docs/manim/what_the_kernel_computes.md) | The paths from `riemannHypothesis` to `classMass` and `Setup.hecke`. [Transcript](docs/manim/where_the_proof_uses_it.md) |

[Sources, captions and rendering instructions](docs/manim/README.md)

## Where this came from

In November 2026, Levent Alpöge released a 17-million-line Lean formalization
of the Riemann Hypothesis and Dirichlet GRH, which the Lean FRO, Mathlib
Initiative, and independent proof checkers (including Andrew Sutherland’s
verification record) subsequently certified against Mathlib’s statement. Even
with kernel certification, a proof of that scale cannot be read line by line.
We wanted to know which concrete, executable pieces a reader could isolate,
check, and run independently. [Original submission, verification record, and
frozen source](docs/references.md)

Two definitions give a concrete answer. On one path from
`riemannHypothesis`, `classMass` gives the sum of reciprocal stabilizer
orders that appears in a volume identity. On another, `Setup.hecke`
specifies how to compute the value of a transformed form by summing over
coset representatives and applying a normalization. Both formulas are
classical and appear explicitly in the original Lean source.
[How the proof uses each definition](docs/primitive-in-the-proof.md) ·
[Source-linked dependency paths](docs/dependency-paths.md)

We trace how Alpöge’s formalization uses class mass and Hecke action,
isolate the exact arithmetic each requires once its finite data are
supplied, and publish a standalone Lean specification with replayable C
and Rust examples. Establishing that a table lists the right classes or
neighbours requires separate evidence.
[Kernel specification](docs/specification.md) · [Replayed cases](docs/replayed-cases.md)

## License

Released under the [MIT License](LICENSE).
