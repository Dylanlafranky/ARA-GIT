# T337 — Di-ARA traversal direction predictor

**Frozen:** 3 August 2026, after T336 and before T337 scoring  
**Status:** post-T336 hypothesis; fixed retrospective ENSO replay  
**Primary horizon:** 6 months  
**Primary challenger:** continuous signed traversal (`base_turn`)

## Why this test is separate from T336

T336 rejected the full radial-plus-turn handover as a direct NINO3.4 value
decoder. Its frozen ablations nevertheless showed that signed traversal
survived much better than radial contraction/expansion, while some handover
forms improved direction and worsened magnitude.

T337 freezes that narrower post-result question. It cannot change T336's
negative verdict.

## Target

For forecast origin `t` and horizon `h`:

\[
y_{t,h}=\operatorname{sign}(T_{t+h}-T_t)\in\{-1,+1\}.
\]

Rows with exactly zero observed change are excluded from fitting and scoring.
The task is directional classification, not point-value forecasting.

## ARA identity and features

Use the exact T336 coupled identity and causal feature construction:

\[
z_t=T_t+iR_t,
\]

with octave lags `m = 1, 2, 4`, centred reciprocal radius

\[
a_{t,m}=\tanh\!\left(\frac12\log\frac{|z_t|}{|z_{t-m}|}\right),
\]

and signed traversal

\[
\delta_{t,m}=\frac{\arg(z_t\overline z_{t-m})}{\pi}.
\]

The primary `base_turn` challenger adds only the three continuous
`delta` values to the raw level/state model. Full Di-ARA, radius-only,
quadrant-only and broken-lineage forms remain declared secondary controls.

## Fixed decoders and controls

Each learned model uses fixed ridge penalty `lambda=1` to regress the signed
training labels `-1/+1`; the forecast class is the sign of its score.

1. `past_trend`: sign of the preceding same-horizon NINO3.4 change.
2. `base_levels`: T336 raw-state lags and annual clock.
3. `base_raw_movement`: levels plus ordinary surface/reservoir changes.
4. `base_turn`: levels plus the three continuous signed traversal cuts.
5. `base_diara`: levels plus radius and traversal.
6. `base_radius`: levels plus radius only.
7. `base_quadrant`: levels plus coarse four-sector labels.
8. `base_broken_diara`: full handover with reservoir shifted by 12 months.

No threshold, lag, penalty or model is tuned after scoring.

## Data, split and causality

Use the same public monthly NINO3.4 and NOAA/PMEL WWV files as T336, the same
January 2008 walk start, the same January 2017 replay boundary and horizons
`3,6,9,12`. A training row is admitted only when its future label is already
known at the current origin. Scaling uses only information available at that
origin.

The replay period has been studied previously. This is not a pristine
outside-domain confirmation.

## Metrics

Report:

- balanced accuracy (primary);
- ordinary accuracy;
- positive- and negative-direction recall;
- rank AUC from the continuous score;
- number of non-zero-change origins.

Use a paired 12-month moving-block bootstrap with `5,000` repetitions and
seed `20260803` for the primary six-month balanced-correctness improvement of
`base_turn` over `base_levels` and `base_raw_movement`.

## Frozen gates

### Supported on this replay

At six months in the 2017+ replay holdout:

1. `base_turn` exceeds both `base_levels` and `base_raw_movement` by at least
   `0.02` balanced-accuracy points;
2. its ordinary accuracy is not lower than either control;
3. the 95% block-bootstrap interval for improvement over raw movement lies
   wholly above zero;
4. broken lineage does not equal or beat `base_turn` in balanced accuracy.

### Provisional

The first, second and fourth gates pass, but the bootstrap interval includes
zero.

### Not supported in this form

The primary `0.02` balanced-accuracy improvement fails, ordinary accuracy is
lower, or broken lineage matches/exceeds the primary challenger.

## Interpretation fence

A positive result would support signed Di-ARA traversal as a directional
coordinate in this fixed ENSO replay. It would not prove a universal
handover law, operational forecast superiority, causal control of ENSO, or
exact amplitude prediction.

