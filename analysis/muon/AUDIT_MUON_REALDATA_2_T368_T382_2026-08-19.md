# Audit — real-data muon tests, batch 2 (T368, T370/T370B, T371, T382)

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** the foundational real-data arc — first individual-timing test, the
resolution-boundary precedent, the COHERENT lineage, and the RAL Silver source that
T397 later reuses.
**Methodology:** per `AUDIT_CORRECTION_METHODOLOGY_2026-08-19.md`.

---

## 1. T368 — muon decay handover information test

**Reported:** `NO OBSERVABLE PREFORMATION IN THE RELEASED VARIABLES`, G3 FAILED.

```
holdout decays            325,185
cross-entropy change      +0.022837%   CI [+0.017127%, +0.027862%]
Cramér's V                 0.000038
Spearman ρ                 0.006513
permutation exceedances    0/1000
```

### 1.1 This null was required by the exponential decay law

Muon decay is **memoryless**. That is the defining property of an exponential lifetime:

```
P(decay in [t, t+dt] | survived to t)  =  constant, independent of t
```

The waiting time therefore carries **no** information about the decay products, and
cannot, at any sample size. T368 tested whether the open-interval duration predicts
daughter momentum class. The answer is fixed by one of the most precisely verified laws
in physics — the muon lifetime is known to `2.1969811(22) μs`, ten significant figures'
worth of exponential behaviour.

The report's framing — "no observable preformation **in the released variables**" —
hedges to the observables, when the stronger and more useful statement is available:
**preformation of this kind is excluded by the decay law, not merely unobserved in this
archive.**

### 1.2 This reframes roughly eight downstream tests

T376, T379, T380, T407, T408 and T409's travelling-ridge hypothesis all search for
advance individual timing information. Every one returned null. Those are not eight
independent data limitations — they are **one law, tested eight times**.

`CLAIMS_STATUS.md` currently describes the barrier as archival:

> no current input event-links an individual spinning muon to its charged daughter and
> both neutrinos

That is true and it is not the binding constraint. Even a perfect archive would return
null on the timing question, because the quantity being sought does not exist in standard
quantum mechanics.

**Two fences, stated fairly:**

- Memorylessness applies to decay **time**. It does not forbid spin-orientation →
  daughter-direction correlations, which are real (parity violation) and which T397
  correctly recovered. The framework's orientation results are untouched.
- A hidden-variable account with internal pre-decay state is not excluded by *these
  data*. It is excluded by standard QM, and any such proposal carries a hard constraint:
  it must reproduce the exponential law exactly, at the precision to which it is known.

### 1.3 Note on the significance framing

The effect is statistically detectable (`0/1000` permutations, CI excluding zero) and
physically nil: Cramér's V of `0.000038` sits four orders of magnitude below the
conventional "negligible" threshold of `0.1`. At `n = 325,185` almost any nonzero
association reaches significance. "`0/1000` permutation exceedances" reads as a positive
finding and should be presented beside the effect size.

**Required:** restate the verdict to say the null is *predicted* by memorylessness; add
a series-level note that the individual-timing thread is in tension with the exponential
law and that reproducing it is a constraint on any ARA account.

---

## 2. T370 / T370B — polarized-muon phase lineage

**Reported:** `NOT SUPPORTED` — 520 G collapsed at the frozen 64 ns resolution.

### 2.1 Class C handling, executed correctly

```
13 runs excluding 520 G     rank 0.9986, slope 0.159% from the independent muon value
520 G at frozen 64 ns       collapsed → all-run rank and slope gates broken
520 G at 32 ns (post-hoc)   7.060 MHz vs 7.048 MHz expected, all four baselines passed
```

> This diagnoses the frozen failure as a resolution boundary, but it does not
> retroactively change the registered verdict.

Textbook Class C: implementation/resolution failure, diagnosis recorded, verdict retained.

### 2.2 The physics recovered is Larmor precession, and the agreement is a good instrument check

`ω = γB`. Recovering the cadence-versus-field slope to `0.159%` of the independently
known muon value is a competent validity check on the whole pipeline. The report's
side-by-side table already states this correctly ("Parent Phase A ↔ Phase B circle |
Precessing polarized muon spin").

### 2.3 A dependency worth flagging

```
run          field    corr    resolved gate
EMU00066651   20 G    0.974   PASS      holdout gain +77.39%
EMU00066652   25 G    0.480   FAIL      holdout gain +12.16%
others        40–     ~0.45–0.64  PASS  gains +10–23%
```

Two things follow:

1. **One run dominates.** The 20 G acquisition has correlation `0.974` and gain `+77%`;
   everything else sits near `0.5` and `+10–20%`. The pooled impression is carried by a
   single run.
2. **The 25 G run failed its own resolved-parent gate** — and T389/T391 later learn their
   detector basis from "the calibration-frozen **20/25 G**" runs. So half the calibration
   basis for the spin anti-phase work failed resolution qualification here.

**Required:** cross-reference this in T389/T391. It does not invalidate them — the basis
is used for spatial decoding, not cadence — but a reader tracing dependencies will find
it and it should not be a surprise.

---

## 3. T371 — COHERENT stopped-pion → muon Di-ARA

**Reported:** `TWO-STAGE DI-ARA HANDOVER RECOVERED`, all six gates passed.

### 3.1 The strongest number is the total-recoil agreement

```
T371 compact reconstruction     319.12 fitted CEvNS recoils
COHERENT published full fit     306 ± 20
```

Within one sigma of an independent collaboration analysis, from a compact reconstruction
that does not attempt their systematics. **That is the result** — it validates the
pipeline against a published number, which is the best kind of instrument check
available.

The two-stage prompt/delayed ordering is COHERENT's design principle and recovering it
confirms the archive was read correctly.

### 3.2 The branch intervals are wide and should travel with the point estimates

```
prompt ν_μ      60.18    [32.42, 89.20]     factor 2.75 across the interval
delayed         258.94   [187.92, 333.30]   factor 1.77
```

These are used downstream (T398, T400) as if reasonably determined. The prompt
normalisation in particular is uncertain by nearly a factor of three, and T372's gradient
result shows the handover coordinate depends directly on the prompt/delayed weight ratio.
That uncertainty should propagate into every landmark derived from the fit.

### 3.3 Good practice: the correction travels with the original

T371 carries T372's native-resolution correction inline, including the corrected
`0.636 μs` / `0.437` and the wide `[0.179, 0.692]` interval. A reader who finds T371
first cannot miss the correction. That should be the pattern everywhere.

---

## 4. T382 — RAL Silver ARA-native handover

**Reported:** `PARENT_RECOVERED_96_DETECTOR_CHILD_NOT_QUALIFIED`.

### 4.1 The child failure is clean and consequential

```
C01/C02  detector-summed parent            PASS
C03–C05  96-detector traversal child       FAIL
C06      child pole at parent ridge        not admissible after child failure
C16      individual advance prediction     UNAVAILABLE
```

Correctly recorded, and it is the reason T397 later had to re-approach the same source
with a different construction. The failure is load-bearing and was not quietly dropped.

### 4.2 The fitted lifetime is 0.19% below the known value, and the interval excludes it

This is the significant finding of this batch.

```
T382 fitted τ_P          2.192800 μs
bootstrap 95% interval   [2.192300, 2.193300]     half-width 0.0005 μs
PDG muon lifetime        2.1969811(22) μs
offset                   −0.0041811 μs  =  −0.190%
offset in interval half-widths            8.4×
```

RAL Silver μSR uses **positive** muons, which do not undergo nuclear capture, so the
expected lifetime is the free value. The fit sits `8.4` interval half-widths below it.

A `0.19%` low bias on a lifetime is readily produced by an unsubtracted flat background,
a truncated fit window, or deadtime — all ordinary and all systematic. The point is not
that the fit is wrong; it is that **the quoted interval is statistical-only and
underestimates the true uncertainty by at least an order of magnitude.**

### 4.3 The second constant shows the same pattern

```
calibration-only γ̂        0.013820000 MHz/G
revealed reference        0.013553896 MHz/G
relative difference       +1.963%
```

Two independently fitted physical constants in one test, both biased outside their
quoted precision, in a source where the true values are known. That is a clean, internal
calibration of how far systematic error exceeds statistical error in this pipeline.

**This is usable rather than merely critical.** It gives a measured floor: intervals of
this construction should be widened by roughly an order of magnitude before any landmark
comparison, and no landmark separated from another by less than ~1–2% should be treated
as discriminated.

That directly bears on T373's `1.25` versus `1.238725` (`0.902%` apart), T392's `0.49019`
versus `0.5` (`1.96%`), and T393's `0.245095` versus `0.25` (`1.96%`) — all inside the
systematic band this test exposes.

---

## 5. Cross-cutting

**5.1 — The individual-timing thread conflicts with a law, not with an archive.** T368's
null is the exponential decay law asserting itself, and eight downstream nulls follow
from the same source. This should be stated once at series level rather than reappearing
as an archival limitation.

**5.2 — Quoted intervals are statistical-only and demonstrably too narrow.** T382 supplies
two measured instances against known constants (`0.19%` and `1.96%` biases, both outside
interval). Every landmark comparison in the series closer than ~2% falls inside that band.

**5.3 — Single-run dominance.** T370B's pooled impression rests on the 20 G acquisition;
T382's parent passes on a fit whose systematic exceeds its interval. Per-run and
per-component breakdowns should accompany pooled statistics.

**5.4 — Positive.** T368 is a well-powered, correctly-called null on a foundational
question. T370B retains a failure it could have re-specified away. T371 validates against
a published collaboration number and carries its own correction inline. T382 records a
child failure that constrained all later work on that source. This batch contains no
overstatement that survives into a verdict line — the reporting-layer problem flagged in
batch 1 is largely absent here.

---

## Required corrections

1. **T368:** restate the null as predicted by memorylessness; add the series-level note.
2. **T368:** present Cramér's V beside the permutation result.
3. **T370B:** cross-reference the 25 G resolution failure into T389/T391's calibration basis.
4. **T371:** propagate the prompt/delayed interval widths into downstream landmark claims.
5. **T382:** record the `τ_P` and `γ̂` biases as a measured systematic floor for the series.
6. **Series:** adopt a ~2% discrimination floor for landmark comparisons until a
   systematic budget is built.

---

**Remaining after this batch: 19 tests** (T307, T369, T369B, T370, T374–T380, T383–T387,
T402) plus the two partials (T305 full, T404/T405 primary).
