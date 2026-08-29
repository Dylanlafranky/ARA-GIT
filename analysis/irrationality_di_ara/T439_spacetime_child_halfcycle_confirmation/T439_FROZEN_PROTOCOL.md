# T439 — frozen multi-SXS spacetime-child half-cycle confirmation

Status before downloading/scoring holdout waveform and horizon products: **FROZEN**

## Question

Does the unchanged T438 relational-child landmark recur near one half of a parent waveform cycle from first common-horizon formation across several untouched binary-black-hole simulations?

T438 produced an absolute offset of `0.426702` parent cycles. Its signed offset was positive: the landmark occurred after first common-horizon formation. T439 therefore tests an **absolute half-cycle displacement** and preserves the sign as a separate descriptive result. It does not predeclare that the landmark must lead the horizon.

## Who / what / when / where / why / how

- **Who:** waveform Space/Connection step `S`, waveform Time/Traversal step `T`, their relational child `R_ST`, and the common apparent horizon `H_C` used only as the answer key.
- **What:** locate the strongest ordered change in the direction of the `(S,T)` path, `|d beta/dt|`, where `beta = atan2(|T|, |S|)`.
- **When:** the unchanged T438 late-parent basin: the waveform-only remaining-relation rank is at or below the `1.0` ridge and time is no later than the total modal-power crest. No horizon time defines this basin.
- **Where:** nine untouched, non-precessing SXS binary-black-hole simulations spanning mass ratio and aligned-spin conditions. SXS:BBH:0305 remains the T438 development case and is excluded from all T439 gates.
- **Why:** test whether T438's near-half-cycle result is a recurring cross-scale landmark rather than a one-simulation coincidence or a consequence of choosing a point near the waveform crest.
- **How:** apply the T435/T438 waveform construction without fitting per simulation, then reveal each simulation's published `common_horizon_time` and score the landmark in local parent cycles.

## Frozen holdout cohort

The cohort was selected from public SXS catalog metadata before any T439 waveform or horizon product was opened. Selection used only mass ratio, aligned spin, eccentricity, orbit count, and product availability.

1. `SXS:BBH:0001` — q≈1, effectively non-spinning.
2. `SXS:BBH:0004` — q≈1, anti-aligned effective spin.
3. `SXS:BBH:0176` — q≈1, high aligned spin.
4. `SXS:BBH:0007` — q≈1.5, effectively non-spinning.
5. `SXS:BBH:1166` — q≈2, effectively non-spinning.
6. `SXS:BBH:1178` — q≈3, effectively non-spinning.
7. `SXS:BBH:1906` — q≈4, effectively non-spinning.
8. `SXS:BBH:0181` — q≈6, effectively non-spinning.
9. `SXS:BBH:0063` — q≈8, effectively non-spinning.

Precessing and eccentric systems are intentionally deferred. This first confirmation asks whether the rule survives clean changes in mass ratio and aligned spin before adding orientation mixing.

## Frozen waveform construction

For the highest available numerical resolution of each simulation, load all complex `Strain_N4` modes on common support.

1. Total modal power: `P = sum_lm |h_lm|^2`.
2. Waveform radius: `A = sqrt(P)`.
3. Parent carrier phase: unwrapped phase of `h_22`.
4. Child orientation: `theta = phase(h_22)/2`.
5. Cadence: `omega = |d theta/dt|`, smoothed with the unchanged T435 cadence-derived Savitzky–Golay rule.
6. Remaining relation: reverse empirical rank of smoothed cadence, mapped to `[0,2]`.
7. Space/Connection step: smoothed `d log(A)/dt`.
8. Time/Traversal step: smoothed `d theta/dt`.
9. Relational-child direction: `beta = atan2(|T|, |S|)`.
10. Relational-child activity: smoothed `|d beta/dt|`.

The primary landmark is the largest relational-child activity inside the frozen late-parent basin. The pair is not forced to sum to 2, and `R_ST` is not defined as `2-S-T`.

## Frozen parent-cycle denominator

To reproduce T438 rather than redefine the scale after seeing new outcomes, use the T435 waveform-only handover estimate:

1. total modal-power maximum;
2. maximum positive derivative of smoothed cadence;
3. maximum absolute derivative of modal concentration `|h_22|^2 / P`;
4. their median time is `t_T435`;
5. local parent waveform cycle is `C_parent = pi / omega(t_T435)`.

No common-horizon time enters this denominator.

## Hidden scoring and frozen endpoints

After waveform landmarks are written and hashed, reveal published metadata and `Horizons.h5`.

For each holdout:

- signed offset: `(t_beta - t_HC) / C_parent`;
- absolute offset: `|t_beta - t_HC| / C_parent`;
- half-cycle deviation: `||t_beta - t_HC| / C_parent - 0.5|`;
- crest baseline: `|t_crest - t_HC| / C_parent`.

Primary confirmation gates:

1. median absolute offset is in `[0.40, 0.60]` parent cycles;
2. at least 6 of 9 holdouts are in the broad frozen half-cycle band `[0.25, 0.75]`;
3. at least 7 of 9 holdouts lie within one parent cycle;
4. the observed mean half-cycle deviation beats the chronology-shuffle distribution at empirical `p <= 0.05`;
5. median absolute offset is smaller than the crest baseline median.

Verdict:

- **SUPPORTED:** all five gates pass.
- **PARTIAL:** gates 1–3 pass but either control or crest comparison fails.
- **NOT SUPPORTED:** any of gates 1–3 fails.
- **UNSCORABLE:** fewer than seven holdouts provide the required products or a comparable common-horizon time.

## Frozen controls

- 1,000 within-simulation chronology permutations of paired `(S,T)` step histories, preserving the eligible time basin but destroying order;
- quarter-record circular roll of paired histories;
- radial/traversal label swap, which must leave the symmetric `beta` landmark unchanged and therefore cannot establish physical labels;
- total modal-power crest as the established waveform-only timing baseline;
- SXS:BBH:0305 retained as an external calibration row, excluded from holdout gates.

## Interpretation boundary

A pass would support a recurring landmark in SXS simulations generated within general relativity. It would be a crosswalk/confirmation of the ARA relational-child measurement, not independent proof that ARA generates gravity, black holes, or physical time. A result near 0.5 may identify child-scale projection, a post-horizon redistribution delay, or a shared waveform/horizon convention; those explanations remain competitors.
