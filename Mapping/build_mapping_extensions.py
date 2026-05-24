#!/usr/bin/env python3
"""
Build the mapping-extension layer for the atlas.

This file keeps new geometry-diagnostic systems out of TheFormula. It produces
nodes for systems we want to map before asking prediction questions:
nostril dominance, tides, solar hemispheres, human gait, and MJO/QBO.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean, median


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FORMULA = ROOT / "TheFormula"
OUT = HERE / "ara_mapping_extensions.json"

PHI = (1.0 + 5.0**0.5) / 2.0
SECONDS_PER_DAY = 86400.0
SECONDS_PER_MONTH = 365.25 * SECONDS_PER_DAY / 12.0
SECONDS_PER_YEAR = 365.25 * SECONDS_PER_DAY


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def node(
    node_id: str,
    name: str,
    system: str,
    system_label: str,
    period_seconds: float,
    ara: float | None,
    weight_value: float,
    weight_label: str,
    source: str,
    notes: str,
    *,
    relation_class: str,
    orientation: str = "declared",
    measurement_status: str = "measured_or_saved_result",
    source_metric: str | None = None,
    source_count: int | float | None = None,
    extra: dict | None = None,
):
    payload = {
        "node_id": node_id,
        "name": name,
        "system": system,
        "system_label": system_label,
        "period_seconds": period_seconds,
        "ara": ara,
        "weight_value": max(float(weight_value), 1e-30),
        "weight_label": weight_label,
        "source": source,
        "layer": "mapped_extension",
        "notes": notes,
        "relation_class": relation_class,
        "orientation": orientation,
        "measurement_status": measurement_status,
    }
    if source_metric is not None:
        payload["source_metric"] = source_metric
    if source_count is not None:
        payload["source_count"] = source_count
    if extra:
        payload["extra"] = extra
    return payload


def rel(rel_id: str, a: str, b: str, rel_type: str, score: float, detail: dict):
    return {
        "id": rel_id,
        "from": a,
        "to": b,
        "type": rel_type,
        "source": "mapping_extension",
        "score": score,
        "detail": detail,
    }


def nasal_nodes(nodes, relations):
    path = FORMULA / "ara_nasal_enso_coupled_geometry_result.json"
    data = load_json(path)
    subjects = data["nasal"]["subjects"]
    interval_m = median(s["median_interval_minutes"] for s in subjects)
    signed_m = median(s["median_signed_cycle_minutes"] for s in subjects)
    n_intervals = data["nasal"]["n_train_intervals"] + data["nasal"]["n_test_intervals"]
    n_cycles = data["nasal"]["n_train_signed_cycles"] + data["nasal"]["n_test_signed_cycles"]
    symmetry_ratio = signed_m / max(1e-9, 2.0 * interval_m)
    source = "TheFormula/ara_nasal_enso_coupled_geometry_result.json"
    nodes.extend(
        [
            node(
                "mapped_nasal_left_dominance_bank",
                "Nostril left/right dominance bank",
                "mapped_nostril_dominance",
                "Nostril Dominance",
                interval_m * 60.0,
                1.0,
                n_intervals,
                "Dominance intervals",
                source,
                "Median dominance half-cycle. Treated as balanced alternation between paired nostril banks.",
                relation_class="paired_anti_phase",
                orientation="left/right alternation",
                source_metric=f"median_interval_minutes={interval_m:.1f}",
                source_count=n_intervals,
            ),
            node(
                "mapped_nasal_signed_full_cycle",
                "Nostril signed full cycle",
                "mapped_nostril_dominance",
                "Nostril Dominance",
                signed_m * 60.0,
                symmetry_ratio,
                n_cycles,
                "Signed cycles",
                source,
                "Two-dominance-interval cycle. ARA here is cycle symmetry ratio: signed_cycle / (2 * dominance_interval), not a raw left/right duration ratio.",
                relation_class="paired_anti_phase",
                orientation="full left-right-left or right-left-right cycle",
                source_metric=f"median_signed_cycle_minutes={signed_m:.1f}",
                source_count=n_cycles,
                extra={
                    "interval_test_corr": data["interval_result"]["test_corr_with_train_shift"],
                    "signed_cycle_test_corr": data["signed_cycle_result"]["test_corr_with_train_shift"],
                },
            ),
        ]
    )
    relations.append(
        rel(
            "mapped_nasal_to_enso_coupled_geometry",
            "mapped_nasal_signed_full_cycle",
            "state_enso_nino_k6",
            "mapped_vertical_partner",
            0.98,
            {
                "interpretation": "Nostril dominance and ENSO share paired anti-phase geometry; prediction use remains provisional.",
                "signed_cycle_test_corr": data["signed_cycle_result"]["test_corr_with_train_shift"],
                "dominance_interval_test_corr": data["interval_result"]["test_corr_with_train_shift"],
            },
        )
    )


def tide_nodes(nodes, relations):
    phi_results = load_json(FORMULA / "ara_phi_coupling_candidate_results.json")
    tides = phi_results["tests"]["tides"]
    amp = tides["amplitude_breathing"]
    high = amp["heldout_high_gate_range"]["mean"]
    low = amp["heldout_low_gate_range"]["mean"]
    range_ratio = high / low
    speed = tides["speed_metrics"]
    source = "TheFormula/ara_phi_coupling_candidate_results.json"
    nodes.extend(
        [
            node(
                "mapped_tide_m2_carrier",
                "Ocean tide M2 carrier",
                "mapped_tides",
                "Tides",
                speed["carrier_period_hours"] * 3600.0,
                1.138,
                amp["heldout_low_gate_range"]["p50"],
                "Heldout low-gate range m",
                source,
                "Semi-diurnal M2 carrier. ARA uses the earlier open-ocean tide asymmetry estimate; current data confirms forced carrier plus spring-neap amplitude breathing.",
                relation_class="forced_pair",
                orientation="flood/ebb window",
                source_metric="M2 open-ocean ARA estimate",
            ),
            node(
                "mapped_tide_spring_neap_envelope",
                "Spring-neap tide envelope",
                "mapped_tides",
                "Tides",
                speed["cycle_period_hours"] * 3600.0,
                1.182,
                speed["fractional_per_spring_neap_cycle"],
                "Fractional range change per cycle",
                source,
                "Spring-neap modulation. ARA uses prior spring-neap asymmetry estimate; amplitude breathing is measured in the 2024 NOAA station window.",
                relation_class="forced_pair",
                orientation="spring/neap envelope",
                source_metric="spring-neap envelope ARA estimate",
            ),
            node(
                "mapped_tide_amplitude_breath_gate",
                "Tide amplitude breath gate",
                "mapped_tides",
                "Tides",
                speed["cycle_period_hours"] * 3600.0,
                range_ratio,
                speed["high_low_range_difference_m"],
                "High-low range difference m",
                source,
                "Measured heldout high-gate mean range divided by low-gate mean range. This maps the envelope breathing rather than the carrier tide itself.",
                relation_class="amplitude_breathing_gate",
                orientation="lunar-solar gate opening/closing",
                source_metric=f"high_mean/low_mean={range_ratio:.3f}",
            ),
        ]
    )
    relations.extend(
        [
            rel(
                "mapped_tide_carrier_to_envelope",
                "mapped_tide_m2_carrier",
                "mapped_tide_spring_neap_envelope",
                "mapped_forcing_gate",
                0.93,
                {"interpretation": "M2 carrier is amplitude-modulated by the spring-neap lunar-solar envelope."},
            ),
            rel(
                "mapped_tide_envelope_to_breath_gate",
                "mapped_tide_spring_neap_envelope",
                "mapped_tide_amplitude_breath_gate",
                "mapped_forcing_gate",
                0.95,
                {"interpretation": "Envelope gate produces measured amplitude breathing in tide range."},
            ),
        ]
    )


def solar_hemisphere_nodes(nodes, relations):
    data = load_json(FORMULA / "ara_phi_coupling_candidate_results.json")["tests"]["solar_north_south"]
    source = "TheFormula/ara_phi_coupling_candidate_results.json"
    north_cycles = data["cycles"]["north"]
    south_cycles = data["cycles"]["south"]

    def period_months(cycles):
        return median(c["end"] - c["start"] for c in cycles)

    north_period = period_months(north_cycles)
    south_period = period_months(south_cycles)
    north_ara = data["cycles"]["north_ara"]["p50"]
    south_ara = data["cycles"]["south_ara"]["p50"]
    speed = data["speed_metrics"]
    gate_period = median([north_period, south_period])
    nodes.extend(
        [
            node(
                "mapped_solar_north_hemisphere",
                "Solar northern hemisphere cycle",
                "mapped_solar_hemispheres",
                "Solar Hemispheres",
                north_period * SECONDS_PER_MONTH,
                north_ara,
                data["cycles"]["north_ara"]["n"],
                "Detected cycles",
                source,
                "SILSO hemispheric Catalogue B saved result. ARA is median cycle fall/rise ratio for the northern hemisphere.",
                relation_class="stellar_coupled_pair",
                orientation="rise/fall sunspot hemisphere",
                source_metric=f"median_cycle_months={north_period:.1f}",
                source_count=data["cycles"]["north_ara"]["n"],
            ),
            node(
                "mapped_solar_south_hemisphere",
                "Solar southern hemisphere cycle",
                "mapped_solar_hemispheres",
                "Solar Hemispheres",
                south_period * SECONDS_PER_MONTH,
                south_ara,
                data["cycles"]["south_ara"]["n"],
                "Detected cycles",
                source,
                "SILSO hemispheric Catalogue B saved result. ARA is median cycle fall/rise ratio for the southern hemisphere.",
                relation_class="stellar_coupled_pair",
                orientation="rise/fall sunspot hemisphere",
                source_metric=f"median_cycle_months={south_period:.1f}",
                source_count=data["cycles"]["south_ara"]["n"],
            ),
            node(
                "mapped_solar_ns_relaxation_gate",
                "Solar N/S relaxation gate",
                "mapped_solar_hemispheres",
                "Solar Hemispheres",
                gate_period * SECONDS_PER_MONTH,
                speed["fractional_toward_balance_per_cycle"],
                speed["relative_damping_per_cycle"],
                "Relative damping per cycle",
                source,
                "Coupling-speed diagnostic: fractional movement toward hemisphere balance per cycle is near phi in the saved heldout test.",
                relation_class="balance_relaxation_gate",
                orientation="north/south balance relaxation",
                source_metric="fractional_toward_balance_per_cycle",
            ),
        ]
    )
    relations.extend(
        [
            rel(
                "mapped_solar_north_south_pair",
                "mapped_solar_north_hemisphere",
                "mapped_solar_south_hemisphere",
                "mapped_counter_pair",
                0.92,
                {"interpretation": "Solar hemispheres form a coupled dynamo pair with different cycle ARA medians."},
            ),
            rel(
                "mapped_solar_pair_to_relaxation_gate",
                "mapped_solar_ns_relaxation_gate",
                "mapped_solar_north_hemisphere",
                "mapped_balance_gate",
                0.91,
                {"fractional_toward_balance_per_cycle": speed["fractional_toward_balance_per_cycle"]},
            ),
            rel(
                "mapped_solar_pair_to_relaxation_gate_south",
                "mapped_solar_ns_relaxation_gate",
                "mapped_solar_south_hemisphere",
                "mapped_balance_gate",
                0.91,
                {"fractional_toward_balance_per_cycle": speed["fractional_toward_balance_per_cycle"]},
            ),
        ]
    )


def gait_nodes(nodes, relations):
    source = "analysis/gait/analyze_gait_phi.py"
    arc_source = "analysis/gait/analyze_running_phi.py"
    gait_period = 1.11
    group_data = [
        ("mapped_gait_control", "Gait control median", 1.3548, 8591, "unimodal, narrow", "16.27%"),
        ("mapped_gait_parkinsons", "Gait Parkinson's median", 1.4414, 7593, "broader, slight bimodality", "10.92%"),
        ("mapped_gait_als", "Gait ALS median", 1.4651, 5193, "clear bimodal: walking peak plus secondary near 1.0-1.1", "9.45%"),
        ("mapped_gait_huntingtons", "Gait Huntington's median", 1.3615, 10148, "broad, asymmetric", "15.85%"),
    ]
    for node_id, name, ara, count, shape, phi_dev in group_data:
        nodes.append(
            node(
                node_id,
                name,
                "mapped_human_gait",
                "Human Gait",
                gait_period,
                ara,
                count,
                "Stride count",
                source,
                f"PhysioNet gaitndd raw rerun on 2026-05-24. Controlled instructed-walk data, not open-environment natural gait. Distribution shape: {shape}. Deviation from phi: {phi_dev}.",
                relation_class="locomotion_stride_geometry",
                orientation="stance/swing",
                source_metric="median stance/swing",
                source_count=count,
                measurement_status="raw_physionet_rerun_2026_05_24",
            )
        )
    nodes.extend(
        [
            node(
                "mapped_gait_preferred_phi_crossing",
                "Preferred walking phi crossing",
                "mapped_human_gait",
                "Human Gait",
                1.0,
                PHI,
                1.27,
                "Speed m/s",
                arc_source,
                "Literature locomotion arc: preferred/energy-optimal walking crosses stance/swing = phi around 1.27 m/s.",
                relation_class="locomotion_arc_anchor",
                orientation="stance/swing",
                source_metric="speed_at_phi_mps=1.27",
                measurement_status="literature_curve_saved_result",
            ),
            node(
                "mapped_gait_walk_run_transition",
                "Walk-run transition",
                "mapped_human_gait",
                "Human Gait",
                0.75,
                1.0,
                2.2,
                "Speed m/s",
                arc_source,
                "Literature locomotion arc: stance and swing equalize at the walk-run transition.",
                relation_class="locomotion_arc_boundary",
                orientation="stance/swing",
                source_metric="speed_at_unity_mps=2.2",
                measurement_status="literature_curve_saved_result",
            ),
            node(
                "mapped_gait_run_mirror_phi_crossing",
                "Sustainable running mirror-phi crossing",
                "mapped_human_gait",
                "Human Gait",
                0.65,
                1.0 / PHI,
                3.85,
                "Speed m/s",
                arc_source,
                "Literature locomotion arc: the running-side mirror of preferred walking crosses stance/swing = 1/phi around 3.85 m/s. This marks the sustainable running branch, not the first moment the body should switch from walking to running.",
                relation_class="locomotion_arc_anchor",
                orientation="stance/swing",
                source_metric="speed_at_inverse_phi_mps=3.85",
                measurement_status="literature_curve_saved_result",
            ),
            node(
                "mapped_gait_als_collapse_peak",
                "ALS secondary collapse peak",
                "mapped_human_gait",
                "Human Gait",
                gait_period,
                1.05,
                1.0,
                "Collapse peak marker",
                "GAIT_LOCOMOTION_ARC.md",
                "Approximate secondary peak reported near 1.0-1.1 in ALS gait. This is mapped as a diagnostic rung-collapse marker, not a precise fitted coordinate.",
                relation_class="rung_collapse_marker",
                orientation="stance/swing",
                source_metric="secondary peak near 1.0-1.1",
                measurement_status="approximate_from_saved_writeup",
            ),
        ]
    )
    relations.extend(
        [
            rel(
                "mapped_gait_control_to_phi_crossing",
                "mapped_gait_control",
                "mapped_gait_preferred_phi_crossing",
                "mapped_arc_progression",
                0.86,
                {"interpretation": "Control subjects were measured in a controlled instructed-walk setting slower than preferred natural speed, so median sits below phi on the locomotion arc."},
            ),
            rel(
                "mapped_gait_phi_crossing_to_walk_run_transition",
                "mapped_gait_preferred_phi_crossing",
                "mapped_gait_walk_run_transition",
                "mapped_arc_progression",
                0.9,
                {"interpretation": "As speed rises from preferred walking, stance/swing moves from phi toward 1.0, the walk-run handoff boundary."},
            ),
            rel(
                "mapped_gait_transition_to_run_mirror_phi",
                "mapped_gait_walk_run_transition",
                "mapped_gait_run_mirror_phi_crossing",
                "mapped_arc_progression",
                0.88,
                {"interpretation": "After the walk-run handoff, the consumer-side running branch approaches the mirror-phi sustainable running anchor."},
            ),
            rel(
                "mapped_gait_als_to_collapse_peak",
                "mapped_gait_als",
                "mapped_gait_als_collapse_peak",
                "mapped_rung_collapse",
                0.9,
                {"interpretation": "ALS distribution is bimodal; secondary peak near 1.0 is mapped as candidate rung collapse."},
            ),
        ]
    )


def mjo_qbo_nodes(nodes, relations):
    qbo = load_json_from_js(FORMULA / "qbo_annual_data.js", "window.QBO_ANNUAL =")
    mjo = load_json_from_js(FORMULA / "enso_mjo_partner_data.js", "window.ENSO_MJO_PARTNER =")
    qbo_k7_ara = qbo["fingerprints"]["QBO"][3]
    qbo_k7_power = qbo["qbo_band_distribution"]["7"]
    source_qbo = "TheFormula/qbo_annual_data.js"
    source_mjo = "TheFormula/enso_mjo_partner_data.js"
    nodes.extend(
        [
            node(
                "mapped_qbo_k7_feeder",
                "QBO k7 feeder",
                "mapped_climate_feeders",
                "MJO / QBO Climate Feeders",
                qbo["rungs"][3][1] * SECONDS_PER_MONTH,
                qbo_k7_ara,
                qbo_k7_power,
                "QBO band power fraction",
                source_qbo,
                "NOAA QBO saved analysis. Power concentrates at phi^7 (~29 months); ARA shown is the k7 annual-fingerprint value from the saved test.",
                relation_class="climate_feeder",
                orientation="westerly/easterly phase",
                source_metric=f"k7_power_fraction={qbo_k7_power:.3f}",
            ),
            node(
                "mapped_mjo_omi_50d_partner",
                "MJO OMI 50-day partner",
                "mapped_climate_feeders",
                "MJO / QBO Climate Feeders",
                50.0 * SECONDS_PER_DAY,
                1.0,
                mjo["n_aligned_months"],
                "Aligned months",
                source_mjo,
                "NOAA OMI MJO partner saved test. Period is the 50-day MJO envelope used in the vertical-ARA test. ARA was not directly measured in that artifact, so this is mapped as a balanced propagating envelope until raw cycle ARA is measured.",
                relation_class="vertical_partner_candidate",
                orientation="MJO phase envelope",
                source_metric=f"enso_mjo_phi_gap={mjo['phi_k_stretch']:.2f}",
                source_count=mjo["n_aligned_months"],
                measurement_status="period_measured_ara_pending",
            ),
        ]
    )
    relations.extend(
        [
            rel(
                "mapped_mjo_to_enso_vertical_partner",
                "mapped_mjo_omi_50d_partner",
                "state_enso_nino_k5",
                "mapped_vertical_partner",
                0.82,
                {
                    "rung_gap_phi": mjo["phi_k_stretch"],
                    "interpretation": "MJO is about 6.94 phi-rungs below ENSO's ~47-month home scale in the saved partner test.",
                },
            ),
            rel(
                "mapped_qbo_to_enso_same_rung_feeder",
                "mapped_qbo_k7_feeder",
                "state_enso_nino_k5",
                "mapped_feeder",
                0.84,
                {
                    "interpretation": "QBO sits near the ENSO feeder/home period band and is mapped as a climate feeder layer.",
                    "qbo_power_k7": qbo_k7_power,
                },
            ),
        ]
    )


def cross_scale_anchor_nodes(nodes, relations):
    """Add a bell-curve spread of period anchors from quantum to cosmic scale.

    These are geometry-mapping anchors selected from the older archive ladder
    work. They are not prediction features and they do not assert causal links
    between adjacent scales.
    """
    ev_j = 1.602176634e-19
    source_real = "archive/numbered_tests/94_real_ara_measurements.py"
    source_gap = "archive/numbered_tests/89_gap_filling_scales.py"
    source_quantum = "archive/numbered_tests/92_subatomic_slope_inversion.py"
    source_sleep = "archive/numbered_tests/64_sleep_consciousness_ara.py"
    source_chem = "archive/numbered_tests/50_chemical_oscillators_ara.py"
    source_galactic_test = "Mapping/galactic_rotation_phi_test_result.json"
    galactic_test_path = HERE / "galactic_rotation_phi_test_result.json"
    galactic_test = load_json(galactic_test_path) if galactic_test_path.exists() else {}
    galactic_summary = galactic_test.get("summary", {})
    galactic_period_myr = galactic_summary.get("solar_nearest_orbital_period_myr", 230.0)
    galactic_carrier_ara = galactic_summary.get("pure_circular_carrier_ara", 1.0)
    galactic_median_kappa = galactic_summary.get("median_kappa_over_omega")
    galactic_global_kappa = galactic_summary.get("global_kappa_over_omega")
    galactic_period_error = galactic_summary.get("atlas_period_error_fraction")
    if galactic_median_kappa is not None:
        galactic_metric = (
            f"solar orbital period={galactic_period_myr:.2f}Myr; "
            f"carrier ARA={galactic_carrier_ara:.2f}; "
            f"median kappa/Omega={galactic_median_kappa:.3f}; "
            "phi_supported=False"
        )
        galactic_notes = (
            "Gaia DR3 Cepheid rotation-curve diagnostic supports the rough galactic-year period "
            "near the solar radius but rejects the archived phi ARA assignment. The pure circular "
            "carrier has neutral ARA=1.0; the measured epicyclic coupling is closer to the "
            "flat-curve sqrt(2) geometry than to phi."
        )
    else:
        galactic_metric = "period~230Myr; galactic phi test result missing"
        galactic_notes = (
            "Fallback cosmic anchor for the Milky Way galactic year. Run "
            "Mapping/galactic_rotation_phi_test.py before treating this as measured."
        )
    anchors = [
        {
            "id": "mapped_scale_molecular_vibration",
            "name": "Molecular vibration",
            "system": "mapped_scale_molecular_vibration",
            "label": "Molecular Vibration",
            "period": 1.0e-14,
            "ara": 1.0,
            "weight": 0.1 * ev_j,
            "weight_label": "Energy J",
            "source": source_quantum,
            "notes": "Archive anchor: representative molecular vibrational period. ARA is treated as a balanced oscillator placeholder until bond-specific rise/fall asymmetry is measured.",
            "relation_class": "quantum_molecular_anchor",
            "orientation": "bond stretch/compress",
            "metric": "period=1e-14s; energy~0.1eV",
        },
        {
            "id": "mapped_scale_alpha_helix_formation",
            "name": "Alpha-helix formation",
            "system": "mapped_scale_alpha_helix",
            "label": "Alpha-Helix",
            "period": 100.0e-9,
            "ara": 1.0,
            "weight": 10 ** -19.8,
            "weight_label": "Archived energy proxy",
            "source": source_real,
            "notes": "Archive cellular/molecular anchor. Kept as a conservative bounded position here; later archive correction discusses possible folding/unfolding overflow and should be tested separately.",
            "relation_class": "protein_folding_anchor",
            "orientation": "fold/unfold",
            "metric": "archive period=100ns",
        },
        {
            "id": "mapped_scale_atp_synthase_rotation",
            "name": "ATP synthase rotation",
            "system": "mapped_scale_atp_synthase",
            "label": "ATP Synthase",
            "period": 0.01,
            "ara": 1.50,
            "weight": 8.3e-20,
            "weight_label": "Energy J",
            "source": source_chem,
            "notes": "ATP-specific chemical-oscillator rerun maps ATP synthase as a three-phase rotary engine at ARA=1.50, near phi. This supersedes the broader archive ladder placeholder that had ARA=3.0. The coupled rotor/gradient idea remains testable, but it needs real substep dwell-time data rather than hard-coded child coordinates.",
            "relation_class": "molecular_rotary_motor",
            "orientation": "three-phase rotary catalysis",
            "metric": "period=10ms; ARA=1.50 from chemical oscillator rerun",
        },
        {
            "id": "mapped_scale_human_breathing",
            "name": "Human breathing",
            "system": "mapped_scale_human_breathing",
            "label": "Human Breathing",
            "period": 4.0,
            "ara": PHI,
            "weight": 0.5,
            "weight_label": "Breath energy proxy J",
            "source": source_real,
            "notes": "Archive organism anchor: resting respiratory rhythm. This is useful as a middle-scale self-organising biological oscillator, not a fresh raw respiratory fit.",
            "relation_class": "respiratory_self_organising_anchor",
            "orientation": "inspiration/expiration",
            "metric": "period=4s; archived ARA=phi",
        },
        {
            "id": "mapped_scale_circadian_sleep_wake",
            "name": "Circadian sleep-wake",
            "system": "mapped_scale_circadian_sleep_wake",
            "label": "Circadian Sleep-Wake",
            "period": SECONDS_PER_DAY,
            "ara": 2.0,
            "weight": 1.0,
            "weight_label": "Behavioral cycle proxy",
            "source": source_sleep,
            "notes": "Archive sleep/consciousness anchor: 16h wake / 8h sleep gives ARA=2.0. This is a human behavioral convention, not a universal biological constant.",
            "relation_class": "circadian_boundary_anchor",
            "orientation": "wake/sleep",
            "metric": "16h/8h=2.0",
        },
        {
            "id": "mapped_scale_chandler_wobble",
            "name": "Chandler wobble",
            "system": "mapped_scale_chandler_wobble",
            "label": "Chandler Wobble",
            "period": 433.0 * SECONDS_PER_DAY,
            "ara": 1.0,
            "weight": 10 ** 20.0,
            "weight_label": "Archived energy proxy",
            "source": source_real,
            "notes": "Archive planetary rotational anchor. Marked balanced because the prior note treats the pole motion as symmetric circular motion.",
            "relation_class": "planetary_rotational_anchor",
            "orientation": "pole wobble cycle",
            "metric": "period=433d",
        },
        {
            "id": "mapped_scale_lunar_nodal_cycle",
            "name": "Lunar nodal cycle",
            "system": "mapped_scale_lunar_nodal",
            "label": "Lunar Nodal Cycle",
            "period": 587088000.0,
            "ara": 1.0,
            "weight": 10 ** 22.7,
            "weight_label": "Archived energy proxy",
            "source": source_real,
            "notes": "Archive orbital anchor: symmetric lunar nodal regression. This is separate from the semi-diurnal M2 tide and the spring-neap envelope.",
            "relation_class": "orbital_regression_anchor",
            "orientation": "node regression",
            "metric": "period~18.6y",
        },
        {
            "id": "mapped_scale_milankovitch_obliquity",
            "name": "Milankovitch obliquity",
            "system": "mapped_scale_milankovitch_obliquity",
            "label": "Milankovitch Obliquity",
            "period": 41000.0 * SECONDS_PER_YEAR,
            "ara": 1.0,
            "weight": 10 ** 26.3,
            "weight_label": "Archived energy proxy",
            "source": source_real,
            "notes": "Archive planetary orbital anchor: symmetric axial-tilt oscillation. Useful as the slow Earth-system end of the mapping ladder.",
            "relation_class": "orbital_forcing_anchor",
            "orientation": "tilt high/low",
            "metric": "period~41kyr",
        },
        {
            "id": "mapped_scale_spiral_arm_passage",
            "name": "Spiral arm passage",
            "system": "mapped_scale_spiral_arm_passage",
            "label": "Spiral Arm Passage",
            "period": 120.0e6 * SECONDS_PER_YEAR,
            "ara": 1.2,
            "weight": 10 ** 46.0,
            "weight_label": "Archived energy proxy",
            "source": source_real,
            "notes": "Archive cosmic anchor. Later correction notes slight compression/expansion asymmetry, so this is mapped at ARA=1.2 rather than the initial balanced placeholder.",
            "relation_class": "galactic_structure_anchor",
            "orientation": "arm entry/exit",
            "metric": "period~120Myr; corrected ARA=1.2",
        },
        {
            "id": "mapped_scale_galactic_rotation_mw",
            "name": "Galactic rotation MW",
            "system": "mapped_scale_galactic_rotation",
            "label": "Galactic Rotation",
            "period": galactic_period_myr * 1.0e6 * SECONDS_PER_YEAR,
            "ara": galactic_carrier_ara,
            "weight": 10 ** 48.0,
            "weight_label": "Archived energy proxy",
            "source": source_galactic_test,
            "notes": galactic_notes,
            "relation_class": "galactic_orbital_anchor",
            "orientation": "galactic orbit",
            "metric": galactic_metric,
            "status": "measured_rotation_curve_phi_rejected",
            "extra": {
                "archived_prior_source": source_gap,
                "archived_prior_ara": PHI,
                "global_kappa_over_omega": galactic_global_kappa,
                "median_kappa_over_omega": galactic_median_kappa,
                "atlas_230myr_period_error_fraction": galactic_period_error,
            },
        },
    ]

    for item in anchors:
        nodes.append(
            node(
                item["id"],
                item["name"],
                item["system"],
                item["label"],
                item["period"],
                item["ara"],
                item["weight"],
                item["weight_label"],
                item["source"],
                item["notes"],
                relation_class=item["relation_class"],
                orientation=item["orientation"],
                source_metric=item["metric"],
                measurement_status=item.get("status", "archived_cross_scale_anchor"),
                extra=item.get("extra"),
            )
        )

    for left, right in zip(anchors, anchors[1:]):
        relations.append(
            rel(
                f"{left['id']}_to_{right['id']}",
                left["id"],
                right["id"],
                "mapped_scale_ladder_step",
                0.72,
                {
                    "interpretation": "Adjacent cross-scale mapping anchors. This is a visual scale ladder, not a causal transfer claim.",
                    "left_period_seconds": left["period"],
                    "right_period_seconds": right["period"],
                },
            )
        )


def load_json_from_js(path: Path, assignment: str):
    text = path.read_text(encoding="utf-8")
    body = text.split(assignment, 1)[1].strip()
    if body.endswith(";"):
        body = body[:-1]
    return json.loads(body)


def main():
    nodes = []
    relations = []
    nasal_nodes(nodes, relations)
    tide_nodes(nodes, relations)
    solar_hemisphere_nodes(nodes, relations)
    gait_nodes(nodes, relations)
    mjo_qbo_nodes(nodes, relations)
    cross_scale_anchor_nodes(nodes, relations)
    payload = {
        "date": "2026-05-24",
        "purpose": "Mapping extension layer for diagnostic systems: nostril dominance, tides, solar hemispheres, human gait, MJO/QBO, and a 10-system quantum-to-cosmic cross-scale anchor ladder.",
        "nodes": nodes,
        "relations": relations,
        "summary": {
            "node_count": len(nodes),
            "relation_count": len(relations),
            "systems": sorted({n["system"] for n in nodes}),
        },
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"extension nodes={len(nodes)} relations={len(relations)}")
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
