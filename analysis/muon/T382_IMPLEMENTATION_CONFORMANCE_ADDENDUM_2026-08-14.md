# T382 implementation-conformance addendum

Date frozen: 2026-08-14  
Status: frozen before inspection of the 96-detector-share outcome

## Reason for this addendum

The first executable draft compressed the EMU detector field into the official
forward/backward banks. That bank asymmetry is a legitimate diagnostic cut, but
it does not implement section 9.1 of the frozen T382 protocol, which explicitly
requires the time-varying shares of all 96 detectors.

The first bank result is therefore retained as a labelled proxy diagnostic. It
is not the primary C03-C06 verdict.

## Corrected primary child instrument

For run `r`, detector `d` and native time bin `t`, define

\[
s_{d,r}(t)=\frac{C_{d,r}(t)}{\sum_j C_{j,r}(t)}
\]

and remove that detector's time-averaged share within the frozen analysis
window:

\[
y_{d,r}(t)=s_{d,r}(t)-\bar s_{d,r}.
\]

Calibration fits the frozen shared cadence and relaxation with detector-owned
coefficients:

\[
\widehat y_{d,r}(t)=e^{-\lambda_s t}
\left[a_d\cos(2\pi\gamma B_rt)+c_d\sin(2\pi\gamma B_rt)\right].
\]

The detector coefficients are learned from calibration runs only and are then
held fixed for validation and holdout runs. No holdout amplitude or phase is
rescaled to manufacture native `0` or `2` extrema.

The child phase origin is fixed from the official forward/backward detector
axis after calibration:

\[
\phi_0=\operatorname{atan2}(-C_{FB},A_{FB}),
\]

where `A_FB` and `C_FB` are the forward-minus-backward projections of the two
calibrated detector-coefficient fields. This fixes orientation without using
holdout timing.

## Controls retained unchanged

- no-phase detector-share baseline;
- reverse phase with the same calibrated detector coefficients;
- circular shifts of the calibrated 96-detector coefficient field;
- validation bookends;
- native, 2-bin and 4-bin sensitivity;
- detector bootstrap;
- random-phase and mirrored-origin C06 controls;
- the independently fitted population parent ridge;
- C16 remains unavailable for aggregate histograms.

## Interpretation boundary

The corrected 96-detector result supersedes the forward/backward proxy for the
primary child gate. The proxy remains visible for provenance. A failed corrected
gate is a source/child failure. A passed corrected gate permits C06 evaluation
but still does not directly observe a neutrino or predict an individual muon.
