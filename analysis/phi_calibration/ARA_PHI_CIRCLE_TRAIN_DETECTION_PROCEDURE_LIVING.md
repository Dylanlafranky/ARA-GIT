# Living procedure — detecting the ARA Phi circle train

**Created:** 2 August 2026  
**Originator:** Dylan La Franchi  
**Formalisation and scientific boundary audit:** Codex  
**Status:** **LIVING METHOD — NOT A FROZEN TEST OR EMPIRICAL RESULT**  
**Current version:** `0.9`

> **Scope revision — 3 August 2026:** This remains the living procedure for
> the narrow, exact Phi-circle candidate. It is no longer the lead procedure
> for the broader rational/irrational ARA question. That parent hypothesis now
> uses a complex quadrant—contraction/expansion crossed with forward/reverse
> phase. Its current ARA placement provisionally spans radial `1/e ↔ Phi`,
> while the exact Phi-circle remains a narrower phase-operator test. See
> `ARA_COMPLEX_IRRATIONALITY_QUADRANT_HYPOTHESIS_2026-08-03.md`. Existing
> frozen Phi-circle tests and verdicts remain unchanged.

This file preserves the current method for looking for the proposed Phi
handover circle in physical data. It may be revised as the geometry becomes
clearer. Every actual test derived from it must be copied into a separately
dated, frozen protocol before the evaluation outcomes are opened.

## Compaction safety rule

If conversation context compacts after a particular dataset test has been
proposed but before it is executed, **stop and restate the exact test to Dylan
in plain language**. Do not run it until Dylan confirms that the identity,
direction, event, rung and intended ARA relation are still correct.

Permission to continue through compaction does not remove this test-specific
reconfirmation rule.

## 1. What is already exact

On one standard ARA diameter, define

\[
a=2-\phi=\phi^{-2}\approx0.38196601125,
\qquad
b=\phi\approx1.61803398875.
\]

The circle whose diameter is `[a,b]` has

\[
\underbrace{\frac{a+b}{2}}_{\text{centre}}=1,
\qquad
\underbrace{b-a}_{\text{diameter}}=\frac{2}{\phi},
\qquad
\underbrace{\frac{b-a}{2}}_{\text{radius}}=\frac1\phi.
\]

Repeating ordinary ARA circles produces a tangent train with period `2`.
Repeating these ridge-centred Phi circles produces a tangent train with period
`2/phi`. Relative to one complete ARA period, its phase step is

\[
\rho_\phi=\frac1\phi\approx0.61803398875.
\]

In raw ARA `0..2` units, the corresponding increment is

\[
\delta_\phi=2\rho_\phi=\frac{2}{\phi}
\approx1.2360679775.
\]

The proposed ordered contact sequence is therefore

\[
\boxed{
x_{n+1}
=
\left(x_n+\delta_\phi\right)\bmod2
}.
\tag{P1}
\]

Equivalently,

\[
x_n=
\left(x_0+n\frac{2}{\phi}\right)\bmod2.
\tag{P2}
\]

These are exact consequences of the declared two-circle construction. The
claim that a physical system follows them is what must be tested.

## 2. Why the signal can look like a ghost

An irrational rotation does not repeatedly occupy one special absolute
position. Over a sufficiently long pure sequence, its positions spread around
the complete circle. Consequently:

- an averaged parent can sit near the `1.0` ridge;
- a histogram can look broad or nearly uniform;
- isolated maxima need not land on `phi` or `2-phi`;
- coarse connected records may display nearby rational values instead;
- destroying temporal order can erase the defining information while leaving
  the marginal distribution almost unchanged.

Therefore the primary target is **ordered displacement between successive
handover events**, not absolute Phi occupancy and not visual resemblance to a
golden spiral.

### Why Phi is being tested, and what may replace it

The search began in April 2026 from a broader ARA intuition. Rational closure
can preserve connection but can also repeatedly revisit the same phase;
unstructured randomness avoids closure but may discard recoverable lineage.
Phi was proposed as a candidate middle path: deterministic, non-closing motion
with organised near-returns, potentially preserving information while avoiding
low-order resonance lock.

This motivation does not establish that the relevant increment is exactly
`2/phi`. The functional target is a **structured irrational or quasiperiodic
handover relation**. Phi is the primary frozen candidate, but another
predeclared irrational or a system-specific quasiperiodic rule may fit that
role. Tests must distinguish:

1. ordered transport from persistence or shuffled order;
2. irrational/quasiperiodic transport from rational cycling and randomness;
3. Phi specifically from other irrational controls.

A result that supports item 2 but not item 3 is evidence for the wider
irrationality slot, not evidence for Phi. The complete historical rationale and
its evidence boundary are recorded in `TWO_RULERS_PHI_AND_TWO.md` under
"Why Phi was hunted".

## 3. The empirical claim

For one independently defined physical identity, successive handover/contact
events should advance around its declared ARA cycle by `2/phi`, subject to
measured noise, external coupling and independently observed singularity
orientation.

The bounded claim for one dataset is:

> The frozen Phi increment predicts untouched ordered handover positions
> better than declared rational, octave, persistence, fitted-development and
> shuffled-order controls.

Even a successful result supports the operator only in the declared system and
measurement. It does not prove that every physical system uses Phi or that ARA
is universally fundamental.

## 4. Required data

Preferred data contain:

1. one continuously trackable identity or lineage;
2. many repeated handover events;
3. raw time order;
4. independently measurable cycle seams or parent boundaries;
5. an observable sign or direction where possible;
6. resolution fine enough to distinguish Phi from nearby rational controls;
7. multiple independent runs, subjects, preparations or archives;
8. minimal preprocessing and complete source provenance.

High-frame-rate wave-tank, vortex, tracer, particle-track or similarly ordered
flow records are currently the most natural candidates. A static spatial
record can qualify only if it contains an independently ordered lineage, such
as a densely reconstructed thalweg across successive cross-sections.

### Resolution gate

The nearest eighth-grid phase fraction to `1/phi` is `5/8`:

\[
\frac58-\frac1\phi
=0.00696601125\ldots.
\]

In raw `0..2` increment units the separation is twice this value:

\[
\frac54-\frac{2}{\phi}
=0.01393202250\ldots.
\]

The frozen child protocol must state measurement uncertainty on the same
scale. If the source cannot distinguish the declared competitors, the verdict
is `INCONCLUSIVE — RESOLUTION`, not support or falsification.

## 5. ARA-first measurement declaration

Before inspecting evaluation outcomes, declare:

1. **Identity boundary:** what remains the same object from event to event?
2. **Observable:** what raw quantity records its handover?
3. **Parent cycle:** which independently observed seams define one complete
   `0..2` period?
4. **Rung:** is the event a child, parent, grandparent or cross-rung relation?
5. **Direction:** what physical sign determines forward versus return travel?
6. **Projection:** what one-dimensional cut of the sphere is being measured?
7. **Event rule:** how are handovers detected without Phi in the detector?
8. **Tie/missing-data rule:** how are ambiguous events handled?
9. **Resolution:** what is the smallest distinguishable ARA displacement?

Do not let an established-domain label redefine this geometry after the fact.
Established terminology should be carried beside the ARA declaration as a
translation column.

## 6. Event extraction must not contain Phi

The event detector must be defined from source measurements alone. Eligible
examples include:

- a sign-changing flux crossing;
- a predeclared local extremum;
- a tracked crest or vortex passing a fixed boundary;
- a source-defined switching event;
- an ordered deepest-point transition between fixed cross-sections;
- a physically recorded contact or transfer event.

Forbidden primary constructions include:

- choosing events because they lie near Phi;
- smoothing bandwidth chosen to make Phi visible;
- Fourier or other transforms used to manufacture the target wave;
- choosing the orientation after observing which direction favours Phi;
- discarding non-Phi events without a predeclared quality rule;
- redefining child and parent after seeing the ratios.

Filtering or transformed views can be shown as secondary diagnostics, but the
primary should remain native to the raw ordered record whenever possible.

## 7. Map each parent cycle to ARA `0..2`

Let independently detected parent seams be (t_k) and (t_{k+1}). For an
event at time (t\in[t_k,t_{k+1})), the simplest time-directed coordinate is

\[
x(t)=2\frac{t-t_k}{t_{k+1}-t_k}.
\tag{P3}
\]

For a spatial lineage, replace time by the declared monotone path coordinate.
The mapping must be selected before evaluation. Local adaptive normalization
is allowed only when the parent seams themselves are independently measured;
Phi cannot define the window.

The resulting ordered sequence is

\[
x_0,x_1,x_2,\ldots,
\qquad x_n\in[0,2).
\]

## 8. Preserve direction and flips

If a physical sign is measured, retain it. Let (s_n\in\{-1,+1\}) be the
independently observed travel direction. The signed model is

\[
x_{n+1}
=
\left(x_n+s_n\frac{2}{\phi}\right)\bmod2.
\tag{P4}
\]

Do not select (s_n) by asking which sign gives the smaller Phi error.

If ARA predicts a singularity flip, the child protocol must state in advance
what observable identifies the crossing and whether the sign should reverse.
A forced alternating-sign model may be registered as a distinct hypothesis,
but must not be substituted for (P1) after seeing failure.

## 9. Primary one-step score

Use circular ARA distance

\[
d_2(a,b)
=
\min\left(|a-b|,\;2-|a-b|\right).
\tag{P5}
\]

The one-step Phi loss is

\[
L_\phi
=
\operatorname{median}_n
d_2\!\left(
x_{n+1},
\left(x_n+s_n\frac{2}{\phi}\right)\bmod2
\right).
\tag{P6}
\]

Report mean and full distribution as secondary summaries. Use uncertainty
resampling at the independent-run or independent-identity level rather than
treating every event as independent.

## 10. Multi-step prediction

Phi must do more than explain adjacent points. Starting from one observed
anchor, freeze

\[
\widehat x_{n+h}
=
\left(
x_n+\frac{2}{\phi}
\sum_{j=0}^{h-1}s_{n+j}
\right)\bmod2
\tag{P7}
\]

when direction is observed. For a fixed forward path this reduces to

\[
\widehat x_{n+h}
=
\left(x_n+h\frac{2}{\phi}\right)\bmod2.
\tag{P8}
\]

Score several horizons fixed in advance. Re-anchoring the model at every event
tests only one-step fit and cannot establish the carrier.

## 11. Fibonacci near-return fingerprint

Let `F_k` be the Fibonacci sequence. The exact identity

\[
\frac{F_k}{\phi}-F_{k-1}
=(-1)^{k-1}\phi^{-k}
\tag{P9}
\]

predicts increasingly close returns of the relative circle phase at Fibonacci
lags. For fixed forward orientation and (k\ge2), the predicted modular ARA
return distance is

\[
R_k^{(\phi)}=2\phi^{-k}.
\tag{P10}
\]

Measure

\[
\widehat R_k
=
\operatorname{median}_n
d_2(x_{n+F_k},x_n)
\tag{P11}
\]

and compare its complete lag profile with:

- neighbouring non-Fibonacci lags;
- each rival rotation's own continued-fraction return lags;
- time-order permutations preserving the same values;
- phase-randomized or broken-lineage controls.

Fibonacci-looking recurrence by itself is insufficient. It must accompany the
correct one-step increment and held-out phase prediction.

## 12. Mandatory rivals

Every child protocol should include at least:

| Model | Phase fraction | ARA increment |
|---|---:|---:|
| Persistence | `0` | `0` |
| Half-turn / ridge | `1/2` | `1` |
| Rational neighbour | `3/5` | `1.2` |
| Nearest eighth | `5/8` | `1.25` |
| Rational neighbour | `2/3` | `1.333333...` |
| Phi | `1/phi` | `2/phi = 1.236067...` |
| Fitted development rotation | fitted on calibration only | twice the fitted fraction |

Add domain-specific nulls where justified. Do not omit a rival because it is
close to Phi; close rivals are the most important discriminators.

The mirrored landmark pair

\[
\left(2-\phi,\phi\right)
\]

and its finite eighth-grid approximation

\[
\left(\frac38,\frac{13}{8}\right)
\]

may be reported as an endpoint/occupancy diagnostic. They are not substitutes
for testing the ordered increment `2/phi`.

## 13. Controls that preserve the ghost's disguise

The strongest controls preserve what a static summary can see while breaking
the proposed carrier:

1. **Within-run time permutation:** preserves all measured values and destroys
   order.
2. **Broken lineage:** substitutes events from another identity while matching
   scale and marginal distribution.
3. **Parent-seam scramble:** independently circular-offset or reassign parent
   cycles, preserving within-cycle values and marginals while breaking
   continuity across the declared seams.
4. **Direction scramble:** preserves event locations but breaks independently
   measured travel sign.
5. **Development fit:** estimates one free constant using calibration only and
   freezes it before evaluation.
6. **Matched irrational controls:** where sample size permits, compare Phi with
   other predeclared irrational rotation numbers so “any irrational works” is
   not mistaken for Phi specificity.

## 14. Data split and freezing

Use, where possible:

- **calibration:** define detector thresholds, quality gates and any physical
  orientation convention;
- **evaluation:** score the frozen primary;
- **external holdout:** replicate on a different run, subject or archive.

Before evaluation:

1. save the dated child protocol;
2. record file identifiers and source provenance;
3. hash the protocol and any frozen predictions;
4. state all exclusions and verdict gates;
5. obtain Dylan's plain-language fidelity confirmation;
6. after any context compaction, repeat that confirmation.

## 15. Verdict gates

A dataset provides meaningful support only if all core conditions hold:

1. **Eligibility:** the identity, lineage, time order and parent seams are
   genuinely measured.
2. **Resolution:** Phi is distinguishable from the nearest declared rival.
3. **One-step prediction:** Phi beats every fixed rival on untouched data.
4. **Free-fit comparison:** the calibration-fitted rotation remains compatible
   with Phi and does not generalize materially better at another value.
5. **Order dependence:** real order beats the time-permuted control.
6. **Lineage dependence:** the true identity beats broken-lineage controls.
7. **Multi-step survival:** Phi retains an advantage beyond one-step
   re-anchoring.
8. **Near-return fingerprint:** Fibonacci-lag behaviour agrees with the same
   Phi model and beats appropriate lag controls.
9. **Replication:** the direction and approximate effect repeat in an
   independent run or source.

Recommended bounded verdicts:

- `SUPPORTED IN THE DECLARED SYSTEM`;
- `MIXED / PARTIAL`;
- `NOT SUPPORTED`;
- `INCONCLUSIVE — RESOLUTION`;
- `INCONCLUSIVE — CONSTRUCT OR ELIGIBILITY`.

No single dataset earns the phrase “proved universally.”

## 16. What does not count as confirmation

- a picture that resembles a golden spiral;
- one ratio near Phi after searching many ratios;
- a histogram peak near `0.382` or `1.618` without ordered prediction;
- a fitted constant near Phi on the same data used to fit it;
- Fibonacci recurrence without the Phi one-step phase law;
- exact mathematics of the constructed circles;
- improved description without holdout prediction;
- a result created by smoothing, filtering or relabelling after inspection;
- recovery only after choosing the favourable flip direction.

## 17. Plain-language field procedure

1. Find one thing that can be followed through many handovers.
2. Mark its complete parent cycles without using Phi.
3. Put each handover on that cycle's `0..2` ARA ruler.
4. Keep the real direction of travel.
5. From the first point, predict the next points by repeatedly adding
   `2/phi` and wrapping at `2`.
6. Do the same with the registered rival steps.
7. Open the withheld events and measure which path was actually closest.
8. Check whether the same path nearly returns at Fibonacci numbers of steps.
9. Break the order and lineage deliberately; the effect should weaken.
10. Repeat on a genuinely independent record.

This is the operational meaning of looking for the “ghost imprint.” We do not
need to see the hidden circle directly. We test whether its proposed contact
rule predicts where the observable system meets our measurement slices.

## 18. Revision protocol

This living procedure may change when:

- Dylan clarifies a different ARA relation or rung;
- a test reveals that the event definition measured the wrong cut;
- a new exact consequence is derived;
- a control exposes a confound;
- a domain supplies a better native observable.

For every revision:

1. preserve the previous wording in version control;
2. add a dated revision-log entry below;
3. state whether the change is mathematical, interpretive or empirical;
4. do not retroactively alter a frozen child protocol or its verdict;
5. write a new child protocol for any retest.

## Revision log

### Version 0.9 - 3 August 2026

- Superseded standalone Phi as the lead explanation of the full ARA
  irrationality/non-locking function.
- Promoted the complex dynamical quadrant—radial contraction/expansion crossed
  with forward/reverse phase—as the parent hypothesis.
- Retained this document as the narrow procedure for testing exact Phi-circle
  progression only after ordered quadrant structure has been established.
- Recorded the current ARA-specific lead placement: provisional radial
  `1/e ↔ Phi`, crossed with forward/reverse phase. This is an asymmetric
  empirical hypothesis rather than a mathematical consequence; the reciprocal
  exponential pair would be `1/e ↔ e`.
- Linked the bubble precedent, where the already frozen complex multipliers
  contained all four sign modes but failed the universal repeated-operator
  gate.
- Canonical revision:
  `ARA_COMPLEX_IRRATIONALITY_QUADRANT_HYPOTHESIS_2026-08-03.md`.

### Version 0.8 - 3 August 2026

- Preserved the April-origin reason Phi was hunted: it was proposed as a
  structured non-repeating relation that could retain recoverable lineage
  without low-order resonance lock.
- Separated the broader candidate class - deterministic irrational or
  quasiperiodic transport - from the narrower claim that the carrier is
  exactly Phi.
- Added a three-stage interpretation rule: first establish ordered transport,
  then irrational/quasiperiodic advantage, then Phi specificity against other
  irrational controls.
- A non-Phi irrational winner now counts as evidence for the wider
  irrationality slot and against the exact-Phi claim, rather than as an
  undifferentiated failure.

### Version 0.7 - 3 August 2026

- Added the T331 `1.2...`-cluster deduplication rule. A left-side landmark
  `s` and its ARA mirror `2-s` have separation `c=2(1-s)`. Consequently
  `2/5`, `8/21`, `2-phi`, `3/8` and `1/e` necessarily map to the narrow
  candidate family `1.2`, `1.238095`, `1.236068`, `1.25` and `1.264241`.
- These transformed candidates count as one registered comparison family,
  not as independent empirical recurrences when repeated across result rows.
- Every future `1.2...` occurrence must be labelled as candidate input,
  algebraic output, freely fitted estimate or unrelated metric before it is
  interpreted.
- Exact-Phi promotion requires a freely estimated held-out result whose
  uncertainty and controls can distinguish `2/phi` from nearby rational and
  constant alternatives, plus persistence, shuffled order and broken lineage.
- Full audit: `T331_PHI_1_2_CLUSTER_DIAGNOSTIC_2026-08-03.md`.

### Version 0.6 - 3 August 2026

- Q60 moved the exact positive recurrence into a time-domain quantum
  interferometer. One complete raw Ramsey sweep was one repeated phase
  identity; its next complete sweep supplied the ordered handover.
- The frozen `2/phi` advance was not present. The calibration-fitted step was
  `0.000256`, and persistence beat Phi decisively in both evaluation and
  chronological holdout. Recorded order also failed shuffle and
  broken-lineage gates.
- This establishes an important exclusion: a repeated coherent interference
  circle is not automatically an eligible Phi circle train. First establish
  that the proposed handover carries ordered motion; a stable laboratory
  phase reference or unordered drift cannot be renamed Vertical Phi.
- Individual sweeps were noisy while averaged Ramsey waves were strong. The
  procedure must report both levels and use identical reconstruction for all
  candidates.
- A future claim that measurement changes irrational transport into a
  connection-fixed record requires conditions that vary which-path or
  measurement strength. It cannot be inferred from Q60's measured-only
  sequence.
- Independent validation passed `70/70` checks.

### Version 0.5 - 2 August 2026

- T329 moved from ordinary bubble headings to independently detected binary
  merger seams without changing the exact `2/phi` candidate.
- A previously frozen detector supplied `52` evaluation and `16` underpowered
  holdout events where one released child ID continued as the parent. The
  joining child's observed side fixed handedness before target calculation.
- Persistence decisively beat Phi in evaluation and holdout. Actual seams did
  not beat broken lineages, contact-side scrambling or immediately preceding
  ordinary turns under the frozen Phi loss.
- The `A_before -> contact -> A_after` decomposition closed exactly, but that
  validates relation bookkeeping rather than the proposed physical constant.
- The field procedure now distinguishes three increasingly strong placements:
  raw frame direction, one actual handover seam, and a repeated handover
  lineage. The first two are unsupported in this bubble archive; the third is
  data-insufficient because only three repeated primary merger links exist.
- Independent validation passed `22/22` checks.

### Version 0.4 - 2 August 2026

- Applied the exact positive operator `x[n+1]=(x[n]+2/phi) mod 2` to raw
  one-frame headings of `170` evaluation and `40` holdout bubble lineages.
- Persistence won both direct local and unreanchored parent scores in every
  split. The recorded ordering did not beat turn shuffles and real lineages
  did not securely beat broken-lineage controls. The direct directional
  carrier is therefore not supported in this observable.
- Phi won the registered Fibonacci-return ranking in calibration, evaluation
  and holdout. A post-result whole-video audit preserved Phi's numerical
  advantage over `8/21`, but did not separate it securely from persistence.
- The bubble archive's median heading grain (`0.04338` ARA) exceeded the
  accumulated Phi-versus-`8/21` separation even at horizon 21. The return
  result is therefore retained as a partial template-ranking clue, not
  exact-Phi recovery. A post-result all-lag audit also showed no concentration
  of observed near-returns at the larger Fibonacci lags.
- This result sharpens the field procedure: always score direct carrier,
  return geometry, lineage, ordering and measurement resolution separately.
  A return-profile win cannot rescue a failed carrier.

### Version 0.3 — 2 August 2026

- Ran the unchanged T325 operator on two independent plant archives and one
  direct ordered river-thalweg cut.
- T326 reconstructed 7,507 ordered events from 196 Landrein Arabidopsis
  plants across eight cohorts. The frozen `3/8` child / Phi parent scale split
  did not replicate: `1/e` won the child score and `8/21` won the parent
  carrier. Real order did not beat 10,000 within-lineage order shuffles
  (`p=0.19808`). Adjacent residual compensation beat a within-lineage shuffle
  (`p=0.03510`) but not broken-lineage pairing (`p=0.44786`), so it is not
  evidence for a lineage-specific Phi carrier.
- The Cyanella archive was retained as a declared resolution control. Its
  22.5-degree bins are much coarser than the 2.508-degree Phi-versus-`3/8`
  separation, so its exact-constant verdict is `INCONCLUSIVE — RESOLUTION`.
- T327 followed the minimum-elevation point through 33 successive flume-bend
  slices and repeated the same downstream-order analysis on elevation ranks
  2–41 as matched controls. Persistence won both local and parent scores;
  true downstream order failed against 10,000 shuffles (`p=0.55094`); the
  thalweg ranked `16/41` for Phi; and `3/8`, not Phi, best matched the frozen
  return fingerprint.
- The river's one-step grain could not separate Phi from `8/21`, but their
  accumulated phase separation exceeded the raw grain by horizon 13. The
  negative parent/order/specificity result therefore remains informative.
- These results constrain the method rather than redefining it. T325 remains
  a valid worked example in its source, but no longer supports a general
  physical-carrier claim without fresh independent replication.
- A validator that imported neither production module rebuilt the principal
  plant and river endpoints and passed `89/89` checks.

### Version 0.2 — 2 August 2026

- Applied version 0.1 to ordered Arabidopsis phyllotaxis in frozen test T325.
- Corrected the source range from a folded `0..180°` cut to the recorded
  directed `0..360°` cycle before any endpoint calculation; the aborted v1
  protocol remains preserved.
- Found the predeclared scale separation: `3/8` won the isolated child-step
  score while exact Phi won the ordered parent carrier and Fibonacci-return
  profile.
- Real order and true within-plant lineage outperformed order-shuffled and
  broken-lineage controls.
- Retained the strict one-step Phi gate. T325 is therefore mixed/partial rather
  than promoted to full support; the procedure is not rewritten to make the
  observed child/parent split count as a universal pass.
- Added T325 as the first worked example of the operational ghost-imprint
  search: local rational occupancy can coexist with an ordered irrational
  carrier, but both must be scored separately.

### Version 0.1 — 2 August 2026

- Created after Dylan's overlaid standard-ARA/Phi-circle drawing.
- Defined the primary ordered increment as `2/phi` on raw ARA `0..2`, or
  `1/phi` of one complete period.
- Added circular one-step and multi-step prediction.
- Added Fibonacci near-return fingerprint.
- Separated endpoint approximation `(3/8,13/8)` from phase increment `5/8`.
- Added mandatory rational, fitted, order and lineage controls.
- Added the compaction reconfirmation rule.

## Canonical references

- `TWO_RULERS_PHI_AND_TWO.md`
- `ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md`, Theorem 9.3
- `EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md`
- `FableConvo/SESSION_RECORD_2026-08-02_PHI_CIRCLE_TRAIN.md`
- `analysis/phi_calibration/T303_PHI_THREE_EIGHTHS_STATE_DUALITY_AUDIT_2026-07-30.md`
- `analysis/hydraulics/T319_LONGITUDINAL_PHI_THREE_EIGHTHS_REPORT_2026-08-02.md`
