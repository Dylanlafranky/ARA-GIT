from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np
import pandas as pd
from scipy import stats


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
EVENT_WINDOW = (-0.32, 0.08)
HOP_SECONDS = 0.004


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mass(values: np.ndarray) -> np.ndarray:
    v = np.maximum(np.asarray(values, dtype=float), 0.0)
    return v / np.sum(v)


def overlap(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sum(np.sqrt(mass(a) * mass(b))))


def main() -> None:
    sources = pd.read_csv(RESULTS / "T440_SOURCE_AUDIT.csv")
    histories = pd.read_csv(RESULTS / "T440_EVENT_HISTORIES.csv")
    detectors = pd.read_csv(RESULTS / "T440_DETECTOR_RESULTS.csv")
    events = pd.read_csv(RESULTS / "T440_EVENT_RESULTS.csv")
    controls = pd.read_csv(RESULTS / "T440_OFFSOURCE_CONTROLS.csv")
    null = pd.read_csv(RESULTS / "T440_WRONG_EVENT_NULL.csv").iloc[:, 0].to_numpy()
    result = json.loads((RESULTS / "T440_RESULTS.json").read_text(encoding="utf-8"))

    checks: dict[str, object] = {}
    checks["source_rows_24"] = len(sources) == 24
    checks["all_source_files_exist"] = all(pathlib.Path(p).exists() for p in sources.path)
    checks["all_source_hashes_match"] = all(sha256(pathlib.Path(row.path)) == row.sha256 for row in sources.itertuples())
    checks["all_public_dq_pass"] = bool(sources.public_dq_pass.astype(bool).all())
    checks["evaluation_events_10"] = histories[histories.role.str.startswith("locked")].event.nunique() == 10
    checks["two_detectors_each"] = bool((histories.groupby("event").detector.nunique() == 2).all())
    coordinate_columns = ["p_space", "p_time", "e_space", "e_time", "joint_child"]
    checks["all_coordinates_finite"] = bool(np.isfinite(histories[coordinate_columns].to_numpy()).all())
    checks["parent_and_child_bounds_0_2"] = bool(((histories[["p_space", "p_time", "e_space", "e_time"]].to_numpy() >= 0) & (histories[["p_space", "p_time", "e_space", "e_time"]].to_numpy() <= 2)).all())

    # Independently reconstruct every event-window overlap directly from the histories.
    max_error = 0.0
    for (event, detector), frame in histories.groupby(["event", "detector"]):
        expected = float(detectors[(detectors.event == event) & (detectors.detector == detector)].overlap.iloc[0])
        actual = overlap(frame.e_space.to_numpy(), frame.e_time.to_numpy())
        max_error = max(max_error, abs(expected - actual))
    checks["overlap_max_abs_error"] = max_error
    checks["overlap_reconstruction_pass"] = max_error < 1e-12

    gate_cols = ["both_overlap_gate", "both_rho_gate", "both_side_gap_gate", "detector_time_gate"]
    accepted = events[gate_cols].astype(bool).all(axis=1)
    checks["accepted_rows_match"] = bool(np.array_equal(accepted.to_numpy(), events.accepted.astype(bool).to_numpy()))
    checks["accepted_count_matches"] = int(accepted.sum()) == int(result["accepted_events"])
    grid = np.arange(EVENT_WINDOW[0], EVENT_WINDOW[1] + HOP_SECONDS / 2, HOP_SECONDS)
    grid_overlaps: list[float] = []
    for (_, _), frame in histories[histories.role.str.startswith("locked")].groupby(["event", "detector"]):
        es = np.interp(grid, frame.time_s.to_numpy(), frame.e_space.to_numpy())
        et = np.interp(grid, frame.time_s.to_numpy(), frame.e_time.to_numpy())
        grid_overlaps.append(overlap(es, et))
    observed = float(np.nanmedian(grid_overlaps))
    checks["common_grid_correct_overlap"] = observed
    # The persisted history table starts at the first in-window STFT frame,
    # whereas the scoring run interpolated the two boundary points from the
    # full history (including one neighbouring frame). The resulting bounded
    # serialization difference must remain below 0.001 overlap units.
    checks["common_grid_overlap_abs_difference"] = abs(observed - float(result["correct_event_median_overlap"]))
    checks["common_grid_overlap_matches"] = checks["common_grid_overlap_abs_difference"] < 1e-3
    wrong_p = float((1 + np.sum(null >= observed)) / (len(null) + 1))
    checks["wrong_event_p_recomputed"] = wrong_p
    checks["wrong_event_p_matches"] = abs(wrong_p - float(result["wrong_event_empirical_p"])) < 1e-15

    # Verify that the two parent coordinates are not an imposed complement.
    evaluation = histories[histories.role.str.startswith("locked")]
    sum_std = float(evaluation.groupby(["event", "detector"]).apply(lambda x: np.std(x.p_space + x.p_time), include_groups=False).median())
    parent_rhos = evaluation.groupby(["event", "detector"]).apply(lambda x: stats.spearmanr(x.p_space, x.p_time).statistic, include_groups=False)
    checks["median_parent_sum_std"] = sum_std
    checks["median_parent_spearman"] = float(np.nanmedian(parent_rhos))
    checks["no_forced_sum_to_two"] = sum_std > 0.05 and bool(np.all(np.abs(parent_rhos) < 0.999))

    opposing = controls.quadrant.isin(["S+/T-", "S-/T+"])
    checks["offsource_opposing_quadrant_fraction"] = float(opposing.mean())
    checks["event_opposing_quadrant_fraction"] = float(detectors[detectors.role.str.startswith("locked")].quadrant.isin(["S+/T-", "S-/T+"]).mean())
    checks["opposition_is_not_source_specific"] = float(opposing.mean()) > 0.95

    required = [value for key, value in checks.items() if key.endswith("_pass") or key in {
        "source_rows_24", "all_source_files_exist", "all_source_hashes_match", "all_public_dq_pass",
        "evaluation_events_10", "two_detectors_each", "all_coordinates_finite", "parent_and_child_bounds_0_2",
        "accepted_rows_match", "accepted_count_matches", "common_grid_overlap_matches", "wrong_event_p_matches", "no_forced_sum_to_two"
    }]
    checks["validation_pass"] = bool(all(required))
    (RESULTS / "T440_VALIDATION.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
