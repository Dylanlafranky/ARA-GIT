# PN7C actual-prime gap sequential-memory protocol

**Test ID:** `PN7C/ACTUAL-GAP-SEQUENTIAL-MEMORY/CODE-ISOLATED-R11-v1`  
**Declared:** 19 July 2026, before constructing any PN7C development or target gap sequence  
**Evidence class:** registered transfer/structural test; R11 is historically opened but code-isolated for PN7C  
**Protected material:** do not construct the p31 primorial wheel and do not open R12

## 1. Question

PN7B showed that actual-prime node/gap frequency and immediate handover recur strongly. PN7C asks the stricter
question:

> Does the direction of arrival into the current actual-prime ARA state improve prediction of the next state on R11,
> and how much of that improvement remains after controlling shared-gap overlap and ordinary first-order raw-gap
> transitions?

This is a next-gap-state distribution test after actual primes are known. It is not a predictor of the next prime's
exact location from integers alone.

## 2. Frozen data separation

- Development R9: `[1,000,000,000, 1,010,000,000)`.
- Development R10: `[10,000,000,000, 10,100,000,000)`.
- Evaluation R11: `[100,000,000,000, 101,000,000,000)`.

Construct exact actual-prime gap sequences independently inside each interval. Do not close interval boundaries with
an outside prime and do not join R9 to R10 when fitting transitions.

Required order:

1. hash this protocol;
2. construct R9/R10 gap sequences only;
3. fit and hash every predictive model;
4. create a target scorer that verifies the frozen model hash;
5. only then construct and score the R11 gap sequence.

R11 has been used in PN6/PN7A/PN7B, so this is not blind evidence. Code isolation prevents PN7C target tuning but does
not restore blindness.

## 3. Native ARA state and three-reading relation

For actual consecutive-prime gaps `(g_i)`, retain the PN7B state

\[
\underbrace{x_i}_{\substack{\text{current node-gap ARA state}\\0<x_i<2}}
=
\frac{2\underbrace{g_{i+1}}_{\text{outgoing gap}}}
{\underbrace{g_i}_{\text{incoming gap}}+\underbrace{g_{i+1}}_{\text{outgoing gap}}}.
\]

The prediction event is

\[
\underbrace{x_{i-1}}_{\text{arrival origin}},
\quad
\underbrace{x_i}_{\text{current state}},
\quad
\underbrace{x_{i+1}}_{\text{next state to predict}}.
\]

Primary resolution: 24 fixed equal bins on `[0,2]`. Sensitivities: 12 and 48 bins. Orientation and bin boundaries
may not change after results. Additive categorical smoothing is frozen at `alpha=0.5`.

## 4. Frozen predictive models

Fit by summing R9 and R10 counts while excluding every cross-window boundary.

1. `ARA-IID`: `P(x_next)`.
2. `ARA-M1`: `P(x_next | x_current)`.
3. `ARA-M2`: `P(x_next | x_previous, x_current)`.
4. `RawGap-M1`: estimate `P(g_next | g_current)` and project its next-gap distribution through the same ARA bin map.

The raw-gap alphabet is fixed to integer gaps `1..1024`. Training gaps outside that range are an implementation
failure; target gaps outside that range use the frozen marginal fallback. Raw transition rows use empirical-Bayes
shrinkage to the training marginal with `lambda=64`; an unseen current gap receives the marginal exactly.

`RawGap-M1` is not information-equivalent to `ARA-M2`: it sees the exact shared current gap but only one raw-gap
transition. The comparison tests useful compression/transfer, not equality of model class.

## 5. Frozen shared-overlap and raw-Markov controls

### 5.1 Exact target-inventory shuffles

Make five independent copies of the R11 gap sequence and shuffle each in place with seeds
`2026071901..2026071905`. Project every shuffled sequence through the same overlapping ARA construction and calculate
the empirical conditional-memory gain

\[
I(x_{i-1};x_{i+1}\mid x_i)
=H(x_{i+1}\mid x_i)-H(x_{i+1}\mid x_{i-1},x_i).
\]

This preserves the exact R11 gap inventory and the mechanical fact that neighbouring ARA readings share a gap, while
destroying real gap order.

### 5.2 First-order raw-gap Markov world

Generate `10,000,000` independent four-gap paths from the frozen R9/R10 `RawGap-M1` chain with seed `2026071917`:

\[
g_0\sim P(g),\quad g_1\sim P(g_1|g_0),\quad
g_2\sim P(g_2|g_1),\quad g_3\sim P(g_3|g_2).
\]

Project `(g_0,g_1,g_2,g_3)` into three overlapping ARA readings and calculate the same conditional-memory gain. This
world retains raw one-step gap dependence and shared-gap overlap but contains no memory beyond first-order gaps.

Control simulations are diagnostic and cannot tune the predictive models.

## 6. Registered scores

Score every R11 event from `x_2` onward in bits per next ARA reading:

- cross-entropy (primary; lower is better);
- Brier score;
- top-1 and top-3 accuracy;
- perplexity.

Divide R11 into 100 fixed contiguous equal-observation blocks. For `ARA-M1 minus ARA-M2` log loss, record:

- number of positive blocks;
- mean block gain;
- seeded 10,000-resample 95% percentile interval with seed `2026071923`.

No block, event or context may be excluded after target construction.

## 7. Registered conditions

### P1 — transferred arrival memory

At 24 bins, `ARA-M1 CE - ARA-M2 CE >= 0.010` bits per reading.

### P2 — distributed rather than isolated

At least 80 of 100 R11 blocks have positive M1-minus-M2 gain and the bootstrap lower 95% bound is above zero.

### P3 — measurement-grain recurrence

The M1-minus-M2 cross-entropy gain is positive at 12, 24 and 48 bins.

### P4 — beyond shared-gap overlap alone

The observed R11 empirical conditional-memory gain exceeds the maximum of the five exact-inventory shuffle gains by
at least `0.010` bits.

### P5 — beyond a first-order raw-gap world

The observed R11 empirical conditional-memory gain exceeds the raw-gap Markov-world gain by at least `0.010` bits.

### P6 — competitive compressed prediction

`ARA-M2` R11 cross-entropy is lower than `RawGap-M1` cross-entropy.

### P7 — supporting proper scores

At 24 bins, `ARA-M2` improves both Brier score and top-3 accuracy over `ARA-M1`.

The **residual ordered-memory core** is P1-P5. P6-P7 assess practical prediction and cannot rescue a failed core.

## 8. Interpretation rules

If P1-P3 pass but P4 fails, the visible arrival-memory gain is adequately explained by the ARA readings sharing a
gap. If P4 passes but P5 fails, shared overlap is insufficient but ordinary first-order raw-gap transition is enough.
If P1-P5 all pass, the allowed statement is:

> On code-isolated R11, arrival direction improves next actual-prime ARA-state prediction, and the observed
> conditional memory exceeds matched shared-overlap and first-order raw-gap worlds.

Even a full pass does not show that:

- ARA predicts exact unknown prime locations;
- the cause is a physical wave;
- ARA creates information absent from the raw gap sequence;
- a second-order or modular arithmetic model cannot explain the residual;
- the result is blind or a new theorem.

## 9. Required outputs and validation

- development and target gap packets with hashes and prime-count reconciliation;
- frozen model packet and pretarget manifest;
- per-model/per-resolution scores and 100 block gains;
- control-memory table;
- result JSON, static figure, report and executed notebook;
- independent validator that reconstructs headline target tensors/scores without importing the scorer;
- mapping update that retains PN7A and PN7B separately.

