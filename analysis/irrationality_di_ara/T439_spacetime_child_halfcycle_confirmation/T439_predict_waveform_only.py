"""T439 waveform-only prediction stage.

This stage reads only the nine frozen SXS Strain_N4 products.  It writes and
hashes every waveform-derived landmark before the hidden Horizons products are
opened by the separate scorer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.signal import savgol_filter
import sxs


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
PROTOCOL = ROOT / "T439_FROZEN_PROTOCOL.md"
LOCK = ROOT / "T439_FREEZE_LOCK.json"
MANIFEST = ROOT / "T439_DOWNLOAD_MANIFEST.json"
SUMMARY = RESULTS / "T439_WAVEFORM_ONLY_PREDICTIONS.json"
RECEIPT = RESULTS / "T439_WAVEFORM_PREDICTIONS_SHA256.txt"


def empirical_rank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(x.size, dtype=float)
    return ranks / max(1, x.size - 1)


def odd_window(n: int) -> int:
    w = max(11, min(301, int(round(n / 200))))
    return w if w % 2 else w + 1


def smooth(x: np.ndarray, window: int) -> np.ndarray:
    w = min(window, len(x) - (1 - len(x) % 2))
    if w < 5:
        return np.asarray(x, dtype=float)
    if w % 2 == 0:
        w -= 1
    return savgol_filter(np.asarray(x, dtype=float), w, 3, mode="interp")


def safe_log(x: np.ndarray) -> np.ndarray:
    floor = max(np.finfo(float).tiny, float(np.nanmax(x)) * 1.0e-15)
    return np.log(np.maximum(x, floor))


def file_for(entry: dict, kind: str) -> Path:
    row = next(item for item in entry["files"] if item["kind"] == kind)
    return Path(row["local_path"])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predict(entry: dict) -> dict:
    simulation = entry["sxs_id"]
    waveform = file_for(entry, "Strain_N4.h5")
    # Strain has spin weight -2.  The compact public H5 files do not include
    # their sidecar JSON, so this invariant metadata is supplied explicitly.
    w = sxs.load(str(waveform), spin_weight=-2)
    t_all = np.asarray(w.t, dtype=float)
    lm = np.asarray(w.LM, dtype=int)
    modes_all = np.asarray(w.ndarray, dtype=complex)

    i22 = np.flatnonzero((lm[:, 0] == 2) & (lm[:, 1] == 2))
    if i22.size != 1:
        raise RuntimeError(f"{simulation}: h_22 is not uniquely available")
    i22 = int(i22[0])

    power_all = np.sum(np.abs(modes_all) ** 2, axis=1)
    peak_i_all = int(np.nanargmax(power_all))
    peak_power = float(power_all[peak_i_all])
    threshold = 1.0e-4 * peak_power
    above = np.flatnonzero(power_all >= threshold)
    if above.size < 500:
        raise RuntimeError(f"{simulation}: insufficient active waveform support")

    start_i = int(above[0])
    start_i = min(peak_i_all - 200, start_i + max(20, int(0.02 * len(t_all))))
    post = np.flatnonzero(
        (np.arange(len(t_all)) > peak_i_all) & (power_all < 5.0e-3 * peak_power)
    )
    end_i = int(post[0]) if post.size else len(t_all) - 1
    end_i = max(end_i, peak_i_all + 100)
    sl = slice(start_i, min(end_i + 1, len(t_all)))

    t = t_all[sl]
    modes = modes_all[sl]
    h22 = modes[:, i22]
    power = np.sum(np.abs(modes) ** 2, axis=1)
    amplitude = np.sqrt(np.maximum(power, 0.0))
    phase = np.unwrap(np.angle(h22))
    theta = 0.5 * phase
    win = odd_window(len(t))

    cadence_raw = np.abs(np.gradient(theta, t))
    cadence = np.maximum(smooth(cadence_raw, win), np.finfo(float).tiny)
    relation = 2.0 * (1.0 - empirical_rank(cadence))
    connection = smooth(np.gradient(safe_log(amplitude), t), win)
    traversal = smooth(np.gradient(theta, t), win)
    beta = np.arctan2(
        np.abs(traversal), np.abs(connection) + np.finfo(float).tiny
    )
    beta_activity = np.abs(smooth(np.gradient(beta, t), win))

    power_peak_i = int(np.nanargmax(power))
    power_peak_time = float(t[power_peak_i])
    late = (relation <= 1.0) & (t <= power_peak_time)
    late[:win] = False
    late[-win:] = False
    eligible = np.flatnonzero(late)
    if eligible.size == 0:
        raise RuntimeError(f"{simulation}: no eligible late-parent basin")
    landmark_i = int(eligible[np.nanargmax(beta_activity[eligible])])

    concentration = np.abs(h22) ** 2 / np.maximum(power, np.finfo(float).tiny)
    d_cadence = smooth(np.gradient(cadence, t), win)
    d_concentration = smooth(np.gradient(concentration, t), win)
    cadence_peak_time = float(t[int(np.nanargmax(d_cadence))])
    concentration_peak_time = float(t[int(np.nanargmax(np.abs(d_concentration)))])
    t_t435 = float(np.median([power_peak_time, cadence_peak_time, concentration_peak_time]))
    cadence_at_t435 = float(np.interp(t_t435, t, cadence))
    parent_cycle = float(np.pi / cadence_at_t435)

    slug = simulation.replace(":", "_")
    npz_path = RESULTS / f"{slug}_WAVEFORM_ONLY.npz"
    np.savez_compressed(
        npz_path,
        time=t,
        total_power=power,
        amplitude=amplitude,
        theta=theta,
        cadence=cadence,
        relation_ara=relation,
        connection_step=connection,
        traversal_step=traversal,
        beta=beta,
        beta_activity=beta_activity,
        eligible_mask=late,
        landmark_index=np.array(landmark_i),
        power_peak_index=np.array(power_peak_i),
        savgol_window=np.array(win),
        t_t435=np.array(t_t435),
        parent_cycle=np.array(parent_cycle),
    )
    return {
        "sxs_id": simulation,
        "selected_level": int(entry["selected_level"]),
        "waveform_path": str(waveform),
        "waveform_md5": next(
            item["md5"] for item in entry["files"] if item["kind"] == "Strain_N4.h5"
        ),
        "n_samples": int(len(t)),
        "active_time_M": [float(t[0]), float(t[-1])],
        "savgol_window_samples": int(win),
        "eligible_samples": int(eligible.size),
        "path_direction_landmark_time_M": float(t[landmark_i]),
        "path_direction_landmark_relation_ara": float(relation[landmark_i]),
        "path_direction_landmark_beta": float(beta[landmark_i]),
        "path_direction_landmark_activity": float(beta_activity[landmark_i]),
        "power_crest_time_M": power_peak_time,
        "cadence_derivative_peak_time_M": cadence_peak_time,
        "modal_concentration_change_peak_time_M": concentration_peak_time,
        "t_T435_M": t_t435,
        "parent_cycle_M": parent_cycle,
        "prediction_npz": str(npz_path),
        "prediction_npz_sha256": sha256(npz_path),
        "answer_keys_opened": False,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    protocol_hash = sha256(PROTOCOL)
    if protocol_hash != lock["protocol_sha256"]:
        raise RuntimeError("T439 protocol changed after freeze")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(manifest) != lock["holdout_count"]:
        raise RuntimeError("Frozen holdout count does not match download manifest")

    rows = []
    for entry in manifest:
        print(f"Predicting {entry['sxs_id']} Lev{entry['selected_level']}...", flush=True)
        rows.append(predict(entry))

    payload = {
        "status": "SEALED_BEFORE_HORIZON_REVEAL",
        "test": "T439_spacetime_child_halfcycle_confirmation",
        "protocol_sha256": protocol_hash,
        "holdout_count": len(rows),
        "predictions": rows,
    }
    SUMMARY.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary_hash = sha256(SUMMARY)
    lines = [
        f"protocol_sha256  {protocol_hash}",
        f"summary_sha256   {summary_hash}",
    ]
    for row in rows:
        lines.append(
            f"{row['sxs_id']}  {row['prediction_npz_sha256']}  {row['prediction_npz']}"
        )
    RECEIPT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"summary_sha256": summary_hash, **payload}, indent=2))


if __name__ == "__main__":
    main()
