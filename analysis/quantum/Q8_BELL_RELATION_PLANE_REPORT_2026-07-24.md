# Q8 Bell relation-plane and TE-ARA deconstruction

**Test ID:** `Q8-BELL-RELATION-PLANE-v1`  
**Ledger ID:** `T267`  
**Date:** 24 July 2026  
**Verdict:** `CALIBRATED — 11/11 frozen gates passed`  
**Class:** post-outcome ARA deconstruction / exact quantum crosswalk

## Answer first

The proposed deconstruction works cleanly on the public Q7 Bell-decoherence trajectories.

A complete Bell-family relation can be compressed to:

\[
\boxed{(K,R,\theta,\text{Bell-family orientation})}
\]

where:

- \(K=|ZZ|\) is the persistent parity/Connection-like parent cut;
- \(R\) is the strength of the phase-sensitive relation;
- \(\theta\) is that relation's location and direction in its two-cut plane;
- the Phi/Psi orientation supplies the correct sign layout when the compact coordinates are decompressed.

This compact account explained a median `98.4080%` of the Ramsey correlation-tensor energy and `98.0694%` of
the Hahn tensor energy. The median absolute mismatch between its expected singular strengths \((K,R,R)\) and
the full tensor's three singular values was only `0.0221845`.

Plainly: the nine measured parent correlations are not nine unrelated pieces. For these Bell identities, almost
all of their structure is carried by one persistent cut and one two-dimensional rotating/contracting relation.
ARA is being used as that relation geometry, not as a remainder calculated after the quantum variables.

## Data and test status

The source is the checksum-pinned public tomography data used in Q7:

- Steinacker et al., *Bell inequality violation in gate-defined quantum dots*, Nature Communications 16, 3606
  (2025);
- data DOI: [10.5281/zenodo.14880901](https://doi.org/10.5281/zenodo.14880901);
- four prepared Bell states;
- eleven Ramsey waits and eleven Hahn-echo waits;
- `88` physical two-qubit reconstructions.

Q7 had already opened the outcomes. Q8 therefore froze its formulas and eleven gates before calculating these
new relation-plane coordinates, but it is still a **post-outcome calibration**, not a blind prediction.

Frozen protocol SHA-256:

`725e307378d8ab8dbcaf31fa1d62dc2715d87f975bdbba0261ade1cc1a448eab`

## Deconstruction 1 — the Bell relation becomes two perpendicular ARA cuts

For Phi-family states:

\[
\underbrace{u_\Phi}_{\substack{\text{first relation cut}\\\text{ARA: one diameter}}}
=
\frac{XX-YY}{2},
\qquad
\underbrace{v_\Phi}_{\substack{\text{perpendicular relation cut}\\\text{ARA: second diameter}}}
=
\frac{XY+YX}{2}.
\]

For Psi-family states:

\[
\underbrace{u_\Psi}_{\substack{\text{first relation cut}\\\text{ARA: one diameter}}}
=
\frac{XX+YY}{2},
\qquad
\underbrace{v_\Psi}_{\substack{\text{perpendicular relation cut}\\\text{ARA: second diameter}}}
=
\frac{YX-XY}{2}.
\]

The two cuts close into:

\[
\underbrace{C}_{\substack{\text{complete phase relation}\\\text{ARA parent on this plane}}}
=
\underbrace{u}_{\text{visible cut}}
+
i\underbrace{v}_{\text{perpendicular cut}}
=
\underbrace{R}_{\text{relation strength}}
e^{i\underbrace{\theta}_{\text{phase/direction}}},
\]

\[
R=\sqrt{u^2+v^2},
\qquad
\theta=\operatorname{atan2}(v,u).
\]

Plainly: \(u\) alone is only a line through the quantum relation. The perpendicular child \(v\) supplies the
missing direction. Together they are one complete parent relation \(C\). Its radius says how strongly the pair
still carries phase information; its angle says where that information sits around the cycle.

If a literal `0–2` ARA coordinate is wanted for either signed standard-quantum cut, the exact affine translation
is:

\[
x_u=1-u,\qquad x_v=1-v.
\]

That is a coordinate translation, not an additional physical law.

## Deconstruction 2 — TE-ARA closes the selected Bell parent

The frozen observable account was:

\[
\boxed{
\underbrace{K}_{\substack{\text{persistent parity}\\\text{parent cut}}}
+
\underbrace{R}_{\substack{\text{phase-sensitive}\\\text{parent relation}}}
+
\underbrace{H}_{\substack{\text{unresolved Other}\\\text{inside this boundary}}}
=2
}
\]

with

\[
K=|ZZ|,
\qquad
H=2-K-R.
\]

The medians were:

| Condition and slice | \(K\) | \(R\) | \(K+R\) | unresolved \(H\) |
|---|---:|---:|---:|---:|
| Ramsey first wait | `0.962079` | `0.969921` | `1.929807` | `0.070193` |
| Ramsey final wait | `0.909182` | `0.054145` | `0.959098` | `1.040902` |
| Hahn first wait | `0.953966` | `0.935796` | `1.886691` | `0.113309` |
| Hahn final wait | `0.781447` | `0.068098` | `0.849544` | `1.150456` |

Plainly: the selected Bell identity begins almost fully expressed by the persistent and phase-sensitive
relations. Under dephasing, the phase relation contracts while the persistent relation remains. TE-ARA still
equals two by definition of the chosen normalized boundary, so the part no longer resolved by \(K+R\) moves into
`Other`.

`Other` is deliberately conservative. It can include system-environment correlation, preparation/readout
limitations and tensor structure outside the compact Bell block. It is **not yet identified as a unique hidden
environmental wave or conserved physical energy**.

## Deconstruction 3 — inferring the hidden perpendicular child

The full parent tensor independently supplies a transverse relation radius:

\[
R_s=\frac{s_2+s_3}{2},
\]

where \(s_2,s_3\) are its two smaller singular values. Given the first child cut \(u\), the hidden perpendicular
magnitude is reconstructed geometrically:

\[
\boxed{
|v|_{\rm inferred}
=
\sqrt{\max(0,R_s^2-u^2)}.
}
\]

Across all `88` records, the median absolute error against the directly measured \(|v|\) was:

\[
\boxed{0.0120460}
\]

on the natural `0–1` correlation-strength scale. The frozen tolerance was `0.08`.

Plainly: once the parent radius and one child are known, the size of the missing perpendicular child follows by
closing the circle. This is the precise version of “use the whole plus the visible Phase A/B to determine what is
left for the hidden wave.”

One boundary is essential: the radius and \(u\) determine **the magnitude** \(|v|\), but not whether \(v\) lies on
the positive or negative side. Those are mirror solutions. A second directional cut, time ordering, or known
family orientation is required to recover the sign. This matches ARA's existing requirement to declare direction
before interpreting a symmetric diameter.

## Deconstruction 4 — rebuilding the larger parent

The compact reconstruction was fixed before calculation.

For Phi:

\[
T_{\rm core}^{\Phi}
=
\begin{pmatrix}
u&v&0\\
v&-u&0\\
0&0&ZZ
\end{pmatrix}.
\]

For Psi:

\[
T_{\rm core}^{\Psi}
=
\begin{pmatrix}
u&-v&0\\
v&u&0\\
0&0&ZZ
\end{pmatrix}.
\]

Its share of the full measured tensor was:

\[
\mathrm{core\ share}
=
1-\frac{\lVert T-T_{\rm core}\rVert_F^2}{\lVert T\rVert_F^2}.
\]

The median shares were:

- Ramsey: `0.984080`;
- Hahn: `0.980694`.

At the initial wait, every declared Bell-family radius exceeded the alternate-family radius by at least
`0.899891`, comfortably above the frozen `0.60` gate.

Plainly: after drilling down to the two perpendicular phase children and the persistent parity child, the larger
Bell parent can be rebuilt with about `98%` of its measured tensor structure retained. The child decomposition did
not flatten the identity; it exposed the small set of relations that generates most of it.

## Dynamical result

At the final Ramsey wait:

- median \(K\) retention was `0.932665`;
- median \(R\) retention was `0.055777`;
- the retention gap was `0.876888`.

The first \(R<0.50\) readings occurred at:

- Ramsey: `16.02 µs` for both Phi states and `20.02 µs` for both Psi states;
- Hahn: `251.19 µs` for all four states.

The geometric-mean Hahn/Ramsey delay was:

\[
\boxed{14.0262\times}.
\]

The \(R<0.50\) event aligned within one sample with Q7's independently calculated transition to one strong
relation axis for every Ramsey state.

Plainly: the ARA relation radius is not merely a decorative redrawing. Its contraction locates the same physical
change that the full singular-value analysis detects, and the Hahn pulse delays that contraction by about
fourteenfold.

## Frozen gates

| Gate | Result |
|---|---:|
| `D1` — 88 physical reconstructions | PASS |
| `D2` — compact-core median share at least 0.90 | PASS |
| `D3` — initially strong \(K\), \(R\), and observable closure | PASS |
| `D4` — every final Ramsey \(K\) retention at least 0.75 | PASS |
| `D5` — every final Ramsey \(R\) retention at most 0.20 | PASS |
| `D6` — median retention gap at least 0.60 | PASS |
| `D7` — singular-model median MAE at most 0.08 | PASS |
| `D8` — \(R<0.50\) aligns with one-axis transition | PASS |
| `D9` — Hahn delay at least fourfold | PASS |
| `D10` — declared family beats alternate family | PASS |
| `D11` — hidden-quadrature median error at most 0.08 | PASS |

Independent validation reconstructed all `88` source rows, matched every audited saved field with maximum absolute
difference `0.0`, and independently reproduced all `11/11` gate outcomes.

## What this supports

Supported on this dataset:

1. A Bell relation can be represented as two perpendicular ARA diameter cuts closing into one complex parent
   relation.
2. The compact \((K,R,\theta,\text{family})\) account retains about `98%` of the full parent tensor structure.
3. The magnitude of a perpendicular child can be inferred from one child and the independently measured parent
   radius with median error `0.0120`.
4. Directional dephasing is expressed as strong retention of \(K\) and contraction of \(R\), and Hahn echo delays
   that contraction.
5. TE-ARA provides a clear normalized allocation ledger for resolved parent relation versus unresolved `Other`.

Not established:

- that \(H\) is a unique hidden ontological Phase B;
- that the missing sign of \(v\) can be recovered without directional information;
- that TE-ARA is conserved physical energy;
- that ARA replaces density-matrix tomography or improves on standard quantum mechanics;
- universal fractality, Information³, phi handover, quantum gravity, or a new quantum law.

The result is stronger than a loose analogy because the formulas exactly reconstruct most of a real measured
parent tensor and pass frozen numerical gates. It remains a compact ARA crosswalk of established Bell/Pauli
geometry, not an independent derivation of quantum mechanics.

## Reproduction

Run:

```powershell
python q8_bell_relation_plane_test.py
python q8_bell_relation_plane_validate.py
```

Artifacts:

- `Q8_BELL_RELATION_PLANE_FIDELITY_v1.md`
- `Q8_BELL_RELATION_PLANE_PROTOCOL_v1_FROZEN.md`
- `Q8_BELL_RELATION_PLANE_PROTOCOL_v1_FROZEN.sha256`
- `Q8_BELL_RELATION_PLANE_RECORDS.csv`
- `Q8_BELL_RELATION_PLANE_GATES.csv`
- `Q8_BELL_RELATION_PLANE_RESULTS.json`
- `Q8_BELL_RELATION_PLANE_VALIDATION.json`
- `Q8_BELL_RELATION_PLANE_DECONSTRUCTION.svg`
- `Q8_BELL_RELATION_PLANE_DECONSTRUCTION.png`
- `q8_bell_relation_plane_test.py`
- `q8_bell_relation_plane_validate.py`

