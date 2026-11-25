# Where the proof uses it

## Opening

[0:00 in the video](where_the_proof_uses_it.mp4#t=0.000)

We followed two chains of references from the declaration named riemannHypothesis in Alpöge’s Lean source.

In the proof, the first enters a volume identity and the second a compatibility condition. This video follows each one in.

## Reading a source reference

[0:15 in the video](where_the_proof_uses_it.mp4#t=15.300)

In the definition of HeckeAt, rd g is the value being specified. On the right, ρ.hecke applies the Hecke operator to rd f.

That reference gives one edge from HeckeAt to Setup.hecke. Watch where it sits in the two paths we traced.

## Two paths from the root declaration

[0:31 in the video](where_the_proof_uses_it.mp4#t=31.267)

The highlighted reference ends the blue path. Both paths start at riemannHypothesis and share their first eight links.

The two paths shown have 15 and 19 links. What does each definition contribute to the argument?

## Mass becomes a volume identity

[0:47 in the video](where_the_proof_uses_it.mp4#t=47.367)

In part 1, the masses of A and B filled a bar: 1/4 + 1/6 = 5/12.

The proof has the same picture with its own data: a volume cut into one piece per double-coset class, each of size 1 ÷ d.

The theorem volumes_eq_masses_of_unfold uses that decomposition: the volume equals the sum of the reciprocal symmetry orders.

That sum is classMass. In the proof, mass identifies a volume.

## Hecke becomes a compatibility condition

[1:15 in the video](where_the_proof_uses_it.mp4#t=75.433)

Keep A’s three neighbours in view. Counting the B destinations gives the matrix entry 2.

Now read the function at the same neighbours. Its values are 2, −3 and −3. They give the new value at A, which is −4.

HeckeAt requires the target value to agree with the normalized neighbour sum for every certified local input.

The series construction copies the setup. The lemma heckeTieT carries the same equality across to the copy.

## What each sum does

[1:45 in the video](where_the_proof_uses_it.mp4#t=105.633)

So that is where the two sums enter the proof. One identifies a volume.

The other specifies the value of a transformed form. The same condition holds in the copied setup.
