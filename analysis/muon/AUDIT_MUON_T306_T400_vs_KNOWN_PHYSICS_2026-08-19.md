# Audit — four further muon tests (T306, T393, T395, T400)

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** T306 (30 Jul), T393 (15 Aug), T395 (16 Aug), T400 (17 Aug) — chosen to
cover the φ/e thread, the neutrino-pair kinematics, the Information³ chain, and the
population→event pivot.
**Companions:** `AUDIT_MUON_T403_T409_...md`, `AUDIT_MUON_T396_T405_...md`

---

## 1. T306 — embedded `1/e ↔ φ` thread

### 1.1 The boxed identity is `x = x`

```
(2 − φ) − 1/e   =   2 − (φ + 1/e)   =   0.01408657008
```

Expand both sides:

```
LHS:  (2 − φ) − 1/e  =  2 − φ − 1/e
RHS:  2 − (φ + 1/e)  =  2 − φ − 1/e
```

These are the **same expression with different bracketing**. The report presents this
in a display box and reads it as "the proposed child-side gap and the parent's
endpoint-closure deficit are the same number." They are the same number because they
are the same subtraction. This is associativity, not a crosswalk.

The label "an exact algebraic crosswalk, not a fitted result" is honest as far as it
goes, but a boxed equation reading `A = A` should not be presented as a finding at all.

**Required:** remove the box, or restate as "trivially, the gap and the deficit are the
same quantity written two ways."

### 1.2 The ridge proximity has no control

```
φ + 1/e = 1.9859134299        0.70% short of 2
(φ + 1/e)/2 = 0.99295671      0.0070 below the ridge at 1
```

The midpoint sits near `1` because the two chosen constants happen to sum near `2`.
With a pool of familiar constants (`φ, 1/e, e, π, √2, ln 2, γ, π−3, φ⁻²`), finding
*some* pair within 0.7% of 2 is close to expected. This is precisely the
crowded-neighbourhood problem your own ledger flags at M6 and D1, and no matched
control was run.

**Required:** a matched-constant control, or explicit demotion to coincidence.

### 1.3 The post-result gate amendment — and a rule this series now needs

```
original frozen verdict:  NOT SUPPORTED (1/3 substantive gates)
amendment:                G2 directionally invalid → INCONCLUSIVE
```

The stated reason is sound in principle: G2 described the child as *slower* than the
parent, while the octave rule says a child one rung down is *faster*. A gate encoding
the reverse of the hypothesis produces an uninformative failure.

But the defect was found **after** the result, and voiding it converts a FAIL to an
INCONCLUSIVE — the direction favouring the framework. This is now the **second**
post-result gate amendment in the series (T409B is the other), and both moved
favourably.

You handled it correctly by refusing to upgrade to PASS. What is missing is a standing
rule rather than case-by-case judgement.

**Proposed rule:** a gate may be voided post-result only if the defect is demonstrable
from the protocol text alone, without reference to the outcome; and the question must
be re-run under a corrected gate before any claim rests on it.

---

## 2. T393 — joint neutrino-pair projection

### 2.1 Every number in the boxed result is supplied by the Standard Model

```
0.245095 + 0.346518 + 0.408387 = 1.000000
```

The sum to `1` is energy conservation — correctly excluded from evidence in the report.
But the three components are the **analytic V−A conditional means**, and at exact
`x_e = 0.5` the decomposition is `0.25 + 0.34375 + 0.40625 = 1`, i.e. `8/32 + 11/32 + 13/32`.

Those are textbook muon-decay numbers. ARA supplies the labels; the Standard Model
supplies the values.

### 2.2 The `0.25` landmark is the Standard Model's, and the data missed it

The report states it plainly: *"The exact massless Standard-Model directional reversal
is `x_e = 0.5`, which would project to `0.25`."*

So the ARA-proposed quarter and the SM-exact quarter **coincide**. ARA cannot claim
confirmation for predicting a value that established theory already fixes exactly.

And the measurement did not reach it:

```
frozen T392 interval   [0.48612, 0.49446]     excludes exact 0.5
measured projection    0.245095               0.004905 below 0.25
```

The "approximate-quarter gate" passed on ARA's tolerance while the SM's exact value
sits outside the digitisation interval. That points at the digitisation, not at either
theory — and it is not evidence for ARA.

**Required:** state that the quarter landmark is Standard-Model exact and that ARA's
agreement with it is a coincidence of landmarks, not a confirmation.

### 2.3 What is genuinely informative

The `ν_e` / `ν̄_μ` asymmetry — `ν̄_μ` the higher-energy sibling in `68.93%` of the V−A
conditional distribution, and neutral-pair coordinates `0.918044 / 1.081956` against a
`(1, 1)` shuffle control — is a real structural statement. It is also standard V−A, so
it belongs as a validity check on the coordinate.

---

## 3. T395 — Information³ parent/child lock

### 3.1 Gate A is algebra and is correctly labelled

`C ≡ 2x_νe/N`, therefore `N·C/2 = x_νe` by substitution. Errors of `1e-16` confirm the
arithmetic. Labelled "forced mathematical composition, not independent physical
confirmation." Correct.

### 3.2 Two-thirds of the headline gain is phase space

This is the main finding of this audit. From the report's own table:

```
unconditional            0.201554
phase-space control      0.026074
Information³ lock       −0.062745

headline gain (uncond − lock)          0.264299   ← quoted as "the non-trivial result"
  of which: uncond → phase-space       0.175480   66.4%   kinematic support alone
            phase-space → lock         0.088819   33.6%   parent conditioning proper
```

The child coordinate is **defined relative to** `N = 2 − P`, so knowing the parent
automatically bounds the child's support. That support information is construction, not
physics, and the phase-space control measures exactly it.

**The genuinely non-trivial Information³ gain is `0.0888` nats/event, not `0.2643`.**

**Required:** quote the decomposition wherever `0.264` appears. As written, the number
overstates the result by 3×.

### 3.3 The point-estimate honesty is good and should stay prominent

```
child MAE      lock 0.233079   vs   unconditional 0.234370    (0.55% better)
absolute ν_e   lock 0.141962   vs   unconditional 0.142865    (0.63% better)
```

Large distributional gain, negligible point gain, reported as such. That is the correct
handling and it is the sentence that keeps the result honest.

---

## 4. T400 — nested child window, population to event

### 4.1 The transfer failed its own eligibility floor

```
beam-coincident rows in window        91
effective delayed-event weights       8.98271
predeclared minimum                   10          ← FAILED
```

The population→event transfer did not reach its registered sample floor. With `n_eff ≈ 9`:

```
weighted mean       1.05075       bootstrap CI [0.93228, 1.17471]
eight-bin mode      1.875         ← nowhere near the mean
broad-ridge mode:   60% of splits, 19.25% of bootstraps
```

A mode at `1.875` against a mean at `1.05` on nine effective events means the
distribution is unresolved, not that a ridge was located. The verdict — "balance or
centre-of-mass coordinate, not a demonstrated bell-curve maximum" — is the right call.

### 4.2 `0.70631` is load-bearing across four tests and its origin is unverified

The frozen primary crest here is `0.70631`. The same value appears as `0.706306` in
T404 (corrected release crest), T406 (population crest) and T407 (transferred band).

**One construction error at its origin invalidates four tests.** That raises the
priority of the check flagged in the T403–T409 audit:

```
0.706306
0.707107 = 1/√2      difference 0.000801
```

and T404 has already demonstrated that this coordinate chain can carry a
definition error that produces a plausible crest (`0.532`, from linear-vs-cumulative
bin mapping).

**Required, and now urgent:** trace whether `1/√2` can enter the construction via an
RMS, quadrature sum, half-power point or equal-area boundary. Until answered, T400,
T404, T406 and T407 share a single unaudited dependency.

### 4.3 The crest is not stable under fitting scope

```
T400 primary (calibration-only 0.5 µs components)    0.70631
T398 full fitted source                              0.88996
```

A shift of `0.18` — most of the distance to the `0.75` gate — from a change in fitting
scope alone. Reported as a diagnostic and not substituted, which is correct handling,
but it means the crest is not a stable feature of the data and no landmark claim should
rest on its exact value.

---

## 5. Cross-cutting

**5.1 — Boxed results that are identities.** Three of these four tests present a boxed
equation that is true by construction: T306's `A = A`, T393's energy conservation,
T395's Gate A. Two are labelled correctly; T306's is not. A reader scanning boxes will
take all three for findings.

**Suggestion:** adopt a visual convention — identities in plain text, empirical results
in boxes. Cheap, and it removes the whole class of misreading.

**5.2 — Information gains need a support baseline.** T395's headline is 3× its
non-trivial part once phase space is removed. T396 (previous audit) recovers 28% of an
analytic oracle. Both are legitimate numbers once decomposed and misleading when quoted
raw. This should become standard: **every reported gain quotes its baseline stack.**

**5.3 — Where the Standard Model is exact, ARA earns nothing by agreeing.** T393's
`0.25` is SM-exact. Coincidence of landmarks is not confirmation, and claiming it
invites the strongest possible objection at the weakest possible point.

**5.4 — Two post-result gate amendments, both favourable.** T306's G2 and T409B. Each
is individually defensible; the pattern needs the standing rule in §1.3.

**5.5 — Positive.** T400's eligibility floor was declared and enforced against
interest. T395's point-estimate weakness is stated in the report rather than buried.
T393 excludes its own conservation identity from evidence. T306 retains the original
NOT SUPPORTED verdict alongside the amendment. In every case the adverse information is
present in the document — the problem is placement and framing, not concealment.

---

## Required corrections

1. **T306:** unbox the `A = A` identity; add a matched-constant control for the
   `φ + 1/e ≈ 2` proximity or demote it.
2. **T306 / series:** adopt the §1.3 rule on post-result gate voiding.
3. **T393:** state that `0.25` is Standard-Model exact and that ARA's agreement is
   coincidence of landmarks, not confirmation.
4. **T395:** quote `0.0888` (parent conditioning) alongside `0.2643` (headline), with
   the phase-space share stated.
5. **T400:** trace the `1/√2` question — it is now a shared dependency of four tests.
6. **T400:** note that the crest moves `0.18` under fitting scope and that no landmark
   claim rests on its exact value.
7. **Series:** identities in plain text, empirical results in boxes.
