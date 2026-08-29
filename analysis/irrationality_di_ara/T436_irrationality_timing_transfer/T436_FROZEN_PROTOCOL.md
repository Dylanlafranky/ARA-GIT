# T436 — Irrationality Di-ARA timing transfer

Status before execution: **FROZEN**

## Question

T435 recovered the two-child axis and their shared closing relation from the
combined SXS waveform, but its frozen three-landmark median estimated the first
common-horizon handover 37.542 M late. Does the already-defined time-facing
Irrationality Di-ARA locate that handover more accurately?

This is a **known-answer method-transfer diagnostic**, not a second blind
discovery: the common-horizon time for SXS:BBH:0305 was already revealed in
T435. The prediction code remains waveform-only and is hashed before the
known answer is scored.

## Who / what / when / where / why / how

- **Who:** the T435 child-axis phase history, its independent openness child
  `U`, closure child `R`, and lag-angle parent `H`.
- **What:** predict a single common-handover time from the joint condition
  `U=R` (child singularity) and `H=1` (parent ridge), then compare it with the
  T435 frozen clock and first common horizon C.
- **When:** the late parent basin before the waveform total-power maximum.
- **Where:** the same SXS:BBH:0305 Lev6 combined strain modes used by T435.
  No horizon or metadata answer-key field enters prediction.
- **Why:** isolate whether the time-facing Irrationality Di-ARA supplies the
  missing handover clock rather than another static identity reconstruction.
- **How:** transfer the T419/T421 equations to the T435 half-phase child axis,
  calculate them from past-only windows, and select the best joint lock in a
  waveform-only ARA basin.

## Frozen ARA identity and equations

The child phase is the T435 octave-halved parent carrier phase:

```text
theta_child(t) = phase(h_22(t)) / 2
z(t) = theta_child(t) / (2*pi) mod 1
```

Every read uses the preceding 128 waveform samples and advances four samples,
matching the T419/T421 time-facing instrument. On this waveform that history is
about one parent-waveform cycle; no horizon value determines it.

The exact transferred coordinates are:

```text
U = 2 * L_local / (L_local + L_null)
R = 2 * median_l |C_l|,       l=1,...,32
H = 2 * median_l |arg(C_l)| / pi
```

where `L_local` is the frozen circular nearest-neighbour phase-prediction loss,
`L_null` is the constant circular-mean loss, and

```text
C_l = mean(exp(i*2*pi*z[j+l]) * conj(exp(i*2*pi*z[j]))).
```

`U`, `R`, and `H` are independently evaluated. No coordinate is defined as the
complement of another and no sum is forced to two.

## Frozen timing rule

T421 defines the hierarchy:

```text
child singularity: |U-R| -> 0
parent ridge:      |H-1| -> 0
```

T436 combines those two already-declared distances without fitting:

```text
D_lock = sqrt((U-R)^2 + (H-1)^2).
```

The eligible parent basin is fixed from waveform-only T435 coordinates:

```text
t <= time of maximum total modal power
and
R12_hat <= 1.
```

This uses the latter half of the T435 closing relation and does **not** restrict
the search to the known one-cycle scoring tolerance. The primary T436 estimate
is the eligible read with minimum `D_lock`; ties choose the earlier read.

For interpretation, all sign-changing `U-R` crossings are retained and linearly
interpolated. They do not replace the frozen minimum-distance clock.

## Frozen controls

1. **Wrong rung:** repeat the construction with the unhalved parent phase.
2. **Circular history shift:** rotate the half-phase history by one quarter of
   the active support while leaving T435 parent-basin coordinates fixed.
3. **Reverse chronology:** reverse the half-phase history while retaining the
   original parent-basin time labels.
4. **Child-only clock:** minimize `|U-R|` without the parent-ridge term.
5. **Parent-only clock:** minimize `|H-1|` without the child-singularity term.

Controls are diagnostics. They cannot change the primary estimate.

## Frozen gates

Let the T435 timing error be 37.542193 M and its local parent-waveform cycle be
11.371039 M.

1. **Improvement:** T436 absolute error is smaller than 37.542193 M.
2. **Cycle accuracy:** T436 absolute error is no larger than 11.371039 M.
3. **Joint-lock specificity:** the primary joint clock is no worse than both
   single-distance clocks, and no worse than at least two of the three phase
   controls.

Verdict:

- **SUPPORTED FOR TIMING TRANSFER:** all three gates pass.
- **IMPROVED BUT NOT LOCKED:** improvement passes but cycle accuracy or
  specificity fails.
- **NOT SUPPORTED:** the primary estimate does not improve on T435.

Because the answer was already known before T436, even a pass is calibration
evidence only. A genuinely untouched SXS simulation is required for prospective
confirmation.

## Visual contract

The result must show numeric axes and units for:

1. `U`, `R`, and `H` through simulation time;
2. the `U x R` chronological Di-ARA path;
3. joint lock distance through the complete eligible parent basin;
4. T435, T436, waveform-power, and hidden common-horizon times together;
5. exact primary and control timing errors.

