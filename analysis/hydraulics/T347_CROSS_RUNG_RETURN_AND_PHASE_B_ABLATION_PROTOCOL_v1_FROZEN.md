# T347 cross-rung return and Phase-B ablation protocol — frozen v1

**Frozen:** 9 August 2026, before T347 scoring  
**Source boundary:** the already-open numerical BAW controlled-weir trajectories used by T344–T346. This is a post-T346 mechanism test, not an independent domain or confirmation.

## Six-question test card

**Who.** The same numerical trajectory identity is viewed at child `W≈7.5`, adult `W=15`, and parent `W=30`. Phase A denotes directional traversal; Phase B denotes the ordered connection/return contribution at the specified rung.

**What.** Test the cross-rung loop `A15 -> B8 -> A8 -> B15 -> A15`, and reconstruct the outgoing direction after graded Phase-B attenuation `lambda_B in {1, .75, .5, .25, 0}`.

**When.** Use the same movement-only `open -> coherent recurrence -> open` handover events selected by the frozen T346 `W=15` rule. Estimate the parent direction from the outer halves of the adjoining `W=15` blocks, without using the recurrent centre to define that direction.

**Where.** Look down from the `W=30` envelope: the parent view should be smoother, the `W=15` centre may contain a jerk/gap, and the two complementary child partitions within that centre should expose the return relation.

**Why.** Determine whether nonclosure is consistent with cross-rung handover and whether the proposed Phase-B contribution merely distorts Phase A, steers its outgoing direction, or stabilizes its return.

**How.** Score intact geometry against whole-track uncertainty and matched wrong-lineage controls. Separately compare intact, weakened, removed, reversed, wrong-child and matched-random Phase-B reconstructions; this is a computational ablation, not a physical intervention.

## Frozen construction

Use only T346 numerical `W=15` coherent anchors: preceding/following directness `D >= .75`, centre directness `D <= .75`, centre turn consistency `G >= .75`, and the frozen non-overlapping three-block construction. No Phase-B, child or outcome value may enter anchor selection.

### Rungs and directions

- **Adult/target rung:** the centre `W=15` block.
- **Parent envelope:** final 7.5 steps of the preceding block, all 15 centre steps, and first 7.5 steps of the following block. Half-step endpoints use fixed linear interpolation.
- **Parent entry and exit:** chord directions of those two 7.5-step outer flanks.
- **Parent direction:** circular mean of parent entry and exit directions.
- **Adult persistence:** `P_A = cos(theta_out - theta_in)`.
- **Adult roughness:** mean absolute step-angle departure from the parent direction, plus maximum perpendicular departure divided by centre path length.
- **Parent smoothing score:** centre angular roughness minus `abs(wrap(theta_out-theta_in))`; positive means the scale-up direction is smoother than the target centre.

### Child decomposition

Because 7.5 samples cannot be observed directly, compute both complementary non-overlapping decompositions, `7|8` and `8|7`, and equal-average their scalar readings. The first child is the proposed Phase-B return child and the second is the proposed Phase-A continuation child.

For each child calculate directness, signed net turn and ordered 4x4 transition information using the T346 estimator. Keep the primary contrasts in their own units:

- `Delta I_BA = I_first - I_second` (predicted positive);
- `Delta D_BA = D_second - D_first` (predicted positive).

The proposed Phase-B turning contribution `delta_B` is the circular mean of the first-child signed net turns from the two decompositions.

## Frozen gates

All confidence intervals use 2,000 whole-track bootstrap replicates with seed `34720260809`. Condition robustness requires the predicted sign in at least two of the three low/medium/high conditions.

### Gate A — parent directional persistence

Pass if the mean `P_A` 95% whole-track interval is above zero, its sign is positive in at least 2/3 conditions, and intact `P_A` beats 1,000 matched wrong-lineage exit directions at one-sided `p <= .01`. Matching strata are condition × progress decile × centre-speed quintile, and donors must come from a different track.

### Gate B — scale-up smoothing

Pass if the smoothing-score 95% whole-track interval is above zero and the score is positive in at least 2/3 conditions.

### Gate C — ordered child handover

Pass only if both `Delta I_BA` and `Delta D_BA` have 95% whole-track intervals above zero and each has the predicted sign in at least 2/3 conditions.

## Frozen Phase-B attenuation arm

For each event and fixed `lambda`:

`theta_hat_out(lambda) = theta_in + lambda * delta_B`

`L(lambda) = 1 - cos(theta_out - theta_hat_out(lambda))`.

Calculate population curves for intact `delta_B`, reversed `-delta_B`, wrong-child substitution, and 1,000 matched wrong-lineage `delta_B` assignments. No event-specific lambda fitting is allowed.

- **Phase A maintains direction:** `lambda=0` has the lowest intact population loss and Gate A passes.
- **Phase B steers:** a positive lambda beats zero with a whole-track interval above zero for `L(0)-L(lambda)`, and intact improvement beats the matched-null maximum at `p <= .01`.
- **Phase B counter-steers/stabilizes:** analogous registered evidence appears only for the reversed contribution.
- **Unresolved:** none of the above.

## Interpretation boundary

T347 can support or reject this operational cross-rung return model in the numerical weir representation. It cannot establish universal ARA geometry, physically remove a Phase-B wave, independently replicate T344–T346, or identify a unique physical energy carrier. Failed gates remain failed; exploratory plots cannot alter the frozen verdict.
