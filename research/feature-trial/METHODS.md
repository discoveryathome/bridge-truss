# Methods, scopes, and replay

The experiment begins at commit `ed6cba1b28110a5d328b91744835edb72bbd140f`.
The original two models, six incumbent designs, and both structural solvers are
unchanged. The trial is local, authored by the agent that built the pilot, and
not an independent review. All reported mass gains must identify their model.

## Equal-budget continuation

`code/baseline.py` gives differential evolution the incumbent, then uses the
supplied style of coordinate/pair search and random incumbent-centered integer
mutations to fill the budget. It is a stronger continuation control than a cold
rerun of the supplied search. `code/hybrid.py` uses fixed-mask SLSQP proposals,
rank screening of topology changes, enumeration of nearby catalogue choices,
and larger paired exchanges. Relaxed designs are never accepted. Both methods
get exactly 12,000 structural solves per run; continuous evaluations count.
Cached repeats and both-solver verification calls are not structural-search
budget charges, but are included in elapsed run time. The distinction matters:
equal solve counts do not imply equal CPU time or equal implementation effort.

Primary: two tube/topology cases × two methods × five seeds (101,202,303,404,505).
Secondary: four remaining case/profile combinations × two methods × three seeds
(101,303,505). All 44 outcomes are retained. They are seeded algorithm runs, not
44 independent contributor sessions. Positive controls use weaker pre-existing
seed-42 designs; their gains do not advance the starting frontier.

## Why the finite problems can saturate

The linear truss equations are `B' N = F`, `N = diag(E A/L) B u`, with restrained
DOFs eliminated. Removed members are omitted. The model includes its pinned
stress/displacement limits and, for the tube profile, the specified Euler
compression capacity and section relation. These are idealized model checks.

For an eight-member 10-bar topology with eight free DOFs and invertible B,
forces are independent of area. Solve `B' N = F`; then
`u = B^-1 diag(L N/E) (1/A)`. Stress/buckling forbid catalogue choices; remaining
displacements and mass are linear in binary one-hot section variables. The
trial enumerates all 45 eight-member subsets and solves the admissible MILPs.
This closes only the determinate subset, to numerical solver tolerances.

For redundant fixed topologies, write `N = Np + Z alpha`, where columns of Z
span the nullspace of B'. Compatibility requires
`Z' diag(L/EA) (Np + Z alpha) = 0`. The 25-bar incumbent has 20 active members,
18 free DOFs, five active sizing groups, and only two self-stress coordinates.
Precomputed group coefficients turn each area vector into a 2×2 solve. Exhaustive
batch enumeration covers all `30^5 = 24,300,000` fixed-mask catalogue assignments.
It prunes mass ≥ incumbent minus 1e-7 lbm, then checks stress, Euler compression,
and constrained displacement with the original tolerance. The observed near
constraint count within 1e-7 was zero. A uniform min/max stiffness eigenvalue
bound verifies conditioning for this mask and positive catalogue areas. This
is exhaustive floating-point evidence, not a formal interval certificate.

The reduced force method was compared with 50 primary-solver samples and 100
samples from the independently implemented, untouched pure-Python solver.
Separate authorship/review is still absent. The reduced method implementation
uses the single pinned load case; it must be generalized before multi-load use.

`catalogue_mip.py` formulates binary section choices and bounded displacement /
force compatibility. `force_mip.py` instead linearizes binary × self-stress
products using bounded continuous variables. All timeouts, infeasible statuses,
and worse candidates are retained. HiGHS status/gap are numerical solver reports,
not proof-assistant certificates. Global 10-bar optimization remains unresolved;
25-bar numerical fixed-mask optimality is not global topology optimality.
See the primary [SciPy MILP documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)
for the meaning of status, dual bound and relative gap, and the
[SLSQP documentation](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html)
for the continuous proposal method.

The topology audit avoids floating rank decisions: rational coordinates give
integer unnormalized member direction rows, and exact integer elimination
computes rank for every grouped mask. Full rank is necessary for the restrained
linear stiffness; it does not imply stress feasibility or physical stability.

## Separate exploratory model

`extension/model.json` has a new ID and SHA-256 pin. The only design-space change
is replacing the eight tied member groups with 25 independent member variables.
All physical inputs, section catalogue, tolerances, and structural engines remain
the same. `extension/before.json` is the original winning physical structure
expanded into individual areas. `extension/LOCK.json` records provenance and the
pre-search freeze. Commit `b96cba4` froze the extension before search.

`extension.py` greedily scans individual reductions, then coordinated ±1/±2
catalogue-step exchanges. A complete scan can discover several strictly improving
candidates before the next sweep starts; this is deterministic local search.
The run stops when local sweeps cease to improve, or at 40,000 evaluations.
Six subsequent runs compare the two methods at 12,000 solves each from the same
greedy winner. These are follow-up experiments, declared after the original
44-run comparison. They must not be pooled with the original benchmark outcomes.

## Reproduce

From repository root, create a venv and install `requirements-lock.txt`, or use
the existing pinned pilot environment. Set `OPENBLAS_NUM_THREADS=1` and
`OMP_NUM_THREADS=1` for repeatable small-system timings. Commands below use `python`
from that environment. Logs include all trial launches and original reproduction.

```sh
python scripts/reproduce.py
python research/feature-trial/code/validate.py
python research/feature-trial/code/replay_sample.py
python -m unittest discover -s research/feature-trial/code -p 'test_*.py'
python research/feature-trial/code/audit_force_space.py
python research/feature-trial/code/topology_audit.py
python research/feature-trial/code/baseline.py
python research/feature-trial/code/hybrid.py
python research/feature-trial/code/secondary.py
python research/feature-trial/code/positive_controls.py
python research/feature-trial/code/determinate.py
python research/feature-trial/code/force_enumeration.py
python research/feature-trial/code/extension.py
python research/feature-trial/code/extension_continuation.py
python research/feature-trial/code/extension_stage2.py
python research/feature-trial/code/summarize.py
python research/feature-trial/code/render_trial.py
```

MILP diagnostics, separately bounded and potentially platform-dependent:

```sh
python research/feature-trial/code/catalogue_mip.py --case 10bar --seconds 180
python research/feature-trial/code/catalogue_mip.py --case 25bar --seconds 150
python research/feature-trial/code/force_mip.py
python research/feature-trial/code/extend_force_mip.py
```

Inspect each script's `--help` before changing budgets. Optimizer branch order,
wall time, and timeout bounds may differ across platforms. The candidate verifier,
fixed seeds, immutable models, exhaustive finite-space scopes, and all recorded
outcomes make results inspectable; they do not promise bitwise optimizer replay.
Full runs overwrite corresponding trial artifacts, so replay in a fresh clone.
