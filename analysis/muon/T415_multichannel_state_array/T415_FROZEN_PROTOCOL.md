# T415 — multichannel ARA state array for later muon release

## Status and boundary

This protocol is frozen before reading the T415 validation outcomes. It uses
the existing public ISIS EMU histogram archive from T413/T414. The source is
an ensemble delay histogram, not a continuous record of an individual muon.
Accordingly, T415 tests future **ensemble release-profile prediction**. It
does not test an individual neutrino timestamp.

The T414 development and validation runs have already been used in the wider
research programme. T415 therefore remains a prospective extension within a
reused archive, not a fully independent external confirmation.

## Relational cut

- **Parent:** population maturity/release envelope.
- **Child phase:** the calibrated spin cycle, represented by two perpendicular
  ARA diameter cuts.
- **Child strength:** lagged detector-share displacement and its one-bin change.
- **External coupling:** magnetic field and RF identity.
- **Prediction target:** detector-summed release at a later bin.

Detector shares and detector totals remain separate. No daughter information
from the predicted bin is allowed into the feature array.

## Population and split

- Development: 13 runs at 300 K, 50–482 G.
- Validation: 13 interleaved runs at 300 K, 68–500 G.
- Two periods per run: RF on and RF off.
- Time window: 0.25–6.00 microseconds at the native 0.016 microsecond spacing.
- The high-field 202 K branch is excluded because T414 established that it has
  only about 2.25 samples per cycle and is not a comparable resolved holdout.

The development split fixes every model, scale and regularisation value before
validation is scored.

## Coordinates and causal timing

The frozen T414 constants are used without refitting:

\[
\tau=2.203\ \mu\mathrm{s},\qquad
\gamma=0.013549\ \mathrm{MHz/G}.
\]

At current time \(t\),

\[
x_P(t)=2\left(1-e^{-t/\tau}\right),
\]

\[
\theta(t)=2\pi\gamma Bt,
\qquad
x_A(t)=1+\sin\theta(t),
\qquad
x_B(t)=1+\cos\theta(t).
\]

For detector shares \(s_d(t)\), the early reference is the mean share vector
over 0.25–0.50 microseconds. The lagged directional strength is

\[
q(t)=\sqrt{96}\,\lVert s(t)-\bar s_{early}\rVert_2,
\]

with one-bin change \(\Delta q(t)=q(t)-q(t-\Delta t)\).

The target at horizon \(h\) is the future log detector-summed rate relative to
the run-period early reference:

\[
y_h(t)=\log\frac{R(t+h\Delta t)}{\bar R_{early}}.
\]

All features are taken at or before \(t\). Horizons are 1, 4 and 8 bins
(0.016, 0.064 and 0.128 microseconds). Four bins is primary.

## Nested models

All non-intercept columns are standardized from development only. Ridge
regularisation is selected separately for each model and horizon by leave-one-
run-out development cross-validation from

\[
\lambda\in\{0,10^{-6},10^{-4},10^{-2},10^{-1},1,10,100\}.
\]

- **M0 parent:** \(1,x_P,x_P^2\).
- **M1 parent + perpendicular spin:** M0 plus
  \(x_A-1,x_B-1,x_P(x_A-1),x_P(x_B-1)\).
- **M2 + lagged child strength:** M1 plus
  \(q,\Delta q,q(x_A-1),q(x_B-1)\).
- **M3 + external coupling:** M2 plus standardized field, RF identity, and
  field/RF interactions with the two spin cuts.
- **M4 Information-lock array:** M3 plus
  \(x_Pq(x_A-1),x_Pq(x_B-1),x_P\Delta q\).

The models are intentionally nested. Improvement can therefore be attributed
to the added ARA branch rather than to an unrestricted black box.

## Scoring

Predictions are scored at the run-period grain with future-log-rate RMSE.
For each validation field the two RF-period squared errors are pooled before
the field-level RMSE is calculated. Improvement over the parent baseline is

\[
I=1-\frac{\mathrm{RMSE}_{M}}{\mathrm{RMSE}_{M0}}.
\]

The report will show median improvement, the number of fields with positive
improvement, and every field-level value. No time-bin pseudo-replication will
be presented as the replicate count.

## Frozen controls

Two validation-only controls are applied to the already-fitted M4 model:

1. **Wrong-frequency control:** spin phase uses the frozen target frequency
   plus \(4/5.75\) MHz.
2. **Broken-history control:** \(q\) and \(\Delta q\) are circularly shifted by
   a deterministic run-period-specific offset of at least 64 bins.

The parent coordinates, target, field, RF identity and fitted coefficients do
not change in either control.

## Primary interpretation gate

The full array supports later ensemble-release information at the primary
four-bin horizon only if all conditions hold:

1. median field-level M4 improvement over M0 is positive;
2. at least 10 of 13 validation fields improve;
3. M4 beats both frozen controls in median field-level RMSE;
4. the median improvement is positive in RF-on and RF-off periods separately.

Failure of this gate does not erase the T414 spin-child recovery. It means the
tested characteristic array did not add stable future release information
beyond the parent envelope in this archive.

## Planned visuals

1. Sequential model improvement at all three horizons (bar).
2. Primary-horizon field-level improvement (scatter).
3. One fixed 284 G validation release profile: observed, parent and M4 (line).
4. Binned child-strength relation to the later parent residual (line).
5. Exact validation and control audit table.

