# Review of the two Manim explainers

The strongest sequence in the first film turns the destinations A, B, B into three chips, an indicator sum, and a matrix entry. The strongest image in the sequel is the dependency path forking into the volume identity and the Hecke condition. Keep both. I would spend the next render on three mathematical corrections and a clearer handoff, then use the same graph to show a software bug a viewer can reproduce.

The timecodes and source locations below refer to the [scene sources for the reviewed 8:17 and 1:58 cuts](https://github.com/brianredbeard/hecke-mass-kernel/tree/291d3390011768fdd34c2444391ce5310a18c919/docs/manim). For the revised cuts, use the chapter links in the [arithmetic transcript](what_the_kernel_computes.md) and the [proof-trace transcript](where_the_proof_uses_it.md). The review covered decoded video frames, the README posters at reduced width, and the scene sources.

## Correct three frames in the first film

| Time | What the viewer sees | Suggested edit |
| --- | --- | --- |
| **1:05** | Removing a square pattern changes the total to 3 while the equation still reads $3=16\div4$. The subtitle correctly says the list is short. | Show **found 3 < expected 4** for the entire missing-row beat. When the pattern returns, restore the equals sign. This makes the failure visible even with the subtitles covered. |
| **2:05–2:25** | “Keep exactly half the points” in a regular grid leads to “exactly three ways.” Keeping odd columns also looks like a regular half-grid. | Mark the origin before the grid splits. Briefly try odd columns and show the marked origin disappearing. Explain that a sublattice here contains zero and is closed under addition. Then reveal even $x$, even $y$, and even $x+y$. |
| **5:24** | The balance equation goes from $3a=2b$ to $a=2,b=3$. The caption gives the upper bound of three. Zero crossings each way also satisfy that equation. | Show the two integer solutions within the bounds, $(0,0)$ and $(2,3)$. Highlight one observed crossing edge to eliminate the first. Label the counts $n_{AB},n_{BA}$ so that $a,b$ can denote vertex values in the next scene. |

[Fair-counting scene](https://github.com/brianredbeard/hecke-mass-kernel/blob/291d3390011768fdd34c2444391ce5310a18c919/docs/manim/what_the_kernel_computes.py#L529) · [Lattice scene](https://github.com/brianredbeard/hecke-mass-kernel/blob/291d3390011768fdd34c2444391ce5310a18c919/docs/manim/what_the_kernel_computes.py#L675) · [Balance scene](https://github.com/brianredbeard/hecke-mass-kernel/blob/291d3390011768fdd34c2444391ce5310a18c919/docs/manim/what_the_kernel_computes.py#L1244)

## Carry one row through both films

At **8:11 in part one**, the code card returns $2$ and the equation immediately below it ends in $-2$. At **1:14 in part two**, the same neighbours give $g(A)=-4$. All three values are correct. The viewer needs to see what changed. Hold the row **A, B, B** still and change only the labels on the chips:

| Question | Values on A, B, B | Answer |
| --- | --- | --- |
| How many neighbours land in B? | $0,1,1$ | $2$, the A-to-B matrix entry |
| What value does mixing give at A for $f=(2,-3)$? | $2,-3,-3$ | $-4$, the first output coordinate |
| What happens to the whole vector? | The B row gives $2+2+2=6$. | $(-4,6)=-2(2,-3)$, so the eigenvalue is $-2$. |

Use the first and last labels on the recap; replay the chip relabelling when the sequel introduces its target value. That gives “readout” a concrete meaning before the general formula appears. [First recap](https://github.com/brianredbeard/hecke-mass-kernel/blob/291d3390011768fdd34c2444391ce5310a18c919/docs/manim/what_the_kernel_computes.py#L1748) · [Hecke condition in the sequel](https://github.com/brianredbeard/hecke-mass-kernel/blob/291d3390011768fdd34c2444391ce5310a18c919/docs/manim/where_the_proof_uses_it.py#L402)

## Give the proof trace a source the viewer can follow

At **0:02 in part two**, “inside a machine-checked proof” reads as an endorsement of the headline theorem. The repository documents particular references in a frozen Lean development. Open with **“We followed two chains of references from the declaration named `riemannHypothesis` in Alpöge’s Lean source.”** At **0:20–0:38**, replace the schematic network and file count with one actual use site, such as `HeckeAt` referring to `Setup.hecke`. Highlight the reference in the source, then pull back to show where that edge sits on the blue branch. Label 15 and 19 as the lengths of the paths shown.

At **1:30–1:38**, the example, general formula, and two setup boxes are all on screen. Once the equality is established, fade the example and move the equality itself into the copied setup. That motion can carry the meaning of “survives transport.” [Dependency paths with source links](../dependency-paths.md) · [Sequel scenes](https://github.com/brianredbeard/hecke-mass-kernel/blob/291d3390011768fdd34c2444391ce5310a18c919/docs/manim/where_the_proof_uses_it.py#L130)

## Give the first film a runnable payoff

Use the existing isogeny example as a short replacement for part of the software recap. Keep the A/B drawing, identify its vertices in the supersingular example as $j=1,0$, and let a graph exporter accidentally discard the second B from A’s destination list. Now $P(A\to B)$ falls from $2/3$ to $1/2$. With normalized vertex weights $3/5,2/5$, the correct flow is $2/5$ each way; the faulty forward flow drops to $3/10$. Show those unequal values beside the two arrows, then show the runnable command.

```sh
cargo run --locked --manifest-path examples/rust/Cargo.toml --example isogeny_graph
```

This makes two sources of data explicit. The film starts from Gross’s supplied Brandt table. The Rust example recovers the matching multiplicities independently from roots of a modular polynomial modulo 11. A lost edge gives the viewer a reason to run the exact check themselves. [Isogeny graph example](../../examples/rust/examples/isogeny_graph.rs)

## Improve first impressions and playback

- **Replace both posters.** The first is taken at 1:50 during a fade; its diagram is nearly black at README width. Use the held two-route hook around 0:04. The second poster, at 0:45, shows the mass bar from the first film. Use the labelled dependency fork around 0:38 and size the endpoint labels for a thumbnail. [Poster extraction](https://github.com/brianredbeard/hecke-mass-kernel/blob/291d3390011768fdd34c2444391ce5310a18c919/docs/manim/render.sh#L24)
- **Make the silent narration searchable.** Both MP4s contain one video stream. The shared `say` method already holds the subtitle text and the scene clock. Export timed captions and a chaptered transcript from that data so a reader can jump to the matrix, point count, or proof branch. Describe the releases consistently as silent, captioned films and identify any separate edition that uses the credited music. [Caption helper](https://github.com/brianredbeard/hecke-mass-kernel/blob/291d3390011768fdd34c2444391ce5310a18c919/docs/manim/style.py#L113) · [Animation notes](README.md)
