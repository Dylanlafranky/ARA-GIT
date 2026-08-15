# T386 — coupled Di-ARA muon-handover protocol

Frozen: 2026-08-15, before T386 outcome calculation.

## Question and claim class

Does coupling the already tested state/path Di-ARA to an independent
determinacy/relation Di-ARA recover causal information about the later visible
muon-decay handover that neither cut carries alone?

This is a **Class-D detector-proxy test** on individual stopped-muon
double-pulse records.  The liquid-scintillator voltage is not identified as a
direct neutrino measurement or as the muon's unobserved internal child.

The source was already opened by T385.  T386 is therefore a frozen
post-result extension with chronological validation and evaluation splits,
not a sealed external confirmation.  A larger dated BUAP archive remains the
appropriate external holdout if this instrument succeeds.

## W5H

- **Who / where:** eligible individual double-pulse waveforms in the same BUAP
  95 L liquid-scintillator apparatus used by T385.  There is no medium,
  detector or identity change.
- **What:** two ARA pairs calculated causally from samples already observed,
  followed by a ridge-centred coupling test.
- **When:** event-local time after the first-pulse recovery, with the final
  `128 ns` before the second-pulse minimum excluded from prediction.
- **Why:** T385's state/path points occupied principally the lower half of its
  declared Di-ARA and improved probability calibration without improving
  ranking.  T386 asks whether an unmeasured determinacy/relation pair supplies
  the missing independent relation.
- **How:** keep T385's source hash, pulse finder, eligibility, chronological
  row splits, balanced event weights and forecast labels.  Add the new causal
  coordinates below and compare nested frozen models.

## Direction declaration

For this test only:

- state radial coordinate `x_R`: `0 = contraction/retention`,
  `2 = expansion/movement`;
- state path coordinate `x_H`: `0 = recurrent/closing`, `2 = open/straight`;
- forecast coordinate `x_F`: `0 = locally predictable`,
  `2 = locally unresolved`;
- relation coordinate `x_L`: `0 = repeated/in-phase window shape`,
  `1 = linearly unrelated`, `2 = inverted/anti-phase window shape`.

Every coordinate has ridge `1`.  No universal quadrant visitation order and
no `1.25` landmark are gates.

## Frozen source, splits and outcome

- File: `MD10000Last.csv`
- SHA-256:
  `C2DC1E012FBDF0F3C5EC305E2D8E4DD1D87B05DF5CBA39B492189C0F7D5454CD`
- sample interval: `8 ns`
- engineering rows: `0:500`
- calibration rows: `500:2000`
- chronological validation rows: `2000:3500`
- internal evaluation rows: `3500:end`

As in T385, a feature endpoint is positive when the later pulse minimum is
`128–384 ns` ahead, negative when it is at least `640 ns` ahead, and excluded
from fitting in the `384–640 ns` ambiguity interval.  Row length, distance to
record end, second-pulse location and any sample inside the `128 ns` guard are
forbidden predictors.

## First Di-ARA: state and path

T386 retains the T385 definitions over adjacent `128 ns` windows:

\[
x_R=\frac{2s}{1+s},\qquad
s=\frac{\operatorname{RMS}(current)+\epsilon}
        {\operatorname{RMS}(previous)+\epsilon},
\]

and

\[
x_H=\frac{2D}{L+\epsilon},
\]

where `D` is direct displacement and `L` is total path length in the declared
two-delay embedding.

## Second Di-ARA: determinacy and relation

### Causal forecast coordinate

Fit an affine AR(2) model to the **previous** 128 ns window only.  Use it for
one-step predictions across the current window, always conditioning only on
samples earlier than the predicted sample.  Compare its current-window RMSE
with a one-step persistence predictor:

\[
q_F=\frac{\operatorname{RMSE}_{AR(2)}+\epsilon}
          {\operatorname{RMSE}_{persistence}+\epsilon},\qquad
x_F=\frac{2q_F}{1+q_F}.
\]

Thus `x_F<1` means the local history is more predictable than persistence;
`x_F>1` means it is less predictable.  Ridge `1` is equal forecast error.

### Window-relation coordinate

Let `r` be the Pearson correlation between the detrended previous and current
128 ns windows.  If either window has negligible variance, set `r=0` rather
than inventing a direction.  Define

\[
x_L=1-r.
\]

This maps identical window shape to `0`, no linear relation to `1`, and exact
inversion to `2`.  It is a relation-orientation cut, not a probability of
rationality.

## Coupling

The two Di-ARAs remain separately visible.  Their paired ridge-centred
couplings are

\[
C_{RF}=(x_R-1)(x_F-1),\qquad
C_{HL}=(x_H-1)(x_L-1).
\]

These are not treated as new energy.  They measure whether the two cuts depart
from their ridges together and with what orientation.

## Frozen model ladder

All models include the same regularized logistic fitting and event-balanced
weights used by T385.

1. `M0`: intercept only.
2. `MT`: elapsed time only.
3. `MG`: elapsed time plus ordinary raw waveform/path covariates.
4. `MS`: `MG` plus the state/path Di-ARA and its causal changes.
5. `MD`: `MG` plus the determinacy/relation Di-ARA and its causal changes.
6. `MC0`: `MG` plus both Di-ARAs without cross-coupling terms.
7. `MC`: `MC0` plus `C_RF` and `C_HL`.
8. `MLEAK`: acquisition row length and remaining buffer, audit only.

`MC0 -> MC` tests coupling rather than mere additional measurement.

## Primary gates

Call the coupled predictive claim **supported** only when all hold:

1. `MC` improves weighted log loss and Brier score over `MG` on both
   chronological validation and evaluation;
2. `MC` improves AUC over `MG` by at least `0.02` on both splits;
3. `MC` has lower log loss than `MS`, `MD` and `MC0` on both splits;
4. on evaluation, a 500-replicate event-cluster bootstrap of log-loss
   improvement over the best component selected on validation has a 95%
   interval wholly above zero;
5. the observed same-time coupling beats 100 determinacy-coordinate shuffles
   made within target and coarse lead bins;
6. no forbidden acquisition field or guarded sample enters a primary feature.

If only proper-score calibration improves, report **calibration structure,
not predictive handover support**.  If `MC0` performs as well as or better than
`MC`, the extra coordinates may carry information but their declared coupling
is not supported.

## Separate retrospective map

After scoring, align eligible evaluation events to the second-pulse minimum
and map all four coordinates through the guard, at `1024, 512, 384, 256, 128,
64, 32, 0, -32, -64 ns` lead.  This is a descriptive detector-handover map.
It may show what happens at release but cannot be called advance prediction.

## Required controls and outputs

- time-reversed inter-pulse history, scored with the frozen `MC` model;
- within-lead determinacy-coordinate alignment shuffles;
- forbidden acquisition leakage audit;
- labelled `0–2` axes, ridge `1`, units, sample counts and guard annotation;
- model scores, event-cluster uncertainty, causal lead profiles and the
  retrospective event-centred trajectories saved in machine-readable files;
- an independent validator that recomputes the headline gates.

