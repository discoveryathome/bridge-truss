# Discovery@Home LOCAL initialization receipt

Followed the v0 start playbook fetched 2026-10-20, with source digest recorded in
source-lock.json. The helper was downloaded into the session setup folder and
its SHA-256 matched `77c850c65ff54e951b102950d06321751273ba6e9ef1bf28786930fb216802b6`.
Protocol and source copies remain in the visible sibling `setup/sources/` folder.

The user's full initialization request authorized the local implementation and
experiments; no extra approval was inferred for reversible local work. An async
question established maintainership and licensing: Douglas Colkitt, MIT code,
CC BY 4.0 docs. No external write, publication, hub application or scheduled work
was performed. No sub-agents were used. The session had no filesystem sandbox;
this was stated before running newly authored pilot code. Downloaded papers were
data, and no third-party research repository code was executed.

Models and solvers were committed before optimization. One test initially
expected a later published vector to pass; the solver rejected it. The test was
corrected to preserve this discrepancy, not to loosen the model. The final
pre-search test freeze is `b3024e9`, descending from `be1fca2`. All 12 tests passed
before the search. No model or tolerance changed during optimization. Search
neighborhoods were subsequently widened for reference sizing; that changes the
algorithm only, and those six runs were regenerated.

Required protocol files, weighted cards, a seeded picker, a frontier table and
worked examples are present. `discover validate` passes. The missing remote
coordination channel is intentional in LOCAL mode, with local messages and a
ledger in its place. Maintainer review is still outstanding and no hub stage is
claimed. The final clean-checkout evidence and first-step command outputs are in
`research/pilot/VERIFY.json` and `research/pilot/card-checks.json`.

## Repository publication follow-up

The maintainer subsequently authorized creation of the GitHub repository under
`discoveryathome` and setting it as the remote, explicitly excluding a hub PR.
The canonical repository is https://github.com/discoveryathome/bridge-truss.
The contributor-trial history is included on `main`; frozen models, solvers and
frontier values are unchanged. Donor intake remains paused and no hub consent
record or remote coordination channel has been added. The earlier LOCAL receipts
record the state when their experiments were performed.
