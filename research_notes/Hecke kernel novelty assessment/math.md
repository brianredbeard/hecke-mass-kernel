# Classical mathematics and computational precedents

## Did previous authors use the two finite sums together?

### Takeaway

Yes. A direct primary precedent defines both sums on consecutive pages of the same paper.

### Cited findings

- Martin and Wakatsuki describe the finite adelic double quotient, write its mass as the sum of reciprocal stabilizer orders in §2, Eq. (2.2), and define the Hecke operator by summing function values over representatives of a double coset in Eq. (2.5). They use mass divisibility to obtain congruences of Hecke eigenforms in Proposition 2.1. The manuscript appeared in 2019. [Martin and Wakatsuki, pp. 6–7](https://arxiv.org/pdf/1907.03417#page=6) · [Preprint record](https://arxiv.org/abs/1907.03417)
- Greenberg and Voight's published algorithm enumerates neighbors, assigns them to representative classes, and computes Hecke action in §6. Their Remark 6.1 explicitly uses mass to stop or cross-check enumeration. Sage documents an implemented level-11, prime-2 ideal-neighbor calculation and the Brandt module approach after Pizer. [Greenberg and Voight, §6](https://arxiv.org/pdf/1209.2460#page=22) · [Sage Brandt modules](https://doc.sagemath.org/html/en/reference/modfrm/sage/modular/quatalg/brandt.html)

### Inferences

- Both mathematics and the idea of using the operations in the same computational setting have clear predecessors. The common operation in this code is literally addition of table entries, implemented by a list fold. The mass takes reciprocals before summing over global classes. Hecke sums over local representatives and multiplies by a scalar. The different index sets, entries, and geometric meanings matter. [Finite.lean](../../lean/HeckeMassKernel/Finite.lean)

### Gaps

- Martin and Wakatsuki's Eq. (2.5) is unnormalized. The repository attributes its precise scalar to the source Lean definition. This comparison establishes priority for the two underlying constructions. [Specification and pinned upstream definitions](../../docs/specification.md)

## Which replay values have concrete precedents?

### Takeaway

The headline level-11 result and Gaussian masses serve well as checks on conventions.

### Cited findings

- Gross's 1987 level-11 example prints the same prime-2 matrix with rows (1,2) and (3,0). Projective group orders 2 and 3 give mass 5/6. Restoring the central signs yields the repository's full group orders 4 and 6 and mass 5/12. The other matrix eigenvalue besides the row sum 3 is −2, the published second coefficient of the level-11 newform. [Gross, §§1 and 6](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf) · [LMFDB newform 11.2.a.a](https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/11/2/a/a/) · [Repository comparison](../../reports/Prior%20Art%20for%20Finite%20Arithmetic.md)
- Schiemann's own Gaussian data files give 1/32 and 1/384 verbatim, alongside the identity Gram matrices, automorphism orders, and adjacency matrices of neighbor counts at the prime used there. [Gaussian rank two](https://www.math.uni-sb.de/ag/schulze/Hermitian-lattices/D-4/dim2) · [Gaussian rank three](https://www.math.uni-sb.de/ag/schulze/Hermitian-lattices/D-4/dim3)

### Inferences

- The published match is an independent reference for examples, with precise choices about full versus projective orders. The software's recorded tables may be useful reusable data even when the expected result is well known. [Replay scope](../../docs/replayed-cases.md)

### Gaps

- Exact published entry-by-entry matches for every level-23, level-37, and Hermitian operator in the package were outside this comparison. Recorded destination labels plus a matrix or spectrum do not certify the individual lattice neighbors. [Replay scope](../../docs/replayed-cases.md)

## What is distinctive about the abstraction?

### Takeaway

The design choice is to expose the computation remaining after a caller supplies the arithmetic geometry as tables. The ordinary finite sum itself offers no evidence of a new mathematical technique.

### Cited findings

- Both definitions call the same small `Frac.sum`. Their signatures require only natural stabilizer orders or rational samples and parameters. The package formally restates the two operations and checks native implementations on fixtures. Its documents expressly distinguish this from proving the correspondence to the pinned upstream statements or verifying the origin of the tables. [Finite.lean](../../lean/HeckeMassKernel/Finite.lean) · [Specification](../../docs/specification.md) · [Replayed cases](../../docs/replayed-cases.md)

### Inferences

- The new material one can point to is the *specific* extraction, evidence, and account of where the two definitions enter the pinned development. The prior art does not make that specific report redundant. It does undermine a general claim of discovering that mass and Hecke sums share finite-table arithmetic. An absolute first for this exact packaging cannot be inferred from this comparison.

### Gaps

- This comparison does not establish priority for the precise implementation, provenance analysis, or interface.
