# T356 — plain ARA physical parent-ridge transfer

**Date:** 11 August 2026  
**Frozen verdict:** **NOT SUPPORTED (`5/7` gates)**  
**Protocol SHA-256:** `CEA75E318D0FBFA28F0869F2BBDFFF7FAFEAC369698C3A058F4B6598709D8289`

## Answer first

Two angle reversals were enough to locate the typical centre of the separately recorded flow event, but not every individual maximum-flow event. The unweighted midpoint was frozen before the velocity channel was scored; no pendulum equation, fitted correction or velocity value moved it.

Across **905 free-swing half-cycles**, the plain-ARA midpoint had median normalized timing error **0.08519** (95% bootstrap CI **0.07676–0.09812**) and 95th-percentile error **0.31010**. It retained **90.56%** of the interval's measured peak angular speed at the predicted location.

The two reversals define a **local half-swing parent** whose geometric ridge is their centre. Maximum flow commonly coincides with that ridge, but the failed tail and replication gates show that this physical expression is not invariant in the freely coupled triple pendulum.

## Registered comparison

| Predictor | Median error / half-swing |
|---|---:|
| Plain ARA midpoint | **0.085185** |
| Left child alone | 0.497065 |
| Right child alone | 0.502935 |
| Wrongly paired children | 0.575849 |

## Frozen gates

- `G1_absolute_location`: **PASS**
- `G2_tail`: **FAIL**
- `G3_two_child_necessity`: **PASS**
- `G4_correct_relation`: **PASS**
- `G5_directional_transfer`: **PASS**
- `G6_replication`: **FAIL**
- `G7_physical_ridge`: **PASS**

## Direction and replication

| Direction | n | Median error | Median retained flow |
|---|---:|---:|---:|
| increasing | 452 | 0.087149 | 0.902482 |
| decreasing | 453 | 0.084783 | 0.909706 |

| Run | Arm | n | Median error | Median retained flow |
|---|---:|---:|---:|---:|
| run1 | 1 | 90 | 0.197235 | 0.720602 |
| run1 | 2 | 90 | 0.138332 | 0.839227 |
| run1 | 3 | 93 | 0.041387 | 0.941002 |
| run2 | 1 | 94 | 0.271682 | 0.593854 |
| run2 | 2 | 95 | 0.170996 | 0.778665 |
| run2 | 3 | 147 | 0.037500 | 0.929735 |
| run3 | 1 | 89 | 0.112174 | 0.912405 |
| run3 | 2 | 90 | 0.120921 | 0.886503 |
| run3 | 3 | 117 | 0.033333 | 0.952894 |

## Driven transfer

The unchanged rule was also applied to **266** externally driven half-cycles. Median error was **0.036906**, 95th-percentile error **0.168304**, and median retained-flow fraction **0.966858**. This transfer cannot alter the free-swing verdict.

## ARA reading and boundary

This is plain ARA in a literal local slice: child pole + opposite child pole + their relation fixes the geometric parent ridge. It also explains why the relation mattered in T355: either landmark alone describes a boundary, while the pair supplies the missing location. T356 does not support equating that geometric ridge with the strongest individual-arm flow in every coupled state.

### Frozen post-result diagnostic

The separately frozen double-pendulum addendum returned `4/5` gates and did not support a generic depth-split law. Both double-pendulum arms instead showed a very clean central ridge: pooled median errors `0.029197` and `0.014545`, with `0.984482` and `0.978834` of peak flow retained at the centre. Together with the clean driven-triple transfer, this confines the strong splitting to particular freely evolving triple-arm states rather than to plain ARA or rung depth in general. See `T356_PHYSICAL_RUNG_DIAGNOSTIC_REPORT_2026-08-11.md`.

The result is a physical crosswalk and a successful prospective endpoint on previously opened public data. It does not prove universal ARA or new pendulum physics. The recovered identity—maximum angular flow—is specific to this oscillator representation; other systems require their own held-out physical referee.

## Reproduction

Run `t356_plain_ara_physical_parent_ridge.py`, then `validate_t356_plain_ara_physical_parent_ridge.py` from this directory with the repository verification environment.
