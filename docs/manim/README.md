# Animations

These two silent films introduce the arithmetic without assuming any number theory. Each has on-screen narration, downloadable English WebVTT captions, and a chaptered transcript. [Manim Community](https://www.manim.community/)

## 1. What the kernel computes

[![Frame from the first explainer](what_the_kernel_computes.png)](https://brianredbeard.com/blog/hecke-mass-kernel/#what-the-kernel-computes)

[Play the film on the blog (8:48)](https://brianredbeard.com/blog/hecke-mass-kernel/#what-the-kernel-computes) · [Read the transcript](what_the_kernel_computes.md) · [Download WebVTT captions](what_the_kernel_computes.vtt)

The video opens with the result it builds toward: mixing numbers between neighbours and counting solutions of an equation both give −2. Each part then uses what the previous one produced.

| Part | Idea | Worked example |
| --- | --- | --- |
| Fair counting | Weight each pattern by 1 ÷ its symmetries. The total is known in advance, so reaching it certifies that a list of genuine, distinct classes is complete. | 16 corner markings of a square, 6 patterns, total $16/4=4$. Then level 11: $1/4+1/6=5/12=(11-1)/24$. |
| What a neighbour is | At the prime 2, keep an index-two sublattice. The marked origin explains why the odd columns fail. At a prime $p$, each rule $ax+by\equiv 0 \pmod p$ comes from a nonzero pair up to scaling, giving $p+1$ neighbours. | The three parity rules keep even $x$, even $y$, or even $x+y$. In the level-11 table, A's neighbours land in A, B, B and B's land in A, A, A. |
| Mixing over neighbours | Each kernel call computes one cell of the Brandt matrix, and the general normalization scales by $u^{-1}q^{-k\lfloor r/2\rfloor}$. Detailed balance links the masses to the matrix and singles out the pattern with mass-weighted average zero. Mixing scales it. | $\left(\begin{smallmatrix}1&2\\3&0\end{smallmatrix}\right)$, `hecke(3/4, 2, 3, 7, [1/2, 1/3, 1/6]) = 1/384`, $\tfrac14\cdot 2=\tfrac16\cdot 3$, so $3a+2b=0$ gives $(2,-3)\mapsto(-4,6)=-2\,(2,-3)$. |
| The equation | The same number is the baseline minus an elliptic curve's point count, because both sides read the coefficients of one modular form. | $y^2+y=x^3-x^2-10x-20$ has 5 points mod 2 and $2+1-5=-2$, the coefficient of $q^2$ in $q\prod(1-q^n)^2(1-q^{11n})^2$. |
| The software | The classes A and B match the supersingular curves $j=1,0 \bmod 11$. A graph exporter drops repeated destinations, breaking detailed balance. | The [Rust example](../../examples/rust/examples/isogeny_graph.rs) derives the edges from a modular polynomial. Correct flows are $2/5$ both ways. Deduplication changes the forward flow to $3/10$. |

The square is a teaching analogy, and the two-dimensional lattice is a model of what happens at one prime: the real objects are lattices in a four-dimensional quaternion algebra, and the $p+1$ count holds at every prime except 11. The scene enumerates the rules and asserts the count for the primes it lists. It also asserts that the balance $\tfrac14 a=\tfrac16 b$ with at most three arrows each way has the single crossing solution $a=2$, $b=3$. Which class each neighbour belongs to is not computed by this repository. The lists A, B, B and A, A, A are the rows of the level-11 matrix $B(2)$ that Gross prints. [Gross, §6](https://wstein.org/papers/bib/Gross-Heights_and_the_Special_Values_of_L-series.pdf) The level-11 data sits in one table at the top of the scene file, and the mass, the matrix, the balance identity, the pattern $(2,-3)$ and its eigenvalue are derived from it and asserted. The scene also counts the curve's points and expands the modular form's product independently and asserts that they agree at the primes shown. It reads the fixture count and the displayed fractional `hecke` row from `tests/vectors/kernel.tsv`. The class-side matrix is computed only at the prime 2; its agreement at other primes is the Eichler–Shimura and Jacquet–Langlands correspondence, which this repository does not compute.

Run the final graph check from the repository root:

```sh
cargo run --locked --manifest-path examples/rust/Cargo.toml --example isogeny_graph
```

## 2. Where the proof uses it

[![Frame from the second explainer](where_the_proof_uses_it.png)](https://brianredbeard.com/blog/hecke-mass-kernel/#where-the-proof-uses-it)

[Play the film on the blog (2:48)](https://brianredbeard.com/blog/hecke-mass-kernel/#where-the-proof-uses-it) · [Read the transcript](where_the_proof_uses_it.md) · [Download WebVTT captions](where_the_proof_uses_it.vtt)

The sequel opens on the same two worked calls, shows the scale of Alpöge's frozen 17.4-million-line archive (`175,187` modules, `1,478,219` reachable declarations) with the caveat that reachability is not logical necessity, follows each path into the formalization ([source and citations](../references.md)), and closes with the formal upstream bridge (`bridge/UpstreamEquivalence.lean`) and 270 replayed matrix entries beyond level 11.

| Definition | Dependency links below `riemannHypothesis` | What the proof does with it |
| --- | ---: | --- |
| `GlobalTheory.Mass.classMass` | 15 | Mass identifies a volume. `volumes_eq_masses_of_unfold` uses a double-coset decomposition to equate a volume with the sum of reciprocal symmetry orders. |
| `GlobalTheory.SeriesTie.Setup.hecke` | 19 | The Hecke sum specifies a readout that survives transport. `HeckeAt` requires a target readout to equal the normalized Hecke sum for every certified local input, and `SerCopy.heckeTieT` carries that condition to the copied setup used in the series construction. |

The film follows the reference from `HeckeAt` to `Setup.hecke`, then places that edge on the blue branch. Each link in both displayed paths has a corresponding line in the pinned source. [Source excerpt shown in the film](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Development/AbelianVarietyTheory/Definitions/NonGaloisDescent/AdmQAdmissibleConjugatePairPlaces.lean#L80) · [Written account](../primitive-in-the-proof.md) · [Dependency paths](../dependency-paths.md)

## Rendering

Requires Manim in the repository's `.venv`, a LaTeX installation, and ffmpeg. Run from the repository root.

```sh
uv pip install manim
sh docs/manim/render.sh
```

The script renders at 1920×1080 and 30 fps. It writes each H.264 video to
`build/manim/release/<film>/<film>.mp4` and copies the poster, WebVTT
captions and Markdown transcript next to the scene source. The captions
and transcript share the text and timing of the on-screen narration.
Chapter links seek directly into the blog-hosted videos. To render one
film, pass `what_the_kernel_computes` or `where_the_proof_uses_it` as the
script argument.
