# Energy-graph test 1 — crossing-timed reservoir read: NOT SUPPORTED

**Date:** 5 Jul 2026 · Dylan La Franchi (direction) / Claude Fable 5 (implementation)
**Orientation:** up = slower/larger. WWV = reservoir below the NINO3.4 surface wave.
**Script:** `energy_graph_crossing_read_test.py` (this folder). Registration
header in-script, written before first run. Data: NOAA PSL NINO3.4 anomalies ×
PMEL WWV west+east anomalies, overlap 1980-01..2025-12 (552 months). Strictly
causal expanding-window walk-forward, golden split (61.8% initial train, 202
scored origins at h=6). Ridge alpha fixed at 1.0, declared not searched.

## Registered expectations and verdicts

- **P1** (consistency: feeder models beat persistence/seasonal/own-history-ridge
  corr at h=6): **NOT SUPPORTED as registered** — the generic feeder A beat all
  baselines (+0.593 vs own-history 0.538), but the crossing-read model B
  (0.532) fell just under own-history. P1 failed on B, not on the physics.
- **P2 — the horse** (crossing-timed read B ≥ continuous read A at h=6 and
  h=18): **NOT SUPPORTED.** B < A at every horizon (6: 0.532 vs 0.593;
  12: 0.223 vs 0.363; 18: 0.251 vs 0.320). The ARA-specific edge rule, in this
  operationalization, added nothing over a generic continuous feeder and cost
  correlation.
- **P3** (any MAE lift over own-history comes only via WWV terms):
  **CONFIRMED** — h=6 MAE 0.560 (A) vs 0.580 (B3); no own-history variant
  improved MAE anywhere. Consistent with the amplitude-from-below rule.

## Full table (held-out)

| h | persistence | seasonal | own-ridge B3 | feeder A | crossing B |
|---|---|---|---|---|---|
| 6 | +0.366 / 0.769 | −0.084 / 0.985 | +0.538 / 0.580 | **+0.593 / 0.560** | +0.532 / 0.593 |
| 12 | −0.093 / 0.990 | −0.093 / 0.990 | +0.278 / 0.643 | **+0.363 / 0.644** | +0.223 / 0.678 |
| 18 | −0.164 / 1.152 | −0.164 / 1.152 | +0.271 / 0.646 | **+0.320 / 0.676** | +0.251 / 0.678 |

(cells: corr / MAE)

## Honest reading

1. The two-node physics replicated cleanly: continuous WWV feeder lifts corr
   at every horizon over own-history (folder 16 confirmed again, new
   implementation, new split).
2. The conjecture's ARA-specific content — read the reservoir at the
   crossing/handoff — LOST its first race. Logged as NOT SUPPORTED, no rescue.
3. **Protocol gap, flagged:** the S1 ground-truth gate was skipped — the
   crossing-read extractor was never validated on synthetic coupled pairs
   where crossing-timed transfer is true by construction. This null is
   therefore *instrument-uncertified*: it may mean the edge rule is wrong, or
   that "WWV at last NINO zero-crossing" is a poor operationalization (stale
   reads at long gaps; crossing choice on the wrong band; no rung
   decomposition first — the RIDGE RULE was not applied to split NINO's two
   interannual bands before locating crossings).
4. Next-test candidates (register separately; do NOT tune on this table):
   (a) S1 synthetic gate for the crossing-read instrument; (b) crossings
   located on the quasi-biennial band (the engine) rather than raw NINO;
   (c) read at WWV's own discharge crossing (the spring pump) rather than
   NINO's zero-crossing.

Per the falsification edges in RULE_PROPOSAL_AMPLITUDE_FROM_BELOW: this null
does not touch the amplitude rule (§1, P3 supported again). It counts against
the transfer-operator conjecture's edge-timing clause only, first
operationalization, uncertified instrument.
