# T409 — Chronological parent-ridge tracking protocol

Frozen before the T409 calculations were run.

## Question

The T408 individual-event scatter visually suggests three vertical structures in the incoming parent ARA coordinate: two comparatively solid bands near `0.75` and `1.0`, plus a weaker structure near `1.3–1.4` that may be movement-loaded. T409 asks whether those structures remain fixed through chronological event order or whether the third centre travels.

This is a test of the incoming parent-coordinate geometry. It is not a direct neutrino measurement and it does not assign an exact release time to an individual muon.

## Who, what, when, where, why and how

- **Who:** the same two held-out event runs used by T407/T408: `6845.2020.0317.0` and `6845.2020.0318.0`.
- **What:** local density-ridge centres in the incoming two-pole ARA coordinate `x_mu`.
- **When:** chronological order within each run, divided into six fixed equal-count blocks per run. The combined track therefore has twelve blocks.
- **Where:** the full 2,109-event held-out population is primary. The 527 events inside the T408 parent daughter-time window are a conditioned control.
- **Why:** distinguish two anchored parent ridges from a genuinely travelling upper branch rather than relying on the aggregate scatterplot.
- **How:** fixed-band Gaussian density centres, chronological block tracking, and two order-shuffle controls.

## Frozen coordinate zones

The zones are read from the user-marked T408 geometry and are not refitted after scoring:

| Ridge | Frozen `x_mu` zone | Intended reading |
|---|---:|---|
| R1 | `[0.60, 0.90)` | lower marked parent ridge, visually near `0.75` |
| R2 | `[0.90, 1.18)` | middle marked parent ridge, visually near `1.0` |
| R3 | `[1.18, 1.55]` | upper weaker structure, visually near `1.3–1.4` |

Exact detector/topology poles `x_mu=0` and `x_mu=2` remain visible in population accounting but are excluded from ridge-centre estimation. No daughter-delay outcome is used to position the ridges.

## Centre estimator

For each population, run, chronological block and frozen zone:

1. evaluate a Gaussian kernel density on an ARA grid spaced by `0.001`;
2. use one fixed bandwidth of `0.035 ARA`;
3. define the ridge centre as the grid point with maximum density inside the frozen zone;
4. record zone occupancy and peak-to-median density contrast;
5. call a block centre *resolved* when the zone contains at least five events and peak-to-median contrast is at least `1.10`.

The pooled and per-run centres use the same estimator.

## Chronological motion statistic

For ridge `j`, with resolved block centres `c_b` and block counts `n_b`, define

\[
M_j=
\sqrt{
\frac{\sum_b n_b(c_b-c_{\rm pooled})^2}
     {\sum_b n_b}
}.
\]

Also report the centre range and mean absolute movement between successive resolved blocks within each run. `M_j` is the primary motion statistic.

## Frozen controls

1. **Global order shuffle:** shuffle `x_mu` across all 2,109 held-out event slots while retaining the original run/block sizes. This tests any chronological structure, including a between-run shift.
2. **Within-run order shuffle:** shuffle `x_mu` only inside each run. This preserves a static difference between runs and tests additional within-run movement.
3. **Conditioned population:** repeat the descriptive ridge track on the 527 T408 parent-window events. This checks whether daughter-time conditioning creates or removes the apparent structure.
4. **Wrong-lineage coordinate:** repeat pooled density summaries using `x_wrong`; this is a specificity diagnostic, not a primary gate.

Each shuffle uses `5,000` deterministic draws. Upper-tail p-values use the add-one rule.

## Gates

- **G1 — lower persistence:** R1 is resolved in at least `10/12` primary blocks.
- **G2 — middle persistence:** R2 is resolved in at least `10/12` primary blocks.
- **G3 — upper observability:** R3 is resolved in at least `8/12` primary blocks.
- **G4 — relative movement:** `M_R3 >= 1.5 × max(M_R1, M_R2)`.
- **G5 — chronological excess:** R3 global-shuffle `p <= 0.05`.
- **G6 — within-run excess:** R3 within-run-shuffle `p <= 0.05`.

## Verdict logic

- **Travelling upper branch supported:** G1–G6 all pass.
- **Run/regime-shifting upper branch:** G1–G5 pass but G6 fails; the displacement is between runs rather than a resolved within-run journey.
- **Anchored or quantized upper structure:** G1–G3 pass but G4 or G5 fails.
- **Upper structure not resolved:** G3 fails.

The labels describe this coordinate and sampling scale only. A failure does not rule out motion in another ARA cut, child coordinate or unmeasured anti-phase.

## Evidence boundaries

- The test is prompted by inspection of the T408 scatter and is therefore diagnostic, not pristine confirmatory discovery.
- Repeated vertical lines can arise from stable physical relations, detector/channel discretization, low-multiplicity ratios, or mixtures of those effects. Chronological motion is required before calling the third line a travelling branch.
- The two held-out runs are independent acquisition periods, not two newly collected experiments.
- `x_mu` is an incoming charged-detector relation. It is not a direct observation of either neutrino.
