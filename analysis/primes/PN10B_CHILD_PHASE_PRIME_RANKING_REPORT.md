# PN10B child phase inside the pre-ridge factor sphere

**Run:** 20 July 2026  
**Registered verdict:** `NULL`  
**Orientation:** `0 = previous tested multiple`, `2 = next tested multiple`; gates run from the largest already-paid
divisor gate downward.  
**Protected material:** the p31 primorial wheel was not constructed and R12 was not opened.

## Technical summary

The proposed child decomposition is geometrically valid but did **not** improve prime ranking. Each paid divisor
gate closes exactly as `A+B=2`, and all gate/leakage guards passed. On the untouched interval
`[4,000,000,000,4,001,000,000)`, however, the primary 17-feature ARA child model scored `0.652923909` bits per
survivor versus `0.652816910` for the empirical parent alone. Its paired gain was therefore
`-0.000106999` bits/event, with a 95% contiguous-block bootstrap interval from `-0.000241111` to `+0.000034314`.
Its ROC AUC was `0.500307`, effectively chance.

The result is a clean instrumented null, not a failure to construct the child axes. It says that this particular
nine-gate residue-phase web does not expose the hidden composite identity before additional factor gates are
tested.

**Important reporting correction:** the registered ranking verdict and the descriptive ARA geometry are separate
results. A post-hoc event-centred disclosure found an exact parent `1.0` crest at each prime, parity troughs near
`0.062701` on every odd raw offset, and wide, frequently flipping child A/B readings inside individual prime
nodes. Those child distributions are almost identical in the surviving composites, which explains rather than
erases the ranking null. The full lead/lag trace, landmark occupancy, flip distribution and worked prime examples
are recorded in `PN10B_EVENT_CENTERED_GEOMETRY_REPORT.md`. This addition does not change any frozen criterion or
promote the test result.

## The fresh target contained ample unresolved identities

At the frozen PN10 parent cutoff `c=0.90`, the fresh interval retained `54,275` integers:

- `45,166` primes;
- `9,109` composites;
- survivor prime prevalence `0.832169507`.

This is a large, non-degenerate target. The task was not to recover primality exactly, but to rank which survivors
were more likely to be prime using only residues from gates already tested by the parent walk.

## The child geometry closed, but the outcome information did not appear

For the nine largest tested prime gates `q_j <= n^0.45`, PN10B defined

\[
A_j=2\frac{n\bmod q_j}{q_j},
\qquad
B_j=2-A_j,
\qquad
s_j=A_j-1,
\qquad
h_j=s_js_{j+1}.
\]

Across development, transfer and fresh intervals:

- maximum `|A+B-2|` was exactly `0` in floating-point arithmetic;
- every selected gate stayed below the paid parent boundary;
- no selected remainder was zero, as required for a survivor.

Plainly: each child gate really can be written as two opposing directions on the 0-2 line. The null occurs one step
later: those child positions do not tell us whether an untested divisor exists farther up the parent factor sphere.

## Fresh model comparison

| Model | Features | Log loss (bits) | Brier | AUC | Top-decile lift |
|---|---:|---:|---:|---:|---:|
| Buchstab parent | 0 | **0.652720245** | **0.139663906** | 0.500000 | 0.994683 |
| Parent empirical | 0 | 0.652816910 | 0.139682356 | 0.500000 | 0.994683 |
| ARA compact | 4 | 0.652846784 | 0.139687805 | 0.501193 | 0.995569 |
| ARA order-scrambled | 17 | 0.652841097 | 0.139686710 | **0.502502** | 1.005088 |
| Raw compact | 4 | 0.652902634 | 0.139698370 | 0.497254 | 0.999111 |
| Raw full | 17 | 0.652923873 | 0.139702352 | 0.496451 | 0.999775 |
| ARA full | 17 | 0.652923909 | 0.139702407 | 0.500307 | 1.012394 |

The established Buchstab rough-number probability was best calibrated on this target, but it is a constant and
does not rank individual survivors. No learned child model produced decision-useful discrimination.

## Registered comparisons

| Comparison | Gain (bits/event) | 95% block-bootstrap interval | Positive blocks / 100 |
|---|---:|---:|---:|
| ARA full vs parent | -0.000106999 | [-0.000241111, +0.000034314] | 40 |
| ARA full vs raw full | -0.000000036 | [-0.000074170, +0.000070622] | 55 |
| ARA full vs order-scrambled | -0.000082811 | [-0.000208106, +0.000032616] | 44 |
| ARA compact vs parent | -0.000029874 | [-0.000125758, +0.000057329] | 50 |
| ARA compact vs raw compact | **+0.000055850** | **[+0.000011362, +0.000103680]** | 59 |

The compact ARA summary did beat the equal-budget raw compact summary, but both were worse than the parent-only
forecast. This supports a narrow statement about compression choice, not hidden prime information.

## Development transfer did not replicate

Training on D and scoring the already-open E interval gave the ARA full model a tiny positive gain over parent:
`0.645482391` versus `0.645490131` bits, a difference of about `0.000007741` bits/event. The untouched F result
reversed that sign and was about fourteen times larger in the wrong direction. The registered cross-scale sign
criterion therefore failed.

## Registered criteria and verdict

| Criterion | Result |
|---|---|
| P1 child closure and gate guard | **PASS** |
| P2 primary fresh child value | **FAIL** |
| P3 development-transfer sign | **FAIL** |
| P4 equal-budget raw control | **FAIL** |
| P5 ordered-coupling control | **FAIL** |
| P6 compact representation | **FAIL** |

The frozen vocabulary therefore gives `NULL`: the measurement was adequate, the fresh target was large, the
implementation and leakage guards passed, and the primary effect was not found.

## Plain-language explanation

We successfully split each already-tested divisor gate into its own little ARA: how far the number has travelled
since the previous multiple, and how far remains until the next one. We then measured how nine of those children
lined up with each other.

That picture was real, but it did not reveal which numbers had a hidden factor farther ahead. Once we already know a
number missed all the tested gates, its exact position between those old gate multiples behaves almost like noise
for the next unseen factor. The best ARA model was essentially a coin-flip ranker inside a group that was already
about 83% prime.

So the answer to the immediate question is: **yes, the two parent directions can be decomposed into smaller A/B
children; no, these particular children do not add useful early prime information.**

## What this changes in the ARA prime map

PN10's factor sphere remains exact: reaching the square-root ridge without a divisor recovers primality. PN10B now
adds a useful boundary. Decompressing the already-paid residue state into local ARA children is not enough by
itself. To gain new prime information, a future method must either:

1. pay for new divisor gates;
2. use a different arithmetic identity whose structure is not conditionally washed out by sieve survival; or
3. predict a population/rung property rather than individual prime identity.

This does not disprove ARA's broader fractal claim. It is evidence against one precise proposed child coordinate as
an individual-prime ranking mechanism.

## Post-hoc geometry verdict

The completed descriptive audit gives a second, explicitly non-predictive verdict:

- **parent event geometry: recovered exactly** — a prime reaches the square-root factor-survival ridge at `1.0`;
- **lead/lag parent geometry: recovered descriptively** — parity troughs and sieve-period shoulders surround the
  event;
- **local child geometry: present and broad** — pooled Phase A spans `0.0000955–1.9999044`, with mean
  `0.9998605`, while individual prime centroids span `0.4997889–1.4266385`;
- **prime-specific child warning: absent** — survivor-composite child summaries differ by less than `0.015`
  pooled standard deviations, and the child centroid has no special offset-zero crest.

Future ARA reports must expose both the registered benchmark verdict and the full geometry verdict. A null on the
first is not permission to suppress the second.

## Validation

An independent script rebuilt all three survivor populations by direct multiple marking rather than importing the
primary implementation. It reconstructed the child features and fresh predictions, checked the fitted gradients,
and recomputed every headline metric and comparison. It passed `79/79` checks; maximum metric disagreement was `0`.

Reproduction:

```text
python analysis/primes/pn10b_child_phase_prime_ranking.py
python analysis/primes/pn10b_validate_child_phase.py
```

Primary artifacts:

- `PN10B_CHILD_PHASE_PRIME_RANKING_PROTOCOL.md`
- `PN10B_FREEZE_MANIFEST.json`
- `PN10B_CHILD_PHASE_RESULTS.json`
- `PN10B_MODEL_METRICS.csv`
- `PN10B_FRESH_COMPARISONS.csv`
- `PN10B_FRESH_TARGET_SCORES.csv`
- `PN10B_CHILD_PHASE_VALIDATION.json`
- `PN10B_CHILD_PHASE_FIGURE.png`
- `PN10B_EVENT_CENTERED_GEOMETRY_REPORT.md`
- `PN10B_EVENT_GEOMETRY_RESULTS.json`
- `PN10B_EVENT_CENTERED_TRACES.csv`
- `PN10B_CHILD_LANDMARK_COUNTS.csv`
- `PN10B_PRIME_CHILD_EXAMPLES.csv`
- `PN10B_EXAMPLE_NEIGHBORHOODS.csv`
- `PN10B_EVENT_GEOMETRY_FIGURE.png`
- `PN10B_EVENT_GEOMETRY_DIAGNOSTIC.ipynb`
- `PN10B_EVENT_GEOMETRY_VALIDATION.json`
