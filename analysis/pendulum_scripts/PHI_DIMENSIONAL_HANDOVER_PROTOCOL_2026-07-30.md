# Frozen protocol — Phi as one handover geometry across dimensions

**Frozen:** 30 July 2026, before computing the endpoints below.

**Status:** prospective reanalysis of previously opened public pendulum data. This is not an untouched-data
discovery. The endpoint, dimensional pairing and controls were not previously measured.

## 1. ARA claim under test

Let

\[
u_\phi=\phi^{-2}=2-\phi\approx0.381966.
\]

The hypothesis is that the two familiar Phi appearances are cuts of one handover operation:

1. **diameter cut:** a child turn occurs while its parent is near the mirrored local ARA landmarks
   \(x\in\{u_\phi,\,2-u_\phi\}=\{0.381966,1.618034\}\);
2. **circular cut:** the same child turn lies near
   \(u\in\{u_\phi,\,1-u_\phi\}=\{0.381966,0.618034\}\) of the parent's full cycle;
3. **identity outcome:** events close to both cuts preserve the parent's next excursion more faithfully.

The physical interpretation is deliberately narrower than “Phi is the smallest possible surviving Space
component.” The test asks whether Phi is an efficient identity-preserving handover. Smaller Space shares may
exist.

## 2. Data

Public dynamicslab *MultiArm-Pendulum* data, Zenodo DOI `10.5281/zenodo.6633719`.

- development: free-swing `run1`, `run2`;
- frozen evaluation: free-swing `run3`;
- transfer check: driven triple-pendulum `triple1`.

Only raw arm angles and timestamps enter the endpoints. No Fourier transform, Hilbert phase, SVD/POD,
normal-mode model or pendulum equation is used.

## 3. Nested child→parent pairs

The two predeclared adjacent-rung pairs are:

- arm 3 child → arm 2 parent;
- arm 2 child → arm 1 parent.

Turns are prominence-filtered extrema using the already audited pendulum detector:

- `PROM = 0.02` ARA units;
- minimum turn spacing `0.4 × 1.333 s`.

No threshold is tuned from the Phi result.

## 4. Measurements

For every child extremum bracketed by two consecutive parent extrema:

### 4.1 Diameter coordinate

The actual parent angle between its two local turns is monotonically oriented from `0` to `2`:

\[
x_d=2\,\frac{\theta_P(t_C)-\theta_P(t_{P,0})}
{\theta_P(t_{P,1})-\theta_P(t_{P,0})}.
\]

This is clipped to `[0,2]` only for numerical overshoot. It is an ARA coordinate for that local parent
half-cycle, not the pendulum's global over-the-top singularity coordinate.

Phi distance:

\[
d_d=\min(|x_d-u_\phi|,\ |x_d-(2-u_\phi)|).
\]

### 4.2 Circular coordinate

Successive parent extrema advance the parent's unwrapped cycle phase by `0.5`. Linear interpolation in time
between the bracketing extrema gives the child event's parent-cycle phase \(u_c\pmod 1\).

Phi distance on the circle:

\[
d_c=\min\bigl(\operatorname{cdist}(u_c,u_\phi),
\operatorname{cdist}(u_c,1-u_\phi)\bigr).
\]

### 4.3 Joint Phi proximity

Normalize both distances by their maximum possible distance to the corresponding mirrored landmark set and
define

\[
P_\phi=1-\frac12(\widetilde d_d+\widetilde d_c).
\]

Higher \(P_\phi\) means the line and circular cuts are jointly nearer the proposed Phi handover.

### 4.4 Parent identity retention

Let \(A_0\) be the absolute angular excursion of the parent half-cycle containing the child event and \(A_1\)
the next parent half-cycle excursion. Define:

\[
R_I=\frac{\min(A_0,A_1)}{\max(A_0,A_1)}.
\]

`1` means the next parent excursion preserves the preceding excursion magnitude; `0` means strong loss or
expansion. This is an identity-retention endpoint, not energy conservation.

## 5. Frozen comparisons

### Landmark specificity

Diameter Phi is compared with:

- ridge: `{1}`;
- quarter pair: `{0.5, 1.5}`;
- third pair: `{2/3, 4/3}`.

Circular Phi is compared with:

- quarter pair: `{0.25, 0.75}`;
- third pair: `{1/3, 2/3}`;
- ridge/opposition pair: `{0, 0.5}`.

All comparisons use median nearest-landmark distance. Phi must beat every named alternative on frozen run 3
to pass landmark specificity.

### Dimensional locking

Within each pair and run, Spearman correlation is calculated between diameter-Phi proximity and circular-Phi
proximity. The pooled statistic is the event-count-weighted Fisher-z mean. Positive association on run 3 is
required for the two cuts to count as one observed operation.

### Identity retention

Within each pair and run, compare median \(R_I\) in the top and bottom quartiles of joint Phi proximity.
The frozen run-3 difference must be positive.

### Event-time control

Within each run and pair, child event times are circularly shifted by a random offset at least one parent
cycle, `2,000` times, seed `20260730`. Parent trajectories and event counts remain fixed. This tests whether
the observed joint proximity and retention advantage exceed an event-time alignment control.

Primary permutation p-values are one-sided:

- joint proximity: observed median \(P_\phi\) greater than shifted;
- retention: observed top-minus-bottom \(R_I\) greater than shifted.

## 6. Verdict

Frozen run 3:

- **SUPPORTED:** Phi beats all named landmarks on both cuts, dimensional locking is positive, retention
  difference is positive, and both permutation p-values are `< 0.05`;
- **MIXED:** at least two of those four families pass, but not all;
- **NOT SUPPORTED:** fewer than two pass.

Driven data are a transfer report only and cannot change the free-swing verdict.

## 7. Boundaries

- A positive result would support a Phi handover coordinate in this pendulum representation, not prove a
  universal physical constant or minimum viable Space fraction.
- Local normalization makes every half-cycle a complete ARA cut. It does not claim that the low-energy
  pendulum reached its global `0/2` over-the-top singularity.
- Linear time interpolation between raw extrema is an observation rule, not a dynamical phase model.
- Runs have been inspected in earlier pendulum work; only this endpoint is prospective.
