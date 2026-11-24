# Prime-pair filter and prescribed-divisor curves

## Is the prime-pair search mathematically new?

### Takeaway

For any fixed auxiliary prime, the arithmetic search is through one reduced residue class. There is close precedent for the choice of a prime whose successor contains both an initial block of small primes and one larger prime. The separate bounded prime windows and the particular Lean bridge define the narrower workbench contribution.

### Cited findings

- Let $C=\prod_{3\le p\le B,\ p\ \mathrm{prime}}p$ and let $M=qC$. The local contract requires prime $q,d$, $B<q<d$, $q\equiv3\pmod8$, $d\equiv7\pmod{16}$, $M\mid d+1$, $\gcd(N,qd)=1$, and two specified lower-exclusive, upper-inclusive intervals. The concept card describes the single-progression search. [Local concept card](/Users/bharrington/Projects/software/lean/hecke-mass-kernel/proof_profile/research/batch-03/concepts/qh-prime-filter.md)
- With $M$ odd, $d+1=Mk$ and $d\equiv7\pmod{16}$ force $k\equiv8\pmod{16}$, since multiplication by any odd number fixes $8$ mod $16$. Hence $d\equiv8M-1\pmod{16M}$. This class is reduced because the residue is odd and equals $-1$ mod $M$. The algebra follows directly from the contract, and Mathlib already provides general coprime-modulus CRT constructions with uniqueness. [Local concept card](/Users/bharrington/Projects/software/lean/hecke-mass-kernel/proof_profile/research/batch-03/concepts/qh-prime-filter.md) · [Mathlib CRT](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/Nat/ChineseRemainder.html)
- Dirichlet's 1837 theorem gives infinitely many primes in each reduced class. Mathlib exposes `Nat.forall_exists_prime_gt_and_modEq`, which supplies a prime beyond any specified lower bound. Thus for fixed $B,N>0$ and with upper bounds dropped, first take a prime $q\equiv3\pmod8$ above $B$ and the prime divisors of $N$, then take a prime $d\equiv8M-1\pmod{16M}$ above $q$ and the prime divisors of $N$. This constructs infinitely many admissible $d$ for that $q$. [Dirichlet's original memoir, English translation](https://arxiv.org/abs/0808.1408) · [Mathlib's formalization](https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/LSeries/PrimesInAP.html#Nat.forall_exists_prime_gt_and_modEq)
- Linnik bounds the least prime in a reduced residue class in terms of its modulus. Xylouris (2018) establishes an admissible exponent $5$ in an upper bound of the form $c m^L$. This provides a size comparison for a fixed progression, while a bound on its first prime alone cannot certify a point in both prescribed windows, including each lower bound and the variable relation between $q$ and the modulus for $d$. [Xylouris, *Linniks Konstante ist kleiner als 5*](https://www.mathnet.ru/php/archive.phtml?jrnid=cheb&option_lang=eng&paperid=681&wshow=paper)
- CSIDH-512 (2018) chose a base-field prime $p=4(3\cdot5\cdots373)\,587-1$. The factor list is the first 73 odd primes plus the larger prime 587. CSURF-512 (2020) chose a base-field prime with $p+1=8$ times an explicitly prescribed odd product, therefore $p\equiv7\pmod{16}$. Both constructions use the selected odd prime divisors as available isogeny degrees. Bernstein, De Feo, Leroux and Smith give both numerical expressions in §6; Castryck and Decru are the primary source for CSURF. [Original CSIDH, IACR 2018/383](https://eprint.iacr.org/2018/383) · [Castryck and Decru, *CSIDH on the surface*](https://biblio.ugent.be/publication/8665496) · [Bernstein et al., ANTS XIV, 2020](https://msp.org/obs/2020/4-1/obs-v4-n1-p04-s.pdf)
- De Feo, Jao and Plût chose field primes $p=\ell_A^{e_A}\ell_B^{e_B}f\pm1$ to obtain supersingular curves with prescribed torsion over $\mathbf F_{p^2}$. This is older, related parameter engineering, with a different base field for the torsion. [Authors' paper source, parameters section](https://github.com/defeo/sidh-paper/blob/master/eprint.tex#L3155)

### Inferences

- The exact congruence package matters when identifying overlap. In CSIDH the constructed **field prime** is $3\bmod8$ because its successor has 2-adic valuation two. In this workbench the **auxiliary prime** $q$ is $3\bmod8$ and the constructed **field prime** $d$ is $7\bmod16$, giving $v_2(d+1)=3$. CSURF overlaps with the second property but does not supply the same auxiliary-prime congruence or interval contract in the sources reviewed.
- The search guarantees prescribed divisors. Full $B$-smoothness of $d+1$ is impossible under the stated $q>B$ condition. The odd cofactor can contain still larger unspecified primes.

### Gaps

- The literature reviewed did not establish priority for the exact conjunction of both prime windows, the two distinct residues, the odd primorial, the distinguished auxiliary prime, and coprimality with $N$. The sources support treating the workbench as a narrow certified instantiation of existing arithmetic rather than claiming a new prime construction theorem.

## Is the named supersingular curve and its point count new?

### Takeaway

The curve and the formula $\#E(\mathbf F_p)=p+1$ at primes $p\equiv3\pmod4$ are classical. The worked row and its machine-checked window remain useful reproducibility artifacts.

### Cited findings

- Bröker's 2009 primary paper names $E:y^2=x^3-x$ over $\mathbf Q$ as the CM curve for $\mathbf Q(i)$ and states that its reductions at primes $p\equiv3\pmod4$ are supersingular. This is also in his 2006 Leiden thesis, §3.5. For $p>3$, supersingularity over $\mathbf F_p$ is equivalent to trace zero and to $\#E(\mathbf F_p)=p+1$. [Bröker, *Constructing supersingular elliptic curves*, §2](https://gkorpal.github.io/files/broker-supersingular.pdf) · [Bröker thesis](https://math.leidenuniv.nl/scripties/Broker.pdf) · [Sutherland, MIT lecture 13, trace-zero corollary](https://ocw.mit.edu/courses/18-783-elliptic-curves-fall-2025/mit18_783_f25_lec_s_13.pdf#page=5)
- An elementary check works for this specific curve: with the quadratic character $\chi$ extended by $\chi(0)=0$, $x\mapsto-x$ negates $x^3-x$, and $\chi(-1)=-1$ for $p\equiv3\pmod4$. The character sum cancels, leaving $p+1$ after counting the point at infinity. This independently explains the reported result without running a supersingularity algorithm. [Bröker, §2, equation and residue class](https://gkorpal.github.io/files/broker-supersingular.pdf)
- Independently reran integer trial division up to each square root and an exhaustive point count with a histogram of all $y^2\pmod p$. Both 59 and 7079 are prime, with $59\equiv3\pmod 8$ and $7079\equiv7\pmod{16}$. For $N=77$, neither divides $N$. They lie in the reported windows $(16,256]$ and $(256,65536]$ at $B=5$. The successor is $7080=8\cdot(3\cdot5\cdot59)$, and the two exhaustive counts are $\#E(\mathbf F_{7079})=7080$ and $\#E(\mathbf F_{59})=60$. Also independently checked that all five benchmark example pairs in the conversation are prime and meet both residues and the prescribed divisor condition. This was a fresh arithmetic check, with the benchmark inputs taken from the local artifacts. [Local example and stated windows](/Users/bharrington/Projects/software/lean/hecke-mass-kernel/proof_profile/research/batch-03/concepts/qh-prime-filter.md) · [Independent workbench benchmark](/Users/bharrington/Projects/software/lean/hecke-mass-kernel/proof_profile/research/batch-03/benchmarks/qh-prime-filter/review.md)
- SageMath offers exhaustive counting and alternative independent methods through its finite-field `cardinality` API. PARI/GP offers `ellcard`. The same example can be tested with `EllipticCurve(GF(7079), [-1,0]).cardinality(algorithm='exhaustive')` in Sage. I ran the histogram algorithm rather than calling Sage. [Sage finite-field elliptic curves](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_finite_field.html#sage.schemes.elliptic_curves.ell_finite_field.EllipticCurve_finite_field.cardinality) · [PARI elliptic curves](https://pari.math.u-bordeaux.fr/dochtml/ref-stable/Elliptic_curves.html#ellcard)

### Inferences

- Since 59 is prime and divides $\#E(\mathbf F_{7079})$, Cauchy's theorem gives an $\mathbf F_{7079}$-rational point of order 59. The prime count proves this existence without asserting a generator or a cyclic structure for the entire group.

### Gaps

- Searches of the exact numbers did not turn up an earlier publication of the identical pair $(59,7079)$ for these windows. An apparent absence does not support a priority claim for an instance of the classical point-count formula.

## What is prior art for the checker and formal certificate?

### Takeaway

Lean already has libraries for CRT, reduced residue classes, and primality checking. The identifiable work here is the executable arithmetic predicate tied to the exact real-window floor hypotheses and an explicit witness, with a reproducible differential suite.

### Cited findings

- Pratt (1975) gave a proof system for succinct certificates of primality. Isabelle's Archive of Formal Proofs contains a 2013 proof of soundness and completeness and a certificate replay method. Mathlib provides `primality`, replaying Lucas/Pratt witnesses, alongside `norm_num` via least-factor evaluation. Bhavik Mehta's `PrimeCert` repository provides Lean 4 Pocklington certificate checking. These precedents cover individual primality proofs and do not address the workbench's specific floor bridge. [Pratt's original paper](https://epubs.siam.org/doi/10.1137/0204018) · [Isabelle AFP](https://isa-afp.org/entries/Pratt_Certificate.html) · [Mathlib primality tactic](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/Primality.html) · [PrimeCert](https://github.com/b-mehta/PrimeCert)
- The local evidence states that the executable Boolean has an empty axiom list, and that the bridge equates it to the specified arithmetic row and coprimality under certified floor inputs. Its named witness uses $z=8\log 2$ and $t=16\log 2$ to supply the five correct floors, then verifies the row. The reported 220 Lean/Python comparisons and 36,144 candidate checks are empirical tests of the implementation. [Window witness](/Users/bharrington/Projects/software/lean/hecke-mass-kernel/proof_profile/research/batch-03/benchmarks/qh-prime-filter/WindowWitness.lean) · [Local benchmark](/Users/bharrington/Projects/software/lean/hecke-mass-kernel/proof_profile/research/batch-03/benchmarks/qh-prime-filter/review.md)

### Inferences

- The defensible description is a verified executable finite-window checker plus concrete example. The certificate interface and audit can be cited independently of the known number-theory statements.

### Gaps

- I did not replay the Lean benchmark, and I found no public earlier implementation combining exactly this bounded pair predicate and these real-to-integer floor certificates. The arithmetic check and witness do not decide the full analytic `PairGood` predicate.
