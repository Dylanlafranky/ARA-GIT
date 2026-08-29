from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T404_corrected_child_release_diara"
PROTOCOL = ROOT / "T404_CORRECTED_CHILD_RELEASE_DIARA_PROTOCOL_2026-08-18.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


results = json.loads((OUT / "T404_RESULTS.json").read_text(encoding="utf-8"))
mapping = pd.read_csv(OUT / "T404_COORDINATE_MAPPING.csv")
landmarks = pd.read_csv(OUT / "T404_REGISTERED_LANDMARKS.csv")
bootstrap = pd.read_csv(OUT / "T404_BOOTSTRAP.csv")
diara = pd.read_csv(OUT / "T404_STORAGE_FLOW_DIARA.csv")
profiles = pd.read_csv(OUT / "T404_CORRECTED_PROFILES.csv")

valid = bootstrap[bootstrap["valid"].astype(bool)]
interval = valid["detector_octave_residual"].quantile([0.025, 0.975]).to_numpy(float)
coord = results["coordinate_audit"]
summary = results["registered_bandwidth_summary"]
gates = results["gates"]

checks = {
    "protocol_hash_matches": results["protocol_sha256"] == sha256(PROTOCOL),
    "mapping_has_eight_registered_bins": len(mapping) == 8,
    "corrected_times_are_monotonic": mapping["correct_time_us"].is_monotonic_increasing,
    "linear_and_corrected_maps_are_not_equal": float(mapping["time_error_us"].abs().max()) > 0.05,
    "corrected_crest_reproduces_saved_T400": np.isclose(
        coord["saved_T400_local_crest"],
        coord["corrected_reconstructed_local_crest"],
        atol=1e-12,
    ),
    "four_registered_bandwidths_present": len(landmarks) == 4,
    "three_stage_order_recomputes": bool(
        (
            (landmarks["detector_crest_x"] < landmarks["source_release_crest_x"])
            & (landmarks["source_release_crest_x"] < landmarks["detector_ridge_x"])
        ).all()
    ),
    "registered_detector_ratio_range_recomputes": np.allclose(
        landmarks["detector_to_ridge_ratio"].agg(["min", "max"]).to_numpy(float),
        np.asarray(summary["detector_to_ridge_ratio_range"], dtype=float),
        atol=1e-12,
    ),
    "registered_source_residual_range_recomputes": np.allclose(
        landmarks["source_octave_residual"].agg(["min", "max"]).to_numpy(float),
        np.asarray(summary["source_octave_residual_range"], dtype=float),
        atol=1e-12,
    ),
    "bootstrap_count_is_5000": len(bootstrap) == 5000,
    "bootstrap_all_valid": len(valid) == 5000,
    "bootstrap_order_fraction_recomputes": np.isclose(
        valid["ordered_three_stage"].astype(bool).mean(),
        results["bootstrap"]["three_stage_fraction"],
        atol=1e-12,
    ),
    "bootstrap_interval_recomputes": np.allclose(
        interval,
        np.asarray(results["bootstrap"]["detector_octave_residual_95_interval"], dtype=float),
        atol=1e-12,
    ),
    "diara_coordinates_are_bounded": bool(
        diara[["storage_ara", "release_flow_ara"]].min().min() >= -1e-12
        and diara[["storage_ara", "release_flow_ara"]].max().max() <= 2 + 1e-12
    ),
    "diara_has_all_four_registered_stages": set(diara["stage"])
    == {"pre-turn storage", "turn to release", "release to handover", "post-handover"},
    "detector_profile_keeps_eight_bins": len(profiles[profiles["series"] == "detector C-AC"]) == 8,
    "gate_logic_coordinate": gates["G1_correct_inverse_map_reproduces_T400_crest"],
    "gate_logic_three_stage": gates["G2_three_stage_all_registered_bandwidths"]
    and gates["G3_three_stage_bootstrap_at_least_90pct"],
    "source_octave_is_rejected": not gates["G5_exact_source_octave_across_bandwidths"],
    "individual_event_claim_is_blocked": not gates["G7_individual_spinning_muon_event_link_available"],
}
checks = {key: bool(value) for key, value in checks.items()}

validation = {
    "test": "T404 independent saved-output validation",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "recomputed": {
        "three_stage_fraction": float(valid["ordered_three_stage"].astype(bool).mean()),
        "detector_octave_residual_95_interval": interval.tolist(),
        "source_octave_residual_range": landmarks["source_octave_residual"].agg(["min", "max"]).tolist(),
    },
    "confidence": "Share with caveats",
    "required_caveats": [
        "T404 is a correction audit performed after the T403 mapping defect was seen.",
        "The saved T402 resampling probes overlap and are not independent experiments.",
        "The Di-ARA storage and flow axes are derived from the same fitted delayed template.",
        "The source-release octave is rejected; the detector-turn octave remains bootstrap-compatible but its registered point estimates are systematically shorter than 2:1.",
        "No individual spinning-muon decay is event-linked in these inputs.",
    ],
}

(OUT / "T404_VALIDATION.json").write_text(
    json.dumps(validation, indent=2), encoding="utf-8"
)
print(json.dumps(validation, indent=2))
raise SystemExit(0 if validation["status"] == "PASS" else 1)
