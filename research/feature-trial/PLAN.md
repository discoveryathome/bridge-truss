# Featured-pilot contributor rehearsal — pre-experiment plan

Started 2026-10-20 18:55:47 UTC. Target about 45 minutes; finish within 60.
Base: ed6cba1b28110a5d328b91744835edb72bbd140f. Task picker seed
`ae59f86324a34a781b86cfa845d99288` drew `search / bounded-search`.
The user specifically requested a featured-pilot fitness trial. Existing local
handoff is for independent solver review, not an overlapping search claim.

Use current incumbents, not heavy uniform starts. Do not change model inputs,
section catalogue, load cases, groups, acceptance tolerances or either verifier.
Keep proposed improvements in this package; do not overwrite the accepted
frontier. The investigator wrote the setup and is not blind to the project.
Reused isolated dependencies; clean local source clone. Onboarding/dependency
setup cost for a new agent is not independently measured.

Primary outcomes: strictly verified lower mass on 10/25-bar tube-topology cases;
percentage gain over current best; new member/topology choices; time/evaluations
to first improvement; reproducibility; signs of saturation. A >0.1% improvement
is a visible numerical increment, but public-demo value will also depend on
whether the geometry/load-path change is intelligible. A >1% gain is stronger
feature evidence. These are evaluation heuristics, not scientific thresholds.

Compare additional existing-method search with reasoning-led methods. Give
ordinary search access to the same incumbents. Use fixed seeds 101, 202, 303,
404, 505, and report all trials, not just successes. Use equal structural-solve
budgets where possible; separate time spent implementing methods from execution.
Do not label differences as a causal estimate of model intelligence: methods and
human/agent development effort differ, and the sample is small.

Hypotheses before testing: (1) narrow feasible local neighborhoods trap the
existing method; continuous proposals and larger coordinated changes may help;
(2) the 10-bar winner is statically determinate and may admit an exact discrete
fixed-topology reformulation, useful for measuring saturation rather than
promising endless hill climbing; (3) classic benchmark novelty is limited.

Deliver a replayable contribution package, fair before/after demo, and a candid
featured-pilot recommendation including a stopping/expansion decision.
