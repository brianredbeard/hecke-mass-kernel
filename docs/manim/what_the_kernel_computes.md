# What the kernel computes

## Opening

[0:00 in the video](what_the_kernel_computes.mp4#t=0.000)

Two computations that look unrelated: mixing numbers between neighbours, and counting the solutions of an equation.

Both reveal the same number, −2. This video explains why, and shows the two small sums underneath.

## Part 1 of 4: fair counting

[0:14 in the video](what_the_kernel_computes.mp4#t=14.167)

Start with a square. Switch each corner on or off: 16 markings.

Rotating the square turns these four into each other. They are one pattern, seen from four sides.

Sorted by rotation, 6 patterns remain. A pattern's symmetries are the rotations that leave it unchanged, 'no turn' included.

Take one row: 4 copies, 1 symmetry. The product is 4, the number of rotations. That is true of every row.

So weigh each pattern by (1 ÷ symmetries), its share of the four rotations, and sum the weights.

The total is 16 ÷ 4 = 4, known before listing anything. This weighted count is called the mass.

Leave out this pattern and its weight disappears. The list now accounts for only 3 of the expected mass of 4.

That sum is the kernel's first function: hand it the symmetry counts and it adds their reciprocals as an exact fraction.

Number theory has the same problem with harder objects. Each has finitely many symmetries. We draw the first one found as A.

A classical formula fixes the total mass in advance: 5/12. A alone weighs 1/4, so something is still missing.

The search finds B, with 6 symmetries. 1/4 + 1/6 = 5/12. The total is reached.

Provided the classes are valid, distinct and correctly weighted, the list is complete. A and B stay with us from here on.

## Part 2 of 4: mixing over neighbours

[1:50 in the video](what_the_kernel_computes.mp4#t=110.367)

To picture a neighbour, start with an integer lattice. The marked point is the origin, with coordinates (0, 0).

At the prime 2, keep half the lattice, including the origin. The sum of any two retained points must also be retained.

Try the odd columns. Their spacing is regular, but the origin falls in the gap. This choice fails the sublattice test.

Three index-two sublattices qualify. Each keeps the origin and satisfies one of these parity rules.

The left grid models one prime. Each parity rule picks out one of its three neighbours at the prime 2.

Why three? Each rule says that some combination a·x + b·y is even. Mod 2 there are four pairs (a, b), and three of them are not zero.

For another prime p, ask that a·x + b·y be divisible by p. Doubling (a, b) gives the same rule, so at p = 3, 8 pairs make 4 rules.

In general: p² − 1 nonzero pairs, p − 1 per rule, so p + 1 rules. An object has p + 1 neighbours at the prime p.

So 'three neighbours at the prime 2' is 2 + 1. For our objects the rule holds at every prime except 11.

Now the real objects. Take one object of class A and build its three neighbours at the prime 2.

They are three different objects. But part 1 taught us to ask a second question: which class does each one belong to?

For A, one neighbour is equivalent to A itself and two are equivalent to B. Different objects can share a class.

Do the same for an object of class B: all three of its neighbours are equivalent to A.

The count of three came from the prime. These labels did not: an upstream computation has to build the objects and classify them.

Draw one arrow per neighbour, pointing at its class. Three arrows leave A and three leave B.

The loop at A does not mean 'do nothing'. Doing nothing would be a different picture, with a loop on every class.

The loop is a real step whose result is equivalent to A. None of B's three steps comes back to B, so B has no loop.

## The Brandt matrix

[4:17 in the video](what_the_kernel_computes.mp4#t=257.600)

Now turn the arrows into numbers. Each class has its list of three neighbours, already sorted into classes.

Build a table one cell at a time. Start at A. Mark each neighbour that lands on B: 0, 1, 1.

Add the marks, 0 + 1 + 1 = 2, and divide by a scale, here 1. That is one call of the kernel's second function.

Every other cell is another call. The finished table is known as the Brandt matrix. Assembling it is the caller's job.

There the scale was 1. In general it is built from parameters the caller supplies, and the samples need not be 0 or 1.

With nonzero k and odd rank—here 3 and 7—the floor picks 2^(3×3) = 512. Exact fractions in give an exact fraction out, never a rounded decimal.

Now connect the two functions. A counts B twice among its neighbours; B counts A three times. It looks lopsided.

Weigh each side by its mass from part 1: 1/4 × 2 = 1/6 × 3. This symmetry across the table is called detailed balance.

Call the two crossing counts n_AB and n_BA. Each has to be a whole number from 0 to 3. Two pairs satisfy the balance equation.

The table has an edge from A to B. That rules out (0, 0). The crossing counts must be 2 and 3, leaving one loop at A.

Put any numbers a and b on A and B, and mix. Because of that balance, the mass-weighted sum just triples.

So a weighted sum of zero stays zero. The patterns with that property are the multiples of 2 on A, −3 on B.

Keep A’s three destinations in place. Counting arrivals at B gives 0 + 1 + 1 = 2, one entry in the matrix.

Now give A the value 2 and B the value −3. On the same three destinations, the new values add to −4. That is the output at A.

From B, all three neighbours land on A, so the second output is 6. Compare the entire output vector with the one we put in.

Both coordinates are multiplied by −2. This common scale factor is the Hecke eigenvalue at the prime 2.

## Part 3 of 4: counting points on the curve

[6:40 in the video](what_the_kernel_computes.mp4#t=400.467)

Now the other side: an equation that appears to have nothing to do with our neighbour graph.

Work mod 2: x and y are 0 or 1, and even numbers vanish. The equation simplifies, leaving four pairs to try.

Both sides are 0 whatever you plug in, so all four pairs are solutions.

The completed curve has one more point, at infinity: 5 in all. An elliptic curve mod p has about p + 1 points.

Expected 2 + 1, found 5. The gap is −2: the same number the neighbour graph produced.

Why the same number? Both computations read one hidden object: a modular form of level 11, written here as a power series.

Call its coefficient of q² a₂. Both routes compute a₂ = −2: one as a scale factor, one from point counts. It is a theorem.

These bars compare curve counts with series coefficients. We computed the neighbour table only at p = 2.

They agree at every prime of good reduction: for this curve, every prime except 11. The neighbour side matches by theorem.

## Part 4 of 4: the software

[7:52 in the video](what_the_kernel_computes.mp4#t=472.400)

We used Gross’s table at level 11. The two classes A and B correspond to the supersingular elliptic curves mod 11, with j = 1 and j = 0.

Divide each mass by 5/12 to get its share. Starting at A, two of three edges cross. From B, all cross. Detailed balance holds at 2/5.

Now export each destination just once. From A, the chance of crossing drops to one half. Detailed balance breaks: 3/10 one way, 2/5 the other.

The Rust example finds these edges independently from Φ₂ mod 11. The detailed-balance check catches the lost edges immediately.

## Recap

[8:30 in the video](what_the_kernel_computes.mp4#t=510.367)

Counting B destinations gives the entry 2. Mixing the whole vector gives the factor −2, the same number we found by counting points.

Lean proves laws of the arithmetic on supplied tables. The next film traces both sums into Alpöge’s Lean source and the bridge.
