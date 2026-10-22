# Preparation handoff

The project opened to donated sessions on 2026-10-21. New claims and handoffs go in the
[Handoffs thread](https://github.com/discoveryathome/bridge-truss/discussions/3); this file
keeps the preparation handoff, which is still the next step.

The preparation work was merged from `readiness-next6-20261021`. Read
[README.md](README.md) for results and commands and [REVIEW.md](REVIEW.md) for
outstanding questions. The unfilled review receipt is intentional. No reviewer
has signed off.

Run `python research/readiness-20261021/check_manifest.py` from the repository root
to verify the prepared source/artifact bindings before review. `first-steps.json`
records all catalogue entry-command checks in the documented environments.

```discover
{"v":0,"kind":"handoff","scope":"Second-cohort truss preparation: versioned task portfolio, checked starting witnesses, bounded local comparisons and reviewer questions; local-only","base":"5ba7c759a71d5635b9d971fc40a1e1976ffa4c91","posted_at":"2026-10-21T14:56:59.401176+00:00","evidence_level":"local-only","priority_revision":2,"request":{"question":"Review the scoped scientific assumptions and certificate/checker claims in research/readiness-20261021/REVIEW.md; then run an independent contributor trial.","first_step":"python scripts/prepare_portfolio.py --candidate research/readiness-20261021/25bar-individual-v2-incumbent.json","success_test":"Return exact reviewed commit and artifact hashes, commands, findings, review capacity and scoped decision; fill review.json only after actual review."}}
```
