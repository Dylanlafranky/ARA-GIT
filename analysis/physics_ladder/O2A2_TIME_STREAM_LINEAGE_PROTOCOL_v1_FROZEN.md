# O2-A2 frozen protocol — declared-child downstream time-stream lineage

**Frozen:** 23 July 2026, 22:00 AEST, before O2-A2 development or target outcomes  
**Status:** prospective synthetic conditional-tracking test  
**Fidelity packet:** `O2A2_TIME_STREAM_LINEAGE_FIDELITY_v1.md`  
**Parent test:** O2-A1 hidden `Other` under controlled observation noise  
**Orientation:** the tracked object is movement/traversal on a predeclared child; this is the time-side test  
**Units:** each model retains its native stored-quantity-per-time units

## 1. Question

Given the correct moving child in advance, does following that same child downstream retain its hidden source/sink
waveform better than repeatedly returning to the mixed parent and selecting the locally strongest child?

This is conditional trajectory recovery. It does not discover the child, test space-side stored-information
maintenance, recurse upstream or predict a future physical source.

## 2. Systems, roles and declared streams

The deterministic generators and boundaries are unchanged from O2-A1.

| System | Declared downstream time stream | Role |
|---|---|---|
| damped coupled oscillators | oscillator 2 | development only |
| resistive capacitor coupling | coupling relation | untouched target |
| open two-level probability | state 2 | untouched target |

The names above are frozen structural declarations. Native hidden waveforms are used only for development scoring
and final target scoring.

## 3. Observation and fresh target draws

Use white additive observation noise on both stored quantities \(q\) and declared transfers \(g\), independently
per channel, at SNR values

\[
\{24,18,12,6,0,-6\}\ {\rm dB}.
\]

Noise scaling is identical to O2-A1. O2-A2 uses a new deterministic seed namespace and sixteen target replicates per
system and SNR. The registered primary condition is 12 dB over 32 capacitor/quantum runs.

## 4. Causal movement instrument

All target methods are causal. A trailing polynomial of degree three estimates the current derivative of each
stored channel. Candidate full-window fractions are

\[
\{0.005,0.010,0.020,0.040,0.080\}.
\]

Each residual stream is

\[
r_i(t)=\widehat{dq_i/dt}-g_i(t).
\]

The downstream trajectory filter is a causal exponentially weighted mean,

\[
z_i(t)=\lambda z_i(t-1)+(1-\lambda)r_i(t),
\qquad
\lambda=2^{-1/h},
\]

where \(h\) is the half-life in samples. Candidate half-life fractions of the record are

\[
\{0,0.0005,0.001,0.002,0.005,0.010,0.020,0.040\}.
\]

Zero means no trajectory smoothing.

The derivative fraction and trajectory half-life are selected jointly using only the first 60% of the oscillator
record at 12 dB, white noise on \(q+g\), across eight deterministic development replicates. The frozen objective is

\[
\operatorname{median}\left[
\operatorname{NRMSE}+\frac14(1-\operatorname{correlation})
\right]
\]

on the declared oscillator-2 stream. The deterministic minimum, with smaller derivative and half-life fractions
as tie-breakers, is then frozen for all target runs.

## 5. Methods and controls

1. **Fixed time-stream lineage (primary):** apply the selected trajectory filter only to the predeclared child.
2. **Repeated parent re-selection:** apply the identical filter to all children, then at each sample select the
   child with the largest causally smoothed absolute residual.
3. **Fixed child without trajectory memory:** the selected causal derivative residual before exponential smoothing.
4. **Wrong fixed child:** follow the next child cyclically with the same selected filter.
5. **Compressed parent:** mean of all identically filtered child residuals.
6. **Zero `Other`:** predict no hidden movement.
7. **O2-A1 centred local-polynomial child:** required noncausal offline reference, excluded from causal pass gates.

The comparison between methods 1 and 2 isolates fixed identity from repeated re-location because their derivative
and filtering instruments are identical.

## 6. Scoring

Score only samples common to every causal candidate. A true active point satisfies

\[
|s(t)|\geq0.05\max_t|s(t)|.
\]

Record per run:

- active-point sign accuracy;
- Pearson waveform correlation;
- hidden-peak-normalized RMSE;
- signed integrated-amount relative error;
- for re-selection, fraction of samples assigned to the declared child and switch count;
- differences between fixed lineage and every control.

Report medians and 5th/95th percentiles by system and SNR. Identity retention for the fixed path is `1` by
construction and must not be reported as discovered location accuracy.

## 7. Registered 12 dB decision gate

Across the 32 untouched target runs, the downstream time-stream claim is `SUPPORTED [pre-registered; synthetic
conditional tracking]` only if all gates hold:

1. pooled median fixed-lineage correlation is at least `0.40`;
2. pooled median fixed-lineage peak-NRMSE is at most `0.35`;
3. pooled median active-point sign accuracy is at least `0.75`;
4. pooled median integrated error is at most `0.35`;
5. fixed lineage has at least `0.10` higher median correlation than repeated re-selection;
6. fixed lineage has at least `10%` lower median NRMSE than repeated re-selection;
7. fixed lineage has lower median NRMSE than zero `Other`;
8. fixed lineage has lower median NRMSE than repeated re-selection separately in both target systems.

If the comparative gates pass but an absolute adequacy gate fails, rate `INCONCLUSIVE` rather than support. If the
instrument is adequate and any comparative gate fails, rate `NOT SUPPORTED`.

## 8. Two-output requirement and scope

The report must separate:

1. **conditional-tracking verdict:** whether the eight registered gates passed;
2. **geometry verdict:** how the declared stream, re-selection occupancy, switching, waveform, integral and
   child/parent controls change down the SNR ladder.

A positive result would show only that a known branch should be followed continuously in these synthetic typed
systems. It would not establish a universal time wave, recover an unknown child, demonstrate space-side
information retention, provide a new denoising theorem or outperform established system-specific estimators.

## 9. Reproduction outputs

The runner must be self-contained apart from NumPy and the existing synthetic generators. It writes development,
trial, aggregate, bounded waveform and JSON artifacts containing the protocol and fidelity hashes. An independent
validator must recompute the primary gates from saved trials and directly reproduce a representative fresh run.

