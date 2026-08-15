# T384 — Irrationality Di-ARA information-lock test

**Frozen:** 15 August 2026, before T384 outcome scoring  
**Source:** the same RAL Silver 96-detector records used by T382/T383  
**Medium change:** none  
**Purpose:** test whether retained path relation supplies information that the
population parent and fixed child cadence do not contain separately.

## WHO — declared identities

1. **Parent (P):** the detector-summed muon population from T382.
2. **Child (C):** the time-varying 96-detector share pattern, projected onto
   a two-axis detector plane fitted on calibration runs only.
3. **Relation (R_{PC}):** the ordered path of the joint parent/child state,
   measured with the Irrationality Di-ARA radial and turning cuts.

No neutrino is directly observed. A passing result concerns population-scale
child tracking and handover localization, not individual neutrino prediction.

## WHAT — exact ARA coordinates

The parent coordinate remains

\[
x_P(t)=2\left(1-e^{-t/\tau}\right),
\]

where \(\tau\) is fitted on the six 20/25 G calibration runs only.

The T382 open-loop child reference remains

\[
\theta_M(t)=2\pi\gamma Bt+\phi_0,
\qquad
x_{C,M}(t)=1-\cos\theta_M(t),
\]

with \(\gamma,\phi_0\) frozen from calibration.

For the observed child, detector-share residuals are projected onto a
calibration-frozen two-axis detector plane. Its two coefficients form

\[
z_C(t)=c_1(t)+i c_2(t),
\qquad
x_{C,O}(t)=1-\cos\arg z_C(t).
\]

The joint parent/child position is

\[
w(t)=\bigl(x_P(t)-1\bigr)+i\bigl(x_{C,O}(t)-1\bigr).
\]

For adjacent valid readings,

\[
q_t=\frac{w(t)}{w(t-1)},
\qquad
x_L(t)=\frac{2|q_t|}{1+|q_t|},
\qquad
x_T(t)=1+\frac{\arg q_t}{\pi}.
\]

Here (x_L) is the contraction/expansion ARA and (x_T) is the
reverse/forward turning ARA. Their four sign combinations are retained as the
Irrationality Di-ARA direction address. No Phi, (e), or fitted universal
constant is imposed.

## WHEN — frozen splits and chronology

- **Calibration:** EMU00066572–EMU00066577, fields 20/25 G.
- **Validation:** EMU00066571 and EMU00066584, fields 25/20 G.
- **Holdout:** EMU00066578–EMU00066580, fields 63/160/400 G.
- **Diagnostic only:** 1000/2000/4000 G records.

The detector plane, parent lifetime, child cadence, amplitude threshold,
relation lookup and all orientations are fixed from calibration. Validation and
holdout values cannot change them.

Complete child cycles are declared by the frozen model phase, not by searching
the observed child for favourable boundaries. Each cycle is resampled to 17
equal phase fractions, including both boundaries and the exact half-cycle.
During recursive recovery only the first two observed child readings are
revealed. A cycle is admissible only when at least 75% of its resampled child
amplitudes exceed the calibration-frozen amplitude threshold.

## WHERE — information-lock geometry

The reconstruction uses the shared parent/child Di-ARA plane with ridge
\((1,1)\). The full relation packet at reading (t) is

\[
\mathcal I_t=
\left(
x_P,
x_C,
\Delta x_P,
x_L,
x_T,
Q
\right)_t,
\]

where (Q) is the causal direction address from the parent's outgoing step and
the child's already-observed or already-reconstructed incoming step.

## WHY — falsifiable claim

T382 recovered the parent but its calibration-frozen 96-detector child did not
generalize. T383 found an exact 7.5-cycle discovery landmark at 63 G, but the
literal count and half-cycle alignment did not transfer across fields.

T384 asks whether those failures occurred because the fixed parent and cadence
discarded the changing relation history. If (R_{PC}) is a genuine third
information component, then (P+R_{PC}), starting from the child's entry
state, should reconstruct later child movement better on untouched records.

## HOW — causal recorder and controls

### Primary recorder

Store calibration transitions under

\[
(x_P/2,\;x_C/2,\;\Delta x_P/s_P,\;x_L/2,\;x_T/2,\;Q)
\longmapsto \Delta x_C,
\]

where (s_P) is the calibration 90th percentile of nonzero
\(|\Delta x_P|\). Retrieve the nine nearest same-address transitions and use
their median \(\Delta x_C\). If no same-address transition exists, use the
nearest transition across addresses and record the fallback.

### Required comparisons

1. **Open-loop T382:** (x_{C,M}(t)).
2. **Linear persistence:** continue the last observed/reconstructed child step.
3. **Parent/child state only:** omit (x_L,x_T,Q).
4. **Direction-only Di-ARA:** retain (Q), omit (x_L,x_T).
5. **Wrong relation:** permute calibration relation targets within direction
   address using frozen seed 384.
6. **Full Irrationality Di-ARA:** retain all declared fields.

### Two scoring levels

1. **Navigator:** teacher-forced one-step prediction, where the true past child
   is available but the next child is hidden.
2. **Restorer:** recursive within-cycle reconstruction from only the first two
   child readings.

Score ARA RMSE, waveform correlation, child-step direction agreement,
four-address agreement, turning-point error and endpoint error. Aggregate first
within run, then across runs; cycles are not treated as independent experiments.

## Frozen gates

The information-lock claim is supported on this source only if:

1. **Observed-child readability:** calibration and both validation runs have
   median detector-plane amplitude above the frozen calibration 10th-percentile
   amplitude threshold.
2. **Local navigation:** on both validation runs and at least two of three
   holdouts, the full recorder has one-step RMSE at least 0.05 ARA units lower
   than state-only and direction-only, with direction agreement at least 0.75.
3. **Wrong-relation control:** full-recorder median one-step RMSE is at least
   0.05 lower than the wrong-relation control on validation and holdout.
4. **Recursive restoration:** on both validation runs and at least two of three
   holdouts, median cycle waveform correlation is at least 0.80 and RMSE at
   most 0.30 ARA units.
5. **Information-lock contribution:** the full recorder improves recursive
   RMSE by at least 0.05 ARA units or direction agreement by at least 0.05 over
   direction-only on both validation runs and at least two holdouts.

The exact arithmetic identity of a constructed remainder is not a pass. The
third relation must improve untouched prediction.

## T383 7.5-cycle tail audit

The T383 common parent coordinate is retained unchanged. The raw tail at that
time is scored only if the background-subtracted detector-summed signal in the
nearest native bin has

\[
\mathrm{SNR}=\frac{S}{\sqrt{S+B}}\ge3.
\]

If admissible, report open-loop, observed and Di-ARA-reconstructed child ARA at
the landmark for 63/160/400 G. This tail audit cannot rescue a failed primary
information-lock gate and is labelled unavailable when the SNR gate fails.

## Interpretation boundary

- **Pass:** the retained parent/child path contains independently useful
  chronological information at population scale.
- **Navigator-only pass:** the relation locates the next local movement but
  accumulated errors prevent full hidden-cycle restoration.
- **Fail:** adding the path relation does not rescue the non-general child.

None of these outcomes establishes direct neutrino observation or event-level
neutrino timing.
