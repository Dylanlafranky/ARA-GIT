# T356 — frozen plain-ARA physical parent-ridge transfer

**Frozen:** 11 August 2026, before the registered velocity endpoints were calculated  
**Test ID:** `T356-PLAIN-ARA-PHYSICAL-PARENT-RIDGE-v1`  
**Representation:** public laboratory pendulum data; prospective endpoint on previously opened records

## 1. Question

Can two opposite, directly observed child landmarks locate a physical parent
event by their relation alone?

For one pendulum arm, let consecutive angular reversals occur at
`t_L` and `t_R`. These are the two opposite child landmarks of one local
half-swing. Plain ARA predicts the parent ridge at their unweighted relational
centre:

\[
\widehat t_{\rm ridge}=\frac{t_L+t_R}{2}.
\]

No pendulum equation, velocity value, learned weight, offset or fitted timing
correction enters this prediction.

Only after the prediction is fixed is the separately stored angular-velocity
channel opened. Its largest absolute value inside the same half-swing defines
the physical referee:

\[
t_{\rm flow}=\arg\max_{t_L<t<t_R}|\dot\theta(t)|.
\]

The test therefore asks whether the two child cuts locate the independently
recorded maximum-flow event between them.

## 2. Data and splits

Public dynamicslab *MultiArm-Pendulum* archive, Zenodo
`10.5281/zenodo.6633719`.

- free-swing runs `run1`, `run2`, `run3`, arms 1–3;
- driven transfer run `triple1`, arms 1–3;
- raw angle and raw recorded angular velocity at `1,000 Hz`
  (`decimate=10` from the 10 kHz source).

The archive and broad pendulum behaviour have been analysed before. The
specific endpoint—predicting recorded peak-flow times from reversal-pair
midpoints—was not previously scored. This is therefore a frozen physical
transfer, not a pristine-data discovery.

## 3. Predictor-only event construction

Each arm is centred on its circular-mean resting angle. Turning points are
detected from the angle channel only using the already audited detector:

- maxima of the centred angle and maxima of its negative;
- prominence floor `0.02*pi` radians (`0.02` ARA units);
- minimum separation `0.4*1.333 s`;
- consecutive accepted turns must have opposite signs;
- edge intervals with fewer than five interior samples are rejected.

Velocity is inaccessible while these events and predictions are constructed.

## 4. Registered predictions and controls

For each eligible half-swing:

1. **plain ARA:** `(t_L+t_R)/2`;
2. **left child alone:** `t_L`;
3. **right child alone:** `t_R`;
4. **wrong relation:** midpoint of `t_L` and the right-hand turn from the next
   eligible half-swing, scored against the current physical referee.

The primary normalized timing error is

\[
E=\frac{|\widehat t-t_{\rm flow}|}{t_R-t_L}.
\]

The velocity retained at the predicted ridge is also reported:

\[
F=\frac{|\dot\theta(\widehat t_{\rm ridge})|}
        {\max_{t_L<t<t_R}|\dot\theta(t)|}.
\]

`F` describes the physical identity exposed at the predicted location. It is
not used to move the prediction.

## 5. Frozen gates

The free-swing result is **SUPPORTED IN THIS PENDULUM CUT** only if all gates
pass:

- **G1 absolute location:** pooled median `E_plain < 0.10`;
- **G2 tail:** pooled 95th-percentile `E_plain < 0.25`;
- **G3 two-child necessity:** `E_plain` is at least 50% lower than each
  single-child median;
- **G4 correct relation:** `E_plain` is at least 50% lower than the wrong-pair
  median;
- **G5 directional transfer:** median `E_plain < 0.12` separately for
  increasing-angle and decreasing-angle half-swings;
- **G6 replication:** at least 8 of the 9 `(run, arm)` groups have median
  `E_plain < 0.12`;
- **G7 physical ridge:** pooled median retained-flow fraction `F > 0.90`.

The driven record is a transfer endpoint and cannot change the free-swing
verdict. Its errors and flow fraction are reported under the same fixed rule.

## 6. Uncertainty and displays

- Event bootstrap, `10,000` resamples, seed `20260811`, for pooled medians and
  their 95% intervals.
- Report every run/arm and both directions; do not suppress poor groups.
- Static figure: representative raw half-swings, prediction-versus-referee,
  control errors, and group replication.
- Machine-readable event, summary, result and validation files.

## 7. Claim boundary

A pass would show that the plain ARA relational-centre rule transfers from the
controlled T355 construction to a public physical oscillator, and would
identify the recovered parent event as the local maximum-flow ridge between
two reversals. It would not prove universal ARA, establish that every physical
parent is a velocity maximum, or discover new pendulum mechanics. A failure
would count against this literal physical translation of the T355 rule.

