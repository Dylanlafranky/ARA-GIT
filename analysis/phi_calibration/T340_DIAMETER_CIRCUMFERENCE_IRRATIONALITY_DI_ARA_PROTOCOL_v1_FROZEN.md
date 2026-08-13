# T340 frozen protocol — diameter/circumference Irrationality Di-ARA

**Frozen:** 4 August 2026, before calculating any test score  
**Test ID:** `T340-DIAMETER-CIRCUMFERENCE-IRRATIONALITY-DI-ARA-v1`  
**Administrative renumbering:** The first execution used `T336`, but that
identifier was already assigned to the ENSO branch. It was changed to `T340`
after scoring and before repository integration. No source, split, formula,
competitor, gate, metric or verdict changed. The original pre-score protocol
SHA-256 was
`52672F7BA5ECC445CF4BB8F40D2C00BCD0D24D29FE1BF2D9DCA09A873E310320`.
**Originator of the ARA hypothesis:** Dylan La Franchi  
**Operationalisation and implementation:** Codex  
**Status:** cross-question validation on previously opened data; not a pristine
discovery test

## 1. Hypothesis frozen before scoring

The complex step

\[
q_n=\frac{z_{n+1}}{z_n}=s_n e^{i\Delta\theta_n}
\]

contains two perpendicular ARA measurements which must not be flattened into
one scalar endpoint:

1. **diameter/radial change:** the real scale multiplier \(s_n\), tested
   against the reciprocal exponential landmarks
   \(1/e\leftrightarrow e\);
2. **circumference/angular change:** the signed fraction of a complete turn,
   tested against the golden non-closing step. In principal-angle form its
   magnitude is

   \[
   \tau_\phi=\phi^{-2}=1-\phi^{-1}\approx0.38196601125
   \]

   turns. This is orientation-equivalent modulo one turn to travelling
   \(1/\phi\) of the circumference in the other direction.

The four sign combinations—radial contraction/expansion crossed with
circumferential forward/reverse traversal—are the Irrationality Di-ARA
quadrants. Occupying four quadrants is structural evidence only and cannot by
itself pass either fixed-constant claim.

## 2. Exact identities and coordinate warning

The historical ARA Phi circle has centre `1` and radius

\[
r_\phi=\phi^{-1}.
\]

Its diameter endpoints are

\[
1-r_\phi=2-\phi=\phi^{-2},
\qquad
1+r_\phi=\phi.
\]

These diameter positions must not be confused with the angular fraction of a
turn. T340 scores the angular observable in **turns**, before any display map
to `[0,2]`.

## 3. Frozen evidence populations

### 3.1 Recorded qutrit — primary real-data archive

- locked Q53 external-vector extraction:
  `analysis/quantum/Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EVENTS.npz`;
- SHA-256:
  `B84918CFF03F2D268DF1C8317CFE16BD93B507BD8CF4CA44A0DBAC79F9F0CE12`;
- reuse the T333 primary `circle` estimator, three declared planes, quality
  rules, continuity rule, chronological calibration/holdout split and lags
  `1,2,4,8,16,32,64` without alteration.

### 3.2 Recorded bubbles — real-data transfer archive

- locked T334 observed-event extraction:
  `analysis/vertical_ara_bubbles/results/T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_EVENTS.csv`;
- SHA-256:
  `262DC32FEE54973223FB4BF4F0D544EAAAB6449761852A3A29F0DCF8AC3D3BA7`;
- use `source_kind=observed` only;
- preserve the frozen calibration/evaluation/holdout split;
- radial variable is the already declared octave-relative value
  \(u=s/2\), not raw scale \(s\);
- angular variable is the native `delta_rad`.

### 3.3 Recorded curved-flume river — real-data domain transfer

- locked T335 event extraction:
  `analysis/hydraulics/results/T335_RIVER_IRRATIONALITY_DI_ARA_EVENTS.csv`;
- SHA-256:
  `A50C13E1F93C0E0115897DDE7F7763B93DC880DBD2DF5BAA6E0EE66FD394FC26`;
- use `source_kind=observed` only;
- rank 1 thalweg is the primary identity; ranks 2–41 are matched path
  controls;
- preserve calibration/evaluation/holdout bend sectors;
- radial variable is native consecutive-step scale `scale_ratio_s`;
- angular variable is native signed turn `turn_delta_rad`.

### 3.4 Muon-Fusion overlap model — construction-positive check only

- locked T307 step extraction:
  `analysis/muon/T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_STEPS.csv`;
- SHA-256:
  `C1F0E60F21C8DF1CECEF8FD6A225C0B0B00E8972A98ADE98FDA65847CC9BB222`;
- use valid steps from the registered primary
  `parent_phi_time_vs_e` pair;
- because the idealised scheduling model already contains Phi and exponential
  components, this population can check implementation direction but cannot
  supply independent empirical support.

## 4. Frozen radial score

For a declared population/split, let

\[
m_- = \operatorname{median}(s\mid s<1),
\qquad
m_+ = \operatorname{median}(s\mid s>1).
\]

For reciprocal candidate \(\alpha>1\), define

\[
D_r(\alpha)=\frac12\left(
|\log m_-+\log\alpha|
+
|\log m_+-\log\alpha|
\right).
\]

The registered radial target is \(\alpha=e\). Fixed competitors are the
plastic constant, \(\sqrt2\), `3/2`, \(\phi\) and `2`.

For each domain with a calibration split, also fit

\[
\widehat\alpha_{\rm cal}
=\exp\left[
\frac{\operatorname{median}(\log s\mid s>1)
-\operatorname{median}(\log s\mid s<1)}2
\right]
\]

on calibration only, then carry it unchanged into evaluation/holdout. The
fitted value is a control, never evidence for the exact \(e\) claim.

## 5. Frozen circumference score

Wrap every signed turn to \((-\pi,\pi]\). Define directional median turn
fractions

\[
a_-=\operatorname{median}\left(-\frac{\Delta\theta}{2\pi}
\middle|\Delta\theta<0\right),
\qquad
a_+=\operatorname{median}\left(\frac{\Delta\theta}{2\pi}
\middle|\Delta\theta>0\right).
\]

For candidate turn fraction \(0<\tau\le1/2\), define

\[
D_c(\tau)=\frac12\left(|a_--\tau|+|a_+-\tau|\right).
\]

The registered circumferential target is
\(\tau=\phi^{-2}\). Fixed competitors are `1/4`, `1/3`, `1/e`, `3/8`,
`2/5` and `sqrt(2)-1`. The deliberately close `1/e` and `3/8` controls make a
golden win non-trivial.

For each domain with calibration data, fit

\[
\widehat\tau_{\rm cal}=\frac{a_-+a_+}{2}
\]

on calibration only and carry it unchanged into evaluation/holdout.

## 6. Frozen gates and verdicts

Each row must report sample counts, both directional medians, all fixed
candidate scores, the fixed-candidate winner and calibration-fitted scores.

For a real-data evaluation or holdout split:

- **radial fixed pass:** `e` has the smallest radial score among all fixed
  radial candidates;
- **circumference fixed pass:** `phi^-2` has the smallest circumference score
  among all fixed angular candidates;
- **joint fixed pass:** both fixed passes occur in the same declared
  population/split;
- **strong transfer pass:** the relevant fixed target also equals or beats its
  calibration-fitted identity-specific control.

The cross-domain fixed hypothesis is supported only if the joint fixed pass
occurs in the holdout of at least two of the three real-data domains. One
domain is insufficient. The muon construction-positive population is excluded
from this count.

Outcomes that recover the two axes or four quadrants but not the fixed
constants support Di-ARA structure while rejecting the universal numerical
placement. Results closer to `3/8` than \(\phi^{-2}\) must be reported as
`3/8`, not rounded or interpreted as Phi.

## 7. Evidence boundary

All four archives were opened before T340, and T333–T335 already established
related complex-quadrant and reciprocal-radial results. T340 therefore tests a
newly frozen **interpretation and fixed placement** on inherited records; it
is not a fully blind discovery. Any positive result requires replication on a
new source whose radial and angular variables are declared before opening.
