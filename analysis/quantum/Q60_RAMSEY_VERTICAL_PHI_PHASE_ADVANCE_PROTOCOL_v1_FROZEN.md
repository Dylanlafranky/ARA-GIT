# Q60 — Ramsey vertical-Phi relative-phase advance

**Status:** FROZEN BEFORE Q60 NUMERICAL SCORING  
**Freeze date:** 3 August 2026 (Australia/Brisbane)  
**Source:** Arnold and Werner, *All-optical superconducting qubit readout*, immutable Zenodo DOI `10.5281/zenodo.14033026`  
**Source archive SHA-256:** `73F3E2CA7B3658452B4C171532C751E96D7392DCB8741B87A18E28C7073D67FD`

## Question

Do consecutive complete Ramsey interference sweeps carry an ordered relative-phase advance compatible with the ARA Phi circle-train step

\[
c_\phi=\frac{2}{\phi}=1.2360679774997897
\quad\text{on the native ARA phase circle }[0,2)?
\]

This distinguishes three claims:

1. **Ordered phase transport:** repeated corresponding Ramsey states possess a reproducible phase advance rather than unordered phase scatter.
2. **Phi compatibility:** the advance is statistically compatible with `2/phi`.
3. **Phi identification:** the data resolve Phi from close alternatives, especially `26/21 = 1.238095238...`.

These verdicts are separate. Ordered phase transport does not by itself identify Phi.

## ARA object and established-physics object

| ARA-first description | Measurement description |
|---|---|
| One complete Ramsey sweep is one whole repeated identity/time slice. | One saved row contains one interference trace across the same 126 delay settings. |
| Its phase location is an ARA coordinate `x_j` on `0..2`. | The trace phase is reconstructed from its fitted sine and cosine coefficients. |
| The vertical handover is `d_j=(x_{j+1}-x_j) mod 2`. | `d_j` is the ordered phase drift between consecutive saved sweeps. |
| The Phi hypothesis is `x_{j+1}=(x_j+2/phi) mod 2`. | A fixed phase-step model predicts the next trace phase. |

The detector `I` and `Q` channels are **not** relabelled as Bloch `X` and `Y`. They are used only to identify the common readout direction of the Ramsey oscillation. The phase itself is recovered from the delay-dependent interference waveform.

## Eligible raw files and frozen split

Only the six raw `T2_errorbars` files with schema `I,Q: (1,2000,126)` and `t_ns: (1,126)` are eligible. Chronological filename order fixes the split:

- **calibration:** 9 May and 12 May 2023;
- **evaluation:** 16 May and 19 May 2023;
- **holdout:** 24 May and 31 May 2023.

The source values have been used by earlier ARA work, so Q60 is a frozen retrospective reanalysis, not a blind discovery test. The exact Q60 phase-advance outcome was not calculated before this protocol was written.

## Phase reconstruction

For each file independently:

1. Average the 2,000 two-channel traces over sweep order.
2. Centre that mean `I/Q` trajectory and take its first principal-component direction. Axis sign is irrelevant because it adds the same `pi` offset to every reconstructed phase.
3. Project every raw sweep onto this one fixed detector direction.
4. Fit the file-mean projected trace to

\[
y(t)=B+A e^{-t/T_2}\cos(\omega t-\theta)
\]

with positive `T2` and `omega`. Initial frequency is the largest non-zero FFT peak. No Phi constant enters this fit.
5. With `T2` and `omega` fixed for the file, fit every sweep by ordinary least squares:

\[
y_j(t)=b_j+a_j e^{-t/T_2}\cos(\omega t)
             +q_j e^{-t/T_2}\sin(\omega t).
\]

6. Recover

\[
\theta_j=\operatorname{atan2}(q_j,a_j),
\qquad
x_j=(\theta_j/\pi)\bmod2.
\]

No Hilbert transform, temporal smoothing, phase unwrapping or rescaling to Phi is allowed.

## Primary and multistep endpoints

The primary ordered step is

\[
d_{j,1}=(x_{j+1}-x_j)\bmod2.
\]

Frozen multi-step horizons are the Fibonacci lags

\[
k\in\{1,2,3,5,8,13,21\},
\]

with

\[
d_{j,k}=(x_{j+k}-x_j)\bmod2,
\qquad
\widehat d_{k}(c)=(kc)\bmod2.
\]

Circular ARA loss is

\[
L(d,c)=\left|((d-c+1)\bmod2)-1\right|.
\]

Every file contributes equally: calculate its median loss first, then average the two file medians inside each split.

## Frozen candidate models

- Phi circle train: `2/phi = 1.2360679774997897`;
- close rational: `26/21 = 1.2380952380952381`;
- nearby rational: `5/4 = 1.25`;
- anti-Phi orientation: `2 - 2/phi = 0.7639320225002103`;
- `2/e = 0.7357588823428847`;
- `1/e = 0.3678794411714423`;
- square-root irrational: `sqrt(2) = 1.4142135623730951`;
- persistence: `0`;
- **calibration-fitted constant:** circular mean of all calibration `d_{j,1}`, frozen before evaluation and holdout are scored;
- **previous-step velocity:** predict `d_{j,1}` from `d_{j-1,1}` (non-constant ordered baseline).

## Controls

1. **Order shuffle:** independently permute sweep order within each file 1,999 times, recompute phases in that order, and score the frozen calibration-fitted constant.
2. **Broken lineage:** pair each `x_j` with a phase from the other file in the same split after a deterministic circular shift of 317 sweeps.
3. **Time reversal:** reverse each phase sequence. A directed forward step `c` must transform to `(2-c) mod 2`; it must not remain spuriously unchanged.
4. **Amplitude stratification:** repeat primary scoring by quartile of `sqrt(a_j^2+q_j^2)` to expose low-signal phase instability. This is diagnostic and cannot rescue a failed primary result.

## Frozen gates and verdict language

### G0 — usable phase reconstruction

All six file-mean fits must have `R^2 >= 0.70`; every file must yield at least 1,900 finite sweep phases. Otherwise verdict: **DATA INADEQUATE**.

### G1 — ordered phase transport

The calibration-fitted constant must:

- beat the order-shuffle median by at least 20% in evaluation and holdout;
- beat broken lineage in evaluation and holdout; and
- beat zero-step persistence in evaluation and holdout.

If all pass: **ORDERED PHASE TRANSPORT SUPPORTED**.

### G2 — Phi compatibility

On both evaluation and holdout:

- Phi's primary loss must be no more than 5% above the calibration-fitted constant's loss; and
- a contiguous-block bootstrap 95% interval for the split's circular-mean step must contain `2/phi`.

If both pass: **PHI-COMPATIBLE**. This is not unique identification.

### G3 — Phi identification

On both evaluation and holdout, the paired block-bootstrap 95% interval for

\[
L_\phi-L_{26/21}
\]

must lie strictly below zero, and Phi must have lower aggregate Fibonacci-horizon loss than every frozen fixed candidate. Otherwise: **PHI NOT IDENTIFIED AT THIS RESOLUTION**.

Block bootstrap uses 5,000 deterministic draws, seed `60032026`, and contiguous blocks of 50 one-step transitions sampled within file.

## Interpretation fence

- Passing G1 would show ordered drift between repeated experimental Ramsey sweeps.
- Passing G2 would show compatibility with the predeclared Phi step in these native units.
- Passing G3 is required to name Phi rather than a nearby rational or generically fitted asymmetric circle.
- This test does not test whether a literal double-slit particle follows a hidden trajectory.
- This test does not by itself establish that measurement causes an irrational-to-rational physical transition. It targets the proposed pre-measurement-style phase handover coordinate.
- The sweep index is assumed to preserve acquisition order because the archive contains no per-sweep timestamps. That assumption must remain visible in the report.

