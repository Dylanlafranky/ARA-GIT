# T308 — Phi Temporal-Ruler Orbital Probe

**Frozen:** 31 July 2026, before downloading or inspecting the orbital vectors  
**Tier:** exploratory probe; not a definitive universal-Time test  
**Primary question:** do Phi-spaced time slices provide an unusually coherent
ARA reconstruction of a later orbital state?

## Declared ARA interpretation

This test keeps structural scale and temporal reach separate.

- A structural octave is not inferred from the passage of time.
- The physical identity remains on the same structural rung.
- A temporal ruler selects progressively more distant slices from the current
  time:

  \[
  \tau_k=\tau_0\lambda^k.
  \]

- The Phi hypothesis tested here is \(\lambda=\phi\), not a claim that the
  orbit grows by Phi or by two.

The orbital circle is reduced to an ARA diameter through

\[
x(t;\,t_0)=1-\cos\!\left(\theta(t)-\theta(t_0)\right),
\]

so a complete directed orbit reads \(0\rightarrow2\rightarrow0\). The branch
sign is the sign of
\(\sin(\theta(t)-\theta(t_0))\).

## Public data

JPL Horizons geometric Cartesian vectors:

1. Moon (`301`) relative to Earth centre (`500@399`);
2. Earth (`399`) relative to Sun centre (`500@10`).

Requested interval: `2000-01-01` through `2026-01-01`, one-day cadence,
ecliptic ICRF/J2000 reference, geometric vectors, kilometres and seconds.

The raw Horizons response and parsed vectors must be retained under
`analysis/phi_calibration/data/t308/`.

## Fixed temporal-ruler candidates

\[
\lambda\in
\left\{
1.25,\sqrt2,1.5,\phi,1.75,2,e
\right\}.
\]

Phi is fixed as `1.618033988749895`.

A continuous ratio sweep may be reported only as an exploratory diagnostic. It
cannot replace the fixed-candidate result.

## Frozen reconstruction rule

For an anchor \(t_0\), final horizon \(H\), and candidate \(\lambda\), use:

\[
t_1=t_0+\frac{H}{\lambda^2},
\qquad
t_2=t_0+\frac{H}{\lambda},
\qquad
t_3=t_0+H.
\]

Only the first two future slices are supplied to the reconstruction. Their
directed, unwrapped orbital advances are \(q_1\) and \(q_2\). The third is
predicted by continuing the straight relation defined by those two landmarks:

\[
\widehat q_3
=
q_2+
\frac{t_3-t_2}{t_2-t_1}(q_2-q_1)
=
q_2+\lambda(q_2-q_1).
\]

This is the same operator for every ruler. It is an information-lock probe:
two measured states and their relation predict the third.

The prediction is converted back to the ARA diameter:

\[
\widehat x_3=1-\cos(\widehat q_3),
\qquad
x_3=1-\cos(q_3).
\]

No Fourier decomposition, orbital model fitting, sieve, or post-result
parameter adjustment is permitted.

## Evaluation windows

The first half of the date range is a stability/calibration half; the second
half is the primary untouched evaluation half. No outcome-derived parameter is
fitted in either half.

For each system, estimate its median orbital period from the calibration
half's unwrapped ecliptic longitude. Evaluate:

\[
H/P\in\{0.25,0.375,0.5,0.75,1.0,1.5,2.0\}.
\]

Use daily anchors for which every required slice and final target exists.
Fractional-day phases are obtained by deterministic linear interpolation of
the unwrapped daily longitude.

## Primary metrics

For every candidate and system:

1. median absolute directed-phase error;
2. median absolute ARA-coordinate error;
3. A/B branch accuracy;
4. median curvature-normalised phase error:

   \[
   E_{\rm curv}
   =
   \frac{|\widehat q_3-q_3|}
   {(t_3-t_1)(t_3-t_2)}.
   \]

The fourth metric compensates for the automatic advantage obtained when the
latest supplied slice lies closer to the target.

Report calibration and evaluation halves separately. Rank candidates on the
evaluation half. Bootstrap evaluation anchors in fixed blocks to quantify
uncertainty in the Phi-versus-best-control difference.

## Frozen interpretation

### Phi supported by this probe

Phi must:

- rank first on evaluation curvature-normalised phase error for both systems;
- not lose materially on raw phase or ARA-coordinate error;
- retain the same direction of advantage across most declared horizons;
- beat its nearest fixed competitor outside the bootstrap uncertainty interval.

### Partial

Phi wins one system or one metric family but not the other, or its lead is
inside uncertainty.

### Not supported

A fixed non-Phi ruler wins both systems, Phi's apparent raw-error advantage is
removed by curvature normalisation, or results are unstable across horizons.

### Boundary

This probe tests one operational meaning of “Phi is a Time ruler.” A null
result does not test every possible Phi handover, temporal-tension, or
cross-scale formulation.

