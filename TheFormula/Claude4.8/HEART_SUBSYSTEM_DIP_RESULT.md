# Heart sub-beat subsystems vs the mid-horizon dip (strict-causal, slp01a)

**Date:** 3 June 2026 · one subject (slp01a, PhysioNet slpdb, 2600 beats, 40 min, 250 Hz). Strict-causal
(features at beat i use only beat i's waveform; train 60%, score held-out rest; persistence baselined).

**Question (Dylan):** the ECG forecast loses to persistence in the 3–8 beat "dip." We had mapped the systems
*around* the heart (BP/Resp/EEG) but treated the heart itself as a black box (RR interval). Does breaking the
heart into its own **sub-beat subsystems** (within-beat ECG/BP morphology) lift the dip?

**Sub-beat features extracted per beat (causal):** ECG T-wave/QT systole fraction, within-beat energy centroid
(a within-beat ARA), ECG amplitude, BP systolic-upstroke timing, BP pulse pressure.

## Result — partial, honest

**(1) Routed through the framework's matched-rung aggregation (summed into torque): NO lift.** Dip unchanged
(h=3 Δ−0.011, h=5 Δ−0.033, h=8 Δ−0.005); on the fitted model it slightly *hurt* at h=5–8. The "look down =
messy" pattern held.

**(2) Routed DIRECTLY into the readout (morphology as its own features): real but small lift, only at short lead.**

| h (beats) | persistence | AR(RR lags) | AR + morphology | verdict |
|---|---|---|---|---|
| 1 | +0.897 | +0.898 | **+0.900** | morph tiny help, beats pers |
| **3** | +0.681 | +0.671 (below pers) | **+0.696** | **morph lifts AR PAST persistence** |
| 5 | +0.567 | +0.534 | +0.520 | nothing beats persistence (random-walk window) |
| 8 | +0.490 | +0.412 | +0.431 | morph helps a little, still below pers |
| 13 | +0.458 | +0.404 | +0.375 | nothing beats persistence |

## Two findings

- **The dip is not one thing.** At **h=3** it *was* the heart missing its own subsystems — adding within-beat
  morphology lifts the model from below persistence (+0.671) to above it (**+0.696 vs +0.681**). At **h=5/h=13**
  nothing (morphology, AR, or framework) beats persistence — a genuine near-random-walk window, an unpredictable
  perturbation passing through, **not** a missing feature.
- **The framework's matched-rung aggregation BURIED the sub-beat signal.** Same features, aggregated → no lift;
  used directly → help at h=3. For within-beat subsystems, direct features beat aggregation (operator lesson).

## Honest fences

One subject; the h=3 win is modest (+0.015 over persistence); small effects on a single record can be
record-specific. **Needs multi-subject replication (the 11-subject set) before it can be cemented or put on the
public page.** Status: promising, not headline. Scripts: `heart_subsystem_dip_test.py` (framework-routed),
`heart_subsystem_direct_test.py` (direct readout).

---

## REPLICATION across 17 slpdb records (3 June 2026)

Re-ran the **direct-readout** test (RR autoregressive lags vs RR lags + sub-beat ECG/BP morphology vs
persistence) on **all 17 slpdb records with waveforms** (slp01a…slp66; slp67 absent). Strict-causal, fetched
live via wfdb, train 60% / held-out rest, features at beat i from beat i's waveform only.

**Does morphology improve on RR-AR alone? (the core question)**

| horizon | morph lifts AR | mean(morph−AR) | morph beats persist | AR beats persist |
|---|---|---|---|---|
| h=1 | 15/17 | +0.027 | 14/17 | 11/17 |
| **h=3** (dip) | **13/17** | **+0.025** | 11/17 | 11/17 |
| h=5 | 10/17 | +0.023 | 11/17 | 12/17 |
| h=8 | 11/17 | +0.038 | 13/17 | 7/17 |
| h=13 | 14/17 | +0.070 | 10/17 | 7/17 |

**Findings (honest):**
- **The effect replicates.** Sub-beat morphology improves on RR-AR at h=3 in **13/17** records (binomial
  p ≈ 0.025 vs a coin-flip null); only 2 records were hurt (slp02b, slp14). Small but consistent.
- **Its value grows with horizon:** mean lift over AR rises +0.025 (h=3) → +0.070 (h=13). At long leads where
  the RR sequence has run out of memory (AR beats persistence in only 7/17 at h=8–13), morphology **recovers**
  it (morph beats persistence 13/17 at h=8). The heart's within-beat state carries information the interval
  sequence cannot — clearest where AR fades.
- **Strongest cases:** slp45 (pers −0.236 → AR +0.450 → morph +0.516), slp04 (pers −0.025 → +0.106 → +0.217).

**Crucial contrast:** unlike the 8-beat brain-lead (a gorgeous n=1 that **evaporated** on replication), this
effect **survives** replication across 17 subjects. The strict-causal protocol that killed the brain-lead lets
this one through.

**Honest fences:** the lift is **small** (mean +0.025–0.07); not universal (2–4 records neutral/hurt); numbers
are window-dependent (30-min sampto). It is a real, replicated, modest improvement — defensible to state as
"small consistent lift across 17 records," not as a large effect. Scripts: `heart_subsystem_replication.py`,
result `heart_subsystem_replication_result.json`.
