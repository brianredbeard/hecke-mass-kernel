# Level-11 Brandt computation and finite Hecke arithmetic

## Which level-11 results were already known?

### Takeaway

Gross published the exact level-11 example in 1987, including the same \(T_2\) matrix, stabilizer orders up to central sign, \(5/12\) mass normalization, and eta product for \(X_0(11)\). The 24 good-prime coefficients are reproducibility targets for the workbench.

### Cited Findings

- Gross, *Heights and the Special Values of L-series* (1987), §6, pp. 146–147, prints \(B(2)=\left(\begin{smallmatrix}1&2\\3&0\end{smallmatrix}\right)\) in the same order as the workbench. He prints \(B(0)\), whose two rows are \((1/4,1/6)\), and the first \(B(n)\) through \(n=5\). Gross's §1 defines \(w_i=\#(R_i^\times/\{\pm1\})\), so \(w_1=2,w_2=3\) mean full orders \(4,6\). Eichler's formula for the quotient weights is \(\sum_i1/w_i=(11-1)/12=5/6\). Dividing by two for the full-order convention gives \(5/12=1/4+1/6\), also printed as the Eisenstein constant term. [Gross, §1 and §6](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf)
- Gross's equation (6.4) gives the full product \(q\prod_{m\ge1}(1-q^m)^2(1-q^{11m})^2=\eta(\tau)^2\eta(11\tau)^2\) and identifies the curve as \(y^2+y=x^3-x^2-10x-20\). Proposition 2.7 gives Brandt row sums and weighted symmetry. Sugiyama documents his use of the matrices transposed relative to Gross in his level-11 example. [Gross, Prop. 2.7 and §6](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf) · [Sugiyama, Example 4.1](https://arxiv.org/pdf/1904.08581)
- Cremona's modular-symbol work computes the level-11 curve and lists 11A1 in tables with Frobenius traces at primes below 100. LMFDB identifies Cremona 11a1 with 11.a2 and links the model of \(X_0(11)\) to newform 11.2.a.a. LMFDB authors report cross-checking modular-symbol and explicit-trace-form data for \(Nk^2\le4000\), including \(N=11,k=2\). [Cremona, Ch. I](https://johncremona.github.io/book/chapter1.html) · [Cremona, appendix to Ch. II](https://wstein.org/edu/Fall2003/252/references/cremona-algs/Cremona-Algorithms_for_modular_elliptic_curves.pdf) · [LMFDB curve](https://www.lmfdb.org/EllipticCurve/Q/11/a/2) · [LMFDB newform](https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/11/2/a/a/) · [Best et al., verification](https://jvoight.github.io/articles/cmfs-mf-101222-scrubbed.pdf)

### Inferences

- The published \(B(2)\) has eigenvalues \(3,-2\). Over \(\mathbf F_2\), both \(y=0,1\) satisfy the equation for both \(x=0,1\). The four affine points and the point at infinity give \(a_2=2+1-5=-2\).
- I expanded Gross's product to degree 97 and enumerated all affine points on Gross's curve equation for the primes in the local workbench record, adding one point at infinity each time. Both computations matched all 24 recorded coefficients. In increasing prime order \(2,3,5,7,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97\), these are \(-2,-1,1,-2,4,-2,0,-1,0,7,3,-8,-6,8,-6,5,12,-7,-3,4,-10,-6,15,-7\). The arithmetic also gives \(2\sum_p(p+1)=2146\), consistent with one enumerated neighbor per projective line, per ideal class. [Published product and curve](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf)
- In Gross's convention every good-prime matrix follows from \(a_p\) and the published matrix identities. Write its rows as \((p+1-x,x)\) and \((y,p+1-y)\). Weighted symmetry gives \(3x=2y\) and the second eigenvalue is \(a_p=p+1-x-y\). Thus \(x=2(p+1-a_p)/5\), \(y=3(p+1-a_p)/5\). The individual neighbor witnesses can carry verification evidence beyond the classical matrices. [Gross, Prop. 2.7 and Eq. (6.4)](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf)

### Gaps

- I reproduced point counts and the product independently. I did not replay individual lattice witnesses or rerun release checks. The number of replayed witnesses is attributed to the project record.

## What precedes the algorithm and finite arithmetic kernel?

### Takeaway

Computing Brandt matrices by quaternion ideals and neighbors, checking completeness by mass, and evaluating Hecke operators as finite sums over cosets all have direct precedents. A separable Lean/C/Rust arithmetic package is an implementation contribution.

### Cited Findings

- Pizer (1980) gave an implementable algorithm for quaternionic theta-series subspaces and Hecke matrices. Magma documents Kohel's implementation inspired by Pizer and the Mestre–Oesterlé supersingular graph method, with a path that stores the ideal basis and computes degree-\(p\) homomorphisms as needed. [Pizer, *An algorithm for computing modular forms on Γ₀(N)*](https://doi.org/10.1016/0021-8693(80)90151-9) · [Magma implementation history](https://www.math.uzh.ch/sepp/magma-2.18.5-cr/html/text1505.htm) · [Magma Brandt module creation](https://www.math.uzh.ch/sepp/magma-2.19.3-cr/html/text1551.htm)
- Sage documents exact level-11 cyclic submodules with three explicit right-ideal neighbors at \(p=2\). It supports direct cyclic-subideal Hecke matrices and a theta-series alternative, and describes enumerating all classes by neighbor iteration and ideal equivalence testing. [Sage Brandt modules, cyclic submodules and Hecke matrix options](https://doc.sagemath.org/html/en/reference/modfrm/sage/modular/quatalg/brandt.html)
- Kirschmer–Voight's §7 gives ideal-class enumeration by neighbors and inequivalence testing. Remark 7.5 explicitly substitutes the already enumerated reciprocal-unit-index mass for a class-number stopping test, using the identity in Remark 5.2. §8 checks class-number calculations and enumeration against each other. Magma documents using Kirschmer–Voight for ideal-class routines. [Kirschmer–Voight, *Algorithmic enumeration of ideal classes for quaternion orders*](https://arxiv.org/pdf/0808.3833) · [Magma Ideal Theory of Orders](https://docs.magma-maths.org/Algebras/QuaternionAlgebras/ideal-theory.html)
- Greenberg–Voight give additive coset evaluation \((Tg)f(x)=\sum_j f(xg_j)\) for a disjoint right-coset decomposition. They compute matrices by identifying neighbors with representative classes and recording group elements witnessing that identification. The finite kernel's particular scale \(u^{-1}(q^{k\lfloor r/2\rfloor})^{-1}\) and zero conventions belong to its API. [Greenberg–Voight, *Lattice methods for algebraic modular forms on classical groups*, §§2, 6](https://arxiv.org/pdf/1209.2460) · [Finite kernel specification](../../docs/specification.md)

### Inferences

- The completeness implication “a partial list of distinct, correctly weighted classes has the full positive mass, hence is exhaustive” is the logic of the prior mass stopping test. Lean checks that implication in the workbench. The full weights, class identities, and application of Eichler's theorem are separate inputs.
- The package's potential contribution is its precise finite contract, formal proof boundary, cross-language implementation and interoperable evidence. Established algorithms already compute the same classes, matrix entries and eigenvalues.

### Gaps

- I found no closely matching reusable Lean/C/Rust split implementation of this specific finite arithmetic contract. Search coverage is insufficient for a priority claim.

## Which parts of the verification workflow may be distinctive?

### Takeaway

Exact independent verification and cross-method eigenvalue checks have precedents. The specific level-11 neighbor certificates plus Lean arithmetic and stopping implication may distinguish this workbench as an artifact.

### Cited Findings

- Hung Dang's 2026 Richelot–Brandt work is a close computational analogue in a different, genus-two setting. It separates graph generation and split-side modular calculations, archives weighted matrices and other certificates, and replays exact spectral identities. It illustrates a related verification structure without establishing the same per-neighbor certificate format or a Lean proof. [Dang, *The Richelot isogeny graph and paramodular forms of weight 3*, §§7.1–7.7](https://arxiv.org/pdf/2608.14145) · [Accompanying artifact](https://github.com/dangthanhhung/richelot-brandt)
- Birkbeck's Lean strong-multiplicity-one project gives proof-assistant precedent for Hecke rings and coefficient/eigenvalue relations. It addresses a different theorem and provides no evidence of a level-11 quaternion neighbor replay. [Strong Multiplicity One Lean blueprint](https://cbirkbeck.github.io/AINTLIB-blueprints/smo/)
- The workbench records that external quaternion mass and Brandt correspondence specialization to its adelic setting remains unformalized. The repository Lean source proves finite formula and example results, and the C/Rust checks compare finite fixtures. [Lean verification scope](../../docs/verification.md)

### Inferences

- Defensible description: “A reproducible level-11 implementation of classical Brandt arithmetic with independently replayable per-neighbor evidence, a Lean-checked conditional stopping implication, and cross-checks against direct point counts and the eta product.”
- Release links and hashes support artifact integrity. They provide different evidence from arithmetic replay, exact unit-group counts, and a proof that the specialization from quaternion theory is correct.

### Gaps

- Searches for theorem-prover-verified quaternion Brandt computations and independently replayable genus-one exact neighbor certificates did not establish a direct match. This does not prove priority. Date the workbench before asserting chronological precedence over the relevant 2026 Richelot artifact.
- Check the per-neighbor witness checker source before claiming it independently verifies coverage, class equivalence or non-equivalence. Published matrix entries cannot supply all those properties.
