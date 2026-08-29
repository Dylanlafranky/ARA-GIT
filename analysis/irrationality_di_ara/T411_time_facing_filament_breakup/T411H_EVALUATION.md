# T411H — three-rung grandchild-lock evaluation

## Validation assessment: share with caveats

**Frozen result: 4/5 gates passed; the full three-point lock is not confirmed.**

The proposed lower-rung seam is informative. Correctly timed
parent–child–grandchild geometry improved the parent+child comparator and beat
all 1,000 grandchild-shift controls. It also improved on parent-only Brier error
in S2, S3, and S4 and raised pooled risk ranking substantially. The remaining
failure is material: the full lock had worse pooled Brier error than
parent-only because it transferred poorly to S1.

## Question and method

Can a quarter-window grandchild seam provide the third relation that locks the
child singularity near the parent ridge?

The test used 123 source-qualified filament identities and 10,206 causal
snapshots. For each event:

\[
D_{PC}=|r_C-r_P|,
\qquad
D_{CG}=|r_G-r_C|,
\]

\[
x_G=2\frac{D_{PC}}{D_{PC}+D_{CG}}.
\]

`r_P`, `r_C`, and `r_G` use trailing parent, half-parent, and half-child
windows. Every complete fluid was held out once. The outcome remained parent
handover within one previously frozen child window.

## Leave-one-fluid-out performance

| Model | Weighted Brier ↓ | Weighted AUC ↑ |
|---|---:|---:|
| Constant | **0.07801** | 0.483 |
| Parent state | 0.08474 | 0.617 |
| Parent + child | 0.08889 | 0.612 |
| Parent + grandchild | 0.08300 | 0.640 |
| Three-rung additive | 0.08629 | 0.680 |
| Three-point lock | 0.08809 | **0.687** |

The constant has the lowest Brier score because the event is rare and the
cross-fluid models remain imperfectly calibrated. It cannot rank individual
snapshots meaningfully. The three-point lock gives the strongest ranking but
does not yet convert that ranking into the best transferable probabilities.

Relative to parent state, the full lock changed Brier error by fluid:

| Held-out fluid | Parent Brier | Lock Brier | Parent − lock | Lock AUC |
|---|---:|---:|---:|---:|
| S1 | 0.10299 | 0.12718 | −0.02419 | 0.641 |
| S2 | 0.08157 | 0.07824 | +0.00333 | 0.684 |
| S3 | 0.08265 | 0.07346 | +0.00919 | 0.792 |
| S4 | 0.06429 | 0.05729 | +0.00700 | 0.835 |

## Grandchild timing falsification

The aligned three-point lock improved on parent+child Brier by `0.000797`.
After shifting only the grandchild path within each event, every one of 1,000
controls became worse:

- observed aligned improvement: `+0.000797`;
- best shifted-control improvement: `−0.007057`;
- one-sided `p = 0.000999`.

The shifted control preserves parent history, child history, outcome,
grandchild distribution, and grandchild autocorrelation. The result therefore
supports timing information specifically in the three-way relation.

## Structural pair versus timed three-way lock

The predeclared parent+grandchild comparator improved on parent Brier in all
four fluids and raised pooled AUC from `0.617` to `0.640`. A post-hoc timing
audit then showed that this pair's gain was **not** specific to the observed
grandchild alignment:

- observed parent+grandchild improvement: `+0.001737`;
- shifted null median: `+0.003375`;
- `p = 0.994`.

Thus parent+grandchild is a useful structural descriptor or regulariser, but it
does not by itself time the handover. Timing specificity appears only when the
direct child relation is also present. This is consistent with an
Information³-style lock: all three relations are needed to distinguish the
event from the surrounding geometry.

## Frozen gates

| Gate | Result |
|---|---|
| Lock Brier below parent state | **Fail** |
| Lock Brier below parent + child | Pass |
| Lock AUC above parent state | Pass |
| Improves parent Brier in at least 3/4 fluids | Pass (3/4) |
| Correct grandchild alignment beats shifts, `p <= 0.05` | Pass |

## Validation checks

- all 123 eligible identities retained;
- no duplicate `(Name, time)` snapshots;
- every predictor timestamp precedes its target;
- every grandchild window is strictly smaller than its child window;
- event weights sum to one for every identity;
- saved `x_G` values reproduce the frozen formula to numerical precision;
- binary outcomes reproduce the saved lead and child-horizon columns exactly;
- headline Brier scores independently recomputed from saved predictions;
- final PNG inspected at full resolution for scales, labels, legends, and
  visible caveats.

## Main caveat and next test

S1 uses a three-frame grandchild against a five-frame child and is the only
fluid where the full lock worsens parent Brier. However, grandchild noise alone
does not explain the failure: parent+grandchild still improves parent Brier in
S1, while adding the direct child and interaction terms causes the loss.
Measurement resolution and fluid identity are confounded in this archive.

The next confirmation should therefore freeze the same three-rung geometry on
a new time-facing dataset with enough temporal resolution for at least five
distinct frames at the grandchild rung. It must retain a whole unseen identity
or medium for final scoring. No S1-specific correction should be fitted from
this result.

## Claim boundary

T411H supports a timed lower-rung contribution to the operational handover and
provides strong evidence for the proposed three-relation architecture within
three of four fluid identities. It does not yet establish a universal
grandchild singularity lock or independently identify the two physical
grandchild phases.

