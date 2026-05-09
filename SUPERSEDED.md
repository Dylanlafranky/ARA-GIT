# Superseded Scripts — Lineage Map

This document maps the numbered research journey scripts (01–243+variants) to their canonical replacements in `TheFormula/`. These scripts were the exploratory trail — hundreds of iterations that refined the ARA framework from early harmonic ratio tests through to the final formula engine. The canonical implementations now live in `TheFormula/`.

**Status key:**
- **Superseded** — has a direct or near-direct replacement in `TheFormula/`
- **Historical** — unique test or exploration with no direct replacement; still valuable as research record
- **Dead End** — iteration or variant that was abandoned in favour of a better approach

---

## Era 1: Early Exploration (01–40)

| Old Script | Status | Replaced By | Notes |
|---|---|---|---|
| 01_harmonic_ratio_test_naive.py | Historical | — | First test; foundation of harmonic ratio idea |
| 02_harmonic_ratio_test_tightened.py | Superseded | TheFormula/canonical_benchmark.py | Refined version of 01 |
| 03_bimodal_cluster_test.py | Historical | — | Early clustering exploration |
| 04_atomic_clock_transitions.py | Historical | — | Atomic clock domain test |
| 05_tighten_subsystems_primary_sources.py | Historical | — | Data quality tightening |
| 06_spacing_candidates_all.py | Historical | — | Spacing exploration |
| 07_phi_significance_monte_carlo.py | Historical | — | Statistical significance test for phi |
| 08_pi_ladder_and_circle_test.py | Historical | — | Pi-ladder geometry origin |
| 09_ara_structured_octave.py | Historical | — | Early ARA structure |
| 10_self_similar_proof_attempt.py | Historical | — | Self-similarity proof attempt |
| 11_kam_mapping_proof.py | Historical | — | KAM theorem connection |
| 12_blind_system_mapping.py | Historical | TheFormula/map_systems_v3.py | First blind mapping test |
| 13_blind_systems_batch2.py | Historical | TheFormula/map_systems_v3.py | Blind mapping batch 2 |
| 14_blind_system_laser.py | Historical | — | Laser system blind test |
| 15_BZ_reaction_mapping.py | Historical | — | Belousov-Zhabotinsky reaction |
| 16_metronome_synchronization.py | Historical | — | Metronome sync domain |
| 17_cosmic_ara_mapping.py | Historical | — | Cosmic scale mapping |
| 18_action_ladder_octave_test.py | Historical | TheFormula/dynamic_rung_assignment_test.py | Action ladder concept |
| 19_ladder_density_ARA.py | Historical | TheFormula/dynamic_rung_assignment_test.py | Ladder density refinement |
| 20_complexity_scale_ARA.py | Historical | — | Complexity scale mapping |
| 21_KAM_golden_torus_ARA.py | Historical | — | KAM golden torus |
| 22_arctic_sea_ice_ARA.py | Historical | — | Arctic sea ice domain |
| 23_firefly_synchronization.py | Historical | — | Firefly sync domain |
| 24_brain_EEG_ARA.py | Historical | — | Brain EEG domain |
| 25_ocean_tides_ARA.py | Historical | — | Ocean tides domain |
| 26_brain_three_deck_ARA.py | Historical | — | Brain three-deck ARA |
| 27_MECFS_three_deck_ARA.py | Historical | — | ME/CFS three-deck ARA |
| 28_immune_system_ARA.py | Historical | — | Immune system domain |
| 29_mechanical_oscillators_ARA.py | Historical | — | Mechanical oscillators domain |
| 30_forced_oscillators_ARA.py | Historical | — | Forced oscillators domain |
| 31_ventilator_patient_ARA.py | Historical | — | Ventilator-patient domain |
| 32_quantum_atomic_ARA.py | Historical | — | Quantum atomic domain |
| 33_planetary_orbital_ARA.py | Historical | TheFormula/orbital_closed_system_test.py | Planetary orbital domain |
| 34_action_potential_ARA.py | Historical | — | Action potential domain |
| 35_electronic_circuits_ARA.py | Historical | — | Electronic circuits domain |
| 36_fluid_dynamics_ARA.py | Historical | — | Fluid dynamics domain |
| 37_human_ant_colony_ARA.py | Historical | — | Human/ant colony domain |
| 38_complexity_scale_curve_fit.py | Superseded | TheFormula/canonical_benchmark.py | Complexity scale curve fitting |
| 39_curve_verification_battery.py | Superseded | TheFormula/canonical_benchmark.py | Curve verification battery |
| 40_spine_wave_analysis.py | Historical | — | Spine wave analysis |

## Era 2: System Mapping (41–77)

| Old Script | Status | Replaced By | Notes |
|---|---|---|---|
| 41_cmb_spine_extension.py | Historical | — | CMB spine extension |
| 42_fractal_nesting_test.py | Historical | TheFormula/compass_fractal_corrector_test.py | Fractal nesting concept |
| 43_triple_helix_analysis.py | Historical | — | Triple helix analysis |
| 44_information_processing_ara.py | Historical | — | Information processing domain |
| 45_consciousness_perception_ara.py | Historical | — | Consciousness/perception domain |
| 46_economic_systems_ara.py | Historical | — | Economic systems domain |
| 47_music_acoustic_ara.py | Historical | — | Music/acoustic domain |
| 48_failure_modes_ara.py | Historical | — | Failure modes analysis |
| 49_geological_tectonic_ara.py | Historical | — | Geological/tectonic domain |
| 50_chemical_oscillators_ara.py | Historical | — | Chemical oscillators domain |
| 51_light_matter_ara.py | Historical | — | Light/matter domain |
| 52_civilizational_span_ara.py | Historical | — | Civilizational span domain |
| 53_fundamental_physics_ara.py | Historical | — | Fundamental physics domain |
| 54_ara_wave_derivation.py | Historical | TheFormula/wave_ara_carry_test.py | ARA wave derivation |
| 55_em_spectrum_ara.py | Historical | — | EM spectrum domain |
| 56_states_of_matter_ara.py | Historical | — | States of matter domain |
| 57_three_phase_universal_ara.py | Historical | — | Three-phase universal ARA |
| 58_fundamental_forces_ara.py | Historical | — | Fundamental forces domain |
| 59_pi_phi_coupling_ara.py | Historical | — | Pi-phi coupling |
| 60_scale_dependent_phase_ara.py | Historical | — | Scale-dependent phase |
| 61_time_as_ara.py | Historical | TheFormula/time_topology_navigator.py | Time as ARA concept |
| 62_quantum_measurement_ara.py | Historical | — | Quantum measurement domain |
| 63_information_entropy_ara.py | Historical | TheFormula/compass_info_cubed_test.py | Information entropy domain |
| 64_sleep_consciousness_ara.py | Historical | — | Sleep/consciousness domain |
| 65_cosmology_ara.py | Historical | — | Cosmology domain |
| 66_evolution_ara.py | Historical | — | Evolution domain |
| 67_economics_ara.py | Historical | — | Economics domain |
| 68_music_sound_ara.py | Historical | — | Music/sound domain |
| 69_ecology_ara.py | Historical | — | Ecology domain |
| 70_language_cognition_ara.py | Historical | — | Language/cognition domain (unique from computations/) |
| 71_technology_computation_ara.py | Historical | — | Technology/computation domain (unique from computations/) |
| 72_medicine_disease_ara.py | Historical | — | Medicine/disease domain (unique from computations/) |
| 73_sociology_civilisation_ara.py | Historical | — | Sociology/civilisation domain |
| 74_chemistry_bonding_ara.py | Historical | — | Chemistry/bonding domain |
| 75_geology_tectonics_ara.py | Historical | — | Geology/tectonics domain |
| 76_three_circle_decomposition.py | Historical | TheFormula/ara_class_control_test.py | Three-circle decomposition |
| 77_circle_orientation_ara.py | Historical | TheFormula/ara_class_control_test.py | Circle orientation |

## Era 3: Advanced Tests (78–99)

| Old Script | Status | Replaced By | Notes |
|---|---|---|---|
| 78_unsupervised_circle_discovery.py | Historical | — | Unsupervised discovery method |
| 79_arc_fitting_circle_discovery.py | Historical | — | Arc fitting discovery |
| 79b_tight_arc_discovery.py | Dead End | — | Variant of 79; abandoned |
| 87_unified_oscillatory_ladder.py | Historical | TheFormula/dynamic_rung_assignment_test.py | Unified oscillatory ladder |
| 88_meta_scale_structure.py | Historical | — | Meta-scale structure |
| 89_gap_filling_scales.py | Historical | — | Gap-filling scales |
| 90_singularity_circle2.py | Historical | — | Singularity circle test |
| 91_meta_wave.py | Historical | — | Meta-wave concept |
| 92_subatomic_slope_inversion.py | Historical | — | Subatomic slope inversion |
| 93_organism_planetary_coupling.py | Historical | TheFormula/cross_subject_reproducibility.py | Organism-planetary coupling |
| 94_real_ara_measurements.py | Historical | TheFormula/actual_values_delta_test.py | Real ARA measurements |
| 95_energy_axis_formalization.py | Historical | — | Energy axis formalization |
| 96_coupler_transparency.py | Historical | — | Coupler transparency |
| 97_metawave_corrected_ara.py | Historical | — | Corrected meta-wave |
| 98_cepheid_blind_test.py | Historical | — | Cepheid blind prediction |
| 99_briggs_rauscher_blind_test.py | Historical | — | Briggs-Rauscher blind prediction |

## Era 4: Coupling & Topology (100–140)

| Old Script | Status | Replaced By | Notes |
|---|---|---|---|
| 100_light_ara_blind_test.py | Historical | — | Light ARA blind test |
| 101_black_hole_coupler_test.py | Historical | — | Black hole coupler |
| 102_ara_conservation_test.py | Historical | — | ARA conservation test |
| 103_pi_leak_entropy_test.py | Historical | — | Pi-leak entropy |
| 104_honeycomb_pi_leak.py | Historical | — | Honeycomb pi-leak |
| 105_hawking_ara_decomposition.py | Historical | — | Hawking radiation ARA |
| 106_mirror_reconstruction_test.py | Historical | — | Mirror reconstruction |
| 107_void_temporal_flow_test.py | Historical | — | Void temporal flow |
| 108_death_boundary_event_test.py | Historical | — | Death boundary event |
| 109_phi_tolerance_band.py | Historical | TheFormula/phi_storage_read_test.py | Phi tolerance band |
| 110_phi_band_independent_validation.py | Historical | TheFormula/phi_storage_read_test.py | Phi band validation |
| 111_three_system_curvature_bridge.py | Historical | — | Three-system curvature bridge |
| 112_phi_singularity_asymmetry.py | Historical | — | Phi singularity asymmetry |
| 113_irrationality_coupling_predictor.py | Historical | — | Irrationality coupling predictor |
| 114_vertical_ara_coupling.py | Historical | TheFormula/multispecies_vertical_ara_test.py | Vertical ARA coupling |
| 115_water_rosetta_stone.py | Historical | TheFormula/calcium_rosetta_test.py | Water as Rosetta stone |
| 116_sp3_template_test.py | Historical | — | SP3 template test |
| 116b_circle_packing_gap.py | Dead End | — | Circle packing gap variant |
| 117_triple_tangency_constraint.py | Historical | — | Triple tangency constraint |
| 118_dark_matter_behavior.py | Historical | — | Dark matter behaviour |
| 119_dark_matter_deep_dive.py | Historical | — | Dark matter deep dive |
| 120_fourth_observable.py | Historical | — | Fourth observable concept |
| 121_spectral_tilts_from_ara.py | Historical | — | Spectral tilts from ARA |
| 122_dark_sector_mirror_evolution.py | Historical | — | Dark sector mirror evolution |
| 123_mirror_structures_colocation.py | Historical | — | Mirror structures colocation |
| 124_ara_loop_circle_mapping.py | Historical | — | ARA loop-circle mapping |
| 125_meta_ara_phi_domains.py | Historical | — | Meta-ARA phi domains |
| 126_entropy_barrier_temporal_axis.py | Historical | — | Entropy barrier temporal axis |
| 127_quantitative_em_binding_chainmail.py | Historical | — | EM binding chainmail |
| 128_closed_chainmail_topology.py | Historical | — | Closed chainmail topology |
| 129_fractal_chainmail_experience.py | Historical | — | Fractal chainmail experience |
| 130_alien_inevitability_love_as_engine.py | Historical | — | Philosophical exploration |
| 131_topology_translation_principle.py | Historical | — | Topology translation principle |
| 132_translation_factor_derivation.py | Historical | — | Translation factor derivation |
| 133_sign_from_wave_phase.py | Historical | — | Sign from wave phase |
| 134_information_singularity_and_the_mess.py | Historical | — | Information singularity |
| 135_consciousness_coupling_map.py | Historical | — | Consciousness coupling map |
| 136_blind_topology_translations.py | Historical | — | Blind topology translations |
| 137_relational_topology_translations.py | Historical | — | Relational topology translations |
| 138_bone_rock_coal_diamond.py | Historical | — | Bone/rock/coal/diamond mapping |
| 139_force_time_circle.py | Historical | — | Force-time circle |
| 140_force_time_proof.py | Historical | — | Force-time proof |

## Era 5: Theory Extensions (141–200)

| Old Script | Status | Replaced By | Notes |
|---|---|---|---|
| 141_physics_formalism_coupling.py | Historical | — | Physics formalism coupling |
| 142_circular_vertical_translation.py | Historical | — | Circular vertical translation |
| 143_ara_chain_coupling.py | Historical | — | ARA chain coupling |
| 144_coupling_substructure.py | Historical | — | Coupling substructure |
| 145_ara_cubed_eta.py | Historical | — | ARA cubed eta |
| 146_three_nested_circles.py | Historical | — | Three nested circles |
| 147_same_phase_circles.py | Historical | — | Same phase circles |
| 148_dylans_pairs_blind.py | Historical | — | Dylan's pairs blind test |
| 149_fires_pimples_blind.py | Historical | — | Fires/pimples blind test |
| 150_sphere_valley_model.py | Historical | — | Sphere valley model |
| 151_seeds_ocean_tears.py | Historical | — | Seeds/ocean/tears mapping |
| 152_caves_muscles.py | Historical | — | Caves/muscles mapping |
| 153_population_tumours.py | Historical | — | Population/tumours mapping |
| 154_thunder_ants.py | Historical | — | Thunder/ants mapping |
| 155_eyes_eating.py | Historical | — | Eyes/eating mapping |
| 156_log_power_circles.py | Historical | — | Log power circles |
| 157_formula_visualisations.py | Historical | — | Formula visualisation generator |
| 158_random_prediction.py | Historical | — | Random prediction test |
| 159_random_reverse.py | Historical | — | Random reverse test |
| 160_phi_clustering_test.py | Historical | — | Phi clustering test |
| 161_sunspot_temporal_prediction.py | Superseded | TheFormula/rolling_vehicle_test.py | Sunspot temporal prediction |
| 162_crossscale_sunspot_earthquake.py | Historical | TheFormula/cross_subject_reproducibility.py | Cross-scale sunspot/earthquake |
| 163_sphere_triangulation.py | Superseded | TheFormula/triangulation_test.py | Sphere triangulation |
| 164_time_as_sphere.py | Historical | TheFormula/time_topology_navigator.py | Time as sphere concept |
| 165_three_sphere_scan.py | Historical | — | Three sphere scan |
| 166_isosceles_phi_triangle.py | Historical | — | Isosceles phi triangle |
| 167_blind_temporal_prediction.py | Historical | — | Blind temporal prediction |
| 168_dampened_network_prediction.py | Historical | — | Dampened network prediction |
| 169_paired_phi_dampening.py | Historical | — | Paired phi dampening |
| 170_phi_inside_mapping.py | Historical | — | Phi inside mapping |
| 171_inside_outside.py | Historical | — | Inside/outside concept |
| 172_log_geared_prediction.py | Historical | — | Log-geared prediction |
| 173_ara_coupled_gearing.py | Historical | — | ARA coupled gearing |
| 174_ara_cycle_clock.py | Historical | — | ARA cycle clock |
| 175_inner_circle_drives_outer.py | Historical | — | Inner circle drives outer |
| 176_tuned_nested_circles.py | Historical | — | Tuned nested circles |
| 177_phi_through_motion.py | Historical | — | Phi through motion |
| 178_phi_through_tuned.py | Dead End | — | Tuned variant of 177 |
| 179_inverted_gear_fractal_clock.py | Historical | — | Inverted gear fractal clock |
| 180_gear_floor_sweep.py | Dead End | — | Gear floor sweep |
| 181_independent_clock_push.py | Historical | — | Independent clock push |
| 182_full_ara_range.py | Historical | TheFormula/high_res_ara_test.py | Full ARA range |
| 183_linear_mapping.py | Historical | — | Linear mapping |
| 184_pi_leak_clock.py | Historical | — | Pi-leak clock |
| 185_pi_leak_fine_tune.py | Dead End | — | Pi-leak fine tuning |
| 186_log_boundary_leak.py | Historical | — | Log boundary leak |
| 187_generative_clock.py | Superseded | TheFormula/generative_vehicle.py | Generative clock |
| 188_time_blend_ara_scale.py | Historical | — | Time blend ARA scale |
| 189_phi_leak_clock_blend.py | Dead End | — | Phi-leak clock blend |
| 190_pi_on_phi_path.py | Historical | — | Pi on phi path |
| 191_phi_valley_watershed.py | Historical | — | Phi valley watershed |
| 192_watershed_tuned.py | Dead End | — | Watershed tuned variant |
| 193_oil_crisis_blind.py | Historical | — | Oil crisis blind prediction |
| 194_reverse_valley_humanity.py | Historical | — | Reverse valley humanity |
| 195_held_out_temporal.py | Historical | — | Held-out temporal test |
| 196_formula_cubed.py | Historical | TheFormula/formula_v4.py | Formula cubed |
| 197_formula_nine.py | Historical | TheFormula/formula_v4.py | Formula nine |
| 198_scalene_triangle.py | Historical | TheFormula/triangulation_test.py | Scalene triangle |
| 199_normal_modes.py | Historical | — | Normal modes |
| 200_perpendicular_singularity.py | Historical | — | Perpendicular singularity |
| 200b_three_way_junction.py | Dead End | — | Three-way junction variant |
| 200c_no_pi_leak.py | Dead End | — | No pi-leak variant |
| 200d_vertical_coupling.py | Superseded | TheFormula/multispecies_vertical_ara_test.py | Vertical coupling |

## Era 6: Formula Engine (201–243+)

| Old Script | Status | Replaced By | Notes |
|---|---|---|---|
| 201_phi_nine.py | Superseded | TheFormula/phi9_atom_test.py | Phi-nine concept |
| 202_full_historical_test.py | Superseded | TheFormula/canonical_benchmark.py | Full historical test |
| 203_temporal_tension.py | Historical | TheFormula/state_propagation_test.py | Temporal tension |
| 203b_valved_phi9.py | Dead End | — | Valved phi9 variant |
| 204_fractal_modulator.py | Historical | TheFormula/compass_fractal_corrector_test.py | Fractal modulator |
| 205_temporal_offset.py | Historical | — | Temporal offset |
| 205b_singularity_read.py | Dead End | — | Singularity read variant |
| 206_dynamic_gate.py | Superseded | TheFormula/gate_inertia_test.py | Dynamic gate |
| 207_causal_gate.py | Superseded | TheFormula/gate_inertia_test.py | Causal gate |
| 208_temporal_decay_gate.py | Superseded | TheFormula/gate_inertia_test.py | Temporal decay gate |
| 209_solar_drain.py | Superseded | TheFormula/drain_architecture_test.py | Solar drain |
| 210_ar_scaled_drain.py | Superseded | TheFormula/drain_architecture_test.py | AR-scaled drain |
| 211_observed_ar_gate.py | Dead End | — | Observed AR gate |
| 212_two_gate.py | Dead End | — | Two-gate variant |
| 213_blended_gate.py | Dead End | — | Blended gate variant |
| 214_vertical_ara.py | Superseded | TheFormula/multispecies_vertical_ara_test.py | Vertical ARA |
| 215_singularity_gated.py | Dead End | — | Singularity gated |
| 215b_singularity_fast.py | Dead End | — | Singularity fast variant |
| 215c_singularity_fine.py | Dead End | — | Singularity fine variant |
| 216_additive_singularity.py | Dead End | — | Additive singularity |
| 217_combined_champion.py | Superseded | TheFormula/combined_predictor_test.py | Combined champion |
| 217b_combined_lean.py | Superseded | TheFormula/combined_predictor_test.py | Combined lean variant |
| 218_4d_lock.py | Historical | — | 4D lock concept |
| 218b_4d_lean.py | Dead End | — | 4D lean variant |
| 219_full_horizontal.py | Superseded | TheFormula/horizontal_map_test.py | Full horizontal |
| 220_hale_horizontal.py | Superseded | TheFormula/horizon_with_solar_test.py | Hale horizontal |
| 221_full_5d.py | Historical | — | Full 5D concept |
| 222_below_cascade.py | Historical | — | Below cascade |
| 222b_overshoot_cascade.py | Dead End | — | Overshoot cascade variant |
| 222c_wave_carried_cascade.py | Dead End | — | Wave carried cascade variant |
| 222d_phase_wave_cascade.py | Dead End | — | Phase wave cascade variant |
| 223_pressure_gate.py | Historical | — | Pressure gate concept |
| 223b_pressure_cascade.py | Dead End | — | Pressure cascade variant |
| 223c_carried_cascade.py | Dead End | — | Carried cascade variant |
| 223d_mirror_collision.py | Dead End | — | Mirror collision variant |
| 223e_triangle_hallway.py | Dead End | — | Triangle hallway variant |
| 223f_diamond_hallway.py | Superseded | TheFormula/diamond_geometry_test.py | Diamond hallway |
| 223g_beeswax_hallway.py | Historical | — | Beeswax hallway |
| 223h_beeswax_phi.py | Historical | — | Beeswax phi |
| 223i_beeswax_edge.py | Dead End | — | Beeswax edge variant |
| 223j_beeswax_smooth.py | Dead End | — | Beeswax smooth variant |
| 223k_phase_log.py | Dead End | — | Phase log variant |
| 223l_ara_beeswax.py | Historical | — | ARA beeswax |
| 223m_grief_pressure.py | Historical | — | Grief pressure concept |
| 223n_two_axes.py | Dead End | — | Two axes variant |
| 223o_best_combos.py | Dead End | — | Best combos variant |
| 223p_blended_collision.py | Dead End | — | Blended collision variant |
| 223q_ensemble.py | Superseded | TheFormula/ensemble_predictor_test.py | Ensemble concept |
| 224_ecg_cross_domain.py | Superseded | TheFormula/ecg_compass_refined_test.py | ECG cross-domain |
| 224b_wobble_solar.py | Dead End | — | Wobble solar variant |
| 225_coupled_oscillator.py | Historical | — | Coupled oscillator |
| 226_ara_bridge.py | Historical | — | ARA bridge concept |
| 236O_phase_gate.py | Dead End | — | Phase gate variant |
| 237_bidirectional.py | Historical | TheFormula/direction_prediction_test.py | Bidirectional concept |
| 237b_vertical_midline.py | Dead End | — | Vertical midline variant |
| 237c_ara_midline.py | Dead End | — | ARA midline variant |
| 237d_universal_midline.py | Dead End | — | Universal midline variant |
| 237e_cross_system.py | Superseded | TheFormula/cross_subject_reproducibility.py | Cross-system |
| 237f_valved_midline.py | Dead End | — | Valved midline variant |
| 237g_dynamic_valve.py | Dead End | — | Dynamic valve variant |
| 237h_inverse_valve.py | Dead End | — | Inverse valve variant |
| 237i_full_resolution_test.py | Superseded | TheFormula/high_res_ara_test.py | Full resolution test |
| 237j_bidirectional_valve.py | Dead End | — | Bidirectional valve variant |
| 237j2_bidirectional_lean.py | Dead End | — | Bidirectional lean variant |
| 237k_camshaft_valve.py | Superseded | TheFormula/camshaft_gate_test.py | Camshaft valve |
| 237k2_camshaft_refined.py | Superseded | TheFormula/camshaft_gate_test.py | Camshaft refined |
| 238_lynx_hare.py | Historical | — | Lynx-hare predator-prey test |
| 239_economy.py | Historical | — | Economy test |
| 240_keeling_co2.py | Historical | — | Keeling CO2 test |
| 241_nile_river.py | Superseded | TheFormula/river_prediction_test.py | Nile river test |
| 242_connection_field.py | Superseded | TheFormula/connection_field_test.py | Connection field |
| 242b_horizontal_map.py | Superseded | TheFormula/horizontal_map_test.py | Horizontal map |
| 242c_enso_coupled_network.py | Superseded | TheFormula/enso_with_feeders.py | ENSO coupled network |
| 243_phi9_atom.py | Superseded | TheFormula/phi9_atom_test.py | Phi9 atom — base version |
| 243b_atom_rider.py | Dead End | — | Atom rider variant |
| 243c_selective_atom.py | Dead End | — | Selective atom variant |
| 243d_pipe_decay.py | Dead End | — | Pipe decay variant |
| 243e_gear_atom.py | Dead End | — | Gear atom variant |
| 243f_inverted_gear.py | Dead End | — | Inverted gear variant |
| 243g_pure_gear.py | Dead End | — | Pure gear variant |
| 243h_ara_gear.py | Dead End | — | ARA gear variant |
| 243i_valve_gear.py | Dead End | — | Valve gear variant |
| 243j_temporal_gear.py | Dead End | — | Temporal gear variant |
| 243k_consumer_gear.py | Dead End | — | Consumer gear variant |
| 243k2_consumer_tilt.py | Dead End | — | Consumer tilt variant |
| 243L_accumulated_grief.py | Historical | — | Accumulated grief concept |
| 243M_valve_split.py | Dead End | — | Valve split variant |
| 243M2_pure_valve.py | Dead End | — | Pure valve variant |
| 243N_camshaft_gate.py | Superseded | TheFormula/camshaft_gate_test.py | Camshaft gate |
| 243N2_camshaft_power.py | Dead End | — | Camshaft power variant |
| 243O_breathing_gear.py | Dead End | — | Breathing gear variant |
| 243P_phi_breathing.py | Dead End | — | Phi breathing variant |
| 243Q_rung_scaled.py | Dead End | — | Rung scaled variant |
| 243R_acc_compensated.py | Dead End | — | Acc compensated variant |
| 243S_dynamic_valve.py | Dead End | — | Dynamic valve variant |
| 243T_directional_valve.py | Dead End | — | Directional valve variant |
| 243U_restoring_valve.py | Dead End | — | Restoring valve variant |
| 243V_ts_pump.py | Dead End | — | TS pump variant |
| 243W_ladder_resonance.py | Dead End | — | Ladder resonance variant |
| 243X_dynamic_ladder.py | Dead End | — | Dynamic ladder variant |
| 243Y_asymmetric_breath.py | Dead End | — | Asymmetric breath variant |
| 243Z_phi_distance_breath.py | Dead End | — | Phi distance breath variant |
| 243AA_phi_singularity_breath.py | Dead End | — | Phi singularity breath variant |
| 243AB_log_singularity.py | Dead End | — | Log singularity variant |
| 243AC_loo_validation.py | Superseded | TheFormula/canonical_benchmark.py | LOO validation |
| 243AD_engine_memory.py | Superseded | TheFormula/engine_class_test.py | Engine memory |
| 243AE_A_memory_only.py | Dead End | — | Memory-only variant |
| 243AE_B_midline_only.py | Dead End | — | Midline-only variant |
| 243AE_memory_midline.py | Dead End | — | Memory midline variant |
| 243AF_A_static_tension.py | Dead End | — | Static tension variant |
| 243AF_B_consumer_wobble.py | Dead End | — | Consumer wobble variant |
| 243AG_midline_wobble.py | Dead End | — | Midline wobble variant |
| 243AH_dynamic_amp.py | Superseded | TheFormula/combined_amplitude_test.py | Dynamic amplitude |
| 243AI_ara_accumulation.py | Dead End | — | ARA accumulation variant |
| 243AJ_amp_scale.py | Superseded | TheFormula/amp_scale_test.py | Amplitude scale |
| 243AK_gated_amp.py | Dead End | — | Gated amplitude variant |
| 243AL_carry_amp.py | Dead End | — | Carry amplitude variant |
| 243AM_blended_carry.py | Dead End | — | Blended carry variant |
| 243AN_phi_carry.py | Dead End | — | Phi carry variant |
| 243AO_asym_phi.py | Dead End | — | Asymmetric phi variant |
| 243AP_ara_map.py | Historical | — | ARA map |
| 243AQ_gleiss_vert.py | Dead End | — | Gleiss vertical variant |
| 243AR_wave_ara.py | Superseded | TheFormula/wave_ara_carry_test.py | Wave ARA |
| 243AS_reverse_gate.py | Superseded | TheFormula/reverse_gate_test.py | Reverse gate |
| 243AT_phi_offset_gate.py | Dead End | — | Phi offset gate variant |
| 243AU_frozen_valve.py | Dead End | — | Frozen valve variant |
| 243AV_reverse_triangle.py | Dead End | — | Reverse triangle variant |
| 243AW_mode_coupling.py | Historical | — | Mode coupling concept |
| 243AX_standing_wave.py | Historical | — | Standing wave concept |
| 243AY_dispersion.py | Historical | — | Dispersion concept |
| 243AZ_phi_audit.py | Dead End | — | Phi audit v1 |
| 243AZ_phi_audit_v2.py | Dead End | — | Phi audit v2 |
| 243AZ_wave_combo.py | Dead End | — | Wave combo variant |
| 243BA_path_teleport_blend.py | Dead End | — | Path teleport blend variant |
| 243BB_blend_pipeline.py | Dead End | — | Blend pipeline variant |
| 243BC_hale_modulation.py | Superseded | TheFormula/horizon_with_solar_test.py | Hale modulation |
| 243BC_hale_v2.py | Dead End | — | Hale v2 variant |
| 243BC_hale_v3_lean.py | Dead End | — | Hale v3 lean variant |
| 243BD_discrete_alternation.py | Dead End | — | Discrete alternation variant |
| 243BE_blend_winner.py | Dead End | — | Blend winner variant |
| 243BE_resonance_amplifier.py | Dead End | — | Resonance amplifier variant |
| 243BF_post_blend_stretch.py | Dead End | — | Post blend stretch variant |
| 243BG_gate_inertia.py | Superseded | TheFormula/gate_inertia_test.py | Gate inertia |
| 243BH_midline_blend.py | Dead End | — | Midline blend variant |
| 243BI_circle_expansion.py | Dead End | — | Circle expansion variant |
| 243BJ_circle_stretch.py | Dead End | — | Circle stretch variant |
| 243BK_full_validation.py | Superseded | TheFormula/canonical_benchmark.py | Full validation |
| 243BL_dark_energy.py | Historical | — | Dark energy test |
| 243BL2_dark_flip.py | Dead End | — | Dark flip variant |
| 243BL3_dark_mapping.py | Dead End | — | Dark mapping variant |
| 243BL4_info_cubed_dark.py | Superseded | TheFormula/compass_info_cubed_test.py | Info cubed dark |
| 243BL5_spacetime_lightdark.py | Historical | — | Spacetime light/dark |
| 243BL6_coupled_grid.py | Historical | — | Coupled grid |
| 243BL7_origin_of_3point5.py | Historical | — | Origin of 3.5 |
| 243BL8_meta_ara.py | Historical | — | Meta ARA |
| 243BL9_randomness_terrain.py | Historical | — | Randomness terrain |
| 243BL9b_randomness_corrected.py | Dead End | — | Randomness corrected variant |
| 243BL10_lotto_prediction.py | Historical | — | Lotto prediction test |
| 243BL11_mirror_lotto.py | Dead End | — | Mirror lotto variant |
| 243BL12_next_draw_prediction.py | Dead End | — | Next draw prediction variant |
| 243BL13_triangulator.py | Superseded | TheFormula/triangulation_test.py | Triangulator |
| 243BL14_gravitational_lens.py | Historical | — | Gravitational lens test |
| 243BL15_sp500_prediction.py | Historical | — | S&P500 prediction test |
| 243BL16_prime_ara.py | Historical | — | Prime number ARA |
| 243BL17_health_ara.py | Historical | — | Health ARA |
| 243BL18_atom_ara.py | Superseded | TheFormula/phi9_atom_test.py | Atom ARA |
| 243BL19_gravity_ara.py | Historical | — | Gravity ARA |
| 243BL20_dna_ara.py | Historical | — | DNA ARA |
| 243BL21_universe_ara.py | Historical | — | Universe ARA |
| 243BL22_singularity_ara.py | Historical | — | Singularity ARA |

---

*Note: Mappings are based on filename similarity and topical alignment. Entries marked "Review needed" or "Historical" with a TheFormula reference indicate partial overlap — the canonical version may have evolved significantly from the original script. When in doubt, the TheFormula/ version is authoritative.*
