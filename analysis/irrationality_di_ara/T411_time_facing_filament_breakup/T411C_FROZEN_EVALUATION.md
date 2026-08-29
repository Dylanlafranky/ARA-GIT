# T411C frozen evaluation — time-facing filament handover

## Outcome first

T411C **recovers a real moving handover**, but the frozen result supports the
narrow claim more strongly than the broad one.

- It strongly supports the ARA rate coordinate as a crosswalk of the known
  mechanical-to-capillary handover in an evolving filament.
- It does not support the stronger claim that the ordered residual contains a
  distinct, additional time-navigator signal beyond its broad rate structure.
- Gravity did not explain the main result under the frozen controls, but this
  vertical apparatus is not gravity-free and therefore cannot prove that
  gravity is absent.

## Frozen holdout scorecard

The S2/S4 holdout was opened once after
`T411C_FROZEN_PARAMETERS.json` was written.

| Frozen gate | Required | Holdout result | Verdict |
|---|---:|---:|---|
| Source-complete runs | coverage >= 0.90 | 86 / 106 | qualification |
| Persistent ridge crossing | >= 75% | 82 / 86 = **95.35%** | pass |
| Median handover location | 0.40076–0.73496 | **0.64485** | pass |
| Temporal ordering | observed median rho > shifted q95 | 0.83051 vs **0.84242**, p=0.2607 | **fail** |
| Initial Bond-number dependence | abs(rho) <= 0.35 | **0.10587** | pass |
| Height-sensitive gravity proxy | abs(rho) <= 0.35 | **0.31720** | pass, near boundary |
| S2 1 mm vs 2 mm median handover | difference <= 0.15 | 0.58885 vs 0.63505; difference **0.04620** | pass |

The overall 2 mm median in the raw result JSON also contains S4. The frozen
plate-size comparison is therefore evaluated within S2, where both sizes are
present.

## What the coordinate measured

The ARA coordinate was

\[
x_{rate}=2\frac{r_I}{r_M+r_I},
\]

with

\[
r_M=-\frac{dD_M}{dt},\qquad
r_I=-\frac{dD_{obs}}{dt}-r_M.
\]

The ridge \(x_{rate}=1\) is therefore exactly the moment at which the inferred
additional current thinning rate equals the mechanically imposed current
thinning rate.

This is the time-facing cut that the earlier droplet analysis lacked: it
follows one neck through its lifetime rather than comparing already resolved
shapes across a perpendicular spatial cut.

## Secondary physical crosswalk (declared post-hoc)

After scoring the frozen gates, the observed ARA ridge was compared with the
independent published capillary-rate estimate

\[
r_C=\frac{2\alpha\sigma}{\mu},\qquad \alpha=0.0709.
\]

For each holdout run, the model-only equality \(r_M(t)=r_C\) predicted the
observed ARA crossing with:

- **Spearman rho = 0.70346** across 82 crossings;
- **median absolute error = 0.06155** of one direct breakup lifetime;
- **median signed error = +0.00876**;
- theoretical median \(u=0.64562\), versus observed median \(u=0.64485\).

This comparison is not a frozen discovery gate and must not be represented as
one. It is a strong diagnostic that the instrument recovered the established
mechanical-to-capillary transfer. The capillary estimate was not used to set
the crossing position, although it was used to choose a physically scaled
smoothing window.

## ARA reading

In ARA language, the experiment contains two current contributions at the
chosen cut:

1. the plate-imposed thinning contribution;
2. the additional/capillary-dominated thinning contribution.

They begin asymmetrically, approach one another and commonly cross their
compressed parent ridge before direct breakup. The handover is not a universal
constant: the median shifts with fluid identity, while the 0–2 relation and
equal-rate ridge remain the stable geometric bookkeeping.

The failed shift gate matters. Circularly shifting the residual preserved
enough of its broad rate structure that chronological order was not uniquely
better in the holdout. Therefore this test does **not** isolate an independent
irrationality navigator or a time force. It shows that the ARA instrument
faithfully locates a physical rate handover when the cut is aligned with the
evolution.

## Gravity boundary

The result is inconsistent with a simple “this is only gravity” explanation:

- the inferred handover remained similar across the 1 mm and 2 mm S2 plate
  groups;
- initial Bond number weakly predicted handover position;
- the ARA analysis contains no gravity term;
- an independent non-gravity mechanical/capillary rate equality predicted the
  observed handover closely.

But the apparatus is vertical, the height-sensitive proxy approached the
predeclared limit, and the source paper notes late-filament slumping. The
scientifically safe claim is therefore **gravity-controlled, not gravity-
eliminated**.

## Claim class

**Supported empirical crosswalk / unresolved broader mechanism.**

The time-facing ARA cut works as an instrument for this physical transition.
The universal Irrationality Di-ARA interpretation remains an open hypothesis
and needs a second longitudinal system with an independently measured pair of
competing rates, preferably in a horizontal or microgravity-compatible setup.

