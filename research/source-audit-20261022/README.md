# 25-bar source audit: area transcription and load units

**Kripka (2004), Table 4, method 6 prints A5 = 2.2 in²; the frozen repository transcription stores 2.1.** The source-transcribed vector reproduces 484.33 lb and passes the unchanged imperial reference model. A separate diagnostic taking Table 3's newton forces literally fails the displacement limit. These are two different findings: an identifiable area-transcription discrepancy and an unresolved interpretation of source load units.

This package adds evidence for maintainer review. It changes no frozen benchmark, tolerance, solver, frontier, ledger, or accepted result. Results remain **author-checked, AI-assisted**; no independent scientific or engineering review is claimed.

## Provenance and primary-source comparison

- Base commit: `d3a2a3da00c7cb329474470f9e112f0ac0d32cb1`.
- Frozen 25-bar model SHA-256: `5291c9023163d70b696d644923fc2ad94bcaf07984a6f037986f13035ef42328`.
- Donation seed: `232b9fe2013342d0308b72a1556a8437`. The hub selected bridge-truss with weight 3/51; its own picker selected `replication/source-audit`.
- Source: M. Kripka, *Discrete optimization of trusses by simulated annealing*, J. Braz. Soc. Mech. Sci. & Eng. 26(2), 170–173 (2004), [DOI](https://doi.org/10.1590/S1678-58782004000200008).

The [original Table 4 image](https://minio.scielo.br/documentstore/1806-3691/vZNDbfZ66DHqFZc3HPcrj4k/94c459eaed0555f014ce4ff81e33b9be4ff48c8b.gif) was visually inspected. Its SHA-256 is `57183e73e8df9f28dab365efd1403fbc745dd45f49ba3bd63030754c628915bd`, exactly the value already pinned in `docs/source-lock.json`. This finding does not depend on OCR or an inferred repair. The method-6 entries are:

```text
Group:        A1   A2   A3   A4   A5   A6   A7   A8
Table 4:     0.1  0.4  3.4  0.1  2.2  1.0  0.4  3.4   W = 484.33 lb
Repository:  0.1  0.4  3.4  0.1  2.1  1.0  0.4  3.4   attributed to the same row
```

Paper group 5 means array index 4. [Table 2](https://minio.scielo.br/documentstore/1806-3691/vZNDbfZ66DHqFZc3HPcrj4k/d1262fa65cf7ebd46adf7790d57a29a937418df5.gif) assigns it to endpoint pairs 3–4 and 5–6: repository members 12–13. All eight group mappings agree. The selected method-4 vector also agrees with Table 4. [Figure 2](https://minio.scielo.br/documentstore/1806-3691/vZNDbfZ66DHqFZc3HPcrj4k/2105cb285d7dd8fc370a85d16c9cf1aa04430967.gif) supports the frozen geometry, subject to the perspective drawing's symmetry/support interpretation.

The [25-bar prose](https://new.scielo.br/j/jbsmse/a/vZNDbfZ66DHqFZc3HPcrj4k/?ilang=pt_BR&lang=en) supports the frozen 30-value area catalogue, imperial modulus/density, 40-ksi stress limit, and 0.35-in X/Y limits at nodes 1 and 2. Its printed SI equivalent of 40 ksi is 257.6 MPa, another inconsistent unit conversion; this audit retains the frozen imperial material values. No author intent is inferred.

[source-transcription.json](source-transcription.json) records the relevant factual table entries, URLs, and retrieval hashes. Figure 2 and Tables 2–4 all match the existing source lock. The article HTML succeeded through `new.scielo.br`; the PDF route returned a security challenge and was not inspected. Raw publisher files remain outside the repository and are not redistributed.

## Unchanged-model numerical evidence

All rows below use the frozen `reference` profile. The A1/A4 alternatives change only the named group from the repository's rejected vector. Each verdict agrees between both implementations; the official `truss.verify.verify` entry point also accepts/rejects the five displayed witnesses as expected.

| Vector | Mass, lbm | Displacement utilization | Node 2 Y, in | Verdict |
|---|---:|---:|---:|---|
| Repository's A5=2.1 control | 482.828644196077 | 1.001716022371 | -0.350600607830 | reject |
| A1=0.3 alternative | 484.328644196077 | 1.001716022371 | -0.350600607830 | reject |
| A4=0.2 alternative | 484.328644196077 | 1.001716022371 | -0.350600607830 | reject |
| Source-transcribed A5=2.2 | 484.328644196077 | 0.999886515967 | -0.349960280588 | pass |
| Selected method-4 control | 485.048797450533 | 0.998587185980 | -0.349505515093 | pass |

The source-transcribed method-6 vector has only **0.0000397194 in** of raw displacement margin. Its stress utilization is about 0.154897. The original 2.1 vector is retained in [audit.json](audit.json), explicitly labeled `repository_disputed_control`, not described as the printed source vector.

The existing `results/25bar-reference-winner.json` has **exactly the same eight areas as the source-transcribed method-6 row**. The stored 0.1485% saving is relative to the selected method-4 baseline, not relative to this published method-6 vector. This audit supplies attribution/comparability evidence, not a new design or a mass improvement; the existing winner and its record are unchanged. The replay records the winner file's hash and checks this equality.

A complete check of the six directly transcribed Table 4 rows gives the following additional controls. All source vectors and full two-solver results are retained under `source_table4_all_methods` in `audit.json`.

| Table 4 method | Printed weight, lb | Computed mass, lbm | Displacement utilization | Frozen-reference verdict |
|---|---:|---:|---:|---|
| 1 | 487.41 | 487.405249552 | 0.997318169671 | pass |
| 2 | 546.01 | 546.012873132 | 0.994586162239 | pass |
| 3 | 562.93 | 557.711787365 | 1.001145158774 | reject |
| 4 | 485.05 | 485.048797451 | 0.998587185980 | pass |
| 5 | 539.78 | 539.777532692 | 0.985380804431 | pass |
| 6 | 484.33 | 484.328644196 | 0.999886515967 | pass |

Five rows match their own printed weights to the nearest hundredth. **Method 3 is a separate unresolved source-comparison discrepancy:** its directly printed vector computes 5.218212635 lbm below its printed weight and fails the frozen displacement check. Table 4 attributes that row to Zhu (1986); the original 1986 formulation was not inspected. This observation does not identify the historical cause, propose a repaired vector, or imply all prior formulations were identical. The original row is preserved.

The predeclared supporting sweep replaced exactly one of eight groups by each other catalogue value: **8 × 29 = 232** candidates. A mass match means lying in `[484.325, 484.335)` lbm, an explicit nearest-hundredth reporting convention. The source does not prescribe a rounding algorithm; no tested mass lies on an endpoint. There are 81 feasible replacements, three mass matches, and just one feasible mass match, A5=2.2. **Mass alone does not identify group 5.** The largest two-solver relative difference over the 232 candidates was below `7.5e-15`, against the unchanged `1e-8` agreement tolerance. Full arrays are retained for the five displayed witnesses, and summaries for all replacements.

The mass formula derived directly from the frozen geometry is:

```text
M(A) = 7.5 A1 + 5 sqrt(109) A2 + 5 sqrt(73) A3
       + 15(A4 + A5) + 5 sqrt(210)(A6 + A7) + 5 sqrt(114) A8.
```

A1: 0.1→0.3, A4: 0.1→0.2, and A5: 2.1→2.2 each add exactly 1.5 lbm. [check_mass_exact.py](check_mass_exact.py) independently derives member lengths from integer doubled coordinates, using integer square roots and rational arithmetic without importing either solver. It classifies all 232 masses with enclosure widths at most `2.32e-50` lbm. Every excluded mass is more than `0.74364419607749081316` lbm from the bin; [mass-exact.json](mass-exact.json) records exact rational bounds. This exact statement is about the finite mass classification, **not structural feasibility**. Widening the mass comparison to the existing 0.02-lbm source tolerance would not change the three matches.

The structural difference has a symmetry explanation. Reflection across Y=0 preserves groups/supports, splitting stiffness into even and odd subspaces. Top-node Y outputs belong to the odd subspace. A1 and A4 have zero extension in that entire subspace, so changing their positive areas leaves those outputs invariant, although they carry nonzero forces under the actual load. A5 affects that subspace. This explains why the equal-mass alternatives need not have equal displacement effects; it does not replace the numerical feasibility checks.

## Separate diagnostic: taking Table 3's newtons literally

**This section changes the loads. It is not a result under the frozen model, a complete SI reconstruction, or a proposed new accepted benchmark.** All other inputs retain their frozen imperial interpretation.

[Table 3](https://minio.scielo.br/documentstore/1806-3691/vZNDbfZ66DHqFZc3HPcrj4k/34bb76069c05c044f63b95a043136f81a4bdda9e.gif) labels its forces in newtons. For example, it prints 4453.74 N where the frozen model uses 1000 lbf. [NIST SP 811, footnote 23](https://www.nist.gov/pml/special-publication-811/nist-guide-si-footnotes) gives exactly `4.4482216152605 N/lbf` at standard gravity. The printed force therefore converts to `1001.2405822409046 lbf`, about 0.12406% higher. The other nonzero entries show the same approximate scaling, with source rounding at node 6.

[check_load_units.py](check_load_units.py) replaces the load vector in memory, assigns a separate diagnostic ID/version, and records the entire changed input and its hash in [load-units.json](load-units.json). It re-solves both source vectors with both implementations. No frozen file is edited and no changed-load candidate is passed off as a frozen-model candidate.

| Source vector | Frozen-load utilization | Literal-Table-3 utilization | Literal-load verdict |
|---|---:|---:|---|
| Method 4 | 0.998587185980 | 0.999825987479 | pass |
| Method 6, A5=2.2 | 0.999886515967 | 1.001126928364 | reject |

For a bounded rounding diagnostic, each of the seven nonzero printed forces varies independently by ±0.005 N; listed zeros mean exactly absent loads. This is an explicit assumption, not a source-stated uncertainty model. All 128 corners were evaluated for each vector. Method 4 remains feasible, with displacement utilization in `[0.999825753256, 0.999826221701]`; method 6 remains rejected, in `[1.001126681667, 1.001127175060]`. For method 6, the same signed node-2 Y displacement violates the limit at every corner; linearity then rules out a rescue anywhere within this load box, subject to the float64 calculation. These are not rigorous interval bounds on the structural solves.

Thus rounding the printed forces to 0.01 N does not account for the changed verdict in this diagnostic. It remains unresolved whether the author intended the reconstructed imperial loads or the displayed newton values. The paper's method-6 area row itself is consistent with its printed mass.

A later primary comparator, [Kaveh and Khadem Hosseini (2012), Table 11, p. 208](https://pp.bme.hu/ci/article/download/460/217), explicitly gives the frozen load vector in kip, with the same stated imperial modulus, density and limits. Figure 11, p. 207, has matching dimension labels. This corroborates later use of the imperial convention, not Kripka's intent: its area catalogue is different (`0.1`, multiples of `0.5` through `38`, `39.81`, `40` in²). The PDF hash matches `docs/source-lock.json`. Attempts to inspect the original Rajeev–Krishnamoorthy (1992) and Tong–Liu (2001) tables did not obtain readable full text. Their numerical content is not inferred from later citations.

## Replay and verification

From the repository root, using the environment in the root README:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p scratch
.venv/bin/python scripts/audit.py sources
.venv/bin/python research/source-audit-20261022/replay.py --output scratch/source-audit.json
.venv/bin/python research/source-audit-20261022/check_mass_exact.py > scratch/source-mass-exact.json
.venv/bin/python research/source-audit-20261022/check_load_units.py --output scratch/source-load-units.json
.venv/bin/python scripts/reproduce.py --tests-only
```

The exact mass check needs only Python's standard library. The two numerical checks use the existing pinned NumPy/SciPy stack and finish in seconds. They retain the rejected source-transcription control, a positive source baseline, the two same-mass rejected alternatives, and the source-transcribed passing vector as self-checks. Package files include input and script hashes. Floating-point bytes and environment labels may differ across platforms; compare the stated tolerances and verdicts.

Initial execution used Linux x86_64, Python 3.13.5, NumPy 2.5.4 and SciPy 1.18.1, with the complete pinned environment installed. All 13 structural tests passed. **The full unmodified `scripts/reproduce.py` did not pass**: after the first result row it stops at line 28's exact list equality when one recomputed mass differs from its stored value by one ULP (`5843.018307418056` versus `5843.018307418055` lbm). A separate diagnostic found all 18 stored seed candidates pass the existing two-solver verifier; the largest mass-list discrepancy was `9.094947017729282e-13` lbm. No assertion, tolerance, stored mass or verifier was changed to suppress this failure. This portability issue is a separate handoff, not a fix in this package.

## Open next questions

1. A maintainer/reviewer should confirm the hosted A5=2.2 cell and adjudicate the frozen repository transcription, associated rejection fixture and literature wording through the project's normal process. This package does not edit those records.
2. Determine and document which force convention the published 25-bar comparator should use. Review the original benchmark lineage before changing loads or claiming source equivalence; a changed model needs its own version and review.
3. Address the reproduction driver's exact mass-list equality with an appropriate numerical comparison and regression control, preserving the existing acceptance policy and stored results.

Not checked: author intent or errata, the original 1986/1992/2001 formulations, a complete SI reconstruction, multi-group changes, an external structural solver, rigorously bounded structural arithmetic, buckling, physical suitability or global optimality. Kripka's PDF was not inspected; original publisher images and article HTML were. The 2012 comparator PDF was inspected as a separate formulation.

Credit: Kripka (2004) and the benchmark authors cited there; the existing bridge-truss model, solvers and source-audit work maintained by Douglas Colkitt. This donation used Codex with parallel AI source/analytic checks. It is author-checked work awaiting maintainer adjudication, with no claim of independent human review.
