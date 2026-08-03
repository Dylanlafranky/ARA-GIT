# T336 — reciprocal/log Di-ARA ENSO handover predictor

**Frozen:** 3 August 2026, before scoring this implementation  
**Status:** fixed retrospective replay; not a pristine untouched-domain test  
**Primary horizon:** 6 months  
**Primary replay holdout:** forecast origins from January 2017 onward

## Question

Does the newly clarified native ARA handover coordinate improve causal
prediction of a complex system, rather than merely redescribing its completed
motion?

The test uses ENSO because TheFormula already has a public-data forecasting
history, a physically meaningful subsurface driver and hard negative controls.
The result therefore cannot be promoted as a first exposure to ENSO. It is a
new, frozen transformation tested on a heavily studied domain.

## Declared ARA identity

At each month, the two-axis ENSO identity is

\[
z_t=T_t+iR_t,
\]

where:

- \(T_t\) is the train-only-standardised NINO3.4 surface anomaly;
- \(R_t\) is the train-only-standardised full-basin warm-water-volume
  reservoir, formed as western WWV plus eastern WWV.

For octave lag \(m\in\{1,2,4\}\), the handover from \(t-m\) to \(t\) is

\[
s_{t,m}=\frac{|z_t|+\epsilon}{|z_{t-m}|+\epsilon},
\qquad
u_{t,m}=\log s_{t,m},
\]

\[
a_{t,m}=\tanh\!\left(\frac{u_{t,m}}2\right)
=\frac{s_{t,m}-1}{s_{t,m}+1},
\qquad
\delta_{t,m}=\frac{\arg(z_t\overline{z}_{t-m})}{\pi}.
\]

In the project's 0–2 language, \(x_{t,m}=1+a_{t,m}\). Thus:

- \(a<0\): contraction / Phase-A side;
- \(a>0\): expansion / Phase-B side;
- \(\delta<0\): reverse traversal;
- \(\delta>0\): forward traversal.

The six primary Di-ARA features are the two native cuts
\((a_{t,m},\delta_{t,m})\) at the three octave lags. No Phi value, Fourier
transform, fitted endpoint or hand-shaped waveform is inserted.

## Data and causal boundary

- NINO3.4 monthly anomaly: local public NOAA/PSL copy
  `TheFormula/Claude4.8/nino34_long_anom.csv`.
- Western and eastern WWV anomalies: local NOAA/PMEL copies
  `TheFormula/Claude4.8/wwv_west.dat` and `wwv_east.dat`.
- Common monthly range is determined by the files at run time.
- Forecast origins start in January 2008.
- For an origin \(t\) and horizon \(h\), a training row \(j\) is allowed only
  when \(j+h\le t\). The target at \(t+h\) is never used in fitting,
  centring, scaling or feature selection.
- Every centring/scaling quantity is recomputed from information available at
  the forecast origin only.

Origins from 2008–2016 are reported as evaluation. Origins from 2017 onward
are the fixed replay holdout. Because those ENSO years have appeared in earlier
TheFormula development, the word *holdout* here means code-level fixed replay,
not pristine scientific confirmation.

## Fixed models

All fitted models use the same direct-horizon ridge regression with fixed
penalty \(\lambda=1\). No penalty, lag, feature or horizon is tuned after
scoring.

1. `climatology`: training-target mean.
2. `persistence`: current NINO3.4 value.
3. `base_levels`: NINO3.4, west-WWV and east-WWV at lags
   `0,1,2,4,8,12`, plus the known annual sine/cosine clock.
4. `base_raw_movement`: `base_levels` plus the six raw, standardised movements
   \((\Delta T,\Delta R)\) at lags `1,2,4`.
5. `base_diara`: `base_levels` plus the six native handover features
   \((a,\delta)\) at lags `1,2,4`.
6. `base_radius`: `base_levels` plus only the three contraction/expansion
   features \(a\).
7. `base_turn`: `base_levels` plus only the three signed-turn features
   \(\delta\).
8. `base_quadrant`: `base_levels` plus one-hot membership in the four Di-ARA
   sectors at each octave lag.
9. `base_broken_diara`: the same six handover features, but NINO3.4 at month
   \(t\) is paired with reservoir state from \(t-12\). This is the declared
   broken-lineage control.

The primary comparison is `base_diara` versus both `base_levels` and
`base_raw_movement`. `base_broken_diara` tests whether intact contemporaneous
surface–reservoir coupling matters.

## Horizons and metrics

Frozen horizons are 3, 6, 9 and 12 months. The 6-month result is primary.

For each split and model report:

- MSE skill versus climatology,
  \(1-\mathrm{MSE}_{model}/\mathrm{MSE}_{climatology}\);
- MAE;
- Pearson correlation;
- direction accuracy for \(T_{t+h}-T_t\);
- number of forecast origins.

A paired moving-block bootstrap with 12-month blocks and seed `20260803`
estimates the 95% interval for the 6-month holdout MSE improvement of
`base_diara` over `base_raw_movement` and `base_levels`.

## Frozen verdict gates

### Supported on this replay

At 6 months on the 2017+ replay holdout:

1. `base_diara` has higher climatology skill and lower MAE than both
   `base_levels` and `base_raw_movement`;
2. its paired MSE improvement over `base_raw_movement` is positive with a
   95% moving-block bootstrap interval wholly above zero;
3. `base_broken_diara` does not equal or beat `base_diara` on both skill and
   MAE.

### Provisional

The point estimates favour `base_diara` over both main controls, but the
bootstrap interval includes zero, or the broken-lineage control remains too
close to distinguish.

### Not supported in this form

`base_diara` fails to improve on `base_raw_movement` in either climatology
skill or MAE at the primary horizon, or the intact relation is matched by the
broken-lineage control.

## Interpretation fence

A positive result would show that the reciprocal/log contraction–expansion
cut crossed with signed traversal is a useful forecast coordinate for this
ENSO replay. It would not prove universal ARA, causal control of ENSO, a
universal radial amplitude, or superiority to operational climate models.

A negative result would reject this direct two-axis handover predictor without
rejecting ARA as a descriptive coordinate or other child/parent boundaries.

