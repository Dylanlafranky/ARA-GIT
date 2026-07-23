# O2-A1 frozen protocol - hidden `Other` under controlled observation noise

**Frozen:** 23 July 2026, before any O2-A1 target outcomes were computed  
**Status:** prospective synthetic instrument-robustness test  
**Parent operator:** `HIDDEN_OTHER_RESIDUAL_PROTOCOL_2026-07-23.md`  
**Orientation:** positive means a source into the declared identity; negative means a sink from it  
**Units:** each model retains its native stored-quantity and stored-quantity-per-time units

## 1. Exact question

The noiseless parent test recovered an omitted source or sink with

\[
\widehat s_i(t)=\frac{dq_i}{dt}-g_i(t),
\]

where \(q_i\) is stored quantity in identity \(i\), \(g_i\) is declared net internal transfer into that identity,
and \(s_i\) is the unrepresented `Other`.

O2-A1 asks:

> When only observation quality is degraded, how far down a fixed noise ladder does the same boundary residual
> retain the hidden term's location, sign, waveform and integral?

This is a controlled diagnostic-recovery test. It is not a forward prediction test, because the diagnostic observes
the storage record whose derivative appears in the target equation.

## 2. Frozen systems and boundaries

The unchanged deterministic generators in `ara_hidden_other_residual_test.py` are reused.

| System | Stored identities \(q_i\) | Declared internal transfer \(g_i\) | Hidden truth, revealed only for scoring | Role |
|---|---|---|---|---|
| Damped coupled oscillators | oscillator 1, coupling spring, oscillator 2 energies | spring-mediated power transfers | \(-\gamma p_2^2\) on oscillator 2 | development only |
| Resistive capacitor coupling | capacitor 1, zero-storage relation, capacitor 2 energies | power leaving/entering capacitors and relation | \(-R I^2\) on the relation | untouched target |
| Open two-level probability | state 1 and state 2 probabilities | probability current between states | \(-\Gamma |b|^2\) on state 2 | untouched target |

The model equations, native coefficients, time grids and identity boundaries cannot change in O2-A1.

## 3. Observation corruption

Noise is added only after the clean systems have been generated. Native truth is never perturbed.

### 3.1 Additive noise families

The following four zero-mean shapes are generated independently for every identity and normalized to unit RMS
before scaling:

1. white Gaussian noise;
2. coloured AR(1) noise with coefficient \(0.95\);
3. impulsive noise: a Gaussian floor plus impulses on 1% of samples;
4. slow drift: a random linear/quadratic trend plus one slow sinusoid, with its mean removed.

The declared SNR ladder is:

\[
\{\mathrm{clean},24,18,12,6,0,-6\}\ {\rm dB}.
\]

For nonzero channel \(y_i\), its reference scale is

\[
\sigma_i=\operatorname{RMS}(y_i-\bar y_i)
\]

for stored quantities and \(\operatorname{RMS}(y_i)\) for transfers. A structurally zero channel uses the median
nonzero channel scale of the same quantity type and system. Noise RMS is

\[
\sigma_{\rm noise}=\sigma_i\,10^{-\mathrm{SNR}/20}.
\]

Three injection modes are scored separately:

- stored quantities \(q\) only;
- transfers \(g\) only;
- both \(q\) and \(g\), using independent draws.

Sixteen deterministic target seeds are used per condition. Seeds are derived only from the fixed system, family,
injection-mode, SNR and replicate labels.

### 3.2 Structural corruption

Two secondary ladders are run without additive noise:

- one contiguous missing block occupying
  \(\{0.25,0.5,1,2,5,10\}\%\) of the record;
- timestamp jitter with standard deviation
  \(\{0.02,0.05,0.10,0.25,0.50,1.00\}\Delta t\).

Missing observations and irregularly stamped observations are linearly interpolated back to the original uniform
grid before applying the frozen derivative estimators. These are stress curves, not part of the primary pass gate.

## 4. Frozen derivative estimators and controls

All methods receive the same corrupted \(q\) and \(g\). None receives the native hidden coefficient or waveform.

### 4.1 Primary ARA continuity diagnostic

The primary method uses a centred cubic local-polynomial derivative followed by the unchanged residual
\(\widehat s_i=dq_i/dt-g_i\).

Its window is selected once, using only the first 60% of the oscillator record under 12 dB white noise applied to
both \(q\) and \(g\). Candidate full-window fractions of the record are:

\[
\{0.005,0.010,0.020,0.040,0.080\}.
\]

The selected fraction minimizes, across eight fixed development seeds,

\[
\operatorname{median}\left(
\mathrm{NRMSE}_{\rm hidden}
+
\mathrm{inactive\ RMS\ fraction}
\right).
\]

After this deterministic selection, the window is frozen for every target system, noise family, injection mode and
SNR.

### 4.2 Required comparison methods

1. raw fourth-order finite difference, as in the noiseless parent test;
2. centred moving-average smoothing followed by the same fourth-order finite difference;
3. a causal trailing-window local-linear state estimate whose slope estimates \(dq_i/dt\);
4. zero-`Other`, parent-only and wrong-location controls.

The moving-average and causal-window fractions are selected on the same development slice, candidate set and
objective as the primary window, then frozen independently.

This comparison separates the continuity account from the numerical derivative used to estimate it. A win for one
derivative is not evidence that local-polynomial smoothing is uniquely ARA.

## 5. Scoring

For a run, the hidden location is the identity with largest integrated absolute recovered residual.

An active hidden point satisfies

\[
|s_{\rm true}(t)|\geq0.05\max_t|s_{\rm true}(t)|.
\]

The following are recorded:

- exact hidden-location accuracy;
- active-point sign accuracy;
- Pearson waveform correlation;
- RMSE normalized by native hidden peak;
- signed integrated-amount relative error;
- maximum inactive-identity RMS divided by native hidden peak;
- performance relative to zero-`Other`, parent-only and wrong-location controls;
- empirical 90% pointwise interval coverage across the sixteen replicates;
- first failure encountered while descending the SNR ladder.

All aggregate tables report medians and 5th/95th percentiles as well as sample counts.

## 6. Primary target and decision gate

The primary condition is frozen as:

- untouched capacitor and quantum systems only;
- white noise;
- noise applied to both \(q\) and \(g\);
- 12 dB;
- sixteen seeds per system;
- the development-selected centred local-polynomial derivative.

The registered 12 dB robustness claim passes only if all six gates hold over the 32 untouched runs:

1. hidden-location accuracy is at least `0.90`;
2. median active-point sign accuracy is at least `0.95`;
3. median waveform correlation is at least `0.80`;
4. median peak-normalized RMSE is at most `0.50`;
5. median integrated-amount relative error is at most `0.35`;
6. median inactive-identity RMS fraction is at most `0.50`.

The primary method must also have lower median hidden-waveform NRMSE than raw finite difference and the zero-Other
control. Results against moving-average and causal local-linear methods are required comparisons, not kill gates.

If all gates pass, rate the frozen claim `SUPPORTED [pre-registered; synthetic instrument test]`. If the instrument
is adequate at cleaner SNRs but these gates fail at 12 dB, rate it `NOT SUPPORTED` at the registered threshold while
reporting the actual noise floor. If no method can recover even the clean/high-SNR controls, classify the run as an
implementation failure or `INCONCLUSIVE`, not an ARA null.

## 7. Geometry and interpretation output

The report must give two separate conclusions.

1. **Robustness verdict:** whether the registered 12 dB gates passed.
2. **Geometry verdict:** how location, sign, recovered magnitude and inactive spill change down the noise ladder,
   including whether corruption of \(q\) and \(g\) fails differently.

A positive result supports only the robustness of a typed continuity residual in three known synthetic systems.
The residual itself is a standard conservation diagnostic. It does not establish a new force, Phi, universal
fractality, physical attribution in an open field dataset or forward prediction of unseen `Other`.

## 8. Reproduction outputs

The runner will be:

`analysis/physics_ladder/o2a1_hidden_other_controlled_noise.py`

It must write bounded aggregate and representative-waveform artifacts, plus a JSON result containing the frozen
protocol SHA-256. An independent validator must regenerate the clean systems, verify hashes and recompute the
primary verdict from saved aggregate rows.

