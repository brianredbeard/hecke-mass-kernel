# Executable reference and computational precedents

## What does Lean establish?

### Takeaway

The standalone, executable specification makes an explicit choice about where the supplied mathematical data ends and rational arithmetic begins. Its proofs cover that small latter part.

### Cited Findings

- Both definitions use `Frac.sum`, a right fold with fraction addition and identity zero. Mass maps orders to reciprocals before the fold. Hecke scales the sum by two inverse factors after it. The generic mass equations are definitional (`rfl`). `hecke_formula` unfolds the implementation and rewrites the zero/one power shortcut. Three example theorems check concrete numerical equalities by decision. [Lean source](../../../../lean/HeckeMassKernel/Finite.lean)
- The rational specialization uses a custom numerator and positive denominator. The specification explicitly describes the comparison with upstream as a reading of the definitions. The source has no general theorem that this fraction implementation realizes upstream field arithmetic. Geometric certification of orders, representatives and samples remains a separate obligation. [Kernel specification](../../../specification.md) · [Lean source](../../../../lean/HeckeMassKernel/Finite.lean)

### Inferences

- Calling the result an extracted *interface* or *standalone restatement* is accurate. Claiming a machine-checked extraction from upstream would overstate the formal link. The shared fold has value as a code observation in a named project. It has no apparent claim to mathematical priority.

### Gaps

- The reviewed evidence does not establish priority among all proof assistants for a particular choice of executable interface.

## Which computation already existed?

### Takeaway

Sage already gives the two pieces together in the same level-11 series, a particularly direct comparison.

### Cited Findings

- In Sage’s `BrandtModule(11).brandt_series(5)` example, the constant coefficients down either column are (1/4) and (1/6). The coefficient of (q^2) is the matrix with rows ((1,3)) and ((2,0)). The same manual returns monodromy weights ((2,3)), explicitly counting half the units. [Sage Brandt series](https://doc.sagemath.org/html/en/reference/modfrm/sage/modular/quatalg/brandt.html#sage.modular.quatalg.brandt.BrandtModule_class.brandt_series) · [Sage monodromy weights](https://doc.sagemath.org/html/en/reference/modfrm/sage/modular/quatalg/brandt.html#sage.modular.quatalg.brandt.BrandtModule_class.monodromy_weights)
- The explainer's full-unit mass is (1/4+1/6=5/12). Its matrix written with source classes along rows is the transpose of the displayed Sage series coefficient. [Explainer source](../../../manim/what_the_kernel_computes.py)

### Inferences

- Coexistence of stabilizer weights and Hecke coefficients in a computational object has direct prior art. Sage also constructs the ideals in its level-11 example, while the repository's native API takes precomputed finite tables. [Sage cyclic submodules](https://doc.sagemath.org/html/en/reference/modfrm/sage/modular/quatalg/brandt.html#sage.modular.quatalg.brandt.BrandtModule_class.cyclic_submodules)

### Gaps

- Sage's concrete example settles precedent for this example and paired computation. It does not establish that all of Alpöge's normalizations are identical to this particular Sage module's.

## What does the software contribute?

### Takeaway

The test corpus, interoperable implementations, and explicit accounting of proof obligations are original deliverables here. The general idea of deriving tests from a theorem-prover specification is established.

### Cited Findings

- The C library uses GMP. Rust uses arbitrary-precision integer and rational types. The two independently written libraries consume a common fixture format through public API tests. The RISC-V vector code exercises an XOR integration probe. [C source](../../../../c/src/kernel.c) · [Rust source](../../../../rust/src/lib.rs) · [Verification](../../../verification.md)
- Lean checks 270 matrix entries against recorded expectations by turning recorded destinations into target indicators with (u=1, k=0). It also checks eight full/projective or Hermitian mass cases. These are executable fixture checks. Additional synthetic inputs cover the general normalization and edge semantics. [Fixture generator](../../../../lean/HeckeMassKernel/ReplayedCases.lean) · [Synthetic cases](../../../../lean/KernelVectors.lean) · [Replay scope](../../../replayed-cases.md)
- Brucker and Wolff (2009) already generated concrete test data and test drivers for implementations from Isabelle/HOL specifications, using a more general testing framework. [Authors’ paper](https://brucker.ch/publications/brucker.ea-hol-testgen-2009/)

### Inferences

- The interface is useful for reproducing finite arithmetic independently of the original environment. Agreement on finite examples gives conformance evidence and leaves general native correctness and the provenance of the geometric input open.

### Gaps

- The evidence reviewed supports crediting repository-specific choices. It cannot date a first-ever Lean/C/Rust package for such computations.
