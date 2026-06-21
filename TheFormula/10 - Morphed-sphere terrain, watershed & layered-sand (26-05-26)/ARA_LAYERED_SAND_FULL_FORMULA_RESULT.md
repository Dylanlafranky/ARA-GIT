# ARA Layered Sand Full Formula Result

Run date: 2026-05-26

## Purpose

This test implements the full layered-sand / rolling-sphere model as one deterministic ARA formula rather than another partial proxy.

The model encoded here is:

- moving floor below the system
- fine, medium, coarse, and measured sand/sphere layers
- each upward layer rolls in the opposite direction to the layer it touches
- each layer receives two lower contacts, creating wobble rather than uniform roll
- each layer reads its own recursive ARA terrain
- lower/faster spin controls how much roll transfers upward
- upper/slower coarse layers apply downward compression/backpressure
- the measured sphere rolls under a fixed water-slice/read point
- the arrived coordinate is read through the fractal ARA terrain

Script:

```bash
python TheFormula/ara_layered_sand_full_formula.py
```

Visualizer:

```text
TheFormula/ara_layered_sand_full_formula_viz.html
```

## Leakage Guard

The layered formula itself is strict-causal:

- all floor/layer/upper spin inputs use raw samples at or before origin `t`
- no lag ridge is used
- no native-value decoder is trained
- no future geometry oracle is used
- no smoothing or bandpass transform is applied
- no visual shift is used for scoring
- no historical nearest-neighbour terrain lookup is used inside the layered formula

Comparison overlays such as `wobble_surface_analog`, `raw_address_top1`, and `lower_core_top1` are included only so the new full formula can be seen beside the previous branches.

## Formula Structure

The cascade uses these periods:

| Layer | Period meaning |
|---|---|
| `floor` | `HOME / phi^4` |
| `fine` | `HOME / phi^3` |
| `medium` | `HOME / phi^2` |
| `coarse` | `HOME / phi` |
| `measured` | `HOME` |
| `upper_coarse` | `HOME * phi` |
| `upper_coursest` | `HOME * phi^2` |

Each layer calculates raw NINO, anti-phase SOI, and PDO spin at its own period. Contact pressure is split between two lower contacts, then transferred upward with parity flip, slip/wobble, recursive terrain pull, and upper compression.

## Main Result

Across the 6/12/24-month focus window:

| Model | MAE | Corr | Direction | Amp ratio |
|---|---:|---:|---:|---:|
| persistence | 0.896 | +0.003 | 0.000 | 0.000 |
| wobble surface analog | 0.608 | +0.218 | 0.779 | 0.732 |
| raw address top-1 | 0.795 | +0.091 | 0.288 | 0.510 |
| lower core top-1 | 0.845 | +0.069 | 0.270 | 0.572 |
| layered arrival | 0.894 | -0.001 | 0.519 | 0.055 |
| layered fractal | 0.882 | +0.013 | 0.544 | 0.203 |
| layered water | 0.886 | +0.008 | 0.544 | 0.085 |

The full layered formula is better than persistence on MAE by a small amount in `layered_fractal` and `layered_water`, and it creates nonzero turn direction. But it does not yet compete with the wobble/terrain analog branch.

## Diagnosis

The important failure is not that the full mechanism is missing pieces anymore. The pieces are now present.

The failure is that the measured sphere still does not advance far enough through the terrain address. The 6/12/24 amplitude ratios show this directly:

- `layered_arrival`: 0.055
- `layered_fractal`: 0.203
- `layered_water`: 0.085
- truth: 1.000 by definition

So the model is still under-rolling the measured sphere. The lower layers are producing directional pressure, but the final roll displacement is too small before the fractal terrain reader is applied.

## Current Interpretation

This is the first pass that is faithful to the user's full topology:

```text
floor movement
-> fast lower grains
-> alternating rolling contact
-> two-contact wobble
-> recursive ARA terrain per layer
-> upper compression
-> measured sphere terrain arrival
```

But the numeric law for converting lower-layer contact pressure into measured-sphere roll distance is still wrong. The next formula should focus on that transfer law:

```text
lower spin speed + two-contact pressure + upper compression
-> measured roll displacement in ARA address space
```

Not another decoder, and not another averaged lookup.

## Output Files

- `TheFormula/ara_layered_sand_full_formula.py`
- `TheFormula/ara_layered_sand_full_formula_result.json`
- `TheFormula/ara_layered_sand_full_formula_result.js`
- `TheFormula/ara_layered_sand_full_formula_viz.html`

