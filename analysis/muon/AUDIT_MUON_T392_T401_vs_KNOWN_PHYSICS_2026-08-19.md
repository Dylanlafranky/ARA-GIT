# Audit — four further muon tests (T392, T394, T399, T401)

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** T392 (origin of `x_e*`), T394 (the V−A generator and Super-K release test
underpinning T395/T396), T399, T401.
**Companions:** `AUDIT_MUON_T403_T409_...`, `AUDIT_MUON_T396_T405_...`,
`AUDIT_MUON_T306_T400_...`

**Methodology note:** §0 replaces the gate-amendment rule proposed in the T306/T400
audit, which conflated two different situations. The corrected version is used
throughout.

---

## 0. Corrected methodology — post-result gate amendments

My earlier rule ("a gate may be voided post-result only if the defect is demonstrable
from the protocol text alone") was too crude, and it treated T306 and T409B as the same
event. They are not, and this series already handles them differently — correctly.
Three distinct classes:

**Class A — translation-fidelity correction. Legitimate.**
The gate encodes something the framework does not claim. Where an AI assistant has
mis-translated a framework rule into a numeric gate, the gate tests the wrong
hypothesis and its failure is uninformative. Voiding is a *correction*, not a rescue.

> **T306's G2 is Class A.** It described the child as *slower* than the parent. The
> octave rule states a child one rung down is *faster*, at approximately half the
> parent period. The gate tested the reverse of the claim.
>
> **Audit check performed:** the octave rule predates the protocol. `ARA_SCALE.md` is
> dated 21 July; "octave" appears in the corpus from 21 April. T306's protocol froze
> 30 July. The mismatch is therefore demonstrable against material months older than
> the gate, and verifiable by a stranger. **The void is legitimate.**

**Class B — threshold softening. Not legitimate.**
The gate encodes the claim correctly but the number proved too strict. Adjusting it
after seeing the outcome is post-hoc. No instance of this was found in the audited set.

**Class C — implementation failure. Retain and mark.**
The gate is faithful; the estimator broke. **T409's R3** selecting its own lower
boundary (`1.180`) is Class C, and it was handled correctly — failure retained, T409B
marked descriptive-only and barred from upgrading the observation.

**Standing safeguard for Class A.** The amendment must name the framework document and
date that establishes the mismatch, and that document must predate the protocol freeze.
This keeps the correction auditable and prevents the framework being rewritten to fit.
T306 satisfies this; the citation should be added explicitly to the amendment text.

---

## 1. T392 — spin anti-phase child at the decay handover

**Reported:** sign reversal at `x_e = 0.49019`, bootstrap `[0.48612, 0.49446]`, all five
frozen gates passed, coarse pair `(x_e, x_N) ≈ (0.5, 1.5)`.

### 1.1 The reversal point is Standard-Model exact, analytically

The polarized Michel spectrum is

```
dΓ / dx dcosθ  ∝  x²[ (3 − 2x) + P_μ ξ cosθ (2x − 1) ]
```

The angular term carries the factor `(2x − 1)`, which changes sign at **exactly
`x = 1/2`** for a massless positron. This is not "a known feature near half the
endpoint" — it is an exact zero of a closed-form expression.

So ARA's proposed `0.5` and the Standard Model's `0.5` coincide. ARA earns no
confirmation for agreeing with a value analytic theory fixes exactly. The report says
"not a newly discovered muon-decay law," which is right; it should also say that the
landmark itself is supplied by the SM.

### 1.2 The measurement misses the exact value by more than its own interval

```
SM exact              0.500000
measured              0.490190
bootstrap interval    [0.48612, 0.49446]    ← excludes 0.5
```

The frozen gate required the root inside `0.45–0.55`. Against a quantity the SM fixes
at exactly `0.5`, a `±0.05` band **cannot fail** unless the digitisation is badly
wrong. It is a check on the digitisation, not on ARA. Likewise "much closer to `0.5`
than to `0.25` or `0.75`" is satisfied by anything in the middle third.

### 1.3 This offset propagates into T393 and explains its near-miss

T393 projects `p_e = x_e*/2 = 0.245095` and reports it as `0.004905` below the proposed
quarter. But:

```
if x_e = 0.500000 (SM exact)   →   p_e = 0.250000 exactly
using T392's 0.490190          →   p_e = 0.245095
```

**T393's shortfall from `0.25` is entirely inherited from T392's shortfall from `0.5`.**
It is one systematic digitisation offset of about −2%, appearing twice and reported as
two separate near-misses. Neither is evidence about the landmark.

**Required:** state the SM-exact status of `0.5` in T392, and cross-reference that
T393's `0.245095` carries the same offset rather than being an independent result.

---

## 2. T394 — native neutral pair and causal release

### 2.1 Test 1 is a clean negative and is correctly reported

```
mean pair                              (0.923816, 1.076184)
within L1 0.20 of (0.5, 1.5)            14.6393%
uniform phase-space control             17.2380%
```

The ARA coarse pair is not merely unsupported at this rung — it is **depleted relative
to phase space**. That is a real negative, stated plainly, against interest.

Note it sits alongside T392's claim of `(0.5, 1.5)` at the charged/neutral rung.
Different rungs, so not a contradiction — but the same landmark is being claimed at one
rung and rejected at another, and the two statements should be cross-referenced so a
reader meets both.

The informative positives — label swap moving `P(ν̄_μ heavier)` from `62.51%` to
`50.04%`, and pair asymmetry rising monotonically across charged-energy quintiles
(`0.2245 → 0.7105`) — are real directional structure, and also standard V−A
consequences of `|M|² ∝ (p_μ·p_ν̄μ)(p_e·p_νe)`.

### 2.2 Test 2's baseline `M0` is known-inadequate on physics grounds

This is the significant finding. `M0` is **one truncated exponential** fitted to
stopped-cosmic-muon decay times in Super-K.

Stopped cosmic muons are a `μ⁺/μ⁻` mixture (surface ratio ≈ 1.27). `μ⁺` decays with
`τ = 2.197 μs`; `μ⁻` is additionally lost to **nuclear capture** on oxygen, shortening
its effective lifetime to roughly `1.8 μs` in water. The decay curve is therefore a sum
of two exponentials with different rates *and* different amplitudes.

**A single exponential cannot fit this, and every stopped-muon lifetime measurement
since the 1950s uses a two-component model.** So `MP` beating `M0` by `0.0436` nats is
partly just recovering the `μ⁺/μ⁻` structure — established physics, not ARA geometry.

### 2.3 The gain scales with flexibility, which the report itself notes

```
bins     NLL gain
 32      0.0173
 64      0.0304
128      0.0436
256      0.0630
```

Monotone in bin count. A 128-bin empirical histogram (~128 effective parameters) is
being compared against a 1-parameter exponential. The reversed control `MR` at NLL
`8.87` is not a meaningful bar either — reversing a monotone decay produces something
wildly wrong.

The report states this ("It is also flexible empirical density estimation... may encode
detector timing structure, capture mixture and response features"), which is honest.
But the missing comparison is the one that would make it a test:

**Required:** compare `MP` against a **matched-flexibility non-ARA** density — a
two-component `μ⁺/μ⁻` exponential, and a spline or histogram with the same degrees of
freedom. Until then the `0.0436` measures flexibility and the known two-component
physics, not ARA structure.

What Test 2 *does* establish cleanly: a calibration-fitted density transfers to an
untouched holdout without leakage. That is a competent pipeline validation.

---

## 3. T399 — child half before the delayed release crest

**Reported:** 6/8 gates; failures at the 95% yield-sensitivity threshold and the
circular-shift alignment control.

### 3.1 The *ordering* is forced by monotonicity; only the values are empirical

```
landmark                cumulative ARA
prompt crest              0.244269
branch equality           0.437389
child half                0.500000   ← defined as the 0.5 point of the cumulative
delayed crest             0.600426
```

Cumulative ARA is monotone increasing in time. "Child half" is *defined* as where the
cumulative reaches `0.5`. The delayed crest sits at cumulative `0.600426`. Since the
cumulative is monotone, the time at which it equals `0.5` **must** precede the time at
which it equals `0.600426`.

So "child half occurs before the delayed release crest" is arithmetic once the crest
lands above `0.5`. The empirical content is that the crest's cumulative value is
`0.600426` rather than something below `0.5` — not the ordering.

Similarly the leave-one-out gate ("child half preceded the delayed crest in 17/18
cuts") tests whether the crest's cumulative stays above `0.5` under refitting. That is
a stability check, not an ordering discovery.

**Required:** restate the claim as "the delayed crest sits at cumulative `0.600426`,
above the child half," and drop "ordered sequence" language that implies the order was
measured.

### 3.2 The circular-shift control is the honest measurement and it failed

```
87 of 1,199 wrong relative phases reproduced both the four-landmark order
and a quarter error no larger than the real curve
add-one upper tail p = 0.07333    (gate: p ≤ 0.05)
```

Roughly 7% of arbitrary phase alignments look like the real one. That is the correct
test of whether the alignment is special, and it did not clear its threshold. Correctly
recorded as a failure.

---

## 4. T401 — winner projection and candidate child anti-phase

**All five frozen gates failed.** This is the cleanest negative in the series and the
best-executed test of the four.

### 4.1 It is a self-caught survivor-bias artefact

T400 displayed only the winning bin per split across 20 splits, and no winner landed in
`[1.25, 1.50]`. That absence looked like structure. T401 retained the full distribution
across 200 partitions:

```
mean occupancy of the 1.375 band          11.86%
occupancy vs its two neighbours            0.99106   (effectively equal)
binned winner rate                        13/164 = 7.93%
sampling-only null prediction                      7.50%
two-sided binomial                        p = 0.76727
P(zero winners across 164 splits)         2.79e-6
```

The observed rate is *exactly ordinary*. T400's zero was a 20-split projection accident
with probability `2.8e-6` of recurring at scale.

Identifying that your own earlier visual was survivor bias, building the test that
would expose it, and publishing the result that dissolves it — that is the strongest
methodological item in the four audits I have written.

### 4.2 The reflected anti-phase test also failed independently

```
reflected exchange score      0.04670   (gate 0.20)
negative reflected relations  2/4       (gate ≥ 3/4)
exact reflection rank         13/24     (gate top 3)
C minus AC score              0.09726   (gate 0.10)
```

The centred-log-ratio transform to remove the trivial constant-sum relation before
testing reflection is the right construction — it prevents `x + (2−x) = 2` from
manufacturing the result. Good design.

### 4.3 The overlap caveat is correctly stated

"These heavily overlapping partitions measure resampling stability, not 164 independent
physical experiments." Correct, and it should stay adjacent to the `164` wherever it
appears.

---

## 5. Cross-cutting

**5.1 — SM-exact landmarks, twice.** T392's `0.5` and T393's `0.25` are both fixed
analytically by the polarized Michel spectrum. ARA proposing the same values earns no
confirmation, and the ~2% shortfall in both is one propagated digitisation offset, not
two results.

**5.2 — Baselines need matched flexibility.** T394's `M0` is a known-inadequate
one-parameter model against a 128-bin empirical density, on data whose two-component
`μ⁺/μ⁻` structure is textbook. This is the same defect class as T395's phase-space
decomposition (previous audit): **the reported gain measures the gap to a weak
baseline, not the strength of the geometry.**

**5.3 — Monotone coordinates make orderings free.** T399's landmark sequence is forced
once the landmarks are read off a cumulative. Any claim of the form "A precedes B" on a
cumulative coordinate is arithmetic; only the coordinate values are empirical.

**5.4 — Positive, and it is the strongest theme in this set.** T394 Test 1 reports its
own landmark as *depleted* against control. T399 records the circular-shift failure
that undermines its headline order. T401 fails all five gates on a claim its author
raised. In this group the framework's own predictions lost more often than they won,
and were reported that way.

---

## Required corrections

1. **T392:** state that `x = 0.5` is SM-exact via the `(2x−1)` factor; note that the
   `±0.05` gate cannot discriminate.
2. **T392/T393:** cross-reference that `0.245095` inherits `0.490190`'s offset — one
   systematic, not two near-misses.
3. **T394:** add a matched-flexibility baseline — two-component `μ⁺/μ⁻` exponential
   plus an equal-df spline — before quoting the `0.0436` gain as evidence.
4. **T394/T392:** cross-reference the `(0.5, 1.5)` claim at one rung against its
   rejection at another.
5. **T399:** restate the ordering as a coordinate-value claim; retire "ordered sequence"
   phrasing.
6. **T306 amendment:** add the explicit citation (`ARA_SCALE.md`, 21 July; octave rule
   in corpus from 21 April) that makes the Class A void auditable.
7. **Series:** adopt the §0 three-class scheme for gate amendments.
