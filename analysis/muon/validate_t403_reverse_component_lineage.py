from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T403_reverse_component_lineage"
PROTOCOL = ROOT / "T403_REVERSE_COMPONENT_LINEAGE_PROTOCOL_2026-08-18.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unit_center(v: np.ndarray) -> np.ndarray:
    z = np.asarray(v, dtype=float) - np.mean(v)
    return z / np.linalg.norm(z)


results = json.loads((OUT / "T403_RESULTS.json").read_text(encoding="utf-8"))
scores = pd.read_csv(OUT / "T403_COMPONENT_SCORES.csv")
profiles = pd.read_csv(OUT / "T403_COMPONENT_PROFILES.csv")
splits = pd.read_csv(OUT / "T403_SPLIT_ROBUSTNESS.csv")
flavor = pd.read_csv(OUT / "T403_FLAVOR_SHAPE_DIAGNOSTIC.csv")

detector = (
    profiles[profiles["series"] == "T402 detector C-AC"]
    .sort_values("ara_x")["raw_value"]
    .to_numpy(float)
)
best_row = scores.sort_values(
    ["absolute_cosine", "registered_shift_rank_of_8"], ascending=[False, True]
).iloc[0]
best_profile = (
    profiles[profiles["series"] == best_row["candidate"]]
    .sort_values("ara_x")["raw_value"]
    .to_numpy(float)
)
if best_row["orientation"] == "reversed":
    best_profile = best_profile[::-1]
recomputed_cosine = float(np.dot(unit_center(detector), unit_center(best_profile)))

whole = scores[
    scores["candidate"].isin(
        ["delayed total release", "nu_e release", "anti_nu_mu release"]
    )
]
max_whole = float(whole["absolute_cosine"].max())

summary = results["split_robustness"]
checks = {
    "protocol_hash_matches": results["protocol_sha256"] == sha256(PROTOCOL),
    "eight_detector_bins": len(detector) == 8,
    "detector_coordinate_is_ordered_0_to_2": bool(
        profiles[profiles["series"] == "T402 detector C-AC"]["ara_x"].is_monotonic_increasing
        and profiles[profiles["series"] == "T402 detector C-AC"]["ara_x"].min() > 0
        and profiles[profiles["series"] == "T402 detector C-AC"]["ara_x"].max() < 2
    ),
    "selected_candidate_matches_score_table": (
        best_row["candidate"] == results["selected_same_archive_candidate"]["candidate"]
        and best_row["orientation"] == results["selected_same_archive_candidate"]["orientation"]
    ),
    "selected_cosine_recomputes": np.isclose(
        recomputed_cosine,
        results["selected_same_archive_candidate"]["cosine"],
        atol=1e-12,
    ),
    "max_whole_rate_recomputes": np.isclose(
        max_whole,
        results["selected_same_archive_candidate"]["max_whole_positive_rate_absolute_cosine"],
        atol=1e-12,
    ),
    "split_count_is_326": len(splits) == 326,
    "split_median_recomputes": np.isclose(
        splits["cosine"].median(), summary["median_cosine"], atol=1e-12
    ),
    "split_95_interval_recomputes": np.allclose(
        splits["cosine"].quantile([0.025, 0.975]).to_numpy(float),
        np.asarray(summary["resampling_interval_95"], dtype=float),
        atol=1e-12,
    ),
    "flavor_diagnostic_has_two_orientations": set(flavor["orientation"]) == {"direct", "reversed"},
    "flavor_children_are_highly_collinear": results["post_frozen_flavor_identifiability"]["nu_e_vs_anti_nu_mu_centered_cosine"] > 0.99,
    "flavor_specific_shape_not_selected": abs(
        results["post_frozen_flavor_identifiability"]["area_normalized_flavor_shape_contrast_direct_cosine"]
    ) < 0.65,
    "t397_is_explicitly_separate": "separate" in results["evidence_classes"]["T397"].lower(),
    "individual_birth_boundary_present": any(
        "individual neutrino birth" in item.lower() for item in results["boundaries"]
    ),
    "gate_logic_matches_partial_verdict": (
        results["gates"]["G1_detector_integrity"]
        and results["gates"]["G2_component_selection"]
        and results["gates"]["G3_alignment_control"]
        and not results["gates"]["G4_derivative_specificity"]
        and results["gates"]["G5_evidence_boundary"]
        and results["verdict"] == "PARTIAL COMPONENT RELATION"
    ),
}
checks = {key: bool(value) for key, value in checks.items()}

validation = {
    "test": "T403 validation",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "recomputed": {
        "selected_cosine": recomputed_cosine,
        "max_whole_rate_absolute_cosine": max_whole,
        "split_median_cosine": float(splits["cosine"].median()),
        "split_interval_95": splits["cosine"].quantile([0.025, 0.975]).tolist(),
    },
    "confidence": "Share with caveats",
    "required_caveats": [
        "The detector contrast is not a pristine neutrino waveform.",
        "The high aggregate match is shared by both flavor templates and does not identify one flavor child.",
        "Split-level resemblance is weak and variable.",
        "T397 is a separate experiment and cannot establish event-linked ancestry.",
    ],
}

(OUT / "T403_VALIDATION.json").write_text(
    json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps(validation, indent=2, ensure_ascii=False))
raise SystemExit(0 if validation["status"] == "PASS" else 1)
