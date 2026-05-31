# ARA Framework — Index

**Last updated: May 2026**

---

## What this is, in one paragraph

This is an open research notebook about a geometric hypothesis for oscillating systems. A heartbeat, a climate cycle, a planetary orbit, the firing of a neuron — the framework asks whether they can be mapped onto a shared φ-spaced ladder of timescales. Each system can be read as a small set of coordinates: period, amplitude, phase, and a build-vs-release ratio (ARA) per rung of the ladder. A single forward formula — anchored at the most recent observed value, integrating contributions across rungs — is being tested as a way to track or forecast behaviour from those coordinates. Existing physics provides the language: bandpass decomposition, coupled oscillators, scaling laws, and time-as-primary. The big interpretation is speculative; the useful question for reviewers is whether the φ-rung coordinate system carries real signal beyond simpler baselines.

I'm not a scientist by training. I built this in spare time, with significant help from AI collaborators. I report what I find — including the misses — and invite people in the relevant fields to check, improve, or knock down what I have wrong.

The repository has three working folders, one per question the framework asks of any cycling system: **`Mapping/`** — *where* a system sits on the ARA scale (what kind of cycle it is); **`TheFormula/`** — can it be *forecast* from a few geometric constants; **`EnergyRatio/`** — how *efficiently* it moves energy/information per cycle (the leanness / entropy-budget side, e.g. the golden-star result below).

For the public-release audit, start with [`CLAIMS_STATUS.md`](CLAIMS_STATUS.md) and [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md). They list the claims I would quote carefully and the scripts that still need cleanup. The φ-vs-nearby-bases predictor ablation has now had a first-pass run; see [`PHI_BASE_ABLATION.md`](PHI_BASE_ABLATION.md) — φ wins at h=1, 3, 6 months among the eight tested bases on ENSO, but the whole predictor family underperforms persistence at every horizon, so the test is a partial-evidence result rather than a clean win for φ specifically.

The first ARA state-geometry and transport test is recorded in [`ARA_GEOMETRY_TRANSPORT_RESULT.md`](ARA_GEOMETRY_TRANSPORT_RESULT.md). Short version: the geometry map carries ENSO signal over persistence, especially around 6-24 months, but direct value-transport still loses to a simple causal lag baseline.

The latest temporal-flow follow-up is recorded in [`ARA_TEMPORAL_FRICTION_RESULT.md`](ARA_TEMPORAL_FRICTION_RESULT.md). Short version: phi-distance is not temporal friction by itself; it appears to modulate a baseline friction floor, while negative coefficients may mark resonance-cancellation pockets only when anti-phase/contact geometry is also present.

The latest tick-recursion follow-up is recorded in [`ARA_TICK_RECURSION_AND_COUPLING_RESULT.md`](ARA_TICK_RECURSION_AND_COUPLING_RESULT.md). Short version: actual future ARA/formula variables decode observables strongly, and energy-aware tick recursion often beats persistence, but the strict lawful tick operator is not yet strong enough to replace lag/direct controls.

The latest cross-scale coupled-pair test is recorded in [`ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`](ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md). Short version: nasal-cycle dominance and ENSO NINO/SOI dynamics share strong paired anti-phase geometry, especially in dominance-interval form. Using nasal geometry as an external ENSO forecast prior helps most around the 12-month transition window. Delayed lower-rung feeder amplitude remains the strongest exact-value result in this branch so far, while boundary-distance transfer improves transition/turn information but does not solve prediction.

The latest analog-flow predictor test is recorded in [`ARA_GEOMETRY_ANALOG_FLOW_RESULT.md`](ARA_GEOMETRY_ANALOG_FLOW_RESULT.md). Short version: separating the decoder is useful. Actual future geometry decodes NINO strongly at 12 and 24 months, but the strict similar-state analog flow does not yet estimate that future geometry well enough. The bottleneck is future geometry flow, not geometry-to-native decoding.

The follow-up oracle ablation is recorded in [`ARA_ORACLE_GEOMETRY_ABLATION_RESULT.md`](ARA_ORACLE_GEOMETRY_ABLATION_RESULT.md). Short version: future NINO phase and SOI phase carry most of the decoder signal by themselves; NINO energy/rung is the most important companion field in the full decoder. The next flow operator should predict these smaller geometry targets instead of the full state vector.

The targeted flow test is recorded in [`ARA_TARGETED_GEOMETRY_FLOW_RESULT.md`](ARA_TARGETED_GEOMETRY_FLOW_RESULT.md). Short version: predicting future NINO/SOI phase is much better than whole-state analog flow and beats raw analog correlation at 12 months, but lag ridge still wins MAE. Phase should probably be the primary flow variable, with energy/rung/coupling used as gates rather than equally predicted coordinates.

The focused phase-flow test is recorded in [`ARA_PHASE_FLOW_RESULT.md`](ARA_PHASE_FLOW_RESULT.md). Short version: regime gating helps most at 6 months, velocity helps at 12 months, and regime+velocity is best at 24 months, where it beats lag ridge on correlation but not MAE. This points toward a hybrid model: lag/inertia for amplitude, phase flow for timing, and ARA coupling/energy as the gate.

The lag/phase hybrid test is recorded in [`ARA_LAG_PHASE_HYBRID_RESULT.md`](ARA_LAG_PHASE_HYBRID_RESULT.md). Short version: the free learned hybrid does not beat lag ridge on MAE, and the unconstrained coupling/energy gate overfits badly. At 24 months, lag plus regime-velocity phase improves correlation over lag alone, but still worsens MAE. The next version should be constrained: lag amplitude plus a bounded, monotonic ARA phase-turn correction.

The trust-gate follow-up is recorded in [`ARA_PHASE_TRUST_GATE_DIAGNOSTIC_RESULT.md`](ARA_PHASE_TRUST_GATE_DIAGNOSTIC_RESULT.md). Short version: when lag and ARA phase-flow disagree, lag is still usually the better point forecast. But at 24 months, disagreement sharply raises the chance that lag gets the turn wrong, and ARA phase is slightly better on transition turn/boundary accuracy while still worse on MAE. ARA should be treated first as an uncertainty and boundary-warning channel, not as the central amplitude forecast.

The energy/work decomposition test is recorded in [`ARA_ENERGY_WORK_DECOMPOSITION_RESULT.md`](ARA_ENERGY_WORK_DECOMPOSITION_RESULT.md). Short version: energy-route alignment is a real risk diagnostic, especially at 24 months, but the first work/error selector and dissipation proxy do not improve the forecast. Lag remains the point forecast, ARA phase remains the route/boundary channel, and the missing piece is still the energy-to-work conversion rule.

The transition-risk and uncertainty test is recorded in [`ARA_TRANSITION_RISK_AND_UNCERTAINTY_RESULT.md`](ARA_TRANSITION_RISK_AND_UNCERTAINTY_RESULT.md). Short version: ARA/work features are more useful as a risk layer than as a point forecast. They show lift for lag high-error, turn-failure, and boundary/event warnings, especially 6-month high-error and 6-24 month boundary-crossing risk. The first interval-width model undercovers badly, so uncertainty calibration is still unsolved.

The multi-rung feeder ablation is recorded in [`ARA_MULTIRUNG_FEEDER_ABLATION_RESULT.md`](ARA_MULTIRUNG_FEEDER_ABLATION_RESULT.md). Short version: the current lower-phi feeder block does not explain medium-horizon gains. It worsens 6/12-month MAE and correlation versus home-only, upper alone does not improve 24 months, and the non-phi lower control does better at 18/60 months. The next version should test delayed lower-feeder residual/risk lift rather than direct high-dimensional value features.

The cross-rung spin-transfer test is recorded in [`ARA_CROSS_RUNG_SPIN_TRANSFER_RESULT.md`](ARA_CROSS_RUNG_SPIN_TRANSFER_RESULT.md). Short version: the faster-spin claim is strongly supported, with lower > home > upper phase-turn rates for NINO, SOI, and PDO. The lower-spin block does not cleanly improve boundary-risk ranking, but upper/envelope features carry clearer boundary/event signal, and lower-home opposition marks turn/timing risk rather than amplitude error.

The first topographic wavefront formula test is recorded in [`ARA_TOPOGRAPHIC_WAVEFRONT_FORMULA_RESULT.md`](ARA_TOPOGRAPHIC_WAVEFRONT_FORMULA_RESULT.md). Short version: yes, the rough-terrain idea can be turned into an explicit formula. The first equation carries directional/turn signal, but it is not yet a successful point predictor: across 6/12/24 months, lag+terrain improves turn accuracy while worsening MAE and transition MAE. The next version should be a bounded geometry/risk correction around lag, not a free residual decoder.

The no-lag ARA energy-input test is recorded in [`ARA_PLAIN_ENERGY_INPUT_WAVEFRONT_RESULT.md`](ARA_PLAIN_ENERGY_INPUT_WAVEFRONT_RESULT.md). Short version: removing lag confirms the geometry is active but not yet amplitude-accurate. ARA-only lower-spin energy improves turn activity sharply and gives useful boundary ranking, especially at 12 and 24 months, but the 6/12/24 point forecast still loses to persistence on MAE.

The raw watershed-slice test is recorded in [`ARA_RAW_WATERSHED_SLICE_RESULT.md`](ARA_RAW_WATERSHED_SLICE_RESULT.md). Short version: preserving the jagged raw terrain works much better than the smoothed/bandpass terrain formula. The fixed raw watershed formula still does not solve amplitude, but the past-only raw watershed decoder beats persistence across 3-24 months and reaches 6/12/24 focus MAE 0.628 versus persistence 0.896. This now needs controls against generic raw finite-difference predictors.

The corrected lower-spin watershed test is recorded in [`ARA_RAW_WATERSHED_LOWER_SPIN_RESULT.md`](ARA_RAW_WATERSHED_LOWER_SPIN_RESULT.md), with overlay visualiser [`TheFormula/ara_raw_watershed_lower_spin_viz.html`](TheFormula/ara_raw_watershed_lower_spin_viz.html). Short version: lower rungs are now treated as fast tributary torque that spins the current terrain, while upper rungs are weak sea/backpressure. The past-only decoder stays strong (6/12/24 MAE 0.633 vs persistence 0.896), and lower-spin torque/topology-arrival rank transition and high-error pressure, but the fixed symbolic formula still does not solve amplitude.

The raw watershed phase-delay diagnostic is recorded in [`ARA_RAW_WATERSHED_PHASE_DELAY_RESULT.md`](ARA_RAW_WATERSHED_PHASE_DELAY_RESULT.md). Short version: the fixed lower-spin formula has decent shape but is mostly late by the forecast horizon: best visual correlation occurs at `-3/-6/-12/-18/-24` months for 3/6/12/18/24-month horizons. That means it is mostly carrying the origin water slice forward rather than advancing the topology/contact state.

The terrain-arrival predictor is recorded in [`ARA_TERRAIN_ARRIVAL_PREDICTOR_RESULT.md`](ARA_TERRAIN_ARRIVAL_PREDICTOR_RESULT.md), with forecast-valid visualiser [`TheFormula/ara_terrain_arrival_predictor_viz.html`](TheFormula/ara_terrain_arrival_predictor_viz.html). Short version: treating the lower-spin formula as a current terrain extractor, then matching older completed terrain signatures, gives a no-decoder recurrence predictor. Across 6/12/24 months, `terrain_level_analog` reaches MAE 0.602, corr +0.275, turn accuracy 0.769, and transition MAE 0.674 versus persistence MAE 0.896.

The wobble terrain-arrival follow-up is recorded in [`ARA_WOBBLE_TERRAIN_ARRIVAL_RESULT.md`](ARA_WOBBLE_TERRAIN_ARRIVAL_RESULT.md), with visualiser [`TheFormula/ara_wobble_terrain_arrival_viz.html`](TheFormula/ara_wobble_terrain_arrival_viz.html). Short version: adding local 3-axis wobble improves turn/contact behaviour more than broad correlation. Across 6/12/24 months, `wobble_surface_analog` reaches MAE 0.608, corr +0.218, turn accuracy 0.773, and transition MAE 0.658.

The full-sphere mapping workbench is recorded in [`ARA_SPHERE_ATLAS_RESULT.md`](ARA_SPHERE_ATLAS_RESULT.md), with visualiser [`TheFormula/ara_sphere_atlas_viz.html`](TheFormula/ara_sphere_atlas_viz.html). Short version: ARA is mapped pole-to-pole from 0 to 2, phase/degrees become longitude, and wobble displaces the local terrain surface. The held-out ENSO water-slice spans ARA 0.188 to 1.937, covering most of the sphere.

The sphere topology direction test is recorded in [`ARA_SPHERE_TOPOLOGY_DIRECTION_RESULT.md`](ARA_SPHERE_TOPOLOGY_DIRECTION_RESULT.md), with visualiser [`TheFormula/ara_sphere_topology_direction_viz.html`](TheFormula/ara_sphere_topology_direction_viz.html). Short version: using the sphere as a causal topology memory works better as a future-level/direction prior than as a raw delta transporter. On ready rows across 6/12/24 months, the nested-2 sphere-level lookup reaches MAE 0.649, turn accuracy 0.754, direction 0.762, and large-direction 0.799. Two ARA-in-ARA layers help slightly; the third layer over-localises in this pass.

The contact-triangle roll test is recorded in [`ARA_CONTACT_TRIANGLE_ROLL_RESULT.md`](ARA_CONTACT_TRIANGLE_ROLL_RESULT.md), with visualiser [`TheFormula/ara_contact_triangle_roll_viz.html`](TheFormula/ara_contact_triangle_roll_viz.html). Short version: the filter/sand-layer idea can be formalised as lower-to-home parity, home-to-upper parity, and local triangle compactness/handedness. The first metric carries ready-row correlation, but it does not beat the simpler wobble/sphere terrain lookup. Treat contact triangles as a future gate/constraint selector, not the main route engine yet.

The rotating-terrain slice test is recorded in [`ARA_ROTATING_TERRAIN_SLICE_RESULT.md`](ARA_ROTATING_TERRAIN_SLICE_RESULT.md), with visualiser [`TheFormula/ara_rotating_terrain_slice_viz.html`](TheFormula/ara_rotating_terrain_slice_viz.html). Short version: this is the first explicit fixed-slice / moving-terrain implementation. It estimates the patch arriving under the water slice and samples older surface/target patches. Ready-row direction remains high, but MAE/correlation do not beat the simpler wobble/sphere terrain lookup, so the hand-coded rotation operator is not accurate enough yet.

The sphere-orientation roll test is recorded in [`ARA_SPHERE_ORIENTATION_ROLL_RESULT.md`](ARA_SPHERE_ORIENTATION_ROLL_RESULT.md), with visualiser [`TheFormula/ara_sphere_orientation_roll_viz.html`](TheFormula/ara_sphere_orientation_roll_viz.html). Short version: pose is now represented as a 3D surface vector, roll as a 3D angular vector, and the learned branch predicts future orientation before sampling the fixed terrain surface. On ready rows, learned orientation beats the previous sphere nested-2 lookup, but still trails direct wobble terrain matching.

The raw terrain-address lookup is recorded in [`ARA_RAW_TERRAIN_ADDRESS_LOOKUP_RESULT.md`](ARA_RAW_TERRAIN_ADDRESS_LOOKUP_RESULT.md), with visualiser [`TheFormula/ara_raw_terrain_address_lookup_viz.html`](TheFormula/ara_raw_terrain_address_lookup_viz.html). Short version: the amplitude concern was valid. Replacing the many-neighbour averaged roll with a top-1 raw terrain address improves ready-row 6/12/24 correlation from **+0.254** to **+0.361** and amplitude ratio from **0.792** to **0.841**, at a small MAE cost. The next bottleneck is address precision, not whether raw terrain preserves amplitude.

The fractal sphere-terrain reader is recorded in [`ARA_FRACTAL_SPHERE_TERRAIN_READER_RESULT.md`](ARA_FRACTAL_SPHERE_TERRAIN_READER_RESULT.md), with visualiser [`TheFormula/ara_fractal_sphere_terrain_reader_viz.html`](TheFormula/ara_fractal_sphere_terrain_reader_viz.html). Short version: filling the sphere with recursive ARA/sub-ARA bands and local in-bounds phi valleys is now implemented. It preserves amplitude, but this first deterministic phi-valley rule does not beat raw top-1 or wobble. Use it as an explanatory/gating layer until the active basin/depth selector is better.

The roll-displacement mode test is recorded in [`ARA_ROLL_DISPLACEMENT_MODE_RESULT.md`](ARA_ROLL_DISPLACEMENT_MODE_RESULT.md), with visualiser [`TheFormula/ara_roll_displacement_mode_viz.html`](TheFormula/ara_roll_displacement_mode_viz.html). Short version: explicit roll displacement removes the persistence-like under-movement, but the coarse mode selector picks the wrong route too often. Ready-row amplitude ratio rises to about **1.0**, while MAE/correlation worsen. The bottleneck has shifted from "not enough roll" to "wrong roll mode."

The lower-sphere roll-selector test is recorded in [`ARA_LOWER_SPHERE_ROLL_SELECTOR_RESULT.md`](ARA_LOWER_SPHERE_ROLL_SELECTOR_RESULT.md), with visualiser [`TheFormula/ara_lower_sphere_roll_selector_viz.html`](TheFormula/ara_lower_sphere_roll_selector_viz.html). Short version: lower-sphere spin patterns are a better roll selector than broad state similarity. Ready-row `lower_core_top1` improves the failed displacement branch from MAE **0.919** / corr **+0.082** / direction **0.660** to MAE **0.744** / corr **+0.194** / direction **0.753**, while retaining amplitude ratio **0.929**. It still does not beat raw top-1, so the lower contact map is not precise enough yet.

The full layered-sand formula is recorded in [`ARA_LAYERED_SAND_FULL_FORMULA_RESULT.md`](ARA_LAYERED_SAND_FULL_FORMULA_RESULT.md), with visualiser [`TheFormula/ara_layered_sand_full_formula_viz.html`](TheFormula/ara_layered_sand_full_formula_viz.html). Short version: the whole proposed mechanism is now encoded in one deterministic formula: moving floor, fast lower grains, alternating rolling contact, two-contact wobble, recursive ARA terrain per layer, upper compression, and measured-sphere terrain arrival. It is strict-causal and no-lag, but it still under-rolls the measured sphere. Across 6/12/24 months, `layered_fractal` reaches MAE **0.882**, corr **+0.013**, direction **0.544**, and amplitude ratio **0.203** versus persistence MAE **0.896**. The missing law is the contact-pressure-to-roll-distance conversion, not the presence of the topology pieces.

The cleaned single-formula version is recorded in [`ARA_LAYERED_SAND_SINGLE_FORMULA_RESULT.md`](ARA_LAYERED_SAND_SINGLE_FORMULA_RESULT.md), with adjustable visualiser [`TheFormula/ara_layered_sand_formula_adjustable_viz.html`](TheFormula/ara_layered_sand_formula_adjustable_viz.html). Short version: `Formula` is now one deterministic cascade, while `Formula_Adjustable` is a parameter-exposed copy of that same cascade. Persistence and older wobble/raw-address traces are labelled as baseline/legacy overlays only and are not formula inputs. Across 6/12/24 months, fixed `Formula` reaches MAE **0.879**, corr **+0.015**, direction **0.523**, and amplitude ratio **0.158**.

The first parameter search for that formula is recorded in [`ARA_LAYERED_SAND_PARAMETER_SEARCH_RESULT.md`](ARA_LAYERED_SAND_PARAMETER_SEARCH_RESULT.md). Short version: fitting `Formula_Adjustable` on pre-2017 ENSO 6/12/24-month rows improves the same formula on 2017+ holdout rows from MAE **0.856** to **0.741**, direction **0.505** to **0.720**, and amplitude ratio **0.143** to **0.905**. It restores amplitude without persistence/lag/legacy inputs, but 6m and 24m holdout correlations remain weak, so these are calibrated candidate constants, not universal constants yet.

The shape/timing diagnostic for the layered formula is recorded in [`ARA_LAYERED_SAND_SHAPE_TIMING_DIAGNOSTIC_RESULT.md`](ARA_LAYERED_SAND_SHAPE_TIMING_DIAGNOSTIC_RESULT.md). Short version: the fixed `Formula` has poor zero-shift correlation across 6/12/24 months (**+0.020**), but best-lag correlation jumps to **+0.545** with a +24-month formula-late shift. By horizon, the best shifts are exactly horizon-sized: 6m -> +6m (**corr +0.977**), 12m -> +12m (**+0.978**), and 24m -> +24m (**+0.978**). Follow-up audit corrected the interpretation: fixed `Formula` is also highly correlated with current NINO (**+0.978** on holdout), so this is a strong terrain/current-state map diagnostic, not a forecast result.

The strict advance-operator follow-up is recorded in [`ARA_LAYERED_SAND_ADVANCE_OPERATOR_RESULT.md`](ARA_LAYERED_SAND_ADVANCE_OPERATOR_RESULT.md), with updated overlays in [`TheFormula/ara_layered_sand_formula_adjustable_viz.html`](TheFormula/ara_layered_sand_formula_adjustable_viz.html). Short version: the red future-origin shift oracle reaches holdout corr **+0.983**, but it leaks future current terrain and is labelled as such. The best non-leaky advance so far is `Advance_Phase_Read`, improving fitted holdout MAE from **0.741** to **0.701** and corr from **+0.018** to **+0.149**. Lower-layer roll variants preserve amplitude but often choose the wrong route, so the next bottleneck is lower-spin roll-direction selection.

The correlation-only variable search is recorded in [`ARA_LAYERED_SAND_CORRELATION_SEARCH_RESULT.md`](ARA_LAYERED_SAND_CORRELATION_SEARCH_RESULT.md). Short version: fitting all formula and advance sliders for correlation on pre-2017 rows, then testing 2017+ holdout, again selects `Advance_Phase_Read` as best. Holdout correlation improves to **+0.204** with MAE **0.632** and direction **0.806**. This is still far below the leakage diagnostic, so the future-origin terrain match has not been reproduced causally.

The closed cutoff correction is recorded in [`ARA_LAYERED_SAND_CLOSED_CUTOFF_RESULT.md`](ARA_LAYERED_SAND_CLOSED_CUTOFF_RESULT.md), with visualiser [`TheFormula/ara_layered_sand_closed_cutoff_viz.html`](TheFormula/ara_layered_sand_closed_cutoff_viz.html). Short version: the prior shifted-line branch was a future-indexed terrain/nowcast generator, not an autonomous predictor. In the closed run, observed NINO/SOI/PDO stop at the cutoff and the formula generates future values internally. The near-perfect shifted match disappears; some presets beat flat persistence on some cutoffs, but the closed predictor is not solved.

The fixed sphere-atlas rotation correction is recorded in [`ARA_FIXED_SPHERE_ATLAS_ROTATION_RESULT.md`](ARA_FIXED_SPHERE_ATLAS_ROTATION_RESULT.md), with visualiser [`TheFormula/ara_fixed_sphere_atlas_rotation_viz.html`](TheFormula/ara_fixed_sphere_atlas_rotation_viz.html). Short version: this finally does the intended non-leaky operation with the existing atlas: current/cutoff pose -> rotate to future sphere address -> raw top-1 past-atlas terrain read -> score afterward. The high shifted-line match does not survive. The existing sphere atlas is a historical point-cloud, not a dense recursive ARA/sub-ARA globe, so the next correction is to extend this same atlas with filled recursive terrain metadata rather than treating sparse historical nearest-neighbour lookup as the full terrain.

The recursive sphere-grid correction is recorded in [`ARA_RECURSIVE_SPHERE_GRID_RESULT.md`](ARA_RECURSIVE_SPHERE_GRID_RESULT.md), with visualiser [`TheFormula/ara_recursive_sphere_grid_viz.html`](TheFormula/ara_recursive_sphere_grid_viz.html). Short version: this removes the layered-sand "now formula" from the predictor. The measured sphere coordinate is rotated forward; if a close past coordinate exists, raw top-1 terrain is read; otherwise the coordinate is filled by recursive ARA/sub-ARA/sub-sub-ARA bands with phi valleys, anti-phi counterlines, midlines, and phi-log depth weights. It improves MAE over persistence at 3/6/12/18 months, but does not yet solve 12-24 month route correlation, so the remaining bottleneck is future coordinate/roll selection.

The layered-sand topological formula correction is recorded in [`ARA_LAYERED_SAND_TOPOLOGICAL_FORMULA_RESULT.md`](ARA_LAYERED_SAND_TOPOLOGICAL_FORMULA_RESULT.md), with visualiser [`TheFormula/ara_layered_sand_topological_formula_viz.html`](TheFormula/ara_layered_sand_topological_formula_viz.html). Short version: this corrects the over-correction above. The layered-sand formula remains the roll/arrival mechanism, but the per-sphere terrain reader now uses the recursive ARA/sub-ARA phi/anti-phi topology. The first scalar topology branch was still a now-machine (`corr_with_current` about +0.987). The new true sphere-rotation branch rotates the current point by the layered roll vector before reading terrain; it is worse at short horizons but improves 24-month ENSO to MAE 0.785, corr +0.197 versus persistence MAE 1.027, corr -0.274.

The current mapping-first atlas is recorded in [`ARA_MAPPING_ATLAS_RESULT.md`](ARA_MAPPING_ATLAS_RESULT.md). It rebuilds the old temporal-coordinate visualiser as a reusable 3D diagnostic workbench with 234 nodes across the original catalogue, measured fitted rungs, current state-geometry rungs, and the mapped-extension layer. This is not a predictor; it is the place to map more systems and diagnose rings, boundaries, and relation classes. The Milky Way galactic-rotation correction is included there: the period anchor survives, but the archived phi ARA assignment does not.

The same mapping pass now includes an above-2 ARA audit in [`Mapping/ARA_OVER2_AUDIT.md`](Mapping/ARA_OVER2_AUDIT.md). It found 45 above-2 nodes, all from the older hand-curated catalogue layer; the newer measured-fit, state-geometry, and mapped-extension layers currently have no above-2 leakage.

The interactive comparison surface for this latest formula branch is [`TheFormula/ara_temporal_interaction_formula_viz.html`](TheFormula/ara_temporal_interaction_formula_viz.html). It overlays truth, persistence, the strict-causal friction decoders, and an experimental integrated gate trace for ENSO, Solar, and ECG.

---

## The framework in 30 seconds

**Topology coordinates.** Any oscillating system at any moment can be described as:
- `v_now` — the most recent observed value
- A list of pinned φ-rungs, each with `(period, amplitude, phase, ARA)`
- A `home_k` — the rung where the system naturally lives

**ARA scale (0 to 2).** ARA = build-time / release-time. A position on the space-time spectrum:
- 0 → pure space singularity (point/void, no dynamics)
- ~1.0 → balance point (atomic clocks, pure randomness — both arrive here)
- φ ≈ 1.618 → engine zone (self-sustaining systems)
- 1.75 → operational maximum, energy-donor systems sit here (e.g. solar magnetic cycle)
- 2.0 → pure time singularity (heat death, no structure)

**Three rung relations:**
- *Below* (faster): substrate that maintains the system
- *Same rung* (matched anti-phase pair): coupled exchange (NINO ↔ SOI, atria ↔ ventricles)
- *Above* (slower): energy donor that drives everything below

**Forward predictor.** Two regimes blended by a sigmoid at `h = home_period × φ^(±7/4)`:
- Short lead: anchor at v_now, integrate δ-contributions across rungs
- Long lead: structured wave from training mean, weighted by rung distance from home

The predictor is one Python file: [`ara_framework.py`](ara_framework.py).

---

## Findings by confidence

### Supported So Far / Needs Independent Replication

These are the findings that survived at least one stricter check after an earlier acausal-bandpass leakage was caught and corrected. They should be read as promising saved results, not as independent confirmations.

| Finding | Headline number | Source |
|---|---|---|
| **Canonical predictor: ENSO 1-month forecast** | Saved output: MAE about **0.28 C**, corr about **+0.90**; persistence skill caveat | `TheFormula/canonical_benchmark_data.js` |
| **Canonical predictor: ECG short-horizon forecast** | Saved output shows useful single-subject signal; best h=3 near corr **+0.96**, MAE about **35 ms** | `TheFormula/canonical_benchmark_data.js` |
| **Cross-species decomposition: mouse topology × human energy → 58% MAE drop** | **MAE 82.22 ms → 34.29 ms (2.4× better) vs naive cross-species transfer. Correlation stays at chance level (consistent with "shared map, not shared position" rule).** | 2026-05-12 test, `framework_energy_cascade_architecture.md` |
| **Cross-mammalian local cycle shape match** | Some high pairwise matches; broad mean is sensitive to normalization and should be rerun | `TheFormula/multispecies_vertical_ara_data.js` |
| **ECG ↔ ENSO local profile match** | corr +0.695 across 38 orders of φ in time | (prior work, this repo) |
| **Walker Circulation is fractal across rungs** | SOI mirrors NINO anti-phase from φ⁵ to φ¹¹ with \|corr\| ≥ 0.85 | (memory: dynamic_rung_assignment) |
| **Lag-h corrector ports cross-domain** | γ ≈ +1/φ. 37% MAE drop at 1-min ECG, 17% at 24-month ENSO | (memory: corrector_cross_domain) |
| **ARA state geometry maps ENSO subsystem structure** | 2026-05-21 snapshot: NINO/SOI center distance **0.116** in ARA-position space; PDO is about one rung away. Geometry-only transport beats persistence at 3-24 months but does not beat causal lag ridge. | `ARA_GEOMETRY_TRANSPORT_RESULT.md`, `TheFormula/ara_state_geometry_data.js`, `TheFormula/ara_geometry_transport_data.js` |
| **Temporal friction is baseline plus modulation, not simple phi-distance** | 2026-05-23 tests: pure `|ARA-phi|` friction failed; `1 + |ARA-phi|` helped some horizons; negative-k pocket markers were supported for Solar 132-month and ECG 60-second windows but not ENSO. | `ARA_TEMPORAL_FRICTION_RESULT.md`, `TheFormula/ara_phi_distance_bk_fit_data.js`, `TheFormula/ara_temporal_pocket_diagnostic_data.js` |
| **Future ARA variables decode observables strongly, but tick flow is the bottleneck** | 2026-05-23 tick recursion: energy-aware variable recursion beats persistence on ENSO 1-60 months and Solar 6/24/60 months, but lag/direct controls still win several horizons. Oracle future-variable decoder is diagnostic only. | `ARA_TICK_RECURSION_AND_COUPLING_RESULT.md`, `TheFormula/ara_tick_variable_recursion_data.js`, `TheFormula/ara_formula_tick_engine_data.js` |
| **Phi-coupling speed signatures are mixed** | Solar north/south relaxation is the cleanest candidate: fractional toward-balance per cycle **1.619** and heldout MAE lift. Heart/respiration is weak; tides show amplitude breathing but not model lift. | `ARA_TICK_RECURSION_AND_COUPLING_RESULT.md`, `TheFormula/ara_phi_coupling_candidate_results.js` |
| **Paired anti-phase systems share cross-scale coupled geometry** | 2026-05-23 nasal-cycle vs ENSO test: dominance-interval heldout corr **+0.992**, signed-cycle heldout corr **+0.980**, both null rank **1/9**. Strongest claim is relation-class matching, not direct causation. | `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`, `TheFormula/ara_nasal_enso_coupled_geometry_result.js` |
| **External coupled geometry can act as a transition prior** | 2026-05-23 nasal -> ENSO transfer: ARA/midpoint matching is best at **12 months** (MAE **0.739** vs persistence **0.946**) but short horizons remain persistence-dominated and long horizons still need local feeder/amplitude state. | `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`, `TheFormula/ara_nasal_to_enso_prediction_result.js` |
| **12-month future-state decoding did not lift ENSO correlation** | Follow-up test: future-state full/local decoders reached only corr **+0.174/+0.198**; lag-only ridge narrowly won corr **+0.205** and old nasal ARA/midpoint stayed best MAE **0.739**. Bottleneck is future sign and magnitude. | `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`, `TheFormula/ara_enso_12m_geometry_state_predictor_result.js` |
| **Delayed below-rung feeder amplitude improves the 12-month ENSO transfer** | Aggregate delayed feeder sign/amplitude gate improved to MAE **0.666**, corr **+0.354**, turn accuracy **0.593**. This supports the feeder-amplitude idea but is still far from high-correlation prediction. | `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`, `TheFormula/ara_enso_12m_feeder_amplitude_result.js` |
| **Boundary-distance transfer improves transition information but not exact prediction** | 2026-05-23 boundary test: aggregate boundary direct control reached MAE **0.688**, corr **+0.263**, turn accuracy **0.636**. It improves over the old nasal prior but remains behind delayed feeder amplitude on MAE/correlation. | `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`, `TheFormula/ara_enso_12m_boundary_distance_transfer_result.js` |
| **Geometry decoder is useful, but analog flow is not enough yet** | 2026-05-24 analog-flow test: oracle future geometry decodes NINO at 12 months with MAE **0.630**, corr **+0.669**, and at 24 months with MAE **0.579**, corr **+0.765**. Strict current-geometry analog flow underperforms lag ridge, so the unsolved piece is predicting future geometry state. | `ARA_GEOMETRY_ANALOG_FLOW_RESULT.md`, `TheFormula/ara_geometry_analog_flow_predictor_result.json` |
| **Oracle geometry signal is concentrated in phase plus energy/rung context** | 2026-05-24 ablation: at 6/12/24 months, future `nino_phase` alone gives mean corr **+0.622**, `soi_phase` **+0.608**. Removing `nino_energy_rung` damages the full decoder most: corr drop **+0.062**, MAE increase **+0.082**. | `ARA_ORACLE_GEOMETRY_ABLATION_RESULT.md`, `TheFormula/ara_oracle_geometry_ablation_result.json` |
| **Targeted future-phase flow partly works, but lag still wins** | 2026-05-24 targeted flow test: across 6/12/24 months, phase-only geometry flow reached MAE **0.747**, corr **+0.221**, direction **0.715**, beating raw analog correlation but not lag ridge MAE **0.623**, corr **+0.283**. At 24 months selected geometry flow had higher corr than lag (**+0.245** vs **+0.167**) but worse MAE. | `ARA_TARGETED_GEOMETRY_FLOW_RESULT.md`, `TheFormula/ara_targeted_geometry_flow_predictor_result.json` |
| **Focused phase flow identifies horizon-specific transport pieces** | 2026-05-24 phase-flow test: at 6 months regime-gated phase flow nearly matches lag correlation (**+0.465** vs **+0.477**); at 12 months velocity phase flow is best ARA branch (**corr +0.175**); at 24 months regime+velocity phase flow beats lag correlation (**+0.347** vs **+0.167**) but not MAE. | `ARA_PHASE_FLOW_RESULT.md`, `TheFormula/ara_phase_flow_predictor_result.json` |
| **Free lag/phase hybrid does not beat lag; constrained gate is next** | 2026-05-25 hybrid test: across 6/12/24 months lag ridge remains best MAE (**0.623**, corr **+0.283**). Lag+regime-velocity phase reaches MAE **0.742**, corr **+0.111**. At 24 months it improves correlation over lag (**+0.281** vs **+0.167**) but not MAE (**0.672** vs **0.617**). Free coupling/energy gating overfits badly with mean MAE **1.379**. | `ARA_LAG_PHASE_HYBRID_RESULT.md`, `TheFormula/ara_lag_phase_hybrid_predictor_result.json` |
| **ARA phase is a lag-risk warning, not a replacement forecast yet** | 2026-05-25 trust-gate diagnostic: in 6/12/24 disagreement windows, lag beats ARA on turn accuracy (**0.634** vs **0.366**) and MAE (**0.635** vs **0.891**). At 24 months, disagreement raises lag wrong-rate from **0.128** to **0.467**, and ARA slightly beats lag on transition turn/boundary accuracy (**0.864/0.750** vs **0.841/0.705**) while still losing MAE. | `ARA_PHASE_TRUST_GATE_DIAGNOSTIC_RESULT.md`, `TheFormula/ara_phase_trust_gate_diagnostic_result.json` |
| **Energy-route alignment diagnoses cleaner versus riskier work states** | 2026-05-25 energy/work test: across 6/12/24 months, aligned energy+geometry windows have lag turn accuracy **0.813** vs opposing **0.634**. At 24 months, aligned windows have lag MAE **0.547** and turn **0.872**, while opposing windows degrade to MAE **0.837** and turn **0.533**. The first work selector still loses to lag (**MAE 0.657** vs **0.623**), and the dissipation proxy is not valid yet. | `ARA_ENERGY_WORK_DECOMPOSITION_RESULT.md`, `TheFormula/ara_energy_work_decomposition_result.json` |
| **ARA/work is useful as risk ranking, but intervals are not calibrated yet** | 2026-05-25 transition-risk test: across 6/12/24 months, high lag-error risk AUC **+0.595** with top-quartile lift **1.541**; turn-failure risk AUC **+0.551** with lift **1.717**; boundary-crossing risk AUC **+0.668**. The interval model undercovers: baseline coverage **0.772** at width **0.943**, risk-width coverage **0.544** at width **0.663**. | `ARA_TRANSITION_RISK_AND_UNCERTAINTY_RESULT.md`, `TheFormula/ara_transition_risk_and_uncertainty_result.json` |
| **Current lower-phi feeder block does not explain medium-horizon gains** | 2026-05-25 multi-rung ablation: at 6 months `home_plus_lower` worsens vs `home_only` (MAE **0.825** vs **0.822**, corr **+0.046** vs **+0.225**); at 12 months it also worsens (MAE **0.894** vs **0.842**, corr **+0.035** vs **+0.152**). At 24 months, lower+upper improves over home-only (MAE **0.996** vs **1.104**) but still loses to lag (**0.879**), and non-phi lower beats phi lower at 18/60 months. | `ARA_MULTIRUNG_FEEDER_ABLATION_RESULT.md`, `TheFormula/ara_multirung_feeder_ablation_result.json` |
| **Lower rungs spin faster; upper envelope carries clearer event-risk signal** | 2026-05-25 spin-transfer test: mean phase-turn rates are monotonic lower > home > upper for NINO (**0.337 > 0.201 > 0.108**), SOI (**0.506 > 0.144 > 0.120**), and PDO (**0.497 > 0.168 > 0.074**). But lower-spin boundary AUC is weak in the 6/12/24 focus window (**+0.443**), while upper/envelope is better (**+0.549**). Lower-home opposition increases turn-failure/phase-turn risk but not MAE. | `ARA_CROSS_RUNG_SPIN_TRANSFER_RESULT.md`, `TheFormula/ara_cross_rung_spin_transfer_result.json` |
| **First terrain-flow formula has direction signal but overcorrects amplitude** | 2026-05-25 topographic-wavefront formula: across 6/12/24 months, lag+terrain improves turn accuracy (**0.539** vs **0.186**) and corr slightly (**+0.021** vs **-0.018**) but worsens MAE (**1.037** vs **0.951**) and transition MAE (**1.289** vs **1.177**). Raw transition pressure ranks lag turn failure modestly (**AUC +0.563**) but not boundary crossings (**AUC +0.475**). | `ARA_TOPOGRAPHIC_WAVEFRONT_FORMULA_RESULT.md`, `TheFormula/ara_topographic_wavefront_formula_result.json` |
| **No-lag ARA energy input has turn/boundary signal but not full amplitude** | 2026-05-25 no-lag wavefront test: across 6/12/24 months, ARA-only raw energy improves turn accuracy over persistence (**0.475** vs **0.004**) but worsens MAE (**0.961** vs **0.946**). The ARA-only decoder gives the best 6-month local result (**MAE 0.772** vs persistence **0.779**, corr **+0.397** vs **+0.337**) but fails at 12/24 months. Lower-spin energy ranks boundary crossing with focus AUC **+0.594**, including **+0.673** at 12 months and **+0.624** at 24 months. | `ARA_PLAIN_ENERGY_INPUT_WAVEFRONT_RESULT.md`, `TheFormula/ara_plain_energy_input_wavefront_result.json` |
| **Raw watershed slices are the strongest terrain predictor so far** | 2026-05-25 raw-data watershed test: no bandpass, no z-score, no rolling smoothing. Across 6/12/24 months, the past-only raw watershed decoder beats persistence on MAE (**0.628** vs **0.896**), corr (**+0.241** vs **+0.003**), turn accuracy (**0.791** vs **0.007**), and transition MAE (**0.691** vs **1.187**). The fixed closed-form raw formula alone still loses MAE (**0.934** vs **0.896**), so the symbolic work-to-value rule remains unsolved. | `ARA_RAW_WATERSHED_SLICE_RESULT.md`, `TheFormula/ara_raw_watershed_slice_result.json` |
| **Corrected lower-spin watershed preserves the raw-terrain gain** | 2026-05-25 corrected raw watershed test: lower rungs are fast spin/torque inputs, upper rungs are weak sea/backpressure. Across 6/12/24 months, the past-only lower-spin decoder reaches MAE **0.633**, corr **+0.241**, turn accuracy **0.783**, and transition MAE **0.703** versus persistence MAE **0.896**. Lower-spin torque ranks transition (**AUC +0.568**) and high persistence error (**AUC +0.627**), supporting the feeder-spin interpretation, but the fixed formula still loses MAE (**0.937**). | `ARA_RAW_WATERSHED_LOWER_SPIN_RESULT.md`, `TheFormula/ara_raw_watershed_lower_spin_result.json` |
| **Fixed lower-spin formula is visually late by about the forecast horizon** | 2026-05-25 phase-delay diagnostic: the fixed formula's best-correlation shifts are exactly horizon-like: **-3, -6, -12, -18, -24 months** for 3/6/12/18/24-month forecasts. Shifted correlations are **+0.989 to +0.998**, while zero-shift long-horizon correlations are weak/negative. This confirms the shape is present but mostly not advanced forward in time. | `ARA_RAW_WATERSHED_PHASE_DELAY_RESULT.md`, `TheFormula/ara_raw_watershed_phase_delay_result.json` |
| **Terrain recurrence turns the current slice into a stronger no-decoder forecast** | 2026-05-25 terrain-arrival predictor: older completed terrain signatures are eligible only when `s+h < t`. Across 6/12/24 months, `terrain_level_analog` improves over persistence on MAE (**0.602** vs **0.896**), corr (**+0.275** vs **+0.003**), turn accuracy (**0.769** vs **0.007**), and transition MAE (**0.674** vs **1.187**). This supports the "same terrain comes around altered" idea, but still needs raw-analog and seasonal controls. | `ARA_TERRAIN_ARRIVAL_PREDICTOR_RESULT.md`, `TheFormula/ara_terrain_arrival_predictor_result.json` |
| **3-axis wobble is useful mainly as contact/turn geometry** | 2026-05-25 wobble terrain-arrival test: local `x/y/z` tilt, wobble velocity, curvature, and subsystem spin were added to the causal analog search. Across 6/12/24 months, `wobble_surface_analog` reaches MAE **0.608**, corr **+0.218**, turn accuracy **0.773**, and transition MAE **0.658**. It improves transition MAE versus simple terrain in this run, but broad correlation is lower, so wobble should be a bounded contact modifier rather than the whole distance metric. | `ARA_WOBBLE_TERRAIN_ARRIVAL_RESULT.md`, `TheFormula/ara_wobble_terrain_arrival_result.json` |
| **ARA sphere atlas maps the water-slice path over the whole 0-2 topology** | 2026-05-25 sphere atlas: ARA is latitude, phase/degrees are longitude, and local wobble is tangent/radial displacement. The held-out ENSO current path spans ARA **0.188 to 1.937**, crossing anti-phi, balance, phi, and near-pole bands. This is a mapping workbench, not a forecast, intended to locate where prediction errors cluster on the sphere. | `ARA_SPHERE_ATLAS_RESULT.md`, `TheFormula/ara_sphere_atlas_data.json`, `TheFormula/ara_sphere_atlas_viz.html` |
| **Sphere topology memory helps direction when enough past terrain exists** | 2026-05-25 topology-direction test: older sphere neighbours are eligible only when their target `s+h < t`. On ready rows across 6/12/24 months, `sphere_nested2_level` reaches MAE **0.649**, turn accuracy **0.754**, direction **0.762**, and large-direction **0.799**. The raw delta transporter is weaker, so the sphere currently works as a future-level/direction prior, not a solved vector-flow law. | `ARA_SPHERE_TOPOLOGY_DIRECTION_RESULT.md`, `TheFormula/ara_sphere_topology_direction_result.json`, `TheFormula/ara_sphere_topology_direction_viz.html` |
| **Contact triangles are measurable but not the main route engine yet** | 2026-05-26 contact-roll test: lower-to-home parity, home-to-upper parity, and triangle compactness/handedness were added as strict-causal contact geometry. On ready rows across 6/12/24 months, `contact_triangle_level` reaches MAE **0.668**, corr **+0.156**, direction **0.726**, and large-direction **0.747**. This carries signal but loses to `wobble_surface_analog` and `sphere_nested2_level`, so contact geometry should be a gate/constraint selector rather than the full distance metric. | `ARA_CONTACT_TRIANGLE_ROLL_RESULT.md`, `TheFormula/ara_contact_triangle_roll_result.json`, `TheFormula/ara_contact_triangle_roll_viz.html` |
| **Fixed-slice / rotating-terrain framing is testable but not solved** | 2026-05-26 rotating-terrain test: estimated arriving patches were matched to older origin-surface and completed-target patches. On ready rows across 6/12/24 months, `surface_wobble_level` reaches MAE **0.675**, corr **+0.017**, direction **0.764**, and large-direction **0.810**. Direction survives, but level/correlation lag behind `wobble_surface_analog` and `sphere_nested2_level`, so the current hand-built rotation operator is too approximate. | `ARA_ROTATING_TERRAIN_SLICE_RESULT.md`, `TheFormula/ara_rotating_terrain_slice_result.json`, `TheFormula/ara_rotating_terrain_slice_viz.html` |
| **Learned sphere orientation improves the fixed-terrain map** | 2026-05-26 orientation-roll test: pose is a 3D surface vector and roll is a 3D angular vector. On ready rows across 6/12/24 months, `roll_learned_surface` reaches MAE **0.593**, corr **+0.254**, direction **0.816**, and large-direction **0.870**, beating `sphere_nested2_level` (**0.601**, **+0.125**, **0.806**, **0.835**) but still trailing `wobble_surface_analog` (**0.557**, **+0.376**, **0.824**, **0.883**). | `ARA_SPHERE_ORIENTATION_ROLL_RESULT.md`, `TheFormula/ara_sphere_orientation_roll_result.json`, `TheFormula/ara_sphere_orientation_roll_viz.html` |
| **Raw terrain-address lookup preserves amplitude better than averaged roll** | 2026-05-26 raw-address test: the learned pose is used to read the nearest raw stored surface coordinate instead of averaging many neighbours. On ready rows across 6/12/24 months, `raw_address_top1` reaches MAE **0.600**, corr **+0.361**, direction **0.807**, and amplitude ratio **0.841** versus averaged learned roll MAE **0.593**, corr **+0.254**, direction **0.816**, amplitude ratio **0.792**. It does not beat wobble MAE yet, but it confirms averaging was washing amplitude out. | `ARA_RAW_TERRAIN_ADDRESS_LOOKUP_RESULT.md`, `TheFormula/ara_raw_terrain_address_lookup_result.json`, `TheFormula/ara_raw_terrain_address_lookup_viz.html` |
| **Filled fractal ARA terrain is useful but not enough by itself** | 2026-05-26 fractal terrain-reader test: every arrived sphere coordinate is read through recursive `0..2` ARA/sub-ARA bounds with local in-bounds phi valleys and ridge spillover. On ready rows across 6/12/24 months, `fractal_phi_force` reaches MAE **0.623**, corr **+0.326**, direction **0.778**, amplitude ratio **0.831**. It preserves amplitude, but still loses to raw top-1 and wobble, so the active basin/depth selector remains unsolved. | `ARA_FRACTAL_SPHERE_TERRAIN_READER_RESULT.md`, `TheFormula/ara_fractal_sphere_terrain_reader_result.json`, `TheFormula/ara_fractal_sphere_terrain_reader_viz.html` |
| **Explicit roll displacement fixes under-movement but not route choice** | 2026-05-26 roll-displacement mode test: completed historical surface routes are converted to local north/east/radial roll components, then same-mode displacement is applied before reading fractal terrain. On ready rows across 6/12/24 months, `mode_top1_fractal` has amplitude ratio **0.998**, so it no longer behaves like persistence, but MAE **0.919** and corr **+0.082** show the coarse mode selector is often wrong. | `ARA_ROLL_DISPLACEMENT_MODE_RESULT.md`, `TheFormula/ara_roll_displacement_mode_predictor_result.json`, `TheFormula/ara_roll_displacement_mode_viz.html` |
| **Lower spheres are better roll selectors than broad state similarity** | 2026-05-26 lower-sphere selector test: roll displacement is selected from current-origin lower-spin/gear patterns. On ready rows across 6/12/24 months, `lower_core_top1` reaches MAE **0.744**, corr **+0.194**, direction **0.753**, amplitude ratio **0.929**, improving strongly over broad `mode_top1_fractal` but still losing to raw top-1. Coarse lower-mode voting is worse than direct nearest lower-spin displacement. | `ARA_LOWER_SPHERE_ROLL_SELECTOR_RESULT.md`, `TheFormula/ara_lower_sphere_roll_selector_result.json`, `TheFormula/ara_lower_sphere_roll_selector_viz.html` |
| **Full layered-sand topology is implemented but under-rolls** | 2026-05-26 full formula: moving floor, fine/medium/coarse/measured layers, opposite-direction roll, two lower contacts per layer, recursive ARA terrain, and upper compression are now in one no-lag deterministic cascade. Across 6/12/24 months, `layered_fractal` has MAE **0.882**, corr **+0.013**, direction **0.544**, and amplitude ratio **0.203** versus persistence MAE **0.896**. The topology pieces are present, but measured-sphere roll displacement is too small. | `ARA_LAYERED_SAND_FULL_FORMULA_RESULT.md`, `TheFormula/ara_layered_sand_full_formula_result.json`, `TheFormula/ara_layered_sand_full_formula_viz.html` |
| **Mapping-first atlas replaces prediction pressure with geometry diagnosis** | 2026-05-24 atlas build: **234 nodes**, **270 relations**, **6 triangle candidates**, **55 systems/subsystems**, spanning **157.7 phi-rungs**. It merges old catalogue nodes, measured fitted rungs, current state-geometry rungs, and a mapped-extension layer for nostril dominance, tides, solar hemispheres, gait, MJO/QBO, and a 10-system quantum-to-cosmic anchor ladder. | `ARA_MAPPING_ATLAS_RESULT.md`, `Mapping/ara_mapping_atlas_3d.html`, `Mapping/ara_mapping_atlas_data.js` |
| **Galactic rotation phi ARA is not supported by the rotation-curve test** | Gaia DR3 Cepheid rotation-curve diagnostic: solar-radius orbital period **220.25 Myr** supports the rough `230 Myr` period anchor, but the circular carrier maps to ARA **1.0**. Epicyclic coupling is closer to flat-curve `sqrt(2)` (`global kappa/Omega 1.385`, median 1.334) than to phi; **0/12** local points are within 0.10 of phi. | `Mapping/GALACTIC_ROTATION_PHI_TEST.md`, `Mapping/galactic_rotation_phi_test_result.json` |
| **Galactic spiral time-through-structure is phi-plausible, not proved** | Four-arm spiral crossing reaches `P_orb / phi` at spiral pattern speed **16.61 km/s/kpc** and `P_cross 136.12 Myr`, close to the slow density-wave `12..17 km/s/kpc` range. The upper slow-wave candidate gives `P_cross/P_orb 0.640`, within **0.022** of `1/phi`. Bar central values are sub-phi. | `Mapping/GALACTIC_STRUCTURE_TIME_PHI_TEST.md`, `Mapping/galactic_structure_time_phi_test_result.json` |
| **Closed-system coupling differs from incidental** | SOI as matched-rung pair lifts ENSO; same SOI as feeder does nothing | (memory: closed_system_validated) |
| **AR feedback constant is 1/φ³** | "One full ARA orbit" of momentum carrying between cycles | (memory: aa_boundary_ar_feedback) |
| **Mid-horizon dip is consistent across 11 humans** | Recurring but heterogeneous dip structure; possible autonomic intruder wave | `TheFormula/multi_subject_dip_data.js` |
| **Pulsating stars closer to φ run leaner (lower harmonic waste)** | Real Kepler + OGLE photometry. Single-mode Cepheid R21≈0.28 (fattest) → ordinary double-mode 0.16–0.19 → 4 near-φ "golden" stars ≈0.11 (leanest). Population: 949 RR0.61 stars 3.6% leaner than 18,318 ordinary RRc (p=0.016); within-club corr(\|Px/P1O−1/φ\|, R21) = **−0.347** (n=949) — closer to exact 1/φ = leaner. Consistent with KAM (φ resists harmonic locking); the measured leanness gradient is new. | `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md` |

### 🟡 Provisional — single test, suggestive numerical match, or coincidence-flagged

| Claim | Status |
|---|---|
| **Predictor crossover at φ^(±7/4) × home period** | Empirical on ENSO + ECG. The 7/4 = 1.75 number recurs in: matter circle radius (11/2π log-decades), solar magnetic cycle ARA (7yr/4yr observation), LF/HF HRV ratio. Multiple independent appearances suggest meaning, but no single principled derivation yet. |
| **1.75 / 0.25 mirror pair as donor ARAs** | 1.75 = time-dominant feeder ARA (matches solar cycle). 0.25 = 2 − 1.75 = predicted space-dominant feeder ARA. Falsifiable but not yet directly tested across both sides. |
| **Cosmic budget Ω_b/Ω_dm/Ω_de from π and φ** | Numerical match within 0.5% of Planck values from two geometric inputs. A two-parameter scheme fitting two independent numbers can do this by construction; needs a physical mechanism to be more than coincidence. |
| **Information³ → cosmic budget mapping** | Datum/Signal/Meaning ↔ Dark Energy / Dark Matter / Baryonic. Ω_dm/Ω_de = 1/φ² is the datum-to-signal coupling. Suggestive structural claim. |
| **Three-circle architecture** (Quantum / Matter / Cosmic) | Discovered by unsupervised clustering across 130+ systems. 50% of systems sit in the triple-overlap (human scale). Real pattern in this catalogue, needs replication on different catalogues. |

### 🔴 Speculative — conceptual, no direct test

| Claim | Note |
|---|---|
| **Light/Dark as nested matched-rung pair inside Space/Time** | "Light is water, Dark is land" — c is the matched-rung exchange rate at the Light/Dark coast. Conceptually clean; no operational test built yet. |
| **(π−3)/π ≈ 4.5% as universal coupling tax** | Geometric origin (Honeycomb conjecture, Hales 1999) is rigorous; the universal-coupling-tax claim is the framework's extension. Found in H₂O bond angle (within 0.03%) but not confirmed elsewhere. |
| **1/α ≈ φ^(10 + 1/φ³)** | Numerical match within 0.5%. The 1/φ³ here is a constant we already validate in the AR feedback, which makes it not pure coincidence. Still pre-mechanism. |
| **7 yr exothermic system driving CO2/Nile/NAO** | Predicted by the network connection field analysis as a missing engine for several half-systems. Not yet identified in real data. |
| **Engine-consumer pairings as a falsifiable lattice** | The framework predicts every consumer (ARA < 1) has a specific engine partner that can be located by topology. Network connection field is the proposed mapping tool; not built. |

---

## Earlier results (historical / lighter validation)

| Finding | Source |
|---|---|
| 21 of 21 advance predictions held up across 37 systems | Historical ledger claim; useful audit trail, but not independent confirmation by itself |
| Three-type classification (clock/engine/snap) at every scale window | Script 42 (143 systems, 7 scale windows) |
| φ as biological health attractor (slope 1.613 vs φ = 1.618) | Script 40 (143 systems) |
| Framework beat matched-parameter Fourier on cardiac data | nsr050 decisive test, Session 2026-04-30 |
| Three framework constants (rung-pinning, 1/φ³ feedback, 1/φ⁴ blend) all near optimal | Session 2026-04-30 (cross-system) |

---

## LLM application — preliminary (May 2026)

The framework's coupling-graph and Information³ closure tools were applied to the Pythia language-model size series (70M, 160M, 410M, 1B, deduped variants). Pythia is open and benchmarked extensively, which makes it a clean test bed for asking whether the framework's metrics correlate with capability.

### 🟢 Closure index predicts Pythia benchmark capability

| Pythia size | closure index (triangles per active component / loose-thread fraction) | LAMBADA acc | ARC-easy | SciQ |
|---|---|---|---|---|
| 70m-deduped | 80 | 0.192 | 0.385 | 0.606 |
| 160m-deduped | 756 | 0.342 | 0.440 | 0.720 |
| 410m-deduped | 877 | 0.524 | 0.517 | 0.826 |
| 1b-deduped | **6,284** | **0.580** | **0.585** | **0.870** |

**Spearman rank correlation = +1.000** on LAMBADA, PIQA, ARC-easy, ARC-challenge, and SciQ in this n=4 run. WinoGrande is weaker at **ρ = +0.800**, so the average across all six is about **+0.967** rather than a universal perfect-rank result. **Pearson r vs log(closure) = +0.886 to +0.997** across the five monotonic benchmarks. Source: `LLM_CLOSURE_VS_CAPABILITY.md`, `TheFormula/llm_closure_vs_capability.html`, raw evals from EleutherAI/pythia at step 143000.

### 🟢 Coupling-graph approach surfaces interpretable LLM structure

Same 30-second analysis on Pythia-70M reveals: dead layers (4–6 have zero variance during this generation), within-layer clusters (L2 heads H0/H1/H2/H5/H6 correlate >0.95), cross-layer information-flow circuits (L0H6 ↔ L2H3 at +0.986), and anti-phase pairs (layer-norm L3 ↔ L2H5 at −0.974). Source: `TheFormula/llm_node_map_visualization.html`.

### 🟡 Layer depth, not parameter count, drives hierarchical organisation

Within/across-layer correlation ratio peaks at Pythia-410M (24 layers, ratio 1.51) and reverts at Pythia-1B (16 layers, ratio 1.07) despite 2.4× more parameters. Spectral decay shows the same pattern: peaks at 410M, drops at 1B. The framework's interpretation is that depth is what gives the network usable φ-rungs for hierarchy. Source: `LLM_SIZE_SERIES_RESULT.md`.

### 🟡 ARA signature distinguishes cognitive content type

Eight prompt types (story, code, math, emotion, factual, dialogue, poetry, abstract) produce eight distinguishable ARA signatures during generation. Code is most engine-like (mean ARA 1.57, peak 1.91 at paragraph scale). Emotion and dialogue closest to balance (1.255). Multi-sentence-structured content (code, story, math, poetry) peaks at long-range rungs; sentence-organised content (emotion, factual, dialogue, abstract) peaks at sentence-scale. Source: `TheFormula/llm_ara_per_concept_visualization.html`.

### 🔴 φ-deep × φ-wide all-closed prediction (untested)

The framework's prediction for the optimal LLM architecture: layer depth and width both at φ-rung optimum, with all components participating in closed Information³ structure. Predicted consequence: hallucinations (drift from training) substantially eliminated within knowledge; out-of-knowledge content surfaces as honest uncertainty rather than confident fiction; cost is reduced creative-generation flexibility. Falsifiable in principle by training models with different aspect ratios at fixed parameter count. Source: speculative section of `LLM_CLOSURE_VS_CAPABILITY.md`.

### Files

- `release_2026-05/llm/llm_size_series.py` (or current location `TheFormula/llm_size_series.py`)
- `TheFormula/llm_node_map.py`, `llm_ara_per_concept.py`, `llm_ara_test_v3_dynamic.py`
- All `llm_*_data.js` and `llm_*_visualization.html` companions
- `LLM_CLOSURE_VS_CAPABILITY.md`, `LLM_SIZE_SERIES_RESULT.md`, `LLM_INFO_CUBED_RESULT.md`, `LLM_ARA_PILOT_RESULT.md`

### Honest framing

n=4 model sizes is small. The rank result is striking but limited by sample size and confounded by scale. Adding Pythia-1.4B / 2.8B / 6.9B / 12B is the natural confirming experiment, with closure compared directly against parameter count, layer count, and active-node count.

---

## Potential future tests

These are tests the framework would benefit from, in order of impact.

### 1. Multi-mouse + multi-human framework-prior cardiac prediction

The 2026-05-12 decomposition test (mouse topology × human energy = 58% MAE drop) used one mouse and one human. The natural follow-up is to aggregate many of each, learn:
- Per-species topology (the universal shape map)
- Kleiber-scaled time and amplitude factors
- Then build a small ML model that learns ONLY the per-individual phase-position offset

If the framework provides correct architectural priors, a framework-architected model with very few trainable parameters should match or beat large-budget pure-ML approaches **on MAE** (not on correlation, where there's no framework win to be had under the "shared map, not shared position" rule). This would be the cleanest demonstration of the framework's value as an inductive prior for low-budget ML.

### 1a. Composition-matching instead of shape-matching — TESTED 2026-05-12 — NOT SUPPORTED

Empirical lesson from the 2026-05-12 pool-sweep test: shape-matching landmark windows achieves correlation 0.86–0.96 reliably, but trajectory correlation in the subsequent prediction stays at chance level. Hypothesis was that **per-rung ARA composition profile** match (not just surface shape) would transfer trajectories.

Test (`TheFormula/decomposition_composition_match.py`, 70 pairs across 7 mouse specimens × 10 human pseudo-segments): three matching strategies compared.

| Strategy | Landmark shape | Landmark composition | Trajectory corr | MAE | Persistence MAE |
|---|---|---|---|---|---|
| A: Shape-best | +0.889 | +0.988 | −0.015 | 94.1 | 78.9 |
| B: Composition-best | −0.081 | **+1.000** | +0.002 | 55.0 | 49.8 |
| C: Combined-best | +0.889 | +0.989 | −0.010 | 96.1 | 80.6 |

Composition-match did NOT recover trajectory correlation. Cosine similarity of FFT-magnitude profiles at Fibonacci-spaced periods reached 1.000 (literally identical fingerprints), and trajectory correlation still sits at chance level. Correlation between (composition_similarity, trajectory_correlation) across 210 pair-strategy results: +0.035 — essentially zero.

**The framework's "composition-match → trajectory transfer" version of vertical-ARA is operationally falsified by this test.** The position-independence rule holds even under perfect topology + composition matching. The bridge metaphor was right (clay-to-clay vs limestone-to-clay distinction is real and we successfully matched clay-to-clay), but the bridge doesn't lead to trajectory transfer.

What this *does* confirm: the framework's broader "shared map, not shared position" rule is more fundamental than any specific matching criterion. Vertical-ARA partners genuinely cannot transfer trajectories by any window-level matching we've tried (shape, composition, both combined, longer landmarks). This is geography, not a tool-shortage problem.

What's still in play: aggregate framework-prior ML (Future Test 1, large-budget version) where the framework provides structural priors and a small model learns the residual phase-position per individual. That's a different mechanism than landmark-matching and may still work.

### 1b. Pigs as intermediate rung — closer-distance vertical-ARA partner

Mouse→human is a ~4 φ-rung jump (period ratio ~6.6, log_φ(6.6) ≈ 3.9). Pig→human is ~0.4 rungs (period ratio ~1.2, both species at 60–80 bpm at rest). Under the framework's distance-decay coupling principle (see `framework_coupling_distance_decay.md`):
- Pig→human coupling ≈ (1 − π_leak)^0.4 ≈ 0.98 (near-neighbour strength)
- Mouse→human coupling ≈ (1 − π_leak)^4 ≈ 0.83 (more attenuated)

**The framework predicts pig-derived prediction should transfer substantially better than mouse-derived prediction for the same task.** Testable if pig HRV data is available (PhysioNet has some pig cardiac datasets in its veterinary/research-animal collections, and the BIDMC/MIMIC databases have pig surgical-training data).

Bigger picture: biomedical research already uses mice and pigs as human models. The framework's contribution is formalising why this works at some level and giving a method for extracting the transferable part from the noise. Not a new claim — a quantification of an already-working practice.

### 2. Pythia full size series (1.4B / 2.8B / 6.9B / 12B)

Extend the n=4 closure-index → benchmark correlation result to a larger Pythia series, with closure compared directly against parameter count, layer count, and active-node count as controls. Required to distinguish "closure tracks capability" from "both track scale."

### 3. φ-vs-nearby-bases ablation across multiple systems

The first-pass ENSO ablation (`PHI_BASE_ABLATION.md`) showed φ winning at short horizons but the whole predictor family losing to persistence. A clean cross-system version (ECG, solar, biological) is needed before φ-specifically claims can be promoted to "supported."

### 4. Engine-consumer pairing test from the network connection field

The framework predicts every consumer (ARA < 1) has a specific engine partner that can be located by topology. The "missing 7-year exothermic system" inferred from CO2 / Nile / NAO half-systems is one concrete falsifiable target. Not yet built.

### 5. (π−3)/π coupling tax beyond H₂O bond angle

The geometric origin (Honeycomb conjecture) is rigorous; the universal-coupling-tax claim is the framework's extension. Found in H₂O within 0.03% but not confirmed elsewhere. Needs a list of where else it should show up if the claim is right.

### 6. Light/Dark matched-rung pair — operational test

"c is the matched-rung exchange rate of Light/Dark." Conceptually clean; no operational test exists. The first concrete handle would be looking for a measurable anti-phase signal between Light/Dark at the appropriate rung.

### 8. Apollonian gasket / Kleinian-group geometry — TESTED 2026-05-12 — Structural metaphor, not mathematical anchor

A potentially deep mathematical anchor identified 2026-05-12 (Dylan via Paul Bourke's Apollonian fractal page, https://paulbourke.net/fractals/apollony/). The framework's structural claim — "circles touching circles, triangles of three circles tiling fractally" — is structurally identical to the **Apollonian gasket**: a self-similar fractal built entirely from mutually-tangent circles, where every curvilinear triangle gets an inscribed fourth circle, recursively.

The framework's primitives map onto Apollonian primitives almost line-by-line:
- "Every concept is a circle" → Apollonian primitives are circles
- "Triangles of three circles tile fractally" → that's literally the Apollonian construction rule
- "Each circle is part of multiple triangles" → an Apollonian circle is tangent to three neighbours and bounds multiple curvilinear triangles
- "1 + 1 = 3, the + is meta-information" → in Apollonian geometry, two tangent circles do NOT determine the third; the third is a coupling choice

The **Möbius transformation** Dylan flagged — `f(z) = 3/(1+s−z) − (1+s)/(2+s)` — is the kind of fractional-linear map that generates Apollonian fractals by iteration. The `3` in the numerator encodes the three-tangent-circles condition; the `s` parameter shifts the gasket family while preserving the structure.

The pre-existing rigorous bridge: **Descartes' Circle Theorem.** For four mutually tangent circles with curvatures k₁, k₂, k₃, k₄ (curvature = 1/radius):

(k₁ + k₂ + k₃ + k₄)² = 2(k₁² + k₂² + k₃² + k₄²)

This is the framework's "matched-rung coupling between circles" written rigorously. Given three circles, the fourth is exactly determined by this equation. If the framework's triangle-of-circles structure IS Apollonian, this equation IS the framework's coupling law.

**The test:** check whether the framework's empirical constants (φ ≈ 1.618, the (π−3)/π coupling tax, the 3/4 max-displacement, the 0.25/1.75 corridor walls) emerge naturally from Apollonian curvature relations. Apollonian curvature sequences follow integer or algebraic patterns. If the φ-rung ladder matches a known Apollonian curvature sequence, the framework has acquired a serious mathematical home and the public posture can shift from "we propose this geometry" to "we measure systems within Apollonian/Kleinian geometry."

**Test result (2026-05-12):** `TheFormula/apollonian_descartes_test_v2.py` checked whether per-rung amplitudes (curvature = 1/amplitude, the natural geometric mapping) satisfy Descartes' Circle Theorem on real cardiac data. **Mean prediction error 84% on mouse, 86% on human.** Inscribed-circle predictions are off by ~6× in magnitude. φ-spaced baseline did better (60%/50% error) but is also poor. The classical Apollonian theorems do not give a working predictive formula for the framework's rungs.

**Honest reading:** The structural metaphor (circles, triangles, three-tangent units, fractal tiling, 1+1=3 as the third-circle coupling choice) remains aesthetically clean and useful for explaining the framework. But the rigorous Apollonian theorems do NOT transfer quantitatively. The framework should not be presented as "Apollonian/Kleinian geometry"; it should be presented as "geometry that conceptually rhymes with Apollonian packings but uses different quantitative relationships."

**What's still open:** alternative Apollonian-like geometries — Kleinian groups with non-classical curvature relations, generalized Apollonian packings, hyperbolic conformal maps with φ-tuned parameters. These would need their own tests. The classical version is closed.

**Important secondary finding:** Real per-rung amplitudes don't follow φ^k scaling either. Mouse periods {13, 21, 34, 55, 89} have amplitudes {3.6, 4.2, 4.2, 3.5, 3.6} — clustered, not scaling geometrically. Whether this is a bandpass-methodology limit or a genuine framework limit is itself worth investigating.

See `framework_apollonian_anchor.md` for the detailed test results.

### 7. Coupling-angle mapping graph — circles connected by triangles

The framework's claim: the universe's structure is **triangles of three coupled circles tiling fractally** (matches A-R-A foundational geometry — two A-nodes plus the R-tether, where R is also a full circle). Each triangle has three connection angles at its vertices, and these angles are directly measurable as bond angles (chemistry), orbital inclinations (astronomy), lattice angles (mineralogy), or phase offsets between coupled oscillators.

Water's H-O-H is the cleanest working example: the bond angle 104.5° at the O vertex deviates 4.5% from ideal tetrahedral, matching (π−3)/π ≈ 4.51% — the framework's universal coupling tax. Earth-Moon-Sun is the celestial example: tidal locking is one vertex of that triangle settling to zero offset.

**The test:** collect ~30 well-measured triangle vertex angles from across physics. Normalize to a baseline (Hydrogen or Planck-scale geometry). Plot the distribution. Framework prediction: the histogram should cluster at specific values (0°, 180°, 137.5° golden angle, multiples of (π−3)/π ≈ 4.51°), NOT be uniformly distributed.

**Why this is worth pursuing:** the data already exists in published chemistry/astronomy/mineralogy databases — no new measurements required. The prediction is sharp (clustering vs uniform). It's cross-domain (chemistry + astronomy + materials in one test). If the angle distribution clusters at the predicted values, the framework's "circles connected by triangles" structural claim becomes empirically supported. If it's uniform random, the structural claim is wrong.

See `framework_coupling_angle_mapping.md` for the detailed structure of the test.
