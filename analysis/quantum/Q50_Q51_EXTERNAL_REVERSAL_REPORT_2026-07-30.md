# Q50–Q51 external-orientation reversal report

**Date:** 30 July 2026  
**Status:** Q50 post-Q49 diagnostic plus Q51 frozen construct holdout  
**Source class:** deterministic changing-connectivity quantum simulator archives; not quantum-hardware measurements

## Answer first

The early/late reversal discovered after Q49 is not explained by different
lineages entering the two time strata. Q50 held the same `(seed, pair)`
lineages fixed and found their aggregate external orientation move from
`x = 0.4156` to `x = 1.7206` on the ARA directional coordinate. The two
aggregate headings were `0.4817` turns apart, only `0.0183` turns from an
exact half-turn. A within-lineage time shuffle gave `p = 0.00019996`.

Q51 then froze that rule and applied the same construct to four network
strategy archives that had previously been used for other questions.
Three strategies supplied an eligible `c2` population, and all three passed
the orientation-reversal gates. The fourth `c2` strategy and all `c4`
branches were not testable because no extracted lineage spanned both time
halves under the frozen eligibility rule.

This supports a recurring `0 → 2` external-orientation reversal within this
simulator family. It does **not** yet establish a complete `0 → 2 → 0` ARA
cycle. No tested archive returned to the starting orientation, and movement
usually became very small around or after the reversal. Deterministic
relaxation toward a fixed state with residual drift reversal therefore
remains a live alternative explanation.

## Measured object

Each complete four-quadrant internal cycle was treated as one circle. Its
fitted centre supplied a point on the external path carrying that complete
circle through time. This report measures the direction of successive
centre-to-centre displacements, not the internal rotation of the circle.

Let \(\hat e\) be the direction at the centre of Q49's declared
\(1/e\rightarrow\phi\) arc and let \(d_i\) be a radius-normalised external
centre displacement. The directional balance and its ARA coordinate are

\[
B_G=\frac{\sum_i d_i\cdot\hat e}{\sum_i\lVert d_i\rVert},
\qquad
x_{\mathrm{ext}}=1-B_G.
\]

The coordinate reads:

- `x = 0`: movement along the declared external orientation;
- `x = 1`: directional ridge, cancellation or perpendicular balance;
- `x = 2`: movement exactly half a turn opposite the declared orientation.

This is a directional participation coordinate. It is not a claim that the
simulator's physical energy equals two.

## Q50 — same-lineage diagnostic

Q50 retained only lineages containing at least three development and three
evaluation events. This yielded `1,120` fixed lineages from `71` seeds and
`32,420` centre-displacement events.

| Q50 result | Value |
|---|---:|
| Development coordinate | `0.415611284` |
| Evaluation coordinate | `1.720566444` |
| Pooled change | `+1.304955161` |
| Aggregate heading separation | `0.481694964` turns |
| Distance from exact half-turn | `0.018305036` turns |
| Declared → opposite lineages | `460 / 1120` (`41.0714%`) |
| Opposite → declared lineages | `20 / 1120` (`1.7857%`) |
| Median paired change | `+0.591520565` |
| Seed-bootstrap mean-change interval | `[0.818297, 1.006540]` |
| Bootstrap probability of positive change | `1.0` |
| Within-lineage time-shuffle p-value | `0.00019996` |

Twenty fixed time bins showed one `0 → 2` ridge crossing, approximately
between slices `125` and `175`. The observed range was
`x = 0.292637...` to `1.994499...`. No `0 → 2 → 0` sequence occurred.

The motion budget is the main qualification. Total radius-normalised
movement fell from `339.817925` in development to `7.742138` in evaluation,
an evaluation/development ratio of `0.0227832`. A preliminary four-flank
comparison made the crossing look like a pinch, but the following two-bin
mean was slightly lower than the crossing bin. Under the amended strict
definition requiring a rebound on both sides, an isolated crossing pinch
was **not supported**.

Independent validation passed `11/11` checks.

## Q51 — frozen cross-archive construct holdout

Q51 froze Q50's extraction, coordinate, eligibility and gates before using
four previously downloaded network-strategy archives. These archives were
not new to the project, but the external-centre reversal construct had not
previously been measured on them. Q51 is therefore a construct holdout, not
a fully blind new-data replication.

The primary frozen `c2` results were:

| Strategy | Fixed lineages | Dev `x` | Eval `x` | Heading separation | Active-motion gate | Complete return |
|---|---:|---:|---:|---:|---|---|
| random | `0` | — | — | — | NOT TESTABLE | NOT TESTABLE |
| greedy | `1,755` | `0.468739` | `1.767051` | `0.491752` turns | PASS via later recovery | FAIL |
| landmax | `1,346` | `0.402825` | `1.413151` | `0.493416` turns | PASS via later recovery | FAIL |
| mimic | `503` | `0.429054` | `1.210370` | `0.498672` turns | FAIL | FAIL |

For every eligible strategy:

- development was on the declared side of the ridge;
- evaluation was on the opposite side;
- heading separation was within `0.01` turns of an exact half-turn;
- declared-to-opposite lineage changes strongly exceeded
  opposite-to-declared changes;
- the seed-bootstrap interval for the orientation change remained above
  zero.

Across the four registered `c2` strategies:

- frozen orientation-reversal replication: **PASS, 3/4 registered and 3/3
  eligible**;
- active-traversal replication: **FAIL, 2/4**;
- complete-cycle replication: **FAIL, 0/4**.

All four `c4` branches were **NOT TESTABLE** under the unchanged
same-lineage rule. This is absence of an eligible cross-stratum lineage, not
evidence that `c4` geometry failed.

Independent validation passed `13/13` checks.

## ARA reading and scientific boundary

The strongest ARA-compatible description is:

1. a complete internally rotating identity has an external orientation;
2. that orientation begins on one side of the directional ARA coordinate;
3. it crosses the ridge and approaches the opposite orientation;
4. the same direction of change occurs inside fixed lineages and repeats
   across three eligible network strategies.

That is evidence for a recurring external **orientation flip** in this
simulator family. Calling it a physical singularity crossing remains an ARA
interpretation, not an established mechanism.

The data do not yet distinguish:

- a true `0 → 2 → 0` cycle whose return occurs after the recorded window;
- a one-way transition into a new orientation;
- ordinary convergence to a fixed state, with the tiny residual motion
  changing sign during relaxation.

The decisive observation is therefore not another replot of these
500-slice archives. It is a longer, predeclared run that keeps appreciable
movement alive beyond the first reversal.

## Next discriminating test

Use an untouched archive or newly generated trajectories of at least
`1,000` slices. Freeze the same centre extraction and directional coordinate,
and introduce no archive-specific rotation. Register the following ordered
requirements before inspection:

1. the path begins on the declared side (`x < 0.5`);
2. it crosses the directional ridge;
3. it reaches the opposite side (`x > 1.5`);
4. radius-normalised movement subsequently recovers rather than remaining
   at the numerical floor;
5. the orientation later crosses back below the ridge, with `x ≤ 0.5` as
   the strict complete-return endpoint.

If movement remains active but no return occurs, the complete ARA-cycle
claim takes a direct hit. If movement dies and remains at the floor, the run
is informative about relaxation but cannot decide whether an unobserved
return exists. If a predeclared return occurs while movement is active, it
would supply the missing half of the proposed external cycle.

## Reproduction

Q50:

```powershell
python analysis/quantum/q50_same_lineage_external_flip_diagnostic.py
python analysis/quantum/q50_validate_same_lineage_external_flip.py
```

Q51:

```powershell
python analysis/quantum/q51_cross_archive_external_reversal.py
python analysis/quantum/q51_validate_cross_archive_external_reversal.py
```

Primary artifacts:

- `analysis/quantum/Q50_SAME_LINEAGE_EXTERNAL_FLIP_DIAGNOSTIC_PROTOCOL_v1.md`
- `analysis/quantum/Q50_SAME_LINEAGE_EXTERNAL_FLIP_RESULTS.json`
- `analysis/quantum/Q50_SAME_LINEAGE_EXTERNAL_FLIP.png`
- `analysis/quantum/Q50_SAME_LINEAGE_EXTERNAL_FLIP_VALIDATION.json`
- `analysis/quantum/Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL_PROTOCOL_v1_FROZEN.md`
- `analysis/quantum/Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL_RESULTS.json`
- `analysis/quantum/Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL.png`
- `analysis/quantum/Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL_VALIDATION.json`

