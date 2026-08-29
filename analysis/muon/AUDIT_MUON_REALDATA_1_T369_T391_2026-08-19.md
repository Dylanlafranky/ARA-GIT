# Audit — real-data muon tests, batch 1 (T369C, T372, T373, T388, T389/T390/T391)

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** the five flagged as highest-weight in the remaining set — the tests where
the framework was most directly exposed to detector physics.
**Methodology:** per `AUDIT_CORRECTION_METHODOLOGY_2026-08-19.md` §0 and §1. ARA-first
is the declared method; established physics is assessed as interpretation and control,
not as the expected source of predictions.

---

## 1. T369C — prompt-energy / neutron-connection branch

**Reported:** `ANTI-DIRECTED ENERGY/CONNECTION BRANCH SUPPORTED`

```
ρ (signed rank)          −0.314980    CI [−0.326753, −0.303274]
holdout rows             20,040
descending adjacent bins 7/7
neutron rate low bin     39.183%
neutron rate high bin     3.225%      ratio 12.15×
shuffle exceedances      0/1,000
hash-half replication    −0.312792 / −0.317226
```

### 1.1 The headline and the caveat point in opposite directions, and the caveat is right

The report's own boundary paragraph states it:

> the `p ≤ 15 MeV` sample is capture-enriched rather than capture-pure. Increasing
> prompt momentum may shift the mixture toward residual muon-decay-electron events,
> which naturally carry fewer capture-neutron tags.

That is not a caveat on the result — **it is the result**. The mechanism is standard:

- `μ⁻` **capture** on a nucleus emits neutrons → neutron tag likely
- `μ⁻`/`μ⁺` **decay** produces an electron/positron with the Michel spectrum extending
  to 52.8 MeV and **no** neutron

So raising the prompt-energy cut moves the sample from capture-dominated to
decay-dominated, and the neutron rate must fall. The anti-correlation is the sample
composition changing with energy.

The `12.15×` ratio supports this reading rather than weakening it. An effect that large
is the size of a composition change, not of a subtle relational coordinate.

**The statistics are sound** — `n = 20,040`, clean shuffle null, replicated across hash
halves, independent raw-source validation. They establish the relation is real. They say
nothing about its cause, and the physics identifies the cause.

**Required:** demote the verdict line. `SUPPORTED` on a relation whose stated mechanism
is a known mixture effect will be read as a finding. Suggested: *"anti-directed relation
confirmed in the detector record; most plausibly explained by the capture/decay mixture
shifting with prompt energy."*

**The test that would separate them:** score the relation *within* fixed capture and
decay subsamples. If it survives inside each, the mixture explanation fails and something
else is present.

---

## 2. T372 — child-half handover gradient

**Reported:** `HANDOVER GRADIENT MAPPED; EXACT CHILD-HALF REMAINS UNCONFIRMED`

### 2.1 The bin-centre correction is exemplary

T371 displayed `(0.492 μs, 0.494 ARA)` because completed 0.5 μs bins were plotted at
their centres. Native 1 ns reconstruction gives `0.4374`. Finding and publishing that an
apparently near-exact `0.5` was a display artefact — on your own prior result — is the
correct handling, and it is the precedent for the same failure mode I raised against
T392's digitisation.

### 2.2 The bootstrap interval is too wide to discriminate any landmark

```
fitted native coordinate    0.4374
95% bootstrap interval      [0.1787, 0.6916]      width 0.5129
```

That interval spans **a quarter of the entire 0–2 diameter**. "`0.5` remains compatible
with this record" is true — and so are `0.2`, `0.25`, `1/3`, `0.375`, `0.4`, `2/3` and
every other candidate in the middle third.

The report's verdict ("compatible but not confirmed") is correct. What is missing is that
the interval width is *why*, and that the measurement cannot distinguish among landmarks
at all. As written, a reader may take "compatible with `0.5`" as weak support. It is not
support; it is non-discrimination.

**Required:** state the interval width and that it excludes no candidate landmark in the
middle third.

### 2.3 The gradient is correctly labelled as an instrument

> the sweep is an exact consequence of the already extracted branch shapes. It is a
> calibration and prediction instrument, not independent evidence for universality.

Correct. And the frozen next-test specification — estimate parent asymmetry without
inspecting the equality handover, predict the sign and magnitude of `Δ_H`, then open the
native timing — is a well-formed prospective test.

---

## 3. T373 — originator identity correction

### 3.1 This is a provenance datum, not just a correction

> T373 changed the measured physical identity from solid CsI to liquid argon, then
> treated the released source-model child cut and the liquid-detector response cut as if
> they occupied the same ARA identity and rung. **Dylan rejected that flattening before
> accepting the result.**

The AI made a rung/identity error; the human caught it *before* the result was accepted.
That is direct evidence for the declared division of labour — geometry from the author,
formalisation from the assistant — and it is worth citing in the prior-knowledge record
alongside the June physics errors, which run the other way.

### 3.2 The `1.25` candidate is unmeasured, not supported

```
observed x_H                 1.238725
proposed 1 + 0.25            1.250000      difference 0.902%
ΔNLL between profiled optimum and exact 1.25      0.000703
```

A likelihood that changes by `7 × 10⁻⁴` across that range **cannot discriminate**. The
report says the likelihood is broad and that Dylan identified `1.25` after seeing
`1.238725` — both correct, and the post-result status is properly recorded.

The precise status is therefore: `1.25` is neither supported nor refuted by this record.
It is unmeasured. That is a stronger and clearer statement than "descriptive lead."

### 3.3 The frozen rule that came out of it is the valuable output

> No result may again be transferred between different media, detector responses or rungs
> without first asking whether the comparison is same-identity, child-to-parent,
> parent-to-child or perpendicular/Di-ARA.

This is the rule that would have prevented the error. Generated from a caught mistake,
frozen, and subsequently observed (the T404 correction follows the same logic). Good.

---

## 4. T388 — same-event anti-phase identification

**Reported:** `DIRECT DETECTOR REPETITION`

### 4.1 This is the most decisive negative in the muon series

```
mapping              median paired RMSE
direct repeat        0.192393     ← winner
x_R-only reversal    0.741836
x_H-only reversal    1.126791
full reversal        1.332082

handedness retained in 100.0% of 650 paired loops
```

The visible out-and-return loop that T387 exposed is the **scintillator/digitizer
response to an energy deposit, repeated after both pulses** — not the muon's physical
anti-phase. That removes an entire interpretation, on 650 paired events, with unambiguous
separation between the winning and losing mappings.

### 4.2 The strongest evidence is stated almost in passing

```
first-pulse median  (x_R, x_H) = (1.000000, 0.157395)
daughter median     (x_R, x_H) = (1.000000, 0.157395)
```

**Identical to six decimal places on both pulses.** That is a far stronger statement than
the RMSE table: the response is stereotyped to displayed precision, which is what a
digitizer does and what a physical process does not. This should be the headline of the
report.

**One thing to check:** `x_R` sits at exactly `1.000000` for both. A coordinate pinned to
the ridge value at full displayed precision usually indicates saturation, clipping, or a
normalisation that forces it. Worth confirming it is a measured median and not a
construction constraint.

### 4.3 Correct claim ceiling

"Even a clean reversal here would remain Class D" — right, and stated before the outcome
was favourable to that framing.

---

## 5. T389 / T390 / T391 — spin anti-phase and the 7.5-turn trigger

### 5.1 T390 is a clean, unambiguous kill

```
pooled observed/expected     0.99868785     a deficit of 0.131%
rank among 8 half-integer landmarks     7th
control 97.5th percentile    1.00180292     not exceeded
bootstrap excess interval    [−0.00356218, +0.00106866]
all five frozen gates        FAILED
```

The 7.5-turn decay trigger is dead, on its own registered terms, and the result is stated
plainly. Note the heterogeneity worth recording: 63 G alone carries the deficit
(`O/E = 0.9816`, residual `−1.576`) while 160 G and 400 G sit flat at `≈1.0005`. So the
pooled deficit is one field, not a consistent shortfall.

### 5.2 The anti-phase itself is trigonometry; the transferable cadence is the result

For a precessing vector, `z(t + T/2) = −z(t)` is the definition of precession, not a
finding. What T389/T391 actually establish is transferable:

- the cadence learned on 20/25 G calibration runs projects into **untouched** 63/160/400 G
  holdouts without fitting orientation;
- correct detector labels beat all 95 cyclic shifts;
- correct cadence beats both wrong-field cadences.

Those are real controls and they are the content. The report should lead with them rather
than with "anti-phase supported," which a physicist will read as restating precession.

### 5.3 The field dependence has an instrumental explanation and should be stated

```
             7.5-turn time   period    samples/turn*   T389 corr    T391 corr
63 G           8.6258 μs    1.1501 μs      71.9        −0.876       −0.751
160 G          3.3964 μs    0.4529 μs      28.3        −0.853       −0.701
400 G          1.3586 μs    0.1812 μs      11.3        −0.707       −0.253
                                          *at 0.016 μs native bins
```

**The correlation degrades monotonically with sampling density, and collapses at 400 G
where there are ~11 samples per turn.** T391's raw-field correlation falls to `−0.253`
there — a third of its 63 G value.

This matters because T370B already found that high-field records crossed the
analysis-resolution boundary. The same instrumental limit is visible here, and it means
the 400 G result is not independent corroboration at full weight. The pooled advantage
`0.50142` with interval `[0.19135, 0.68616]` reflects a genuinely field-dependent
quantity, not a uniform effect measured three times.

**Required:** report samples-per-turn alongside each field, and state that 400 G is
resolution-limited rather than a weaker instance of the same effect.

---

## 6. Cross-cutting

**6.1 — Four of five have the honest reading in the body and a stronger verdict line.**
T369C's verdict says `SUPPORTED` while its boundary paragraph identifies a mixture
mechanism. T372's "compatible with `0.5`" omits that the interval excludes nothing.
T389/T391's "anti-phase supported" restates precession while the transferable-cadence
controls do the real work. T373 records `1.25` as a lead when the likelihood is flat.

In every case the correct statement is present in the document. The defect is at the
reporting layer — verdict lines and headlines that a reader will take at face value
without reaching the qualifying paragraph. That is a fixable and consistent problem.

**6.2 — T388 and T390 are the strongest items in this batch.** Both are negatives, both
removed a live interpretation, both are stated without hedging. T388 in particular closed
off the "visible loop is the physical anti-phase" reading that several earlier tests had
been circling.

**6.3 — The instrumental-limit theme.** T372's bin centres, T388's stereotyped digitizer
response, T391's sampling collapse at 400 G, T369C's capture/decay mixture. Four
independent instances in five tests where the detector, not the physics, is generating or
bounding the signal. That is not a criticism of the programme — it is what working with
real detector archives is like — but it argues for a standing **instrument-first
diagnostic** before ARA scoring: what does this apparatus do to any signal, before we ask
what the signal means.

---

## Required corrections

1. **T369C:** demote the verdict; add the within-subsample test that would separate
   mixture from relation.
2. **T372:** state the bootstrap width `0.5129` and that no middle-third landmark is
   excluded.
3. **T373:** restate `1.25` as unmeasured (ΔNLL `7e-4`), not as a lead.
4. **T373:** cite the caught rung/identity error in the prior-knowledge record as
   evidence for the division of labour.
5. **T388:** promote the identical `(1.000000, 0.157395)` medians to the headline; confirm
   `x_R = 1.000000` is measured rather than forced.
6. **T389/T391:** lead with the transferable-cadence controls; report samples-per-turn;
   mark 400 G resolution-limited.
7. **Series:** add an instrument-first diagnostic step ahead of ARA scoring on any new
   detector archive.

---

**Remaining after this batch: 23 tests** (T307, T368, T369, T369B, T370, T370B, T371,
T374–T380, T382–T387, T402) plus the two partials (T305 full, T404/T405 primary).
