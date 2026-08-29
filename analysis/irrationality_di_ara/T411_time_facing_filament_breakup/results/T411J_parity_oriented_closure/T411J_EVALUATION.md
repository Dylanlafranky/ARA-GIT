# T411J — parity-oriented parent/child/grandchild closure

## Assessment

The frozen **parent -> opposite child -> same-side grandchild** closure rule is **not supported as a universal causal handover predictor** in this dataset. It passed 2 of 4 predeclared gates.

The test does, however, preserve a useful structural result: orienting the child opposite the parent improves the unflipped closure score, and three of four fluids score above chance. What fails is the stronger claim that this absolute closure identifies the correct event time.

## What was tested

The test reused the 123 S1–S4 filament identities and the causal parent, child, and grandchild cuts established in T411H. Every predictor snapshot occurs before its target handover.

With centred coordinates

\[
v=x_P-1,\qquad u=x_C-1,\qquad w=x_G-1,
\]

the frozen candidate was

\[
(v,-u,w),
\]

meaning parent and grandchild retain the same orientation while the child is read in the opposite orientation.

For an oriented triplet \(z=(z_1,z_2,z_3)\), the coefficient-free score was

\[
A(z)=1-\frac{|z_1-z_2|+|z_2-z_3|+|z_3-z_1|}{4},
\]

\[
R(z)=1-\left|\frac{z_1+z_2+z_3}{3}\right|,
\]

\[
H(z)=A(z)R(z).
\]

Higher \(H\) was frozen to mean greater handover likelihood. AUC is used only as a ranking statistic; \(H\) is not a calibrated probability.

## Frozen gates

| Gate | Result |
|---|---:|
| Child-flip AUC above 0.5 | Pass — 0.5641 |
| Child flip best of four parity assignments | Fail — grandchild flip 0.5764 |
| Child-flip AUC above 0.5 in at least 3 of 4 fluids | Pass — S1, S2, S4 |
| Correct child timing beats within-event circular shifts at \(p\le0.05\) | Fail — \(p=0.1788\) |

**Frozen outcome: 2/4 gates passed.**

## Overall parity comparison

| Orientation | Handover AUC | Mean H in event window | Mean H outside event window |
|---|---:|---:|---:|
| No flip | 0.5514 | 0.4485 | 0.4099 |
| Child flip | 0.5641 | 0.4756 | 0.4295 |
| Grandchild flip | **0.5764** | **0.4772** | 0.4205 |
| Both lower flips | 0.5648 | 0.4586 | 0.4094 |

The child-flip score is above chance, but it is not the strongest of the four assignments. Its aligned timing is also not unusual relative to shifted versions of the same child trajectory: observed AUC 0.5641, shift-null mean 0.5536, 95% interval [0.5321, 0.5759].

## Fluid-level result

| Fluid | Child-flip AUC | Interpretation |
|---|---:|---|
| S1 | 0.5458 | Above chance |
| S2 | 0.6013 | Strongest child-flip result |
| S3 | 0.4884 | Below chance; counterexample |
| S4 | 0.5673 | Above chance |

The S3 counterexample prevents a universal reading. Its estimate is also based on only seven events, so it is informative but imprecise.

## Post-test channel-crossing observation

This section is explicitly **post hoc** and is not part of the frozen result.

The child-flip channel exceeds the grandchild-flip channel throughout the incoming trajectory. In the final child horizon, their order reverses:

| Lead before handover | Child-flip H | Grandchild-flip H | Grandchild minus child |
|---|---:|---:|---:|
| >8 | 0.4067 | 0.3981 | -0.0086 |
| (4,8] | 0.4457 | 0.4377 | -0.0080 |
| (2,4] | 0.4420 | 0.4325 | -0.0095 |
| (1,2] | 0.4708 | 0.4578 | -0.0130 |
| (0,1] event window | 0.4756 | 0.4772 | **+0.0016** |

In ARA language, absolute closure appears to describe the stable incoming relation, while the **change of dominant oriented channel** is a candidate description of the handover itself.

That candidate is not confirmed. The post-hoc switch score has AUC 0.5983, but its correct timing does not beat same-shift lower-rung controls: \(p=0.2128\), shift-null mean 0.5848, 95% interval [0.5528, 0.6184]. It also fails directionally in S1 (AUC 0.4758).

The grandchild-flip advantage over child flip is likewise not secure: AUC difference +0.0123 with event-bootstrap 95% interval [-0.0017, 0.0260]. Correct grandchild timing performs worse than its shifted controls (\(p=0.9201\)), indicating that its higher absolute AUC is mainly structural rather than event-timed.

## Claim boundary

- **Supported here:** the alternating parent/child/grandchild orientation remains a useful structural coordinate; orienting the child changes the recovered closure in the predicted direction.
- **Not supported here:** this coefficient-free absolute closure is a universal or correctly timed handover predictor.
- **New unresolved lead:** a causal child-to-grandchild channel crossing may be closer to the handover quantity than either absolute channel alone.

## Next frozen test

Predeclare the channel-crossing rule on untouched data before inspecting outcomes. The clean version should require:

1. grandchild-oriented closure minus child-oriented closure crosses from negative to positive;
2. the crossing persists for a frozen minimum dwell;
3. no fluid-specific coefficients or thresholds are fitted;
4. performance is compared with within-event time shifts and against the two absolute channels;
5. evaluation reports both event ranking and warning-time distribution.

The present T411J data must be treated as discovery data for that rule, not as its confirmation set.

## Reproducibility

- Protocol: `T411J_PARITY_ORIENTED_CLOSURE_PROTOCOL.md`
- Script: `t411j_parity_oriented_closure.py`
- Machine-readable result: `T411J_RESULTS.json`
- Scored snapshots and every bootstrap/shift audit are stored beside this file.
