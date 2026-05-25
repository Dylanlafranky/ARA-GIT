# Reproducibility Notes

**Public-release note, May 2026**

This repo contains current work, older exploratory scripts, visualizations, transcripts, and superseded attempts. Not every file is expected to run cleanly. The goal of this note is to make that explicit instead of leaving reviewers to discover it accidentally.

## Intended Minimal Setup

```bash
python -m pip install -r requirements.txt
python ara_framework.py
```

The current `requirements.txt` includes the main scientific stack used by the framework:

```text
numpy
scipy
pandas
matplotlib
neurokit2
wfdb
lightkurve
yfinance
requests
```

Some LLM scripts also require packages such as `torch` and `transformers`; those are not part of the minimal predictor install.

## Known Public-Release Issues

These were found during an outside-style audit of the local folder.

| Area | Issue |
|---|---|
| Hardcoded paths | Several scripts still point to old local paths such as `/sessions/amazing-cool-archimedes/...`. These should be replaced with repo-relative paths before asking others to rerun them. |
| Broken exploratory scripts | Some old `TheFormula` scripts have syntax or indentation errors. Treat these as archived experiments unless fixed. |
| Missing LLM dependencies | LLM scripts compile, but running them requires a separate ML environment with model weights/cache access. |
| Claim/data mismatches | A few public-facing headline numbers were stronger than the saved artifacts I reviewed. `CLAIMS_STATUS.md` lists the main ones. |
| Baseline comparisons | Forecast claims should report persistence, AR/Fourier, and non-phi log-ladder controls beside the ARA result. |

## Preregistered `home_k` Rule

For any public benchmark, choose `home_k` before scoring:

```text
home_k = round(log(ground_cycle_period) / log(phi))
```

Use the same time unit as the data. If more than one ground cycle is scientifically plausible, list all candidates before running the test and report all candidate results. Do not choose `home_k` from forecast performance.

## Recommended Validation Harness

The repo would be much stronger with one command that:

1. Downloads or locates public data.
2. Runs the canonical ARA predictor.
3. Runs persistence, AR/Fourier, and simple ML baselines.
4. Runs phi against nearby log bases such as sqrt(2), 1.5, 1.6, 1.7, and an optimized free base.
5. Reports correlation, MAE, directional accuracy, and skill versus persistence.
6. Separates descriptive classification, tracking, and blind forecasting.

Until that exists, please treat the repository as an inspectable research record rather than a turnkey benchmark package.

## Recent Runnable Geometry Tests

The 2026-05-21 ARA state-geometry and ENSO transport tests were run locally with the scientific Python stack available and repo-local data already present.

Useful entry points:

```bash
python TheFormula/ara_state_geometry.py
python TheFormula/ara_geometry_transport_test.py
```

Outputs:

- `TheFormula/ara_state_geometry_data.js`
- `TheFormula/ara_state_geometry_viz.html`
- `TheFormula/ara_geometry_transport_data.js`
- `ARA_GEOMETRY_TRANSPORT_RESULT.md`

Important interpretation guard: `ara_state_geometry.py` is a state-map extractor, not a forecast test. `ara_geometry_transport_test.py` is strict-causal for ENSO: at origin `t`, ridge training uses only anchors `s` where `s + horizon < t`. The result shows geometry-only lift over persistence at several horizons, but causal lag ridge remains stronger.

## Recent Runnable Temporal-Friction Tests

The 2026-05-23 temporal-flow follow-up was also run locally. These tests use repo-local ENSO, SILSO Solar, and ECG RR data where applicable.

Useful entry points:

```bash
python TheFormula/ara_retroactive_flow_test.py
python TheFormula/ara_temporal_friction_diagnostic.py
python TheFormula/ara_phi_distance_friction_test.py
python TheFormula/ara_phi_distance_bk_fit_test.py
python TheFormula/ara_temporal_pocket_diagnostic_test.py
python TheFormula/ara_enso_coupled_pocket_visibility_test.py
```

Outputs:

- `TheFormula/ara_retroactive_flow_data.js`
- `TheFormula/ara_temporal_friction_data.js`
- `TheFormula/ara_phi_distance_friction_data.js`
- `TheFormula/ara_phi_distance_bk_fit_data.js`
- `TheFormula/ara_temporal_pocket_diagnostic_data.js`
- `TheFormula/ara_enso_coupled_pocket_visibility_data.js`
- `ARA_TEMPORAL_FRICTION_RESULT.md`

Important interpretation guard: these tests do not prove that temporal friction is phi-distance. The strict result is narrower: pure `|ARA-phi|` friction fails, `1 + |ARA-phi|` is more useful, and negative `k` in `B + k*|ARA-phi|` is only a candidate temporal-pocket marker when paired with anti-phase/contact geometry.

## Recent Runnable Tick-Recursion And Coupling Tests

The 2026-05-23 tick-recursion and phi-coupling candidate tests were run locally with cached public data where required.

Useful entry points:

```bash
python TheFormula/ara_formula_tick_engine_test.py
python TheFormula/ara_tick_variable_recursion_test.py
python TheFormula/ara_phi_coupling_candidate_tests.py
python TheFormula/ara_enso_12m_geometry_state_predictor_test.py
python TheFormula/ara_enso_12m_feeder_amplitude_test.py
python TheFormula/ara_enso_12m_boundary_distance_transfer_test.py
```

Outputs:

- `TheFormula/ara_formula_tick_engine_data.js`
- `TheFormula/ara_formula_tick_engine_viz.html`
- `TheFormula/ara_tick_variable_recursion_data.js`
- `TheFormula/ara_phi_coupling_candidate_results.js`
- `TheFormula/ara_phi_coupling_candidate_results.json`
- `TheFormula/ara_enso_12m_geometry_state_predictor_result.js`
- `TheFormula/ara_enso_12m_geometry_state_predictor_result.json`
- `TheFormula/ara_enso_12m_feeder_amplitude_result.js`
- `TheFormula/ara_enso_12m_feeder_amplitude_result.json`
- `TheFormula/ara_enso_12m_boundary_distance_transfer_result.js`
- `TheFormula/ara_enso_12m_boundary_distance_transfer_result.json`
- `ARA_TICK_RECURSION_AND_COUPLING_RESULT.md`

Important interpretation guard: `direct_value_required_variables` is a strict-causal control, not the clean formula. It tests whether current required variables directly regress future value deltas. The cleaner framework test is variable recursion first, then decoding. Results show useful signal but not a solved universal tick operator.

## Recent Runnable Coupled-Geometry Transfer Tests

The 2026-05-23 cross-scale coupled-geometry tests were run locally using cached public data and train/test controls.

Useful entry points:

```bash
python TheFormula/ara_ecg_solar_temporal_geometry_test.py
python TheFormula/ara_nasal_enso_coupled_geometry_test.py
python TheFormula/ara_nasal_to_enso_prediction_test.py
python TheFormula/ara_enso_12m_boundary_distance_transfer_test.py
```

Outputs:

- `TheFormula/ara_ecg_solar_temporal_geometry_result.js`
- `TheFormula/ara_ecg_solar_temporal_geometry_result.json`
- `TheFormula/ara_nasal_enso_coupled_geometry_result.js`
- `TheFormula/ara_nasal_enso_coupled_geometry_result.json`
- `TheFormula/ara_nasal_to_enso_prediction_result.js`
- `TheFormula/ara_nasal_to_enso_prediction_result.json`
- `TheFormula/ara_enso_12m_boundary_distance_transfer_result.js`
- `TheFormula/ara_enso_12m_boundary_distance_transfer_result.json`
- `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`

Important interpretation guard: the nasal/ENSO result supports shared paired anti-phase geometry and a partial transition prior. It does not prove direct causal prediction. Short-horizon ENSO remains persistence-dominated in the corrected forecast run, while the ARA/midpoint-matched transfer is strongest around the 12-month transition window. Boundary-distance transfer improves turn/transition information, but delayed feeder amplitude remains the strongest exact-value 12-month branch in this folder.

## Recent Runnable Geometry Analog-Flow Test

The 2026-05-24 analog-flow predictor test separates the flow operator from the decoder:

```bash
python TheFormula/ara_geometry_analog_flow_predictor.py
```

Outputs:

- `TheFormula/ara_geometry_analog_flow_predictor_result.json`
- `TheFormula/ara_geometry_analog_flow_predictor_result.js`
- `ARA_GEOMETRY_ANALOG_FLOW_RESULT.md`

Important interpretation guard: the oracle future-geometry decoder is diagnostic only. It uses the actual future geometry state and therefore is not a forecast. The strict forecast branch predicts future geometry by similar-state analog flow before decoding. In this run, the decoder ceiling is promising at 12 and 24 months, but the analog flow operator is not strong enough and lag ridge remains the best strict forecast.

The oracle ablation identifies which future geometry fields carry that decoder signal:

```bash
python TheFormula/ara_oracle_geometry_ablation.py
```

Outputs:

- `TheFormula/ara_oracle_geometry_ablation_result.json`
- `TheFormula/ara_oracle_geometry_ablation_result.js`
- `ARA_ORACLE_GEOMETRY_ABLATION_RESULT.md`

Important interpretation guard: this is also diagnostic only. It uses actual future geometry `S(t+h)` to decide which fields are worth predicting in a later strict flow operator. In this run, future NINO phase and SOI phase are strongest alone, while NINO energy/rung context is the most damaging removal from the full decoder.

The targeted strict follow-up predicts only those smaller future-geometry targets and adds geometry velocity/acceleration:

```bash
python TheFormula/ara_targeted_geometry_flow_predictor.py
```

Outputs:

- `TheFormula/ara_targeted_geometry_flow_predictor_result.json`
- `TheFormula/ara_targeted_geometry_flow_predictor_result.js`
- `ARA_TARGETED_GEOMETRY_FLOW_RESULT.md`

Important interpretation guard: this is a strict forecast test, unlike the oracle ablation. It shows partial improvement over whole-state analog flow, especially for future phase, but lag ridge still wins overall MAE.

The focused phase-flow follow-up isolates three transport ideas:

```bash
python TheFormula/ara_phase_flow_predictor.py
```

Outputs:

- `TheFormula/ara_phase_flow_predictor_result.json`
- `TheFormula/ara_phase_flow_predictor_result.js`
- `ARA_PHASE_FLOW_RESULT.md`

Important interpretation guard: this is strict-causal. It finds horizon-specific phase-flow signal but does not beat lag ridge overall. The useful read is architectural: phase flow improves timing/shape, while lag/inertia still carries native-unit amplitude.

The lag/phase hybrid follow-up tests whether the phase-flow branch can improve a lag amplitude prior:

```bash
python TheFormula/ara_lag_phase_hybrid_predictor.py
```

Outputs:

- `TheFormula/ara_lag_phase_hybrid_predictor_result.json`
- `TheFormula/ara_lag_phase_hybrid_predictor_result.js`
- `ARA_LAG_PHASE_HYBRID_RESULT.md`

Important interpretation guard: this is strict-causal, with inner past-only calibration for hybrid weights. The free hybrid does not beat lag ridge on MAE. At 24 months, lag plus regime-velocity phase improves correlation over lag alone, but still worsens MAE. The unconstrained coupling/energy gate overfits, so the next fair version should use a bounded ARA phase-turn correction rather than a free high-dimensional gate.

The trust-gate diagnostic tests whether ARA phase-flow should be used as a confidence/regime warning rather than a value blend:

```bash
python TheFormula/ara_phase_trust_gate_diagnostic.py
```

Outputs:

- `TheFormula/ara_phase_trust_gate_diagnostic_result.json`
- `TheFormula/ara_phase_trust_gate_diagnostic_result.js`
- `ARA_PHASE_TRUST_GATE_DIAGNOSTIC_RESULT.md`

Important interpretation guard: this is strict-causal. The selector for origin `t` only uses previous records whose target is already in the past. In this run, ARA phase should not replace lag when they disagree. The useful signal is narrower: disagreement is a 24-month lag-risk warning, and ARA phase has slight transition turn/boundary skill while still losing on MAE.

The energy/work decomposition diagnostic tests whether lag energy and ARA route geometry align cleanly:

```bash
python TheFormula/ara_energy_work_decomposition_test.py
```

Outputs:

- `TheFormula/ara_energy_work_decomposition_result.json`
- `TheFormula/ara_energy_work_decomposition_result.js`
- `ARA_ENERGY_WORK_DECOMPOSITION_RESULT.md`

Important interpretation guard: this is strict-causal for the base lag/phase forecasts, and the error selector only uses previous completed outcomes. The result supports alignment as a risk diagnostic, especially at 24 months, but does not improve the forecast. The first dissipation/turbulence proxy is not valid yet.

The transition-risk and uncertainty model keeps lag as the central point forecast and predicts risk/interval quantities around it:

```bash
python TheFormula/ara_transition_risk_and_uncertainty_model.py
```

Outputs:

- `TheFormula/ara_transition_risk_and_uncertainty_result.json`
- `TheFormula/ara_transition_risk_and_uncertainty_result.js`
- `ARA_TRANSITION_RISK_AND_UNCERTAINTY_RESULT.md`

Important interpretation guard: this is strict-causal. For origin `t`, risk models train only on previous records whose targets are already known. The risk ranking has useful signal, especially high-error and boundary/event risk, but the first interval-width model undercovers and should not be used as an honest forecast interval yet.

The multi-rung feeder ablation tests whether lower phi-rung information specifically explains medium-horizon lift:

```bash
python TheFormula/ara_multirung_feeder_ablation.py
```

Outputs:

- `TheFormula/ara_multirung_feeder_ablation_result.json`
- `TheFormula/ara_multirung_feeder_ablation_result.js`
- `ARA_MULTIRUNG_FEEDER_ABLATION_RESULT.md`

Important interpretation guard: this is strict-causal. All variants share the same lag/inertia base and home-rung features; only the added lower/upper block changes. In this run, the current lower-phi feeder block does not improve 6/12-month prediction, upper alone does not improve 24 months, and non-phi lower controls are competitive. Treat this as a negative result for the current direct-feature feeder construction.

The cross-rung spin-transfer test checks the subtler version where lower rungs feed by phase/frequency pressure rather than direct amplitude:

```bash
python TheFormula/ara_cross_rung_spin_transfer_test.py
```

Outputs:

- `TheFormula/ara_cross_rung_spin_transfer_result.json`
- `TheFormula/ara_cross_rung_spin_transfer_result.js`
- `ARA_CROSS_RUNG_SPIN_TRANSFER_RESULT.md`

Important interpretation guard: this is strict-causal. The first run exposed a training-window bug and was discarded; the saved result is from the corrected run with pre-test records available for causal training and held-out scoring. It supports the faster-spin claim, but lower-spin features do not yet cleanly improve boundary-risk ranking.

The topographic wavefront formula test turns the rough-terrain idea into a first explicit prediction/risk equation:

```bash
python TheFormula/ara_topographic_wavefront_formula_test.py
```

Outputs:

- `TheFormula/ara_topographic_wavefront_formula_result.json`
- `TheFormula/ara_topographic_wavefront_formula_result.js`
- `ARA_TOPOGRAPHIC_WAVEFRONT_FORMULA_RESULT.md`

Important interpretation guard: this is strict-causal. At origin `t`, the terrain surface, wavefront, lower-rung impulses, upper-rung reservoir, and residual correction all use only information available before the target. The first equation has direction/turn signal but is not yet a successful point predictor: it improves turn accuracy while worsening MAE, so the next version should use the terrain formula as a bounded risk/turn correction rather than a free amplitude decoder.

The no-lag ARA energy-input test removes the lag/inertia predictor and asks whether lower-rung spin energy can move the home wavefront directly:

```bash
python TheFormula/ara_plain_energy_input_wavefront_test.py
```

Outputs:

- `TheFormula/ara_plain_energy_input_wavefront_result.json`
- `TheFormula/ara_plain_energy_input_wavefront_result.js`
- `ARA_PLAIN_ENERGY_INPUT_WAVEFRONT_RESULT.md`

Important interpretation guard: this is strict-causal and uses no lag-only/native lag feature block. The point forecast is still anchored at the current value, but all future deltas come from ARA terrain, lower-spin energy input, upper-reservoir gates, and past-only ARA calibration. In this run, ARA-only energy improves turn activity and boundary ranking, but it does not solve native-unit amplitude at 6/12/24 months.

The raw watershed-slice test avoids smoothed terrain entirely:

```bash
python TheFormula/ara_raw_watershed_slice_test.py
```

Outputs:

- `TheFormula/ara_raw_watershed_slice_result.json`
- `TheFormula/ara_raw_watershed_slice_result.js`
- `ARA_RAW_WATERSHED_SLICE_RESULT.md`

Important interpretation guard: this is strict-causal and uses the raw ENSO dataframe directly. It avoids bandpass, z-score, rolling smoothing, and lag-ridge/native lag feature blocks. The fixed raw formula is still not enough by itself, but the past-only raw watershed decoder beats persistence across 3-24 months. The next required check is a control against generic raw finite-difference predictors.

The corrected raw watershed lower-spin test demotes upper rungs to weak sea/backpressure and makes lower-rung spin torque the primary topology-arrival term:

```bash
python TheFormula/ara_raw_watershed_lower_spin_test.py
```

Outputs:

- `TheFormula/ara_raw_watershed_lower_spin_result.json`
- `TheFormula/ara_raw_watershed_lower_spin_result.js`
- `TheFormula/ara_raw_watershed_lower_spin_viz.html`
- `ARA_RAW_WATERSHED_LOWER_SPIN_RESULT.md`

Important interpretation guard: this is strict-causal and raw-data only. It corrects the mechanism wording from the previous watershed test: lower rungs spin the current terrain, upper rungs provide slow sea/backpressure. The decoder preserves the raw-terrain lift, while the fixed symbolic formula still needs work.

The phase-delay diagnostic for the lower-spin visualiser checks whether the generated wave is systematically late:

```bash
python TheFormula/ara_raw_watershed_phase_delay_diagnostic.py
```

Outputs:

- `TheFormula/ara_raw_watershed_phase_delay_result.json`
- `TheFormula/ara_raw_watershed_phase_delay_result.js`
- `ARA_RAW_WATERSHED_PHASE_DELAY_RESULT.md`

Important interpretation guard: this is diagnostic-only and compares already-generated held-out forecasts against shifted truth. It is not a causal prediction improvement. It confirms that the fixed lower-spin formula mostly matches truth when shifted earlier by the forecast horizon, meaning it carries the current slice forward instead of advancing the topology/contact state.

The terrain-arrival predictor treats the lower-spin formula as a current terrain extractor, then searches older completed terrain signatures for the arriving future surface:

```bash
python TheFormula/ara_terrain_arrival_predictor.py
```

Outputs:

- `TheFormula/ara_terrain_arrival_predictor_result.json`
- `TheFormula/ara_terrain_arrival_predictor_result.js`
- `TheFormula/ara_terrain_arrival_predictor_viz.html`
- `ARA_TERRAIN_ARRIVAL_PREDICTOR_RESULT.md`

Important interpretation guard: this is strict-causal and target-date aligned. Each analog neighbor is eligible only if its own target `s+h` is already before the current origin `t`; no decoder, lag ridge, shifted truth, smoothing, or future geometry oracle is used. The first run is promising, with `terrain_level_analog` beating persistence across the 6/12/24-month focus window, but it still needs controls against generic raw finite-difference and seasonal/ENSO analog recurrence.

The wobble terrain-arrival follow-up adds a local 3-axis terrain frame, recent wobble velocity, curvature, and lower-subsystem spin:

```bash
python TheFormula/ara_wobble_terrain_arrival_predictor.py
```

Outputs:

- `TheFormula/ara_wobble_terrain_arrival_result.json`
- `TheFormula/ara_wobble_terrain_arrival_result.js`
- `TheFormula/ara_wobble_terrain_arrival_viz.html`
- `ARA_WOBBLE_TERRAIN_ARRIVAL_RESULT.md`

Important interpretation guard: this is strict-causal and no-decoder/no-lag-ridge. In the first run, wobble improves the transition/contact side more than broad correlation. Treat wobble as a bounded modifier around contact windows until a stronger distance metric is tested.

The sphere atlas maps the wobble records onto a full ARA sphere:

```bash
python TheFormula/ara_sphere_atlas_from_wobble.py
```

Outputs:

- `TheFormula/ara_sphere_atlas_data.json`
- `TheFormula/ara_sphere_atlas_data.js`
- `TheFormula/ara_sphere_atlas_viz.html`
- `ARA_SPHERE_ATLAS_RESULT.md`

Important interpretation guard: this is a mapping/export tool, not a forecast. It maps ARA as pole-to-pole latitude, phase/degrees as longitude, and local wobble as surface displacement. Use it to inspect where water-slice paths, prediction errors, and transition/contact regions sit on the sphere.

The sphere topology direction test uses that atlas as a causal topology memory:

```bash
python TheFormula/ara_sphere_topology_direction_predictor.py
```

Outputs:

- `TheFormula/ara_sphere_topology_direction_result.json`
- `TheFormula/ara_sphere_topology_direction_result.js`
- `TheFormula/ara_sphere_topology_direction_viz.html`
- `ARA_SPHERE_TOPOLOGY_DIRECTION_RESULT.md`

Important interpretation guard: this is strict-causal and no-decoder/no-lag-ridge. Each sphere neighbour is eligible only when its target `s+h` is already before the current origin `t`; non-ready rows fall back to persistence. In this first pass the sphere atlas contains only held-out visual records, so ready coverage is limited. The useful result is ready-only: nested ARA-band level lookup helps future direction/turn, while raw sphere-delta transport is weaker.

## Recent Runnable Mapping Atlas

The 2026-05-24 mapping-first atlas rebuilds the old temporal-coordinate visualiser as a reusable data export plus local HTML workbench.

Useful entry point:

```bash
python Mapping/galactic_rotation_phi_test.py
python Mapping/galactic_structure_time_phi_test.py
python Mapping/build_mapping_extensions.py
python Mapping/ara_mapping_atlas_build.py
python Mapping/audit_over2_ara_nodes.py
```

Outputs:

- `Mapping/ara_mapping_atlas_data.json`
- `Mapping/ara_mapping_atlas_data.js`
- `Mapping/ara_mapping_atlas_3d.html`
- `Mapping/ara_mapping_extensions.json`
- `Mapping/galactic_rotation_phi_test_result.json`
- `Mapping/galactic_structure_time_phi_test_result.json`
- `Mapping/ara_over2_audit.json`
- `Mapping/ARA_OVER2_AUDIT.md`
- `ARA_MAPPING_ATLAS_RESULT.md`

Important interpretation guard: this is a geometry diagnostic map, not a predictor. It combines hand-curated catalogue nodes, fitted subsystem nodes, and anchor-state geometry nodes, so filters should be used when comparing like with like.

The mapping-extension build currently adds nostril dominance, tides, solar hemispheres, human gait, MJO/QBO, and a 10-system quantum-to-cosmic anchor ladder as a separate `mapped_extension` layer. Run the galactic rotation test first so the Milky Way node uses the measured rotation-curve correction instead of the older archived phi scaffold. Human gait was rerun from raw PhysioNet `gaitndd` records on 2026-05-24 using the local verification venv:

```powershell
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe analysis\gait\analyze_running_phi.py
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe analysis\gait\analyze_gait_phi.py
```

The raw gait rerun requires network access to `physionet.org` plus `numpy`, `scipy`, `matplotlib`, `wfdb`, and `aiohttp` in that venv. Read the PhysioNet medians as controlled instructed-walk geometry; the natural locomotion crossover anchors are taken from `analysis\gait\analyze_running_phi.py`.

The cross-scale anchor ladder is drawn mostly from older archive scripts (`archive\numbered_tests\92_subatomic_slope_inversion.py`, `archive\numbered_tests\94_real_ara_measurements.py`, `archive\numbered_tests\89_gap_filling_scales.py`, and `archive\numbered_tests\64_sleep_consciousness_ara.py`). Treat it as a mapping scaffold, not a new independent measurement pass. Exception: the Milky Way galactic-rotation node now uses `Mapping\galactic_rotation_phi_test_result.json`; that test supports the rough period anchor but rejects the archived phi ARA assignment, so the circular carrier is mapped at ARA `1.0`.

The galactic structure-time follow-up uses `Mapping\galactic_structure_time_phi_test_result.json`. It does not change the carrier ARA. It records that a four-arm spiral crossing becomes `P_orb / phi` at `Omega_pattern = 16.61 km/s/kpc`, close to the slow density-wave `12..17 km/s/kpc` range, while bar-pattern central values remain sub-phi.

ATP synthase is currently taken from the ATP-specific chemical-oscillator rerun:

```powershell
$env:PYTHONIOENCODING='utf-8'
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe archive\numbered_tests\50_chemical_oscillators_ara.py
```

That rerun maps ATP synthase at ARA `1.50`. The earlier hard-coded rotor/gradient child nodes have been removed. Testing that coupled-subsystem idea requires real single-molecule substep dwell-time data.

The triangle overlay is included in the same build output. It detects low-ARA fitted event nodes near named state-rung clusters, plus K2/K4 endpoint faces that pass through K3 as a bridge/gate rung. Both are exposed behind the `Triangles` toggle in `ara_mapping_atlas_3d.html`.

The above-2 audit is a guardrail pass for the bounded ARA convention. It currently reports `45` nodes over `2.0`, all in the older hand-curated `catalog` layer. No over-2 nodes are introduced by the newer measured-fit, state-geometry, or mapped-extension layers. Treat those older entries as diagnostic overflow until source-specific retests decide whether they are reversed orientation, rung mismatch, compound/coupled systems, or one-shot storage/release ratios.
