# T350 — Tick-parent versus pure closure-front

**Run date:** 11 August 2026  
**Evidence boundary:** synthetic known-referee causal instrument calibration  
**Parent-memory verdict:** **SUPPORTED — 4/4 frozen gates passed**  
**Pure closure-front verdict:** **NOT SUPPORTED — 0/2 frozen gates passed**  
**Local tick/front verdict:** **SUPPORTED**

## Outcome first

The dominant instrument result is **parent memory; local tick remains a closure locator**.

The test gave every matched path the same endpoint and an exactly identical
final half-path. Therefore the final current state, final motion and all recent
ticks were identical. The only remaining difference was the ordered early
history.

## Parent-memory checks

| Check | Holdout result | Frozen gate |
|---|---:|---:|
| maximum tick reconstruction error | `8.882e-16` | `<1e-9` |
| pairs retaining final history distance >=0.02 | `1.0000` | `>=0.70` |
| median final/peak history retention | `0.8720` | `>=0.30` |
| median half-final emergence time | `0.2500` | `<=0.75` |
| median closure-jump share | `0.0162` | `<0.25` |
| median cadence distance | `0.0003` | `<=0.08` |
| cadence pairs within 0.12 | `1.0000` | `>=0.80` |

## Pure closure-front checks

| Check | Holdout result | Frozen gate |
|---|---:|---:|
| final history distances <=0.02 | `0.0000` | `>=0.90` |
| median final history distance | `0.4158` | `<=0.01` |
| median half-final emergence time | `0.2500` | `>=0.90` |
| median closure-jump share | `0.0162` | `>=0.50` |

## Local closure-front utility

Inside the shared linear suffix, current remaining distance divided by current
motion predicted the final handover with median error
`1.2335e-11` ticks and 95th-percentile error
`7.92511e-11` ticks. This is a local geometric locator,
not evidence that the front creates the stored history.

## Interpretation boundary

Exact tick reconstruction and exact closure timing in the common suffix are
partly algebraic sanity checks. The load-bearing result is whether the frozen
history vector retains early ordered information after half an event of
identical present-state ticks, whether that distinction appears before final
closure, and whether it survives cadence changes.

Passing the parent gates means the current ARA implementation behaves as:

`ordered tick-state children -> compressed path/history parent`.

It does not exclude a simultaneous top-down parent constraint or prove that
every physical system preserves the same amount of history.

## Artifact index

- frozen claim: `T350_TICK_PARENT_CLOSURE_FRONT_CLAIM_PACKET_v1.md`
- frozen protocol: `T350_TICK_PARENT_CLOSURE_FRONT_PROTOCOL_v1_FROZEN.md`
- path/prefix data: `T350_TICK_PARENT_CLOSURE_FRONT_PATHS.csv`, `T350_TICK_PARENT_CLOSURE_FRONT_PREFIXES.csv`
- matched curves and summary: `T350_TICK_PARENT_CLOSURE_FRONT_PAIR_CURVES.csv`, `T350_TICK_PARENT_CLOSURE_FRONT_PAIR_SUMMARY.csv`
- cadence and local closure: `T350_TICK_PARENT_CLOSURE_FRONT_CADENCE.csv`, `T350_TICK_PARENT_CLOSURE_FRONT_LOCAL_CLOSURE.csv`
- frozen gates: `T350_TICK_PARENT_CLOSURE_FRONT_FROZEN_GATES.csv`
- machine result: `T350_TICK_PARENT_CLOSURE_FRONT_RESULTS.json`
- main figure: `T350_TICK_PARENT_CLOSURE_FRONT_FIGURE.png`
