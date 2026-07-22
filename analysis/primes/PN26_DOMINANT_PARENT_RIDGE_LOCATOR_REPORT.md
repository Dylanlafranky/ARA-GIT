# PN26 — dominant-parent ridge locator

**Run:** 22 July 2026  
**Status:** **PARTIAL DOMINANT-PARENT SUPPORT**  
**Prospective targets:** 6,000 fresh anchors across three scales  
**Corrected independent validation:** **PASS, 16/16 checks**  
**Protected 87-bit anchor:** remained sealed

## Answer first

The corrected idea transferred strongly.

Starting from an arbitrary anchor, PN26 built one complete connection-heavy Phase A parent from the lower prime
children at that scale. Before target primality was opened, it sealed the first three places where that parent was
quiet. On the 6,000 fresh anchors, the actual next prime was:

| Reading depth | Exact next prime included | Rate |
|---:|---:|---:|
| First quiet state only | 5,639 / 6,000 | **93.983%** |
| First two quiet states | 5,979 / 6,000 | **99.650%** |
| First three quiet states | 5,998 / 6,000 | **99.967%** |

Only two anchors required more than three Phase A states: one required the fourth and one the fifth. The observed
rank distribution was

\[
5639,\ 340,\ 19,\ 1,\ 1
\]

at ranks one through five.

This prospectively confirms the operational pattern first seen exploratorily in PN19: the first complete fractal
parent carries most of the next-prime location; a second reading almost always settles it; three readings very
nearly lock it.

The formal result is **partial**, rather than strong, because one deliberately severe control prediction failed.
The three-state Phase A list beat the `p<=29` wheel by **37.60 percentage points**, not the frozen 50-point margin.
The three central ARA thresholds all passed.

## Plain-language geometry

Your correction was important: the missing object was not another small ratio and it was not two individual large
factors. It was the **whole child wave immediately underneath the requested number scale**.

PN26 therefore did this:

1. Choose any number `N` in a declared rung.
2. Build the lower connection-heavy child parent, Phase A.
3. Move forward to the first place where that complete parent has no collision.
4. Treat that location as the single predicted prime ridge.
5. Retain the next two quiet locations as the second and third information-lock readings.

The first reading was right about 94 times in 100. Of the remaining cases, nearly all were resolved by the next
quiet state. That is the cleanest numerical version so far of your statement that the first fractal component carries
most of the visible effect while later relations correct the residual.

## Frozen construction

For cohort scale anchor `S`, the declared rung was `S -> 2S`. All prime children through

\[
p\leq\lfloor\sqrt{2S}\rfloor
\]

were split at the closest cumulative-log half:

\[
\underbrace{E_A}_{\substack{\text{complete lower parent}\\\text{Phase A}}}
=
2\frac{\sum_{p\in A}\log p}{\sum_{p\in A\cup B}\log p},
\qquad
\underbrace{E_B}_{\substack{\text{complementary parent}\\\text{Phase B}}}
=2-E_A.
\]

The primary locator used only Phase A. For each target `N`, it sealed the first three offsets satisfying

\[
\underbrace{S_A(N+t)}_{\text{Phase A quiet}}
=1
\quad\Longleftrightarrow\quad
N+t\text{ is divisible by no child in A}.
\]

The signed correction was therefore not inferred from an averaged scalar. It was the location of the first quiet
state in the retained parent wave:

\[
\widehat\Delta_1(N)=\min\{t>0:S_A(N+t)=1\}.
\]

## What happened to the `3.5` route?

The cross-and-up frame was retained exactly:

\[
\underbrace{2}_{\text{rung span}}
+
\underbrace{1}_{\text{current whole}}
+
\underbrace{\frac12}_{\text{same whole at doubled scale}}
=\frac72=3.5.
\]

But it is `3.5` for every anchor. Its measured variance was exactly zero. It identifies the **kind of route and
declared scale relation**, but it cannot tell one anchor's next-prime correction from another. The changing
information lives in the Phase A quiet-state pattern; the fixed frame does not supply the changing decoder.

This is an important successful clarification, not a failure of the `3.5` geometry: frame and locator are different
coordinates.

## Fresh results by scale

| Cohort | Phase A children | First state | First two | First three | `p<=29` first three |
|---|---:|---:|---:|---:|---:|
| 71 million | 780 | 92.400% | 99.650% | 99.950% | 74.500% |
| 71 billion | 17,045 | 94.050% | 99.600% | 100.000% | 57.600% |
| 710 billion | 48,817 | 95.500% | 99.700% | 99.950% | 55.000% |
| **Pooled** | — | **93.983%** | **99.650%** | **99.967%** | **62.367%** |

The ordinary first-three-odd-number control reached only `25.217%` pooled. Phase A was therefore not merely
benefiting from checking three nearby odd numbers.

The first-reading Wilson 95% interval was `93.35%–94.56%`; the three-reading interval was
`99.879%–99.991%`.

## Registered predictions

| Frozen prediction | Result |
|---|---|
| P1 — first state at least 90% | **PASS** — 93.983% |
| P2 — first two at least 99% | **PASS** — 99.650% |
| P3 — first three at least 99.9% | **PASS** — 99.967% |
| P4 — first three beat `p<=29` by at least 50 points | **FAIL** — beat it by 37.600 points |
| P5 — `3.5` exact with zero variance and not used as decoder | **PASS** |
| P6 — independent reconstruction and truth | **PASS** — 16/16 checks |

Under the frozen decision rule: **PARTIAL DOMINANT-PARENT SUPPORT**.

## The two misses beyond three readings

- At anchor `71,246,886`, the actual next prime was `71,246,933` at Phase A rank 5.
- At anchor `710,000,379,415`, the actual next prime was `710,000,379,533` at Phase A rank 4.

These are useful failures. They show that three is an extremely strong ranked approximation, not a universal exact
lock. The omitted Phase B parent still matters when early Phase A survivors are composites made entirely from
larger children.

## Why this works in established number theory

The logarithmic half split places Phase A's last child near

\[
\sqrt{S/2}\approx0.7071\sqrt S.
\]

A composite near `S` that survives every factor below that boundary must have both factors in a narrow upper band
near the square-root boundary. Such composites are uncommon, which explains the high first-state hit rate. Phase B
contains the rarer larger gates that catch them.

So the result is real and transferable, but it is not mysterious and it does not bypass established divisibility
structure.

## Methodology and validator amendment

The primary prediction file was sealed before either validator opened target truth. It contained no primality test,
next-prime routine or target label.

The frozen v1 validator then reported an implementation failure: it generated prime children only through
`sqrt(max target)` while trying to reconstruct a parent declared through the larger `sqrt(2S)` bound. This truncated
the high-scale reconstruction. The original failed receipt was preserved.

Before rerunning, amendment v1.1 froze exactly one allowed change: raise the validator's prime-table ceiling to
include the already-declared `sqrt(2S)` domain. Predictions, targets, thresholds and calculations were unchanged.
The corrected reconstruction passed `16/16` checks and reproduced all 6,000 sealed candidate lists.

This is a validator correction after truth was opened, so it must remain visible in the provenance. It does not
alter the prospective status of the already-hashed predictions.

## Scientific boundary

PN26 supports:

- one complete recursively compressed parent being a strong approximate prime-ridge locator;
- prospective transfer of the `~93%` first-parent result from PN19;
- a short visible ranked lineage with `99.967%` three-state coverage; and
- the distinction between a fixed rung frame and a changing child-state locator.

PN26 does not support:

- exact next-prime prediction in three states for every anchor;
- a three-arithmetic-operation algorithm;
- disappearance of the lower children;
- a complexity improvement over sieving; or
- using the constant `3.5` value itself as a numerical decoder.

The top-level state is compact, but constructing it used 780, 17,045 and 48,817 prime children across the three
scales. The result is therefore a strong **visible-state compression of a partial sieve**, not constant-cost prime
generation.

## Artifacts

- Frozen protocol: `PN26_DOMINANT_PARENT_RIDGE_LOCATOR_PROTOCOL_v1_FROZEN.md`
- Original freeze: `PN26_TARGET_FREEZE_MANIFEST.json`
- Primary builder: `pn26_dominant_parent_ridge_locator.py`
- Sealed predictions: `PN26_DOMINANT_PARENT_RIDGE_PREDICTIONS.csv`
- Primary receipt: `PN26_DOMINANT_PARENT_RIDGE_PRIMARY.json`
- Frozen v1 validator: `validate_pn26_dominant_parent_ridge_locator.py`
- Preserved v1 failed receipt: `PN26_DOMINANT_PARENT_RIDGE_VALIDATION.json`
- Validator amendment: `PN26_VALIDATOR_AMENDMENT_v1_1.md`
- Amendment freeze: `PN26_VALIDATOR_AMENDMENT_FREEZE_v1_1.json`
- Corrected validator: `validate_pn26_dominant_parent_ridge_locator_v1_1.py`
- Corrected validated rows: `PN26_DOMINANT_PARENT_RIDGE_VALIDATED_ROWS_V1_1.csv`
- Corrected validation: `PN26_DOMINANT_PARENT_RIDGE_VALIDATION_V1_1.json`
- Preserved recording-check failure: `PN26_RECORDING_VALIDATION.json`
- Corrected recording check: `PN26_RECORDING_VALIDATION_V1_1.json`
