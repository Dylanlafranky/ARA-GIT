# O2-A3 frozen protocol — ARA fixed lineage versus causal state-space tracking

**Frozen:** 23 July 2026, 22:32 AEST, before O2-A3 target outcomes  
**Status:** prospective synthetic matched-comparator test  
**Fidelity packet:** `O2A3_STATE_SPACE_COMPARATOR_FIDELITY_v1.md`  
**Parent:** O2-A2 declared-child downstream time-stream lineage  
**Primary target:** open two-level probability, declared state 2  
**Secondary boundary target:** resistive capacitor coupling relation

## 1. Question and two outputs

Given the correct child identity in advance, compare:

1. the frozen O2-A2 causal fixed-lineage instrument; and
2. a conventional causal augmented-state Kalman filter.

The report must answer separately:

- Is ARA fixed-lineage quantum tracking adequate in absolute terms?
- Is its performance better than, worse than, or practically similar to the conventional tracker?

## 2. Same-information contract

Both methods receive only:

- the declared target child;
- noisy \(q_{\rm obs}\);
- noisy \(g_{\rm obs}\);
- sample times.

The first `10%` of each record is an observed-only calibration and warm-up prefix. Scoring begins after that prefix
and after every method has a valid estimate. Target truth is used only after predictions are saved.

The Kalman filter must estimate measurement-noise variances from second differences in the calibration prefix. It
may not receive the injected SNR, clean target quantities, native hidden waveform or native hidden law.

## 3. Data and split

Retain the unchanged O2 synthetic generators:

| System | Declared child | Role |
|---|---|---|
| damped coupled oscillators | oscillator 2 | development only |
| open two-level probability | quantum state 2 | primary target |
| resistive capacitor coupling | coupling relation | secondary target |

Use white independent observation noise on \(q\) and \(g\) at

\[
\{24,18,12,6,0,-6\}\ {\rm dB}.
\]

Use a fresh `O2A3` deterministic seed namespace, `12` oscillator development replicates, and `32` fresh replicates
per target system and SNR. The registered primary condition is the `32` quantum runs at `12` dB.

## 4. Frozen ARA instrument

Use the O2-A2 selected settings without retuning:

- trailing cubic derivative window fraction: `0.04`;
- causal EWMA trajectory half-life fraction: `0.02`.

For declared child \(j^\star\):

\[
\widehat s_{\rm ARA}(t)
=
\operatorname{EWMA}_{0.02}
\left[
\widehat{\frac{dq_{j^\star}}{dt}}_{\rm trailing\ cubic,\ 0.04}
-g_{j^\star}(t)
\right].
\]

This is the operational ARA fixed-lineage instrument being evaluated. The derivative and EWMA are standard
signal-processing components; the ARA-specific choice under test is preserving the declared identity.

## 5. Conventional state-space comparator

Use state

\[
x_k=
\begin{bmatrix}
q_k\\s_k
\end{bmatrix},
\]

with transition and observation

\[
x_{k+1}
=
\begin{bmatrix}
1&\Delta t\\
0&1
\end{bmatrix}x_k
+
\begin{bmatrix}
\Delta t\\0
\end{bmatrix}g_{{\rm obs},k}
+w_k,
\qquad
y_k=
\begin{bmatrix}1&0\end{bmatrix}x_k+v_k.
\]

Thus \(s_k\) is a conventional random-walk latent input in the same continuity account
\(\dot q=g+s\). Use a forward Kalman filter only—no backward smoother.

Estimate \(R_q\) and \(R_g\) robustly from calibration-prefix second differences. Set

\[
Q_{qq}
=
\tfrac12\Delta t^2R_g+\alpha R_q,
\qquad
Q_{ss}
=
\beta\,\sigma_g^2.
\]

Select \((\alpha,\beta)\) only on oscillator development at 12 dB using:

\[
\alpha\in\{0,10^{-6},10^{-5},10^{-4},10^{-3},10^{-2},10^{-1}\},
\]

\[
\beta\in\{10^{-10},10^{-9},10^{-8},10^{-7},10^{-6},10^{-5},10^{-4},10^{-3},10^{-2}\}.
\]

The selection objective is the median across development replicates of

\[
\operatorname{NRMSE}+\tfrac14(1-r),
\]

with smaller \(\alpha\), then smaller \(\beta\), as deterministic tie-breakers.

## 6. Metrics and controls

Score paired replicates on the common post-calibration interval:

- Pearson waveform correlation;
- hidden-peak-normalized RMSE;
- active-point sign accuracy;
- signed-integral relative error.

Also retain zero `Other`, compressed parent and O2-A2 repeated re-selection as contextual controls. They do not
enter the primary ARA-versus-Kalman classification.

Report paired differences and paired win rates. Bootstrap intervals are descriptive and must not replace the
frozen practical margins.

## 7. Frozen primary classification

### Absolute ARA quantum quality

Rate `GOOD ABSOLUTE TRACKING` only if all hold at 12 dB:

1. median correlation \(\geq0.70\);
2. median NRMSE \(\leq0.25\);
3. median sign accuracy \(\geq0.85\);
4. median integrated error \(\leq0.15\).

Otherwise rate `NOT GOOD BY FROZEN ABSOLUTE GATES`.

### Comparative classification

Let positive NRMSE improvement mean ARA is better:

\[
I_N=1-\frac{\operatorname{median\ NRMSE}_{\rm ARA}}
{\operatorname{median\ NRMSE}_{\rm KF}},
\qquad
\Delta r=r_{\rm ARA}-r_{\rm KF}.
\]

- `ARA-SPECIFIC ADVANTAGE` requires \(I_N\geq0.10\), \(\Delta r\geq0.05\), and ARA median integrated error no
  more than `10%` above Kalman.
- `STATE-SPACE ADVANTAGE` requires the mirrored NRMSE and correlation margins and Kalman median integrated error no
  more than `10%` above ARA.
- `STANDARD-RANGE TIE` requires absolute relative NRMSE difference below `10%` and absolute correlation difference
  below `0.05`.
- Every other pattern is `MIXED`.

This classification concerns the two implemented instruments, not all ARA methods or all state-space models.

## 8. Required controls and falsifiers

The run is invalid if:

- any target outcome is used to tune either method;
- the state-space filter receives clean target values, injected SNR or the native sink law;
- different target noise draws are used between paired methods;
- scoring intervals differ;
- a backward smoother is substituted after results are seen.

The independent validator must recompute primary metrics and directly reproduce at least one quantum target path
without importing saved result summaries.

## 9. Scope fence

This is a synthetic matched-method comparison. It cannot establish a hidden quantum Phase B, pure information as a
physical substance, human perceptual uncoupling, a new quantum law or superiority on public experimental data.

