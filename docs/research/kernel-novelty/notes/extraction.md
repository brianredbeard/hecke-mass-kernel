# What the extraction establishes

## Who first supplied these particular formulas?

### Takeaway

The frozen formalization itself explicitly states both finite formulas. This repository's identifiable design choice is to stop at the point where someone has already supplied and justified the data, specialize to rationals, and give both operations an executable interface.

### Cited Findings

- Upstream `classMass` is a real-valued sum over a double-coset class set. Its theorem `classMass_eq_sum_of_bijective` already rewrites it as a finite sum of inverse stabilizer cardinalities given bijective representatives. [Definition and theorem, lines 28–49](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Development/AbelianVarietyTheory/Definitions/Foundations/ClassMassEqSumOfBijective.lean#L28-L49)
- Upstream `Setup.hecke` is a complex linear operator. The adjacent `hecke_apply` gives the full pointwise normalized sum, including the inverse character value and exponent with natural-number division by two. [Definition and evaluation theorem, lines 62–71](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Development/AbelianVarietyTheory/Definitions/NonGaloisDescent/AdmQAdmissibleConjugatePairPlaces.lean#L62-L71)
- Both standalone definitions use the same ordinary fraction-list addition fold. Mass maps reciprocals over orders before the fold. Hecke scales the fold of function values. [Local definitions](../../../../lean/HeckeMassKernel/Finite.lean#L28-L66)

### Inferences

- Claiming discovery of either reduction, its scaling exponent, or a new mathematical relation between mass and operator would overstate the result. Their inputs represent different objects. The same summation routine and data-validation boundary suffice for the two evaluations.

### Gaps

- A source comparison can establish attribution and a concrete contribution here. It cannot establish that nobody previously selected these same two declarations for analysis.

## What did the proof audit reveal?

### Takeaway

The strongest project-specific finding answers a question one cannot settle just by reading classical number theory. The frozen root reaches these particular definitions, and the two arithmetic expressions enter the development in distinct roles.

### Cited Findings

- The repository records one path with 15 declaration-body links to mass and one with 19 to Hecke. They share the first nine named declarations, and the latter count includes a compiler-generated proof auxiliary. The authors restrict their public claim to existence of the displayed paths. [Source-linked proof paths](../../../dependency-paths.md)
- On the mass branch a double-coset decomposition feeds the identity identifying volume and mass under the theorem's hypotheses. On the Hecke branch `HeckeAt` specifies a target form's readout for each admissible datum, and `heckeTieT` transfers compatibility across a copied setup. [Volume theorem](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Development/AbelianVarietyTheory/Proofs/IwasawaDecomposition/VolumesEqMassesOfUnfold.lean#L12-L19) · [Readout condition](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Development/AbelianVarietyTheory/Definitions/NonGaloisDescent/AdmQAdmissibleConjugatePairPlaces.lean#L75-L85) · [Transport theorem](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Development/AbelianVarietyTheory/Proofs/IwasawaDecomposition/ClassSumEq.lean#L204-L208)

### Inferences

- The paths document a fact about a particular version of a formal argument. They do not establish that its proof needs these arithmetic operations in any alternative derivation or evaluates the level-11 fixtures at all. The case study can stand independently of the status of the headline result.

### Gaps

- The public write-up supplies source-line witnesses for readers. Its references say the exploratory scripts and intermediate records were not published, so the public evidence supports the displayed paths without relying on global shortest-path or completeness claims. [Provenance](../../../references.md)

## How much verification travels with the extraction?

### Takeaway

Readers gain a reproducible specification and a shared oracle for supplied data. The new Lean theorems in the standalone project cover recursive equations, evaluation, and fixed rational examples. They do not certify the representatives, a faithful translation of the parent development, or both native implementations for every input.

### Cited Findings

- The two mass recursion equations follow by definitional equality. The Hecke theorem unfolds the fold and justifies the implementation of the exponentiation shortcut. Concrete cases are checked by decision. [Proofs](../../../../lean/HeckeMassKernel/Finite.lean#L59-L79)
- The upstream interpretation requires complete representatives, correct stabilizer orders or function values, matching normalization and appropriate geometric data. The standalone project explicitly says equivalence to the upstream definitions has not been proved here. [Specification](../../../specification.md)
- CI compares outputs from Lean with checked-in fixtures and C and Rust replay each arithmetic row through their public APIs. An RVV test concerns the scaffold probe. [Verification](../../../verification.md)

### Inferences

- This is original work of transcription, proof analysis, testing and exposition. Its novelty lies in which evidence has been assembled about this formalization. None of the cited results establish a new arithmetic algorithm, complexity improvement or number-theoretic theorem.

### Gaps

- The review checked the local statements and the pinned original formulas and use sites. It did not reconstruct the whole compiled proof graph.
