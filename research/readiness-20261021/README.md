# Truss optimization: second-cohort preparation

Local preparation authorized by the project coordinator on 2026-10-21. Evidence is
**author-checked**; outside scientific review and public intake approval are pending.
No external contact, hub submission, or new reviewer consent is implied.

## Prepared work

Eight frozen sensitivity cases derived from two existing geometries use individual-member sizing and explicit load reversals. Coordinate descent strengthens starts before equal structural-solve-budget DE and guided-search comparisons. Every retained incumbent is checked by both structural engines. Section count is reported alongside mass.

The machine-readable portfolio is [`portfolio.json`](portfolio.json).
Historical experiments retain their original exposure and evidence labels. These
preparation cases are now exposed development material, not a sealed test set.

## First contributor step

Activate the repository's documented Python environment, then run from its root:

```sh
python scripts/prepare_portfolio.py --candidate research/readiness-20261021/25bar-individual-v2-incumbent.json
```

Research-portfolio-2.0.0 is separate from the original grouped benchmark. Original section catalogues, tolerances and linear pin-jointed/Euler model retained. Load variations are synthetic sensitivity questions pending engineering approval. Section count is a separate tradeoff; the model is not a construction design.

Before searching, read the portfolio and select one bounded task. Preserve the
starting witness, source hashes, seed and budget. Reserve time to verify the final
artifact. Record unsuccessful runs. A useful handoff can be a replication, a
reproducible defect, a bounded negative finding, or an improvement under the same
formulation; identify which one it is. Passing a local check does not imply novelty
or independent acceptance.

## Outside review

[REVIEW.md](REVIEW.md) contains concrete questions; [review.json](review.json) is an
unfilled review receipt. Review must identify a commit and exact artifact hashes.
The person reproducing a result should disclose any involvement in its creation.

## Independent contributor trial protocol

Choose a task using the refreshed catalogue and give a new contributor only the
published instructions. Record setup time, time to first valid artifact, total
compute, failed attempts and reviewer minutes. Start from the inherited frontier.
Freeze algorithm submissions before evaluating on a separately prepared unseen
case pool. Author-run smoke checks here do not count as independent trials.

Remaining gates:

- Structural optimization/physics review.
- Independent model and solver replay.
- Independent contributor trials over sequential rounds.

## Interpretation of the eight cases

The same two original geometries underlie all cases. Load reversals are sensitivity
questions chosen for preparation, not measured service loads. The individual-member
25-bar case inherits the prior 519.790682 lbm witness. New load cases first receive
up to 12,000 coordinate-descent evaluations, then both DE and guided search start
from that same strengthened witness with 2,000 structural-solve allowances each.
Continuous proposal solves count against the guided allowance. Timing is descriptive.

An initial smoke portfolio started new cases at maximum sections and exposed weak
starts; it was regenerated with coordinate descent before freezing this package.
The final files are preparation benchmarks, not a preregistered contributor trial.
Two 10-bar reversal cases currently share the same witness; count them as related
model checks, not independent research opportunities. A reviewer should decide which
cases are worth retaining. Classic grouped cases remain tutorials/regression controls.
