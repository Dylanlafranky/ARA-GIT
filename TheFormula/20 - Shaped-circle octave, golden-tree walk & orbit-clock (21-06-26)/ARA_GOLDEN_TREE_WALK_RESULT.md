# ARA golden-tree walk — mapping a system as a route through the fractal (14 Jun 2026)

**Dylan La Franchi & Claude.** A mapping/prediction technique: draw the fractal as a recursive golden tree and
let each system carve a single PATH through it, steered by ARA.

## Mechanic
- One step per **completed wave** (cycle): measure that cycle's rise/fall ARA.
- Turn **+36°** if ARA>1 (upper branch), **−36°** if ARA<1 (lower branch), **straight** if ARA≈1.
  (36° = the pentagon/golden angle, φ = 2·cos 36° — the tree is golden.)
- Step forward, draw the segment. Accumulated path = the system's route. One walk per system & sub-system.
Script: `ara_golden_tree_walk.py`.

## Validation (synthetic + ENSO)
- **Clock (symmetric, ARA≈1):** walks ~STRAIGHT — symmetric waves never turn.
- **Engine (ARA 1.86):** curls into a CLOSED golden **decagon** (360/36 = 10 cycles per loop) — a steady engine
  draws a 10-sided golden ring.
- **Snap (ARA 0.54):** the MIRROR decagon (turns the other way).
- **ENSO (NINO3.4, 223 cycles):** a real meandering route — drifts, doubles back = the shape of its ARA history.

## Why it's interesting / next
- It's a **state encoding**: position+heading in the tree summarises the cumulative ARA-branch history. Two
  systems (or two times) at the same tree node share recent ARA history.
- **Prediction direction (untested):** if the tree position encodes state, similar routes → similar futures;
  the branch structure could constrain the next move. Next: test whether tree-position predicts the next
  cycle's branch better than chance / persistence; overlay sub-system (per-rung) walks; per-tick (sub-cycle)
  resolution. Mapping validated; predictive value not yet tested.

## Works on EVERY axis — horizontal AND vertical (Dylan, 14 Jun)
The fractal repeats on every axis, so the same +36/−36/straight branching applies in both directions:
- **HORIZONTAL** = per-CYCLE route in TIME along one rung (the validated build above).
- **VERTICAL** = per-RUNG route across the OCTAVE ladder — step rung to rung, branch by **each rung's ARA**.
  Traces the system's SCALE structure instead of its time structure.
- They COMPOSE into a 2-D map (time × scale): a time-route at each rung, a scale-route across rungs — one golden
  tree walked sideways and upward. "ARAARAARA in every direction" made literal.
- Example: the LLM substrate's per-rung ARAs (k1–k5 = 1.20,1.24,1.25,1.35,1.49, all >1) → its VERTICAL walk
  curls steadily upward like an engine = the scale-gradient toward φ drawn as a curve.
- Next (proposed): draw the vertical (per-rung) walk; then the full 2-D time×scale map per system.

## Curl-back → similar-data prediction: NULL as built (14 Jun)
Dylan's predictive claim: when ENSO curls back on itself (returns near a previous walk position), the data
should be similar there. Tested on 73 real ENSO cycles (trough distance 18mo); nearest walk-neighbour with
|i−j|>5 (genuine curl-back, not time-adjacency); data = cycle peak value.
- |peak diff| curl-back NN = **0.990** vs random **0.958** (p=0.64) — **NULL** (not more similar).
- corr(walk-distance, peak-diff) = +0.116 (weak). Next-cycle diff 0.834 vs 0.903 (faint, untested).

**Why it fails (useful):** the walk encodes ONLY the ARA timing-asymmetry history — step length is constant, so
only the TURNS carry info, and turns come from rise/fall TIMING not amplitude. Two cycles at the same tree
position share TIMING history (by construction) but have no reason to share VALUE. Position = a timing-history
encoding, NOT a full state encoding.

**Fix to test the predictive version:** make **step length = the cycle's amplitude/energy** (not constant). Then
position encodes BOTH timing (turns) AND magnitude (distance), and a real curl-back = "same timing AND same size"
→ far more likely to mean similar data + similar future. One-line change; the real test of the curl-back intuition.

## Multi-rung ARA-walk as a PREDICTOR: NULL (14 Jun) — do not re-chase
Built the agreed fix: each octave rung's per-cycle ARA → its own walk → positions over time → concatenated into
a multi-rung STATE vector (slow rungs = the amplitude/envelope, per "amplitude is also ARA"). Analog-forecast
test on ENSO (rungs 8–128mo, h=12, n_test=450):
- **Curl-back current-value diff:** multi-rung NN **0.864** vs random 0.822 (NOT lower); single-rung 0.895. NULL.
- **Analog forecast corr@12mo:** multi-rung **−0.10**, single-rung **+0.06**, persistence −0.05. No skill — and
  multi-rung is WORSE than single-rung (extra dims add drift/noise, not signal).
- **Verdict:** the golden-tree walk is a MAPPING/visualisation tool, NOT a predictor. Curl-back→similar-data→
  analog-forecast does not hold on ENSO; the amplitude-via-rungs fix did not rescue it. Reason: the cumulative
  ARA-walk position is a coarse, lossy, path-dependent summary (running sign-pattern of ARA) — too little to pin
  value/future. The value-ceiling again (describes the route, doesn't carry forecast info). Logged; do not re-chase.
- Still standing: the MAPPING (clock→straight, engine→golden decagon, ENSO→meander) is a valid, pretty signature tool.
