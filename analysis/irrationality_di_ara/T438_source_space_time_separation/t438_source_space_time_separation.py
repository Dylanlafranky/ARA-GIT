"""T438 source-side polar Space/Time separation.

Uses the already sealed T435 waveform prediction and the already revealed T435
horizon score.  This is an explicitly non-blind one-system calibration.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.stats import rankdata, spearmanr


ROOT = Path(__file__).resolve().parent
ARA_ROOT = ROOT.parents[2]
T435 = ROOT.parent / "T435_blind_ara_binary_inversion"
PREDICTION = T435 / "results" / "T435_WAVEFORM_ONLY_PREDICTION.npz"
SCORED = T435 / "results" / "T435_SCORED_SERIES.npz"
T435_SCORE = T435 / "results" / "T435_SCORED_RESULT.json"
PROTOCOL = ROOT / "T438_FROZEN_PROTOCOL.md"
LOCK = ROOT / "T438_FREEZE_LOCK.json"
RESULTS = ROOT / "results"


def rank02(x: np.ndarray) -> np.ndarray:
    return 2.0 * (rankdata(np.asarray(x), method="average") - 1.0) / max(1, len(x) - 1)


def rho(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 8:
        return float("nan")
    return float(spearmanr(x[mask], y[mask]).statistic)


def odd_nearest(x: float, lower: int = 11, upper: int | None = None) -> int:
    value = max(lower, int(round(x)))
    if upper is not None:
        value = min(value, upper)
    if value % 2 == 0:
        value += 1
    if upper is not None and value > upper:
        value -= 2
    return max(5, value)


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


def component_steps(log_radius: np.ndarray, angle: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray]:
    radial = smooth(np.gradient(log_radius), window)
    angular = smooth(np.gradient(np.unwrap(angle)), window)
    return radial, angular


def stage_label(t: float, horizon: float) -> str:
    if t < horizon - 100.0:
        return "inspiral"
    if t <= horizon:
        return "late approach"
    return "post-common-horizon waveform"


def relpath(path: Path) -> str:
    return path.resolve().relative_to(ARA_ROOT.resolve()).as_posix()


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    protocol_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if protocol_hash != lock["protocol_sha256"]:
        raise RuntimeError("T438 protocol changed after freeze")

    pred = np.load(PREDICTION)
    scored = np.load(SCORED)
    t435_score = json.loads(T435_SCORE.read_text(encoding="utf-8"))

    t_pred = np.asarray(pred["time"], dtype=float)
    t = np.asarray(scored["time"], dtype=float)
    horizon = float(scored["common_horizon_time"])
    cycle = float(t435_score["metrics"]["parent_waveform_cycle_at_prediction"])

    amplitude_pred = np.sqrt(np.maximum(np.asarray(pred["total_power"], dtype=float), 0.0))
    amplitude = np.interp(t, t_pred, amplitude_pred)
    theta = np.asarray(scored["predicted_angle_aligned"], dtype=float)
    separation = np.asarray(scored["actual_relation"], dtype=float)
    actual_angle = np.unwrap(np.asarray(scored["actual_angle"], dtype=float))

    pred_window = int(pred["savgol_window"])
    pred_dt = float(np.median(np.diff(t_pred)))
    score_dt = float(np.median(np.diff(t)))
    score_window = odd_nearest(pred_window * pred_dt / score_dt, upper=len(t) - 1)

    c_p, t_p = component_steps(safe_log(amplitude), theta, score_window)
    c_h_raw, t_h = component_steps(safe_log(separation), actual_angle, score_window)
    c_h = -c_h_raw

    trim = max(2, score_window)
    valid = np.zeros(len(t), dtype=bool)
    valid[trim:-trim] = True
    valid &= np.isfinite(c_p + t_p + c_h + t_h)

    cp = c_p[valid]
    tp = t_p[valid]
    ch = c_h[valid]
    th = t_h[valid]
    tv = t[valid]

    beta_p = np.arctan2(np.abs(tp), np.abs(cp) + np.finfo(float).tiny)
    beta_h = np.arctan2(np.abs(th), np.abs(ch) + np.finfo(float).tiny)

    rng = np.random.default_rng(438)
    perm = rng.permutation(len(beta_p))
    quarter = len(beta_p) // 4

    metrics = {
        "traversal_recovery_rho": rho(tp, th),
        "connection_on_hidden_traversal_rho": rho(cp, th),
        "closure_recovery_rho": rho(cp, ch),
        "traversal_on_hidden_closure_rho": rho(tp, ch),
        "path_direction_rho": rho(beta_p, beta_h),
        "path_direction_shuffled_rho": rho(beta_p[perm], beta_h),
        "path_direction_quarter_roll_rho": rho(np.roll(beta_p, quarter), beta_h),
    }
    metrics["traversal_specificity_margin"] = metrics["traversal_recovery_rho"] - abs(
        metrics["connection_on_hidden_traversal_rho"]
    )
    metrics["closure_specificity_margin"] = metrics["closure_recovery_rho"] - abs(
        metrics["traversal_on_hidden_closure_rho"]
    )
    metrics["path_direction_shuffle_margin"] = metrics["path_direction_rho"] - metrics[
        "path_direction_shuffled_rho"
    ]

    gates = {
        "traversal_recovery": metrics["traversal_recovery_rho"] >= 0.80,
        "traversal_specificity": metrics["traversal_specificity_margin"] >= 0.20,
        "closure_recovery": metrics["closure_recovery_rho"] >= 0.50,
        "closure_specificity": metrics["closure_specificity_margin"] >= 0.20,
        "path_direction": metrics["path_direction_rho"] >= 0.50
        and metrics["path_direction_shuffle_margin"] >= 0.20,
    }
    if all(gates.values()):
        verdict = "SUPPORTED"
    elif gates["traversal_recovery"] and gates["traversal_specificity"]:
        verdict = "PARTIAL"
    else:
        verdict = "NOT SUPPORTED"

    # Exact symmetry QA on ordered component definitions.
    _, rotated_t = component_steps(safe_log(amplitude), theta + np.pi / 3.0, score_window)
    phase_rotation_error = float(np.nanmax(np.abs(rotated_t[valid] - tp)))
    swapped_angle = np.unwrap(actual_angle + np.pi)
    _, swapped_t = component_steps(safe_log(separation), swapped_angle, score_window)
    hole_swap_traversal_error = float(np.nanmax(np.abs(swapped_t[valid] - th)))

    rev_c, rev_t = component_steps(safe_log(amplitude[::-1]), theta[::-1], score_window)
    reverse_radial_error = float(np.nanmedian(np.abs(rev_c[::-1][valid] + cp)))
    reverse_angular_error = float(np.nanmedian(np.abs(rev_t[::-1][valid] + tp)))
    symmetry = {
        "global_phase_rotation_max_error": phase_rotation_error,
        "hole_label_swap_max_traversal_error": hole_swap_traversal_error,
        "chronology_reversal_median_radial_odd_parity_error": reverse_radial_error,
        "chronology_reversal_median_angular_odd_parity_error": reverse_angular_error,
    }

    # Full waveform-only timing diagnostics, fixed in the protocol.
    amp_full = amplitude_pred
    theta_full = np.asarray(pred["theta_hat"], dtype=float)
    c_full, tr_full = component_steps(safe_log(amp_full), theta_full, pred_window)
    relation_full = np.asarray(pred["relation_ara"], dtype=float)
    power_peak = float(np.asarray(pred["landmark_times"])[0])
    late = (relation_full <= 1.0) & (t_pred <= power_peak)
    late[:pred_window] = False
    late[-pred_window:] = False
    eligible = np.flatnonzero(late)
    if eligible.size == 0:
        raise RuntimeError("No eligible late-parent timing basin")

    def timing_indices(connection_steps: np.ndarray, traversal_steps: np.ndarray) -> tuple[list[tuple[str, int]], np.ndarray, np.ndarray, np.ndarray]:
        x_connection = rank02(np.abs(connection_steps))
        x_traversal = rank02(np.abs(traversal_steps))
        beta = np.arctan2(np.abs(traversal_steps), np.abs(connection_steps) + np.finfo(float).tiny)
        beta_change = np.abs(smooth(np.gradient(beta), pred_window))
        i_beta = int(eligible[np.argmax(beta_change[eligible])])
        diff = x_connection - x_traversal
        crossings = np.flatnonzero(late[:-1] & late[1:] & (np.signbit(diff[:-1]) != np.signbit(diff[1:])))
        i_cross = int(crossings[-1]) if crossings.size else int(eligible[np.argmin(np.abs(diff[eligible]))])
        ridge_distance = np.hypot(x_connection - 1.0, x_traversal - 1.0)
        i_ridge = int(eligible[np.argmin(ridge_distance[eligible])])
        return (
            [
                ("strongest path-direction change", i_beta),
                ("last connection/traversal crossing", i_cross),
                ("nearest joint ridge (1,1)", i_ridge),
            ],
            x_connection,
            x_traversal,
            beta,
        )

    def score_timing(control: str, indices: list[tuple[str, int]]) -> list[dict]:
        rows = []
        for name, idx in indices:
            predicted_time = float(t_pred[idx])
            signed_error = predicted_time - horizon
            rows.append(
                {
                    "control": control,
                    "landmark": name,
                    "time_M": predicted_time,
                    "signed_error_M": signed_error,
                    "absolute_error_M": abs(signed_error),
                    "absolute_error_cycles": abs(signed_error) / cycle,
                    "within_one_parent_cycle": abs(signed_error) <= cycle,
                }
            )
        return rows

    primary_indices, x_c_full, x_t_full, beta_full = timing_indices(c_full, tr_full)
    timing_rows = score_timing("observed order", primary_indices)

    timing_rng = np.random.default_rng(438)
    timing_perm = timing_rng.permutation(len(c_full))
    shuffled_indices, _, _, _ = timing_indices(c_full[timing_perm], tr_full[timing_perm])
    rolled_indices, _, _, _ = timing_indices(
        np.roll(c_full, len(c_full) // 4), np.roll(tr_full, len(tr_full) // 4)
    )
    swapped_indices, _, _, _ = timing_indices(tr_full, c_full)
    timing_control_rows = (
        timing_rows
        + score_timing("chronology shuffle", shuffled_indices)
        + score_timing("quarter-record roll", rolled_indices)
        + score_timing("radial/traversal swap", swapped_indices)
    )
    timing_baseline_rows = []
    for name, predicted_time in [
        ("waveform power crest baseline", power_peak),
        ("T435 frozen median baseline", float(pred["handover_hat"])),
    ]:
        signed_error = predicted_time - horizon
        timing_baseline_rows.append(
            {
                "control": "baseline",
                "landmark": name,
                "time_M": predicted_time,
                "signed_error_M": signed_error,
                "absolute_error_M": abs(signed_error),
                "absolute_error_cycles": abs(signed_error) / cycle,
                "within_one_parent_cycle": abs(signed_error) <= cycle,
            }
        )

    gate_rows = [
        {
            "order": 1,
            "gate": "Traversal recovery",
            "required": "rho >= 0.80",
            "observed": metrics["traversal_recovery_rho"],
            "passed": gates["traversal_recovery"],
        },
        {
            "order": 2,
            "gate": "Traversal specificity",
            "required": "margin >= 0.20",
            "observed": metrics["traversal_specificity_margin"],
            "passed": gates["traversal_specificity"],
        },
        {
            "order": 3,
            "gate": "Closure recovery",
            "required": "rho >= 0.50",
            "observed": metrics["closure_recovery_rho"],
            "passed": gates["closure_recovery"],
        },
        {
            "order": 4,
            "gate": "Closure specificity",
            "required": "margin >= 0.20",
            "observed": metrics["closure_specificity_margin"],
            "passed": gates["closure_specificity"],
        },
        {
            "order": 5,
            "gate": "Path-direction recovery",
            "required": "rho >= 0.50 and shuffle margin >= 0.20",
            "observed": metrics["path_direction_rho"],
            "passed": gates["path_direction"],
        },
    ]

    # Reviewed, bounded datasets for files and the portable report.
    xv_c = rank02(np.abs(cp))
    xv_t = rank02(np.abs(tp))
    xh_c = rank02(np.abs(ch))
    xh_t = rank02(np.abs(th))
    # Four long-form history series share this index; 450 keeps the canonical
    # report dataset under the portable reader's 2,000-row bound.
    sample_idx = np.unique(np.linspace(0, len(tv) - 1, min(450, len(tv)), dtype=int))

    component_rows = []
    for i in sample_idx:
        component_rows.extend(
            [
                {
                    "time_to_horizon_M": float(tv[i] - horizon),
                    "series": "waveform Space/Connection",
                    "ara_coordinate": float(xv_c[i]),
                },
                {
                    "time_to_horizon_M": float(tv[i] - horizon),
                    "series": "horizon radial closure",
                    "ara_coordinate": float(xh_c[i]),
                },
                {
                    "time_to_horizon_M": float(tv[i] - horizon),
                    "series": "waveform Time/Traversal",
                    "ara_coordinate": float(xv_t[i]),
                },
                {
                    "time_to_horizon_M": float(tv[i] - horizon),
                    "series": "horizon angular traversal",
                    "ara_coordinate": float(xh_t[i]),
                },
            ]
        )

    plane_rows = [
        {
            "time_to_horizon_M": float(tv[i] - horizon),
            "connection_ara": float(xv_c[i]),
            "traversal_ara": float(xv_t[i]),
            "stage": stage_label(float(tv[i]), horizon),
        }
        for i in sample_idx
    ]

    match_rows = []
    for i in sample_idx:
        match_rows.extend(
            [
                {
                    "component": "Space/Connection",
                    "waveform_coordinate": float(xv_c[i]),
                    "horizon_coordinate": float(xh_c[i]),
                },
                {
                    "component": "Time/Traversal",
                    "waveform_coordinate": float(xv_t[i]),
                    "horizon_coordinate": float(xh_t[i]),
                },
            ]
        )

    correlation_rows = [
        {
            "waveform_component": "Space/Connection",
            "hidden_target": "radial closure",
            "rho": metrics["closure_recovery_rho"],
            "role": "matching",
        },
        {
            "waveform_component": "Space/Connection",
            "hidden_target": "angular traversal",
            "rho": metrics["connection_on_hidden_traversal_rho"],
            "role": "cross",
        },
        {
            "waveform_component": "Time/Traversal",
            "hidden_target": "angular traversal",
            "rho": metrics["traversal_recovery_rho"],
            "role": "matching",
        },
        {
            "waveform_component": "Time/Traversal",
            "hidden_target": "radial closure",
            "rho": metrics["traversal_on_hidden_closure_rho"],
            "role": "cross",
        },
    ]

    pd.DataFrame(component_rows).to_csv(RESULTS / "T438_COMPONENT_HISTORIES.csv", index=False)
    pd.DataFrame(plane_rows).to_csv(RESULTS / "T438_SPACE_TIME_PLANE.csv", index=False)
    pd.DataFrame(match_rows).to_csv(RESULTS / "T438_COMPONENT_MATCH.csv", index=False)
    pd.DataFrame(correlation_rows).to_csv(RESULTS / "T438_CORRELATION_MATRIX.csv", index=False)
    pd.DataFrame(gate_rows).to_csv(RESULTS / "T438_GATES.csv", index=False)
    pd.DataFrame(timing_rows).to_csv(RESULTS / "T438_TIMING_DIAGNOSTICS.csv", index=False)
    pd.DataFrame(timing_control_rows + timing_baseline_rows).to_csv(
        RESULTS / "T438_TIMING_CONTROLS.csv", index=False
    )

    timing_control_summary = {
        control: {
            "within_one_cycle_count": int(
                sum(row["within_one_parent_cycle"] for row in timing_control_rows if row["control"] == control)
            ),
            "minimum_absolute_error_cycles": float(
                min(row["absolute_error_cycles"] for row in timing_control_rows if row["control"] == control)
            ),
        }
        for control in ["observed order", "chronology shuffle", "quarter-record roll", "radial/traversal swap"]
    }

    result = {
        "test": "T438_source_space_time_separation",
        "verdict": verdict,
        "evidence_class": "one-system, non-blind numerical-relativity calibration",
        "simulation": "SXS:BBH:0305 Lev6",
        "declared_orientation": {
            "space_connection": "radial accumulation/closure",
            "time_traversal": "angular movement around the recovered pair relation",
        },
        "sample_count_scored": int(valid.sum()),
        "smoothing_window_scored_samples": int(score_window),
        "common_horizon_time_M": horizon,
        "parent_cycle_M": cycle,
        "metrics": metrics,
        "gates": gates,
        "symmetry_checks": symmetry,
        "timing_diagnostics": timing_rows,
        "timing_controls": timing_control_rows,
        "timing_baselines": timing_baseline_rows,
        "timing_control_summary": timing_control_summary,
        "protocol_sha256_verified": True,
    }
    (RESULTS / "T438_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Static audit visual; the interactive portable report is the primary handoff.
    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 2, figsize=(17, 11), constrained_layout=True)
    fig.suptitle(f"T438 — source-side Space/Time separation: {verdict}", fontsize=20, fontweight="bold")

    ax = axes[0, 0]
    recent = tv >= horizon - 1500.0
    ax.plot(tv[recent] - horizon, xv_c[recent], color="#ff9f43", lw=1.2, label="waveform Space/Connection")
    ax.plot(tv[recent] - horizon, xh_c[recent], color="#ffd166", lw=1.1, alpha=0.8, label="hidden radial closure")
    ax.plot(tv[recent] - horizon, xv_t[recent], color="#5ba7ff", lw=1.2, label="waveform Time/Traversal")
    ax.plot(tv[recent] - horizon, xh_t[recent], color="#ae81ff", lw=1.1, alpha=0.8, label="hidden angular traversal")
    ax.axvline(0, color="white", ls="--", lw=1.2, label="first common horizon")
    ax.axhline(1, color="white", ls=":", alpha=0.5)
    ax.set(title="Independent component histories near handover", xlabel="simulation time relative to common horizon / M", ylabel="independent ARA coordinate (0–2)", ylim=(-0.05, 2.05))
    ax.legend(fontsize=8, ncol=2)

    ax = axes[0, 1]
    matrix = np.array(
        [
            [metrics["closure_recovery_rho"], metrics["connection_on_hidden_traversal_rho"]],
            [metrics["traversal_on_hidden_closure_rho"], metrics["traversal_recovery_rho"]],
        ]
    )
    im = ax.imshow(matrix, vmin=-1, vmax=1, cmap="coolwarm")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center", fontsize=14, fontweight="bold")
    ax.set_xticks([0, 1], ["hidden radial\nclosure", "hidden angular\ntraversal"])
    ax.set_yticks([0, 1], ["waveform Space/\nConnection", "waveform Time/\nTraversal"])
    ax.set_title("Matching versus crossed relations (Spearman rho)")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax = axes[1, 0]
    colors = {"inspiral": "#577590", "late approach": "#f9c74f", "post-common-horizon waveform": "#f94144"}
    for stage in colors:
        m = np.array([stage_label(float(tt), horizon) == stage for tt in tv])
        ax.scatter(xv_c[m], xv_t[m], s=8, alpha=0.35, color=colors[stage], label=stage)
    ax.axvline(1, color="white", ls=":", alpha=0.6)
    ax.axhline(1, color="white", ls=":", alpha=0.6)
    ax.set(title="Waveform-only Space/Time Di-ARA path", xlabel="Space/Connection step (0–2)", ylabel="Time/Traversal step (0–2)", xlim=(-0.05, 2.05), ylim=(-0.05, 2.05))
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    names = [row["landmark"] for row in timing_rows]
    y_positions = np.arange(len(names))
    control_colors = {
        "observed order": "#5ba7ff",
        "chronology shuffle": "#f94144",
        "quarter-record roll": "#f9c74f",
        "radial/traversal swap": "#ae81ff",
    }
    for control, color in control_colors.items():
        rows = [row for row in timing_control_rows if row["control"] == control]
        ax.scatter([row["signed_error_M"] for row in rows], y_positions, s=55, color=color, label=control, zorder=3)
    ax.axvline(0, color="white", lw=1.2, label="common horizon")
    ax.axvspan(-cycle, cycle, color="#5ee38f", alpha=0.15, label="±1 parent cycle")
    for y, row in zip(y_positions, timing_rows):
        ax.annotate(f"{row['signed_error_M']:+.1f} M", (row["signed_error_M"], y), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_yticks(y_positions, names)
    ax.set(title="Predeclared timing diagnostics (not primary gates)", xlabel="signed error relative to common horizon / M")
    ax.legend(fontsize=7, ncol=2)

    for ax in axes.flat:
        ax.grid(alpha=0.16)
    fig.savefig(RESULTS / "T438_SOURCE_SPACE_TIME_AUDIT.png", dpi=180)
    plt.close(fig)

    build_artifact(
        result=result,
        component_rows=component_rows,
        plane_rows=plane_rows,
        match_rows=match_rows,
        correlation_rows=correlation_rows,
        gate_rows=gate_rows,
        timing_rows=timing_rows,
        timing_control_rows=timing_control_rows,
        timing_baseline_rows=timing_baseline_rows,
    )
    print(json.dumps(result, indent=2))


def build_artifact(
    *,
    result: dict,
    component_rows: list[dict],
    plane_rows: list[dict],
    match_rows: list[dict],
    correlation_rows: list[dict],
    gate_rows: list[dict],
    timing_rows: list[dict],
    timing_control_rows: list[dict],
    timing_baseline_rows: list[dict],
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    metrics = result["metrics"]
    gates = result["gates"]
    verdict = result["verdict"]

    def csv_source(source_id: str, label: str, path: Path) -> dict:
        relative = relpath(path)
        return {
            "id": source_id,
            "label": label,
            "path": relative,
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": f"SELECT * FROM read_csv_auto('{relative}')",
                "description": f"Loads the reviewed rows from {path.name}.",
                "tables_used": [relative],
            },
        }

    result_relative = relpath(RESULTS / "T438_RESULTS.json")
    sources = [
        {
            "id": "t438_results",
            "label": "T438 scored component separation",
            "path": result_relative,
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": f"SELECT test, verdict, metrics, gates, timing_diagnostics, timing_controls, timing_control_summary FROM read_json_auto('{result_relative}')",
                "description": "Loads the frozen T438 score, metrics, gates and timing diagnostics.",
                "tables_used": [result_relative],
            },
        },
        csv_source("t438_components", "T438 reviewed component histories", RESULTS / "T438_COMPONENT_HISTORIES.csv"),
        csv_source("t438_plane", "T438 reviewed Space/Time plane", RESULTS / "T438_SPACE_TIME_PLANE.csv"),
        csv_source("t438_match", "T438 reviewed component matching rows", RESULTS / "T438_COMPONENT_MATCH.csv"),
        csv_source("t438_correlations", "T438 matching and crossed correlations", RESULTS / "T438_CORRELATION_MATRIX.csv"),
        csv_source("t438_gates", "T438 frozen empirical gates", RESULTS / "T438_GATES.csv"),
        csv_source("t438_timing", "T438 frozen timing diagnostics", RESULTS / "T438_TIMING_DIAGNOSTICS.csv"),
        csv_source("t438_timing_controls", "T438 timing diagnostics and frozen controls", RESULTS / "T438_TIMING_CONTROLS.csv"),
        {
            "id": "t438_protocol",
            "label": "Frozen T438 protocol",
            "path": relpath(PROTOCOL),
        },
        {
            "id": "t435_waveform",
            "label": "Sealed T435 waveform-only prediction",
            "path": relpath(PREDICTION),
        },
        {
            "id": "t435_horizons",
            "label": "T435 scored individual-horizon answer key",
            "path": relpath(SCORED),
        },
        {
            "id": "sxs0305",
            "label": "SXS:BBH:0305 public numerical-relativity simulation",
            "href": "https://zenodo.org/records/13182440",
        },
    ]

    headline = [
        {
            "traversal_rho": metrics["traversal_recovery_rho"],
            "traversal_margin": metrics["traversal_specificity_margin"],
            "closure_rho": metrics["closure_recovery_rho"],
            "path_rho": metrics["path_direction_rho"],
        }
    ]
    timing_chart = [
        {
            "landmark": row["landmark"],
            "absolute_error_cycles": row["absolute_error_cycles"],
            "control": row["control"],
        }
        for row in timing_control_rows + timing_baseline_rows
    ]
    source_sample = component_rows[:10]

    def metric_text(value: float) -> str:
        return f"{value:.3f}"

    all_pass = sum(bool(v) for v in gates.values())
    strongest = next(row for row in timing_rows if row["landmark"] == "strongest path-direction change")
    shuffled_strongest = next(
        row
        for row in timing_control_rows
        if row["control"] == "chronology shuffle" and row["landmark"] == "strongest path-direction change"
    )
    rolled_strongest = next(
        row
        for row in timing_control_rows
        if row["control"] == "quarter-record roll" and row["landmark"] == "strongest path-direction change"
    )
    summary_text = (
        f"## Technical summary\n\n**Frozen verdict: {verdict}.** "
        f"The waveform-only angular half-phase step recovered the hidden horizon traversal with "
        f"Spearman rho `{metrics['traversal_recovery_rho']:.3f}`, but its specificity margin over the radial waveform component was "
        f"`{metrics['traversal_specificity_margin']:.3f}`. The radial waveform step recovered hidden closure at rho "
        f"`{metrics['closure_recovery_rho']:.3f}`. Overall, `{all_pass}/5` frozen empirical gates passed. "
        "This identifies an operational Time/Traversal candidate only if the matching relations beat the crossed relations; "
        "it does not identify physical Time as a substance."
    )

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "T438 — Separating Space and Time in the Recovered Black-Hole Relation",
        "description": "Frozen source-side polar decomposition of the T435 recovered binary relation into radial Space/Connection and angular Time/Traversal components.",
        "generatedAt": now,
        "cards": [
            {
                "id": "headline_metrics",
                "dataset": "headline",
                "sourceId": "t438_results",
                "description": "Frozen component-recovery and specificity metrics on one SXS simulation.",
                "metrics": [
                    {"label": "Traversal recovery rho", "field": "traversal_rho", "format": "number"},
                    {"label": "Traversal specificity margin", "field": "traversal_margin", "format": "number"},
                    {"label": "Closure recovery rho", "field": "closure_rho", "format": "number"},
                    {"label": "Path-direction rho", "field": "path_rho", "format": "number"},
                ],
            }
        ],
        "charts": [
            {
                "id": "component_histories",
                "title": "Independent waveform and horizon component histories",
                "type": "line",
                "dataset": "component_histories",
                "sourceId": "t438_components",
                "encodings": {
                    "x": {"field": "time_to_horizon_M", "type": "quantitative"},
                    "y": {"field": "ara_coordinate", "type": "quantitative"},
                    "color": {"field": "series", "type": "nominal"},
                },
            },
            {
                "id": "component_match",
                "title": "Waveform components against matching horizon components",
                "type": "scatter",
                "dataset": "component_match",
                "sourceId": "t438_match",
                "encodings": {
                    "x": {"field": "waveform_coordinate", "type": "quantitative"},
                    "y": {"field": "horizon_coordinate", "type": "quantitative"},
                    "color": {"field": "component", "type": "nominal"},
                },
            },
            {
                "id": "space_time_plane",
                "title": "Waveform-only Space/Time Di-ARA path",
                "type": "scatter",
                "dataset": "space_time_plane",
                "sourceId": "t438_plane",
                "encodings": {
                    "x": {"field": "connection_ara", "type": "quantitative"},
                    "y": {"field": "traversal_ara", "type": "quantitative"},
                    "color": {"field": "stage", "type": "nominal"},
                },
            },
            {
                "id": "timing_diagnostics",
                "title": "Predeclared timing-diagnostic errors",
                "type": "bar",
                "dataset": "timing_chart",
                "sourceId": "t438_timing_controls",
                "encodings": {
                    "x": {"field": "landmark", "type": "nominal"},
                    "y": {"field": "absolute_error_cycles", "type": "quantitative"},
                    "color": {"field": "control", "type": "nominal"},
                },
                "options": {"orientation": "vertical", "grouping": "grouped"},
            },
        ],
        "tables": [
            {
                "id": "gate_table",
                "title": "Frozen empirical gates",
                "dataset": "gates",
                "sourceId": "t438_gates",
                "columns": [
                    {"field": "order", "label": "#", "format": "number"},
                    {"field": "gate", "label": "Gate"},
                    {"field": "required", "label": "Required"},
                    {"field": "observed", "label": "Observed", "format": "number"},
                    {"field": "passed", "label": "Pass"},
                ],
                "defaultSort": {"field": "order", "direction": "asc"},
            },
            {
                "id": "timing_table",
                "title": "Timing diagnostics against first common horizon",
                "dataset": "timing",
                "sourceId": "t438_timing",
                "columns": [
                    {"field": "landmark", "label": "Landmark"},
                    {"field": "time_M", "label": "Time", "format": "number", "unit": "M"},
                    {"field": "signed_error_M", "label": "Signed error", "format": "number", "unit": "M", "movement": True},
                    {"field": "absolute_error_cycles", "label": "Absolute error", "format": "number", "unit": "parent cycles"},
                    {"field": "within_one_parent_cycle", "label": "Within one cycle"},
                ],
                "defaultSort": {"field": "absolute_error_cycles", "direction": "asc"},
            },
            {
                "id": "timing_control_table",
                "title": "Observed-order timing against frozen controls and baselines",
                "dataset": "timing_controls",
                "sourceId": "t438_timing_controls",
                "columns": [
                    {"field": "control", "label": "Order/control"},
                    {"field": "landmark", "label": "Landmark"},
                    {"field": "signed_error_M", "label": "Signed error", "format": "number", "unit": "M", "movement": True},
                    {"field": "absolute_error_cycles", "label": "Absolute error", "format": "number", "unit": "parent cycles"},
                    {"field": "within_one_parent_cycle", "label": "Within one cycle"},
                ],
                "defaultSort": {"field": "absolute_error_cycles", "direction": "asc"},
            },
            {
                "id": "correlation_table",
                "title": "Matching and crossed component relations",
                "dataset": "correlations",
                "sourceId": "t438_correlations",
                "columns": [
                    {"field": "waveform_component", "label": "Waveform component"},
                    {"field": "hidden_target", "label": "Hidden horizon target"},
                    {"field": "rho", "label": "Spearman rho", "format": "number"},
                    {"field": "role", "label": "Role"},
                ],
                "defaultSort": {"field": "rho", "direction": "desc"},
            },
            {
                "id": "source_sample_table",
                "title": "First ten reviewed component-history rows",
                "dataset": "source_sample",
                "sourceId": "t438_components",
                "columns": [
                    {"field": "time_to_horizon_M", "label": "Time to horizon", "format": "number", "unit": "M"},
                    {"field": "series", "label": "Series"},
                    {"field": "ara_coordinate", "label": "ARA coordinate", "format": "number"},
                ],
                "defaultSort": {"field": "time_to_horizon_M", "direction": "asc"},
            },
        ],
        "sources": sources,
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T438 — Separating Space and Time in the Recovered Black-Hole Relation"},
            {"id": "technical_summary", "type": "markdown", "sourceId": "t438_results", "body": summary_text},
            {"id": "headline", "type": "metric-strip", "cardIds": ["headline_metrics"]},
            {
                "id": "main_result",
                "type": "markdown",
                "sourceId": "t438_results",
                "body": (
                    "## The matching components must beat the crossed relations\n\n"
                    f"Time/Traversal matched hidden angular traversal at rho `{metric_text(metrics['traversal_recovery_rho'])}`; "
                    f"Space/Connection matched hidden radial closure at rho `{metric_text(metrics['closure_recovery_rho'])}`. "
                    "The correlation table is the decisive read: a high diagonal alone is insufficient if both waveform components simply track the same maturity trend."
                ),
            },
            {"id": "correlation_table_block", "type": "table", "tableId": "correlation_table"},
            {
                "id": "history_read",
                "type": "markdown",
                "sourceId": "t438_components",
                "body": "## The split is radial change versus angular traversal\n\nEach history is independently ranked onto 0–2 only for visual comparison. The orange pair asks how connection amount changes radially; the blue/purple pair asks how the relation advances around its axis. Because the axes are independent, their sum has no prescribed value.",
            },
            {"id": "component_histories_block", "type": "chart", "chartId": "component_histories"},
            {"id": "component_match_block", "type": "chart", "chartId": "component_match"},
            {
                "id": "plane_read",
                "type": "markdown",
                "sourceId": "t438_plane",
                "body": "## The Di-ARA plane shows the source path without manufacturing a complement\n\nEvery point is one ordered source step. Horizontal position is radial Space/Connection change; vertical position is angular Time/Traversal change. Colour shows whether the waveform sample is early inspiral, late approach or post-common-horizon waveform. A trajectory is evidence of coupled evolution, not by itself evidence that either axis is literal spacetime.",
            },
            {"id": "space_time_plane_block", "type": "chart", "chartId": "space_time_plane"},
            {
                "id": "scope_definitions",
                "type": "markdown",
                "sourceId": "t438_protocol",
                "body": "## Scope and metric definitions\n\nThe source is one SXS numerical-relativity simulation. The waveform-only radius is the square root of total modal power; the waveform angle is the T435 half-phase child axis. Hidden radial closure is minus the log-change of A–B horizon separation, while hidden traversal is the angular change of the A–B horizon axis. Spearman correlations are calculated on the common inspiral support after the frozen T435 smoothing span is transferred to the horizon grid.",
            },
            {
                "id": "methodology",
                "type": "markdown",
                "sourceId": "t438_protocol",
                "body": "## Frozen polar-decomposition methodology\n\nFor `z=A exp(i theta)`, the local differential is radial `dA` plus tangential `A dtheta`. T438 uses the scale-free pair `d log A` and `d theta`. A single constant orientation/handedness symmetry already allowed by T435 is removed; no time-varying fit is permitted. Chronology shuffle, quarter-roll, phase rotation, hole swap and reversal checks are scored separately.",
            },
            {"id": "gate_table_block", "type": "table", "tableId": "gate_table"},
            {
                "id": "timing_read",
                "type": "markdown",
                "sourceId": "t438_results",
                "body": (
                    "## Ordered joint-path change is the useful timing lead\n\n"
                    f"The strongest radial-versus-angular path-direction change landed `{strongest['absolute_error_cycles']:.3f}` parent cycles from first common-horizon formation. "
                    f"The same rule moved to `{shuffled_strongest['absolute_error_cycles']:.1f}` cycles under chronology shuffle and `{rolled_strongest['absolute_error_cycles']:.1f}` cycles under a quarter-record roll. "
                    "The last component crossing is weaker evidence because one shuffled ordering also landed within a cycle. Radial/traversal label swap leaves these symmetric landmarks unchanged, so they locate a joint handover but cannot by themselves decide which axis is physical Time."
                ),
            },
            {"id": "timing_diagnostics_block", "type": "chart", "chartId": "timing_diagnostics"},
            {"id": "timing_control_table_block", "type": "table", "tableId": "timing_control_table"},
            {
                "id": "limits",
                "type": "markdown",
                "body": "## Limits and robustness boundary\n\nT438 is not blind because T435 already revealed the horizon answer key. It uses a simulation generated within general relativity, not independent detector evidence. The half-phase traversal crosswalk is expected to be strong after T435's orientation result; the stricter question is component specificity and whether the radial waveform amount independently matches radial horizon closure. Empirical ranks expose ordering, not absolute physical units, and one source cannot establish universality.",
            },
            {"id": "source_sample_block", "type": "table", "tableId": "source_sample_table"},
            {
                "id": "next",
                "type": "markdown",
                "body": "## Recommended next step\n\nIf traversal specificity survives, freeze this exact polar split on several additional SXS binaries and test whether one unchanged Time/Traversal landmark predicts the offset from waveform crest to first common horizon. If specificity fails, do not rename cadence as Time; instead test a genuinely independent source relation such as mode-to-mode phase lag or horizon shear on a development system before another holdout.",
            },
            {
                "id": "questions",
                "type": "markdown",
                "body": "## Further questions\n\n- Does the same separation survive mass-ratio and spin changes?\n- Is the relevant Time-facing observable angular traversal itself, remaining traversal budget, or a cross-scale phase lag?\n- Which source observable supplies an independent radial connection measure without sharing the same chirp cadence?\n- Can a frozen component landmark improve common-horizon timing across untouched simulations?",
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": now,
            "status": "ready",
            "datasets": {
                "headline": headline,
                "component_histories": component_rows,
                "component_match": match_rows,
                "space_time_plane": plane_rows,
                "timing_chart": timing_chart,
                "gates": gate_rows,
                "timing": timing_rows,
                "timing_controls": timing_control_rows + timing_baseline_rows,
                "correlations": correlation_rows,
                "source_sample": source_sample,
            },
        },
        "sources": sources,
    }
    (RESULTS / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
