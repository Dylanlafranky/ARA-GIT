# T454 frozen protocol — contextual TE-ARA remaining path

Frozen before inspecting T454 results.

## Question

Does the contextual TE-ARA allocation predict the unseen remainder of an individual yeast lifespan more accurately than the pure complement `2 − x_A`?

## Boundary

T453 prefix states are reused. Every forecast sees only observations through the current prefix. Individual total lifespan, terminal time, future intervals and completed-life normalisations remain forbidden.

## Coordinates

- `x_A = x_generation`: development-population 0–2 generation path.
- `x_clock`: development-population 0–2 elapsed-clock path.
- `R_AB = x_clock − x_A`: signed relational displacement.
- `x_size`, `x_rpl`: prefix-only internal-child coordinates.

Canonical TE-ARA remains the fixed total `2`. This test compares allocations within that ledger:

1. **Pure:** `B_pure = clip(2 − x_A, 0, 2)`.
2. **Relational:** `B_rel = clip(2 − (x_A + R_AB), 0, 2)`.
3. **Fixed grandchild:** `B_025 = clip(2 − (x_A + R_AB + 0.25), 0, 2)`.
4. **Measured size grandchild:** `B_size = clip(2 − (x_A + R_AB + x_size/4), 0, 2)`. A child ridge `x_size=1` projects to `0.25` two rungs up.
5. **Measured Rpl grandchild:** `B_rpl = clip(2 − (x_A + R_AB + x_rpl/4), 0, 2)`; Experiment 9 only.
6. **Reverse-relation control:** `B_reverse = clip(2 − (x_A − R_AB), 0, 2)`.

Size and Rpl are tested separately, not summed, because they may be coupled descriptions rather than independent allocations.

## Targets

- Remaining-generation share: `clip(2 × remaining_divisions / development median completed intervals, 0, 2)`.
- Remaining-clock share: `clip(2 × remaining_hours / development median completed hours, 0, 2)`.

These use development-population scales, not the tested cell's endpoint. Results are also shown against unbounded target values so clipping cannot manufacture a win.

## Evaluation

No formula is fitted. Primary score is mean per-cell MAE on untouched Experiment 9, followed by Experiments 1–6 external transfer. Whole-cell bootstrap, 2,000 resamples.

## Frozen gates

1. Relational forecast improves remaining-generation MAE by at least 5% over pure on Experiment 9.
2. At least one predeclared child forecast improves by at least 5% over relational on Experiment 9.
3. The winning Experiment 9 formula also improves remaining-clock MAE by at least 5% over pure.
4. Relational forecast improves remaining-generation MAE by at least 5% over pure externally.
5. The size-child correction improves externally over relational by at least 2%.
6. The reverse-relation control is worse than the correctly signed relational formula on both holdouts.

Passing supports a more accurate contextual allocation for this lifespan cut. It does not make TE-ARA variable, prove the child allocation universal, or identify Time itself.
