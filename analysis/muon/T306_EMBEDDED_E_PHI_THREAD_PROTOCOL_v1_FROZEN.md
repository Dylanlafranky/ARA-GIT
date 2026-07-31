# T306 — Embedded \(1/e \leftrightarrow \phi\) ARA Thread

**Frozen:** 30 July 2026, 13:43 AEST  
**Status at freeze:** unrun  
**Target exposure:** T305 prefixes `N=4..64` are open. This protocol uses
untouched continuations `N=65..256`. The arrival equations are inherited
unchanged from T305, so this is a fresh-prefix mathematical/scheduling test,
not independent laboratory Fusion evidence.

> **Post-run framework-fidelity amendment — 30 July 2026.** G2 below
> accidentally inverted the ARA octave direction by describing the child as
> slower than the parent. Dylan's rule is: a child one pure octave down is
> smaller and faster, with approximately half the parent's period at the
> declared pure `x2` rung step. The quantities \(1/\Delta_P\) and
> \(1/\Delta_C\) in this protocol are **relative beat recurrences between
> selected carrier constants**, not physical parent and child cycle periods.
> The original frozen gate is retained below as an audit record, but it is
> invalid as a test of the ARA child-cadence rule and cannot count as evidence
> against that rule.

## User-specified ARA geometry

The proposed parent thread is an embedded ARA sphere whose local poles retain
their locations on the parent `0..2` coordinate:

\[
u=0 \longleftrightarrow x_B=e^{-1}=0.367879\ldots
\quad\text{(Space / Phase B)}
\]

\[
u=2 \longleftrightarrow x_A=\phi=1.618034\ldots
\quad\text{(Time / Phase A)}.
\]

The embedded coordinate is

\[
x(u)=e^{-1}+\frac{u}{2}\left(\phi-e^{-1}\right).
\]

The landmarks are not moved to the parent poles. The equation only measures
the fractal sphere between them.

The proposed child Phase-B thread is

\[
e^{-1}\longleftrightarrow\phi^{-2}.
\]

## Pre-run mathematical consequences

On a unit scheduling circle, full Phi is read modulo one turn:

\[
\alpha_A=\operatorname{frac}(\phi)=\phi^{-1},
\qquad
\alpha_B=e^{-1}.
\]

The parent carrier separation is

\[
\Delta_P=\phi^{-1}-e^{-1}=0.2501545475\ldots,
\]

which is close to one quarter-turn. Its relative closure period is
\(1/\Delta_P\approx3.9975\) placements.

The child-pair carrier separation is

\[
\Delta_C=\phi^{-2}-e^{-1}=0.0140865701\ldots,
\]

with a longer **relative beat recurrence**
\(1/\Delta_C\approx70.99\) placements. This number describes how long the
two selected carrier phases take to realign; it is not the cadence of an ARA
child identity.

These are exact arithmetic consequences of the selected landmarks and count
only as implementation/geometry checks.

## Unchanged scheduling instrument

Reuse T305 without refitting:

- fixed pulse width `0.15/64`;
- circular wrapped rectangular pulses;
- `128` unknown source phases;
- arrival families `beam7`, `beam7_cycle23`, and `beam7_decay`;
- fifth-percentile overlap \(f_X\) as the robust cell reading;
- same analytic integration functions.

No Fourier or fitted model creates the schedules. Fourier regression below is
used only to measure whether an already-generated contrast contains the
predeclared four-prefix cadence.

## Fresh range and fixed comparison pairs

Fresh prefixes: every integer `N=65..256`.

Primary parent pair:

- `phi_time` \(=\phi^{-1}\);
- `one_over_e` \(=e^{-1}\).

Child pair:

- `anti_phi` \(=\phi^{-2}\);
- `one_over_e` \(=e^{-1}\).

Fixed controls:

- `phi_time` versus `sqrt2_minus_1`;
- `one_over_e` versus `sqrt2_minus_1`;
- `phi_time` versus `pi_minus_3`;
- `one_over_e` versus `pi_minus_3`;
- `sqrt2_minus_1` versus `pi_minus_3`.

For each pair and arrival family, define the endpoint contrast

\[
D_f(N)=f_{X,\mathrm{left}}^{(5\%)}(N)
      -f_{X,\mathrm{right}}^{(5\%)}(N).
\]

## Frozen tests

### G0 — implementation and embedded geometry

- recover all stated constants to `<=1e-12`;
- confirm \(x(0)=e^{-1}\), \(x(2)=\phi\);
- confirm the four-step parent seam drift
  \(\left|4\Delta_P-1\right|<0.001\);
- all overlap values remain in `[0,1]`;
- independently recompute selected dense-grid cells to `<=5e-4`.

G0 is an instrument check and earns no evidence.

### G1 — parent four-step thread

For every pair/family contrast, fit:

1. baseline `intercept + linear N`;
2. the same baseline plus
   \(\sin(\pi N/2)\) and \(\cos(\pi N/2)\).

Record the partial \(R^2\), harmonic amplitude and phase. G1 passes only if
the parent pair has the highest mean period-four partial \(R^2\) of all fixed
pairs across the three arrival families.

### G2 — parent/child rung separation

G2 passes only if the parent pair's mean period-four partial \(R^2\) exceeds
the child pair's, and the child pair's dominant fitted period on the
predeclared scan `4..128` is longer than the parent's dominant fitted period.

**Post-run correction:** this sentence and gate inverted the ARA octave
direction. A proper child-cadence test requires child period
\(T_C\approx T_P/2\), not a longer child period. The frozen gate remains
unchanged for provenance, but it is not a valid child-speed test.

### G3 — coupling-driven endpoint handover

At each fresh prefix, mix the already-normalized phase-resolved arrival
readings:

\[
V_c=(1-c)V_{\mathrm{beam7\_decay}}
    +cV_{\mathrm{beam7\_cycle23}},
\qquad c=0,0.05,\ldots,1.
\]

Recalculate the fifth-percentile overlap after mixing, then compare
`phi_time` with `one_over_e` at fixed `N`.

G3 passes only if varying this independently supplied coupling coordinate
changes the winning endpoint for at least `20%` of fresh prefixes. Direction
is not predeclared; only genuine within-prefix handover is.

### G4 — stationary matched-resource null

On the inherited flat source, all non-overlapping irrational schedules at a
matched prefix must agree to `<=5e-4`. Rational collision behaviour remains an
expected arithmetic control.

## Verdict

- **Supported for this idealized thread model:** G0/G4 and all G1-G3 pass.
- **Mixed:** G0/G4 and two of G1-G3 pass.
- **Not supported:** G0/G4 pass but fewer than two of G1-G3 pass.
- **Invalid:** G0 or G4 fails.

## Interpretation boundary

Support would show that these two predeclared ARA landmarks behave like a
four-step parent contrast and that source coupling can move which endpoint
couples better in this idealized scheduling model. It would not prove that
physical Fusion contains a literal \(1/e\)-Phi double helix, nor that the
constants are universal Phase-A/Phase-B poles. Laboratory use requires
time-resolved stuck-muon arrival and stripping-field data.
