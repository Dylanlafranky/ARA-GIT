# T362 frozen protocol v1 - laboratory-fault Irrationality Di-ARA

**Frozen:** 12 August 2026, after source/schema QA and before coordinate scoring  
**Claim packet:** `T362_LAB_FAULT_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md`  
**Dylan heading:** exact enough to test

## WHO

The primary identity is laboratory stick-slip Event 101. Connection is local shear stress at sensor S20, x = 73.15 mm. Movement is local fault displacement at sensor L3, x = 70 mm. These are adjacent, independently measured channels with separate 2 microsecond time records.

The replication identities are 10 dry and 5 water-pressurized stick-slip cycles from Acosta et al. Their published fault-coupling histories are used only to replicate the connection-side handover, not to manufacture a second axis.

## WHAT

The physical Di-ARA is `(x_C, x_M)`:

- `x_C` is the robust 0-2 coordinate of local shear stress: low stored shear to high stored shear.
- `x_M` is the robust 0-2 coordinate of local slip-movement magnitude: low traversal to high traversal.
- The physical ridge is `(1,1)` on this declared within-event cut.
- Direction signs of both coordinates form the four causal states `++`, `+-`, `--`, `-+`, translated as the applicable `Ab`, `aB`, `Ba`, `bA` relation rather than earthquake classes.

The Irrationality parent is calculated from the angular/circumference history of that two-axis path:

- `x_P`: finite/reused addresses (0) to open/resolving addresses (2).
- `x_R`: relation-determined movement (0) to stochastic residual (2).
- `C(H)`: retained multi-lag closure history.

## WHEN

The synchronized dense event is downsampled from 2 microseconds to non-overlapping 2 millisecond bins. The first 80% of aligned time fixes all robust scales and trains the causal relation record. The last 20% is untouched holdout and contains the main rupture, whose time is defined independently as the largest positive local-displacement increment.

Irrationality coordinates use causal 512-bin windows (1.024 s) ending every 64 bins (0.128 s). A coordinate at time `t` contains no sample after `t`.

## WHERE

Calibration-only quantiles define each raw 0-2 diameter:

`x_C = clip(2 * (stress - Q05_stress) / (Q95_stress - Q05_stress), 0, 2)`.

Movement is first converted to `log1p(abs(delta displacement) / median_positive_calibration_increment)` and then mapped by its calibration Q05/Q95 to `x_M` with the same clipped 0-2 formula. Signed displacement increment is retained separately.

The angular path is

`z = atan2(x_M - 1, x_C - 1) / (2*pi) mod 1`.

Radius from `(1,1)` is retained so center-angle instability remains visible.

## WHY

The test asks whether Irrationality Di-ARA tracks the actual physical transition accumulation -> weakening/opening -> slip/release -> arrest/reconnection, and specifically whether the slip interface is a closure/handover of the movement channel rather than merely a large value on one sensor.

## HOW

### Source and alignment

The primary files are aligned by their published time vectors. The displacement stream begins 0.649370 s before the stress stream, exactly 324,685 samples at 2 microseconds. Only their common interval is retained. File checksums must match Zenodo metadata.

### Irrationality readings

For every causal 512-bin path window:

- Count occupied angular bins at 16, 32, 64, 128 and 256 bins. Twice the clipped log-log slope is `x_P`.
- Fit a 9-neighbour circular successor relation on the first half and score it on the second half. Twice its circular loss divided by the no-history circular-mean loss, capped at 2, is `x_R`.
- Retain closure coherence and miss for lags 1-128 as `C(H)`.

The label-blind ARA handover time is the end time of the largest chronological step in `(x_P,x_R)`. The physical main-slip time is not used to choose that step.

### Immediate movement record

Using calibration bins only, a 31-neighbour record predicts the next signed log-displacement increment from `(x_C,x_M,dir_C,dir_M)`. It is scored on the untouched suffix. Controls are:

1. direction-blind `(x_C,x_M)`;
2. connection-only `(x_C,dir_C)`;
3. movement-only `(x_M,dir_M)`;
4. wrong-pair target shifted by one quarter of calibration length;
5. previous-increment persistence.

Report RMSE, MAE, direction agreement, main-slip risk percentile and recursive free-run behavior. Only one-step recovery is a required gate; free-run is descriptive and cannot rescue a failure.

### Geometry controls

- 100 same-value time shuffles preserve physical values but destroy chronology.
- Wrong pairing circularly shifts movement by one quarter record.
- Connection-only and movement-only paths replace the missing coordinate with the ridge value 1.
- Reversal is descriptive because it preserves the visited geometry while changing direction.

### Independent repeated-cycle replication

For each of the 10 dry and 5 fluid-pressure fault-coupling curves, use only times from -50 s to 0 s. Define the connection handover as the greatest persistent fall in a 1 s centered moving mean. It must occur in the final 20% of the pre-mainshock interval (-10 s to 0 s). Dry and fluid records are scored separately and together.

## FROZEN GATES

1. **Independent physical traversal:** source QA passes, the two raw coordinates are not forced complements (`abs(r) < 0.98` outside the rupture +/-0.1 s), and at least three physical `(x_C,x_M)` quadrants are occupied by at least 1% of bins each.
2. **Irrationality parent traversal:** at least two `(x_P,x_R)` quadrants are occupied by at least three causal windows each, and the strongest parent step ends within one window length (1.024 s) of main slip.
3. **Broken-geometry discrimination:** the chronological parent handover has smaller absolute timing error than the median of all 100 shuffles and each of wrong-pair, connection-only and movement-only controls.
4. **Two-axis movement record:** primary holdout RMSE is at least 10% lower than every direction-blind, connection-only, movement-only, wrong-pair and persistence control; direction agreement is at least 0.65.
5. **Held-out rupture localization:** the primary predicted movement magnitude at the independently defined main-slip bin is in the top 1% of all holdout risk scores.
6. **Repeated connection handover:** at least 12/15 replication curves, including at least 8/10 dry and 4/5 fluid, place their greatest persistent coupling fall in the final 20% before mainshock.

`SUPPORTED ON THIS PHYSICAL ARCHIVE` requires Gates 1-6. Every failed gate remains failed; descriptive geometry cannot rescue the benchmark. Partial findings are reported narrowly.

## CHART CONTRACT

1. Raw synchronized stress, displacement and movement through time with main-slip and ARA-handover markers.
2. Physical 0-2 Di-ARA trajectory, fixed equal axes, ridge lines, chronological segments and direction-state styling.
3. Irrationality `(x_P,x_R)` parent path with fixed 0-2 axes, quadrant labels and window chronology.
4. Predictor/control comparison with exact error and direction values.
5. Replication heatmap or small multiples for all 15 coupling histories.
6. Frozen gate table visibly separated from descriptive findings.

No visual may imply that a physical ridge is an absolute energy equality; the 0-2 axes are declared robust relational cuts of this measured identity.

