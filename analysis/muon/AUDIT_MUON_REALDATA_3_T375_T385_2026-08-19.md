# Audit — real-data muon tests, batch 3 (T375, T379, T380, T385)

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** the liquid-argon resolution ladder, the QuarkNet archive that T408/T409
later reuse, the same-scale child cut, and the BUAP waveform test.
**Methodology:** per `AUDIT_CORRECTION_METHODOLOGY_2026-08-19.md`. Systematic floor from
batch 2 §4 applied throughout.

---

## 1. T375 — liquid-argon nested energy placement

**Reported:** `PROGRESSIVE ENERGY-PLACEMENT MECHANISM SUPPORTED`, `ρ = −1.000`.

```
energy groups        1        2        3        5        12
recovered handover   1.99893  1.73393  1.27726  1.22397  1.23883
distance from 1.25   0.74893  0.48393  0.02726  0.02603  0.01117
```

### 1.1 The target is framework-derived, but the derivation was performed post-observation

**Correction to an earlier draft of this audit.** I described `1.25` as "chosen." That is
wrong. `1.25` is derivable from rules that predate the muon programme, and T373 gives the
chain explicitly:

```
half-weight child rule (April-dated)          child contributes 0.5 at the parent rung
project one further rung                      0.5 / 2 = 0.25          grandchild
liquid = movement-heavy parent, so the         1 + 0.25 = 1.25        far side of ridge
retained child expresses across the ridge
```

Each step invokes a stated framework rule tied to the declared identity, not a free pick
from a grid. The author's reading — `0.25` as the connection-side child landmark and
`1.25` as its time-side grandchild expression, forming a paired pole — is a coherent
geometric statement, not a number fitted to data.

**What remains true** is that this derivation was constructed *after* the value was seen.
T373 records it:

> Dylan identified `1.25` after seeing `1.238725`.
> T373 therefore cannot confirm the liquid quarter-above-ridge rule.

So the correct status is: the framework can reach `1.2387` by a principled chain. It has
not been shown to have *predicted* it. That is the author's own recorded position, and it
is the right one.

**Consequence for T375's correlation.** With the 1-group and 12-group endpoints already
known, `ρ = −1.000` against distance from a target near the terminal value is close to
structurally forced regardless of how the target was derived. The intermediate 2/3/5
values being frozen constrains the path, not the destination. This point is about the
statistic, not about the landmark's provenance, and it stands.

Under those conditions `ρ = −1.000` is close to forced. Any monotone convergent sequence
running from a known start to a known end will correlate perfectly with distance from a
target placed near that end. The intermediate 2/3/5-group values being frozen in advance
constrains the *path*, not the *destination*.

### 1.2 Convergence completes at three groups; the rest is inside the noise

```
1 → 3 groups     1.99893 → 1.27726     movement 0.72167
3 → 12 groups    1.27726 → 1.23883     movement 0.03843
                 and non-monotone in value: 1.277 (above) → 1.224 (below) → 1.239 (below)
```

The physical effect is entirely in the first three groups. After that all three estimates
sit within `0.027` of each other and wobble across the target. The "successive
improvement" from `0.02726` to `0.02603` is `0.0012` — noise on a quantity moving by
`0.72` over the full ladder.

The report notices this honestly ("the five-group cut crossed below it... the twelve-group
cut remained below but moved closer again"), but describes it as convergence rather than
as arrival-then-scatter.

### 1.3 Against the measured systematic floor, `1.25` is not discriminated

```
1.25 vs 1.23883      0.89% apart
T382 measured systematic biases      0.19% and 1.96% on known constants
```

`0.89%` sits inside the band batch 2 established. The record cannot separate `1.25` from
the observed `1.2387`, from `1.2240`, or from anything else in that neighbourhood.

**What survives, and it is worth keeping:** recoil-energy resolution *strongly determines*
where the handover is placed — a movement of `0.72` on a `0–2` diameter between the
coarsest and a 3-group reconstruction. That is a real, large, useful instrument finding,
and it retroactively explains T373/T374. It is not support for `1.25`.

**Required:** restate the verdict as support for the *mechanism* (energy resolution places
the handover) with an explicit note that the `1.25` derivation is post-observation, that
convergence completes by three groups, and that the residual separation is inside the
systematic floor.

### 1.4 The paired-pole reading generates a much stronger test than one landmark does

The author's `0.25` / `1.25` pairing — connection-side child against time-side grandchild
— is not merely an interpretation of one number. It implies a **two-medium prediction**:

```
connection-heavy medium (solid CsI)      handover near 0.25
movement-heavy medium (liquid argon)     handover near 1.25
```

That is a far better test than either landmark alone, because it predicts a *contrast*
with a declared direction, and a wrong assignment fails visibly rather than landing
somewhere else on a quarter grid. It is also exactly the solid-versus-liquid comparison
T373 was reaching for before the rung/identity error was caught.

T373 already specifies the prospective form: freeze the identity assignment and the
`0.5 → 0.25 → 1.25` chain, predict the handover, then open an untouched liquid record. The
paired version adds the solid arm and a falsifier — if the media do not separate in the
declared direction, the pairing fails regardless of where either lands.

**This is the highest-value unrun test in the muon series.** It is prospective, it has a
declared direction, it uses a landmark set of two rather than a grid, and both media are
already in hand.

---

## 2. T379 — individual-muon child handover (QuarkNet)

**Reported:** `INDIVIDUAL ADVANCE INFORMATION NOT SUPPORTED`; `x_μ = 0.50` landmark
`NOT SUPPORTED`.

```
raw lines            15,884,080
hardware triggers     4,720,318
clean linked pairs        4,505
```

### 2.1 The reduction and the controls are sound

A `3,500:1` reduction from raw lines to event-linked pairs, with a deliberately wrong
diagonal counter pairing (`MW`) carried as a control and a separately frozen landmark
model (`ML50`). No delayed-electron information enters the coordinate. Correctly called
on both questions.

### 2.2 `x_μ` is a stopping-depth coordinate, and this resolves T409's bands

```
A = q₁ + q₂   (upper pair)          x_μ = 2B / (A + B)
B = q₃ + q₄   (lower pair)          from time-over-threshold
```

Four closely stacked scintillators, upper pair against lower pair. So:

- muon depositing evenly through the stack → `A ≈ B` → `x_μ ≈ 1`
- muon stopping high, more signal upper → `x_μ < 1`
- signal weighted low → `x_μ > 1`

**`x_μ` measures where in the stack the track terminated.** And time-over-threshold is
digitised, so the coordinate is quasi-discrete.

That gives a concrete physical reading of T409's three bands on this same archive:

```
R1  0.761   41% of events    upper-weighted    → stopped higher in the stack
R2  1.041   39% of events    balanced          → through-going or stopped low
R3  1.395    6% of events    strongly lower    → rare topology
```

Two dominant stopping-depth classes plus a sparse tail is exactly what a four-layer stack
produces. This is a sharper version of the combinatorics check I recommended in the
T403–T409 audit, and it is directly testable: **cross-tabulate band membership against
which counters fired.** If R1 and R2 separate by counter-hit pattern, the bands are track
topology.

### 2.3 A dependency worth stating

T408 and T409 re-interrogate the `2,109` holdout records produced here — an archive whose
primary question and frozen landmark both returned NOT SUPPORTED. That is legitimate
(new questions on old data are allowed, and both later tests declare it), but it should be
visible: the source did not pass its own first test.

---

## 3. T380 — same-scale muon child cut

**Reported:** `NOT SUPPORTED AS AN INDIVIDUAL HANDOVER CLOCK`.

```
x_U = 2q₂/(q₁+q₂)        x_L = 2q₄/(q₃+q₄)
median same-scale coupling   0.9527
```

### 3.1 The negative is the strongest form available

```
pooled score           slightly better than parent model
sign across days       REVERSED
uncertainty interval   crosses zero
wrong pairing          scored SLIGHTLY BETTER
permutation control    not cleared
```

**A deliberately broken pairing outperformed the real geometry.** That is the most
decisive negative outcome a geometric claim can receive, and it is reported without
hedging.

The design is also clean: detector, material, source, event linking, calibration/holdout
dates and outcome all held fixed from T379; **only the geometric cut changed.** That is a
proper controlled comparison of two ARA cuts, and it isolates the geometry as the only
variable.

### 3.2 Consistency with T368

This is the fourth independent individual-timing null on this detector family (T376,
T379, T380, plus T407/T408 later). Under the memorylessness finding from batch 2 §1, that
consistency is expected rather than disappointing — the tests are well-built and the
quantity is not there to find.

---

## 4. T385 — BUAP source and reproduction record

**This is the best data-provenance document in the repository and should be the template.**

```
landing page       https://ciiec.buap.mx/Muon-Decay
direct file        .../MD10000Last.csv
retrieved          2026-08-15 (Australia/Brisbane)
Content-Length     53,641,959 bytes
Last-Modified      Tue, 03 Feb 2026 19:27:09 GMT
SHA-256            C2DC1E01...5454CD
rows observed      5,001
```

### 4.1 Three practices worth naming

**Label versus content.** The page advertises 10,000 events; the frozen object contains
`5,001` non-empty rows. The analysis reports what it observed rather than the page label.
Most work silently adopts the label.

**Mutable-endpoint handling.**

> The `MD10000Last.csv` endpoint is mutable; if BUAP updates it, the downloader exits with
> a hash mismatch rather than presenting new events as an exact T385 replication.

This is the correct treatment of a rolling data source and it is rarely done at all.

**Leakage control most people would miss.**

> row length and record end are forbidden because the acquisition buffer reveals the
> second-pulse position

The buffer length encodes the answer. Excluding it before running is a sharp catch.

### 4.2 The result itself is a proper detector-proxy negative

Per the session record: ARA features improved calibration loss but **reduced AUROC**,
failed time reversal, and did not recover the proposed movement landmark.

Improved calibration with degraded ranking is the standard signature of a model that fits
the marginal distribution better while carrying **no additional discriminative
information**. Correctly classified as a detector-proxy result rather than an observed
traversal child.

---

## 5. Cross-cutting

**5.1 — One real problem in this batch, and it is T375.** The `1.25` target was selected
from the endpoint it is measured against, the correlation is structurally near-forced, and
the residual separation lies inside the systematic floor. The mechanism finding is real;
the landmark claim is not.

**5.2 — The `x_μ` interpretation is actionable now.** T379 defines a stopping-depth
coordinate on a four-layer stack. T409's bands are most plausibly stopping-depth classes.
One cross-tabulation against counter-hit patterns settles it, using data already held.

**5.3 — T385's source discipline should be lifted into a standing requirement.** Frozen
hash, retrieval timestamp, observed-versus-advertised row count, mutable-endpoint guard,
and an explicit forbidden-predictor list. Applying that template to every external source
in the series would materially raise its auditability.

**5.4 — Positive.** T380 reports a wrong-pairing control beating the real geometry. T379
calls both its questions negative on a `4,505`-pair archive built from 15.9 million lines.
T385 refuses to inherit a source's own row-count claim. This batch contains stronger
negative reporting than any previous one.

---

## Required corrections

1. **T375:** restate as mechanism-supported / landmark-post-hoc; note convergence completes
   by three groups; apply the systematic floor to the `0.89%` residual.
2. **T379:** state that `x_μ` is a stopping-depth coordinate.
3. **T409 (retro):** run the band-versus-counter-hit cross-tabulation; cite T379's
   coordinate definition.
4. **T408/T409:** note visibly that the source archive failed its own primary test.
5. **Series:** adopt T385's source-record template as a standing requirement.

---

**Remaining after this batch: 15 tests** (T307, T369, T369B, T370, T374, T376, T377, T378,
T383, T384, T386, T387, T402, plus T391 and T393 already covered — net list below) plus the
two partials.

Net remaining: T307, T369, T369B, T370, T374, T376, T377, T378, T383, T384, T386, T387,
T402 — **13 tests**, plus T305 full and T404/T405 primary.
