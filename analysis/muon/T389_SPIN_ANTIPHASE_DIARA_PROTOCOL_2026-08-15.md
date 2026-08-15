# T389 — frozen spin anti-phase Di-ARA protocol

Date frozen: 2026-08-15 (Australia/Brisbane)

## Question

Does the population spin imprint recovered from the RAL Silver detector field contain a genuine two-axis anti-phase, rather than only the folded scalar cut used in T382?

## W5H and identity boundary

- **Who / where:** the same 300 K silver positive-muon population recorded by the 96 ISIS EMU detector histograms in investigation `10.5286/ISIS.E.RB1620201`. No medium or source identity changes from T382/T383.
- **What:** reconstruct the two signed calibration-frozen quadratures of the detector-share field. The geometric coordinates are
  \[
  x_c=1-c,\qquad x_s=1-s,
  \]
  where `c` and `s` are the detector-space cosine and sine projection coefficients. T382 retained only the folded phase cut `1-cos(theta)`; T389 tests the perpendicular companion explicitly.
- **When:** native 0.016 microsecond bins from 0.25 to 8.00 microseconds. Calibration is restricted to the frozen 20 G and 25 G runs. Primary scores use only the untouched 63 G, 160 G and 400 G holdout runs.
- **Where in ARA:** this is one child identity represented by a geometric Di-ARA. A full spin anti-phase is the simultaneous inversion
  \[
  (c,s)\mapsto(-c,-s),
  \qquad
  (x_c,x_s)\mapsto(2-x_c,2-x_s).
  \]
  A one-axis inversion is a reflection control, not the declared anti-phase.
- **Why:** determine whether the previously missing half is a real opposed spin branch in the measured detector relation. This test does not observe neutrinos and cannot by itself time an individual muon decay.
- **How:** fit cadence, relaxation and the 96-detector cosine/sine basis on calibration only. Project each untouched holdout detector-share slice into the frozen two-dimensional basis. Compare the observed vector after half a frozen spin period with full inversion, direct repetition, either one-axis reflection, and wrong temporal offsets.

## Frozen primary comparisons

For each holdout field, interpolate the projected complex vector `z=c+i s` at `t+qT`, where `T=1/(gamma B)` and `q` is a turn fraction. Weight each pair by the geometric mean of detector-summed counts.

1. At `q=0.5`, full inversion must have lower normalized vector error than direct repetition and both one-axis reflections in every holdout field.
2. The weighted complex correlation at `q=0.5` must have negative real part in every holdout field.
3. Across a frozen shift grid `q=0.30,...,0.70`, the most negative real correlation must lie within `0.50 +/- 0.05` for every holdout field.
4. A field-block bootstrap 95% interval for the pooled full-inversion advantage over the best competing mapping must lie above zero.

All four are required for a primary pass. Validation-run behaviour is reported as a prerequisite diagnostic and cannot replace a failed holdout gate.

## Claim boundary

T382's primary 96-detector child did not qualify. T389 is therefore an exploratory but frozen test of the same detector field in the two-axis geometry the earlier scalar cut omitted. A pass would support a measurable population spin anti-phase; it would not rescue T382 automatically, establish a universal Di-ARA, observe either neutrino, or produce single-muon advance prediction.

