# Kernel specification

The kernel evaluates two exact rational expressions from finite tables.

| Operation | Inputs | Result |
| --- | --- | --- |
| Class mass | Natural stabilizer orders $d_i$ | $\sum_i d_i^{-1}$ |
| Hecke coefficient | Rational character value $u$, natural parameters $q,k,r$, rational samples $v_i$ | $u^{-1}(q^{k\lfloor r/2\rfloor})^{-1}\sum_i v_i$ |

Arithmetic follows the extracted Lean model. Fractions have positive denominators and are reduced to lowest terms during evaluation. Inversion maps zero to zero, powers use $0^0=1$, and an empty sum is zero. All three implementations use balanced pairwise summation and short-circuit exponentiation when $u=0$, $q=0$ with positive exponent, or $\sum_i v_i=0$.

A geometric interpretation requires certificates about the supplied input. For a class mass, the orders must belong to a complete set of inequivalent classes and count their stabilizers. For a Hecke coefficient, the samples must come from the appropriate coset representatives and function values, with the matching local parameters and character. In the level-11 example Gross gives stabilizer orders $2,3$ modulo the central sign. The full orders are $4,6$, so the kernel returns $1/4+1/6=5/12$. [Gross, §§1 and 6](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf)

Alpöge gives both finite formulas explicitly. The theorem `classMass_eq_sum_of_bijective` expresses `classMass` as a sum over a complete list of representatives. The theorem `hecke_apply` gives the pointwise formula for `Setup.hecke`, including its normalization. The standalone Lean file specializes these expressions to rational inputs with zero external dependencies, and `bridge/UpstreamEquivalence.lean` provides the formal bridge theorems proving equivalence to the upstream definitions when checked against the pinned Lean 4.33.1 parent repository. [Upstream mass theorem](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Development/AbelianVarietyTheory/Definitions/Foundations/ClassMassEqSumOfBijective.lean#L44-L49) · [Upstream Hecke formula](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Development/AbelianVarietyTheory/Definitions/NonGaloisDescent/AdmQAdmissibleConjugatePairPlaces.lean#L62-L71) · [Standalone Lean definitions](../lean/HeckeMassKernel/Finite.lean) · [Upstream bridge](../bridge/README.md)

## Scaffold probe

The scaffold applies a bitwise exclusive OR with `0xa5a5a5a5` to each unsigned 32-bit input word. It emits the same number of words, in the same order. An empty input produces an empty output. The portable and RISC-V Vector backends use this probe to test the build and replay the same Lean-generated inputs. The C library uses GMP for the two rational operations. [Library integration](integration.md)
