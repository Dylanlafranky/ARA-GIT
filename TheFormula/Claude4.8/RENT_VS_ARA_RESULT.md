# Does information rent-per-rung track ARA?  (test of rent = 2 − ARA)

**Date:** 2026-05-30
**Script:** `rent_vs_ara_test.py` → `rent_vs_ara_result.json`

## The claim being tested

Prediction: a system's **rent** (fraction of information it sheds per φ-rung of forward
time) should equal **2 − ARA**.

- ARA = φ (golden engine) → rent = 2 − φ = 1/φ² = **0.382** ("most effective")
- ARA → 2 (pure harmonic / flywheel, e.g. Sun) → rent → 0 (retains everything)
- ARA → 1 (balance point) → rent → 1 (sheds the most)

## How it was measured — two INDEPENDENT legs, no shared maths

- **ARA** = single-cycle waveform asymmetry. Dominant cycle located by narrowband
  bandpass (trough→trough); build = trough→peak, release = peak→next trough, measured on
  the raw signal. ARA = median(release)/median(build). Bounded in (0, 2) by construction.
- **RENT** = 1 − geomean per-φ-rung retention of auto-mutual-information, anchored at ~1
  cycle (the entropy leg from `phi_rung_entropy_decay_test.py`).

These never touch the same computation, so a correlation between them is not circular.

Systems (all real, public): ENSO Niño3.4 monthly; SILSO sunspots monthly; slpdb slp01a
@250 Hz — ECG (heart), BP (vascular), EEG C4-A1 (brain), Resp (lung).

## Results

| System | ARA | rent | 2 − ARA (predicted rent) | AMI power-law R² |
|---|---|---|---|---|
| EEG (brain) | 1.000 | **0.129** | 1.000 | 0.25 |
| Solar (Sun) | 1.091 | 0.488 | 0.909 | 0.60 |
| ECG (heart) | 1.200 | 0.629 | 0.800 | 0.72 |
| BP (vascular) | 1.556 | 0.383 | 0.444 | 0.91 |
| Resp (lung) | 1.667 | 0.558 | 0.333 | 0.82 |

ENSO dropped out: its mutual information is already exhausted by one full cycle, so there
is no retained signal above the noise floor to measure rent against (consistent with the
earlier finding that ENSO only holds memory at short anchors).

**Headline (correlation-led):**

- corr(ARA, rent) = **+0.41**   — prediction wanted this **NEGATIVE**.
- corr(2 − ARA, rent) = **−0.41** — prediction wanted this **POSITIVE**.
- MAE of the literal law rent = 2 − ARA = **0.350** (large, given rent spans 0.13–0.63).
- Best-fit line: rent = 0.084 + 0.27·ARA — *rising*, not falling.

## Honest read

**The law rent = 2 − ARA is not supported.** The relationship doesn't just miss the
slope — it leans the **opposite way**: higher-ARA (more harmonic) systems here shed
*somewhat more*, not less. The single cleanest contradiction is the balance point: EEG
sits at ARA ≈ 1.0, where the law predicts the **maximum** rent (→1), yet EEG shed the
**least** of all (0.13). The Sun (most harmonic of the slow systems) sheds a middling
0.49, not ~0.

With N = 5 and ENSO missing, none of this is statistically decisive in either direction —
a +0.41 correlation on five points is noise-compatible. But there is no signal pulling
*toward* the prediction.

## Two caveats that matter

1. **What "ARA" means here.** This ARA is the asymmetry of the *dominant smoothed cycle*,
   not the framework's structural snap class. The bandpass that locates the cycle also
   smooths away fast spikes (e.g. the ECG QRS), so a textbook "deep snap" can read near
   1.0 here. The two notions of ARA are not the same measurement, and that gap alone could
   wash out a real relationship.
2. **Rent anchored at one cycle** is the only anchor where all systems are comparable, but
   it's exactly where slow, dissipative systems (ENSO) have already lost their memory.

## Bottom line

Run without tuning. The clean, independent test of "rent = 2 − ARA" comes back **negative
to flat** on five real systems. The earlier, separate finding still stands on its own:
dissipative systems lose information as a *power law* per φ-rung (fractal memory) — but the
**value** of that loss does **not** line up with 2 − ARA. The intuition that the golden
engine is "most effective" at shedding, and the harmonic Sun retains everything, is not
visible in the measured numbers.
