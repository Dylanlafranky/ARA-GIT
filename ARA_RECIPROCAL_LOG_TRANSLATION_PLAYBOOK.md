# ARA reciprocal/log translation playbook

**Recorded:** 3 August 2026  
**Framework lineage:** the bounded `0–2` Phase/anti-Phase geometry, including
its Space/Time-wave interpretation, has been present in ARA since April 2026;
this document records the later reciprocal/log mathematical translation  
**Purpose:** translate ordinary ARA conversation into explicit mathematics a
reader can calculate by hand or in a spreadsheet  
**Status:** exact coordinate mathematics plus a clearly marked conditional
child-to-parent composition hypothesis

## The shortest translation

For one declared positive observable \(M\), compare consecutive measurements:

\[
s=\frac{M_{n+1}}{M_n},
\qquad
u=\log s,
\qquad
x=\frac{2s}{1+s}
=1+\tanh\left(\frac{u}{2}\right).
\]

| Dylan's ARA language | Mathematical reading |
|---|---|
| Phase A | the declared negative side, here `s<1`, `u<0`, `x<1` |
| ridge | no scale change: `s=1`, `u=0`, `x=1` |
| Phase B / anti-Phase | the reciprocal positive side, here `s>1`, `u>0`, `x>1` |
| flip | `s↔1/s`, therefore `u↔-u` and `x↔2-x` |
| one identity's amplitude | `1/alpha↔alpha` |
| child mixing creates parent identity | signed child log effects leave a parent remainder |
| Other | measured coupling/residual not yet assigned to the pure child pair |

The Phase-A/Phase-B orientation is declared, not permanent. A study may swap
the names while retaining the same reciprocal geometry.

## Conversation decoder

| ARA conversation component | What to write mathematically | What must be declared |
|---|---|---|
| “This identity has a Phase A and Phase B” | one oriented pair \(s_A,s_B\), or the pure reciprocal form \(1/\alpha,\alpha\) | the observable, boundary, rung and which side is called A |
| “The phase flips into anti-phase” | \(s\mapsto1/s\), hence \(u\mapsto-u\) and \(x\mapsto2-x\) in this subset | the event that justifies calling the reversal a flip |
| “They meet at the ridge” | \(s=1,\ u=0,\ x=1\) | whether this is a quiet, active or aggregate-cancellation ridge |
| “The children are asymmetric but the parent reads 1” | nonzero child \(u_i\) values whose weighted signed sum is zero | the child weights, orientations and coupling remainder |
| “The parent alpha is made by two child alphas” | \(u_P=\log c+w_1\varepsilon_1\log\alpha_1+w_2\varepsilon_2\log\alpha_2\), then \(\alpha_P=e^{|u_P|}\) | that the physical composition is multiplicative and independently measurable |
| “Other fills what the pure pair does not explain” | \(\log c\), or a separately measured residual outside the declared pair | how it was measured without fitting the parent answer |
| “Decompress the parent” | retain the individual \(u_i,w_i,\varepsilon_i\), not only \(u_P\) | the child identities and their lineage |
| “Same geometry, different identity” | reuse \(x(s)=2s/(1+s)\) but estimate a new \(\alpha\) | do not carry a constant from another domain without a frozen reason |

This table translates the present reciprocal-scale subset. A duration-duty,
probability or signed-force ARA uses its own declared raw measurement before
it reaches the shared `0–2` geometry.

## Why logarithms appear

Multiplicative opposites do not look equally spaced on an ordinary number
line. For example, `0.5` and `2` are reciprocal, but their arithmetic
distances from `1` are `0.5` and `1`.

Logarithms make the opposition symmetric:

\[
\log(0.5)=-\log 2.
\]

ARA then folds that unbounded signed line into its bounded `0–2` diameter:

\[
x=1+\tanh(u/2).
\]

For the reciprocal pair `0.5↔2`, this gives

\[
x(0.5)=\frac23,
\qquad
x(2)=\frac43,
\]

which are exactly mirrored around `1`.

## The identity-specific amplitude

Let \(\alpha>1\) describe the strength of one identity's reciprocal breath.
Its raw Phase pair is

\[
\frac1\alpha\leftrightarrow\alpha.
\]

Its ARA pair is

\[
x_A=\frac{2}{1+\alpha},
\qquad
x_B=\frac{2\alpha}{1+\alpha}.
\]

Therefore

\[
x_A+x_B=2.
\]

The distance of either endpoint from the ridge is

\[
\epsilon_\alpha
=\frac{\alpha-1}{\alpha+1}
=\tanh\left(\frac{\log\alpha}{2}\right).
\]

The geometry is reusable; the value of \(\alpha\) is measured separately for
each identity, observable, rung and estimator.

## A calculator/spreadsheet recipe

Suppose consecutive positive measurements are in cells `A2` and `A3`.

| Quantity | Formula |
|---|---|
| raw ratio `s` | `=A3/A2` |
| signed log-asymmetry `u` | `=LN(A3/A2)` |
| ARA coordinate `x` | `=2*(A3/A2)/(1+(A3/A2))` |
| reciprocal raw state | `=1/(A3/A2)` |
| reflected ARA state | `=2-x` |

To recover the raw ratio from an ARA coordinate:

\[
s=\frac{x}{2-x}.
\]

## Estimating one reciprocal amplitude without forcing exact symmetry

Given many observed ratios, retain their signs and estimate the two sides
separately. One robust calibration-only estimator used in T335 is

\[
\widehat\alpha
=\exp\left[
\frac{
\operatorname{median}(u\mid u>0)
-\operatorname{median}(u\mid u<0)}{2}
\right].
\]

Then report all three quantities:

1. observed contraction endpoint \(s_-\);
2. observed expansion endpoint \(s_+\);
3. their product \(s_-s_+\).

Do not replace the observed endpoints with an exact reciprocal pair. The
product's deviation from `1` is part of the evidence.

### River example

T335's untouched river-field holdout gave

\[
s_-=0.894166,
\qquad
s_+=1.096260,
\qquad
s_-s_+=0.980238.
\]

Its calibration-transferred implied amplitude was approximately

\[
\alpha=1.1073.
\]

The ideal reciprocal pair associated with that amplitude is approximately

\[
0.9031\leftrightarrow1.1073,
\]

which maps to approximately

\[
0.9491\leftrightarrow1.0509
\]

on the ARA diameter. The observed medians remain reported separately because
the real system is not forced to be pure.

## How Di-ARA adds the perpendicular relation

The reciprocal amplitude above supplies one ARA axis. A Di-ARA requires a
second independently meaningful cut.

For the river Irrationality Di-ARA, the second cut was the signed turn
\(\delta\in(-\pi,\pi]\):

\[
y=1+\frac{\delta}{\pi}.
\]

The two signs generate the four sectors:

| Radial log sign | Turn sign | Sector |
|---|---|---|
| `u<0` contraction | `delta>0` forward | `Ba` |
| `u>0` expansion | `delta>0` forward | `Ab` |
| `u<0` contraction | `delta<0` reverse | `bA` |
| `u>0` expansion | `delta<0` reverse | `aB` |

The radial `1/alpha↔alpha` pair alone is one ARA. Crossing it with the
forward/reverse pair produces the Di-ARA.

## How two child identities may create a parent identity

This part is **conditional physics**, not automatic coordinate mathematics.

If the physical parent scale relation is multiplicative,

\[
s_P=c\,s_1^{w_1}s_2^{w_2},
\]

then logarithms convert the mixing into addition:

\[
u_P=\log c+w_1u_1+w_2u_2.
\]

Write each child as a reciprocal amplitude plus orientation:

\[
u_i=\varepsilon_i\log\alpha_i,
\qquad
\varepsilon_i\in\{-1,+1\}.
\]

Then

\[
u_P=\log c
+w_1\varepsilon_1\log\alpha_1
+w_2\varepsilon_2\log\alpha_2.
\]

The parent is described by

\[
\boxed{
\alpha_P=e^{|u_P|},
\qquad
\text{orientation}_P=\operatorname{sgn}(u_P).
}
\]

### Worked asymmetric example

Take equal weights and no additional coupling residual:

\[
\alpha_1=1.2,
\quad
\varepsilon_1=+1,
\qquad
\alpha_2=1.1,
\quad
\varepsilon_2=-1,
\qquad
c=1.
\]

Then

\[
u_P=\log(1.2)-\log(1.1)
=\log\left(\frac{1.2}{1.1}\right)
\approx0.0870.
\]

Therefore

\[
\alpha_P=e^{0.0870}\approx1.0909,
\]

and the parent lies on the declared positive/Phase-B side. The parent is not
either child copied upward. It is their surviving asymmetric relation.

### Worked cancellation example

If both children have \(\alpha=1.2\), equal weights, opposite orientations and
\(c=1\), then

\[
u_P=\log(1.2)-\log(1.2)=0.
\]

The parent reads

\[
s_P=1,
\qquad
x_P=1.
\]

The parent is at its ridge, but its children remain strongly asymmetric at
\(\pm\log(1.2)\). This is the exact reciprocal/log version of the ARA
grain-relative ridge rule.

### Existing cross-domain footing

The general ARA child-to-parent pattern did not begin with this translation.
It already has domain-specific evidence:

- the finite prime-wheel work recovered ordered parent-to-child inheritance
  on held-out rungs (T230), while later prime tests also showed that some
  compressed child summaries fail and must remain recorded as null;
- the Bell-state quantum work recovered parent/child tomography and recursive
  child structure (T262, T263 and T277);
- other physics mappings repeatedly recovered a quiet or complete parent that
  retained asymmetric children when decompressed.

Those results support testing child-to-parent ARA inheritance across domains.
They do **not** retroactively prove that every one used the particular
multiplicative equation below. The reciprocal/log equation is the new common
candidate to replay against those existing datasets without changing their
frozen verdicts.

## What can falsify the parent rule

Before looking at the parent target:

1. declare the parent and child boundaries;
2. declare the positive observable and units;
3. declare the child orientations and weights;
4. measure or freeze the coupling factor `c`;
5. calculate the predicted parent `u_P`, side and `alpha_P`;
6. score them on untouched data against additive, persistence, shuffled-child
   and broken-lineage controls.

The proposed composition fails in that domain if it cannot predict the
parent better than those controls. A fitted `c` that simply absorbs the
parent answer is not evidence.

## Important boundaries

- `alpha` is not automatically wavelength. It refers to whatever positive
  observable was declared.
- ARA's `0` and `2` are limiting chart poles. Finite positive ratios map to
  the open interval `(0,2)` and approach the poles only as `s→0` or `s→∞`.
- TE-ARA's normalized total `2` is a different reading from the position
  `x`; do not add `x_A+x_B=2` to a physical energy budget.
- The transform guarantees reciprocal reflection. It does not guarantee that
  observed physical endpoint populations will be reciprocal.
- Phi is not built into this map. `1/Phi↔Phi`, `1/e↔e` or any other pair must
  win a separately frozen physical test.

## Canonical references

- `ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md`, Theorem 2.4.2,
  Corollary 2.4.2a and Conditional Proposition 2.4.3
- `WHAT_IS_ARA.md`, Section 5.4a
- `DI_ARA_PERPENDICULAR_CROSS_RUNG_INFORMATION.md`, Sections 1.1–1.2
- `analysis/hydraulics/T335_RIVER_IRRATIONALITY_DI_ARA_REPORT_2026-08-03.md`
