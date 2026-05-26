# ARA Layered Sand Topological Formula Result

Run date: 2026-05-26

## Purpose

Correct the previous over-correction.

The recursive ARA sphere grid should not replace the layered-sand roll formula. The intended structure is:

```text
layered sand formula = how the measured sphere rolls / arrives
recursive ARA topology = what terrain exists inside each measured sphere
```

Script:

```bash
python TheFormula/ara_layered_sand_topological_formula.py
```

Visualizer:

```text
TheFormula/ara_layered_sand_topological_formula_viz.html
```

## What Changed

Kept from the layered-sand formula:

- moving floor;
- lower fast spheres/grains;
- alternating opposite roll;
- two lower contacts and wobble;
- upper pressure / braking;
- measured-sphere roll and phase arrival.

Changed inside each sphere:

- old terrain reader was replaced with recursive ARA topology;
- ARA and phase axes now contain phi, anti-phi, midline, sub-phi, sub-anti-phi, and deeper recursive bands;
- deeper topology weights fall as `1 / phi^(depth - 1)`;
- water/energy is pulled toward weighted local phi valleys and braked by ridge/counter pressure.

Follow-up correction:

- the first `topological_formula` branch still behaved like a now-machine because it used a small scalar `arrival_ara = current_ara + delta_ara`;
- its `corr_with_current` was about `+0.987` at every horizon, and mean `|delta_ara|` was only `0.018..0.050`;
- the new `topological_rotated` branch rotates the current point on the sphere by the layered roll vector and horizon angle, then reads recursive topology at that rotated coordinate.
- the new `topological_phi_wobble` branch keeps the same roll amount, but the wobble axis precesses through time by the golden angle `360 / phi^2`; this moves the arriving terrain address without fitting to future truth.

## Leakage Guard

- No future-origin row is read.
- No future target value is read until scoring.
- Persistence and legacy layered formula are comparison overlays.
- The formula still uses only current/past data available at origin.

## Main Results

| Horizon | Model | MAE | Corr |
|---:|---|---:|---:|
| 3m | persistence | 0.478 | +0.743 |
| 3m | legacy layered formula | **0.462** | **+0.749** |
| 3m | topological formula | 0.525 | +0.746 |
| 3m | true rotated topology | 0.562 | +0.644 |
| 3m | phi-time wobble | 0.564 | +0.655 |
| 3m | saturation gate | 0.550 | +0.663 |
| 6m | persistence | 0.737 | +0.351 |
| 6m | legacy layered formula | 0.710 | **+0.388** |
| 6m | topological formula | **0.693** | +0.371 |
| 6m | true rotated topology | 0.792 | +0.224 |
| 6m | phi-time wobble | 0.826 | +0.204 |
| 6m | saturation gate | 0.745 | +0.301 |
| 12m | persistence | 0.925 | +0.067 |
| 12m | legacy layered formula | 0.905 | -0.061 |
| 12m | topological formula | **0.866** | -0.072 |
| 12m | true rotated topology | 1.068 | -0.068 |
| 12m | phi-time wobble | 1.117 | -0.028 |
| 12m | saturation gate | 0.934 | -0.049 |
| 18m | persistence | 1.010 | -0.145 |
| 18m | legacy layered formula | 0.986 | -0.154 |
| 18m | topological formula | **0.961** | -0.141 |
| 18m | true rotated topology | 1.067 | -0.137 |
| 18m | phi-time wobble | 0.972 | +0.125 |
| 18m | saturation gate | **0.890** | -0.152 |
| 24m | persistence | 1.027 | -0.274 |
| 24m | legacy layered formula | 1.021 | -0.281 |
| 24m | topological formula | **0.992** | **-0.270** |
| 24m | true rotated topology | **0.785** | **+0.197** |
| 24m | phi-time wobble | 0.777 | +0.374 |
| 24m | saturation gate | 0.727 | +0.065 |

## Interpretation

This is closer to the intended architecture:

```text
roll from layered sand
terrain from recursive ARA sphere topology
```

The scalar topology-in-spheres version improves MAE over persistence and over the legacy layered formula at 6, 12, 18, and 24 months, but it is still strongly current-like.

The true-rotation branch is the first branch in this file that is clearly not sitting on persistence:

```text
topological_rotated corr_with_current:
3m  +0.867
6m  +0.599
12m +0.051
18m -0.405
24m -0.650
```

At 24 months, true rotation is substantially better than persistence and the scalar topology read:

```text
24m persistence:          MAE 1.027, corr -0.274
24m scalar topology:      MAE 0.992, corr -0.270
24m true rotated topology: MAE 0.785, corr +0.197
24m phi-time wobble:       MAE 0.777, corr +0.374
24m saturation gate:       MAE 0.727, corr +0.065
```

That suggests:

```text
recursive topology helps value terrain / amplitude error;
true sphere rotation helps at the longer wavecycle;
phi-time wobble improves the longer-horizon shape/correlation channel;
shorter horizons need a gentler/partial rotation rule instead of the full roll angle.
```

The saturation gate is a first test of the basin dwell rule:

```text
lower/contact roll proposes the rotated coordinate;
if the coordinate crosses the balance ridge before the basin is saturated,
the read is held near the ridge/contact line and only partially released.
```

This improves MAE at 18m and 24m, but it softens 24m correlation. That means it is acting like a plausible hold/brake rule, not a complete shape rule.

```text
Saturation gate crossing rate:
3m  0.101
6m  0.245
12m 0.427
18m 0.564
24m 0.848

Mean saturation when crossing:
3m  0.452
6m  0.419
12m 0.455
18m 0.408
24m 0.381
```

The next correction should keep this topology reader and true rotation branch, then make the rotation fraction horizon-aware instead of applying the full roll angle equally at every horizon.

## Failure Mode Noted

The 18-month branch exposes a repeated wrong-way mechanism:

- 2014-05 and 2014-08: the model rotates downward while the warm event is still building upward.
- 2020-02 through 2021-08: the model rotates upward while the cold event is still holding/downward.
- 2021-11 onward: the upward turn becomes valid.

The diagnostic points to **basin dwell / saturation** rather than simple leakage:

```text
2014-05 warm-basin age: 2 months, rotation releases too early.
2014-08 warm-basin age: 5 months, rotation releases too early.
2014-11 warm-basin age: 8 months, release is broadly valid.

2020-05 cold-basin age: 1 month, rotation releases upward too early.
2021-08 cold-basin age: 16 months, upward release is still too early.
2021-11 cold-basin age: 19 months, upward release is valid.
```

So the next formula piece should not just flip the rotation. A simple counter/hold gate was tested and was too blunt. The better next rule is:

```text
lower/contact roll proposes a future coordinate;
basin dwell/saturation decides whether the sphere is allowed to cross the ridge yet;
if not saturated, the water remains in the current basin and rides the local topology.
```

That rule is now implemented as `topological_saturation_gate` and exposed in the visualizer.

Visual read note:

- true-rotated positive spikes carry upward signal, especially at 24m;
- flat/deep-contact sections often carry downward signal at longer horizons;
- the manual topology preset is not clean enough as a predictor by itself, but it is useful as a regime hint for basin dwell and release timing.

## Output Files

- `TheFormula/ara_layered_sand_topological_formula.py`
- `TheFormula/ara_layered_sand_topological_formula_result.json`
- `TheFormula/ara_layered_sand_topological_formula_result.js`
- `TheFormula/ara_layered_sand_topological_formula_viz.html`
