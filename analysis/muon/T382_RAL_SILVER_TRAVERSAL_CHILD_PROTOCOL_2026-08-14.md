# T382 — RAL Silver muon traversal-child handover

**Status:** FROZEN BEFORE RAW COUNT INSPECTION OR MODEL EXECUTION  
**Freeze date:** 14 August 2026  
**Parent protocol:** `T381_ARA_NATIVE_MUON_NEUTRINO_HANDOVER_MASTER_PROTOCOL_2026-08-14.md`  
**Source:** ISIS EMU investigation RB1620201, DOI `10.5286/ISIS.E.RB1620201`  
**Capability class:** P — population histograms; no individual parent record and no directly observed neutrino  

## 1. Exact question

This first T381 execution asks:

> Is the precessing muon-spin relation a reproducible Phase A traversal child, and does its native `2.0` pole align with or predict the independently measured `1.0` ridge of the muon parent population?

The source can test C01-C06 at population grain. It cannot pass C16 because it contains 96 detector histograms rather than an individually monitored parent muon linked to its own daughter. C16 is therefore frozen as **UNAVAILABLE FOR THIS SOURCE**, not failed and not replaced by detector amplitudes.

## 2. W5H freeze

- **Who:** polarized positive-muon populations stopping in the RAL Silver sample, observed through their aggregate charged-daughter detector histograms.
- **What:** the parent survival/release envelope and the candidate spin-phase traversal child, measured as separate sum and directional-contrast components.
- **When:** 20 October 2016; native `0.016 microsecond` bins. Calibration, validation and holdout are separated by acquisition run before count inspection.
- **Where:** ISIS EMU, one declared RAL Silver sample at `300 K`, with transverse applied-field runs.
- **Why:** test the child-mediated ARA architecture on a physical internal muon relation rather than another pulse-balance detector proxy.
- **How:** learn the parent lifetime, spin cadence and detector phase geometry on repeated 20/25 G calibration runs; validate drift on the first and final low-field runs; predict untouched 63/160/400/1000 G histograms; then test native child, parent ridge and their alignment separately.

## 3. Frozen identity and phase declaration

### Parent identity

The parent is the population of muons from stopping in the RAL Silver sample until decay or loss from the measured population.

### Candidate traversal child

The candidate lower-rung traversal child is the coherent spin-precession relation. It is an internal physical relation of the parent population, inferred from the directional charged-daughter distribution after decay.

This archive therefore observes the child's imprint through the daughter. It does not continuously measure the internal spin of one muon before that muon decays. The result ceiling is retrospective population lineage.

### Orientation

- child Phase A: first half-turn, `0 -> 2`;
- child Phase B: return half-turn, `2 -> 0`;
- child pole: anti-alignment at phase `pi`, represented by `x_child=2`;
- parent ridge: cumulative population release `x_parent=1`.

The frozen mirror control replaces `theta` by `-theta` or `x` by `2-x` where appropriate. The primary orientation is not changed after inspection.

### External Other

Applied magnetic field is a controlled external coupling that changes child cadence. Sample, temperature, instrument and analysis resolution are held fixed. The field is not itself labelled the child.

## 4. Source manifest and split

All selected files have 96 detector histograms, 2,048 native bins, corrected-time range `-0.133 to 32.619 microseconds`, and median step `0.016 microsecond`.

### Calibration — repeated low-field runs

| run | field | bytes | SHA-256 |
|---|---:|---:|---|
| EMU00066572 | 20 G | 953952 | A01EE39846193C08DC4B661E04C78ECA60A825337C5AFD1DE9320E666097CB39 |
| EMU00066573 | 25 G | 986232 | 4A50403866A1218A885733E3228DA24DD38C547CAB792B66020EC6363FB92F05 |
| EMU00066574 | 20 G | 949581 | 7242B168C30BF685F045AD8F755F8267BE9CBA07EB745D595605EBD8064F531A |
| EMU00066575 | 25 G | 987983 | C351F6D451A85C84E08E114B2FCFA8B8FC9CF750B78B6AC63AE50F18B3D2595B |
| EMU00066576 | 20 G | 949653 | FA55FFC01159D1CAA93838B8BADF0099D16D2A451414C16097D198245A2E58A0 |
| EMU00066577 | 25 G | 987645 | 12149F36B0441FF6C2A71F5AE8108ADBD8CB19CDEB4E4E9E59A86D6BCA32C751 |

### Validation — low-field temporal bookends

| run | field | bytes | SHA-256 |
|---|---:|---:|---|
| EMU00066571 | 25 G | 1073718 | F08F376BC995A88BDF4F5F3DE97E203DD7ACD286A4AC6EAF25818EBFF7F43908 |
| EMU00066584 | 20 G | 952760 | BE23FD0CFBCF654E53F0D97C044930E5745F636CC4F0BD0E9FC4513573AD3A08 |

### Untouched primary holdout — in-band field ladder

| run | field | bytes | SHA-256 |
|---|---:|---:|---|
| EMU00066578 | 63 G | 1020809 | B2C575E52E38A23C61A3F5A8B1D86ACB5D56291AE028B2CC04E3844268CC482C |
| EMU00066579 | 160 G | 986802 | 7E88216711AD466AA05ED90FC456A89C26AD56C8F44ABB93E275254816E422A5 |
| EMU00066580 | 400 G | 988086 | A48FB41CA2CC4FA34CD23604B03F15F3D67D3CBDCB920187242DBAB3C68A5BB4 |
| EMU00066581 | 1000 G | 987503 | E18CB646DC10B0E7F2A689E286D78F028AF251AE145EC2011D372BFF26697786 |

### Resolution controls excluded from primary gates

| run | field | reason |
|---|---:|---|
| EMU00066582 | 2000 G | expected cadence leaves fewer than 2.5 native samples per cycle |
| EMU00066583 | 4000 G | expected cadence exceeds the native Nyquist limit |

These exclusions are frozen from field metadata and native sampling resolution before count inspection.

## 5. Data-quality gates

For every included run:

1. shape is exactly `96 x 2048`;
2. corrected time is finite and strictly increasing;
3. median native step is `0.016 +/- 0.0001 microsecond`;
4. counts are finite, integer-valued and non-negative;
5. no detector has zero total counts over the analysis window;
6. all source hashes match the manifest;
7. analysis-window retention and per-detector totals are reported;
8. calibration/validation/holdout membership is immutable.

Failure of a core file-integrity or time-axis gate blocks the run. A low-count detector is retained and flagged unless the same frozen detector rule removes it from every split.

## 6. Frozen time boundaries

- native binning is retained for the primary analysis;
- physical analysis window: `0.25 <= t < 8.00 microseconds`;
- background window: `12.0 <= t < 30.0 microseconds`;
- no rebinning in the primary analysis;
- sensitivity views may use 2-bin and 4-bin aggregation but cannot replace the native verdict.

## 7. C01 — parent population cycle

Let the detector-summed counts be

\[
N(t)=\sum_{d=1}^{96}n_d(t).
\]

On calibration runs, fit the count-rate model

\[
\lambda_P(t)=A_r e^{-t/\tau_P}+b_r,
\]

with shared lifetime `tau_P` and run-specific non-negative amplitude/background nuisance terms. Fit by Poisson likelihood at native resolution.

Freeze `tau_P` after calibration. Validation and holdout runs may estimate only their amplitude and background while `tau_P` remains fixed.

The population parent coordinate is

\[
x_P(t)=2\left(1-e^{-t/\tau_P}\right),
\]

and its ridge time is

\[
t_{P,1}=\tau_P\ln2.
\]

This is explicitly a cumulative population coordinate. It is not an individual muon's internal state.

### C01 gate

Parent recovery is supported if:

1. the fixed calibration lifetime predicts validation and every primary holdout run better than a constant-plus-background model;
2. per-run Pearson or deviance residuals show no unmodelled monotone lifetime drift large enough to move `t_P,1` by more than 10%;
3. the parent ridge lies inside the physical analysis window;
4. the calibration bootstrap 95% interval for `tau_P` is finite and reported.

## 8. C02 — direct parent handover baseline

The direct population handover is the observed decay-release curve implied by C01. It is scored without spin-child terms.

This source does not directly observe either neutrino, so `decay release` means the population timing of detected charged daughters produced in the same decay. The neutrino handover remains a same-event physical inference, not a direct detector timestamp.

`MP`, the parent-only model, is the frozen direct baseline for all child comparisons.

## 9. C03-C05 — physical spin traversal child

### 9.1 Calibration-only cadence

For calibration run `r` with field `B_r`, model each detector share after removal of its time-averaged baseline:

\[
y_{d,r}(t)=
e^{-\lambda_s t}
\left[a_d\cos(2\pi\gamma B_rt+\phi_0)
+c_d\sin(2\pi\gamma B_rt+\phi_0)\right].
\]

Estimate one shared cadence coefficient `gamma_hat`, one shared relaxation `lambda_s`, one shared origin `phi_0`, and detector coefficients `a_d,c_d` using calibration runs only. The field values come from source metadata.

The established muon gyromagnetic coefficient is withheld from fitting and revealed only as an external crosswalk after `gamma_hat` is frozen.

### 9.2 Native child coordinate

For any run:

\[
\theta_r(t)=2\pi\hat\gamma B_rt+\hat\phi_0,
\]

\[
x_C(t)=1-\cos\theta_r(t).
\]

This gives the traversal child's native cycle

\[
0\rightarrow2\rightarrow0.
\]

Store separately:

- native child `x_C(t)`;
- projected child `p_C(t)=x_C(t)/2`;
- child raw amplitude/envelope recovered from the detector coefficients;
- parent population `x_P(t)`;
- detector count scale.

### C03-C05 gate

The spin relation qualifies as a recovered traversal child if the calibration-frozen child model:

1. predicts validation and every holdout detector-share field better than a no-phase detector-share model;
2. beats the frozen reverse-phase model on pooled holdout likelihood;
3. beats at least 95% of circular detector-label shifts with matched complexity;
4. recovers a holdout phase cadence that is monotone with the metadata field without refitting `gamma`;
5. retains the declared orientation and raw amplitude rather than rescaling every run to artificial `0` and `2` extrema.

Passing this gate supports a physical spin-phase child crosswalk. It does not yet support child-mediated decay timing.

## 10. C06 — child singularity versus parent ridge

At the calibration-frozen parent ridge time, calculate for each untouched holdout run:

\[
\theta_{P,r}=\theta_r(t_{P,1})\bmod2\pi,
\]

\[
x_{C@P,r}=1-\cos\theta_{P,r}.
\]

The exact child-mediated hypothesis predicts

\[
\theta_{P,r}\approx\pi
\qquad\text{and}\qquad
x_{C@P,r}\approx2.
\]

The projected value is `p_C@P=x_C@P/2`, but the actual comparison is against the independently estimated parent ridge time. The equality `2/2=1` is not itself scored as evidence.

### Primary pole-alignment gate

The exact alignment claim passes only if:

1. every primary holdout phase is within `pi/4` of the native child pole `pi` at the parent ridge;
2. the pooled circular mean direction is closer to `pi` than to `0`, `pi/2` or `3pi/2`;
3. a run-level bootstrap 95% interval for the pole score

\[
S_{pole}=-\cos\theta_{P,r}
\]

is wholly above zero;
4. the result beats matched random-phase and mirrored-origin controls;
5. the relationship is not created by selecting the nearest repeated child pole after seeing `t_P,1`.

Four primary holdout fields provide weak run-level power. A pass is therefore a lead requiring same-medium replication, not final confirmation.

### Gradient result

Whether or not exact alignment passes, report the full oriented quantities:

\[
\Delta\theta_r=operatorname{wrap}(\theta_{P,r}-\pi),
\]

\[
x_{C@P,r},\quad p_{C@P,r},\quad S_{pole,r}.
\]

A stable non-zero offset may define a future frozen identity-specific gradient. It cannot be fitted and called confirmation on T382.

## 11. Release modulation diagnostic

After removing the frozen parent envelope, test whether detector-summed release residuals contain the calibration-predicted child phase:

\[
R_r(t)=\frac{N_r(t)}{\hat\lambda_{P,r}(t)}-1.
\]

Compare parent-only residuals with frozen `cos(theta)` and `sin(theta)` terms. Because incomplete detector acceptance can leave a phase signal in the sum, this is a diagnostic, not the primary C06 gate. Report it beside detector-shift and spatial-pattern controls.

## 12. C16 — individual advance prediction

**Frozen status for T382: UNAVAILABLE.**

The source stores aggregate time-by-detector counts. It does not provide repeated pre-decay spin measurements for one named muon followed by that muon's daughter time. Therefore it cannot determine whether child state predicts which individual muon will decay next.

No histogram bin, detector sector or fitted phase point may be relabelled as an individual parent event.

## 13. Frozen model ladder

- `M0`: constant/background-only total-count model.
- `MP`: frozen parent exponential plus background.
- `MC0`: time-constant detector-share model.
- `MC`: calibration-frozen spin-child detector-share model.
- `MR`: reverse-phase child model.
- `MS_k`: circular detector-shift controls with the same parameter count.

Primary model scores are native-bin Poisson deviance/NLL for total counts and weighted held-out detector-share error or multinomial NLL for spatial shares. Exact implementation and numerical-stability choices must be recorded in the notebook without changing the model definitions.

## 14. Uncertainty and controls

- parametric Poisson bootstrap for parent lifetime;
- detector bootstrap for child-pattern error;
- run bootstrap for pole alignment, with the low run count prominently stated;
- circular detector-label shifts;
- reverse phase;
- random phase offsets frozen by seed `382`;
- parent-only and no-phase baselines;
- validation bookends for temporal instrument drift;
- native versus 2-bin and 4-bin sensitivity;
- independent established-physics cadence comparison only after ARA calibration is frozen.

## 15. Required outputs

1. source manifest and data-quality table;
2. executable notebook with all parameters at the top;
3. machine-readable result and validation JSON;
4. per-run parent and child tables;
5. saveable HTML report;
6. figure showing parent `0-2`, native child `0-2` and projected child `0-1` with unambiguous axes;
7. phase-at-parent-ridge polar or circular plot for all holdout fields;
8. observed versus frozen-predicted detector pattern;
9. model/control comparison;
10. explicit gate table for C01, C02, C03-C05, C06 and C16.

## 16. Interpretation rules

- Child recovery plus failed pole alignment means spin precession is a real traversal child imprint, but this source does not support it as the timing trigger of the population handover.
- Pole alignment without child-pattern recovery is not support; it is a numerical coincidence.
- Passing both is a same-source lead requiring a second untouched RAL Silver family or equivalent same-medium replication.
- T382 cannot directly observe neutrinos or support individual advance prediction.
- No result changes the medium, phase direction, chosen holdout fields, landmark or rung after inspection.
