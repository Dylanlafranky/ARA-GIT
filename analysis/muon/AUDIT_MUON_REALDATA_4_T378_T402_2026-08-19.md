# Audit — real-data muon tests, batch 4 (T378, T383, T387, T402)

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** the only independent-source COHERENT replication, the 7.5-turn antecedent,
the return-wave discovery T388 later resolved, and the T401 predecessor.

---

## 1. T402 — whole-shape child relation

**Reported:** `NO STABLE WHOLE SHAPE`; but a narrower relation replicated —
*"C is enriched below the local ARA ridge and depleted above it, with a continuous
handover close to the ridge."*

### 1.1 The differences sum to zero, so the sign change is mathematically guaranteed

```
local child ARA   0.125    0.375    0.625    0.875    1.125    1.375    1.625    1.875
mean C − AC      -0.00581 +0.02661 +0.02463 +0.00722 -0.00432 -0.00583 -0.01036 -0.03215

                                                                  SUM = −0.00001
```

Both distributions are normalised over the window, so `C − AC` integrates to zero. **A
sign change must therefore exist somewhere in the window.** Its existence is not a
finding; only its location could be.

### 1.2 And the location is where a decaying distribution crosses a flat one

`C` is beam-coincident — real neutrino events, following the delayed muon-decay
exponential. `AC` is anticoincident — accidentals, flat in time.

So `C − AC` is **exponential minus uniform, both normalised**. That function is
necessarily positive early, negative late, and crosses zero near the middle of the
window. The ARA coordinate places `1.0` at the middle of the window by construction.

Hence:

```
observed positive crest      0.50–0.57      exponential excess, early
observed crossing            0.94–1.05      where exponential meets its own mean level
observed deficit             1.88–1.91      exponential deficit, late
```

Every one of those is what signal-versus-accidental produces on any time-monotone
coordinate. **The "stable source-specific axis with a handover close to the ridge" is the
time-shape difference between neutrino events and accidentals.**

### 1.3 What the replication actually establishes

The replication statistics are sound — `326/400` valid transfers, `73.62%` of partitions
in both directions, all four KDE bandwidths inside their registered windows. They
establish that the effect is **real and stable**, which it is: signal and background
genuinely have different time distributions, reliably, in every partition.

They do not establish that the ridge is a meaningful location for it.

**Required:** restate as *"C and AC differ in time-shape as expected for exponential
signal against flat accidentals; the sign change is forced by normalisation and its
position tracks the window midpoint."* The `NO STABLE WHOLE SHAPE` primary verdict is
correct and should stay.

**Cheap decisive check:** repeat with `AC` replaced by a *simulated* flat background and
by a simulated exponential of the same lifetime. If the axis survives against the
simulated exponential, something beyond time-shape is present. If it only survives
against flat, it is signal-versus-accidental.

---

## 2. T378 — independent COHERENT 2017 holdout

**Reported:** strong near-replication; `2/8` predeclared gates missed.

### 2.1 This is the only genuinely independent-source replication in the series

T371 used the 2022 release; T378 uses the 2017 release under DOI
`10.5281/zenodo.1228631` — a separate exposure with the same source architecture. SHA-256
recorded for all eleven source files, independent validation reproduced grids, counts,
templates, fit, handover and gate verdicts with zero failures.

**And it partially failed.** That is more informative than a pass, and calling it a
near-replication rather than a replication is the correct handling.

### 2.2 The signal fraction should travel with the branch numbers

```
beam-on coincidence counts        547
fitted steady background          416.247        76.1% of the window
beam-off coincidence              209
```

Roughly three-quarters of the beam-on coincidence window is fitted background. The
neutrino branches are extracted from the remaining ~24%, which is why the bootstrap
intervals downstream (T371: prompt `[32.42, 89.20]`) are as wide as they are.

Anywhere T378's or T371's branch values propagate into a landmark — T398, T399, T400 —
that signal fraction is the reason the landmark cannot be tightly located.

---

## 3. T383 — 7.5 child cycles before the parent pole

### 3.1 The post-hoc handling is exemplary and should be the template

> The observation was made after T382 outcome inspection and **cannot confirm itself.**

Then:

- two separable hypotheses declared — **H1** literal count invariance, **H2** fractional
  phase locking — so a partial result cannot be reported as a whole one;
- the common parent coordinate `xP_star = 1.9608580375` **frozen before** calculating the
  comparison-field phases.

That is the correct way to handle a visual noticing: label it, split it, freeze the shared
coordinate before comparison. It is the same discipline T409 later applied to the marked
upper ridge.

### 3.2 But the object under test had already failed qualification

T382's verdict was `PARENT_RECOVERED_96_DETECTOR_CHILD_NOT_QUALIFIED`. The "candidate
child" whose cycles T383 counts is the object that failed C03–C05 in the parent test.

The session record states the consequence: *"The candidate child had already failed
qualification, so the test could not establish neutrino timing in any case."* Correct —
and it means T383 was uninformative before it ran.

### 3.3 7.5 turns has now been killed three times

T382 (child not qualified) → T383 (both H1 and H2 rejected) → T390 (all five gates
failed, ranked 7th of 8 landmarks). A claim tested three times on progressively better
controls and rejected each time. It should be listed in `CLAIMS_STATUS.md` under
permanently failed claims that cannot be relabelled, alongside the fixed-φ entries.

---

## 4. T387 — full-pulse return wave

**Reported:** `NON-MIRRORED TWO-AXIS RETURN`; 3 of 4 gates passed; timing
`MIXED / UNDETERMINED`.

### 4.1 Every passing quantity is window-dependent, and the dependence is the instrument

```
window        64 ns      128 ns     256 ns
x_R at min    1.89124    1.84914    1.79912
x_H maximum   1.96226    1.57335    1.07247
trough time   128 ns     256 ns     464 ns
```

**Trough time ≈ 2 × window**, across all three. That is the signature of comparing
adjacent RMS windows: activity enters the current window and then sits in the previous
one. The report says so directly:

> An `x_R` expansion followed by contraction is partly expected from comparing adjacent
> RMS windows.

More seriously, `x_H` maximum falls from `1.96` to `1.07` as the window grows. The gate
*"`x_H` crosses the ridge and returns"* passes at `1.07` at 256 ns — barely. So the
strongest structural gate is marginal at the largest window and its margin is set by
window choice, not by the data.

### 4.2 T388 then settled it, which is the right sequence

T387 exposed the loop; T388 tested whether it reverses or repeats, and found direct
repetition at `100%` handedness retention with identical medians. So the honest joint
reading is: **T387 measured the analysis window's response; T388 identified it.** Two
tests, one artefact, correctly resolved.

The post-result extrema note (`peak + trough − 2` residuals of `+0.01958`, `+0.00133`,
`+0.00381`) is flagged exploratory and does not replace the failed frozen mirror gate.
Correct.

---

## 5. Cross-cutting

**5.1 — Normalisation forcing, second instance.** T402's sign change is guaranteed by
`Σ(C−AC) = 0`, exactly as T395's support gain was guaranteed by `C ≡ 2x_νe/N`. Standing
Rule 7 covers forced *closure*; it should be extended to cover **forced sign changes and
forced correlations** arising from normalisation, which are the same defect wearing a
different hat.

**5.2 — Two instrument-generated features identified in one batch.** T387's window-scaled
trough and T402's exponential-versus-flat axis. Both were caught in the reports' own
interpretation sections, and in both cases the verdict line is stronger than the caveat.
Same reporting-layer pattern as batch 1.

**5.3 — Signal fraction as a standing disclosure.** T378 shows 76% background in the
beam-on window. That number should accompany every COHERENT-derived landmark in the
series, because it bounds how precisely any of them can be located.

**5.4 — Positive.** T383's post-hoc handling is the best example of that discipline in
the repository. T378 reports a partial failure on the only independent-source replication
available. T402 fails its own primary gate and says so first. T387 flags its own
instrumental explanation before the outcome favoured it.

---

## Required corrections

1. **T402:** restate the axis as signal-versus-accidental time-shape; note the forced sign
   change; run the simulated-background check.
2. **T378:** attach the 76% background fraction to the branch numbers wherever they
   propagate.
3. **T383:** record that the tested child had already failed T382 qualification.
4. **7.5 turns:** list in `CLAIMS_STATUS.md` as permanently failed after three tests.
5. **T387:** state that the trough time scales with the analysis window and that `x_H`'s
   ridge crossing is window-dependent.
6. **Series:** extend Rule 7 to forced sign changes and forced correlations from
   normalisation.

---

**Remaining after this batch: 9 tests** — T307, T369, T369B, T370, T374, T376, T377, T384,
T386 — plus the two partials (T305 full, T404/T405 primary).

**Note:** `T377_GE_MINI_HANDOVER_REPLICATION_PROTOCOL_2026-08-14.md` exists with no
corresponding report or findings file. Either the run is outstanding or its output is
stored elsewhere; worth resolving so the series has no unaccounted frozen protocol.
