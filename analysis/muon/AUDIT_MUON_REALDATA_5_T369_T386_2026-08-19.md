# Audit — real-data muon tests, batch 5 (T369, T374, T376, T386)

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** the capture-closure parent test, the liquid-argon axis audit that
underpins T375, the solid-scintillator event-linked test, and the coupled Di-ARA.

---

## 1. T374 + T375 — axis choice dominates the landmark

This is the most consequential finding of the batch, and it emerges only from reading the
two together.

### 1.1 On identical events, the recovered handover spans most of the diameter

```
same 3,752 CENNS-10 events, different retained axes:

full three-dimensional record        x_H = 1.23883
energy + arrival time                x_H = 1.35817
pulse shape + arrival time           runs to the 2.0 boundary
                                     1.25 inside 95% by ΔNLL 1.91264 vs limit 1.92073
time alone                           runs to 2.0
no arrival time                      nearly flat — "do not locate it"
```

**Frozen verdict: `LIQUID-PARENT 1.25 LEAD NOT AXIS-CONSISTENT`.** Correct, and the
pulse-shape+time margin is worth stating plainly: `1.25` sits inside the 95% profile by
`0.008` NLL units. That is the definition of barely.

### 1.2 T375's convergence is within one axis choice

T375 then ran the energy-resolution ladder on the full 3-D record and found movement of
`0.72` settling near `1.239`. That is a real within-axis result about resolution.

But **between-axis variation on the same events is larger than the within-axis
convergence**, and spans from `1.24` to the `2.0` boundary. So the landmark is not located
by the data — it is located by which axes are retained.

Both reports are honestly labelled (T374 says not axis-consistent; T375's evidence class
says "internal same-event mechanism test"). The problem is that a reader meeting T375
alone will take `1.239 → 1.25` as a located value, when T374 has already shown it isn't.

**Required:** T375 must carry T374's axis-inconsistency verdict inline, the way T371
carries T372's correction. They concern the same events and the same number.

### 1.3 What T374 establishes positively

> the native prompt-to-delayed order passed every shifted-order control

The *ordering* of the two branches is robust to axis choice; only its ARA *coordinate* is
not. That distinction is clean and worth keeping.

---

## 2. Coupling loses to its own best component — third and fourth instances

### 2.1 T369

```
joint prompt-time × prompt-energy Di-ARA address     +2.8823%
prompt energy alone                                 +2.8962%    ← wins
```

> The observed added signal is therefore energy-led; this test did not recover a
> two-coordinate timing-energy mixing advantage.

### 2.2 T386

```
                    validation AUC    evaluation AUC
raw MG (baseline)      0.741865         0.741824      ← beats everything
determinacy MD         0.734674         0.735617
state MS               0.712320         0.710783
additive MC0           0.712004         0.710251
coupled MC             0.711774         0.710197      ← lowest

gate: coupled_logloss_beats_each_component_both_splits    FAIL
gate: auc_gain_at_least_0p02_vs_raw_both_splits           FAIL
gate: evaluation_bootstrap_above_zero                     FAIL
```

The **raw baseline outranks the coupled model by 0.032 AUC on both splits**, and the
coupled model is last of five. It wins only on log loss (`0.6324` vs `0.6409`) — better
calibrated, worse at ranking, which is the signature of a model fitting the marginal
distribution without adding discriminative information. Same pattern as T385.

### 2.3 The pattern is now consistent across four independent tests

```
T369   energy alone        >  joint time×energy address
T386   raw baseline        >  coupled Di-ARA        (and MS > MC on both splits)
T396   additive fusion     >  joint Information³
T385   raw features        >  ARA features on AUROC
```

Four data classes — capture archive, liquid-scintillator waveforms, V−A truth events,
BUAP waveforms. **Every time a coupled or joint ARA construction is scored against its own
best single component, the simpler object wins or ties.**

This is adverse to the Information³ interaction claim specifically, and it is now
sufficiently replicated to be reported as a series-level result rather than four separate
disappointments. The framework's two-identities-plus-relation structure has repeatedly
failed to beat two-identities-added.

**Required:** state this at series level in `CLAIMS_STATUS.md`, with the four instances
named.

### 2.4 T386's time-reversal parity is separately damning

```
forward coupled MC evaluation AUC     0.710197
time-reversed fixed-model AUC         0.712179     ← slightly better
```

For a coordinate claimed to carry directional temporal relation, reversal should degrade
performance. It does not — it is marginally *better*. That is a strong negative on the
temporal-direction content and it deserves more prominence than a line in the coupling
checks.

---

## 3. T369 — capture daughter closure

**Reported:** `COMMON-PARENT RECOVERED; PARTIAL ADDED RELATION; FULL CLOSURE NOT SUPPORTED`

```
capture-enriched holdout rows            354,273
prompt-present neutron rate               20.439%
prompt-absent neutron rate                 7.096%     enrichment 2.881×
cross-entropy improvement                 +1.7577%    CI [+1.6214%, +1.8853%]
```

### 3.1 The parent recovery is μ⁻ capture physics, correctly used as a validity check

`μ⁻ + N → ν_μ + N'*` leaves an excited nucleus that emits prompt gammas and delayed
neutrons. So prompt-gamma presence tags capture events, which produce neutrons; absence
tags decay events, which do not. The `2.881×` enrichment is that tag working.

The report frames it correctly — *"This is expected physics and validates the cut"* — and
explicitly refuses to let it rescue the deeper claim: *"recovering the known relation
cannot rescue a failed deeper claim."* That is the right structure.

### 3.2 Same mechanism as T369C, used correctly here and overstated there

T369 calls this relation a validity check. T369C, on the same physics, carries the verdict
line `ANTI-DIRECTED ENERGY/CONNECTION BRANCH SUPPORTED`. The two should be reconciled —
the mechanism is identical and T369's framing is the accurate one.

---

## 4. T376 — event-linked solid scintillator

**Reported:** individual prediction not supported; population landmark a "small unresolved
preference for `x = 0.50`".

### 4.1 Four landmarks were predeclared, so "largest of four" is a 1-in-4 outcome

```
frozen candidate coordinates:  0.50, 0.75, 0.25, 1.25
observed at 0.50:              1.0389× expectation, largest of the four
binomial interval:             includes the null
```

With four predeclared windows, one being largest is expected by construction. Combined
with an interval covering the null, this carries no evidential weight — and the report
says so, calling it "a **hint**, not a confirmed landmark." Correct.

Worth noting for the record: this is the same four-landmark family (`0.25`, `0.50`,
`0.75`, `1.25`) that recurs throughout the series. When several are live simultaneously,
a hit on one needs the multiplicity stated.

### 4.2 The ARA cut made individual prediction worse

```
held-out exponential NLL change from adding ARA     +0.001836 per event (worse)
run-block 95% interval                              [−0.003495, +0.000167]
```

"Mostly on the wrong side and crossing zero only slightly." That is the **fifth**
independent individual-timing negative (T368, T376, T379, T380, T407/T408), and under the
memorylessness finding it is the expected outcome.

### 4.3 Good identity discipline

Two January files were rejected before extraction because the lower-counter stream was
absent — *"Including them would have changed the measured detector identity inside the
test."* Rejecting data before extraction, on identity grounds rather than outcome grounds,
is the correct order.

---

## 5. Cross-cutting

**5.1 — Coupled loses to component, four times.** See §2.3. This should now be a
series-level statement.

**5.2 — Axis choice dominates the liquid-argon landmark.** T374 and T375 must travel
together.

**5.3 — T386's leakage audit is a model practice.**

```
forbidden acquisition leakage AUC     0.999978  (audit only)
```

Quantifying what the forbidden channel *would* have given — essentially perfect prediction
— demonstrates the guard is load-bearing rather than decorative. Every test with a
pre-outcome guard should report this number. Few analyses anywhere do.

**5.4 — Positive.** T369 refuses to let a recovered known relation rescue the deeper
claim. T374 fails its own primary gate on the number the programme was pursuing. T376
calls a 1-in-4 outcome a hint. T386 reports its raw baseline beating its own coupled
model, and its time-reversed control matching forward performance. This batch reports
adverse results against interest at every opportunity.

---

## Required corrections

1. **T375:** carry T374's axis-inconsistency verdict inline.
2. **Series:** report the coupled-loses-to-component pattern at `CLAIMS_STATUS.md` level,
   naming T369, T385, T386, T396.
3. **T386:** promote the time-reversal parity from the coupling checks to the outcome.
4. **T369C:** reconcile its verdict line with T369's accurate framing of the same physics.
5. **T376:** state the four-landmark multiplicity beside the `0.50` result.
6. **Series:** require the forbidden-channel AUC wherever a pre-outcome guard is used.

---

**Remaining after this batch: 5 tests** — T307, T369B, T370, T377, T384 — plus the two
partials (T305 full, T404/T405 primary). T377 still has a frozen protocol with no
corresponding report.
