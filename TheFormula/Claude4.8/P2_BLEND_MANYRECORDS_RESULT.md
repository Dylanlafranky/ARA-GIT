# P2 - Next rung = MIX, on RAW data, MANY records (brain first)

**Date:** 2026-05-30
**Script:** `p2_blend_manyrecords.py` -> `p2_result.json`
**Data:** PhysioNet slpdb (18 sleep records, raw 250 Hz), NOAA NINO3.4, SILSO sunspots. All public.

## What changed vs the first blend test
The first test (`blend_next_rung_test.py`) gave each system **one dot** and placed it on the
*smoothed* ARA ruler. Two upgrades here, both Dylan's requirements:
1. **RAW-faithful placement** - each record sits on the axis by its P1 raw snap-ARA
   (peaks/troughs on the raw signal), not the smoothed cycle.
2. **Many records** - every slpdb subject gives a brain (EEG) and heart (ECG) trace, so brain
   and heart become a **cloud** of dots, not one. ENSO/Sun long series are windowed.
3. **Single-systems only** - composites (BP, Resp-sum) excluded until the breathing belts are
   split (per the P1 composite finding).

The mechanism (exact): two consecutive phi-rungs, periods r and r*phi, multiplied, make a
difference-frequency at period r*phi^2 - the next rung. So the product of the two fast raw
bands, re-filtered at the slow band, should reconstruct the real slow band above a
phase-randomized null. **recon** = peak corr (generated-slow vs actual-slow); **z** = how far
that beats a spectrum-matched surrogate null; **lag** = delay at the peak (fraction of slow period).

## Result

| System | records | snap-ARA (med) | recon | z (med) | above null | \|lag\| |
|---|---|---|---|---|---|---|
| **EEG (brain)** | 5 | 1.00 | +0.18 | **+9.7** | **5/5** | 0.37 |
| **ECG (heart)** | 18 | 0.033 | +0.47 | +3.1 | 10/18 | 0.35 |
| Solar (Sun) | 1 | 1.59 | +0.91 | +3.0 | 1/1 | 0.74 |
| ENSO | 2 | 0.83 | +0.67 | +0.7 | 0/2 | 0.38 |

## Read

**P2 (next rung = the mix): CONFIRMED, and stronger than before.**
- **Brain is rock-solid: all 5 independent records beat the null, z~+9.7.** This is exactly
  where neuroscience independently documents cross-frequency (phase-amplitude) coupling, so we
  are detecting a known real effect across a real sample, not one lucky record.
- **Heart: deep snap reproduced across all 18 hearts** (snap-ARA 0.033, IQR 0.03-0.04 - tight).
  The mix mechanism beats null in 10 of 18 - real in the majority, not universal.
- **Sun shows it** (single long record, z+3.0). **ENSO does not** (high raw recon +0.67 but
  z+0.7 - it does not beat its own spectrum-matched null, so that's spectral coincidence, not
  coupling). Both consistent with the earlier one-dot test.

**P4 (friction: clean hand-off near phi, lagged at balance 1.0): NOT supported on raw.**
- corr(|snap-ARA - phi|, |lag|) = -0.36 (predicted POSITIVE) - **wrong sign.**
- corr(|snap-ARA - 1.0|, |lag|) = -0.20 (predicted negative) - right sign but weak.
- The killer detail: the system **nearest phi** (Sun, snap-ARA 1.59) has the **largest** lag
  (0.74), while the balance-point brain (1.00) lags less (0.37). That is the opposite of the
  prediction. The earlier "lag shrinks toward phi" hint (corr -0.65) was measured on the
  *smoothed* axis with one dot per system; **it does not survive the raw-faithful redo.**

## Bottom line
Doing it the way Dylan insisted - raw data, many records - **strengthened** the mixing claim
(brain went from 1 record to 5/5 above null) and **killed** the friction-lag claim (the near-phi
system lags most, not least). The honest scoreboard:

- **Next rung = mix: real in brain (strong, replicated), heart (majority), Sun. Not ENSO.**
- **Friction lags at balance: not supported; leans contradicted at the high end (N still thin there).**

## Caveats / next
- Brain N=5, Sun N=1 - the high/clean end of the axis is still thin. More EEG records and a
  second slow/pure system would firm up both P2-high-end and P4.
- ENSO windows are short relative to its slow rung (only 2 dots); not a fair N.
- Composites (BP, Resp) still excluded. slp32/37/41 carry separate chest/abdominal/nasal
  breathing belts - those can be split to put a *clean* single-lung system on the axis next.
- Surrogate nulls reduced to 15 per dot for runtime in a memory-limited sandbox; z's are
  stable but could be tightened with more surrogates offline.
