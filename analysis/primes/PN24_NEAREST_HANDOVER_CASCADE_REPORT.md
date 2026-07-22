# PN24 — nearest-child handover cascade

**Run:** 22 July 2026  
**Status:** **PARTIAL STRUCTURAL SUPPORT; COMPACT 90% CLAIM NOT MET**  
**Independent validation:** **PASS, 12/12 checks**  
**Protected 87-bit anchor:** remained sealed

## Answer first

The proposed nearest-child construction produces an exact, monotone handover path to the next prime when every
relevant factor gate is retained. It is a clean ARA description of an incremental wheel/sieve:

1. the nearest surviving lane below and above the chosen number form the local child pair;
2. the upper child is the first candidate;
3. when a later factor gate kills that child, the next surviving child takes over;
4. the first child that survives every gate through its square root is the next prime.

On the frozen 2,000-anchor development sample, the median path contained **two visible handovers** and **three
candidate states**. That is real compression of the *visible lineage*. However, only **63.65%** reached the prime
within three candidate states, below the frozen 90% threshold. If “three steps” means three handover corrections
after the initial state, the cumulative rate was **83.85%**, still below 90%.

Most importantly, the median path crossed **6,336 non-base prime gates**, of which about **6,334 were silent**.
The small visible event count therefore does not constitute a three-operation prime algorithm.

## The tested geometry in plain language

At the base rung, the number line is filtered by `2` and `7`. Around an anchor `N`, PN24 finds:

\[
\underbrace{L_0}_{\text{nearest survivor at or below }N}
\quad N \quad
\underbrace{U_0}_{\text{nearest survivor above }N}.
\]

The first forward correction is

\[
\Delta_0=U_0-N.
\]

If `U_0` is composite, some later prime gate `p` divides it. That gate removes the candidate. The wheel is enlarged
through `p`, and the nearest surviving upper lane becomes `U_1`. Repeating gives

\[
U_0\xrightarrow{p_1}U_1\xrightarrow{p_2}U_2\xrightarrow{}\cdots\xrightarrow{}P,
\]

where `P` is the next prime. This is exactly the proposed child → current rung → adult correction path, but every
arrow is found by factor information.

## Primary development result

The deterministic sample contained 2,000 anchors from the already-open interval
`[4,000,000,000, 4,001,000,000)`. It contained 1,930 distinct next-prime labels; overlaps mean rows are descriptive,
not independent prime events.

| Visible path measure | Result |
|---|---:|
| Initial base child already prime | 11.60% |
| Prime reached within 2 candidate states | 35.75% |
| Prime reached within 3 candidate states | **63.65%** |
| Prime reached within 3 handovers / 4 states | **83.85%** |
| More than 3 handovers required | 16.15% |
| Mean handovers | 2.1305 |
| Median handovers | 2 |
| 90th-percentile handovers | 4 |
| Maximum handovers | 9 |
| Mean candidate states | 3.1305 |

The handover count distribution was:

| Handovers | Anchors | Share |
|---:|---:|---:|
| 0 | 232 | 11.60% |
| 1 | 483 | 24.15% |
| 2 | 558 | 27.90% |
| 3 | 404 | 20.20% |
| 4 | 213 | 10.65% |
| 5 | 75 | 3.75% |
| 6 | 27 | 1.35% |
| 7 | 4 | 0.20% |
| 8 | 3 | 0.15% |
| 9 | 1 | 0.05% |

Under the frozen decision rule this is **partial structural support**, not strong compact support.

## How much did the first pair know?

The initial forward correction captured:

- mean `Delta_0 / Delta_final`: **24.82%**;
- median `Delta_0 / Delta_final`: **11.11%**.

So the first local pair normally pointed in the correct direction and supplied a genuine first child, but it did not
contain approximately 90% of the final location. Later gates contributed most of the numerical correction.

The exact mod-14 anti-pair cases `(1,13)` and `(5,9)` closed within three candidate states at **65.05%**, versus
**62.63%** for the other adjacent lane pairs. The difference was only 2.42 percentage points and was not compelling
in this development sample (`z≈1.11`, two-sided normal approximation `p≈0.267`). Exact anti-pair status did not
provide the missing prime locator.

## Fixed-rung comparison

Adding known child gates improved the first-candidate hit rate gradually:

| First surviving candidate after gates | Exact next-prime rate | Mean survivor candidates through prime | Median |
|---|---:|---:|---:|
| `2` only — odd scan | 10.36% | 10.063 | 7 |
| `2,7` — base mod 14 | 11.56% | 8.697 | 6 |
| through `3` | 16.99% | 5.955 | 4 |
| through `5` | 20.38% | 4.848 | 4 |
| through `11` | 22.52% | 4.434 | 3 |
| through `13` | 24.71% | 4.094 | 3 |
| through `17` | 26.11% | 3.877 | 3 |

This is the expected wheel-sieve progression: every additional gate removes some composite children before they are
proposed. There is no abrupt point at which one base child pair becomes a sufficient statistic.

## The hidden-work result

| Work measure on 2,000 anchors | Result |
|---|---:|
| Median visible handovers | **2** |
| Mean visible handovers | **2.1305** |
| Median non-base prime gates crossed | **6,336** |
| Mean non-base prime gates crossed | **6,335.80** |
| Median silent gates | **6,334** |
| Mean silent gates | **6,333.67** |

Plainly: most gates do not visibly alter the current candidate. They are still required to establish that no earlier
factor kills it and to prove the terminal candidate prime.

The clearest scale-anchor example is `900,000,000,000`:

\[
900000000001\xrightarrow{634939}900000000013.
\]

It looks like one clean handover, but gate `634,939` was reached only after **51,712 silent gates** in the declared
ordering. At `700,000,000,000`, the one visible handover occurred at gate `41,149` after 4,303 silent gates.

This is why “few visible corrections” and “few calculations” are different claims.

## Seven opened scale anchors

| Anchor | Base forward child | Handover gates | Next prime | Candidate states |
|---:|---:|---|---:|---:|
| 100,000,000 | +1 | `17, 643` | +7 | 3 |
| 1,000,000,000 | +3 | `23` | +7 | 2 |
| 10,000,000,000 | +1 | `101, 33889` | +19 | 3 |
| 100,000,000,000 | +1 | `11` | +3 | 2 |
| 400,000,000,000 | +3 | `59, 379, 36943` | +19 | 4 |
| 700,000,000,000 | +1 | `41149` | +9 | 2 |
| 900,000,000,000 | +1 | `634939` | +13 | 2 |

Six of seven reached the exact prime within three candidate states. The previously known `400,000,000,000` case
required three handovers and four states.

## What PN24 supports

### Supported exactly

- The nearest surviving lower/upper children are a well-defined local pair at every declared wheel rung.
- A killed upper child hands over monotonically to the next survivor when the relevant factor gate is added.
- The same update rule repeats at every gate.
- The complete cascade recovers the exact next prime on all 2,007 tested anchors.
- The event paths and final primes passed 12/12 independent validation checks.

### Supported as a useful ARA representation

- The prime search can be narrated compactly as a short lineage of visible child identities.
- Quiet gates and releasing gates are meaningfully different: most gates preserve the current identity; a few cause
  a visible handover.
- The same local phase-pair/handover rule recursively describes the wheel growth.

### Not supported

- The first nearest pair retaining approximately 90% of the final prime location.
- Exact next-prime recovery within three candidate states at least 90% of the time.
- Replacing factor gates with only two child values and one arithmetic correction.
- A new or faster prime algorithm from this rule alone.

## Scientific classification

PN24 is an exact **incremental wheel/trial-division crosswalk** with a useful event compression. It separates the
algorithm into:

\[
\underbrace{\text{many silent gates}}_{\text{proof / hidden work}}
+
\underbrace{\text{few releasing gates}}_{\text{visible identity changes}}
\longrightarrow
\underbrace{\text{next-prime ridge}}_{\text{first fully surviving child}}.
\]

That distinction is interesting for ARA because TE-ARA-like decompression can retain the “Other” factor gates while
the compressed identity path records only the few actual handovers. It is not evidence that the Other contribution
can yet be discarded.

## Artifacts

- Frozen protocol: `PN24_NEAREST_HANDOVER_CASCADE_PROTOCOL_v1_FROZEN.md`
- Primary script: `pn24_nearest_handover_cascade.py`
- Machine results: `PN24_NEAREST_HANDOVER_CASCADE_RESULTS.json`
- Per-anchor paths: `PN24_NEAREST_HANDOVER_CASCADE_ANCHORS.csv`
- Handover events: `PN24_NEAREST_HANDOVER_CASCADE_EVENTS.csv`
- Fixed-rung candidates: `PN24_NEAREST_HANDOVER_CASCADE_RUNGS.csv`
- Independent validator: `validate_pn24_nearest_handover_cascade.py`
- Validation receipt: `PN24_NEAREST_HANDOVER_CASCADE_VALIDATION.json`
