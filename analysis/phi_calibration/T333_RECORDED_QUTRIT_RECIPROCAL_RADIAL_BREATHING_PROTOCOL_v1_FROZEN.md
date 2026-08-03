# T333 — recorded-qutrit reciprocal radial-breathing protocol

**Frozen:** 3 August 2026, before calculating the registered endpoint scores  
**Status:** prospective with respect to the T307 reciprocal-radial result; the
source archive and Q53 external-vector extraction were previously opened for a
different directional-return question  
**Primary question:** on a real time-ordered quantum record that contains no
Phi scheduling rule, does the radial part of a whole-circle ARA vector breathe
between the reciprocal landmarks (1/\phi) and \(\phi\)?

## 1. Reason for the test

T307 recovered all four contraction/expansion × forward/reverse states in an
idealised muon-Fusion scheduling model. Its post-gate radial audit placed the
two median radial changes near

\[
\phi^{-1}\longleftrightarrow\phi,
\]

rather than the provisionally proposed asymmetric pair

\[
1/e\longleftrightarrow\phi.
\]

That result cannot establish a physical rule because the scheduling model
already contains \(\phi^{-1}\). T333 therefore freezes the reciprocal-golden
radial prediction on recorded hardware data whose acquisition geometry does
not contain a golden schedule.

## 2. Source and reuse boundary

The source is the ETH Zürich single-\(^{40}\mathrm{Ca}^{+}\)-qutrit
contextuality record used by Q53:

- raw source: `ExpDataYuOh.csv`;
- SHA-256:
  `5410775C307EDEA9F68E95133CF0A733B6CD34E7D9D774B6509472FACE74D55D`;
- `53,459,987` valid sequential measurements;
- thirteen fixed Yu–Oh measurement rays;
- the next ray was selected by the experiment's quantum random-number
  generator.

Q53 reconstructed complete circles on three fixed sphere cuts and retained
the external movement vector between neighbouring whole-circle centres. T333
reuses that checksum-locked extraction. Q53 tested whether vector headings
completed a particular \(1/e\rightarrow\phi\rightarrow1/e\) arc. It did not
test the successive **radial scale ratios** registered here.

This is therefore a new exact question on an existing opened archive, not a
pristine unopened-data test. Any support must be labelled cross-question
external evidence and later replicated on a second archive.

## 3. ARA-first measured object

For plane \(p\), estimator \(c\), and retained whole-circle event \(t\), define

\[
z_{p,c,t}=a_{p,c,t}\exp(2\pi i h_{p,c,t}),
\]

where:

- \(a\) is the Q53 external-centre movement strength relative to the local
  circle radius;
- \(h\) is its directed heading in turns.

This is one complete vector, not two unrelated scalar observables. For a
registered event lag \(\ell\),

\[
q_{p,c,t,\ell}=\frac{z_{p,c,t+\ell}}{z_{p,c,t}}
=s_{p,c,t,\ell}\exp(i\delta_{p,c,t,\ell}).
\]

Its two ARA cuts are:

- radial breathing: \(\log s\), contracting below zero and expanding above;
- directed turn: \(\delta=\arg q\), reverse below zero and forward above.

The four quadrants are the four sign combinations. The primary endpoint test
uses the radial cut only; the directed cut verifies that the full complex
coordinate has not been flattened away.

## 4. Fixed populations

The three registered sphere cuts are:

1. `psi0_psi1`;
2. `psi1_psi2`;
3. `psi2_psi0`.

The primary centre estimator is Q53's algebraic fitted-circle centre
(`circle`). The `centroid` and `extrema` constructions are fixed sensitivity
estimators and cannot rescue a failed primary verdict.

Each plane is split chronologically at its midpoint:

- first half: calibration only;
- second half: frozen holdout.

Registered event lags are

\[
\ell\in\{1,2,4,8,16,32,64\}.
\]

Thus the primary holdout contains \(3\times7=21\) plane-lag cells.

## 5. Fixed quality and continuity rules

An endpoint is eligible only when:

- heading and strength are finite;
- strength is at least `0.01` local circle radii;
- the fitted-circle residual is at most `0.25`.

For a lagged pair, both endpoints must be eligible and every intervening Q53
event-time gap must be no greater than `2200` raw measurement positions. This
fixed ceiling lies just above the previously inspected approximately 99.5th
percentile of the three gap distributions and prevents a tracker restart or
long missing stretch from being treated as one continuous local step.

No smoothing, interpolation, Fourier transform, phase fitting, target-driven
binning or clipping of valid radial ratios is allowed.

## 6. Registered reciprocal endpoint score

For any collection of valid ratios, let

\[
m_- = \operatorname{median}(s\mid s<1),\qquad
m_+ = \operatorname{median}(s\mid s>1).
\]

For a candidate reciprocal pair \((1/\alpha,\alpha)\), define

\[
D_\alpha=
\left|\log m_-+\log\alpha\right|
+
\left|\log m_+-\log\alpha\right|.
\]

Smaller is better. The primary prediction is

\[
\boxed{\alpha=\phi}.
\]

Fixed comparison values are:

- plastic constant \(1.324717957\ldots\);
- \(\sqrt2\);
- rational \(3/2\);
- \(\phi\);
- octave \(2\);
- \(e\).

The \(e\) candidate explicitly tests the reciprocal exponential pair
\(1/e\leftrightarrow e\). The previously proposed asymmetric
\(1/e\leftrightarrow\phi\) is reported separately but is not a reciprocal-pair
competitor.

## 7. Fitted reciprocal control

One global reciprocal endpoint is fitted using only the primary calibration
halves. Pooling all three planes and all seven lags, calculate

\[
\widehat\alpha_{\rm train}
=
\exp\!\left[
\frac{
\operatorname{median}(\log s\mid s>1)
-
\operatorname{median}(\log s\mid s<1)
}{2}
\right].
\]

It is then frozen and scored on the holdout without refitting. This asks
whether exact Phi transfers better than a generic reciprocal breathing scale
learned from the earlier time period.

## 8. Temporal-order null

Use `500` deterministic null replicates with seed `3332026`.

Inside each plane's holdout, divide the original event indices into fixed
blocks of `10,000`. Within every block, permute eligible primary amplitudes
among eligible positions while leaving:

- event times;
- continuity gaps;
- eligibility locations;
- residuals;
- headings;
- the marginal amplitude distribution

unchanged. Recalculate the pooled seven-lag reciprocal-Phi score for each
replicate.

The one-sided empirical percentile is

\[
p=\frac{1+\#\{D_{\phi,\mathrm{null}}\le D_{\phi,\mathrm{observed}}\}}
{501}.
\]

## 9. Frozen gates

### G0 — source and implementation integrity

Pass only if:

- the raw Q53 source checksum matches;
- the derived extraction contains all three expected cuts and finite arrays;
- event counts match Q53's registered extraction;
- an independent validator reconstructs the registered scores from the saved
  events without importing the primary runner.

### G1 — usable four-quadrant coordinate

At lag one in each primary holdout cut, every contraction/expansion ×
forward/reverse quadrant must contain at least `5%` of valid steps.

### G2 — fixed-pair specificity

Phi must have the smallest \(D_\alpha\) among all six fixed reciprocal pairs
in at least `15/21` primary holdout plane-lag cells.

### G3 — absolute ordered endpoints

For each of the three primary holdout cuts after pooling its seven lags:

- \(m_-\) must be within `10%` of \(1/\phi\);
- \(m_+\) must be within `10%` of \(\phi\);
- \(|m_-m_+-1|\le0.05\).

At least two of three cuts must pass all three conditions.

### G4 — temporal-order specificity

The observed reciprocal-Phi score must beat the fifth percentile of its 500
blockwise temporal nulls in at least two of three cuts, and the three-cut
pooled observed score must have empirical \(p<0.05\).

### G5 — out-of-time generalisation

On the pooled primary holdout, exact Phi must score no worse than the one
globally fitted calibration endpoint:

\[
D_{\phi,\mathrm{holdout}}
\le
D_{\widehat\alpha_{\rm train},\mathrm{holdout}}.
\]

### G6 — estimator sensitivity

This is reported but is not allowed to change the primary verdict. Repeat the
holdout endpoint table using `centroid` and `extrema` strengths and state
whether the primary conclusion survives.

## 10. Verdict rule

- **SUPPORTED ON THIS RECORDED EXTERNAL VECTOR:** G0–G5 all pass.
- **PARTIAL / COORDINATE ONLY:** G0 and G1 pass, at least two of G2–G5 pass,
  but the full rule does not.
- **NOT SUPPORTED:** G0 passes but the partial threshold is not reached.
- **INVALID / NO TEST:** G0 fails or fewer than 1000 eligible primary holdout
  ratios exist in any cut.

No post-result reinterpretation can alter this frozen verdict. Exploratory
structure may be recorded separately and must be labelled post hoc.

## 11. Scientific boundary

Even full support would establish a repeatable relation in this recorded
measurement-derived external vector. It would not by itself prove a universal
time wave, a fundamental constant generator, or an ontological quantum
mechanism. A second independently acquired time-resolved archive would remain
necessary.
