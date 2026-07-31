# Q43 child-ridge projection and Phi handover test

Date frozen: 2026-07-28 (Australia/Brisbane)

Test ID: `Q43-CHILD-RIDGE-PHI-HANDOVER-v1`

Status at authorship: frozen before the calculations below were run.

The Q40 greedy and Q41B landmax archives, and the Q42 profiles derived from
them, have already been inspected. Q43 is therefore a **frozen descriptive
cross-archive test**, not a prospective test on untouched quantum data.

## ARA questions

Q42 found that, at matched half-wave progress \(p=0.5\),

\[
\tau(p)=x_{\rm forward}(p)+x_{\rm return}(p)-2
\]

was about \(0.544\) in the aggregate profile.

Q43 separates two hypotheses that must not be allowed to imply one another:

1. **Projected child ridge.** At its own rung a child ridge is \(1.0\). Under
   the already-declared octave-halving rule, the same completed child
   contributes \(0.5\) when viewed one full rung upward. Is the exposed Q42
   residual centred on that parent-view coordinate?
2. **Phi handover.** Does the declared directional pair
   \((2-\phi,\phi)\) carry lower temporal handover tension than ordinary
   symmetric ARA landmark pairs?

The first question can be supported while the second fails, or vice versa.

## Sources and unchanged ARA coordinate

Reuse:

- `Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz`;
- `Q42_ARA_DUAL_STRAND_FLOW_PROFILES.npz`;
- the Q40 greedy development cache; and
- the Q41B landmax development cache.

Do not redefine Q42 eligibility, strand extraction, family labels,
development anchors, or the \(0\!-\!2\) coordinate.

Q42 independently measured the forward and return paths. Neither path was
constructed as \(2-x\) of the other.

## Part A — projected child-ridge test

### Primary population

Use the two-turn `7.5` family, because Q42 localized the large exposed
closure residual there. Report the one-turn `15` family as a control.

At Q42 progress index \(p=0.5\), calculate

\[
\tau_{1/2}
=
x_{\rm forward}(1/2)+x_{\rm return}(1/2)-2.
\]

For every archive and seed, take the median \(\tau_{1/2}\) across eligible
half-wave pairs. The archive estimate is the median of those seed medians.
Use 20,000 fixed-seed bootstrap resamples of seeds for a 95% interval.

The predeclared parent-view child-ridge equivalence band is

\[
0.45\leq\tau_{1/2}\leq0.55.
\]

This is a descriptive tolerance of \(0.05\) parent-rung ARA units. It is not
a universal physical constant.

Support requires the complete seed-bootstrap interval to lie inside that
band independently in both greedy and landmax. Otherwise report the
direction and size of the miss.

### Sampling-control correction

Repeat Q42A's post-result sampling control without changing it:

1. fit each eligible lineage's development half to one symmetric sinusoid at
   that lineage's measured orbit period;
2. sample it at the same integer times;
3. pass it through the unchanged Q42 half-wave extractor; and
4. measure its median synthetic \(\tau_{1/2}\).

For lineages present in both observed and synthetic outputs, define

\[
\tau_{\rm corrected}
=
\tau_{\rm observed}
-
\tau_{\rm symmetric\ sampling}.
\]

This directly tests the proposed explanation that the apparent excess above
\(0.5\) is produced by coarse sample timing. Apply the same seed-balanced
summary and equivalence band. Report both raw and corrected results; the
correction may improve, worsen, or over-correct the child-ridge match.

The synthetic sine is a fitted post-result control, not an independent
physical baseline.

## Part B — directional Phi handover test

Let

\[
\phi=\frac{1+\sqrt5}{2},\qquad
a_\phi=2-\phi,\qquad
b_\phi=\phi.
\]

For a symmetric candidate pair \((a,2-a)\), calculate the fraction of each
half-wave's own elapsed duration at which it crosses the landmarks:

- \(p_f(a)\) and \(p_f(2-a)\) for the increasing path;
- \(p_r(a)\) and \(p_r(2-a)\) for the decreasing path, where progress still
  runs forward in observed time from the high endpoint to the low endpoint.

The directional passage-tension score is

\[
H_t(a)
=
\frac12\left(
\left|p_f(2-a)-p_r(a)\right|
+
\left|p_f(a)-p_r(2-a)\right|
\right).
\]

This compares the same directional handover reached from opposite ends.
Lower is smoother.

As a secondary check, interpolate the absolute local traversal rates
\(\left|dx/dp\right|\) at the same four crossings and calculate the analogous
normalized speed mismatch

\[
H_v(a)
=
\frac12\left(
\frac{|v_f(2-a)-v_r(a)|}{v_f(2-a)+v_r(a)}
+
\frac{|v_f(a)-v_r(2-a)|}{v_f(a)+v_r(2-a)}
\right).
\]

Use only pairs whose independently observed forward and return paths both
span the common interval \(0.20\) through \(1.80\). This ensures every
candidate is evaluated on the same population.

Evaluate:

- the exact Phi pair \((2-\phi,\phi)\);
- a fixed grid \(a=0.20,0.205,\ldots,0.50\);
- named rational references \(a=0.25,1/3,0.40,0.50\).

For each archive and family, first take the median score within each seed,
then the median across seeds.

The predeclared Phi support gate is stringent:

- exact Phi must have lower \(H_t\) than at least 90% of the fixed grid
  candidates in the two-turn family; and
- this must occur independently in both greedy and landmax.

The speed score \(H_v\), the one-turn family, the best grid location, and
comparisons with named rational landmarks are secondary descriptive checks.
They cannot rescue a failed primary gate.

## Required outputs

- lineage-level sampling-control rows;
- archive/family child-ridge estimates and seed-bootstrap intervals;
- the fixed-grid Phi tension curves and exact Phi ranks;
- a static diagnostic figure;
- an independent validation pass checking row/profile alignment, formulas,
  common support, candidate grid, and frozen protocol hash.

## Claim boundary

Q43 can determine whether these already-revealed simulator trajectories are
consistent with a projected \(0.5\) child ridge and whether the exact Phi
pair is privileged under one frozen temporal-handover definition.

It cannot establish that the residual is a physical hidden child, that Phi
is a universal handover constant, or that the result transfers beyond these
archives. Any successful operator must later be frozen on untouched data.
