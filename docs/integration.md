# Library integration

## C with CMake

Build and install the library, then configure the standalone consumer against the install prefix. Run these commands from the repository root.

```sh
cmake -S c -B build/c -DCMAKE_BUILD_TYPE=Release
cmake --build build/c
cmake --install build/c --prefix "$PWD/build/install"

cmake -S examples/c -B build/c-example -DCMAKE_PREFIX_PATH="$PWD/build/install"
cmake --build build/c-example
(cd build/c-example && ctest --output-on-failure)
```

Use `find_package(HeckeMass CONFIG REQUIRED)` in the consumer project and link the `HeckeMass::hecke_mass` target. The target supplies the include path for `<hecke_mass/scaffold.h>`. `hecke_mass_scaffold_probe` accepts separate input and output buffers or operates in place. For library-only builds, configure with `-DBUILD_TESTING=OFF`.

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

`hecke_mass_kernel::scaffold_probe` takes a `&[u32]` and returns a `Vec<u32>`. The crate builds with Cargo and has no C or Lean build dependencies.

## RISC-V Vector backend

`-DHECKE_MASS_ENABLE_RVV=ON` selects the RV64GCV implementation of the C scaffold probe. The resulting library requires a CPU or emulator with the RISC-V Vector extension. The CMake target and public header are the same for either backend.

For a Linux cross-build, the CI recipe uses Clang 18, a RISC-V GNU cross toolchain, and QEMU user-mode emulation on Ubuntu 24.04.

```sh
cmake -S c -B build/rvv \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_SYSTEM_NAME=Linux \
  -DCMAKE_SYSTEM_PROCESSOR=riscv64 \
  -DCMAKE_C_COMPILER=clang-18 \
  -DCMAKE_C_COMPILER_TARGET=riscv64-linux-gnu \
  -DCMAKE_C_FLAGS=--gcc-toolchain=/usr \
  '-DCMAKE_CROSSCOMPILING_EMULATOR=qemu-riscv64;-L;/usr/riscv64-linux-gnu' \
  -DHECKE_MASS_ENABLE_RVV=ON
cmake --build build/rvv
(cd build/rvv && QEMU_CPU=rv64,v=true,vlen=128,elen=64 ctest --output-on-failure)
```
