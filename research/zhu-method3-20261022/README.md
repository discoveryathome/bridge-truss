# Method 3: a bounded source-comparability and mass audit

**The printed vector does not have the printed mass under the frozen model.**
Exactly one of 232 single-group catalogue substitutions matches that mass:
group 2 changes from 1.8 to 1.9 in². Both existing solvers accept this
diagnostic under the frozen reference constraints. This does **not** establish
a historical correction: the original 1986 formulation was not obtained, and
mass plus feasibility does not uniquely determine the vector.

This follows the [method-3 handoff][handoff] from [PR #7][prior], which already
identified the row's mass and displacement discrepancy. New evidence here is
the original PDF check, identified DOI and access record, a complete one-group
census, an independent exact mass enclosure, and explicit ambiguity controls.
It does not repeat the earlier method-6 investigation or propose a new record.

## Source evidence and its limit

Kripka (2004), [printed p. 172, Table 4][pdf], attributes method 3 to Zhu
(1986) and prints the following areas, in group order:

`[0.1, 1.8, 2.6, 0.1, 0.1, 0.8, 2.1, 2.6] in²`, with weight `562.93 lb`.

The PDF and [separately hosted publisher table image][table] agree. The
source's p. 173 bibliography and the [publisher-deposited DOI record][crossref]
identify *An improved Templeman's algorithm for the optimum design of trusses
with discrete member sizes*, Engineering Optimization 9(4) (1986),
[DOI 10.1080/03052158608902522][zhu]. Preserve the metadata distinction:
Kripka cites `Zhu, D.M., 302–312`; the deposit gives name fields `DUAN` /
`MING-ZHU` and pages `303–312`. Neither difference explains the numerical row.

The publisher abstract/PDF/ePDF/full-text routes returned no readable original
in this session (direct requests returned HTTP 403). Exact-title/DOI and
institutional searches, plus archive and bibliographic-index discovery, found
no retrievable original. This is a bounded access result, not a claim that no
copy exists. No author contact, purchase or access-control bypass was used.
The source's original geometry, loads, grouping, density, constraints, vector,
weight and tolerances therefore remain **unverified**.

The numeric audit uses `benchmarks/25bar.json` v1.0.0, `reference` profile,
SHA-256 `5291c9023163d70b696d644923fc2ad94bcaf07984a6f037986f13035ef42328`.
It does not equate this frozen imperial model with every historical
formulation. In particular, the force-unit comparability qualification in
PR #7 remains open. Hashes, source locators and the factual row are retained
in [source.json](source.json); copyrighted sources are linked, not redistributed.

## A complete finite diagnostic

After an exploratory group-2 check, we exhaustively replaced each of the
eight group areas by each of the other 29 frozen catalogue values. The
comparison convention is `[562.925,562.935) lbm`, representing nearest-hundredth
reporting. It is not a claim about the author's rounding algorithm. No
calculated mass lies at either endpoint.

The 232 changes contain **51 feasible vectors** and **one mass match**.
Both implementations agree on every validity decision and on the checked
force, displacement, reaction, mass and utilization arrays. The largest
relative discrepancy is below `5.8e-15`, against the unchanged `1e-8` agreement
tolerance. [audit.json](audit.json) retains every census summary and the full
two-solver arrays for the printed row and the displayed diagnostic controls.

| Vector relative to the printed row | Mass (lbm) | Maximum displacement utilization | Frozen reference result |
|---|---:|---:|---|
| Unchanged | 557.711787365477 | 1.001145158774 | Rejected |
| A2 = 1.9 | 562.931940619932 | 0.996089953851 | Feasible |
| A2 = 1.9, A6 = 0.9, A7 = 2.0 | 562.931940619932 | 0.989151824691 | Feasible |
| A2 = 1.9, A6 = 2.1, A7 = 0.8 | 562.931940619932 | 1.063768278263 | Rejected |

The unchanged row exceeds the displacement limit by much more than the
`1e-8` utilization allowance. A matching mass alone is insufficient, and even
mass **plus feasibility** fails to identify a unique vector once multiple
entries may differ. These controls are not proposed source repairs.

## Exact arithmetic check, independent of the structural solvers

Parsing the frozen decimal coordinates and density as rational numbers gives
the mass identity, with areas in in²:

```text
M(a) = (15/2)a1 + 5√109 a2 + 5√73 a3 + 15(a4+a5)
       + 5√210(a6+a7) + 5√114 a8                         [lbm].
```

[check_mass_exact.py](check_mass_exact.py) derives member squared lengths
directly from the JSON endpoints. For `q=n/d`, integer square root with
`S=10^30` gives `k=isqrt(floor(n*S²/d))` and
`k/S <= sqrt(q) <= (k+1)/S`; exact roots use singleton bounds. Positive
rational areas and density preserve the enclosures under summation.
No NumPy, structural solver or floating-point square root is used.

```text
M(printed) is in
[557.711787365476761859621656275753,
 557.711787365476761859621656275758] lbm.

M(A2=1.9) is in
[562.931940619932036949500533287027,
 562.931940619932036949500533287032] lbm.
```

The script proves that this one-change enclosure is inside the reporting
window and that all other 231 are disjoint, with zero unresolved cases.
The nearest excluded candidate is A1 = 0.8, at least `0.02678736 lbm`
above the window. Thus floating-point roundoff does not explain the finite
mass classification.

Groups 6 and 7 have exactly equal total length. Holding their sum at 2.9
gives **26 ordered catalogue pairs**, all with exactly the same mass as the
one-change match. The script constructs this family; it does not exhaust all
multi-entry changes. The table above separately checks one different feasible
member and one infeasible member of that family. Exact mass enclosures are
not rigorous bounds on structural displacements or stresses.

## Reproduce and review

From the repository root, after installing the existing pinned environment:

```sh
.venv/bin/python research/zhu-method3-20261022/replay.py
python3 research/zhu-method3-20261022/check_mass_exact.py
.venv/bin/python scripts/reproduce.py --tests-only
```

The first command prints the full diagnostic JSON. The second is standard
library only and prints rational enclosures and the census; run it without
`-O`, since its self-checks use assertions (it explicitly rejects `-O`).
The structural replay's checks remain enabled under `-O`. Neither script
writes files. [mass-exact.json](mass-exact.json) retains the exact replay.

The unmodified full `scripts/reproduce.py` was also run: all 13 structural
tests passed, then its exact stored-mass list comparison at line 28 failed.
This reproduces the [already reported portability handoff][portability],
not a new finding in this audit. No tolerance or stored result was changed to
make that driver pass. The frozen reference comparator passes the unchanged
two-solver verifier as a separate positive control in `replay.py`.

**Next:** obtain the identified 1986 original through authorized access and
compare its exact numerical formulation page by page. The matching diagnostic
is a question to test against that source, not a reason to replace the printed
row. A distinct historical formulation must be labeled separately.

Base `d3a2a3da00c7cb329474470f9e112f0ac0d32cb1`; seed
`6c582405067d1504975a52aca071c263`. Author-checked, substantially AI-assisted
research by Sagar Thakrar with Codex. Credit Kripka (2004), the 1986 author as
identified in the source records, and the existing model/solver work maintained
by Douglas Colkitt. The exact arithmetic check uses a separate internal method;
it is not external scientific review. Frozen models, solvers, stored results,
frontier and acceptance ledger are unchanged. No optimum or physical safety
claim is made.

[handoff]: https://github.com/discoveryathome/bridge-truss/discussions/3#discussioncomment-19132027
[prior]: https://github.com/discoveryathome/bridge-truss/pull/7
[pdf]: https://new.scielo.br/j/jbsmse/a/vZNDbfZ66DHqFZc3HPcrj4k/?lang=en&format=pdf
[table]: https://minio.scielo.br/documentstore/1806-3691/vZNDbfZ66DHqFZc3HPcrj4k/94c459eaed0555f014ce4ff81e33b9be4ff48c8b.gif
[crossref]: https://api.crossref.org/works/10.1080/03052158608902522
[zhu]: https://doi.org/10.1080/03052158608902522
[portability]: https://github.com/discoveryathome/bridge-truss/discussions/3#discussioncomment-19131877
