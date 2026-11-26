# RISC-V hardware benchmarks

## Native Brandt destination counts

The same benchmark scanned 1,048,576 unsigned 32-bit destination labels
on each board. Each pass found 4,041 matches. The table reports medians
of six native samples per backend, with one process pinned to CPU 0.

| Board and CPU | Scalar (million labels/s) | RVV (million labels/s) | RVV speedup on the same board |
| --- | ---: | ---: | ---: |
| Pico, SpacemiT K3 X100 | 990.14 | 1,952.34 | **1.97×** |
| HiFive Premier P550, ESWIN EIC7700X | 595.13 | — | Scalar only |

Pico ran GCC 14.4.1 on Linux
`6.12.0-284.acpidebug.1.el10.riscv64` and reported 256-bit vector registers.
The P550 ran GCC 14.2.1 on Linux `6.12.0-75.rv.1.el10.riscv64`. Its
reported ISA lacks the vector extension, so it used the portable counter.
The experiment compares each vector result with its own board's scalar
baseline. [K3 datasheet](https://github.com/spacemit-com/docs-chip/blob/main/en/key_stone/k3/k3_docs/k3_ds.md#21-cpu-subsystem) · [HiFive Premier P550 specifications](https://www.sifive.com/development-platforms/hifive-premier-p550)

Each sample makes 256 passes over one 4 MiB buffer. The benchmark prepares
the buffer and computes the expected count before timing. It checks the
aggregate count after each timed sample. On Pico the two backends alternate
which runs first. Both use `-O3 -fno-lto`. The scalar counter uses
`-march=rv64gc -fno-tree-vectorize`, and the RVV counter uses
`-march=rv64gcv`. These are single-core repeated-scan rates. Buffer size,
cache behavior, clocks and compiler choices affect the result.
[Benchmark source](../examples/rvv/brandt_bench.c)

### How RVV performs the count

A Brandt matrix entry counts how many neighbors in a source row reach a
particular target. Repeated destination labels each contribute one.
The scalar implementation checks each label individually. The RVV loop
uses four instructions to process a chunk of the row.

| Instruction | Role in the count |
| --- | --- |
| `vsetvli` | Selects 32-bit elements and an eight-register group (`e32,m8`), then returns the active length based on how many labels remain. |
| `vle32.v` | Loads the active contiguous destination labels. |
| `vmseq.vx` | Compares the labels with the scalar target and sets one mask bit for every match. |
| `vcpop.m` | Returns the number of active set bits in a scalar register. |

The loop adds the population count to the result and advances by the
active length. With a 256-bit VLEN, `e32,m8` provides capacity for up to
64 labels per chunk. The returned length also governs the final load,
comparison and count, so short rows and tails use the same loop. Grouping
registers reduces the number of loop iterations and mask reductions. The
processor's physical execution and memory bandwidth still govern how
quickly it processes a register group.
[RVV counter](../c/src/rvv/brandt.c) · [RISC-V V 1.0 specification](https://docs.riscv.org/reference/isa/unpriv/v-st-ext)

### Reproduce the measurements

Run from the repository root on RISC-V Linux. The scalar build works on
both boards.

```sh
mkdir -p build/riscv-bench
gcc -std=c99 -O3 -fno-lto -fno-tree-vectorize -march=rv64gc -I c/include \
  examples/rvv/brandt_bench.c c/src/brandt.c -o build/riscv-bench/brandt-scalar
taskset -c 0 build/riscv-bench/brandt-scalar
```

On an RVV 1.0 system such as Pico, compile the scalar reference separately
and link both backends into the same benchmark.

```sh
gcc -std=c99 -O3 -fno-lto -fno-tree-vectorize -march=rv64gc -I c/include \
  -Dhecke_mass_brandt_count_u32=hecke_mass_brandt_count_scalar_u32 \
  -c c/src/brandt.c -o build/riscv-bench/brandt-scalar.o
gcc -std=c99 -O3 -fno-lto -march=rv64gcv -I c/include \
  examples/rvv/brandt_bench.c build/riscv-bench/brandt-scalar.o c/src/rvv/brandt.c \
  -o build/riscv-bench/brandt-rvv
taskset -c 0 build/riscv-bench/brandt-rvv
```

Take the median rate for each backend and divide the RVV median by the
scalar median. The repository's QEMU checks exercise the counter at
128-, 256-, and 512-bit VLEN for correctness.
[Build and test the library](integration.md#risc-v-vector-backend)

## SpacemiT K3 matrix extension

| Workload on Pico's X100 | Scalar median | Base IME median | Speedup |
| --- | ---: | ---: | ---: |
| Packed signed INT8 4×8 by 8×4 tile with INT32 output | 99.13 ns/tile | 7.01 ns/tile | **14.1×** |

The benchmark measures the call, register setup, operand loads,
accumulator clear and output store. Both versions use the same prepared
inputs and write the same sixteen INT32 outputs. Input packing and output
verification run outside the timer. The ratio describes small prepared
tiles on one X100 core. Larger matrix products also pay for packing,
tiling and memory traffic. [Packed-tile methodology and commands](../examples/k3-ime/README.md#packed-tile-benchmark)

For the level-23 example, the C code pads the two 3×3 Brandt matrices with
zeros and packs four left rows and four right columns into contiguous
buffers. The assembly loads those buffers into `v4` and `v5`, with eight
signed bytes per row or column. One `smt.vmadot` replaces the scalar
multiply-add loops for the entire tile. It adds sixteen eight-term dot
products to INT32 accumulators in `v16` and `v17`, keeping the
intermediate sums in the vector register file. The wrapper then stores
the entire 4×4 output tile. The demo checks all sixteen outputs against
scalar multiplication and gets the same 3×3 product for $T_2T_3$ and
$T_3T_2$. [Demo source](../examples/k3-ime/brandt_demo.c) · [Assembly wrapper](../examples/k3-ime/vmadot.S) · [SpacemiT base IME instruction](https://github.com/spacemit-com/docs-ai/blob/main/en/architecture/ime_extension.md#51-integer-matrix-multiplication-base-path-smtvmadot)

Pico exposed eight X100 CPUs to Linux, and the matrix demo passed on each
of them. SpacemiT documents a separate A100 core with 1024-bit vectors
and IME-II. The native results above cover the X100's 256-bit RVV and
base IME. [K3 CPU subsystem](https://github.com/spacemit-com/docs-chip/blob/main/en/key_stone/k3/k3_docs/k3_ds.md#21-cpu-subsystem)

## Floating-point reductions

The GMP oracle sums exact reciprocals of integer orders or exact products
of binary64 inputs. It rounds the sum once to nearest, ties to even.
ULP distance compares the result to that rounded reference. The benchmark
also computes absolute error against the unrounded rational value.
[Floating-point audit guide](guides/rvv-oracle.md)

### Native results

Each rate is the median of five samples with 2,048 calls per sample.
Each call processes 4,099 input terms. Both processes ran on CPU 0.
Pico used GCC 14.4.1 and 256-bit vectors. The P550 used GCC 14.2.1 and
the scalar backend. Rates count every input term, including zero orders.
The exact reference, input generation and validation run outside the timer.
[Benchmark source](../examples/rvv/f64_bench.c)

| Workload | Pico scalar | Pico RVV ordered | Pico RVV unordered | P550 scalar | Pico ULPs, scalar / ordered / unordered |
| --- | ---: | ---: | ---: | ---: | ---: |
| Harmonic reciprocal sum | 110.99 | 115.17 | 115.21 | 42.38 | 18 / 18 / 7 |
| Wide orders with zeros | 124.86 | 115.18 | 115.23 | 47.69 | 47 / 47 / 20 |
| Signed weighted sum with cancellation | 650.71 | 651.83 | 1,203.66 | 349.42 | 46,544,526,227,013,632 / 46,544,526,227,013,632 / 4,473,582,959,932,211,200 |

Rates are in million terms per second. The P550's results matched Pico's
scalar results bit for bit.

The reciprocal loop loads unsigned 32-bit orders using `e32,m4` and
widens them exactly to binary64 in `e64,m8`. Both configurations have the
same lane capacity, up to 32 terms per chunk on Pico. Masked
`vfrdiv.vf` computes the reciprocals and leaves
zeros in the lanes for zero orders. The weighted loop uses `vfmul.vv`
and rounds each product before reduction. `vfredosum.vs` adds each term
in input order. `vfredusum.vs` may regroup the terms within a chunk.
[RVV source](../c/src/rvv/f64.c) ·
[RISC-V V reductions](https://docs.riscv.org/reference/isa/v20240411/_attachments/riscv-unprivileged.pdf)

On Pico, unordered RVV reduced the measured ULP error for both reciprocal
workloads. Its throughput ranged from 0.92× to 1.04× scalar throughput.
For the weighted case it was 1.85× as fast. The exact weighted sum was
`1367 × 2^-40`. Scalar and ordered RVV returned `2^-40` and unordered RVV
returned zero. Their absolute errors were about `1.2424e-9` and
`1.2433e-9`, respectively. Both lost almost the entire answer, despite
the small absolute error. This is why the benchmark reports both ULP
distance and absolute error for signed inputs.

### QEMU accuracy at three vector lengths

Clang 18.1.3 cross-built the conformance test, and QEMU 8.2.2 ran it at each
vector length. All three backends gave the same result on each supplied
workload in this emulator run. The table reports the distance from the
expected binary64 value for the unordered kernel.

| VLEN | Harmonic ULPs | Wide-order ULPs | Signed cancellation ULPs |
| ---: | ---: | ---: | ---: |
| 128 bits | 18 | 47 | 46,544,526,227,013,632 |
| 256 bits | 18 | 47 | 46,544,526,227,013,632 |
| 512 bits | 18 | 47 | 46,544,526,227,013,632 |

The absolute distance from the rounded reference in the cancellation
case was `1.2424e-9` at all three lengths. Pico's unordered path produced
different values even at the same 256-bit VLEN. These emulator runs
exercise vector lengths and tails for correctness. The throughput
figures come from native hardware.
[Conformance cases](../c/tests/f64_vectors.c)
