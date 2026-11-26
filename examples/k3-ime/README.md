# SpacemiT K3 matrix demonstration

The demo multiplies the recorded level-23 Brandt matrices `T2` and `T3`
in both orders using one signed INT8 `smt.vmadot` instruction per product.
It zero-pads the matrices to the hardware's 4×8 by 8×4 tile, checks each
INT32 result against scalar multiplication, and compares the two products.
[Level-23 fixtures](../../lean/HeckeMassKernel/ReplayedCases.lean) ·
[SpacemiT IME specification](https://github.com/spacemit-com/docs-ai/blob/main/en/architecture/ime_extension.md#chapter-5-integer-matrix-multiplication-instructions)

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
