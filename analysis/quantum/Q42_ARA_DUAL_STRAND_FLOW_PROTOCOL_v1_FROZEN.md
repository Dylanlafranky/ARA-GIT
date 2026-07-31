# Q42 ARA dual-strand flow and mixing decomposition

Date frozen: 2026-07-28 (Australia/Brisbane)

Test ID: `Q42-ARA-DUAL-STRAND-FLOW-v1`

Status at authorship: frozen before the calculations described below were run.
Both source archives and their Q40/Q41B fourth identities have already been
opened in earlier tests. Q42 is therefore a **pre-calculation frozen
descriptive cross-archive test**, not a prospective target test.

## Question

Does the independently observed forward and return movement close on the
ARA diameter,

\[
x_{\rm forward}(p)+x_{\rm return}(p)=2,
\]

and can the actual fourth matrix movement be separated into:

1. movement along the visible forward/reverse relation axis; and
2. a perpendicular residual retained as `Other` rather than incorrectly
   reversing the whole visible vector?

## Sources

The test reuses the verified local caches from:

- Q40: `unnati_submit_12_inhomo_v1_greedy.hdf5.zip`;
- Q41B: `unnati_submit_12_inhomo_v1_landmax.hdf5.zip`;
- branch: `c2_2local connectivity`;
- 100 seeds, 66 pair identities, 500 samples per archive.

No new archive is opened for Q42.

## Frozen ARA coordinate

For each seed and pair, use development samples `0..249` only. Let \(h(t)\)
be the already-defined connected-closure scalar. Its development 5th and
95th percentiles are \(h_{05}\) and \(h_{95}\). Define

\[
x(t)=2\,\frac{h(t)-h_{05}}{h_{95}-h_{05}}.
\]

Thus the development anchors map to:

- \(x=0\): first singularity;
- \(x=1\): ridge;
- \(x=2\): opposite singularity.

Values are not clipped. Overshoot beyond the development anchors remains
visible.

Eligibility is unchanged from Q40: direction coherence at least `0.80` and
minimum four-quadrant occupancy at least `0.05`.

## Independently measured scalar strands

Use evaluation transitions `250..497`. Split each \(x(t)\) path at observed
sign changes of \(\Delta h(t)\):

- positive run: observed forward/increasing half-wave;
- negative run: observed return/decreasing half-wave.

Zero differences inherit the preceding non-zero direction. A half-wave must:

- contain at least three observed transitions;
- reach \(x\leq0.5\); and
- reach \(x\geq1.5\).

Pair each qualifying positive run only with the immediately following
qualifying negative run. Neither strand is defined from the other.

Resample both observed paths at 33 equally spaced fractions
\(p\in[0,1]\) of their own elapsed sample duration. Preserve the return
strand in its observed high-to-low time direction.

The ARA closure residual is

\[
\epsilon(p)=x_{\rm forward}(p)+x_{\rm return}(p)-2.
\]

Record:

- signed mean residual;
- mean absolute residual;
- maximum absolute residual;
- forward and return durations;
- mean forward and return speeds;
- the equal-duration coordinate
  \(2T_f/(T_f+T_r)\);
- the equal-speed coordinate
  \(2v_f/(v_f+v_r)\); and
- RMS change of \(\epsilon(p)\), the unresolved mixing-flow profile.

The deliberately wrong orientation control reverses the return path in
sample order before calculating closure. It is not a substantive baseline;
it verifies that the temporal orientation carries information.

## Frozen matrix-axis decomposition

For every unchanged Q40 complete four-quadrant evaluation window, calculate
the four actual connected identities \(C_1,C_2,C_3,C_4\). Define

\[
D=C_1-C_2,\qquad Y=C_4-C_3.
\]

Project the actual fourth movement onto the independently observed relation
axis:

\[
\alpha=\frac{\langle Y,D\rangle}{\langle D,D\rangle},
\qquad
x_{\rm matrix}=1-\alpha.
\]

This fixes the ARA landmarks without fitting:

- \(\alpha=+1,\ x_{\rm matrix}=0\): full forward relation;
- \(\alpha=0,\ x_{\rm matrix}=1\): ridge/no net movement along \(D\);
- \(\alpha=-1,\ x_{\rm matrix}=2\): full reverse relation.

Retain the perpendicular part:

\[
R=Y-\alpha D.
\]

Because \(R\) is orthogonal to \(D\) by construction, define the descriptive
TE-ARA participation accounting:

\[
\mathrm{Along}=2\,
\frac{\|\alpha D\|^2}{\|\alpha D\|^2+\|R\|^2},
\qquad
\mathrm{Other}=2-\mathrm{Along}.
\]

These are normalized geometric participations, not joules or physical
energies.

For stability, the registered primary matrix summary uses cycles satisfying

\[
\|D\|\geq0.10\,s_{\rm lineage},
\]

where \(s_{\rm lineage}\) is the development median connected-matrix norm.
All cycles are retained in the output and the excluded fraction is reported.

## Frozen comparisons

Report results separately for:

- greedy and landmax archives;
- two-turn `7.5`, one-turn `15`, and other cadence families;
- all four fourth-visit quadrants;
- especially two-turn Ba (`q4=1`), which Q41B prospectively localized.

The central descriptive checks are:

1. whether independently measured scalar strands close near two;
2. whether correct temporal orientation closes better than the wrong
   orientation control;
3. where the actual matrix movement lies on \(0\!-\!2\);
4. how much matrix participation is retained as perpendicular `Other`;
5. whether the two-turn Ba population is a mixture of complete child-level
   reversals and carried/mixing structure rather than one full parent-vector
   reversal; and
6. whether the result has the same direction in both archives.

No universal numerical support threshold is introduced after seeing these
archives. Q42 measures the missing law and determines what can later be
frozen prospectively on an untouched archive.

## Required controls and validation

- Recompute the \(x\) anchors from development samples only.
- Do not construct either scalar strand as \(2-x\) of the other.
- Verify interpolation endpoints reproduce the observed endpoints.
- Verify \(\langle R,D\rangle\) is numerically zero.
- Verify `Along + Other = 2`.
- Report sample counts, exclusions, medians, interquartile ranges and
  seed-cluster bootstrap intervals for the main archive contrasts.
- Save cycle-level and strand-level records for independent reproduction.
- Produce a static diagnostic figure and inspect the rendered PNG.

## Claim boundary

Q42 can establish a repeatable ARA-coordinate decomposition of these public
simulator archives. It cannot by itself establish a universal physical
mixing law, a hidden quantum field, or transfer beyond this source identity.
Any predictive operator inferred from Q42 must be frozen and tested on an
untouched archive.
