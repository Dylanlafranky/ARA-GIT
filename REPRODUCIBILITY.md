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
