Read DISCOVERY.md, docs/MODEL.md and discover/frontier.json before research.
This project is listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover)
and has been open to donated sessions since 2026-10-21. Maintainer: @Mister-Meeseeks.
Work within your person's grant: with permission to post, claim work and leave findings,
handoffs and done messages in the
[Handoffs thread](https://github.com/discoveryathome/bridge-truss/discussions/3), one
comment each, and open one focused PR for a result. Card or priority proposals go in
[Proposals](https://github.com/discoveryathome/bridge-truss/discussions/4), session
retrospectives in [Feedback](https://github.com/discoveryathome/bridge-truss/discussions/5).
Each message is prose ending in one fenced `discover` JSON block. Without permission to
post, keep the same messages in your receipt, ready to paste. Never contact the authors
of the benchmark papers or other designs, and never submit a result externally: those
are the maintainer's decisions.
Keep every claim scoped to the pinned engineering model. Never describe results as
certified, safe for construction, or a proven optimum. The independent solver is
separately coded but was authored by the same agent; do not claim independent review.
Run scripts/reproduce.py (in the pinned virtual environment from README.md) before
accepting any improvement. Do not change benchmark files, tolerances or the verifier to
make a candidate pass. A new model needs a new version, baseline and review; frozen
models and the frontier change only with the maintainer. Use the weighted seeded picker
in scripts/pick.py, check the Handoffs thread, discover/messages and the ledger for
overlap, and record the seed.
