# SpacemiT K3 matrix demonstration

The demo multiplies the recorded level-23 Brandt matrices `T2` and `T3`
in both orders using one signed INT8 `smt.vmadot` instruction per product.
It zero-pads the matrices to the hardware's 4×8 by 8×4 tile, checks each
INT32 result against scalar multiplication, and compares the two products.
[Level-23 fixtures](../../lean/HeckeMassKernel/ReplayedCases.lean) ·
[SpacemiT IME specification](https://github.com/spacemit-com/docs-ai/blob/main/en/architecture/ime_extension.md#51-integer-matrix-multiplication-base-path-smtvmadot)

From the repository root on a SpacemiT Linux system such as Pico, build
and run with GCC and GNU binutils.

```sh
cc -std=c99 -O2 -Wall -Wextra -Werror -march=rv64gc -mabi=lp64d \
  examples/k3-ime/brandt_demo.c examples/k3-ime/vmadot.S -o k3-ime-demo
./k3-ime-demo
```

The assembly uses the documented `smt.vmadot v16, v4, v5, i8` instruction
encoding so older assemblers can build it. The demo exits with status 77
if its child traps with an illegal instruction or the vector registers
have a different width.

On Pico the demo passed on CPUs 0–7, with 256-bit vector registers.
The Linux CPU inventory contains eight X100 cores. The K3 specification
also describes A100 AI cores with 1024-bit vector registers and IME-II.
[K3 CPU specifications](https://github.com/spacemit-com/docs-chip/blob/main/en/key_stone/k3/k3_docs/k3_ds.md#21-cpu-subsystem)

```text
[2 8 2]
[4 5 3]
[3 9 0]
```

## How the instruction multiplies a tile

Each operand register holds 32 signed bytes. The first holds four
rows of the left tile and the second holds four columns of the right
tile as contiguous eight-byte sequences. The wrapper clears the INT32
accumulator in `v16`–`v17`, loads the operands into `v4` and `v5`, then
issues `smt.vmadot`. That instruction accumulates sixteen eight-term dot
products. The wrapper stores all sixteen INT32 results. The same vector
register file holds the operands and accumulator throughout the operation.
[Assembly wrapper](vmadot.S) · [SpacemiT tile instruction](https://github.com/spacemit-com/docs-ai/blob/main/en/architecture/ime_extension.md#51-integer-matrix-multiplication-base-path-smtvmadot)

## Packed tile benchmark

On Pico's X100 CPU 7, the median time for a packed 4×8 by 8×4 tile was
**99.13 ns** in scalar C and **7.01 ns** with base IME, giving **14.1×**
the scalar throughput. The run used GCC 14.4.1 and 256-bit vectors.

```sh
gcc -std=c99 -O3 -fno-tree-vectorize -fno-lto -Wall -Wextra -Werror \
  -pedantic -march=rv64gc -mabi=lp64d examples/k3-ime/brandt_bench.c \
  examples/k3-ime/vmadot.S -o k3-ime-bench
taskset -c 7 ./k3-ime-bench
```

The benchmark cycles through 128 prepared tiles with varied signed bytes.
Each sample makes 1,048,576 calls. Six samples per implementation alternate
which one runs first. Both use the same indirect call and produce the same
sixteen INT32 values per tile, verified against scalar products after
timing. The IME timing includes register setup, accumulator clearing,
operand loads and result stores. Input packing and comparisons occur
outside the timer. These results describe repeated calls on a small
prepared working set. Larger matrix multiplications also incur packing,
tiling and memory costs. [Benchmark source](brandt_bench.c)
