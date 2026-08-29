"""T435 waveform-only prediction stage.

This script must be run before any horizon or metadata answer key is opened.
It reads only the combined SXS strain modes and writes a hashed ARA prediction.
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
WAVEFORM = DATA / "SXS_BBH_0305_Lev6_Strain_N4.h5"
PREDICTION = RESULTS / "T435_WAVEFORM_ONLY_PREDICTION.npz"
SUMMARY = RESULTS / "T435_WAVEFORM_ONLY_PREDICTION.json"
RECEIPT = RESULTS / "T435_PREDICTION_SHA256.txt"


def empirical_rank(x: np.ndarray) -> np.ndarray:
    """Average-free deterministic ranks on [0, 1]."""
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(x.size, dtype=float)
    return ranks / max(1, x.size - 1)


def robust_map(x: np.ndarray, lo: float = 5.0, hi: float = 95.0) -> np.ndarray:
    q0, q1 = np.nanpercentile(x, [lo, hi])
    if not np.isfinite(q0 + q1) or q1 <= q0:
        return np.zeros_like(x, dtype=float)
    return np.clip((x - q0) / (q1 - q0), 0.0, 1.0)


def odd_window(n: int) -> int:
    # About 0.5% of the active waveform, bounded and forced odd.
    w = max(11, min(301, int(round(n / 200))))
    return w if w % 2 else w + 1


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    w = sxs.load(str(WAVEFORM))
    t_all = np.asarray(w.t, dtype=float)
    lm = np.asarray(w.LM, dtype=int)
    modes_all = np.asarray(w.ndarray, dtype=complex)

    i22 = np.flatnonzero((lm[:, 0] == 2) & (lm[:, 1] == 2))
    if i22.size != 1:
        raise RuntimeError("The frozen parent carrier h_22 is not uniquely available")
    i22 = int(i22[0])

    power_all = np.sum(np.abs(modes_all) ** 2, axis=1)
    peak_i_all = int(np.nanargmax(power_all))
    peak_power = float(power_all[peak_i_all])

    # Waveform-only active support: remove startup/junk and retain early ringdown.
    threshold = 1.0e-4 * peak_power
    above = np.flatnonzero(power_all >= threshold)
    if above.size < 500:
        raise RuntimeError("Insufficient active waveform support")
    start_i = int(above[0])
    # Require at least 2% of the full samples after the first crossing to avoid junk.
    start_i = min(peak_i_all - 200, start_i + max(20, int(0.02 * len(t_all))))
    # Stop when post-peak power has fallen below 0.5% of peak, or at file end.
    post = np.flatnonzero((np.arange(len(t_all)) > peak_i_all) & (power_all < 5.0e-3 * peak_power))
    end_i = int(post[0]) if post.size else len(t_all) - 1
    end_i = max(end_i, peak_i_all + 100)
    sl = slice(start_i, min(end_i + 1, len(t_all)))

    t = t_all[sl]
    modes = modes_all[sl]
    h22 = modes[:, i22]
    power = np.sum(np.abs(modes) ** 2, axis=1)
    h22_power = np.abs(h22) ** 2
    concentration = h22_power / np.maximum(power, np.finfo(float).tiny)

    phase = np.unwrap(np.angle(h22))
    theta_hat = 0.5 * phase
    dt = np.gradient(t)
    cadence_raw = np.abs(0.5 * np.gradient(phase) / dt)
    win = odd_window(len(t))
    cadence = savgol_filter(cadence_raw, win, 3, mode="interp")
    cadence = np.maximum(cadence, np.finfo(float).tiny)

    even_mask = ((lm[:, 0] + lm[:, 1]) % 2) == 0
    odd_mask = ~even_mask
    p_even = np.sum(np.abs(modes[:, even_mask]) ** 2, axis=1)
    p_odd = np.sum(np.abs(modes[:, odd_mask]) ** 2, axis=1)
    a_raw = np.sqrt(p_odd / np.maximum(p_even + p_odd, np.finfo(float).tiny))
    a_hat = robust_map(a_raw)

    # Primary ARA relation: reverse cadence order on a 0--2 coordinate.
    relation_ara = 2.0 * (1.0 - empirical_rank(cadence))
    # Established-science sidecar only; it does not enter the ARA gate.
    relation_science_raw = cadence ** (-2.0 / 3.0)
    relation_science = 2.0 * robust_map(relation_science_raw)

    share_near = 0.5 * (1.0 - a_hat)
    share_far = 0.5 * (1.0 + a_hat)
    radius_near = relation_ara * share_near
    radius_far = relation_ara * share_far

    child1_x = radius_near * np.cos(theta_hat)
    child1_y = radius_near * np.sin(theta_hat)
    child2_x = -radius_far * np.cos(theta_hat)
    child2_y = -radius_far * np.sin(theta_hat)

    d_cadence = savgol_filter(np.gradient(cadence, t), win, 3, mode="interp")
    d_concentration = savgol_filter(np.gradient(concentration, t), win, 3, mode="interp")
    landmark_power = float(t[int(np.nanargmax(power))])
    landmark_cadence = float(t[int(np.nanargmax(d_cadence))])
    landmark_concentration = float(t[int(np.nanargmax(np.abs(d_concentration)))])
    handover_hat = float(np.median([landmark_power, landmark_cadence, landmark_concentration]))

    np.savez_compressed(
        PREDICTION,
        time=t,
        theta_hat=theta_hat,
        parent_phase=phase,
        cadence=cadence,
        total_power=power,
        modal_concentration=concentration,
        odd_power=p_odd,
        even_power=p_even,
        asymmetry_raw=a_raw,
        asymmetry_ara=a_hat,
        relation_ara=relation_ara,
        relation_science=relation_science,
        share_near=share_near,
        share_far=share_far,
        radius_near=radius_near,
        radius_far=radius_far,
        child1_x=child1_x,
        child1_y=child1_y,
        child2_x=child2_x,
        child2_y=child2_y,
        lm=lm,
        active_indices=np.array([start_i, end_i], dtype=int),
        landmark_times=np.array([landmark_power, landmark_cadence, landmark_concentration]),
        handover_hat=np.array(handover_hat),
        savgol_window=np.array(win),
    )

    summary = {
        "status": "PREDICTION_WRITTEN_BEFORE_HORIZON_REVEAL",
        "input": WAVEFORM.name,
        "n_samples": int(len(t)),
        "active_file_indices": [int(start_i), int(end_i)],
        "active_time": [float(t[0]), float(t[-1])],
        "parent_power_peak_time": landmark_power,
        "cadence_derivative_peak_time": landmark_cadence,
        "modal_concentration_change_peak_time": landmark_concentration,
        "predicted_common_handover_time": handover_hat,
        "savgol_window_samples": int(win),
        "mode_count": int(modes.shape[1]),
        "mode_ell_range": [int(lm[:, 0].min()), int(lm[:, 0].max())],
        "answer_keys_opened": False,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    digest = hashlib.sha256(PREDICTION.read_bytes()).hexdigest()
    protocol_digest = hashlib.sha256((ROOT / "T435_FROZEN_PROTOCOL.md").read_bytes()).hexdigest()
    RECEIPT.write_text(
        f"prediction_sha256  {digest}\nprotocol_sha256    {protocol_digest}\n",
        encoding="utf-8",
    )
    print(json.dumps({**summary, "prediction_sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
