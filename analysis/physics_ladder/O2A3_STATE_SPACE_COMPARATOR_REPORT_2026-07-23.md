# O2-A3: quantum tracking versus a causal state-space filter

**Date:** 23 July 2026  
**Ledger:** T257  
**Frozen status:** `GOOD ABSOLUTE TRACKING / MIXED COMPARATIVE RESULT`  
**Primary target:** synthetic open two-level probability, declared state 2  
**Primary condition:** 12 dB white observation noise on stored probability and declared transfer  
**Replicates:** 32 fresh paired target draws

## Technical summary

The answer is more informative than either “just standard” or “ARA wins.”

1. **ARA's quantum time-stream tracking was good by every frozen absolute gate.** Median correlation was `0.762`,
   NRMSE `0.165`, active-point sign accuracy `0.905`, and integrated relative error `0.118`.
2. **ARA tracked the local waveform better than the matched conventional filter.** The causal augmented-state
   Kalman comparator reached correlation `0.687` and NRMSE `0.235`. ARA improved NRMSE by `29.95%` and correlation
   by `+0.074`; it won both local metrics in all `32/32` paired quantum runs.
3. **The Kalman filter retained the cumulative amount better.** Its integrated relative error was `0.038` versus
   ARA's `0.118`, and it won that endpoint in all `32/32` runs.
4. The frozen comparative classification is therefore **MIXED**. ARA clears the waveform-superiority margins, but
   fails the rule requiring its integral to remain within `10%` of the conventional tracker.

In Dylan's current language, the implemented ARA instrument was better at following the moving time-stream shape;
the conventional state-space account was better at retaining cumulative storage closure. That is an operational
measurement split in these simulations, not evidence that quantum is pure information or that a hidden Phase B has
been physically identified.

## Registered 12 dB quantum result

| Method | Correlation | Peak NRMSE | Sign accuracy | Integrated error |
|---|---:|---:|---:|---:|
| ARA fixed lineage | **0.7616** | **0.1646** | **0.9051** | 0.1175 |
| Causal state-space | 0.6873 | 0.2349 | 0.8079 | **0.0380** |
| Repeated re-selection | 0.6534 | 0.2152 | 0.7074 | 0.2249 |
| Compressed parent | 0.7098 | 0.1803 | 0.8795 | 0.4500 |
| Zero `Other` | 0 | 0.2960 | 0 | 1.0000 |

The methods used the same noisy child observations and timestamps. The ARA settings remained frozen from O2-A2.
The state-space process ratios were selected on oscillator development only (`alpha=0`, `beta=0.001`); target
noise scales were estimated from each record's first `10%` observed-only prefix.

## The local waveform advantage repeated across every primary run

For each replicate, subtract the state-space score from the paired ARA score:

- median paired correlation gain: `+0.0658`;
- post-hoc descriptive 90% bootstrap interval: `[+0.0610,+0.0802]`;
- median paired NRMSE reduction: `0.0730`;
- post-hoc descriptive 90% bootstrap interval: `[0.0674,0.0757]`;
- ARA correlation wins: `32/32`;
- ARA NRMSE wins: `32/32`.

These intervals quantify the repeated paired separation; they do not replace the frozen practical classification.
The result demonstrates that the fixed ARA instrument carried useful local waveform information beyond this
specific conventional random-walk latent-input filter.

## Cumulative closure points in the opposite direction

The paired integral difference was equally consistent but reversed:

- ARA median integrated error: `0.1175`;
- state-space median integrated error: `0.0380`;
- ARA integral wins: `0/32`;
- median paired integral-error reduction attributed to ARA: `-0.0767`;
- post-hoc descriptive 90% interval: `[-0.0856,-0.0713]`.

This is why the result cannot be labelled an unqualified ARA advantage. The Kalman transition explicitly enforces
the storage equation across time, so small local errors are reconciled through the state covariance. The ARA
derivative-plus-EWMA instrument follows local shape but can retain a small bias whose integral accumulates.

## The advantage occupies a finite noise region

Across the quantum noise ladder, ARA had lower NRMSE from `24` through `0` dB and higher correlation from `24`
through `6` dB. At `0` dB, the state-space correlation became higher while ARA retained a small NRMSE advantage.
At `-6` dB, the state-space filter was better on both local metrics. The state-space filter retained lower
integrated error at every tested SNR.

This is not a universal dominance result. It is a middle-to-high-observability time-stream advantage followed by a
very-low-SNR crossover.

## Same-information method contract

Both primary methods received:

- declared quantum state 2;
- noisy stored probability \(q_{\rm obs}(t)\);
- noisy declared internal current \(g_{\rm obs}(t)\);
- sample times;
- the first `10%` observed-only warm-up prefix.

ARA used

\[
\widehat s_{\rm ARA}
=
\operatorname{EWMA}
\left(
\widehat{\frac{dq}{dt}}-g
\right).
\]

The conventional filter used

\[
\begin{bmatrix}q_{k+1}\\s_{k+1}\end{bmatrix}
=
\begin{bmatrix}1&\Delta t\\0&1\end{bmatrix}
\begin{bmatrix}q_k\\s_k\end{bmatrix}
+
\begin{bmatrix}\Delta t\\0\end{bmatrix}g_{{\rm obs},k}
+w_k,
\qquad
y_k=q_k+v_k.
\]

It was a forward filter only. It received no clean target quantity, injected SNR, native hidden waveform or native
sink law.

## Secondary capacitor result is not a valid cross-domain comparison

The registered `10%` calibration prefix leaves only `0.229%` of the capacitor relation sink's original peak in the
scored interval because that synthetic transient decays almost entirely near the beginning. Consequently, every
nonzero local estimator has an unstable peak-normalized score and the zero control appears best. This is a useful
design failure, not evidence for either method.

Any capacitor replication must move the dissipative event into the post-calibration interval or use repeated
driving. The frozen run is preserved unchanged.

## Limitations

- This compares one frozen ARA instrument with one simple two-state Kalman model. It does not exhaust conventional
  state-space methods.
- The Kalman latent input is a random walk selected on oscillator development. A quantum-family development set,
  higher-order state model or correctly specified native sink law could change its performance.
- Conversely, the ARA derivative and EWMA are established signal-processing tools. The specifically ARA part is
  preserving the declared child identity.
- The test is synthetic conditional recovery, not child discovery or forward prediction.
- No result here establishes quantum as pure information, a hidden Phase B, or human perceptual uncoupling.

## Recommended next steps

1. Preserve the `GOOD / MIXED` classification without converting the local waveform win into a universal win.
2. Build a new driven target family in which both local movement and cumulative storage remain identifiable after
   calibration.
3. Compare against several preregistered conventional causal trackers: local-level Kalman, local-linear latent
   input, and a system-family-trained state-space model.
4. Keep time-stream shape and space-side cumulative retention as separate endpoints.

## Further questions

- Does fixed identity still win locally when the conventional filter is trained on one quantum-family parameter
  set and tested on untouched parameter values?
- Can one causal ARA account preserve both waveform shape and integral without post-run correction?
- Is the observed split specific to smooth monotone sinks, or does it persist with oscillatory and sign-changing
  hidden transfers?

## Reproduction

- Frozen protocol: `O2A3_STATE_SPACE_COMPARATOR_PROTOCOL_v1_FROZEN.md`
- Fidelity packet: `O2A3_STATE_SPACE_COMPARATOR_FIDELITY_v1.md`
- Runner: `o2a3_state_space_comparator.py`
- Independent validator: `validate_o2a3_state_space_comparator.py`
- Results: `O2A3_STATE_SPACE_COMPARATOR_RESULTS.json`
- Trial data: `O2A3_STATE_SPACE_COMPARATOR_TRIALS.csv`
- Aggregates: `O2A3_STATE_SPACE_COMPARATOR_AGGREGATES.csv`
- Validation: `O2A3_STATE_SPACE_COMPARATOR_VALIDATION.json`
