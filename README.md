**Contributor trial (20 October 2026):** [featured-pilot assessment](research/feature-trial/REPORT.md) and [replay instructions](research/feature-trial/METHODS.md). This repository contains a separate exploratory model; the original frontier below is unchanged.

# Lightweight structural truss optimization

A Discovery@Home research pilot maintained by **Douglas Colkitt**. Minimize
material on a fixed ground structure using discrete sizes while checking every
constraint in a pinned engineering model. These are **model-validated research
designs, not physically certified construction designs**.

The executable portfolio is the planar 10-bar and spatial 25-bar truss. The 72-bar
tower is researched and transcribed as a follow-on, with a mass-only baseline
audit. Published reference sizing and a new tube/Euler buckling profile remain
separate. Published baseline masses reproduced here: 5490.737892 lbm (10-bar) and
485.048797 lbm (25-bar). Two lower printed source rows are rejected, with reasons
in [the literature audit](docs/LITERATURE.md). These are selected comparators,
not asserted worldwide records.

Read [the results](docs/RESULTS.md), [practical transfer and donor assessment](docs/ASSESSMENT.md),
[model contract](docs/MODEL.md), and [agent entry](AGENTS.md).

![10-bar comparison](results/10bar-tube-topology.png)
![25-bar comparison](results/25bar-tube-topology.png)

## Reproduce

Python 3.12+ is required by the pinned numerical stack; tested with Python 3.14
on macOS arm64. Use a local environment, no global installs:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/reproduce.py
.venv/bin/python scripts/check.py results/10bar-tube-topology-winner.json
```

The offline verifier runs tests, re-solves every saved winner and seed result
with both implementations, and recomputes masses, savings and result arrays.
Expected runtime is seconds after installation (allow a few minutes on a slow
machine); environment creation needs a package download. No optimization or
network is needed to verify stored results. Numerical results use float64,
not rigorous interval certificates.

To replay the full search in a separate output directory:

```sh
.venv/bin/python scripts/run_search.py --iterations 120 --seeds 17 42 2026 --output scratch/replay
.venv/bin/python scripts/render.py
```

The first command can take several minutes and preserves the checked-in results.
The renderer intentionally reads checked-in `results/` and regenerates its plots
and CSV schedules. Seeded replay is deterministic within the pinned stack;
across libraries/platforms compare verified feasibility and numeric tolerances,
not byte-identical floating point output. The search uses integer differential
evolution, complete coordinate scans and paired local exchanges, with no global
optimality guarantee. The source freeze is commit `b3024e9`, before any search.

Each result has candidate inputs, a model hash, full structural verification,
seed, evaluation counts, elapsed time and improvement trace. `results/summary.json`
is the local frontier table. `results/*-members.csv` and `*-nodes.csv` contain full
force, stress, section, displacement and reaction schedules. `benchmarks/LOCK.sha256.json`
prevents unnoticed input changes.

## Participation

Repository: [discoveryathome/bridge-truss](https://github.com/discoveryathome/bridge-truss).
Public donor intake is paused and review capacity is not yet specified.
No hub submission or listing has been requested. [DISCOVERY.md](DISCOVERY.md) states review,
credit and coordination rules. Code: MIT. Original documentation/figures: CC BY 4.0.

The verifier and frontier deserve the most care: review capacity, rather than
additional search compute, will determine whether donated work is useful.
