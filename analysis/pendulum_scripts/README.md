# Triple-Pendulum ARA Deconstruction — Reproducible Scripts

These scripts reproduce every result in `../PENDULUM_ARA_RESULT.md` from public
data. Each is self-documenting (see the docstring at the top), prints its numbers
to stdout, and saves its figure into `../` (the `analysis/` folder).

## 1. Get the data (public)

Source: **dynamicslab "MultiArm-Pendulum"** — the standard experimental benchmark
for chaos/learning/control on real pendulum hardware.

- GitHub: https://github.com/dynamicslab/MultiArm-Pendulum  (`Datas/` folder)
- Zenodo: https://doi.org/10.5281/zenodo.6633719
- Paper: Kaheman, Fasel, Bramburger, Strom, Kutz, Brunton (2022), arXiv:2205.06231

We use the **triple-pendulum free-swing runs** (three independent runs). Each is a
MATLAB `.mat` file containing the keys:

```
Theta1, Theta2, Theta3        # joint angles (rad), theta=0 is UP, rest/down ~ +-pi
dTheta1, dTheta2, dTheta3     # angular velocities (rad/s)
Time                          # seconds (0..60)
dt                            # sample period (1e-4 s, i.e. 10 kHz, 600001 samples)
```

Place the three triple-pendulum runs in a folder and name them (or edit `RUNS`
in `pendulum_common.py` to match your filenames):

```
run1 -> pend_triple.mat
run2 -> tri2.mat
run3 -> tri3.mat
```

> The dataset ships single, double, and triple pendulum experiments. **Triple is
> the published maximum — there is no 4+ arm experimental data.** Adding arms
> would require simulation, which this project deliberately avoids (real measured
> data only).

### Driven / excited runs (also in `data/`)

The `*WithControl*` files are the **driven** runs: the cart is moved back and
forth, so the system has an **external driver** and is **non-conservative**.
Same `Theta{1,2,3}`/`dTheta{1,2,3}` keys as free-swing (the triple-control single
files store the cart's own `Distance`/`Velocity` as MATLAB structs).

- `TripleDataWithControl_1_Dt_0_0001.mat` (70 s)
- `DoubleDataWithControl_1/2_Dt_0_0001.mat`
- `SingleDataWithControl_1/2_Dt_0_0001.mat`

Load the driven triple with `pendulum_common.load_triple_driven("triple1")`.

> **Verified, important:** the driven runs are *gentler* than free-swing
> (arm-3 max ~0.93 rad vs 1.73 free) — the cart excitation is mild, so they do
> **not** reach the over-the-top 0/2 singularity either. Their value is the
> external forcing + broken energy conservation (which lets the rise/fall ARA
> asymmetry — null on the conservative free-swing — actually become testable),
> NOT higher energy. The tumbling/flywheel regime remains untested by this dataset.

## 2. Environment

```
python >= 3.9
pip install numpy scipy matplotlib
```

## 3. Run

Point the scripts at your data folder with `PENDULUM_DATA` (default `./data`):

```bash
export PENDULUM_DATA=/path/to/your/pendulum/data
python 01_per_arm_geometry.py
python 02_leadership_rung_dominance.py
python 03_relational_ara.py
python 04_coupling_partial_corr.py
python 05_reconstruction_svd.py
python 06_forecast_causal.py
python 07_predict_last_arm.py
```

Figures are written to the parent `analysis/` folder by default (override with
`PENDULUM_OUT`).

## 4. What each script does (and the numbers to expect, run1)

| Script | Element | Key expected result |
|---|---|---|
| `01_per_arm_geometry.py` | each arm alone | all share period **1.333 s**; amplitude ladder A1 0.31 < A2 0.43 < A3 0.78 rad; arm-2 most clock-like |
| `02_leadership_rung_dominance.py` | coupling / dominance | lowest rung (arm-3) leads most often and holds longest blocks, **replicated 3/3** (exact %/switch counts pending re-run after prominence-filtered turn detection) |
| `03_relational_ara.py` | between-arms ARA | bend on rest-relative angles; upper joint hugs 1.0 ridge (std ~0.04); lower joint ~3x wider; no poles reached |
| `04_coupling_partial_corr.py` | arm-2 = shared carrier (clock = common mode) | PLV 0.94–0.99; **partial corr(1,3\|2) flips negative 2/3 runs** = arm-2 is the shared carrier (NOT a proven mediator); arm-2 not the steadiest (no replicate) |
| `05_reconstruction_svd.py` | reconstruction | mode1 89% (common clock = amplitude ladder), mode2 10.4% (1v3 anti-phase); **2 modes = 99.4%**, corr 0.984/0.994/1.000 |
| `06_forecast_causal.py` | strictly-causal forecast | high raw skill BUT **period-ago baseline (0.98 flat) ties/beats it** = quasi-periodic, not a chaos win; mode3 dies <1 s |
| `07_predict_last_arm.py` | predict the last arm | arm-3 from **only arms 1-2** = corr **0.99** nowcast→2 s, **beats arm-3 self-AR at 2 s** |

## 5. Reproducibility / honesty notes

- **Causality.** Scripts 06 and 07 are strictly causal: mode shapes and forecast
  weights fit on the training half only, no future features, no `filtfilt`/Hilbert.
  Script 04 *does* use `filtfilt`+Hilbert — that is fine because it is a
  **descriptive coupling** measure, not a forecast. Do not copy that pattern into
  a forecasting script.
- **Honest status.** The component techniques (POD/normal-mode decomposition,
  benchmark forecasting, low-rank reconstruction) are standard, and the high
  prediction scores are partly because this run is in the tame/quasi-periodic
  regime (the period-ago baseline proves it). The distinctive contribution is the
  ARA framing predicting the structure (clock/ridge, amplitude rung, arm-1-vs-3
  coupled via arm-2, no singularity without a flywheel) in advance — each of which
  held. See `../PENDULUM_ARA_RESULT.md` §9 for the full status discussion.
- Small numerical differences across machines/library versions are expected;
  conclusions (orderings, replications, the baseline deflation) are robust.
