# T391 — frozen raw-detector anti-phase protocol

**Frozen before holdout scoring:** 2026-08-15.

## Who / where

- Same identity and medium as T382/T389/T390: the population muon-spin signal recorded by the 96 detector histograms of the ISIS EMU RAL Silver experiment at 300 K.
- Source: DOI `10.5286/ISIS.E.RB1620201`.
- Calibration fields: 20 G and 25 G only.
- Diagnostic validation fields: 20 G and 25 G held outside calibration.
- Untouched primary holdouts: 63 G, 160 G and 400 G.
- Native analysis window: 0.25–8.00 microseconds.

## What

Test whether the anti-phase recovered by T389 exists in the **raw 96-detector share field**, rather than being manufactured by T389's learned cosine/sine decoder.

For each run, detector counts are converted to detector shares and each detector's run-wide share is removed. The resulting vector

\[
\mathbf y(t)\in\mathbb R^{96}
\]

is the measured population detector pattern. No learned detector projection, cosine axis, sine axis or detector amplitude is used in the primary score.

The only inherited calibration quantity is the cadence coefficient

\[
\widehat\gamma=0.01382\ \mathrm{MHz/G},
\]

learned from the six 20/25 G calibration runs before the primary fields are scored. Each raw run is phase-folded at

\[
T_B=\frac{1}{\widehat\gamma B}
\]

into 48 equal spin-phase bins. Folding is a time alignment and averaging operation, not a learned spatial decoder.

## ARA identity, rung and direction

- **Identity:** population spin orientation as carried by the full 96-detector daughter-share pattern.
- **Rung:** the same population-spin child validated in T389; this is not an individual-muon or neutrino event cut.
- **Direction:** T389's Phase A orientation advances through one spin cycle. Its proposed Phase B/anti-phase is the raw detector-pattern inversion reached after half a cycle.
- **ARA statement:** after a half-turn, a raw pattern and its anti-phase should obey

\[
\mathbf y(\theta+\pi)\approx-\mathbf y(\theta).
\]

Equivalently, after any common 0–2 display normalization, every detector component maps as `x -> 2-x`.

## When / how

For every holdout field:

1. Phase-fold the raw 96-detector residual shares into 48 bins using only the calibration-frozen cadence.
2. Pair each of the first 24 phase bins with the bin exactly half a turn later.
3. Compare four frozen mappings using weighted normalized RMS error:
   - full inversion: `-y`;
   - direct repetition: `+y`;
   - first detector bank inverted only;
   - second detector bank inverted only.
4. Measure the raw weighted cosine correlation at the half-turn.
5. Sweep temporal shifts from 0.30 to 0.70 turns in 0.01-turn increments and locate the most negative correlation.
6. Compare the correct detector correspondence with all 95 non-zero cyclic detector-label shifts.
7. Re-fold each record using each of the other two holdout fields as a deliberately wrong cadence control.
8. Bootstrap paired phase bins within fields and fields as blocks to estimate the uncertainty of the full-inversion advantage over its best mapping competitor.

Unfolded native-bin comparisons are retained as a diagnostic only. They are not a primary gate because count noise is not averaged at that grain.

## Frozen primary gates

All six must pass:

1. Full inversion has lower error than direct repetition and both one-bank inversions in every holdout field.
2. Half-turn raw-pattern correlation is negative in every holdout field.
3. The most negative temporal correlation lies at `0.50 ± 0.05` turns in every holdout field.
4. The correct detector correspondence has lower inversion error than the 5th percentile of the 95 wrong detector-label shifts in every holdout field (it beats at least 95% of shifts).
5. The correct cadence has lower inversion error than both wrong-field cadence controls in every holdout field.
6. The hierarchical-bootstrap 95% lower bound for the mean full-inversion advantage is greater than zero.

## Why / future relation

A pass would establish that the anti-phase is already present in the measured detector field before it is compressed into T389's two-axis Di-ARA coordinate. A failure would restrict T389: its anti-phase would be principally a property of the calibrated low-rank decoder, not a directly recovered 96-component field inversion.

Neither outcome tests whether spin triggers muon decay or neutrino creation. That requires event-linked individual or small-ensemble parent/daughter data at a lower rung.

