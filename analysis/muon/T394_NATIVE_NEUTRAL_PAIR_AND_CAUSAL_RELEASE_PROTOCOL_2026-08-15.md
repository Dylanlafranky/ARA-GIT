# T394 - Native neutral-pair and causal individual-release protocol

**Frozen:** 15 August 2026, before inspecting the Super-K event rows  
**Purpose:** execute two related but separately scored ARA tests without mixing child and parent rungs or using daughter information as a pre-decay predictor.

## Test 1 - neutral siblings at their native rung

### Identity and coordinate

For each truth-resolved positive-muon decay

\[
\mu^+\rightarrow e^+ + \nu_e + \bar\nu_\mu,
\]

let the child energy coordinates be `x_e`, `x_nue`, and `x_anumu`, with

\[
x_e+x_{\nu_e}+x_{\bar\nu_\mu}=2.
\]

The joint neutral pair is promoted to its own native `0-2` identity:

\[
y_{\nu_e}=\frac{2x_{\nu_e}}{x_{\nu_e}+x_{\bar\nu_\mu}},
\qquad
y_{\bar\nu_\mu}=2-y_{\nu_e}.
\]

The pair is not assumed to be exactly `(0.5,1.5)`. Its complete event-level
distribution is the object being measured. A measured pair that does not sum
to two must retain the residual as `Other`; truth-level simulation has no
detector Other.

### Source and generation

Use the massless Standard-Model V-A muon-decay distribution already frozen in
T393:

- charged-daughter Michel density `f(x)=2*x^2*(3-2*x)` on `[0,1]`;
- conditional electron-neutrino density proportional to `z*(1-z)` on
  `[1-x_e,1]`;
- `x_anumu=2-x_e-z`.

Generate 1,000,000 accepted events with fixed seed `394`. This is a
truth-model crosswalk, not direct observation of both neutrinos.

### Frozen outputs and controls

1. native-pair median, quantiles and density;
2. fraction near either oriented `(0.5,1.5)` coarse pair within L1 distance
   `0.20`;
3. pair asymmetry `|y_nue-y_anumu|` by charged-daughter quintile;
4. ordering probability for the two neutral children;
5. comparison with an identity-shuffled control and a phase-space-only
   conditional control;
6. parent projection and native-pair coordinates shown separately.

No density mode or landmark will be moved after inspection.

## Test 2 - reconstructed anti-phase and later individual release

### Who

Every row in the Super-Kamiokande stopped-cosmic-muon release, including
tagged decay electrons, rows without a tagged decay electron and rows with
tagged neutrons.

### What

The later handover outcome is the first tagged decay-electron time. Neutron
times and missing-electron rows remain outcome/Other information. They are
never predictor inputs.

The visible parent phase in calibration is the empirical survival curve of
the declared cohort. Its missing anti-phase is reconstructed as the
complementary cumulative release coordinate. This is a population-level
TE-ARA reconstruction unless a pre-outcome variable differs between
individual muons.

### When and leakage boundary

At prediction time, only information that exists before the daughter event is
allowed. Decay-electron time, momentum, neutron presence, neutron count and
neutron time are forbidden predictors. Rows are split by a deterministic hash
of their frozen row number because the release does not document acquisition
order; the split is not called chronological.

### Models

- `M0`: ordinary exponential release model fitted on calibration;
- `MP`: calibration empirical-survival / reconstructed anti-phase model;
- `MI`: individual ARA model, allowed only if the source contains a genuine
  pre-outcome field that varies between muons.

### Gates

1. **Source grain:** one row must represent one stopped muon.
2. **Leakage:** no outcome or post-outcome field may enter `MP` or `MI`.
3. **Population anti-phase:** `MP` must improve held-out distributional score
   over `M0` and remain calibrated.
4. **Individual discrimination:** `MI` must improve held-out individual
   release prediction over `MP`, survive shuffled-identity and time-reversal
   controls, and provide positive lead time.
5. **Claim ceiling:** if the source contains no varying pre-outcome field,
   Gate 4 is structurally untestable and must not be reported as a failure of
   ARA or as individual support.

### Required visual outputs

1. native neutral-pair `0-2` density and charged-coordinate dependence;
2. parent versus native-rung decomposition;
3. calibration anti-phase and untouched holdout release curve;
4. held-out residuals against exponential and empirical-survival models;
5. a plainly labelled panel showing which source fields existed before and
   after the handover;
6. individual prediction panel only if Gate 4 is testable.

## Interpretation boundary

- Test 1 can support an ARA representation of a known truth-level decay law;
  it cannot directly observe the two neutrinos.
- Test 2 can support population anti-phase reconstruction if it predicts the
  held-out release distribution.
- Only an independently measured, varying pre-decay child linked to the same
  muon can support advance individual release information.
- Complementary closure constructed from one measured phase is exact
  bookkeeping; its out-of-sample predictive performance is the empirical
  question.

## Sources

- Super-Kamiokande stopped-muon data release:
  `https://doi.org/10.5281/zenodo.15081911`
- PDG muon decay parameters:
  `https://pdg.lbl.gov/2025/reviews/rpp2025-rev-muon-decay-params.pdf`
- T393 protocol and findings in this directory.
