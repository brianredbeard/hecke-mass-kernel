# Kernel specification

The Hecke mass kernel definition is pending. The specification will define the mathematical inputs and outputs, their representation and valid ranges, and the arithmetic and edge cases that the implementations must reproduce. Public kernel signatures and kernel fixture encoding will follow that definition.

## Scaffold probe

The scaffold applies a bitwise exclusive OR with `0xa5a5a5a5` to each unsigned 32-bit input word. It emits the same number of words, in the same order. An empty input produces an empty output. The probe gives the proof, fixture, packaging, and backend checks a concrete operation while the kernel definition is open.
