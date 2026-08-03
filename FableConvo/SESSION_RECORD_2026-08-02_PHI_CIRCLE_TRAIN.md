# Session record — ridge-centred Phi circle train

**Date:** 2 August 2026  
**Originator:** Dylan La Franchi  
**Mathematical translation and boundary audit:** Codex  
**Source sketch:** `C:\Users\Dylan\Desktop\Phicircles.png`  
**Status:** exact geometry for the declared construction; physical use untested

## Dylan's geometric statement

Dylan drew the standard ARA circle train as repeated cream circles of diameter
`2`, then overlaid a repeated blue circle train defined by the mirrored Phi
landmarks. The intended reading was not simply “smaller children nested inside
larger parents.” It was two repeated circle/wave systems sharing one axis. The
second system drifts through the first and is proposed as the moving handover
relation.

Dylan also proposed that flipping and repeating this relation may carry the
handover through parent/grandparent ridges and singularities, and may explain
the recurring `3/8` and `9/8` observations.

## Exact mathematical decomposition

Let the ordinary ARA diameter be `[0,2]`, and let

\[
a=2-\phi=\phi^{-2}\approx0.38196601125,
\qquad
b=\phi\approx1.61803398875.
\]

The blue circle using `[a,b]` as its diameter has

\[
\frac{a+b}{2}=1
\]

as its centre, so its first placement is exactly ridge-centred. Its diameter
and radius are

\[
\ell=b-a
=2\phi-2
=\frac{2}{\phi}
\approx1.2360679775,
\]

\[
r=\frac{\ell}{2}
=\frac1\phi
\approx0.61803398875.
\]

The cream tangent-circle train repeats every `2`. The blue tangent-circle
train repeats every `2/phi`. Relative to one cream period, the blue phase step
is therefore

\[
\frac{2/\phi}{2}=\frac1\phi.
\]

One exact contact-phase record is

\[
h_n=
\left[
(2-\phi)+n\frac{2}{\phi}
\right]\bmod2.
\]

Because `1/phi` is irrational, no positive finite number of blue steps returns
to exactly the same phase of the cream train. The relative contact phase walks
through the full ARA cycle rather than locking permanently.

The natural near-returns are Fibonacci:

\[
\frac{F_k}{\phi}-F_{k-1}
=(-1)^{k-1}\phi^{-k}.
\]

After Fibonacci numbers of steps, the relative phase comes increasingly close
to its earlier position while remaining non-identical.

## Phi and `3/8`

On an eight-part grid, the nearest symmetric rational endpoint pair is

\[
\left(2-\phi,\phi\right)
\approx
\left(\frac38,\frac{13}{8}\right).
\]

The two endpoint errors are exactly equal:

\[
\frac{13}{8}-\phi
=(2-\phi)-\frac38
=0.00696601125\ldots.
\]

This supplies a precise mathematical mechanism for the existing ARA phrase
**“3/8 is Phi cooled into connection”**:

- the moving/non-locking relation is the irrational Phi pair;
- a finite eight-part connected representation records the nearby rational
  pair `3/8` and `13/8`.

This is a candidate interpretation, not proof that every connected physical
system takes those values.

## The `9/8` distinction

The earlier arithmetic

\[
3\left(\frac38\right)=\frac98
\]

is exact and remains a valid three-step generator candidate. It is not forced
as the period or endpoint of the two-circle train. In the present construction,
the directly forced eighth-grid pair is `3/8` and `13/8`.

If “eight child passages plus a ninth returning state” is intended as a cycle
count rather than the literal number `9/8`, that is a separate hypothesis and
remains open.

## ARA interpretation

The result gives a clean two-ruler geometry without replacing the declared
ARA sphere:

- `2` is the complete rational circle/structural period;
- `2/phi` is the diameter of the ridge-centred handover circle;
- `1/phi` is the relative phase advance per base-circle period;
- the moving contact does not repeatedly occupy one fixed landmark;
- Fibonacci counts create near-closure without resonance death;
- a Phase-A/Phase-B flip label can be added to alternating circles, but the
  label is not forced by the unlabeled circle metric itself.

This is compatible with the Hexagon/Pentagon language: a rational closure
scaffold carries a non-locking pentagonal/Phi handover. It does not overturn
the adverse physical results in Q59, T321 or T322; those tested different
operationalizations.

## River/thalweg correction

The same distinction shows why the 2 August river maxima test did not directly
measure this new operator. T319 measured

\[
s_v=\arg\max_s U_s(s),
\qquad
s_d=\arg\max_s D_{\rm centre}(s),
\]

two absolute maxima along a fixed centreline. A direct thalweg handover test
would instead reconstruct the ordered deepest-point path across successive
cross-sections, such as

\[
y_t(s)=\arg\max_y D(s,y),
\]

and then measure signed displacement/contact phase from one retained slice to
the next. A thalweg is not defined as Phi in established hydraulics. Phi is
the ARA hypothesis to test on that ordered path.

T319 therefore remains a valid longitudinal-extrema proxy with an inconclusive
resolution verdict. It is not a direct test of the Phi circle-train operator.

## Frozen future test thread

The maintained version of this method is
`analysis/phi_calibration/ARA_PHI_CIRCLE_TRAIN_DETECTION_PROCEDURE_LIVING.md`.
This section preserves the initial version recorded in the session.

A future test should be registered before opening the evaluation data:

1. choose one ordered identity path with enough resolution;
2. declare its ARA period-`2` support and orientation;
3. calculate successive handover/contact displacements without using Phi to
   construct the observations;
4. freeze the predicted increment `2/phi`, equivalently `1/phi` of the base
   period;
5. compare with rational rivals, fitted-development controls and shuffled
   order;
6. predict held-out contact phase;
7. test whether near-closures concentrate at Fibonacci counts more strongly
   than under matched irrational and rational controls.

Success requires prospective phase prediction, not merely visual similarity
or one point lying near a Phi landmark.

## Evidence tiers

- **Exact mathematics:** ridge centre, `2/phi` diameter, `1/phi` radius and
  relative step, irrational non-closure, Fibonacci near-return identity, and
  the equal-error `3/8`/`13/8` approximation.
- **ARA structural interpretation:** Phi as a moving handover train carried
  through the rational period-`2` scaffold; `3/8` as its finite connected
  representation.
- **Open empirical claim:** physical systems across domains implement that
  circle train and its Fibonacci near-closures.
- **Not claimed:** `9/8` is automatically the train period; every thalweg is
  Phi; or the construction repairs earlier negative results.

## Canonical cross-references

- `TWO_RULERS_PHI_AND_TWO.md`
- `EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md`
- `ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md`, Theorem 9.3
- `GLOSSARY.md`
- `CLAIMS_STATUS.md`
- `analysis/phi_calibration/T303_PHI_THREE_EIGHTHS_STATE_DUALITY_AUDIT_2026-07-30.md`
- `analysis/phi_calibration/ARA_PHI_CIRCLE_TRAIN_DETECTION_PROCEDURE_LIVING.md`
- `analysis/hydraulics/T319_LONGITUDINAL_PHI_THREE_EIGHTHS_REPORT_2026-08-02.md`
- `MASTER_PREDICTION_LEDGER.md`
- `FableConvo/PROVENANCE_LEDGER.md`

## Independent empirical follow-up: T326 and T327

The circle-train construction was then tested without changing its frozen
operator.

T326 used independent Landrein Arabidopsis lineages. Across 196 plants and
7,507 events, the T325 `3/8` child / Phi parent separation did not replicate:
the child winner was `1/e`, the parent winner was `8/21`, and true event order
did not beat 10,000 order shuffles (`p=0.19808`). A short-range compensation
signal survived within-lineage shuffling (`p=0.03510`) but not broken-lineage
pairing (`p=0.44786`). Cyanella was retained as a coarse resolution control;
its 22.5-degree bins cannot distinguish Phi from `3/8`.

T327 performed the direct river test called for above. It reconstructed the
minimum-elevation point through 33 ordered flume-bend cross-sections and ran
the same downstream analysis on all other elevation ranks as 40 matched
control paths. Persistence won both local and parent comparisons, true order
failed against 10,000 shuffles (`p=0.55094`), and the thalweg ranked `16/41`
for the Phi carrier. `3/8` best matched the return profile. Multi-step Phi
versus `8/21` separation exceeded the raw spatial grain at horizon 13, so the
central negative result is not merely unresolved source resolution.

The scientific reading is deliberately asymmetric:

- the ridge-centred circle-train mathematics remains exact for its declared
  construction;
- T325 remains a real within-source pattern;
- the frozen physical carrier did not generalise in these first independent
  tests;
- neither the living method nor the geometry was retuned after seeing the
  misses.

Joint independent validation rebuilt both result families without importing
the production analyses and passed `89/89` checks. Canonical empirical record:
`analysis/phi_calibration/T326_T327_PHI_CIRCLE_TRAIN_CROSS_DOMAIN_REPORT_2026-08-02.md`.

## Direct bubble-direction follow-up: T328

After explicitly reconfirming the test following context compaction, T328
mapped each raw one-frame displacement direction of an uninterrupted bubble
identity to the ARA `0..2` circle and froze the exact positive recurrence

\[
x_{n+1}=\left(x_n+\frac{2}{\phi}\right)\bmod2.
\]

The analysis retained `170` evaluation roots and `40` strict-holdout roots.
Persistence won local and unreanchored parent scores in calibration,
evaluation and holdout. True order was ordinary under 10,000 within-root turn
shuffles (`p=0.49045` evaluation; `p=0.68243` holdout), and the real-lineage
advantage over broken lineages was not cluster-secure.

Phi nevertheless won the predeclared six-lag Fibonacci return fingerprint in
all three splits. A post-result validation audit found that numerical return
advantage over `8/21` in evaluation and holdout, while Phi-versus-persistence
intervals still crossed zero. The source's median heading grain was `0.04338`
ARA; the exact Phi-versus-`8/21` separation remained smaller even at horizon
21. A post-result all-lag audit found no shrinkage toward zero at the larger
Fibonacci lags, so this is a reproducible fixed-template ranking rather than
an observed near-closure sequence. The frozen verdict is therefore **PARTIAL
/ MIXED**: a return-score win, but no direct carrier, order, lineage,
near-closure or exact-constant recovery.

Independent validation passed `107/107` checks with zero raw-root spot-check
error. Canonical record:
`analysis/vertical_ara_bubbles/T328_PHI_CIRCLE_TRAIN_BUBBLES_REPORT_2026-08-02.md`.

## Actual binary-merger handover follow-up: T329

T329 implemented the narrower reading of Theorem 9.3 after T328 showed that
ordinary headings were persistence-heavy. It reused the previously frozen
primary merger detector and retained only events where one released child ID
continued exactly as the parent. The declared three vectors were the
inherited pre-merger direction, the joining-child contact direction, and the
inherited parent direction after merger. The contact side fixed event
handedness before target scoring.

The test retained `23` calibration, `52` evaluation and `16` holdout seams.
Persistence won evaluation (`0.286706` mean circular loss) and holdout
(`0.419947`), while Phi returned `0.651495` and `0.553797`. In evaluation,
Phi-minus-persistence was `+0.364789` with cluster interval
`[+0.229724,+0.503693]`. Broken-lineage, contact-side-scramble and pre-event
turn controls did not establish a Phi-specific seam.

The Information³ relation

\[
x_{AA}=(x_{AB}+x_{BA})\bmod2
\]

closed to machine precision, showing that the directional handover can be
decompressed consistently into inherited-to-contact and contact-to-parent
legs. That identity is mathematical bookkeeping, not a physical Phi result.
The median seam grain (`0.037218` ARA) also exceeded Phi-versus-`26/21`
separation (`0.002027` ARA). Only three primary lineages had another detected
merger, so the full Fibonacci near-return train was not tested.

T329 is therefore a clean negative one-step handover test and does not become
a new empirical carrier by moving the coordinate again. Independent
validation passed `22/22`. Canonical record:
`analysis/vertical_ara_bubbles/T329_ACTUAL_HANDOVER_PHI_SEAM_REPORT_2026-08-02.md`.
