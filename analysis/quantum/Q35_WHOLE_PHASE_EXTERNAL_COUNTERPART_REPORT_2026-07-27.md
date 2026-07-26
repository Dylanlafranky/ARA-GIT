# Q35 — Whole Phase-A / External Phase-B Counterpart

**Date:** 27 July 2026  
**Ledger:** T290  
**Frozen claim verdict:** **INCONCLUSIVE — INSUFFICIENT SEAM-ELIGIBLE
LINEAGES**  
**Geometry verdict:** strong external phase-opposition signal, not yet a
recovered parent Phase B

## Outcome first

Q35 correctly treated the visible `c2` circle as one complete local identity.
It then searched outside that loop for one different fixed identity whose
motion was equal and opposite at the parent view.

The frozen external pair was strikingly opposed in the evaluable subset:

- median half-turn opposition: **`0.89576`** (`1` is perfect);
- positive opposition: **`100%`** of retained lineages;
- median parent cancellation residual: **`0.19366`** (`0` is perfect);
- half-turn occupancy: **`93.15%`**;
- counterpart evaluation circulation: median **`1.0`**.

Every phase-opposition and parent-cancellation control comparison passed with
seed-cluster bootstrap probability `1.000`.

However, the preregistered claim cannot be promoted. Although `2,495`
development lineages were complete loops and `2,491` received a frozen
counterpart, only **`84`** lineages repeated the strict low-boundary seam at
least five times in evaluation. The frozen eligibility floor was `500`.
Moreover, the exact counterpart's seam position (`x=1.736`) did not exceed
the `37`-slice time control (`x=1.776`). The strict result is therefore
**inconclusive**, not confirmed.

## What was tested

### ARA reading

| Step | ARA meaning |
|---|---|
| fixed source pair | one complete local identity followed through time |
| closure + movement | two diameter cuts revealing its loop |
| four occupied sign quadrants + coherent circulation | complete visible Phase-A loop |
| different fixed pair | candidate parent Phase B |
| half-turn separation | equal-and-opposite parent relation |
| small \(|A+B|/2\) | cancellation at the parent ridge |
| source low return while releasing | local singularity seam |
| counterpart high rank at that moment | far-pole handover signature |

### Physics/data reading

| Step | Public-simulator measurement |
|---|---|
| source | one fixed two-qubit pair lineage |
| closure | \(h=|\det C|^{1/3}\) |
| movement | \(g=h_{t+1}-h_t\) |
| loop chart | development-calibrated direction of \((h,g)\) |
| counterpart selection | different complete pair and lag `0..7`, development only |
| evaluation | unchanged pair and lag at times `250..498` |
| controls | displaced time, seed, pair, and `c4` network branch |

The closure magnitude was never substituted into the structural `0–2` ARA
diameter. The `0–2` empirical rank used at seam events is a display/crosswalk
coordinate only.

## Frozen evaluation results

| Relation | Median opposition ↑ | Positive | Median parent residual ↓ | Half-turn occupancy |
|---|---:|---:|---:|---:|
| **exact fixed counterpart** | **0.89576** | **100.00%** | **0.19366** | **93.15%** |
| time +37 | 0.67724 | 100.00% | 0.32184 | 63.23% |
| next seed | 0.12723 | 76.19% | 0.58189 | 27.93% |
| displaced pair | -0.10219 | 21.43% | 0.66564 | 26.28% |
| `c4` network | 0.09539 | 83.33% | 0.60013 | 28.10% |

For all four controls:

- \(P(\text{exact opposition}>\text{control})=1.000\);
- \(P(\text{exact residual}<\text{control})=1.000\).

These comparisons are clustered by unitary seed and use `20,000`
deterministic bootstrap draws.

## Seam results

The `84` eligible source lineages produced `1,344` seam events.

| Relation | Median counterpart x | Fraction above ridge | High-pole turn |
|---|---:|---:|---:|
| **exact fixed counterpart** | **1.736** | **100.00%** | **76.93%** |
| time +37 | 1.776 | 91.15% | 40.18% |
| next seed | 1.328 | 61.09% | 18.90% |
| displaced pair | 1.080 | 64.14% | 5.95% |
| `c4` network | 0.976 | 48.88% | 22.10% |

The exact relation is clearly at the far side and turns much more often than
the controls. But the time control reaches a slightly higher median rank.
Because the protocol required the exact relation to beat **every** control on
both seam measures, that gate fails.

The most likely methodological reason is visible in the original phase
portrait: this archive is strongly periodic. A displacement of `37` slices
can land near another far-pole visit. That makes "high when A is low" less
specific than the full fixed-pair phase relation.

## Why the eligibility gate failed

The development loop test and the evaluation seam test ask different
questions:

- `2,495` lineages trace complete loops during development;
- only `84` return to the same strict development-defined low boundary at
  least five times during evaluation.

Thus the **loop identity persists much more often than its absolute low
boundary**. The local loop centre/range drifts between halves, or the strict
5th-percentile seam is too sparse to serve as an invariant absolute seam.
Q35 cannot decide which explanation is physical. It only establishes that
the preregistered seam anchor was not sufficiently stable.

## Post-result all-loop diagnostic

Because the seam gate retained only `84` lineages, a clearly separated
post-result diagnostic asked whether the phase result was confined to that
rare subset. It was not.

Across all `2,491` development-eligible frozen pairings:

| Relation | Median opposition ↑ | Positive | Median residual ↓ | Half-turn occupancy |
|---|---:|---:|---:|---:|
| **exact** | **0.90474** | **100.00%** | **0.19201** | **99.18%** |
| time +37 | -0.70480 | 40.67% | 0.89468 | 10.04% |
| next seed | 0.04316 | 53.99% | 0.62292 | 26.12% |
| displaced pair | 0.11179 | 60.38% | 0.60518 | 26.75% |
| `c4` network | -0.05982 | 35.29% | 0.65782 | 23.69% |

This is a strong descriptive result: a counterpart selected in development
remains almost exactly half a turn away in evaluation throughout the greedy
network. It does **not** change the frozen Q35 verdict because it was examined
after the seam eligibility failure.

It also has a conservative established reading: `pure_greedy` is a highly
ordered deterministic simulator. Persistent paired phase relations can be a
property of its locked interaction schedule. Q35 located that structure using
the ARA complete-loop/opposite-parent construction; it has not shown that the
same pairing is a new fundamental quantum degree of freedom.

## Plain-language explanation

We followed one complete circular motion and used the first half of the data
to choose another circle that sat on the opposite side of the same larger
cycle. We then stopped choosing and watched the second half.

The chosen circle stayed opposite extremely well. When one was on one side,
the other was usually on the other side, and combining them left a much
quieter parent reading than any shuffled comparison. That is exactly the
shape you were asking us to look for.

The failure is narrower: our chosen definition of the black seam was too
strict and did not reappear often enough in most lineages. Among the few
lineages where it did, a 37-step time shift also landed near the far pole
because the system repeats strongly. So we have found a stable opposite pair
inside this simulator, but we have not yet earned the right to call it the
previously unseen parent Phase B.

## Honest interpretation

### Supported as a descriptive geometry

- The red `c2` loop can be operationalised as a complete local identity.
- Separate fixed loops can be paired development-first and remain nearly
  half a cycle opposed in evaluation.
- Their combined parent-direction residual is far smaller than broken
  relations.
- The pairing is identity- and network-specific, not just a free time shift.

### Not established

- an invariant absolute singularity seam;
- a fundamental hidden Phase B;
- a new quantum state or interaction;
- behavior outside this deterministic simulator;
- or universal ARA fractality.

## Best next test

The next clean step is **not** to loosen Q35 after seeing the result. Preserve
this failure. Freeze a new cross-archive test whose primary observable is the
development-selected half-turn pairing itself, with no absolute seam-frequency
gate, and transfer it to an untouched greedy archive with a different system
size or energy subspace. The seam should remain a secondary diagnostic.

That would distinguish:

1. a general external-counterpart rule;
2. a special property of this one greedy schedule;
3. and a local phase pairing that does not scale to a parent identity.

## Reproduction and validation

- Fidelity:
  `Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_FIDELITY_v1.md`
- Frozen protocol:
  `Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_PROTOCOL_v1_FROZEN.md`
- Primary script:
  `q35_whole_phase_external_counterpart_test.py`
- Results:
  `Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_RESULTS.json`
- Fixed candidates:
  `Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_CANDIDATES.csv`
- Scored lineages:
  `Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_TRACKS.csv.gz`
- Geometry:
  `Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_GEOMETRY.png`
- Post-result diagnostic:
  `Q35_POST_RESULT_ALL_LOOP_DIAGNOSTIC.json`
- Independent validator:
  `q35_validate_whole_phase_external_counterpart.py`
- Validation:
  `Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_VALIDATION.json`

Independent bounded validation passed **`9/9`**, including `24` independently
rebuilt candidate selections, `24` exact evaluation metrics, seam counts,
source hashes, saved summaries and the frozen verdict.

