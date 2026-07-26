# Session Record — Q33B ARA-First Boundary-Child Flow Route

**Date:** 26 July 2026
**Ledger:** T288
**Status:** BOUNDARY-CHILD FLOW ROUTE SUPPORTED INSIDE THIS SIMULATOR

## Why Q33B was necessary

Q33 measured a raw endpoint/source energy-capacity ratio and substituted it
for ARA's rung coordinate. Dylan corrected the category error:

- ARA is the fixed generating geometry;
- physical closure, amplitude and energy are variable loads over it;
- a complete child contributes `1` at its own rung;
- the same child contributes exactly `0.5` one octave upward;
- the route uses the single child nearest the relevant boundary, not the
  average of two recipients.

Therefore the structural route is

\[
\underbrace{2}_{\text{complete same-rung span}}
+
\left(
\underbrace{1}_{\text{current rung}}
+
\underbrace{0.5}_{\text{boundary child one rung up}}
\right)
=3.5.
\]

The `0.5` was held fixed. Q33B tested a consequence of that geometry instead
of trying to derive it from energy.

## Frozen prediction

When a high-side source releases, the one exact endpoint child nearest the
low/`0` boundary should receive the flipped relation flow.

For each endpoint child:

\[
z_c(t)=\frac{h_c(t)}{Q_{.95}^{dev}(h_c)},\qquad
g_c(t)=\frac{h_c(t+1)-h_c(t)}{Q_{.95}^{dev}(h_c)},
\qquad
h_c=|\det C_c|^{1/3}.
\]

The smaller starting \(z\) selected the child without using its future. The
next-slice \(g\) was the scored outcome.

## Controls

The exact child was compared with:

1. its exact sibling;
2. a starting-position-matched non-endpoint topology pair;
3. an endpoint pair displaced to seed `+37`;
4. an endpoint pair displaced to time `+137`.

Every pair used the same one-of-two lower-\(z\) selection, so any generic
headroom or mean-reversion benefit was shared by the controls.

## Result

The evaluation set contained `11,543` source events across `200`
branch/seed strata.

| Route | Median flow | Mean flow | Positive fraction |
|---|---:|---:|---:|
| Exact boundary child | **+0.04143** | **+0.04952** | **63.64%** |
| Sibling | +0.04081 | +0.02570 | 55.83% |
| Topology | +0.00033 | +0.01335 | 50.79% |
| Seed | +0.00237 | +0.02146 | 56.38% |
| Time | +0.00203 | +0.02126 | 56.02% |

Median paired exact-minus-route flow was:

- sibling: `+0.01781`;
- topology: `+0.03385`;
- seed: `+0.02997`;
- time: `+0.02909`.

Every cluster-bootstrap probability that the exact route exceeded the named
comparator was `1.000`.

Both connectivity branches reproduced:

- `c2`: `5,772` events, median `+0.04281`, positive `63.34%`;
- `c4`: `5,771` events, median `+0.03964`, positive `63.94%`.

Development and evaluation were stable. Every frozen gate passed.

## Interpretation

Plainly: after the source releases, the ARA boundary rule points to the
endpoint relation that closes more reliably on the next slice. The displaced
controls are mildly positive, showing that selecting the lower candidate
generically creates some rebound. The exact endpoint retains an additional
`7.26–12.85` percentage-point positive-flow advantage.

The result therefore supports the **directed boundary-child closure-flow
consequence** of the fixed route inside this simulator.

It does not numerically derive `3.5`. The fixed `3.5` geometry generated the
prediction.

## Evidence boundary

- The primary result is determinant-closure movement, not raw energy.
- Median raw connected-energy flow did not order exact above sibling.
- The simulator is exactly diagonal and already open from Q27/Q28.
- The evaluation split was unchanged but not blind to the wider project.
- This is not hardware evidence, Phase-B identification, universal ARA or
  cosmological \(\varphi^{3.5}\) validation.

## Validation and artifacts

Independent validation passed `11/11`, including `64/64` deterministic
raw-route reconstructions.

- `analysis/quantum/Q33B_ARA_FIRST_BOUNDARY_CHILD_FIDELITY_v1.md`
- `analysis/quantum/Q33B_ARA_FIRST_BOUNDARY_CHILD_PROTOCOL_v1_FROZEN.md`
- `analysis/quantum/q33b_ara_first_boundary_child_test.py`
- `analysis/quantum/Q33B_ARA_FIRST_BOUNDARY_CHILD_RESULTS.json`
- `analysis/quantum/Q33B_ARA_FIRST_BOUNDARY_CHILD_TRIALS.csv`
- `analysis/quantum/Q33B_ARA_FIRST_BOUNDARY_CHILD_GEOMETRY.png`
- `analysis/quantum/Q33B_ARA_FIRST_BOUNDARY_CHILD_REPORT_2026-07-26.md`
- `analysis/quantum/Q33B_ARA_FIRST_BOUNDARY_CHILD_NOTEBOOK.ipynb`
- `analysis/quantum/q33b_validate_ara_first_boundary_child.py`
- `analysis/quantum/Q33B_ARA_FIRST_BOUNDARY_CHILD_VALIDATION.json`

The deterministic gzip event table is Git-ignored because of its size and is
recreated by the primary script from checksum-locked source caches.
