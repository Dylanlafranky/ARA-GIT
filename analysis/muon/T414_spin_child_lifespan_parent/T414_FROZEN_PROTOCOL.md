# T414 — Spin-child / lifespan-parent test (frozen protocol)

## Status and relational location

This is an ARA-first, population-histogram test using the public ISIS EMU RF-µSR archive already frozen for T413. It does **not** contain event IDs for individual muons or direct neutrino observations.

- **Parent identity:** the observed muon survival/release envelope in detector-summed counts.
- **Child identity:** the observed spin/precession phase encoded in the changing distribution of counts across detectors.
- **Cross-rung cut:** local spin phase (x_s\in[0,2)) is placed inside the parent release coordinate (x_p\in[0,2]).
- **Main scientific question:** does total release retain a repeatable dependence on spin-child phase after the smooth lifespan envelope is removed?

A detector-direction oscillation is a required calibration result, but it is not evidence that total release is phase-locked.

## Who / what / when / where / why / how

### Who

Forty-six public ISIS EMU runs from experiment RB1620447, already listed in `../T413_live_state_handover/source/T413_SOURCE_MANIFEST.csv`:

- 13 development runs at 300 K and 50–482 G;
- 13 validation runs at 300 K and 68–500 G;
- 20 nominal holdout runs at 202 K and 1800–2484 G.

Each run contains 96 RF-on detector histograms and the corresponding 96 RF-off histograms. RF-on and RF-off are analysed separately first and compared only after their identities remain visible.

### What

For every period and time bin:

1. detector shares isolate directional/spin redistribution,
2. detector totals isolate the observed release envelope,
3. spin phase is converted to a local 0–2 ARA child coordinate,
4. the smooth parent envelope is converted to a 0–2 release coordinate,
5. residual total release is tested against spin-child phase.

### When

Use corrected times from 0.25 to 6.00 microseconds at the native 0.016-microsecond sampling. The first-good-bin rule in the source is respected by the 0.25-microsecond lower boundary.

### Where

All frequency and phase fitting occurs within a run and RF period, while the field-to-frequency calibration is learned from development runs only. No detector order is interpreted as a physical angle because the archived `angles` and `grouping` fields contain no usable geometry.

### Why

The previous two-axis lifespan picture used selected elapsed-time landmarks. T414 asks whether actual spin cycles are the smaller child cycles riding inside that parent curve, and whether those child cycles merely redirect observed daughters or also modulate total release.

### How

The child calibration is obtained from detector *shares*; the release gate is obtained from detector *totals*. This separation prevents a brightening detector from being counted as an increase in total release without evidence in the sum.

## Frozen coordinate definitions

Let (C_{i,r,p}(t)) be the count in detector (i), run (r), RF period (p), at corrected time (t). Let (F_{r,p}) be the exposure frames.

### Directional child channel

The detector rate and share are

\[
R_i(t)=\frac{C_i(t)}{F},
\qquad
q_i(t)=\frac{R_i(t)}{\sum_jR_j(t)}.
\]

The share vector (q(t)) changes when the detected angular/spin distribution changes, while its components sum to one.

Development-only spectral calibration fixed

\[
\boxed{g_{\rm dev}=0.013549\ \mathrm{MHz/G}}
\]

by maximizing pooled detector-share spectral power across the 13 development fields and both RF periods. No external gyromagnetic constant was inserted.

For field (B_r), the frozen child frequency is

\[
f_r=g_{\rm dev}B_r,
\]

and the local child ARA phase is

\[
\boxed{x_s(t)=2\,\operatorname{frac}(f_rt)}.
\]

Thus one full observed spin turn maps (0\rightarrow2\rightarrow0). Phase zero is the archive's corrected (t=0); no outcome-derived phase rotation is allowed in the primary coordinate.

### Parent release channel

The observed total rate is

\[
T(t)=\sum_iR_i(t).
\]

The parent calibration curve is

\[
\widehat T(t)=a_r e^{-t/\tau_{\rm dev}}+b_r,
\]

where one common (\tau_{\rm dev}) is learned from development runs only, while (a_r\ge0) and (b_r\ge0) are nuisance scale/background terms fitted independently for each run and RF period. The fitting rule and calibrated (\tau_{\rm dev}) must be frozen before validation and holdout scoring.

The parent release coordinate is

\[
\boxed{x_p(t)=2\left(1-e^{-t/\tau_{\rm dev}}\right)}
\]

and the release residual is

\[
z(t)=\frac{T(t)-\widehat T(t)}{\sqrt{\max(\widehat T(t),\epsilon)}}.
\]

The square-root denominator makes the residual approximately count-noise scaled without forcing it to have a particular ARA shape.

## Frozen analysis

### 1. Spin-child calibration

At the frozen (f_r), fit detector-share residuals with cosine and sine terms after removing detector-specific intercept and linear drift. Record:

- target-frequency pooled improvement over drift-only;
- target spectral power divided by the median of predeclared sideband controls;
- the fraction of runs in which the target beats the sideband median;
- RF-on and RF-off results separately.

The share result establishes whether (x_s) is an observed child cycle in this archive.

### 2. Parent release phase test

Fit the release residual using

\[
z(t)=\beta_c\cos(2\pi f_rt)+\beta_s\sin(2\pi f_rt)+\eta(t).
\]

Record harmonic amplitude, phase, weighted error reduction, and the target statistic's percentile among predeclared wrong-frequency sidebands. Use the same frozen (f_r) as the detector-share calibration; the total channel may not select its own best frequency.

### 3. ARA phase profiles

Bin (x_s\) into 32 equal bins on ([0,2)) and report, separately by split and RF period:

- directional detector-share projection;
- release residual (z);
- uncertainty and effective count weight;
- parent coordinate (x_p).

### 4. Controls

- **Wrong-frequency sidebands:** offsets of (k/L) from the target, where (L=5.75\ \mu s), (k\in\{2,3,4,5,6,8,10,12,15,18,22,26,30\}), on both sides when inside the resolvable band.
- **Broken detector order:** independently permute detector labels in each time bin. It must destroy the coherent detector-share mode but leave total counts unchanged.
- **Broken temporal order:** permute contiguous eight-bin blocks before recomputing the target statistic.
- **RF identity:** analyse RF-on and RF-off independently and compare their outcomes; do not average them before scoring.
- **Alias sensitivity:** runs whose raw (f_r) exceeds the native Nyquist frequency are excluded from the primary holdout gate and reported separately.

### 5. Frozen gates

The detector-share calibration is supported only if, in validation and primary holdout separately:

1. median target/sideband power ratio exceeds 1;
2. more than half of runs beat their sideband median;
3. broken detector/time order is worse than intact order.

Total-release phase locking is supported only if, in validation and primary holdout separately:

1. median target/sideband release statistic exceeds 1;
2. more than half of runs beat their sideband median;
3. pooled phase profiles reproduce in RF-on and RF-off or an RF-specific difference is stable and predeclared as such after validation;
4. temporal block permutations are worse than intact order;
5. the effect is not explained solely by detector-share modulation.

If only the detector-share gate passes, the finding is: **spin-child cycles are visible inside the lifespan parent, but this archive does not show that total release is phase-locked to them.**

## Holdout and alias boundary

At 0.016 microseconds, the native Nyquist frequency is 31.25 MHz. With the frozen development slope, fields above approximately 2306 G exceed that limit.

- Primary holdout: 15 runs at 1800–2304 G.
- Alias sensitivity: 5 runs at 2340–2484 G.

The sensitivity runs may test sampled alias consistency but cannot establish the direction of the original high-frequency cycle.

## Claim boundary

This test can establish population-level spin-phase structure in detector histograms and whether detector-summed release contains a reproducible component at that phase. It cannot identify or time an individual neutrino, and it cannot distinguish every source of incomplete angular acceptance because detector angles are absent from the archive.

