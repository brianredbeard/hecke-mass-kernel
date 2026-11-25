# References and attribution

## Original Lean source

Alpöge, Levent. 2026. [Lean formalization of the Riemann Hypothesis and GRH for Dirichlet L-functions]. Original submission, 20 November 2026. Lean 4.33.1. Frozen mirror, commit `4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e`. Independently compiled and certified against Mathlib’s `RiemannHypothesis` by the Lean FRO, Mathlib Initiative, and Andrew Sutherland. The bracketed title is descriptive. [Author’s announcement and archive links](https://alpo.ge/remark.pdf) · [Lean community certification](https://leanprover-community.github.io/blog/posts/riemann-hypothesis) · [Andrew Sutherland’s verification record](https://math.mit.edu/~drew/grh/) · [Frozen `src/Main.lean`, theorem `riemannHypothesis`](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Main.lean#L4)

Alpöge describes working with Claude on the argument and formalization. [Alpöge’s account](https://alpo.ge/remark.pdf)

## Prior art

The arithmetic is classical. These are the public sources the documentation relies on.

- Gross, Benedict H. 1987. *Heights and the special values of L-series*. Sections 1, 2 and 6 give the level-11 Brandt matrices, the unit-group weights and the mass. [PDF](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf)
- Kirschmer, Markus, and John Voight. 2010. *Algorithmic enumeration of ideal classes for quaternion orders*. Remark 7.5 uses the mass to stop an enumeration. [arXiv:0808.3833](https://arxiv.org/pdf/0808.3833)
- Greenberg, Matthew, and John Voight. 2014. *Lattice methods for algebraic modular forms on classical groups*. Section 2 gives the finite coset-sum formula for a Hecke operator. [arXiv:1209.2460](https://arxiv.org/pdf/1209.2460)
- Martin, Kimball, and Satoshi Wakatsuki. *Mass formulas and Eisenstein congruences in higher rank*. Equations (2.2) and (2.5) give the mass of a finite class set and the Hecke action on functions on that same set. [Section 2](https://arxiv.org/pdf/1907.03417#page=6)
- Johansson, Fredrik, et al. *FLINT: Fast Library for Number Theory* (`fmpq` and binary-splitting / product-tree summation, after Brent 1976 and Haible–Papanikolaou 1998). [FLINT binary splitting](https://flintlib.org/doc/algorithms/integers/binary-splitting.html)
- Ho, Son, and Jonathan Protzenko. *Aeneas: Rust verification by functional translation* (Lean 4 backend for verifying safe Rust directly against Lean specifications, alongside Fiat-Crypto and HACL*/Eurydice). [Aeneas](https://lean-lang.org/use-cases/aeneas)

The [prior-art report](research/prior-art/README.md) compares the replayed values with published tables. The [novelty assessment](research/kernel-novelty/README.md) compares the extraction and proof trace with earlier work.

## What this repository adds, and how to check it

The frozen source gives both finite formulas. This repository traces a dependency path from `riemannHypothesis` to each definition, publishes formal upstream equivalence bridge theorems in [`bridge/UpstreamEquivalence.lean`](../bridge/README.md), and gives a standalone zero-dependency Lean specification with replayable C and Rust implementations. Readers can check the source analysis, the Lean proofs, and the arithmetic separately.

- [The specification](specification.md) links the two original definitions.
- [The dependency paths](dependency-paths.md) link the source line for every step from `riemannHypothesis` to each definition.
- [The write-up](primitive-in-the-proof.md) links the theorems that use them.

The definitions and paths were located with our own exploratory scripts over the compiled formalization. Those scripts and their intermediate records are not published and nothing here relies on them.
