# References and attribution

## Original Lean source

Alpöge, Levent. 2026. [Lean formalization of the Riemann Hypothesis and GRH for Dirichlet L-functions]. Original submission, 20 November 2026. Lean 4.33.1. Frozen mirror, commit `4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e`. The bracketed title is descriptive. [Author’s announcement and archive links](https://alpo.ge/remark.pdf) · [Frozen `src/Main.lean`, theorem `riemannHypothesis`](https://github.com/homeowmorphism/riemann-hypothesis-original/blob/4e8bb36faa8c9e3f1bda144ccf5a637f8b96066e/src/Main.lean#L4)

Alpöge describes working with Claude on the argument and formalization. [Alpöge’s account](https://alpo.ge/remark.pdf)

## Phase 2.1 analysis

Use a separate bibliography entry for the analysis. Fill in the analysts’ names and a version-specific DOI or permanent release URL for a public citation.

> [Analysis authors]. 2026. *Reverse engineering computational arithmetic in the original RH formalization*. Phase 2.1. Research report, Lean certificates, and verification artifacts. [Version-specific DOI or release URL].

Cite the research report for the extraction methods and mathematical experiments. Cite the Phase 2.1 verification receipt for exact test counts and transitive axiom footprints. The report is `docs/REVERSE_ENGINEERING_REPORT.md` and the receipt is `proof_profile/research/phase-02/release/verification.json` in the workbench source tree.

The factoring audit reports that it found no public-input factoring algorithm in the audited dependency paths.
