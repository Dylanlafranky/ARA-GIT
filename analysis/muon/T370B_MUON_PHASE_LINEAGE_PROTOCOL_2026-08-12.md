# T370B — Muon parent-phase lineage across an in-band field ladder

**Frozen:** 2026-08-12, before calculating outcomes for the additional runs.

## Question

Does a pre-decay two-pole/circular parent relation learned from raw detector
counts persist into untouched later decay counts, and does its cadence move
with the independently controlled field as a genuine parent-spin phase should?

In ARA language this is the cut

\[
\text{parent Phase A}\leftrightarrow\text{parent Phase B}
\longrightarrow
\text{visible charged-child distribution}
+\text{hidden neutral-child complement}.
\]

The raw archive observes the parent relation through the visible charged
daughter branch. It does not observe the two neutrinos. Their combined branch
is therefore an exact conservation-derived complement, not a separately
observed signal.

## Who, what, when, where, why and how

- **Who:** polarized stopped muons in the public ISIS EMU acquisition family
  `LCB1-88 T=135.0`.
- **What:** the circular parent coordinate inferred from all 96 raw detector
  shares, followed across the decay handover.
- **When:** development interval `0.25 <= t < 3.0 microseconds`; untouched
  holdout interval `3.0 <= t < 6.0 microseconds`.
- **Where:** one specimen and temperature, across the complete in-band field
  ladder in dataset `83342268`.
- **Why:** T370 found a clean 230 G phase but three high-field acquisitions
  exceeded the rebinned sampling bandwidth. This extension distinguishes a
  true parent phase from a generic envelope.
- **How:** fit one two-coordinate circular relation on development counts;
  freeze it; predict the holdout; compare with named baselines and an
  independently known field/cadence relation.

## Frozen selection rule

From all 100 NeXus runs in the complete public raw dataset, include every run
whose title is `LCB1-88 T=135.0 F=<field>`, whose total count is positive, and
whose field satisfies `0 < F <= 520 G`. Independent archive validation found
one earlier 40 G acquisition omitted from the initial contiguous-block listing;
it was added before its outcome was calculated. The complete rule yields 14 runs:

`66627, 66651, 66652, 66654, 66655, 66656, 66657, 66658, 66659, 66660, 66661,
66662, 66663, 66669`.

The field ceiling keeps the expected parent cadence below the 7.8125 MHz
Nyquist limit created by four-channel rebinning. No run is selected by its
outcome.

## Frozen ARA instrument

For detector `d`, normalize its count share by its development mean and fit

\[
y_d(t)=c_d+e^{-\lambda t}
\left[a_d\cos(2\pi f t)+b_d\sin(2\pi f t)\right].
\]

The cosine and sine coordinates are the diameter cuts of the same circular
parent relation. Detector coefficients are learned only in development. The
future time coordinate is then propagated into holdout without refitting.

Frequency search: `0.10..7.80 MHz` in `0.01 MHz` steps. Decay search:
`0..1.5 per microsecond` in `0.05` steps.

## Frozen baselines

1. **No parent phase:** each detector remains at its development mean.
2. **Persistence:** each detector remains at its last development value.
3. **Reverse traversal:** the circular time direction is reversed.
4. **Detector rotation:** the predicted detector pattern is circularly shifted
   through all 95 non-zero detector offsets.

## Frozen gates

A run passes the ARA holdout gate only if it:

1. beats no-parent-phase RMSE;
2. beats persistence RMSE;
3. beats reverse-traversal RMSE;
4. has positive observed/predicted holdout correlation; and
5. no circular detector shift performs as well as the registered geometry.

The independent physics lock is evaluated beside, not substituted for, the
ARA instrument:

\[
f_{\rm expected}=0.013553896\,F\quad\text{MHz when F is in gauss}.
\]

A resolved run must pass the ARA gate and recover this cadence within 5%.

The cross-run result is supported only if at least 10 of 14 runs pass both the
ARA gate and the independent cadence lock. Additionally:

- Spearman rank correlation between field and recovered cadence must be at
  least `0.90`;
- the zero-intercept recovered-frequency/field slope must be within 5% of the
  independent rate; and
- the two 200 G runs must agree within `0.10 MHz`.

## Interpretation boundary

A pass would show that the visible decay branch retains and exposes the
pre-decay parent Phase A/Phase B relation, and that ARA recovers the same
physical lineage from raw counts. It would not directly observe the neutrinos,
identify a new field, or prove that the hidden complement is an ontologically
separate ARA pole.
