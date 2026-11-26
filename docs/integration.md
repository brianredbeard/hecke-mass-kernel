# Library integration

## C with CMake

Install GMP development files, then build and install the library and configure the standalone consumer against the install prefix. Run these commands from the repository root.

```sh
cmake -S c -B build/c -DCMAKE_BUILD_TYPE=Release
cmake --build build/c
cmake --install build/c --prefix "$PWD/build/install"

cmake -S examples/c -B build/c-example -DCMAKE_PREFIX_PATH="$PWD/build/install"
cmake --build build/c-example
(cd build/c-example && ctest --output-on-failure)
```

Use `find_package(HeckeMass CONFIG REQUIRED COMPONENTS FiniteKernel)` in the consumer project and link the `HeckeMass::hecke_mass` target. The target supplies the include path for `<hecke_mass/kernel.h>` and links GMP. `hecke_mass_class_mass_checked` and `hecke_mass_hecke_checked` validate pointers, nonnegative integer inputs, and positive denominators, returning `HECKE_MASS_OK` or `HECKE_MASS_ERR_INVALID_ARGUMENT` without modifying `result` on error. The void wrappers `hecke_mass_class_mass` and `hecke_mass_hecke` delegate to the checked implementations and zero `result` on invalid input. Output aliasing (`result == u` or `result == samples[i]`) is supported. For library-only builds, configure with `-DBUILD_TESTING=OFF`.

## Rust with Cargo

Run the standalone consumer from the repository root.

```sh
cargo run --locked --manifest-path examples/rust/Cargo.toml
```

Use a path dependency pointing to the repository's `rust/` directory in a local checkout. For a Git dependency, pin the revision you tested.

```toml
[dependencies]
hecke-mass-kernel = { git = "https://github.com/brianredbeard/hecke-mass-kernel.git", rev = "<commit>" }
```

`hecke_mass_kernel::class_mass` takes a slice of `BigUint` orders (with `class_mass_u64` for `&[u64]`). `hecke_mass_kernel::hecke` takes a `BigRational` character value, three `BigUint` parameters, and a slice of `BigRational` samples. Both use balanced pairwise summation and return a `BigRational` in lowest terms. `check_detailed_balance` verifies weighted symmetry of an operator matrix against positive stabilizer orders. The crate reexports `BigInt`, `BigUint`, and `BigRational` and builds with Cargo independently of C and Lean.

## Orbit completeness

The audit computes coverage as the group order times the reciprocal sum of
the stabilizer orders. It returns the signed deficit, meaning the expected
total minus coverage. The group and stabilizer orders must be positive.
Positive orders that fail to divide the group order can yield fractional
coverage.

- In C, call `hecke_mass_orbit_deficit_checked` with two distinct initialized
  `mpq_t` outputs and a nonnegative rational target. A positive deficit means
  missing coverage, and a negative one means excess. The install also provides
  `pkg-config --cflags --libs hecke_mass`.
- In Rust, call `orbit_completeness` with the order slice and nonnegative rational
  target, or feed orders incrementally to `OrbitAccumulator`. The typed status
  distinguishes complete, missing, and excess, with positive magnitudes in
  the last two cases.
- From a checkout, install the CLI with `cargo install --locked --path cli`.
  The `orbits` command accepts a nonnegative integer target and an optional
  input file. [Graph-generator recipe](guides/graph-orbits.md) ·
  [Crystal mesh recipe](guides/crystal-meshes.md)

## RISC-V Vector backend

`hecke_mass_brandt_count_u32` counts a target class in a row of neighbor
destinations, preserving repeated edges. Include `<hecke_mass/brandt.h>`
and link `HeckeMass::hecke_mass`. Set `-DHECKE_MASS_ENABLE_RVV=ON` to
select the RV64GCV implementation. It uses vector equality and mask
population count, adjusting the active length for the last chunk. The
count is an integer operation and needs no GMP.

On a RISC-V Linux host with GCC supporting RVV intrinsics, build and test
natively. This build also includes the scalar GMP-backed rational kernel
when GMP development files are installed.

```sh
cmake -S c -B build/rvv-native -DCMAKE_BUILD_TYPE=Release -DHECKE_MASS_ENABLE_RVV=ON
cmake --build build/rvv-native
ctest --test-dir build/rvv-native --output-on-failure
```

The native benchmark compares the vector counter with the same library's
scalar implementation compiled without auto-vectorization. Run these commands
against the static build above.

```sh
gcc -std=c99 -O3 -march=rv64gc -fno-tree-vectorize -I c/include \
  -Dhecke_mass_brandt_count_u32=hecke_mass_brandt_count_scalar_u32 \
  -c c/src/brandt.c -o build/rvv-native/brandt-scalar.o
gcc -std=c99 -O3 -march=rv64gcv -I c/include examples/rvv/brandt_bench.c \
  build/rvv-native/brandt-scalar.o build/rvv-native/libhecke_mass.a \
  -o build/rvv-native/brandt-bench
taskset -c 0 build/rvv-native/brandt-bench
```

On Pico's SpacemiT X100, the median was about 1.85 billion labels/s with RVV
and 0.99 billion labels/s with scalar code. Both counted 4,041 matches in
the same 4 MiB buffer. This measures repeated scans on one core with
256-bit vectors. [Separate K3 matrix hardware demo](../examples/k3-ime/README.md)

For a Linux cross-build, CI uses Clang 18, a RISC-V GNU cross toolchain, and
QEMU user-mode emulation on Ubuntu 24.04. Set
`HECKE_MASS_BUILD_FINITE_KERNEL=OFF` for a build without target GMP.

```sh
cmake -S c -B build/rvv \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_SYSTEM_NAME=Linux \
  -DCMAKE_SYSTEM_PROCESSOR=riscv64 \
  -DCMAKE_C_COMPILER=clang-18 \
  -DCMAKE_C_COMPILER_TARGET=riscv64-linux-gnu \
  -DCMAKE_C_FLAGS=--gcc-toolchain=/usr \
  '-DCMAKE_CROSSCOMPILING_EMULATOR=qemu-riscv64;-L;/usr/riscv64-linux-gnu' \
  -DHECKE_MASS_ENABLE_RVV=ON \
  -DHECKE_MASS_BUILD_FINITE_KERNEL=OFF
cmake --build build/rvv
(cd build/rvv && QEMU_CPU=rv64,v=true,vlen=128,elen=64 ctest --output-on-failure)
```
