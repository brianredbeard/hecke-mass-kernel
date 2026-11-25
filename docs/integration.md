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

`hecke_mass_kernel::class_mass` takes a slice of `BigUint` orders. `hecke_mass_kernel::hecke` takes a `BigRational` character value, three `BigUint` parameters, and a slice of `BigRational` samples. Both return a `BigRational` in lowest terms. The crate reexports these types and builds with Cargo independently of C and Lean.

## RISC-V Vector backend

`-DHECKE_MASS_ENABLE_RVV=ON` selects the RV64GCV implementation of the C scaffold probe. The resulting library requires a CPU or emulator with the RISC-V Vector extension. The CMake target and public header are the same for either backend.

For a Linux cross-build of the probe, the CI recipe uses Clang 18, a RISC-V GNU cross toolchain, and QEMU user-mode emulation on Ubuntu 24.04. Use `HECKE_MASS_BUILD_FINITE_KERNEL=OFF` for probe-only builds without target GMP. The exact operations use scalar GMP arithmetic.

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
