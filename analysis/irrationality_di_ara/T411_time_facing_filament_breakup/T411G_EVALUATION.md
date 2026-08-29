# T411G — causal child–parent Di-ARA evaluation

## Result

**Not supported under the frozen six-gate rule: 2/6 gates passed.**

The data nevertheless contain a narrower positive result. Correct temporal
alignment of the child and parent paths is informative: the aligned Di-ARA was
less damaging than all 1,000 within-event parent-shift controls
(`p = 0.000999`). However, the full fixed Di-ARA did not beat the simpler
child-state, additive, or constant models on probability error, and it improved
on the constant baseline in only two of four held-out fluid identities.

## Frozen data and geometry

- 123 filament identities;
- 10,308 causal snapshots after requiring both child and parent coordinates;
- one complete fluid identity held out at a time;
- outcome: parent handover within one frozen child window;
- child axis: `u = x_C - 1`;
- parent axis: `v = x_P - 1`;
- radial flow: `u du + v dv`;
- circulation: `u dv - v du`.

## Out-of-fluid performance

| Model | Weighted Brier ↓ | Weighted AUC ↑ |
|---|---:|---:|
| Constant | 0.07182 | 0.485 |
| Child position | 0.07312 | 0.402 |
| Child state | 0.07316 | 0.402 |
| **Parent state** | **0.07124** | **0.670** |
| Additive child + parent | 0.07403 | 0.614 |
| Full Di-ARA | 0.07491 | 0.628 |

The parent state was the strongest transferable instrument. It improved Brier
error by about 0.81% over the leave-one-fluid-out constant and ranked the next
handover substantially above chance.

The full Di-ARA ranked risk above chance in every held-out fluid
(`AUC = 0.560–0.711`) but its probability calibration was worse than the
constant overall. It beat the constant Brier score only in S2 and S4.

## Parent-alignment falsification

The aligned full Di-ARA was still worse than child state by 0.00175 Brier. The
median circularly misaligned Di-ARA was worse than child state by 0.00848, and
the 95th percentile remained worse by 0.00661. Thus the correct parent timing
recovers real information, but not enough to make this fixed full model the
best transferable predictor.

This distinction matters:

- **supported:** the observed child–parent timing relation is not exchangeable
  with arbitrary within-event parent alignment;
- **not supported:** one universal fixed Di-ARA interaction law, as
  operationalised here, predicts all four fluid identities better than the
  simpler controls.

## Why transfer failed

The parent-coordinate coefficient was positive and stable in all four training
folds. Several child and interaction coefficients changed sign when a fluid was
removed, including child position, child direction, `uv`, and circulation.
That is consistent with the per-fluid geometry panels: the parent axis carries
a common ordering signal while the child contribution is identity-dependent at
this measurement scale.

This is not evidence that the parent acts alone. The parent-shift control shows
that its correct coupling to the child matters. It is evidence that simply
adding all frozen child–parent terms with one shared set of coefficients is too
coarse.

## Frozen-gate audit

| Gate | Result |
|---|---|
| Di-ARA Brier below constant | Fail |
| Di-ARA AUC above 0.5 | Pass |
| Di-ARA Brier below child state | Fail |
| Di-ARA Brier below additive | Fail |
| Improves constant in at least 3/4 fluids | Fail (2/4) |
| Aligned parent beats shift controls, `p <= 0.05` | Pass |

## Interpretation boundary and next cut

T411G is an already-exposed archive diagnostic, not external confirmation. Its
strongest next use is to freeze a **parent-gated, identity-normalised Di-ARA**:
retain the transferable parent state as the coarse causal axis, then express
child displacement and circulation relative to each identity's own quiet
trajectory before testing a genuinely new fluid identity. That would test
whether the child geometry is a locally scaled distortion around a transferable
parent relation rather than a universal absolute coordinate.

