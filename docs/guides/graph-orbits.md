# Audit graph-generator coverage with nauty

## 1. The bug this catches

The 11 unlabeled simple graphs on four vertices cover all 64 labeled graphs.
Removing the empty graph drops one labeled graph because its stabilizer has
order 24. The audit returns `missing covered=63 deficit=1`. An asymmetric
graph on nine vertices would contribute `9! = 362880` labeled graphs.

## 2. Export the stabilizer orders

Run from the repository root with Rust and nauty installed. On Ubuntu the
commands are named `nauty-geng` and `nauty-countg`; a source build names them
`geng` and `countg`. The CLI reads one positive decimal integer per line.
`countg -V --a` prints an automorphism group order for each graph. [nauty and Traces manual](https://pallini.di.uniroma1.it/Guide.html)

```bash
set -euo pipefail
nauty-geng -q 4 | nauty-countg -q -V --a |
  awk -F'groupsize=' 'NF == 2 && $2 ~ /^[1-9][0-9]*$/ { print $2; next } { exit 2 }' |
  cargo run --quiet --locked --manifest-path cli/Cargo.toml -- orbits --group-order 24 --expected 64
```

Expected output is `complete covered=64 deficit=0`. For an unrestricted
simple graph run on $n$ vertices, pass group order $n!$ and expected total
$2^{\binom n2}$. For a run restricted to exactly $m$ edges, use
$\binom{\binom n2}{m}$ as the expected total.

For a Python replay using automorphism groups from pynauty, see the
[pynauty notebook](../../python/examples/pynauty_orbits.ipynb).

## 3. Put it in CI

Install the `nauty` package in the runner and put the pipe above in a Bash
step. To exercise the missing-orbit path, save the adapter's orders to a file
and delete one of the two lines containing `24`. The CLI returns exit code 1
for a deficit or surplus and 2 for malformed input. `pipefail` propagates
errors from the upstream tools.

## 4. Interpret the result

The sum $\sum_i n!/|\operatorname{Aut}(G_i)|$ measures represented labeled
graphs. An equal total certifies coverage when the representatives lie in the
specified family, are pairwise non-isomorphic, and have the supplied
automorphism orders. A missing orbit and a duplicate of the same size can
cancel, so keep the generator's isomorphism checks.

## 5. Scaling and precision

The CLI consumes orders incrementally and retains at most logarithmically many
partial sums. Rational bit sizes still depend on the input denominators. To
see the precision difference with a synthetic table, pass a single order
`1`, group order `2432902008176640000` ($20!$), and expected total
`2432902008176640001`. The CLI reports an exact deficit of one, even though
those last two numbers round to the same binary64 value.
