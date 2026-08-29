from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np
import pandas as pd


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
LOCK = ROOT / "T432_FREEZE_LOCK.json"
PROTOCOL = ROOT / "T432_FROZEN_PROTOCOL.md"
MANIFEST = ROOT / "T432_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
CORE = ROOT / "t432_lagged_pushpull_settlement.py"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile_high(value: float, controls: np.ndarray) -> float:
    controls = controls[np.isfinite(controls)]
    return float((np.sum(controls < value) + 0.5 * np.sum(controls == value)) / len(controls))


def percentile_low(value: float, controls: np.ndarray) -> float:
    controls = controls[np.isfinite(controls)]
    return float((np.sum(controls > value) + 0.5 * np.sum(controls == value)) / len(controls))


def main() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    freeze = {
        "protocol_sha256": sha256(PROTOCOL),
        "source_manifest_sha256": sha256(MANIFEST),
        "analysis_script_sha256_at_freeze": sha256(CORE),
    }
    freeze_ok = all(freeze[key].lower() == str(lock[key]).lower() for key in freeze)

    development = pd.read_csv(RESULTS / "T432_DEVELOPMENT_EVENTS.csv")
    events = pd.read_csv(RESULTS / "T432_CONFIRMATION_EVENTS.csv")
    controls = pd.read_csv(RESULTS / "T432_CONFIRMATION_OFFSOURCE_CONTROLS.csv")
    histories = pd.read_csv(RESULTS / "T432_CONFIRMATION_HISTORIES.csv")
    qa = pd.read_csv(RESULTS / "T432_CONFIRMATION_SOURCE_QA.csv")
    gates = json.loads((RESULTS / "T432_CONFIRMATION_GATES.json").read_text(encoding="utf-8"))

    percentile_checks: list[bool] = []
    for _, row in events.iterrows():
        off = controls.loc[controls.event == row.event]
        expected = {
            "pushpull_percentile": percentile_high(row.pushpull_score, off.pushpull_score.to_numpy()),
            "speed_settlement_percentile": percentile_high(row.speed_settlement, off.speed_settlement.to_numpy()),
            "radius_settlement_percentile": percentile_high(row.radius_settlement, off.radius_settlement.to_numpy()),
            "corner_avoidance_percentile": percentile_low(row.top_left_occupancy, off.top_left_occupancy.to_numpy()),
        }
        percentile_checks.extend(abs(float(row[key]) - value) <= 1e-12 for key, value in expected.items())

    recomputed = {
        "G1_dynamic_4_of_6": bool((events.pushpull_percentile >= 0.95).sum() >= 4),
        "G2_settlement_4_of_6": bool(
            ((events.speed_settlement_percentile >= 0.90) & (events.radius_settlement_percentile >= 0.90)).sum() >= 4
        ),
        "G3_detector_3_of_6": bool(
            ((events.H1_pushpull_percentile >= 0.90) & (events.L1_pushpull_percentile >= 0.90)).sum() >= 3
        ),
        "G4_corner_4_of_6": bool((events.corner_avoidance_percentile >= 0.90).sum() >= 4),
    }
    recomputed["dynamic_handover_supported"] = bool(
        recomputed["G1_dynamic_4_of_6"] and recomputed["G2_settlement_4_of_6"]
    )
    gates_ok = all(bool(gates[key]) == value for key, value in recomputed.items())

    expected_history_rows = int(events.n_frames.sum())
    event_set = set(events.event)
    development_set = set(development.event)
    audit = json.loads((RESULTS / "T432_SOURCE_AUDIT.json").read_text(encoding="utf-8"))
    source_hashes_ok = all(
        pathlib.Path(str(row["local_path"])).exists()
        and sha256(pathlib.Path(str(row["local_path"]))).lower() == str(row["sha256"]).lower()
        for row in audit
    )

    checks = {
        "freeze_hashes_match": freeze_ok,
        "six_unique_confirmation_events": len(event_set) == 6 and len(events) == 6,
        "no_development_confirmation_overlap": not bool(event_set & development_set),
        "fifty_three_controls_per_event": bool((controls.groupby("event").size() == 53).all()),
        "history_row_count_matches": len(histories) == expected_history_rows,
        "all_source_hashes_match": source_hashes_ok,
        "twelve_detector_files": len(audit) == 12 and len(qa) == 12,
        "source_qa_pass": bool(
            (qa.fs_hz == 4096.0).all()
            and (qa.duration_s == 32.0).all()
            and (qa.finite_fraction == 1.0).all()
            and (qa.zero_fraction == 0.0).all()
            and qa.public_dq_pass.astype(bool).all()
        ),
        "percentiles_recomputed": all(percentile_checks),
        "gates_recomputed": gates_ok,
        "coordinates_within_0_2": bool(
            histories.connection_C.between(0, 2).all()
            and histories.movement_M.between(0, 2).all()
            and histories.unresolved_H.between(0, 2).all()
        ),
        "corner_metric_is_tied": bool(
            (events.top_left_occupancy == 0).all()
            and (controls.top_left_occupancy == 0).all()
            and (events.corner_avoidance_percentile == 0.5).all()
        ),
    }
    output = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "recomputed_gates": recomputed,
        "result_hashes": {
            path.name: sha256(path)
            for path in sorted(RESULTS.glob("T432_CONFIRMATION_*"))
            if path.is_file()
        },
    }
    target = RESULTS / "T432_INDEPENDENT_VALIDATION.json"
    target.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
