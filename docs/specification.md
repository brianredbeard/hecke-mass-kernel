# Kernel specification

The kernel evaluates two exact rational expressions from finite tables.

| Operation | Inputs | Result |
| --- | --- | --- |
| Class mass | Natural stabilizer orders \(d_i\) | \(\sum_i d_i^{-1}\) |
| Hecke coefficient | Rational character value \(u\), natural parameters \(q,k,r\), rational samples \(v_i\) | \(u^{-1}(q^{k\lfloor r/2\rfloor})^{-1}\sum_i v_i\) |

Arithmetic follows the extracted Lean model. Fractions have positive denominators. Inversion maps zero to zero, powers use \(0^0=1\), and an empty sum is zero. The rational result can be rendered in lowest terms.

A geometric interpretation requires certificates about the supplied input. For a class mass, the orders must belong to a complete set of inequivalent classes and count their stabilizers. For a Hecke coefficient, the samples must come from the appropriate coset representatives and function values, with the matching local parameters and character. The finite calculation gives \(5/12\) on the two stabilizer orders \(4,6\) supplied by the level-11 workbench.

The Lean arithmetic adapts `extracted/hecke-mass-kernel/Minimal.lean` from the research workbench. Its extraction targets `GlobalTheory.Mass.classMass` and `GlobalTheory.SeriesTie.Setup.hecke` in the upstream formalization at revision `4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e`.

## Scaffold probe

The scaffold applies a bitwise exclusive OR with `0xa5a5a5a5` to each unsigned 32-bit input word. It emits the same number of words, in the same order. An empty input produces an empty output. The probe gives the proof, fixture, packaging, and backend checks a concrete operation while the kernel definition is open.
