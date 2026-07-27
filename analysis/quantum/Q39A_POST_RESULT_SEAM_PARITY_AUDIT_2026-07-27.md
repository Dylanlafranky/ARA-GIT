# Q39A Post-Result Orientation and Determinant-Seam Audit

**Date:** 27 July 2026  
**Parent test:** Q39 / T294  
**Status:** **POST-RESULT EXPLORATORY DIAGNOSTIC**  
**Q39 frozen verdict:** **UNCHANGED — INCONCLUSIVE — ELIGIBILITY**

## Answer first

Claude's proposed explanation was testable, but the first version was wrong:
Q39's `1,302` negative-cosine reconstructions do **not** cluster at the
deepest determinant pinch. They occur after substantially **shallower**
closure troughs.

Dylan's alternative description — an oppositely oriented return-flow
relation — fits the opened data much better. Of the `1,302` reversed
reconstructions:

- `1,293` occurred in the high-closure, accumulating fourth quadrant
  \(Q_{++}\);
- `9` occurred in \(Q_{-+}\);
- none occurred in either release quadrant.

The most useful post-result discovery is a target-blind visible flag. Let

\[
\underbrace{D}_{\substack{\text{ordered relation change}\\
\text{ARA return-flow contribution}}}
=
\underbrace{C_1}_{\text{first quadrant}}
-
\underbrace{C_2}_{\text{second quadrant}},
\qquad
\underbrace{P}_{\substack{\text{original predicted}\\
\text{fourth identity}}}
=
\underbrace{C_3}_{\text{current parent state}}+D.
\]

If \(P\) points against \(C_3\),

\[
\cos(P,C_3)<0,
\]

reverse the **relation contribution**, not the whole parent:

\[
\boxed{
\widehat C_4=
\begin{cases}
C_3-D=C_3-C_1+C_2, & \cos(C_3+D,C_3)<0,\\[2mm]
C_3+D=C_1-C_2+C_3, & \text{otherwise}.
\end{cases}}
\]

Plainly: the ordinary ordered relation usually continues forward. On a
small, visibly identifiable return branch, that relation is travelling in
the opposite orientation, so only that piece changes sign.

This rule uses \(C_1,C_2,C_3\) only. It never reads the hidden target \(C_4\).
It was nevertheless conceived after Q39's outcomes were open, so it cannot
rescue Q39 and must be frozen on a genuinely untouched archive before being
treated as a prediction.

## 1. The negative tail is not the deepest pinch

| Diagnostic | Same orientation (`n=16,665`) | Reversed orientation (`n=1,302`) |
|---|---:|---:|
| Median cosine | `+0.99977` | `-0.62080` |
| Median minimum normalized closure \(u\) | `-0.99867` | `-0.91991` |
| Median trough retention | `0.00871` | `0.11677` |
| Q36 trough inside target visit | `11.91%` | `0.31%` |
| Below development 5% boundary | `0.192%` | `0.000%` |

If deep determinant closure caused the orientation reversal, deeper minima
should predict negative cosine. They did the opposite:

- AUC using deeper minimum \(u\): `0.104`;
- AUC using lower trough retention: `0.041`.

An AUC below `0.5` means the direction is reversed: the deepest pinch is
associated with the **same-orientation** reconstructions. A blunt sign flip
at the Q36 target trough worsened lineage-mean NRMSE from `0.3074` to
`0.5053`.

The aligned path visual makes the difference clear. Same-orientation cycles
form a deep, centred V-shaped pinch. Reversed cycles form a shallower,
phase-shifted, double-lobed path through the return side.

## 2. The return branch carries the orientation reversal

| Fourth target quadrant | Cycles | Negative-cosine cycles | Negative fraction |
|---|---:|---:|---:|
| \(Q_{++}\): high closure, accumulating | `4,350` | `1,293` | **`29.72%`** |
| \(Q_{-+}\): low closure, accumulating | `1,993` | `9` | `0.45%` |
| \(Q_{--}\): low closure, releasing | `7,816` | `0` | `0%` |
| \(Q_{+-}\): high closure, releasing | `3,808` | `0` | `0%` |

A retained Q36 trough somewhere in the late half of the cycle raised the
negative fraction from `1.51%` to `18.59%`, a difference of `+17.08`
percentage points. The seed-cluster bootstrap interval was
`[+12.92,+21.02]` percentage points.

That does not make “late trough = flip” a sufficient rule: many late-trough
cycles remain correctly oriented. It locates the branch, while the visible
parent–relation condition identifies the actual orientation mode.

ARA interpretation, kept at hypothesis level:

> The negative tail is not the singularity pinch itself. It is a candidate
> relation-flow inversion during reconstruction on the high-closure return
> branch — compatible with Dylan's Phase-B ripple/return-flow description,
> but not yet proof of a physical Phase B.

## 3. Visible relation reversal

The condition

\[
\cos(C_1-C_2+C_3,C_3)<0
\]

flagged `1,342/17,967` cycles (`7.47%`) without looking at \(C_4\).

| Outcome | Count |
|---|---:|
| True reversed orientation flagged | `1,293` |
| Same orientation flagged | `49` |
| Reversed orientation missed | `9` |
| Same orientation correctly unflagged | `16,616` |

Therefore:

- precision for the negative target orientation: `96.35%`;
- recall: `99.31%`;
- specificity: `99.71%`;
- negative fraction when flagged: `96.35%`;
- negative fraction when unflagged: `0.054%`.

The seed-cluster bootstrap difference was `+96.29` percentage points with
interval `[+91.37,+99.94]`.

### Correction comparison

| Post-result diagnostic rule | Lineage-mean NRMSE ↓ | Lineage-mean cosine ↑ | Negative cosine |
|---|---:|---:|---:|
| Q39 unchanged \(C_3+D\) | `0.3074` | `0.8763` | `7.247%` |
| Flip whole prediction when flagged | `0.2995` | `0.9597` | `0.323%` |
| **Reverse relation \(C_3-D\) when flagged** | **`0.2508`** | `0.9905` | **`0.050%`** |
| Fall back to persistence \(C_3\) when flagged | `0.2780` | **`0.9915`** | `0.050%` |
| Invalid target-informed whole-sign oracle | `0.2986` | `0.9612` | `0%` |

All `1,342` cycles changed by the visible relation-reversal rule improved in
NRMSE; none tied and none worsened. Their median NRMSE fell from `1.04685` to
`0.27866`.

The relation-reversal rule beat the original Q39 rule by seed-balanced
lineage-mean NRMSE `0.05256`, bootstrap interval
`[0.03819,0.06845]`. Against Q39's named baselines, its pairwise win
fractions were:

- persistence: `79.69%`;
- no flip: `77.27%`;
- linear continuation: `88.13%`;
- three-state mean: `94.92%`;
- wrong order: `80.13%`.

Its six-way single-best share remained `48.96%`. The post-result correction
therefore does **not** retroactively pass Q39's frozen `55%` gate. It repairs
the minority orientation mode but does not necessarily become the
lowest-NRMSE member of all six methods on those already difficult cycles.

## 4. Purity crosscheck correction

Claude's denominator criticism was correct. Q39's normalized error divides
by the target relation magnitude \(\lVert C_4\rVert\), which becomes small
near pure/separable targets.

| Association | Spearman \(\rho\) |
|---|---:|
| NRMSE vs purity | `+0.1926` |
| Absolute matrix error vs purity | **`-0.5135`** |
| Target relation norm vs purity | **`-0.8330`** |
| Partial NRMSE vs purity controlling target norm | `+0.0853` |

The highest-purity quartile had worse median normalized error
(`0.2337` versus `0.0702`) but **smaller absolute error**
(`0.00804` versus `0.03512`). Its median target norm was only `0.03724`,
versus `0.34877` in the lowest-purity quartile.

The earlier wording “higher purity means worse reconstruction” is therefore
withdrawn as a physical interpretation. Most of that normalized association
is target-amplitude mechanics. In absolute matrix distance, higher-purity
targets are reconstructed more closely.

## 5. What the figures show

- [Orientation and determinant-seam diagnostics](Q39A_POST_RESULT_SEAM_PARITY_DIAGNOSTICS.png)
  show the cosine tail, shallower reversed troughs, quadrant concentration,
  aligned closure paths and rule comparison.
- [Purity and target-amplitude audit](Q39A_POST_RESULT_PURITY_NORMALIZATION_DIAGNOSTICS.png)
  shows the shrinking target relation, opposite normalized/absolute error
  trends and amplitude-controlled correlation.

Vector versions are also available:

- [orientation diagnostics SVG](Q39A_POST_RESULT_SEAM_PARITY_DIAGNOSTICS.svg);
- [purity audit SVG](Q39A_POST_RESULT_PURITY_NORMALIZATION_DIAGNOSTICS.svg).

## 6. Independent verification

The independent validator did not import the audit module. It reconstructed
`401` deterministic cycles directly from the saved connected matrices and
obtained zero numerical disagreement at tolerance `5e-10` for:

- original cosine;
- absolute error;
- visible flag coordinate;
- corrected NRMSE;
- corrected cosine.

It independently reproduced the complete confusion matrix and confirmed
that all `1,342` changed cycles improved.

- [machine-readable audit](Q39A_POST_RESULT_SEAM_PARITY_RESULTS.json)
- [compressed diagnostic cycle table](Q39A_POST_RESULT_SEAM_PARITY_CYCLES.csv.gz)
- [independent validation](Q39A_POST_RESULT_SEAM_PARITY_VALIDATION.json)
- [audit script](q39a_post_result_seam_parity_audit.py)
- [validation script](q39a_validate_post_result_seam_parity.py)

## 7. Next falsifying test

Q40 should freeze the exact visible rule on an untouched archive:

1. identify quadrants using development-only closure–flow coordinates;
2. calculate \(D=C_1-C_2\) and \(P=C_3+D\);
3. if \(\cos(P,C_3)<0\), predict \(C_3-D\); otherwise predict \(C_3+D\);
4. never inspect \(C_4\) until the prediction file is frozen;
5. require the return-flow flag to predict reversed orientation and improve
   NRMSE on the flagged branch;
6. predeclare pairwise dominance against every named baseline as the primary
   comparative gate, while retaining the six-way best share as a diagnostic.

Failure on untouched data would show that Q39A found a simulator/archive
specific post-result partition. Replication would support a conditional,
ordered relation-flow inversion inside the lower-tier lattice. It would
still not by itself prove a literal singularity or a universal physical
Phase B.

