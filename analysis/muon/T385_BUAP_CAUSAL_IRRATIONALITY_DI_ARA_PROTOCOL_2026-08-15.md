# T385 — BUAP causal Irrationality Di-ARA pre-release protocol

**Frozen:** 2026-08-15, after format/engineering inspection of rows `0:500` and before calculation of any ARA predictor on rows `500:`.  
**Status at freeze:** development, chronological validation and internal evaluation protocol. The larger BUAP archive remains unopened and is reserved for later external replication.  
**Primary orientation:** movement/release Phase A is `0 -> 2`; retained/closing Phase B is `2 -> 0`.  
**Secondary landmark only:** `x=1.25` is reported descriptively if present. It is not a success gate and will not be moved after scoring.

## 1. Exact question

Does a causal detector-waveform cut, calculated before the visible decay-electron pulse, contain a movement-side Irrationality Di-ARA change that improves prediction of the later handover beyond elapsed time and ordinary raw-waveform features?

This is a **Class D detector-proxy test conditional on a recorded double-pulse event**. It does not directly observe a neutrino, the muon's internal traversal child, captures, censored parents or decays whose daughter was not recorded. A positive result would justify a stronger same-medium test; it would not establish deterministic muon decay or identify a neutrino-spawning coordinate.

## 2. Who, what, when, where, why and how

- **Who:** eligible individual stopped-cosmic-muon double-pulse records in the BUAP 95 L liquid-scintillator experiment.
- **What:** two causal ARA cuts of the inter-pulse waveform: radial activity expansion/contraction and open/recurrent path geometry.
- **When:** rolling time slices after the first pulse and at least `128 ns` before the second pulse's detected minimum.
- **Where:** the detector waveform identity in one liquid-scintillator source. This is a medium and identity change from the RAL Silver population test.
- **Why:** T384 reconstructed the visible build but missed the anti-phase return. T385 asks whether a lower, earlier detector-waveform cut contains advance information before visible release.
- **How:** engineer on rows `0:500`, freeze the instrument, fit on rows `500:2000`, debug only on rows `2000:3500`, and report rows `3500:end` as internal chronological evaluation. Compare elapsed-time, raw-waveform and ARA-augmented models; run time, order and mirror controls.

## 3. Source freeze

- Landing page: `https://ciiec.buap.mx/Muon-Decay`
- Development file: `https://ciiec.buap.mx/Muon-Decay/Datos/MD10000Last.csv`
- Local disposable path: `F:/SystemFormulaFolder/DataTEsted(TOBEDELETEDBEFOREGIT)/muon_buap/MD10000Last.csv`
- SHA-256: `C2DC1E012FBDF0F3C5EC305E2D8E4DD1D87B05DF5CBA39B492189C0F7D5454CD`
- Downloaded size: `53,641,959 bytes`
- Observed rows: `5,001`
- Sampling interval: `8 ns`
- Source pulse finder: two waveform minima separated by more than the declared `150 ns` veto; pulse amplitudes are measured from the source baseline.

The row length and record end are forbidden predictor inputs because acquisition places the second pulse near a repeatable buffer position. All analysis time is measured from the detected first-pulse minimum. The second-pulse location may generate labels and post-score alignment only.

## 4. Engineering-only findings

Rows `0:500` were opened to select detector-safe timing constants, not to estimate the final effect.

- `439/500` rows met the provisional two-pulse quality requirements used for timing inspection.
- Inter-pulse baseline noise standard deviation was about `0.692 mV`.
- The detected second-pulse rise preceded its minimum by a median `8 ns` and 90th percentile `16 ns`.
- The aligned mean waveform remained at baseline at `-128 ns`, `-96 ns` and `-64 ns`; visible mean departure began close to `-16 ns`.

Therefore the frozen guard is `128 ns`, eight times the 90th-percentile visible rise lead.

## 5. Event qualification

Parse the actual waveform samples as columns `1:-1`; the final column is the declared event size. Reproduce the public two-minimum algorithm in chronological order.

An event is eligible only if:

1. both detected pulses are at least `10 mV` below their causal baseline;
2. the first pulse has at least `15` pre-pulse samples;
3. the inter-pulse interval permits two complete feature windows, the first-pulse recovery margin and the outcome guard;
4. all used samples are finite;
5. neither row length nor the distance from the second pulse to the file end enters a predictor.

The first-pulse recovery margin is `256 ns`. Events too short to supply the required causal interval are excluded with counts reported by split.

## 6. Frozen causal ARA instrument

### 6.1 Rolling windows

- feature window `W = 128 ns = 16 samples`;
- immediately preceding comparison window also `16 samples`;
- evaluation stride `64 ns = 8 samples`;
- delay-embedding lag `16 ns = 2 samples`;
- numerical floor `epsilon = 0.05 mV`.

At endpoint `t`, only samples at or before `t` may be used.

### 6.2 Radial activity cut

Let `R_t` be the RMS baseline-subtracted voltage in the current feature window and `R_{t-W}` the RMS in the preceding window. Define

\[
s_t=\frac{R_t+\epsilon}{R_{t-W}+\epsilon},
\qquad
x_R(t)=\frac{2s_t}{1+s_t}.
\]

`x_R>1` is the frozen movement/expansion side; `x_R<1` is the contraction/retention side. The user prediction is movement-side placement before release. `x_R=1.25` is a secondary liquid-rung landmark only.

### 6.3 Open-versus-recurrent path cut

Within the same causal window construct delay points

\[
z_j=(V_j,V_{j-2}).
\]

Let `L_t` be their total path length and `D_t` the direct distance between the first and final delay points. Define

\[
x_H(t)=\frac{2D_t}{L_t+\epsilon}.
\]

Clip only numerical roundoff to `[0,2]`. `x_H -> 0` is recurrent/closing; `x_H -> 2` is open/straight traversal. This is a path-history axis, not an energy amount.

The typed Irrationality Di-ARA is

\[
D_t=(x_R(t),x_H(t)),
\]

with ridges at `x_R=1` and `x_H=1`. No universal quadrant visitation order is assumed.

### 6.4 Raw scale and ordinary detector covariates

Retain beside the normalized coordinates:

- current RMS `R_t` in mV;
- preceding RMS in mV;
- current mean and standard deviation in mV;
- total variation in mV;
- direct path and total path lengths in mV;
- elapsed time since first pulse in ns.

This prevents normalization from manufacturing a result and supplies the non-ARA detector baseline.

## 7. Forecast label and lead-time boundary

The visible daughter minimum occurs at `t_2`. A causal window is:

- **positive/imminent** when `128 ns <= t_2-t < 384 ns`;
- **negative/open** when `t_2-t >= 640 ns`;
- excluded from fitting when it lies in the `384–640 ns` ambiguity band or inside the `128 ns` guard.

Thus the primary model predicts an event in the next `128–384 ns` while remaining outside the visible pulse guard. Separate descriptive profiles are reported at fixed leads `128`, `256`, `512` and `1024 ns` when available.

## 8. Model ladder

Fit unregularized or weakly ridge-stabilized logistic models using calibration rows only. Standardization parameters also come only from calibration.

- `M0`: intercept only.
- `MT`: elapsed time since first pulse.
- `MG`: `MT` plus the raw detector covariates in section 6.4.
- `MA`: `MG` plus `x_R`, `x_H`, their ridge-centred product `(x_R-1)(x_H-1)`, and their one-stride causal changes.

The primary increment is `MG -> MA`. `MT -> MA` is secondary because raw detector features are a necessary control.

## 9. Primary gates

T385 is supported only if all of the following hold in both chronological validation and internal evaluation:

1. imminent windows have median `x_R>1` and a positive imminent-minus-open difference;
2. `MA` improves mean log loss and Brier score over `MG`;
3. `MA` improves AUROC over `MG` by at least `0.02`;
4. the event-cluster bootstrap 95% interval for `logloss(MG)-logloss(MA)` is wholly above zero in internal evaluation;
5. chronological order, correct event linkage and the declared movement orientation beat the frozen controls;
6. the improvement exists outside the `128 ns` guard and is not explained by row length, record end, pulse amplitude or a visible leading edge.

Failure of any gate is recorded as not supported. A suggestive partial pattern may motivate external replication but is not promoted to confirmation.

## 10. Frozen controls

1. **Outcome-time permutation:** permute second-pulse times within chronological split while retaining each pre-pulse waveform.
2. **Event-link shuffle:** pair the causal waveform of one event with another eligible event's release time.
3. **Time reversal:** reverse only each inter-pulse causal segment and recompute the instrument.
4. **ARA mirror:** replace `x_R` by `2-x_R`; the declared movement-side sign must reverse rather than improve opportunistically.
5. **False rung:** compare `x_R/2` and the unprojected coordinate only as named controls; neither may replace the frozen native cut.
6. **Matched pseudo-times:** place pseudo-release labels in quiet eligible intervals with the same elapsed-time distribution.
7. **Acquisition leakage audit:** explicitly test row length, distance-to-record-end and second-pulse buffer position; they are never admitted to `MA`.

## 11. Reporting and visual contract

The output must show exact numbers, axes and units:

1. representative waveform in `mV` versus `µs since first pulse`, with feature, guard and outcome regions;
2. `x_R` and `x_H` on their own `0–2` ARA axes versus `ns to release`, including ridge `1` and secondary `1.25`;
3. Di-ARA quadrant distributions for imminent and open windows;
4. model AUROC, log loss and Brier by split;
5. causal lead/precision or risk profile with the `128 ns` guard visibly marked;
6. time-reversal, shuffle, mirror and acquisition-leakage controls beside the primary result;
7. eligibility/exclusion counts and dataset capability class.

Use a white background, charcoal text, blue for the frozen movement-side result, orange for the opposed/control relation and neutral grey for baselines. Colour must be reinforced with marker or line style.

## 12. Claim boundary

This file freezes a detector-proxy test of pre-release geometry. Even a complete pass would establish only that this liquid-scintillator waveform contains reproducible advance information under the declared ARA cut. Direct neutrino creation, a physical muon traversal child and unconditional per-muon prediction require a Class G/S source with all parents, censoring and independently measured pre-decay state.
