# T322 — cross-scale same-phase golden-section protocol v1 (frozen)

**Frozen:** 31 July 2026, before calculating T322 results  
**Status:** direct test of Dylan's corrected object after T321 measured an
`A -> B -> A` route instead of the `A(parent) -> A(child)` handover  
**Public source:** dynamicslab *MultiArm-Pendulum*, Zenodo
[`10.5281/zenodo.6633719`](https://doi.org/10.5281/zenodo.6633719)

## Question

Let lowercase `a` and `b` be two occurrences of the **same phase type at
adjacent ARA scales**, not Phase A and Phase B:

\[
a=A_{\rm parent},\qquad b=A_{\rm child}.
\]

Does their direct scale relation satisfy the golden-section identity?

\[
\frac{a}{b}
=
\frac{a+b}{a}
=
\phi.
\]

Equivalently,

\[
a^2=b(a+b).
\]

The ordinary within-scale `A -> B -> A` circuit is retained only as the
octave/cycle control. It is not used to construct the T322 ratio.

## Frozen identities and hierarchy

1. Use the three public free-swing triple-pendulum records at `500 Hz`
   (`decimate=20`). Runs 1–2 are development/audit records. Run 3 is the
   primary evaluation record. The public driven triple-pendulum record is a
   secondary transfer check.
2. Rest-centre each arm using its circular mean.
3. Detect positive and negative turning points separately using the previously
   audited rule: prominence `0.02*pi` radians and minimum separation
   `0.4 * 1.333 s`.
4. A positive same-phase recurrence is one positive maximum to the next
   positive maximum. A negative recurrence is one negative minimum to the next
   negative minimum. No intervening opposite-phase turning point is used as a
   measurement vertex.
5. The adjacent scale lineages are frozen as arm 1 -> arm 2 and arm 2 -> arm 3.
   The first arm is the parent and the next arm is the child. Ratios are not
   sorted or inverted after observation.
6. For each parent recurrence, select the same-sign child recurrence having
   the greatest temporal overlap. Break zero-overlap or exact-overlap ties by
   nearest midpoint and then earliest child start time. This is a deterministic
   local handover match; unmatched child recurrences are allowed.

## Frozen primary and secondary lengths

### Primary: elapsed same-phase recurrence time

For each matched event,

\[
a_t=t^{(p)}_{A,k+1}-t^{(p)}_{A,k},\qquad
b_t=t^{(c)}_{A,j+1}-t^{(c)}_{A,j}.
\]

The primary ratios are

\[
r_t=\frac{a_t}{b_t},\qquad
s_t=\frac{a_t+b_t}{a_t}=1+\frac1{r_t}.
\]

### Secondary: motion accumulated inside the same A-to-A gap

For each recurrence, integrate absolute angular motion:

\[
L=\int_{t_A}^{t_{A'}}|\dot\theta(t)|\,dt.
\]

Then calculate

\[
r_L=\frac{L_p}{L_c},\qquad
s_L=\frac{L_p+L_c}{L_p}.
\]

This secondary coordinate checks whether Phi belongs to traversed motion
rather than elapsed time. It cannot overturn the primary verdict.

## Frozen comparison landmarks and residuals

Compare the median primary `r_t` with

\[
1,\quad\sqrt2,\quad1.5,\quad\phi,\quad\sqrt3,\quad2.
\]

For every event also report

\[
e_\phi=\max(|r_t-\phi|,|s_t-\phi|),
\]

and the dimensionless golden-section closure residual

\[
e_G=\frac{|a_t^2-b_t(a_t+b_t)|}{a_t^2+b_t(a_t+b_t)}.
\]

## Frozen controls

- Report arm 1 -> 2 and arm 2 -> 3 separately.
- Report positive and negative same-phase branches separately.
- Repeat the matching after circularly shifting child recurrence identities by
  `17%`, `31%`, and `47%` within each lineage and phase branch. These controls
  preserve the marginal parent and child period distributions while breaking
  their observed local temporal pairing.
- Report the driven record separately as transfer evidence.
- Report the ordinary value `2` explicitly as a candidate. If it wins, this
  realization recovers octave/cycle geometry rather than Phi.

## Frozen gates

- **G1:** Phi is the unique closest landmark to the pooled run-3 median `r_t`.
- **G2:** Phi is the unique closest landmark for both adjacent lineages.
- **G3:** Phi is the unique closest landmark for both same-phase branches.
- **G4:** pooled median `e_phi <= 0.08`.
- **G5:** observed local matching has lower median `e_phi` than all three
  circular-shift controls.

Verdict:

- `5/5`: **SUPPORTED**;
- `3–4/5`: **MIXED**;
- `0–2/5`: **NOT SUPPORTED**.

## Interpretation boundary

T322 tests one literal operationalization of the proposed same-phase
cross-scale handover. A negative result does not reject mathematical Phi or
all possible ARA handovers. In particular, a result near `2` would show that
the selected observable is still reading a complete recurrence/cycle rather
than the slippier inter-scale handover Dylan intends. T321 is retained as a
valid diagnostic of routed `A -> B -> A` geometry but is not a verdict on this
corrected `A(parent) / A(child)` claim.
