# Practical transfer and donor discovery potential

> **Historical (2026-10-20).** The recommendation below predates the launch: the project has
> been open to donated sessions since 2026-10-21, with a maintainer. Current status is in
> `DISCOVERY.md`; independent review of the solvers and benchmark transcription is still wanted.

The pilot is technically viable for donated computational research: a candidate is small, the objective is explicit, and a stranger can cheaply recompute every stored result with two implementations. The strongest immediate contribution is verification quality. Published-row discrepancies were detected before optimization, demonstrating useful outcomes even without a new minimum.

Practical transfer is **conceptual and methodological**. Discrete member sizing, explicit section inertia, load-path checks and grouped construction choices resemble real design decisions. The delivered model omits many governing engineering effects. No model here establishes real-world structural safety or suitability for construction. Review of full load combinations, self-weight, support/connection behavior, material/product data, global and local stability, nonlinear imperfections, manufacturing and physical tests would be required in a new engineering programme. An Euler factor of 1.5 is not a substitute for that programme.

Winning designs sit close to model constraints. The diagnostic below increases all prescribed loads by 1% without optimizing again; it is deliberately outside the frozen frontier. Its narrow linear load multipliers are not physical safety factors.

- 10bar: uniform linear load multiplier limit 1.004413; passes +1% load diagnostic: False.
- 25bar: uniform linear load multiplier limit 1.007245; passes +1% load diagnostic: False.

Donor potential is moderate for methodological discovery and source auditing, low for claims of fundamental novelty from small classic benchmarks alone. Useful bounded tasks are independent external-solver reproduction, correction of inconsistent source vectors, more complete mechanism tests, a pinned discrete 72-bar extension, stronger local-search neighborhoods and lower-bound/optimality methods. The MILP literature motivates exact-bound work, but its assumptions must match the pilot's rank and buckling requirements. Three seeds are a pilot exploration, not a statistically convincing algorithm comparison.

The portfolio offers independent case/profile/seed units; replay is cheap and CPU-only. Limit submitted candidates to one verified improvement or a substantive negative finding per task, preserving the search budget and model digest. Duplicate tiny heuristic improvements should be batched for review. A volunteer can usually verify and report within a short session without rerunning the whole search. Additional compute is useful only after source fidelity and acceptance rules are trusted.

Douglas Colkitt is the confirmed maintainer. Review capacity remains unspecified; no public intake or hub consent is active. Before opening donations, obtain an independent review of both solver implementations and benchmark transcription, resolve or explicitly quarantine disputed baseline rows, measure a fresh donor rehearsal, and agree on a sustainable review rate. The current verification is author-checked; no claim of external acceptance is made. The repository contains concrete task cards, seeded task allocation, local handoffs, model hashes, replay commands and result packages, but no evidence yet of sustained multi-donor coordination or review throughput.
