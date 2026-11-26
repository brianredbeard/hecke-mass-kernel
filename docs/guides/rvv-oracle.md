# Check floating-point SIMD sums against exact arithmetic

## 1. The bug this catches

Scalar and vector code can agree after both have lost a term. In
binary64, evaluating `(2^53 + 1) - 2^53` from left to right gives zero.
The exact answer is one. A reference built with rational arithmetic
recovers that term and makes the loss visible.

## 2. Build and run the oracle

The reciprocal benchmark accepts nonnegative 32-bit integer orders.
Each order converts to binary64 exactly, and zero contributes zero.
The weighted benchmark accepts finite binary64 weights and samples.
Its oracle converts each operand to its exact rational value, multiplies
and sums in GMP, then rounds the total once to binary64.

On a Linux system with GMP development headers, build the benchmark
from the repository root. Add `-DHECKE_MASS_ENABLE_RVV=ON` to the first
command on an RVV 1.0 host such as Pico.

```sh
cmake -S c -B build/f64 -DCMAKE_BUILD_TYPE=Release
cmake --build build/f64
ctest --test-dir build/f64 --output-on-failure
build/f64/hecke_mass_f64_bench
```

The benchmark times only the approximate kernels. It prints the rounded
exact answer, each kernel's ULP distance from that answer, and absolute
error against the rational total. [Benchmark source](../../examples/rvv/f64_bench.c)

## 3. Run it in CI

The GMP-backed build tests rounding at ties, subnormal boundaries and
overflow. The GMP-free conformance test uses fixed binary64 reference
bits and can run on a target without GMP. The repository cross-build checks
that same test under QEMU at VLEN 128, 256, and 512.

```sh
ctest --test-dir build/f64 -R 'f64_oracle|f64_vectors' --verbose
```

[Cross-build instructions](../integration.md#risc-v-vector-backend) ·
[CI workflow](../../.github/workflows/ci.yml)

## 4. Interpret the result

The reference rounds to nearest with ties to even. Implementing this in
integer arithmetic keeps it independent of the host's rounding mode.
GMP's `mpq_get_d` uses rounding toward zero. [GMP conversion rules](https://gmplib.org/manual/Rational-Conversions)

The scalar and RVV ordered implementations add the rounded terms in
input order. The ordered RVV loop carries the running sum from one chunk
to the next. The unordered instruction may regroup additions within
each chunk, so different vector lengths or processors can give different
rounded results. Weighted products round before addition in both cases.
[RISC-V V floating-point reductions](https://docs.riscv.org/reference/isa/v20240411/_attachments/riscv-unprivileged.pdf)

ULP distance counts representable binary64 steps from the rounded
reference. Around zero, cancellation can give a large ULP count even
for a small absolute error. Read both values for signed weighted sums.
These are accuracy checks on the supplied arithmetic cases.

## 5. Compare throughput and error

The harness uses a harmonic tail, mixed orders including zero and
large unsigned integers, and a signed weighted workload with
cancellation. Time the same inputs on native hardware and use
emulation for correctness checks at other vector lengths.
[Native results and QEMU error measurements](../benchmarks.md#floating-point-reductions)
