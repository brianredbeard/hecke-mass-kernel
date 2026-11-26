# Where the proof uses it

## Opening

[0:00 in the video](https://brianredbeard.com/blog/hecke-mass-kernel/where_the_proof_uses_it.mp4#t=0.000)

We followed two chains of references from the declaration named riemannHypothesis in Alpöge’s Lean source.

In the proof, the first enters a volume identity and the second a compatibility condition. This film traces both and checks the bridge.

## Sifting a 17-million-line graph

[0:15 in the video](https://brianredbeard.com/blog/hecke-mass-kernel/where_the_proof_uses_it.mp4#t=15.800)

The original archive spans 175,187 modules and reaches almost 1.5 million declarations from riemannHypothesis.

Raw caller counts put core Lean plumbing at the top. Filtering out boilerplate leaves small domain operations like classMass and hecke.

Reachability in that frozen build shows what this formalization actually routed through—not that every RH proof must go this way.

## Reading a source reference

[0:38 in the video](https://brianredbeard.com/blog/hecke-mass-kernel/where_the_proof_uses_it.mp4#t=38.700)

In the definition of HeckeAt, rd g is the value being specified. On the right, ρ.hecke applies the Hecke operator to rd f.

That reference gives one edge from HeckeAt to Setup.hecke. Watch where it sits in the two paths we traced.

## Two paths from the root declaration

[0:54 in the video](https://brianredbeard.com/blog/hecke-mass-kernel/where_the_proof_uses_it.mp4#t=54.667)

The highlighted reference ends the blue path. Both paths start at riemannHypothesis and share their first eight links.

From the fork, the amber branch reaches classMass in 15 links; the blue branch runs through heckeTieT and HeckeAt in 19.

## Mass becomes a volume identity

[1:11 in the video](https://brianredbeard.com/blog/hecke-mass-kernel/where_the_proof_uses_it.mp4#t=71.467)

In part 1, the masses of A and B filled a bar: 1/4 + 1/6 = 5/12.

The proof has the same picture with its own data: a volume cut into one piece per double-coset class, each of size 1 ÷ d.

The theorem volumes_eq_masses_of_unfold uses that decomposition: the volume equals the sum of the reciprocal symmetry orders.

And because every omitted class adds positive weight, matching the volume certifies that a list of classes is complete.

## Hecke becomes a compatibility condition

[1:41 in the video](https://brianredbeard.com/blog/hecke-mass-kernel/where_the_proof_uses_it.mp4#t=101.967)

Keep A’s three neighbours in view. Counting the B destinations gives the matrix entry 2.

Now read the function at the same neighbours. Its values are 2, −3 and −3. They give the new value at A, which is −4.

HeckeAt requires the target value to agree with the normalized neighbour sum for every certified local input.

The series construction copies that setup so it can match forms to series coefficients. heckeTieT carries the equality straight across.

## The formal bridge and replayed cases

[2:13 in the video](https://brianredbeard.com/blog/hecke-mass-kernel/where_the_proof_uses_it.mp4#t=133.067)

To check the arithmetic without compiling all 175,187 modules, the repo separates the standalone Lean kernel from a formal bridge.

The bridge ties the rational formulas to Alpöge’s exact definitions, while 270 replayed entries check row sums, detailed balance, and commutativity.

## What each sum does

[2:29 in the video](https://brianredbeard.com/blog/hecke-mass-kernel/where_the_proof_uses_it.mp4#t=149.367)

So that is where the two sums enter the proof. One identifies a volume and pins completeness.

The other specifies the value of a transformed form and survives transport into the series setup.
