# T307 — Embedded octave-closure crosswalk

Date frozen: 30 July 2026, 14:37 AEST

Test ID: `T307-EMBEDDED-OCTAVE-CLOSURE-CROSSWALK-v1`

Status: **retrospective cross-domain audit**. The Q40C quantum archive and the
T306 constant geometry are already open. During method checking, the global
continuous-period ratio was also inspected. This protocol therefore freezes
the remaining seed-balanced calculation, candidate-factor comparison and
pairing control; it is not a blind prediction.

## Question

Does the exact embedded \(1/e\leftrightarrow\phi\) geometry have the same
dimensionless factor-two closure form as the previously measured quantum
`7.5 : 15` child/parent cadence?

This is a test of a **shared relational form**, not equality of physical units
and not evidence that \(1/e\), \(\phi\), quantum periods and muon-fusion
scheduling are the same object.

## Source lock

- T306 result:
  `analysis/muon/T306_EMBEDDED_E_PHI_THREAD_RESULTS.json`
  - SHA-256:
    `F1D524DD32B7A6B1DFF5537FE0313164A318B0710BBFDCEE0A74FDFB1A483484`
- Q40C result:
  `analysis/quantum/Q40C_POST_RESULT_DOUBLE_HELIX_RESULTS.json`
  - SHA-256:
    `5BFDEA834CD3E9F40ECD0FEF75DEE8A848D00902C62F342FA1DB96F21128B242`
- Q40C source calculation:
  `analysis/quantum/q40c_post_result_double_helix_projection_audit.py`
  - SHA-256:
    `F1180A851C7792D774146B97BC7F0D4D50DE138EDCD3271A68738900B48F2A81`

No simulator trajectories are refit in T307. The continuous development
periods and unchanged Q40C family flags are read from the saved result.

## ARA geometry calculation

Let

\[
\ell=e^{-1},\qquad
h=2-\phi=\phi^{-2}.
\]

The parent interval is \([\ell,\phi]\). Its centre and displacement from the
ARA ridge are

\[
m_P=\frac{\ell+\phi}{2},
\qquad
d_P=1-m_P.
\]

The embedded child interval is \([\ell,h]\). Its radius is

\[
r_C=\frac{h-\ell}{2}.
\]

The declared geometric closure coordinate is

\[
G=\frac{r_C}{d_P}.
\]

Because \(h=2-\phi\), \(G=1\) is an **exact algebraic identity**:

\[
r_C
=
\frac{(2-\phi)-1/e}{2}
=
1-\frac{\phi+1/e}{2}
=d_P.
\]

This identity is a formal crosswalk target, not an empirical discovery.

The complete interval widths are not predeclared as an octave pair:

\[
\frac{(2-\phi)-1/e}{\phi-1/e}
\approx0.01127,
\]

not \(1/2\). T307 therefore tests a matching factor-two **closure form**,
not literal equality of the constant interval-size ratio and the quantum
period ratio.

## Quantum cadence calculation

For every seed containing both unchanged Q40C families:

- \(T_C(s)\) is the median continuous period among
  `two_turn_7_5` rows;
- \(T_P(s)\) is the median continuous period among
  `one_turn_15` rows.

The cadence closure coordinate is

\[
Q_s=\frac{2T_C(s)}{T_P(s)}.
\]

The factor-two octave correspondence predicts \(Q_s=1\). T307 will report:

- number of eligible seeds;
- pooled continuous medians;
- median and mean \(Q_s\);
- 2.5%, 25%, 75% and 97.5% seed quantiles;
- mean and median absolute distance \(|Q_s-1|\); and
- a deterministic 10,000-resample seed bootstrap interval for median \(Q_s\)
  using random seed `20260730`.

## Candidate-factor control

For

\[
k\in\{1,\ 3/2,\ \phi,\ 2,\ e,\ 3\},
\]

score

\[
E(k)=\operatorname{median}_s
\left|
\log\frac{T_P(s)}{kT_C(s)}
\right|.
\]

The factor `2` must be the unique minimum.

This is a scale-form control. Since Q40C families were identified around
approximately `7.5` and `15`, it cannot by itself establish a new empirical
law.

## Pairing control

To distinguish a shared global cadence rule from seed-specific
child-to-parent pairing:

1. compute the observed mean
   \[
   A_{\rm paired}=\operatorname{mean}_s |Q_s-1|;
   \]
2. permute the parent medians across the eligible seeds 10,000 times while
   keeping child medians fixed;
3. calculate
   \[
   p_{\rm pair}
   =
   \Pr(A_{\rm shuffled}\le A_{\rm paired}).
   \]

Specific pairing is supported only when \(p_{\rm pair}\le0.05\). Failure means
the factor-two relation is population-wide but does not identify which parent
belongs to which child.

## Frozen gates

| Gate | Criterion |
|---|---|
| G1: cadence closure | the 95% bootstrap interval for median \(Q_s\) lies wholly inside `[0.995, 1.005]` |
| G2: factor specificity | `2` uniquely minimizes \(E(k)\) |
| G3: seed-specific pairing | \(p_{\rm pair}\le0.05\) |

Interpretation:

- G1 + G2 pass: **Q40C factor-two cadence supported and formally analogous
  to the exact constant closure identity**;
- G3 pass: additionally supports seed-specific child/parent matching;
- G3 fail: retain only the population-level structural crosswalk.

## Boundaries

Even a complete pass would not prove:

- universal ARA fractality;
- that the exact constant identity caused the quantum cadence;
- that \(\phi\) sets the Q40C period;
- transfer beyond the deterministic simulator;
- physical equality between coordinate distance and elapsed samples.
- a literal `1 : 2` ratio between the raw embedded-child and parent constant
  intervals.

The clean prospective test is a changed simulator intervention for which the
two continuous cadence modes move away from `7.5` and `15`, while their
ratio remains approximately `2` under unchanged extraction.
