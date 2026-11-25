# Worked kernel examples

Each program exercises the public Rust library on a small case with an independently known answer. Run any example from the repository root by passing its name to Cargo.

```sh
cargo run --locked --manifest-path examples/rust/Cargo.toml --example isogeny_graph
```

Every example prints the correct result and the effect of a deliberate error. A successful run means both matched the expected values.

| Cargo example | What it checks | Error it exposes |
| --- | --- | --- |
| [isogeny_graph](examples/isogeny_graph.rs) | Counts 2-isogenies between the two supersingular vertices in characteristic 11. The stationary probability flow is $2/5$ in each direction. | Keeping unique destinations loses parallel edges. The two flows become $3/10$ and $2/5$. |
| [unitary_hecke](examples/unitary_hecke.rs) | Evaluates the full normalization $u^{-1}q^{-k\lfloor r/2\rfloor}\sum v_i$ at $r=5,k=2,q=3,u=-2/3$ and checks additivity across split coset blocks ($-1/18$). | Multiplying $k\cdot r$ before halving gives $-1/54$ (off by $q=3$); dropping $u$ gives $1/27$. |
| [crystal_mesh](examples/crystal_mesh.rs) | Four representatives of an eight-point reciprocal mesh have multiplicities $1,3,3,1$. For the test values $0,1,4,9$, the reduced mesh reproduces the full-grid mean of $3$. | Giving each representative equal weight changes the mean to $7/2$. |
| [telemetry_coverage](examples/telemetry_coverage.rs) | Ten scenarios cover all 27 labelled assignments of healthy, stale, or silent states to three interchangeable telemetry lanes. | Omitting the scenario with three different states misses six labelled assignments. |
| [clifford_twirl](examples/clifford_twirl.rs) | Averaging a $1/8$ phase-flip error over 24 one-qubit Clifford frames gives error probability $1/24$ along each Pauli axis. | Replacing the Hadamard frame with a second identity preserves the frame count but changes the X and Z probabilities to $7/192$ and $3/64$. |
| [compiler_patterns](examples/compiler_patterns.rs) | Six canonical integer-add patterns on three registers expand to all nine ordered operand pairs. | Dropping the mixed pattern for registers 0 and 1 misses both operand orders. |

## How the checks work

**Isogeny graph.** The program finds the roots of the classical modular polynomial $\Phi_2(j,Y)$ modulo 11 at $j=1,0$. Root multiplicity counts edges. Averaging a destination indicator gives a transition probability. Normalizing the reciprocal automorphism orders gives the vertex weights used for the independent balance check. [Sage modular polynomial](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/mod_poly.html) · [Gross, §6](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf)

**Higher-rank normalized Hecke readout.** The other five examples set `k = 0`, which collapses the power factor to 1. `unitary_hecke` evaluates the full normalization $u^{-1}q^{-k\lfloor r/2\rfloor}\sum v_i$ at odd rank $r=5$, degree $k=2$, norm $q=3$, and central character $u=-2/3$. Because $k\lfloor r/2\rfloor = 4 \neq \lfloor kr/2\rfloor = 5$, it exposes integer-division order-of-operations bugs as well as a missing character factor, while verifying additivity across split coset blocks.

**Crystal mesh.** On an unshifted $2\times2\times2$ simple-cubic grid, a point has zero, one, two, or three half-coordinates. The example squares that count to obtain a test value. It checks each representative's multiplicity using the 48 symmetries of the cube, then compares the weighted mean with direct evaluation at all eight points—the classic Monkhorst–Pack irreducible Brillouin zone weighting (Monkhorst & Pack, 1976; Togo & Tanaka, 2018). The default run generates the mapping in Rust. To check an independent implementation, pipe the [spglib exporter](spglib_mesh.py) into the same program. [spglib reciprocal mesh API](https://spglib.readthedocs.io/en/stable/api/autodoc/spglib.kpoints.html)

```sh
uv run --no-project --with spglib==2.7.0 python examples/rust/spglib_mesh.py |
  cargo run --locked --manifest-path examples/rust/Cargo.toml --example crystal_mesh -- --stdin
```

The input has eight rows, one per point. Each contains two whitespace-separated integers from 0 to 7 giving the point and its representative. Bits 0, 1 and 2 mark half-coordinates along the x, y and z axes. The importer accepts any representative in the correct orbit.

**Telemetry and compiler coverage.** For distinct representatives with correct stabilizer orders, the group order times `class_mass` counts the original labelled cases. In formal verification this orbit-stabilizer accounting is the basis of symmetry reduction in model checking (Clarke et al., 1996; Emerson & Sistla, 1996; Ip & Dill’s Murphi scalarsets), and in compilers it underlies commutative canonicalization in e-graphs and superoptimizers. The telemetry example sorts lane states to identify equivalent scenarios and checks coverage against direct enumeration. Applying this reduction to a simulator requires both the simulator and its pass criterion to treat the three lanes interchangeably. The compiler example uses operand exchange as its symmetry and identifies the exact missing ordered pairs by expanding the surviving patterns.

**Clifford noise.** The simulator generates the group by composing the actions of the Hadamard and phase gates on the Pauli axes. After conjugation, a phase flip can land on X, Y, or Z. The program averages the rational error probabilities over frames using `hecke` with degree zero and the frame count as its divisor, illustrating exact Pauli/Clifford twirling as used in unitary 2-designs and randomized compiling (Wallman & Emerson, 2016). It uses the same averaging operation as the graph example. [Dankert et al., *Exact and Approximate Unitary 2-Designs*](https://arxiv.org/abs/quant-ph/0606161)
