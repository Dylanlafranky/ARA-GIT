# Audit — real-data muon tests, final batch (T307, T369B, T370, T377, T384)

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Status:** completes coverage of the muon series.

---

## 1. T370 — the control itself separates resolved from unresolved

**Reported:** `SUPPORTED AS A CROSSWALK` — passed every primary gate in 3 of 4
acquisitions (required 3 of 4). Superseded by T370B's audit, noted at the head of the
file.

### 1.1 Three "passing" runs report an identical fitted frequency

```
run           setting              f (/µs)
EMU00066666   F=1600               0.200
EMU00066667   F=2200               0.200
EMU00066668   F=3000               0.200
EMU00066669   F=230                3.120
```

Three different acquisition settings returning **exactly** `0.200 /µs` is the signature of
a fit pinning to a low-frequency envelope rather than resolving a precession. A resolved
measurement varies with the setting; these do not.

### 1.2 And the wrong-orientation control ties the real one in exactly those runs

```
run       ARA RMSE    wrong orientation    separation
1         0.03052     0.03050              wrong is BETTER
2         0.03149     0.03153              tie
3         0.02578     0.02585              tie
4 (230)   0.03501     0.04048              real separation, 15.6%
```

**In the three unresolved acquisitions the deliberately wrong orientation performs
identically to the correct one.** Only in the 230 G run — the one T370B independently
identified as physically resolved — does orientation matter at all.

The data therefore confirms T370B's diagnosis from inside the frozen table, without
needing the resampling audit. That is a strong internal consistency result, and it means
the honest count is **1 of 4 acquisitions resolved, and that one passed** — not 3 of 4.

### 1.3 Handling

The superseding note is placed at the top of the file, which is correct. But the verdict
line still reads "passed every primary gate in **3 of 4**," and that sentence will be
quoted without the header. The wrong-orientation tie should be stated in the same
paragraph as the verdict, because it is the cheapest available demonstration that three
of those passes are empty.

**Required:** amend the verdict line to "1 of 4 physically resolved; that acquisition
passed"; cite the wrong-orientation tie as the internal evidence.

---

## 2. T307 — the lineage control did not bite

**Reported:** `COORDINATE RECOVERED WITHOUT FULL PREDICTIVE SUPPORT`; G2–G4 fail;
independent validation `8/8`.

### 2.1 Two failures of different severity

```
quadrant state beat persistence, one global complex ratio,
and all 1,000 temporal-shuffle controls                          PASS

generic affine AR(2) predicted the next complex state better
in all three families                                            FAIL

breaking the same-prefix lineage did not consistently damage
the quadrant predictor                                           FAIL  ← the serious one
```

The AR(2) result is the **fifth** instance of a generic or simpler model beating the ARA
construction (with T369, T385, T386, T396). But the lineage failure is worse in kind:

**A predictor of a relation that survives breaking the relation is not measuring the
relation.** The wrong-lineage control exists precisely to catch structure that is generic
rather than relational, and here it did not bite. That should be stated as the primary
negative rather than sitting third in a list.

### 2.2 The post-hoc clue is correctly quarantined

> the observed breathing was consistently closer to `1/φ ↔ φ` than to the proposed
> asymmetric `1/e ↔ Φ` radial pair. That clue is promising enough for a fresh test, but it
> is post-hoc and cannot change the frozen verdict.

Correct. Note also that the *primary* pair — Phi-Time against `1/e` — "was not the most
predictive tested pair," which is a direct negative on the registered hypothesis.

---

## 3. T369B — the data marginally favours the opposite of the prediction

**Reported:** `NO ORIENTED TIMING RELATION`, post-result diagnostic.

```
both-child rows                    4,096
same-phase effect                 +3.3386%     shuffle exceedances  93/1000
anti-phase effect                 +1.1414%     shuffle exceedances 838/1000
rank correlation                  +0.017702
```

The framework predicts **anti-phase** (`x_N ≈ 2 − x_G`). The anti-phase reading is
exceeded by `838` of `1,000` shuffles — it performs *worse than a typical shuffle*. The
same-phase reading is marginally better (`p ≈ 0.093`) and still not significant, with a
rank correlation of `0.018`.

So the registered orientation fails and the opposite orientation is weakly, non-
significantly preferred. Correctly called, and correctly labelled post-result diagnostic
rather than confirmation.

**Worth adding:** the shuffle test retained neutron multiplicity during shuffling, which
is the right control construction — it prevents the multiplicity distribution from
carrying the result.

---

## 4. T377 — an incomplete test in the record

```
present:  T377_GE_MINI_HANDOVER_REPLICATION_PROTOCOL_2026-08-14.md
          T377_ge_mini_handover/T377_results.json
          T377_timing_projection.csv, T377_on_count_grid.csv, T377_off_count_grid.csv
missing:  any report or findings document
```

### 4.1 The results explain why, and the verdict should be written

```
background-subtracted counts per 2 µs (on-projection):
  3.47, −3.53, 0.47, 8.47, 4.47, 3.47, 2.47, 4.47, −0.53, −0.53, −0.53,
  2.47, 1.47, −1.53, −3.53, −3.53, 1.47, 0.47, −1.53
sigma ≈ 3.5
```

Single-digit counts against `σ ≈ 3.5`. The largest bin is `8.47`, about `2.4σ`; several
bins are negative. **Most bins are consistent with zero.** This is an insufficient-
statistics outcome, and it is a legitimate result — the COHERENT Ge-Mini exposure is far
smaller than CsI.

Source discipline is good (SHA-256 on the tarball and all three figure PDFs, explicit
vector-calibration constants for the digitisation).

**Required:** write and file the verdict — *"independent Ge-Mini replication attempted;
insufficient statistics to resolve the prompt/delayed branches"* — so no frozen protocol
in the series is left without a written outcome. An unresolved protocol is more damaging
to the record than a null.

### 4.2 Same gap appears for T384

`T384_IRRATIONALITY_INFORMATION_LOCK_PROTOCOL_2026-08-15.md` has no corresponding report
or findings file either. Per the 16 August session record, T384's outcome was: *only child
readability passed; navigation, wrong-relation discrimination, recursive restoration and
added-information gates failed* — 1 of 5. **Audit note: this is cited from the session
record, not from a primary T384 document, because none exists.** It should be written up.

---

## 5. Series-level close

With this batch the muon series is fully audited: **47 tests across T305–T409**, plus the
master protocol T381.

### 5.1 The six patterns that recur

| Pattern | Instances |
|---|---|
| Simpler or generic model beats the ARA construction | T307 (AR(2)), T369 (energy), T385, T386 (raw baseline), T396 (additive) |
| Individual-timing null, predicted by memorylessness | T368, T376, T379, T380, T407, T408, T409 |
| Result forced by normalisation or definition | T393, T395 (support), T402 (sign change), T405 (`ρ = 1.000`) |
| Instrument generates or bounds the signal | T369C (mixture), T370 (unresolved fit), T372 (bin centres), T387 (window), T388 (digitizer), T391 (sampling), T402 (accidentals) |
| Landmark inside the systematic floor | T373 (0.90%), T375 (0.89%), T392/T393 (1.96%) |
| Verdict line stronger than the body's own caveat | T369C, T372, T375, T389/T391, T370 |

### 5.2 What the series established

**Positively:** the coordinate reads real detector archives correctly (T371's `319.12` vs
COHERENT's published `306 ± 20`; T370B's Larmor slope within `0.159%`), and the programme
reliably recovers known structure when it is present.

**Negatively, and this is the substantive scientific content:** the individual pre-decay
timing claim failed seven times, and the failure is explained by the exponential law
rather than by the archives. The Information³ *interaction* claim failed five times
against simpler constructions. `7.5` turns failed three times. Those are real, replicated,
informative negatives.

### 5.3 What I would change about the reporting, in one sentence

The correct statement is present in the body of nearly every report; the defect is that
verdict lines and headlines consistently overstate it, and a reader who stops at the
verdict gets a different impression from a reader who reaches the caveat.

---

## Required corrections

1. **T370:** amend the verdict to 1-of-4 resolved; cite the wrong-orientation tie.
2. **T307:** promote the lineage-control failure to the primary negative.
3. **T377:** write and file the insufficient-statistics verdict.
4. **T384:** write and file the 1-of-5 outcome from the session record.
5. **Series:** adopt §5.1 as a standing self-check list before freezing any new protocol.
