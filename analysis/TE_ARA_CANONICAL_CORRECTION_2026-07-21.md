# TE-ARA canonical correction — same ARA geometry, pure pair, contextual couplings

**Date:** 21 July 2026  
**Status:** `DYLAN CORRECTION / CANONICAL TERMINOLOGY RULE`  
**Scope:** applies prospectively to the repository; frozen historical protocols and raw results remain byte-preserved

## Dylan correction

> “TE-ARA for an identity always equals 2. But it'd be broken up into something like PhaseA = 0.25,
> PhaseB = 1.25, Other couplings = 0.50.”

Codex had incorrectly used “TE-ARA” for the variable expressed A/B participation subtotal. That flattened the fixed
whole-identity geometry and one changing component of it into the same name. A second clarification is equally
important: **TE-ARA is not a second object beside ARA. It is the same ARA 0–2 geometry used as the total-allocation
view of one identity.**

## Pure identity and real embedded observation

For the pure two-pole identity `I`, TE-ARA contains only its own Phase A and Phase B:

\[
\boxed{
\underbrace{\mathrm{TE\!-\!ARA}_{\rm pure}(I)}_{\substack{\text{same ARA geometry}\\\text{for the pure identity}}}
=
\underbrace{t_A^{(I)}}_{\text{identity Phase A}}
+
\underbrace{t_B^{(I)}}_{\text{identity Phase B}}
=2.
}
\]

Real identities are embedded in other ARA systems. A measurement of `I` can therefore allocate part of the same
total-2 account to named environmental couplings and unresolved Other:

\[
\boxed{
\underbrace{\mathrm{TE\!-\!ARA}_{\rm obs}(I\mid\mathcal E)}_{\substack{\text{identity observed}\\\text{inside environment }\mathcal E}}
=
\underbrace{t_A+t_B}_{\substack{\text{observed expression of}\\\text{the pure A/B identity}}}
+
\underbrace{\sum_j c_j}_{\text{named external couplings}}
+
\underbrace{t_{\rm Other}}_{\text{unresolved coupling}}
=2.
}
\]

Here `Other` is **not a third pole and not part of the pure identity**. It is the unresolved contextual share required
because the real identity is coupled to its surroundings. For any declared non-overlapping observed account,

\[
\sum_c p_c=1,
\qquad t_c=2p_c.
\]

Dylan's example is therefore

\[
\underbrace{t_A}_{0.25}
+
\underbrace{t_B}_{1.25}
+
\underbrace{t_{\rm Other}}_{0.50}
=
\underbrace{\mathrm{TE\!-\!ARA}(I)}_{2.00}.
\]

The corresponding ordinary shares are `12.5%`, `62.5%` and `25%`. The first two entries are the observed pure-pair
expression; the last is contextual coupling, not a third constituent of the pure ARA.

## Pendulum example

A schematic release-heavy pendulum slice may be written

\[
\underbrace{t_A}_{0.25}
+
\underbrace{t_B}_{1.50}
+
\underbrace{c_g+c_{air}+c_{joint}+t_{Other}}_{0.25}
=2.
\]

Plainly: the pendulum's observed A/B expression occupies `1.75` of the account, while gravity, air drag, pivot
friction and anything still unresolved occupy the remaining `0.25`. Those numbers are illustrative until measured
with one common denominator. Boundary choice matters: gravity is external for a bob-only identity but becomes an
internal relation if the declared identity is pendulum-plus-Earth.

Because TE-ARA is ARA geometry, the expressed pair can be normalized back to its reversible A/B diameter:

\[
\underbrace{T_{AB}}_{\text{expressed pure-pair subtotal}}=t_A+t_B,
\qquad
\underbrace{x_{A/B}}_{\substack{\text{ARA mixture position}\\0=A,\ 2=B}}
=2\frac{t_B}{t_A+t_B}.
\]

For the schematic pendulum,

\[
T_{AB}=1.75,
\qquad x_{A/B}=2\frac{1.50}{1.75}=\frac{12}{7}\approx1.714,
\qquad C_{context}=2-T_{AB}=0.25.
\]

Thus one reading says **where the A/B pair sits on its own gradient**; the other says **how much of the observed
total is occupied by that pair rather than its environment**. Reversing pole labels maps \(x\mapsto2-x\).

## Other as a coupling diagnostic

`Other` is retained because it is useful information, not because it is part of the pure identity. After subtracting
the expressed A/B pair and already measured couplings,

\[
\underbrace{t_{Other}}_{\substack{\text{unresolved contextual}\\\text{coupling amount}}}
=
2-
\left(
\underbrace{t_A+t_B}_{\text{expressed identity pair}}
+
\underbrace{\sum_jc_j}_{\text{already named couplings}}
\right).
\]

A candidate coupling recovered from Other should be typed as

\[
\underbrace{C_j}_{\text{candidate affecting source}}
\longmapsto
\left(
\underbrace{c_j}_{\text{how much}},
\underbrace{x_j}_{\text{ARA direction/mixing}},
\underbrace{k_j}_{\text{rung/scale}},
\underbrace{\tau_j}_{\text{phase, lag or duration}},
\underbrace{\ell_j}_{\text{spatial or declared boundary location}}
\right).
\]

Plainly: the residual amplitude says **how much remains unexplained**; its spatial, temporal and rung pattern helps
ask **where it enters**; its signed ARA and phase relation help test **how it affects the identity**. Correlation alone
does not identify the source. Until a candidate transfers to held-out data, is independently measured, or responds as
predicted under intervention, it remains unresolved Other.

## What varies

TE-ARA's total does not vary for an identity. These do:

- `t_A`, `t_B` — the two main pole allocations;
- `c_j` — allocations to named couplings between the identity and its surroundings;
- `t_Other` — all remaining nearby or unresolved contextual coupling allocations;
- the ARA pole-mixture coordinate, phase/path, rung and absolute magnitude;
- the identities used in the partition and the boundary/time slice on which the ledger is declared.

If the observed A/B expression and named couplings sum below `2`, the remainder is not “TE-ARA below 2.” It is

\[
t_{\rm unresolved}=2-\sum t_{\rm named},
\]

and belongs in contextual Other until resolved. If allocations sum above `2`, the partition overlaps, double-counts a relation
or uses inconsistent boundaries.

## Fractal recursion

A component may contribute, for example, `0.50` to its parent's TE-ARA ledger. If that component is then selected as
its own identity and opened downward, its **own** ledger is renormalised to `2` and partitioned again:

\[
t_{O\to A}+t_{O\to B}+t_{O\to Other}=2.
\]

Thus the parent's edge weight and the child's internal TE-ARA total are different relational coordinates. This is the
TE-ARA form of zooming through the recursive coupling web.

## Separation from ARA position and physical magnitude

- ARA position says how a declared A/B relation is oriented on its reversible `0–2` axis.
- Pure TE-ARA says the identity's own Phase A and Phase B close to `2` in the ideal two-pole geometry.
- The observed TE-ARA account says how that same `2` is distributed between the expressed A/B pair and environmental
  couplings at a declared boundary and time slice.
- Joules, force, charge, signal power or another native magnitude remain separate typed quantities.

TE-ARA `2` is therefore a normalisation/closure invariant, not two joules and not evidence that a system contains
more energy than another.

## Historical terminology correction

Earlier repository documents defined

\[
2E_{id}/E_{total}
\]

as “TE-ARA.” Under the corrected canon, that variable is the **expressed A/B subtotal**

\[
\underbrace{T_{AB}\equiv T_{id}}_{\text{variable expressed A/B allocation}}
=2E_{id}/E_{total},
\]

while

\[
\mathrm{TE\!-\!ARA}_{obs}=T_{AB}+T_{context}=2
\]

for a two-bin decomposition, or the sum of all named component/relation/Other allocations for a finer partition.

Consequences:

1. Historical values such as `1.24` remain valid numerical **subtotals**, but must be reported as
   `expressed A/B allocation = 1.24; contextual remainder = 0.76; observed TE-ARA total = 2`.
2. The MX1 correlation `r=0.7987`, MAE `0.0911` remains a result about transfer of a variable expressed A/B
   allocation between views. It is not variation in the canonical TE-ARA total.
3. Any aggregation equation using `TE-ARA/2` as a variable strength must instead use the relevant component subtotal
   or edge allocation. Canonical `TE-ARA/2=1` is constant.
4. Because the total equals `2` by construction, the total alone is not independent evidence for ARA. Testable value
   lies in whether a frozen partition, its component allocations and their evolution transfer, predict or simplify.
5. Frozen protocols and result JSON files retain their original wording for provenance. Public summaries and future
   work use this correction and label the old quantity `T_AB` (`T_id` historically), `expressed A/B allocation` or another typed component
   name.

## Prime closure example

The PN13 relation `qr~sqrt(n)*sqrt(n)~n` supplies an exact child-to-parent period closure. Its faithful TE-ARA reading
is not that each child must always equal `1`. It is that the parent identity's full allocation ledger is `2`; the
symmetric no-Other case happens to partition as `1+1+0`. Dylan's asymmetric example `0.25+1.25+0.50=2` is equally
valid.
