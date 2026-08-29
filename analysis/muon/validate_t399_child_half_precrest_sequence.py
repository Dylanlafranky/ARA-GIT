#!/usr/bin/env python3
"""Independent saved-artifact checks for T399."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T399_child_half_precrest_sequence"
RESULTS = OUT / "T399_RESULTS.json"
LANDMARKS = OUT / "T399_NATIVE_LANDMARKS.csv"
LOO = OUT / "T399_LEAVE_ONE_OUT_LANDMARKS.csv"
SHIFTS = OUT / "T399_CIRCULAR_SHIFT_CONTROLS.csv"
HIST = OUT / "T399_YIELD_SENSITIVITY_HISTOGRAM.csv"
SVG = OUT / "T399_CHILD_HALF_PRECREST_SEQUENCE.svg"
HTML = OUT / "T399_CHILD_HALF_PRECREST_SEQUENCE_REPORT.html"
PROTOCOL = HERE / "T399_CHILD_HALF_PRECREST_SEQUENCE_PROTOCOL_2026-08-17.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    landmark_rows = rows(LANDMARKS)
    loo_rows = rows(LOO)
    shift_rows = rows(SHIFTS)
    hist_rows = rows(HIST)
    landmark = {row["landmark"]: row for row in landmark_rows}
    p = result["primary_native_landmarks"]
    gates = result["gates"]

    loo_fraction = sum(row["half_before_delayed_crest"].lower() == "true" for row in loo_rows) / len(loo_rows)
    as_good = sum(row["as_good_as_real"].lower() == "true" for row in shift_rows)
    p_upper = (as_good + 1) / (len(shift_rows) + 1)
    hist_fraction = sum(float(row["fraction"]) for row in hist_rows)

    checks = {
        "protocol_hash_matches": result["protocol_sha256"] == sha256(PROTOCOL),
        "four_landmarks_present": set(landmark) == {"prompt crest", "branch equality", "child half", "delayed crest"},
        "saved_native_order": float(landmark["prompt crest"]["time_us"]) < float(landmark["branch equality"]["time_us"]) < float(landmark["child half"]["time_us"]) < float(landmark["delayed crest"]["time_us"]),
        "child_half_is_exact_coordinate": close(float(landmark["child half"]["ara_x"]), 0.5),
        "native_delta_recomputes": close(0.5 - float(landmark["prompt crest"]["ara_x"]), float(p["ara_prompt_crest_to_half"])),
        "native_time_gap_recomputes": close(float(landmark["delayed crest"]["time_us"]) - float(landmark["child half"]["time_us"]), float(p["time_half_to_delayed_crest_us"])),
        "leave_one_out_row_count_18": len(loo_rows) == 18,
        "leave_one_out_fraction_recomputes": close(loo_fraction, float(result["leave_one_out"]["half_before_delayed_crest_fraction"])),
        "yield_histogram_sums_to_one": close(hist_fraction, 1.0, 1e-10),
        "circular_shift_row_count_1199": len(shift_rows) == 1199,
        "circular_shift_p_recomputes": close(p_upper, float(result["circular_shift_control"]["p_upper_add_one"])),
        "gate_1_matches_native_order": bool(gates["G1_native_four_landmark_order"]) == bool(p["full_four_landmark_order"]),
        "gate_3_matches_window": bool(gates["G3_native_quarter_compatibility"]) == (0.20 <= float(p["ara_prompt_crest_to_half"]) <= 0.30),
        "gate_4_matches_loo": bool(gates["G4_leave_one_out_half_before_crest_at_least_90pct"]) == (loo_fraction >= 0.90),
        "gate_5_matches_sensitivity": bool(gates["G5_yield_sensitivity_half_before_crest_at_least_95pct"]) == (float(result["yield_sensitivity"]["half_before_delayed_crest_fraction"]) >= 0.95),
        "gate_7_matches_shift_control": bool(gates["G7_circular_shift_alignment_p_at_most_0p05"]) == (p_upper <= 0.05),
        "svg_contains_axis_and_landmark_labels": all(token in SVG.read_text(encoding="utf-8") for token in ("time after SNS pulse", "cumulative ARA x", "child half x=0.5", "delayed crest")),
        "html_embeds_visual_and_boundaries": all(token in HTML.read_text(encoding="utf-8") for token in ("T399_CHILD_HALF_PRECREST_SEQUENCE.svg", "population timing result", "Frozen gates")),
    }
    verdict = "PASS" if all(checks.values()) else "FAIL"
    validation = {
        "test": "T399 independent saved-artifact validation",
        "verdict": verdict,
        "checks": checks,
        "files_sha256": {
            path.name: sha256(path)
            for path in (RESULTS, LANDMARKS, LOO, SHIFTS, HIST, SVG, HTML, PROTOCOL)
        },
    }
    (OUT / "T399_VALIDATION.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
