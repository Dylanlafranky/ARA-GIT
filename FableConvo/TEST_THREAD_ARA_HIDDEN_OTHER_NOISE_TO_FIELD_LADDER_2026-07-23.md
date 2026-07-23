# Test thread — hidden `Other` from controlled noise to medical and natural systems

**Date captured:** 23 July 2026
**Status:** `O2-A1, O2-A2 AND O2-A3 COMPLETE / O2-B THROUGH O2-E PARKED`
**Parent result:** `analysis/physics_ladder/ARA_HIDDEN_OTHER_RESIDUAL_REPORT_2026-07-23.md`

## Why this thread exists

The controlled hidden-`Other` test recovered

\[
\widehat s_i(t)=\frac{dq_i}{dt}-g_i(t)
\]

in three noiseless simulated systems when stored quantities \(q_i\) and declared internal transfers \(g_i\) were
supplied. It localized the omitted sink and reconstructed its waveform, but it used the observed storage change and
did not predict the sink law before that change occurred.

Dylan proposed progressing through steadily noisier systems, then public medical, weather and natural data with
known diagnostics. The purpose is to determine which parts survive measurement noise and which parts survive a
genuinely open system.

## Claims that must remain separate

1. **Diagnostic recovery:** after seeing \(q(t)\), does the residual still locate where an account fails to close?
2. **Noise robustness:** does the recovered location/sign remain stable as observation noise increases?
3. **Forward prediction:** can a law learned before the holdout predict unseen `Other` without using the holdout
   storage change?
4. **Diagnostic association:** does a large or reorganized residual align with independently annotated events?
5. **Physical attribution:** does the residual identify the actual omitted mechanism rather than merely mark that
   the chosen account is incomplete?

Success at an earlier item does not automatically establish the later items.

## Recommended ladder

### O2-A — original three systems with controlled noise

Keep the original oscillator, capacitor and quantum equations and exact hidden truth. Add noise separately to
stored quantities and internal transfers:

- Gaussian measurement noise;
- coloured / \(1/f\) noise;
- impulsive artifacts;
- slow calibration drift;
- missing blocks;
- irregular sampling and timestamp jitter.

Use a declared SNR ladder including `24, 18, 12, 6, 0, -6 dB` so the results connect directly to the public ECG
noise benchmark below. Derivative/smoothing settings must be selected on development data only.

Primary outputs:

- hidden-location accuracy;
- sink/source sign accuracy;
- waveform correlation and NRMSE;
- integrated residual error;
- inactive-identity false residual;
- earliest SNR at which each criterion fails;
- uncertainty calibration.

Controls:

- raw finite differences;
- standard smoothing plus continuity residual;
- a state-estimation/system-identification baseline;
- wrong-location and parent-only residuals;
- persistence and zero-`Other` forward forecasts.

This is the mandatory bridge: the truth remains known while only observation quality changes.

### O2-B — public controlled medical noise

Use the open MIT-BIH Noise Stress Test Database:

https://physionet.org/content/nstdb/1.0.0/

It contains clean ECG records `118` and `119`, the same recordings with calibrated electrode-motion noise at
`24, 18, 12, 6, 0, -6 dB`, and correct beat annotations copied from the clean originals.

Purpose:

- define one beat-local ARA diagnostic on the clean signals;
- freeze its calculation and event-localization rule;
- apply it unchanged at every noise level;
- test whether the same beat identity/location is retained.

This is a **diagnostic robustness test**, not yet a physiological conservation-law test. ECG voltage alone does not
supply a complete cardiac energy or material account. The native stored quantity, transfers and measurement
boundary must be declared before using the word `Other` physically.

### O2-C — patient-separated medical diagnostic holdout

Use the full MIT-BIH Arrhythmia Database:

https://physionet.org/content/mitdb/1.0.0/

It contains approximately 109,000 expert-reviewed beat labels plus rhythm annotations. Develop only on named
records/subjects; freeze the ARA diagnostic and controls; score on completely held-out subjects.

Questions:

- does an ARA residual trained on normal/clean dynamics predict its next value before the beat?
- do residual location, direction or scale changes align with independently annotated beat/rhythm classes?
- does it add out-of-subject information beyond RR, morphology, spectral and standard classifier controls?

Clinical fence: this would be exploratory signal analysis, not diagnosis, treatment advice or proof that an
arrhythmia is literally an ARA sink.

### O2-D — observed land-atmosphere energy closure

Use half-hourly/hourly AmeriFlux or FLUXNET tower data. AmeriFlux reports standardized QA/QC variables and sign
conventions for net radiation, ground heat, sensible/latent heat and storage fluxes:

https://ameriflux.lbl.gov/data/aboutdata/data-variables/

A typed field residual can be declared as

\[
O_E(t)
=
R_{\rm net}(t)-G(t)-H(t)-LE(t)-\frac{dS(t)}{dt},
\]

with signs and optional storage terms fixed from the selected site's metadata before scoring.

Protocol concept:

- develop on earlier years/sites;
- predict `Other` on later years or untouched sites using only information available beforehand;
- compare with persistence, hour/season climatology, linear energy-balance regression and a flexible standard
  forecasting baseline;
- stratify by radiation, wind, precipitation, canopy state and quality flags;
- report closure and predictive performance separately.

This is the closest first natural-system continuation because it is already an observed boundary-energy account.
The residual is real, but its mechanism can mix advection, storage, footprint mismatch, sensor error and turbulence.
Forward prediction does not by itself identify which mechanism caused it.

### O2-E — TAO/ENSO ocean-atmosphere holdout

The NOAA TAO buoy array provides surface meteorology, radiation, rainfall, surface/subsurface temperature, salinity
and selected current profiles:

https://tao.ndbc.noaa.gov/

Construct a mixed-layer heat/storage account only at stations and periods with the required measurements. Freeze
the layer depth, sign conventions, gap rules and transfer variables before opening later years.

This is the harder natural rung:

- measured storage: mixed-layer heat-content change;
- declared transfers: radiative and turbulent surface fluxes plus measured current terms where available;
- `Other`: unresolved advection, entrainment, mixing and measurement mismatch;
- forward target: later residual waveform or sign, not reconstructed SST after using future SST.

Compare with persistence, seasonal climatology, autoregression and established heat-budget/state-space baselines.
Do not call the residual `Time`, `Dark`, Phi or a new force unless a separately frozen discriminating prediction
requires that interpretation.

## Order of activation

1. Activate and freeze O2-A.
2. If O2-A identifies a usable noise floor, freeze O2-B before inspecting ARA outcomes across its SNR ladder.
3. Use O2-C only after a medical observable and subject split are fixed.
4. Prefer O2-D as the first real open-system continuity test.
5. Use O2-E only after the derivative, missingness and forward-holdout machinery passes A–D.

Jumping directly to weather would combine noise, missing data, unknown storage, unmeasured transfers and scale
selection in one failure. The ladder keeps those causes separable.

## Activation requirements

When Dylan activates a stage:

1. create a separate versioned protocol;
2. declare native \(q\), \(g\), boundary, orientation and units;
3. declare development and untouched target partitions;
4. declare smoothing/derivative method and every baseline;
5. declare primary endpoint, uncertainty method and kill threshold;
6. record prior exposure to the dataset;
7. hash the protocol before computing target outcomes.

## Current recommendation

O2-A1 and O2-A2 are complete. The next open-data rung remains O2-B: test identity retention on genuine
physiological waveforms with a calibrated public noise ladder and unchanged annotations, without claiming that ECG
voltage identifies a physical hidden `Other`. The complementary space-side storage-maintenance test should receive
its own frozen protocol if activated; it is not a repair of O2-A2. AmeriFlux should follow as the first true field
continuity account. Weather/ENSO is valuable, but it is not the cleanest next step.

## O2-A1 completion - 23 July 2026

The controlled-noise diagnostic was frozen as ledger test T255 and run across `16,140` trials. The registered
12 dB target was **NOT SUPPORTED** (`4/8` gates): location `0.50`, median sign `0.762`, correlation `0.460`,
NRMSE `0.314`, integrated error `0.00787`, inactive spill `0.367`. The primary estimator beat raw differentiation
but did not beat zero-Other NRMSE or ordinary moving-average smoothing pointwise. Independent validation passed
`11/11`.

The retained information was the signed integral, not reliable local attribution. Separate input corruption showed
that noisy \(g\) was the main bottleneck; smoothing \(q\) alone was insufficient. Before a physical continuity
claim is attempted on O2-D or O2-E, add a separately frozen joint \(q,g\) observation-error model. O2-B may still
proceed as a clean/noisy ECG identity-retention test, with no claim that voltage alone defines a physical
hidden-`Other` account. Full report:
`../analysis/physics_ladder/O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_REPORT_2026-07-23.md`.

## O2-A2 completion - 23 July 2026

Dylan separated two operations before this follow-up was frozen:

- follow movement downstream: time-side stream lineage;
- preserve stored information: complementary space-side identity maintenance.

T256 tested only the first. The moving child was named before the run, followed with a causal derivative and
trajectory filter, and compared with the same instrument repeatedly re-selecting the locally strongest child.
Oscillator development selected the instrument; capacitor relation and quantum state 2 remained fresh targets.

The exact result was **NOT SUPPORTED** (`6/8` frozen gates). At 12 dB, fixed lineage achieved correlation `0.764`,
NRMSE `0.168`, sign `0.933`, integrated error `0.354`, `+0.060` correlation advantage and `10.84%` relative NRMSE
improvement. It beat re-selection NRMSE in both targets, but missed the integral and correlation-advantage gates.
Quantum was the clean positive case. Capacitor local shape was good, but the signed integral failed badly and the
compressed-parent control had lower NRMSE.

The retained result is therefore narrow: once the branch identity is supplied, following it can resist noisy
identity switching. This is not branch discovery, upstream recursion, physical attribution or forward prediction.
The storage/space-side test remains a separate parked thread rather than a post-hoc reinterpretation of T256.
Independent validation passed `12/12`. Full report:
`../analysis/physics_ladder/O2A2_TIME_STREAM_LINEAGE_REPORT_2026-07-23.md`.

## O2-A3 completion - 23 July 2026

T257 asked whether the quantum tracking that looked good in O2-A2 was genuinely strong against a conventional
tracker. ARA fixed lineage and a forward augmented-state Kalman filter received the same named state, noisy stored
probability, noisy transfer and timestamps. ARA settings remained frozen; Kalman process ratios were selected on
oscillator development only.

ARA passed every frozen absolute quality gate. At 12 dB it reached correlation `0.762`, NRMSE `0.165`, sign
accuracy `0.905`, and integrated error `0.118`. State-space reached `0.687`, `0.235`, `0.808`, and `0.038`.

The paired split was exact across the `32` fresh quantum draws:

- ARA won correlation `32/32`;
- ARA won NRMSE `32/32`;
- state-space won cumulative integral `32/32`.

Frozen result: **GOOD ABSOLUTE TRACKING / MIXED COMPARATIVE RESULT**. Following the named moving stream preserved
local waveform information better; the explicit storage-state model preserved cumulative closure better. Neither
endpoint should be substituted for the other.

The capacitor secondary comparison is unusable because its sink had decayed before the post-calibration scoring
interval; only `0.229%` of its original peak remained. Independent validation passed `12/12`. Full report:
`../analysis/physics_ladder/O2A3_STATE_SPACE_COMPARATOR_REPORT_2026-07-23.md`.
