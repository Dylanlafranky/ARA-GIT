"""T439 reveal, controls, and frozen-gate scoring stage.

Run only after T439_predict_waveform_only.py has sealed all nine predictions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MANIFEST = ROOT / "T439_DOWNLOAD_MANIFEST.json"
PREDICTIONS = RESULTS / "T439_WAVEFORM_ONLY_PREDICTIONS.json"
RECEIPT = RESULTS / "T439_WAVEFORM_PREDICTIONS_SHA256.txt"
OUTPUT = RESULTS / "T439_SCORED_RESULT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smooth(x: np.ndarray, window: int) -> np.ndarray:
    w = min(window, len(x) - (1 - len(x) % 2))
    if w < 5:
        return np.asarray(x, dtype=float)
    if w % 2 == 0:
        w -= 1
    return savgol_filter(np.asarray(x, dtype=float), w, 3, mode="interp")


def file_for(entry: dict, kind: str) -> Path:
    row = next(item for item in entry["files"] if item["kind"] == kind)
    return Path(row["local_path"])


def common_horizon_time(path: Path) -> float:
    with h5py.File(path, "r") as handle:
        arr = np.asarray(handle["AhC.dir"]["CoordCenterInertial.dat"])
    if arr.ndim != 2 or arr.shape[0] == 0:
        raise RuntimeError(f"No common-horizon coordinate series in {path}")
    return float(arr[0, 0])


def control_landmark_time(
    t: np.ndarray,
    s: np.ndarray,
    tr: np.ndarray,
    eligible: np.ndarray,
    window: int,
) -> float:
    beta = np.arctan2(np.abs(tr), np.abs(s) + np.finfo(float).tiny)
    activity = np.abs(smooth(np.gradient(beta, t), window))
    indices = np.flatnonzero(eligible)
    return float(t[int(indices[np.nanargmax(activity[indices])])])


def verify_seal(pred: dict) -> None:
    receipt = RECEIPT.read_text(encoding="utf-8").splitlines()
    receipt_map = {}
    for line in receipt[2:]:
        simulation, digest, path = line.split("  ", 2)
        receipt_map[simulation] = (digest, path)
    if sha256(PREDICTIONS) != receipt[1].split()[1]:
        raise RuntimeError("Waveform prediction summary hash does not match seal")
    for row in pred["predictions"]:
        expected, path = receipt_map[row["sxs_id"]]
        if path != row["prediction_npz"] or sha256(Path(path)) != expected:
            raise RuntimeError(f"Prediction seal failed for {row['sxs_id']}")


def main() -> None:
    pred = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    verify_seal(pred)
    manifest = {entry["sxs_id"]: entry for entry in json.loads(MANIFEST.read_text(encoding="utf-8"))}
    rng = np.random.default_rng(439)
    rows = []
    control_by_sim = []

    for prow in pred["predictions"]:
        simulation = prow["sxs_id"]
        entry = manifest[simulation]
        horizon = common_horizon_time(file_for(entry, "Horizons.h5"))
        metadata = json.loads(file_for(entry, "metadata.json").read_text(encoding="utf-8"))
        series = np.load(prow["prediction_npz"])
        t = np.asarray(series["time"], dtype=float)
        s = np.asarray(series["connection_step"], dtype=float)
        tr = np.asarray(series["traversal_step"], dtype=float)
        eligible = np.asarray(series["eligible_mask"], dtype=bool)
        window = int(series["savgol_window"])
        landmark_time = float(prow["path_direction_landmark_time_M"])
        crest_time = float(prow["power_crest_time_M"])
        cycle = float(prow["parent_cycle_M"])
        signed = (landmark_time - horizon) / cycle
        absolute = abs(signed)
        crest_absolute = abs(crest_time - horizon) / cycle

        quarter_time = control_landmark_time(
            t, np.roll(s, len(s) // 4), np.roll(tr, len(tr) // 4), eligible, window
        )
        swapped_time = control_landmark_time(t, tr, s, eligible, window)
        quarter_offset = abs(quarter_time - horizon) / cycle
        swapped_offset = abs(swapped_time - horizon) / cycle

        simulation_controls = np.empty(1000, dtype=float)
        for j in range(1000):
            perm = rng.permutation(len(t))
            shuffled_time = control_landmark_time(t, s[perm], tr[perm], eligible, window)
            simulation_controls[j] = abs(shuffled_time - horizon) / cycle
        control_by_sim.append(simulation_controls)

        rows.append(
            {
                "sxs_id": simulation,
                "selected_level": int(prow["selected_level"]),
                "mass_ratio": float(entry["reference_mass_ratio"]),
                "chi_eff": float(entry["reference_chi_eff"]),
                "metadata_common_horizon_time_M": metadata.get("common_horizon_time"),
                "horizon_first_sample_time_M": horizon,
                "landmark_time_M": landmark_time,
                "parent_cycle_M": cycle,
                "signed_offset_cycles": signed,
                "absolute_offset_cycles": absolute,
                "half_cycle_deviation": abs(absolute - 0.5),
                "crest_time_M": crest_time,
                "crest_absolute_offset_cycles": crest_absolute,
                "quarter_roll_absolute_offset_cycles": quarter_offset,
                "swap_absolute_offset_cycles": swapped_offset,
                "within_broad_half_cycle_band": 0.25 <= absolute <= 0.75,
                "within_one_parent_cycle": absolute <= 1.0,
                "landmark_after_horizon": signed > 0.0,
            }
        )

    control_matrix = np.vstack(control_by_sim)
    observed_mean_deviation = float(np.mean([row["half_cycle_deviation"] for row in rows]))
    shuffled_mean_deviation = np.mean(np.abs(control_matrix - 0.5), axis=0)
    empirical_p = float((1 + np.sum(shuffled_mean_deviation <= observed_mean_deviation)) / 1001)
    absolute_offsets = np.array([row["absolute_offset_cycles"] for row in rows])
    crest_offsets = np.array([row["crest_absolute_offset_cycles"] for row in rows])
    median_absolute = float(np.median(absolute_offsets))
    broad_count = int(np.sum((absolute_offsets >= 0.25) & (absolute_offsets <= 0.75)))
    within_one_count = int(np.sum(absolute_offsets <= 1.0))
    median_crest = float(np.median(crest_offsets))
    gates = {
        "median_in_frozen_half_cycle_band": 0.40 <= median_absolute <= 0.60,
        "six_of_nine_in_broad_band": broad_count >= 6,
        "seven_of_nine_within_one_cycle": within_one_count >= 7,
        "beats_chronology_shuffle": empirical_p <= 0.05,
        "beats_power_crest_baseline": median_absolute < median_crest,
    }
    if all(gates.values()):
        verdict = "SUPPORTED"
    elif all(list(gates.values())[:3]):
        verdict = "PARTIAL"
    else:
        verdict = "NOT SUPPORTED"

    summary = {
        "test": "T439_spacetime_child_halfcycle_confirmation",
        "verdict": verdict,
        "prediction_seal_verified": True,
        "interpretation": "absolute half-cycle displacement confirmation; signed direction retained descriptively",
        "metrics": {
            "holdout_count": len(rows),
            "median_absolute_offset_cycles": median_absolute,
            "mean_absolute_offset_cycles": float(np.mean(absolute_offsets)),
            "median_signed_offset_cycles": float(np.median([row["signed_offset_cycles"] for row in rows])),
            "mean_half_cycle_deviation": observed_mean_deviation,
            "broad_half_cycle_band_count": broad_count,
            "within_one_parent_cycle_count": within_one_count,
            "after_horizon_count": int(np.sum([row["landmark_after_horizon"] for row in rows])),
            "shuffle_empirical_p": empirical_p,
            "shuffle_mean_deviation_median": float(np.median(shuffled_mean_deviation)),
            "power_crest_median_absolute_offset_cycles": median_crest,
            "label_swap_max_timing_difference_cycles": float(
                np.max(
                    np.abs(
                        absolute_offsets
                        - np.array([row["swap_absolute_offset_cycles"] for row in rows])
                    )
                )
            ),
        },
        "gates": gates,
        "holdouts": rows,
        "evidence_class": "frozen holdout confirmation within public SXS numerical-relativity simulations",
        "limits": [
            "SXS waveforms and horizons are generated within general relativity, so this is a crosswalk/confirmation rather than independent proof.",
            "The primary endpoint is unsigned; whether the landmark leads or follows the horizon remains descriptive.",
            "The waveform landmark may reflect child projection, post-horizon redistribution, or a shared simulation convention.",
        ],
    }
    OUTPUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(RESULTS / "T439_HOLDOUT_SCORES.csv", index=False)
    np.savez_compressed(
        RESULTS / "T439_SHUFFLE_CONTROLS.npz",
        control_offsets=control_matrix,
        shuffled_mean_deviation=shuffled_mean_deviation,
        observed_mean_deviation=np.array(observed_mean_deviation),
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
