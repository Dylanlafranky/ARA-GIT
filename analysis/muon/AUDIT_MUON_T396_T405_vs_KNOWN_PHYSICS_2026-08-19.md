# Audit — four more muon tests against established physics

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** T396, T397, T398, T404/T405 — the 16–18 August cluster.
**Companion:** `AUDIT_MUON_T403_T409_vs_KNOWN_PHYSICS_2026-08-19.md`

---

## 1. T396 — Information³ spin/child lock (10⁶ polarized V−A truth events)

**Reported:** primary gate **PASS**; joint `(P,R)→C` gains `+0.015506` nats/event,
CI `[+0.014412, +0.016642]`; zero-polarization falsifier `−0.027820`.

### 1.1 The correlation being measured is fixed by the Standard Model Lagrangian

For `μ⁺ → e⁺ ν_e ν̄_μ`, the V−A matrix element is

```
|M|² ∝ (p_μ · p_ν̄μ)(p_e · p_νe)
```

so positron kinematics and the neutrino energy split are correlated **analytically**.
Your own `analytic_va_oracle` row is that correlation computed exactly. T396 therefore
does not discover a relation; it measures how much of a known analytic relation the
ARA coordinates recover.

```
                        holdout NLL      gain vs parent_only    share of oracle
analytic_va_oracle       −0.116014          +0.054968              100%
additive_factorized      −0.081931          +0.020885               38.0%
joint_information3       −0.076552          +0.015506               28.2%
parent_only              −0.061046               —                    —
```

**The ARA joint construction recovers 28% of information that is available in closed
form.** That is a legitimate and interesting number — but it is a *recovery fraction*,
not a discovery, and the report does not state it.

### 1.2 The structure Information³ specifically predicts is the one that failed

Information³ asserts two identities **plus their retained relation** — i.e. that the
relation contributes beyond the two cuts taken separately. If so, the joint model must
beat additive fusion. It does not:

```
additive_factorized  +0.020885
joint_information3   +0.015506       additive wins by +0.005379  (35% more gain)
```

The report states this correctly ("does not require a learned nonlinear `P×R`
interaction") but the headline verdict is a PASS on the joint model. **The gate passed;
the hypothesis's distinctive content did not.** Two cuts each carry information and
their interaction adds nothing measurable — which is additivity, not Information³.

**Fair caveat, and it should be stated both ways:** the joint model is a dense
histogram and therefore higher-variance. Losing to additive is consistent with
estimator noise as well as with genuine absence of interaction. So this is decisive
against *this estimator demonstrating* an interaction, not against interaction
existing. A lower-variance interaction test (e.g. a constrained bilinear term) would
settle it.

### 1.3 The falsifier is well built

At zero polarization there is no spin axis, so `R = 1+cos θ_eS` carries no orientation
information and the gain should vanish. It reverses to `−0.027820`. Correct behaviour,
properly predeclared. This validates the estimator; it does not bear on ARA.

**Required:** report the oracle-share (28.2%), and restate the verdict as *complementary
additive information, interaction not demonstrated*.

---

## 2. T397 — spin phase: maturity versus orientation (muSR, RAL Silver)

**Reported:** `ORIENTATION_SUPPORTED_MATURITY_NOT_SUPPORTED`.

### 2.1 The orientation result is the founding principle of the instrument

```
Orientation O    +14.4147% SSE gain    CI [2.4618%, 25.2033%]    positive at 3/3 fields
```

Parity violation in muon decay means the positron is emitted preferentially along the
muon spin — asymmetry `a = 1/3` averaged over the Michel spectrum, rising toward 1 at
the endpoint. This is Garwin–Lederman–Weinrich, 1957, and **it is the entire physical
basis of the μSR technique.** A μSR apparatus exists because spin phase determines
which detector fires.

So "spin phase predicts detector direction" is not a finding — it is what the archive
was built to measure. Recovering it at 14.4% is a **validity check on the coordinate**,
and a good one, but the status string `ORIENTATION_SUPPORTED` will be read as a result.

**Required:** state explicitly that `O` recovers the known μSR decay asymmetry.

### 2.2 The genuinely new claim failed, and the residue looks systematic

```
W (strict common mode)   +0.7128%   CI [−1.9853%, +2.8053%]   crosses zero
per field:  63 G +1.0357%  ·  160 G +1.9543%  ·  400 G −1.0622%
reverse parity: 63 G also turns negative
amplitude: 0.06310% of the fitted parent envelope
```

An effect of 6 parts in 10⁴ that changes sign with field and with parity reversal is
the profile of an imperfect detector-balancing residue, not a population clock. The
high phase-resultant length (`0.9350`) is expected for any residue that is locked to
the same cadence used to bin it.

The frozen verdict — maturity not supported — is correct, and the informative content
of T397 is this negative.

---

## 3. T398 — population neutrino wave overlap (COHERENT CsI)

**Reported:** `POPULATION NEUTRINO RELEASE WAVEFORM OBSERVED; INDIVIDUAL BIRTH UNOBSERVED`;
all 8 frozen gates and 11 validation checks passed.

### 3.1 The prompt/delayed structure is COHERENT's design principle

Separation of the 26 ns prompt `ν_μ` from the 2.2 μs delayed `ν_e + ν̄_μ` is *how the
experiment works* and appears in every COHERENT publication. Recovering it confirms the
pipeline reads the archive correctly.

**The genuinely measured result is the AIC figure:** removing the delayed branch costs
`57.68` units, and the 2017 CsI holdout independently repeats positive prompt and
delayed populations in the correct order. That is real and should be the headline
rather than the handover coordinate.

### 3.2 Two validation checks are definitional identities

```
"pointwise flavor-child closure error: exactly 0.0"
"exact remaining-plus-released complement"
```

`ν_e + ν̄_μ = delayed total` and `remaining + released = 1` hold by construction. They
are correct as implementation checks but they cannot fail on valid inputs, and counting
them among 11 passed validation checks inflates the apparent stringency.

The flavour shares (`38.72%` / `61.28%`) are **inputs** — taken from the official
flavour-resolved source file under the frozen T371 response. The report says so
("source-template components... not flavor-tagged individually"), which is right, and
that sentence should sit with the numbers rather than below them.

### 3.3 The ARA coordinate at handover is derived, not observed

`cumulative 0–2 ARA coordinate at rate equality = 0.43740278` is a reading of a fitted
crossing point. The report's own warning — that instantaneous rate equality and the
cumulative parent ridge are different cuts and must not be collapsed — is the correct
and important caveat, and is well placed.

---

## 4. T404 / T405 — corrected child release and distortion-aware Di-ARA

### 4.1 T404 is the best thing in this group

T403 mapped eight local-child bins **linearly** into source time where T400 defines them
by **cumulative parent ARA**. The attractive `0.532` crest was an artefact of that
mismatch. You found it, corrected it to `0.706306`, and retained the record.

Catching a coordinate-definition error that had already produced a publishable-looking
crest, in your own prior test, is the single strongest methodological signal in the
muon series.

### 4.2 T405's ρ = 1.000 is algebra and is correctly labelled

```
Spearman ρ = 1.000  (prompt participation vs child-crest displacement)
every leave-one-out ρ = 1.000
equality-boundary position: same perfect rank
```

A Spearman of exactly 1.000 that survives every leave-one-out is the signature of a
**deterministic monotone function**, not a statistical relationship. `CLAIMS_STATUS.md`
already says this — "structurally encoded by the coordinate construction and is not
independent physical confirmation" — which is the correct call.

Same for the Di-ARA: both axes derive from the same fitted delayed template, so the
phase portrait plots a function against a transform of itself. Descriptive only, and
flagged as such.

**Required:** nothing. Both are already correctly bounded. Keep them that way — a later
reader will see `ρ = 1.000` and, without the caveat adjacent, take it for a result.

---

## 5. Cross-cutting finding

Across all four, the pattern is consistent and worth stating once at series level:

**Every positive result recovers something already established or definitionally
forced:**

| Test | "Positive" result | What it actually is |
|---|---|---|
| T396 | joint model gate PASS | 28% recovery of an analytic V−A correlation |
| T397 | orientation supported | the μSR decay asymmetry, known since 1957 |
| T398 | prompt/delayed waveform | COHERENT's design principle |
| T405 | ρ = 1.000 | a monotone function of the coordinate construction |

**Every genuinely novel claim returned negative:**

- T396: interaction beyond additive — not demonstrated
- T397: population maturity clock — failed, sign-flips with field and parity
- T398: individual neutrino birth — unobserved, and unobservable in this archive
- T404: the attractive crest that motivated the chain — an implementation artefact

This is the same boundary the T403–T409 audit found. It is a real and reportable result
in its own right: **the coordinate is validated against known physics and has not yet
produced information beyond it.** Stated that way it is a credible position. Stated as a
sequence of individual PASSes it will not survive outside reading.

---

## Required corrections

1. **T396:** report the 28.2% oracle-recovery share; restate as additive complementarity
   with interaction not demonstrated; note the variance caveat both ways.
2. **T397:** state that orientation recovers the known μSR asymmetry; describe the `W`
   residue as consistent with detector-balancing systematics.
3. **T398:** mark the two definitional identities as such and exclude them from the
   validation count; move "these are source-template inputs" adjacent to the flavour
   percentages; promote the AIC result and the 2017 holdout replication to the headline.
4. **T404/T405:** no change — keep the circularity caveats adjacent to the numbers.
5. **Series:** adopt the §5 table as the summary framing.
