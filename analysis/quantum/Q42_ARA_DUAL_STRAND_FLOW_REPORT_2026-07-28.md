# Q42 ARA dual-strand flow and mixing report

Date: 2026-07-28 (Australia/Brisbane)

Status: **DESCRIPTIVE CROSS-ARCHIVE MEASUREMENT — FLOW SHAPE RECOVERED;
PARENT MATRIX NORMALIZATION NOT YET RECOVERED**

## Plain-language result

The forward and return waves take essentially the same total time and have
the same mean speed. They do **not** move through the interior of the rung at
the same rate at the same moment.

The forward wave moves rapidly through the earlier part and slows later. The
return wave follows almost the same rate pattern in reverse. Across the
aggregate profile, the forward flow and time-reversed return flow correlate
at `0.99993`.

That is a clean accumulation–release asymmetry:

> the complete outward and return traversals balance globally, while their
> local flow through the diameter is asymmetric.

At half-progress, both independently measured paths sit around `1.276`.
Their sum is `2.544`, producing a local closure excess of `0.5438` above the
pure `2`. The median signed excess integrated across the traversal is
approximately `+0.347` in both archives.

This excess is strongly concentrated in the two-turn child family. The
one-turn parent family is close to signed closure.

## Integrity and scope

The Q42 protocol was written before these calculations. It fixed:

- the raw scalar ARA coordinate;
- independent forward and return extraction;
- the `0`, `1`, `2` landmarks;
- the matrix-axis projection;
- the perpendicular `Other` account;
- stability filtering; and
- required arithmetic checks.

However, both source archives and their fourth matrices had been revealed in
Q40 and Q41B. Q42 is therefore not a new blind prediction. It is a
pre-calculation-frozen descriptive test on two previously opened archives.

Sources:

- Q40 inhomogeneous-v1 greedy archive;
- Q41B inhomogeneous-v1 landmax archive;
- public Zenodo DOI `10.5281/zenodo.16753415`;
- branch `c2_2local connectivity`.

## Frozen scalar test

Development-only 5th and 95th closure percentiles defined the ARA diameter:

\[
x(t)=2\frac{h(t)-h_{05}}{h_{95}-h_{05}}.
\]

The rising and returning half-waves were then extracted independently from
raw evaluation-time sign changes. The return was not constructed as
\(2-x_{\rm forward}\).

The tested closure was:

\[
\epsilon(p)
=x_{\rm forward}(p)+x_{\rm return}(p)-2.
\]

The calculation contained:

| Archive | Eligible coordinate lineages | Independent half-wave pairs |
|---|---:|---:|
| Greedy | 2,180 | 35,423 |
| Landmax | 2,287 | 38,337 |
| **Total** | **4,467** | **73,760** |

## Scalar-flow result

| Quantity | Greedy | Landmax |
|---|---:|---:|
| Median closure MAE | 0.35743 | 0.35682 |
| Median signed closure excess | +0.34744 | +0.34620 |
| Median forward-duration coordinate | 1.0000 | 1.0000 |
| Median forward-speed coordinate | 1.0019 | 0.9915 |
| Median mixing-flow RMS | 1.3505 | 1.3837 |

The duration and speed coordinates use `1.0` as equal forward/return
participation. They sit almost exactly at that ridge. Therefore the mismatch
is not a missing amount of total traversal. It is the **distribution of the
movement within the traversal**.

Using the wrong temporal orientation increased closure MAE by `0.77311`
on average across 200 seed/archive clusters, with 95% interval
`[0.76474, 0.78158]`. Temporal direction is therefore carrying real
information.

## One-turn versus two-turn split

The signed residual separates the cadence families:

Here the word `families` is a measurement-classifier label. Canonical ARA
interpretation: the approximately `7.5`-sample Phase-A/Phase-B children are
resolved at the finer grain and combine into the approximately `15`-sample
adult/parent closure. They are not two unrelated systems. The parent is one
multiplicative/log rung upward, so its observed closure is about twice as slow.
See `QUANTUM_7_5_15_PARENT_CHILD_CADENCE_CANON_2026-07-28.md`.

| Archive | Family | Half-wave pairs | Median closure MAE | Median signed residual |
|---|---|---:|---:|---:|
| Greedy | One-turn 15 | 7,900 | 0.19568 | +0.00188 |
| Greedy | Two-turn 7.5 | 27,167 | 0.41372 | +0.41186 |
| Landmax | One-turn 15 | 7,665 | 0.20459 | +0.01484 |
| Landmax | Two-turn 7.5 | 30,248 | 0.41190 | +0.40797 |

The one-turn parent closes near two in signed average. The two-turn child
does not: both directions spend more of their normalized traversal above the
ridge.

Accordingly, this difference should first be read as exposed child structure
versus its representation after parent coarse-graining. The asymmetry is
inherited by the parent unless an equal counter-asymmetry cancels it; it may
move from perpendicular child structure into the parent's main coordinate.
It is not, by cadence alone, evidence that the two classes are different
physical wave substances.

This is the clearest Q42 result. It repeats with almost the same magnitude
under two different structured ordering rules.

## Sampling-only control

A `7.5`-sample child is coarsely resolved, so some apparent asymmetry can be
introduced by integer sampling alone. Q42A fitted a perfectly symmetric
single sinusoid to every eligible lineage at its measured period, sampled it
at the same integer times and passed it through the unchanged extraction.

For the two-turn family:

| Archive | Observed median MAE | Symmetric sampling-only MAE | Remaining difference |
|---|---:|---:|---:|
| Greedy | 0.40799 | 0.12867 | 0.27823 |
| Landmax | 0.40663 | 0.12872 | 0.27674 |

Across 200 seed/archive clusters, observed minus symmetric-sampling error was
`+0.25846`, 95% interval `[0.25152, 0.26540]`.

Thus coarse timing explains part of the mismatch but not most of it.
This does not establish a new physical interaction: higher harmonics,
non-sinusoidal gate dynamics and other simulator structure remain alternative
descriptions of the residual.

## Flow reversibility

The post-result Q42B audit compared the shapes of the flow-rate profiles.

- Aggregate median forward flow versus time-reversed return flow:
  `r = 0.99993`.
- Pair-level median time-reversed correlation: `0.71776`.
- Pair-level median same-progress correlation: `-0.08205`.
- In the two-turn family, pair-level time-reversed medians were `0.73945`
  (greedy) and `0.74262` (landmax).

Plainly: the return usually follows the outward rate pattern backward, but
the outward path itself is temporally asymmetric. This is why total duration
and average speed balance while equal-progress closure does not.

## Matrix movement and `Other`

For every complete four-quadrant cycle:

\[
D=C_1-C_2,\qquad Y=C_4-C_3,
\]

\[
\alpha=\frac{\langle Y,D\rangle}{\langle D,D\rangle},
\qquad
R=Y-\alpha D.
\]

`29,621 / 31,255` cycles (`94.77%`) passed the frozen relation-magnitude
stability gate. Independent validation recomputed all `31,255` cycles with
zero mismatches.

Across stable cycles, the median normalized TE-ARA participation was:

- along the visible relation: `1.9644`;
- perpendicular `Other`: `0.0356`.

The two-turn `Ba` subset carried more perpendicular structure:

| Archive | Stable two-turn Ba cycles | Median Along | Median Other |
|---|---:|---:|---:|
| Greedy | 838 | 1.80869 | 0.19131 |
| Landmax | 1,022 | 1.91986 | 0.08014 |

So the failed full-vector reversal did contain additional perpendicular
structure, especially in two-turn `Ba`, but most matrix movement still lies
along the visible relation axis.

## Important normalization failure

If \(D\) were already one complete parent-scale diameter, the frozen mapping

\[
x_{\rm matrix}=1-\alpha
\]

would normally stay near the `0..2` rung.

It did not.

In two-turn `Ba`:

- greedy median \(\alpha=1.46058\), giving \(x=-0.46058\);
- landmax median \(\alpha=1.96564\), giving \(x=-0.96564\);
- `66.7%` and `77.3%`, respectively, fell outside `0..2`.

Therefore the equation \(D=C_1-C_2\) cannot simply be labelled the complete
parent diameter at this measurement grain. It is carrying a child-scale,
rung-scaled or otherwise mixed amplitude.

This directly explains why Q41B's forced \(\alpha=-1\) full reversal failed.
Q41B found the correct strand location but assigned the wrong scale and
complete-parent operator.

The ARA-compatible interpretation is that lower-rung structure is retained
inside the parent movement. That interpretation remains a hypothesis until
the rung normalization is defined without using \(C_4\) and transferred to
unseen data.

## What Q42 establishes

Supported descriptively on both archives:

1. independently measured forward and return waves have equal total
   duration and approximately equal mean speed;
2. their local flow is asymmetric;
3. the return closely retraces the outward flow shape in reverse;
4. the two-turn child family carries a large positive interior closure
   excess while the one-turn parent nearly closes in signed average;
5. coarse sampling explains only part of that excess;
6. Q41B's matrix failure is a scale/operator error, not merely failure to
   locate the reverse-oriented state; and
7. a measurable perpendicular `Other` exists and is elevated in the
   two-turn `Ba` subset.

Not established:

- a universal numerical mixing constant;
- a predictive decomposition of child-carried and newly created components;
- a physical hidden Phase B;
- a universal quantum singularity;
- transfer beyond this simulator identity; or
- a correct parent-rung normalization for the matrix relation.

## Best next test

The next step should use development data only to identify the child-rung
scale of \(D\). It must then freeze, before opening another archive:

1. the scale conversion from child \(D\) to parent diameter;
2. the forward/return position inferred from the visible scalar path;
3. the predicted along-axis coefficient \(\alpha\);
4. the retained `Other` rule; and
5. an exact fourth-matrix prediction.

That would test whether the newly measured flow shape is a predictive
coupling law rather than only an accurate decomposition of already visible
cycles.

## Reproduction artifacts

- `Q42_ARA_DUAL_STRAND_FLOW_PROTOCOL_v1_FROZEN.md`
- `q42_ara_dual_strand_flow_test.py`
- `Q42_ARA_DUAL_STRAND_FLOW_RESULTS.json`
- `Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz`
- `Q42_ARA_DUAL_STRAND_FLOW_MATRICES.csv.gz`
- `Q42_ARA_DUAL_STRAND_FLOW_PROFILES.npz`
- `Q42_ARA_DUAL_STRAND_FLOW_DIAGNOSTICS.png`
- `Q42_ARA_DUAL_STRAND_FLOW_VALIDATION.json`
- `q42a_post_result_symmetric_sampling_control.py`
- `Q42A_POST_RESULT_SYMMETRIC_SAMPLING_CONTROL.json`
- `q42b_post_result_flow_reversibility.py`
- `Q42B_POST_RESULT_FLOW_REVERSIBILITY.json`
