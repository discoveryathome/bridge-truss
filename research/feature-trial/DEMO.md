# A public demo that makes the progress honest

Use [the before/after figure](figures/extension-before-after.png), followed by
[the strategy comparison](figures/method-comparison.png). The PNGs are rendered
from saved candidates rechecked in both structural engines; SVG originals are
also available for the before/after and trial overview. No image-generation
model was used to invent the geometry or forces.

Suggested 45-second narration:

> These dots are fixed joints, and the arrows are the loads our virtual structure
> must carry. Red bars are being pulled; blue bars are being compressed. Wider
> lines mean more material. We ask: can we reduce that material while staying
> within the mathematical model's limits?
>
> First we let each bar choose its own size from a fixed catalogue. Local search
> saved about seven percent. Then a different strategy proposed coordinated size
> changes, snapped them to available sizes, and checked them again. That brought
> the total saving to thirteen percent. Two separately coded solvers agree on
> the calculations.
>
> This is a virtual engineering research result, not a construction design. The
> gain belongs to this individual-bar model, not the original grouped benchmark.
> The next research challenge is to keep making progress while accounting for
> practical tradeoffs—this lighter design needs more different section sizes.

For a live technical demonstration, run `python scripts/reproduce.py`, then
`python research/feature-trial/code/validate.py` from the pinned environment.
Those commands verify saved results quickly. To show an actual search, replay
one guided extension run as described in `code/replay_sample.py`; it takes seconds
on the tested M2. Replaying a known result is demonstration, not a new discovery.

The present visual changes are subtle because node positions are fixed. A mass
counter and the common-start strategy chart communicate the result more clearly
than implying a dramatic shape transformation. Do not use the original setup's
uniform-to-winner savings as the contributor trial's achievement. A real audience
test remains to be done.
