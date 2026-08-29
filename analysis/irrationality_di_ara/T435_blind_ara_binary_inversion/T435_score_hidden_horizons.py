"""T435 reveal-and-score stage.

Run only after T435_WAVEFORM_ONLY_PREDICTION.npz and its SHA-256 receipt exist.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
PREDICTION = RESULTS / "T435_WAVEFORM_ONLY_PREDICTION.npz"
RECEIPT = RESULTS / "T435_PREDICTION_SHA256.txt"
HORIZONS = DATA / "SXS_BBH_0305_Lev6_Horizons.h5"
METADATA = DATA / "SXS_BBH_0305_Lev6_metadata.json"


def robust_map(x: np.ndarray, lo: float = 5.0, hi: float = 95.0) -> np.ndarray:
    q0, q1 = np.nanpercentile(x, [lo, hi])
    if not np.isfinite(q0 + q1) or q1 <= q0:
        return np.zeros_like(x, dtype=float)
    return np.clip((x - q0) / (q1 - q0), 0.0, 1.0)


def interp(t_new: np.ndarray, t: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.interp(t_new, t, x)


def rho(x: np.ndarray, y: np.ndarray) -> float:
    value = spearmanr(x, y, nan_policy="omit").statistic
    return float(value) if np.isfinite(value) else 0.0


def axis_coherence(actual_angle: np.ndarray, predicted_angle: np.ndarray) -> tuple[float, int, float, np.ndarray]:
    """Modulo-pi coherence allowing global handedness and constant rotation."""
    best = (-np.inf, 1, 0.0, predicted_angle)
    for sign in (1, -1):
        delta = actual_angle - sign * predicted_angle
        z = np.exp(2j * delta)
        mean_z = np.mean(z)
        coherence = float(np.abs(mean_z))
        offset = float(0.5 * np.angle(mean_z))
        aligned = sign * predicted_angle + offset
        if coherence > best[0]:
            best = (coherence, sign, offset, aligned)
    return best


def read_series(group: h5py.Group, name: str) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(group[name])
    return arr[:, 0], arr[:, 1:]


def main() -> None:
    receipt_text = RECEIPT.read_text(encoding="utf-8")
    sealed_hash = receipt_text.splitlines()[0].split()[-1]
    current_hash = hashlib.sha256(PREDICTION.read_bytes()).hexdigest()
    if current_hash != sealed_hash:
        raise RuntimeError("Prediction hash no longer matches the pre-reveal seal")

    pred = np.load(PREDICTION)
    t_pred = pred["time"]
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))

    with h5py.File(HORIZONS, "r") as f:
        tA, posA = read_series(f["AhA.dir"], "CoordCenterInertial.dat")
        tB, posB = read_series(f["AhB.dir"], "CoordCenterInertial.dat")
        tmA, massA_col = read_series(f["AhA.dir"], "ChristodoulouMass.dat")
        tmB, massB_col = read_series(f["AhB.dir"], "ChristodoulouMass.dat")
        tC, posC = read_series(f["AhC.dir"], "CoordCenterInertial.dat")

    # Horizon A/B grids are equal for this product; retain an interpolation-safe implementation.
    t0 = max(float(t_pred[0]), float(tA[0]), float(tB[0]))
    common_horizon_time = float(tC[0])
    t1 = min(float(t_pred[-1]), float(tA[-1]), float(tB[-1]), common_horizon_time)
    maskA = (tA >= t0) & (tA <= t1)
    t = tA[maskA]
    A = posA[maskA]
    B = np.column_stack([interp(t, tB, posB[:, k]) for k in range(3)])
    mA = interp(t, tmA, massA_col[:, 0])
    mB = interp(t, tmB, massB_col[:, 0])

    rel_vec = A - B
    separation = np.linalg.norm(rel_vec, axis=1)
    actual_angle = np.unwrap(np.arctan2(rel_vec[:, 1], rel_vec[:, 0]))
    com = (mA[:, None] * A + mB[:, None] * B) / (mA + mB)[:, None]
    radiusA = np.linalg.norm(A - com, axis=1)
    radiusB = np.linalg.norm(B - com, axis=1)
    shareA = radiusA / separation
    shareB = radiusB / separation

    theta = interp(t, t_pred, pred["theta_hat"])
    full_phase = interp(t, t_pred, pred["parent_phase"])
    relation = interp(t, t_pred, pred["relation_ara"])
    relation_science = interp(t, t_pred, pred["relation_science"])
    radius_near = interp(t, t_pred, pred["radius_near"])
    radius_far = interp(t, t_pred, pred["radius_far"])
    share_near = interp(t, t_pred, pred["share_near"])
    share_far = interp(t, t_pred, pred["share_far"])

    orient, handedness, angle_offset, theta_aligned = axis_coherence(actual_angle, theta)
    orient_full, _, _, _ = axis_coherence(actual_angle, full_phase)
    orient_margin = orient - orient_full
    angular_delta = np.angle(np.exp(1j * 2.0 * (actual_angle - theta_aligned))) / 2.0
    median_axis_error_deg = float(np.degrees(np.median(np.abs(angular_delta))))

    relation_spearman = rho(relation, separation)
    science_spearman = rho(relation_science, separation)
    shifted = np.roll(relation, len(relation) // 3)
    shuffled_spearman = rho(shifted, separation)
    relation_margin = relation_spearman - shuffled_spearman

    # Score the unordered pair by the mapping with the larger mean correlation.
    direct = (rho(radius_near, radiusA), rho(radius_far, radiusB))
    swapped = (rho(radius_near, radiusB), rho(radius_far, radiusA))
    if np.mean(swapped) > np.mean(direct):
        radius_corrs = swapped
        actual_near, actual_far = radiusB, radiusA
        actual_share_near, actual_share_far = shareB, shareA
        label_mapping = "near->B, far->A"
    else:
        radius_corrs = direct
        actual_near, actual_far = radiusA, radiusB
        actual_share_near, actual_share_far = shareA, shareB
        label_mapping = "near->A, far->B"
    radius_median = float(np.median(radius_corrs))
    share_mae = float(
        np.mean(
            np.r_[
                np.abs(share_near - actual_share_near),
                np.abs(share_far - actual_share_far),
            ]
        )
    )

    handover_hat = float(pred["handover_hat"])
    handover_error = abs(handover_hat - common_horizon_time)
    cadence_at_handover = float(interp(np.array([handover_hat]), t_pred, pred["cadence"])[0])
    parent_cycle = float(np.pi / cadence_at_handover)
    child_orbital_cycle = float(2.0 * np.pi / cadence_at_handover)

    gates = {
        "orientation": bool(orient >= 0.80 and orient_margin >= 0.10),
        "relation": bool(relation_spearman >= 0.70 and relation_margin >= 0.20),
        "child_radii": bool(radius_median >= 0.50),
        "handover_timing": bool(handover_error <= parent_cycle),
    }
    if gates["orientation"] and gates["relation"]:
        overall = "SUPPORTED" if all(gates.values()) else "PARTIAL"
    else:
        overall = "NOT SUPPORTED"

    # ARA-scaled hidden quantities are for visual comparison only; correlations use raw values.
    actual_relation_ara = 2.0 * robust_map(separation)
    actual_near_ara = 2.0 * robust_map(actual_near)
    actual_far_ara = 2.0 * robust_map(actual_far)

    summary = {
        "test": "T435_blind_ara_binary_inversion",
        "result": overall,
        "prediction_sha256_verified": True,
        "simulation": "SXS:BBH:0305 Lev6",
        "hidden_system_revealed": {
            "reference_mass_ratio": metadata.get("reference_mass_ratio"),
            "reference_spin1": metadata.get("reference_dimensionless_spin1"),
            "reference_spin2": metadata.get("reference_dimensionless_spin2"),
            "common_horizon_time": common_horizon_time,
        },
        "scoring_window": [float(t[0]), float(t[-1])],
        "metrics": {
            "orientation_axis_coherence": orient,
            "unhalved_phase_control_coherence": orient_full,
            "orientation_margin": orient_margin,
            "median_axis_error_degrees": median_axis_error_deg,
            "relation_spearman": relation_spearman,
            "circular_shift_control_spearman": shuffled_spearman,
            "relation_margin": relation_margin,
            "science_omega_minus_two_thirds_spearman": science_spearman,
            "child_radius_spearman_pair": list(map(float, radius_corrs)),
            "child_radius_median_spearman": radius_median,
            "child_share_mean_absolute_error": share_mae,
            "predicted_handover_time": handover_hat,
            "common_horizon_time": common_horizon_time,
            "handover_absolute_error": handover_error,
            "parent_waveform_cycle_at_prediction": parent_cycle,
            "child_orbital_cycle_at_prediction": child_orbital_cycle,
        },
        "symmetry_resolution": {
            "handedness": int(handedness),
            "constant_rotation_radians": angle_offset,
            "unordered_label_mapping": label_mapping,
        },
        "gates": gates,
        "evidence_class": "single numerical-relativity simulation; crosswalk and inversion calibration",
    }
    (RESULTS / "T435_SCORED_RESULT.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    np.savez_compressed(
        RESULTS / "T435_SCORED_SERIES.npz",
        time=t,
        actual_position_A=A,
        actual_position_B=B,
        actual_relation=separation,
        actual_relation_ara=actual_relation_ara,
        actual_angle=actual_angle,
        predicted_angle_aligned=theta_aligned,
        predicted_relation_ara=relation,
        predicted_relation_science=relation_science,
        actual_radius_near=actual_near,
        actual_radius_far=actual_far,
        actual_radius_near_ara=actual_near_ara,
        actual_radius_far_ara=actual_far_ara,
        predicted_radius_near=radius_near,
        predicted_radius_far=radius_far,
        actual_share_near=actual_share_near,
        actual_share_far=actual_share_far,
        predicted_share_near=share_near,
        predicted_share_far=share_far,
        common_horizon_time=np.array(common_horizon_time),
        predicted_handover_time=np.array(handover_hat),
    )

    # Static audit figure. The durable interactive report is built separately.
    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), constrained_layout=True)
    ax = axes[0, 0]
    stride = max(1, len(t) // 1500)
    ax.plot(A[::stride, 0], A[::stride, 1], lw=1.1, label="hidden horizon A")
    ax.plot(B[::stride, 0], B[::stride, 1], lw=1.1, label="hidden horizon B")
    ax.scatter([A[-1, 0], B[-1, 0]], [A[-1, 1], B[-1, 1]], s=28, c=["#66a3ff", "#ff9f43"])
    ax.set(title="Hidden answer: two individual horizon centres", xlabel="inertial x / M", ylabel="inertial y / M", aspect="equal")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(t, actual_relation_ara, color="#d8dee9", lw=2, label="actual A–B separation (ARA-scaled)")
    ax.plot(t, relation, color="#ffb000", lw=1.2, alpha=0.9, label="blind ARA relation")
    ax.axvline(common_horizon_time, color="#5ee38f", ls="--", label="first common horizon C")
    ax.set(title=f"Relation recovery: Spearman {relation_spearman:.3f}", xlabel="simulation time / M", ylabel="remaining relation (0–2)", ylim=(-0.05, 2.05))
    ax.legend(fontsize=8)

    ax = axes[0, 2]
    ax.plot(t, np.degrees(np.unwrap(actual_angle)), color="#d8dee9", lw=1.6, label="actual A–B axis")
    ax.plot(t, np.degrees(np.unwrap(theta_aligned)), color="#66a3ff", lw=1.0, label="blind half-phase axis")
    ax.set(title=f"Child orientation: coherence {orient:.3f}", xlabel="simulation time / M", ylabel="unwrapped axis angle / degrees")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.plot(t, actual_near_ara, color="#5ee38f", lw=1.8, label="actual near child radius")
    ax.plot(t, actual_far_ara, color="#c084fc", lw=1.8, label="actual far child radius")
    ax.plot(t, 2.0 * robust_map(radius_near), color="#5ee38f", ls="--", lw=1.0, label="predicted near")
    ax.plot(t, 2.0 * robust_map(radius_far), color="#c084fc", ls="--", lw=1.0, label="predicted far")
    ax.set(title=f"Unordered child radii: median rho {radius_median:.3f}", xlabel="simulation time / M", ylabel="within-series ARA coordinate (0–2)")
    ax.legend(fontsize=7, ncol=2)

    ax = axes[1, 1]
    ptime = pred["time"]
    for key, color, label in [
        ("total_power", "#66a3ff", "total mode power"),
        ("cadence", "#ffb000", "cadence"),
        ("modal_concentration", "#c084fc", "modal concentration"),
    ]:
        ax.plot(ptime, robust_map(pred[key]), color=color, lw=1.1, label=label)
    ax.axvline(common_horizon_time, color="#5ee38f", ls="--", lw=2, label="actual C")
    ax.axvline(handover_hat, color="#ff5c5c", ls=":", lw=2, label="blind handover")
    ax.set(xlim=(common_horizon_time - 250, common_horizon_time + 160), title=f"Handover timing: error {handover_error:.1f} M", xlabel="simulation time / M", ylabel="waveform-only feature (robust 0–1)")
    ax.legend(fontsize=8)

    ax = axes[1, 2]
    labels = ["orientation", "relation", "child radii", "timing"]
    # Timing is displayed as allowed-cycle/error, capped at 1; it passes only at 1.
    timing_display = min(1.0, parent_cycle / max(handover_error, 1e-12))
    values = [orient, relation_spearman, radius_median, timing_display]
    thresholds = [0.80, 0.70, 0.50, 1.0]
    colors = ["#5ee38f" if gates[k] else "#ff5c5c" for k in ["orientation", "relation", "child_radii", "handover_timing"]]
    ax.bar(labels, values, color=colors, alpha=0.85)
    ax.scatter(labels[:3], thresholds[:3], marker="_", s=700, color="white", label="frozen minimum")
    ax.set(title=f"Frozen result: {overall}", ylabel="gate score (timing = allowed cycle / error)", ylim=(-0.15, 1.08))
    ax.tick_params(axis="x", rotation=18)
    ax.legend(fontsize=8)

    fig.suptitle("T435 — blind ARA inversion of a combined binary-black-hole waveform", fontsize=18, weight="bold")
    fig.savefig(RESULTS / "T435_BLIND_BINARY_INVERSION_AUDIT.png", dpi=170)
    plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
