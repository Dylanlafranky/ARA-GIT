"""T362: frozen laboratory-fault Irrationality Di-ARA test.

The claim and protocol were hashed before this scorer was written.  The dense
primary record contains independently measured local shear stress and nearby
local fault displacement.  Fifteen published coupling histories provide the
connection-side replication.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
NPZ = HERE / "T362_SOURCE_EVENT101_QA_2MS.npz"
COUPLING = HERE / "T362_SOURCE_ACOSTA_COUPLING_15.csv"
CLAIM = HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md"
PROTOCOL = HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"

EXPECTED_SHA256 = {
    CLAIM.name: "34FB8445B4C49B421D5FAEE2FC75E8EE5386C827A8798F96C794EB89488DE8F8",
    PROTOCOL.name: "C015E113906130E10858807126F9A3EB3BBFA214C50739E043CFF785DCCB6299",
}
EXPECTED_MD5 = {
    "T362_SOURCE_Event101_ShearStress_Time.txt": "8F380689AFBCB9C092D48808A04CB1E7",
    "T362_SOURCE_Event101_ShearStress_S20_x73.15mm.txt": "F9C64F17BD62C6B037E1D25D5EE26954",
    "T362_SOURCE_Event101_FaultDisplacement_Time.txt": "CE02B3D212B3E1CA03B4876399783FAD",
    "T362_SOURCE_Event101_FaultDisplacement_L3_x70mm.txt": "973C817C03C95A63F0E3B82BA6B5C247",
    "T362_SOURCE_Acosta_2019_Figure1Data.xlsx": "EBB1D8B290AD1324DAC1E3AAB3B9D308",
}

WINDOW = 512
STEP = 64
SPLIT_SHARE = 0.80
RNG_SEED = 362


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def robust_map(values: np.ndarray, q05: float, q95: float) -> np.ndarray:
    return np.clip(2.0 * (values - q05) / (q95 - q05), 0.0, 2.0)


def circular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs((a - b + 0.5) % 1.0 - 0.5)


def quadrant(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    # User-frozen orientation: upper-right Ab, lower-right aB,
    # lower-left bA, upper-left Ba.
    return np.select(
        [
            (x >= 1) & (y >= 1),
            (x >= 1) & (y < 1),
            (x < 1) & (y < 1),
            (x < 1) & (y >= 1),
        ],
        ["Ab", "aB", "bA", "Ba"],
        default="ridge",
    )


def parent_window(xc: np.ndarray, xm: np.ndarray, with_history: bool) -> dict[str, float]:
    z = np.mod(np.arctan2(xm - 1.0, xc - 1.0) / (2.0 * np.pi), 1.0)
    resolutions = np.array([16, 32, 64, 128, 256], dtype=float)
    occupied = []
    for resolution in resolutions.astype(int):
        occupied.append(np.unique(np.floor(z * resolution).astype(int) % resolution).size)
    slope = np.polyfit(np.log(resolutions), np.log(np.maximum(occupied, 1)), 1)[0]
    xp = float(np.clip(2.0 * slope, 0.0, 2.0))

    half = len(z) // 2
    train_source, train_target = z[: half - 1], z[1:half]
    test_source, test_target = z[half:-1], z[half + 1 :]
    train_xy = np.column_stack(
        [np.cos(2 * np.pi * train_source), np.sin(2 * np.pi * train_source)]
    )
    test_xy = np.column_stack(
        [np.cos(2 * np.pi * test_source), np.sin(2 * np.pi * test_source)]
    )
    neighbours = cKDTree(train_xy).query(test_xy, k=9)[1]
    target_complex = np.exp(2j * np.pi * train_target)
    prediction = np.mod(np.angle(np.mean(target_complex[neighbours], axis=1)) / (2 * np.pi), 1)
    loss = float(np.mean(circular_distance(prediction, test_target)))
    baseline = np.mod(np.angle(np.mean(target_complex)) / (2 * np.pi), 1)
    baseline_loss = float(np.mean(circular_distance(baseline, test_target)))
    xr = float(np.clip(2.0 * loss / max(baseline_loss, 1e-12), 0.0, 2.0))

    out = {
        "x_P": xp,
        "x_R": xr,
        "radius_mean": float(np.mean(np.hypot(xc - 1, xm - 1))),
        "successor_loss": loss,
        "successor_no_history_loss": baseline_loss,
    }
    if with_history:
        coherences = []
        for lag in range(1, 129):
            delta = np.mod(z[lag:] - z[:-lag], 1.0)
            coherences.append(abs(np.mean(np.exp(2j * np.pi * delta))))
        out["history_coherence_mean"] = float(np.mean(coherences))
        out["history_coherence_peak"] = float(np.max(coherences))
        out["history_peak_lag"] = int(np.argmax(coherences) + 1)
    return out


def parent_series(xc: np.ndarray, xm: np.ndarray, time: np.ndarray, history: bool) -> pd.DataFrame:
    rows = []
    for end in range(WINDOW - 1, len(xc), STEP):
        result = parent_window(xc[end - WINDOW + 1 : end + 1], xm[end - WINDOW + 1 : end + 1], history)
        result.update({"end_index": end, "end_time_s": float(time[end])})
        rows.append(result)
    frame = pd.DataFrame(rows)
    frame["quadrant"] = quadrant(frame["x_P"].to_numpy(), frame["x_R"].to_numpy())
    step = np.hypot(frame["x_P"].diff(), frame["x_R"].diff())
    frame["parent_step"] = step.fillna(0.0)
    return frame


def handover(parent: pd.DataFrame) -> tuple[float, float]:
    row = parent.loc[parent["parent_step"].idxmax()]
    return float(row["end_time_s"]), float(row["parent_step"])


def knn_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, k: int = 31) -> np.ndarray:
    neighbours = cKDTree(train_x).query(test_x, k=k)[1]
    return np.median(train_y[neighbours], axis=1)


def prediction_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    error = predicted - actual
    nonzero = (np.abs(actual) > 1e-12) | (np.abs(predicted) > 1e-12)
    direction = np.mean(np.sign(actual[nonzero]) == np.sign(predicted[nonzero])) if np.any(nonzero) else np.nan
    return {
        "RMSE": float(np.sqrt(np.mean(error**2))),
        "MAE": float(np.mean(np.abs(error))),
        "direction_agreement": float(direction),
    }


def coupling_replication() -> pd.DataFrame:
    source = pd.read_csv(COUPLING)
    rows = []
    for (medium, event), group in source.groupby(["medium", "event"], sort=True):
        group = group.sort_values("time_to_mainshock_s")
        group = group[(group["time_to_mainshock_s"] >= -50) & (group["time_to_mainshock_s"] <= 0)]
        t = group["time_to_mainshock_s"].to_numpy(float)
        y = group["coupling"].to_numpy(float)
        dt = float(np.median(np.diff(t)))
        width = int(round(1.0 / dt))
        if width % 2 == 0:
            width += 1
        kernel = np.ones(width) / width
        smooth_valid = np.convolve(y, kernel, mode="valid")
        half = width // 2
        smooth_time = t[half : len(t) - half]
        fall = -np.diff(smooth_valid)
        index = int(np.argmax(fall)) + 1
        event_time = float(smooth_time[index])
        rows.append(
            {
                "medium": medium,
                "event": int(event),
                "handover_time_s": event_time,
                "persistent_fall_per_step": float(fall[index - 1]),
                "final_20_percent": bool(-10 <= event_time <= 0),
                "start_coupling": float(y[0]),
                "end_coupling": float(y[-1]),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    qa = []
    for name, expected in EXPECTED_MD5.items():
        actual = digest(HERE / name, "md5")
        qa.append({"item": name, "algorithm": "MD5", "expected": expected, "actual": actual, "passed": actual == expected})
    for name, expected in EXPECTED_SHA256.items():
        actual = digest(HERE / name, "sha256")
        qa.append({"item": name, "algorithm": "SHA256", "expected": expected, "actual": actual, "passed": actual == expected})
    qa_frame = pd.DataFrame(qa)
    source_qa = bool(qa_frame["passed"].all())

    raw = np.load(NPZ)
    time = raw["time"]
    stress = raw["stress_mean"]
    displacement = raw["disp_mean"]
    n = len(time)
    split = int(np.floor(SPLIT_SHARE * n))
    calibration = slice(0, split)

    displacement_delta = np.diff(displacement, append=displacement[-1])
    positive_scale = float(np.median(np.abs(displacement_delta[:split][np.abs(displacement_delta[:split]) > 0])))
    movement_log = np.log1p(np.abs(displacement_delta) / positive_scale)
    stress_q05, stress_q95 = np.quantile(stress[calibration], [0.05, 0.95])
    movement_q05, movement_q95 = np.quantile(movement_log[calibration], [0.05, 0.95])
    xc = robust_map(stress, stress_q05, stress_q95)
    xm = robust_map(movement_log, movement_q05, movement_q95)
    main_index = int(np.argmax(displacement_delta))
    main_time = float(time[main_index + 1])

    dir_c = np.sign(np.diff(xc, prepend=xc[0]))
    dir_m = np.sign(displacement_delta)
    dir_c[dir_c == 0] = 1
    dir_m[dir_m == 0] = 1
    physical_q = quadrant(xc, xm)
    physical_occupancy = {key: int(np.sum(physical_q == key)) for key in ["Ab", "aB", "bA", "Ba"]}

    exclude = np.abs(time - main_time) > 0.1
    raw_correlation = float(np.corrcoef(xc[exclude], xm[exclude])[0, 1])

    parent = parent_series(xc, xm, time, history=True)
    ara_time, ara_step = handover(parent)
    real_timing_error = abs(ara_time - main_time)

    controls = []
    rng = np.random.default_rng(RNG_SEED)
    shuffle_errors = []
    for number in range(100):
        order = rng.permutation(n)
        shuffled = parent_series(xc[order], xm[order], time, history=False)
        # Shuffled values have no physical time.  Preserve window position as the
        # destroyed-chronology pseudo-time against the real slip location.
        event_time, event_step = handover(shuffled)
        error = abs(event_time - main_time)
        shuffle_errors.append(error)
        controls.append({"control": f"time_shuffle_{number:03d}", "handover_time_s": event_time, "timing_error_s": error, "parent_step": event_step})

    geometry_controls = {
        "wrong_pair": (xc, np.roll(xm, n // 4)),
        "connection_only": (xc, np.ones_like(xm)),
        "movement_only": (np.ones_like(xc), xm),
        "reversed_descriptive": (xc[::-1], xm[::-1]),
    }
    control_parents = {}
    for name, (control_xc, control_xm) in geometry_controls.items():
        p = parent_series(control_xc, control_xm, time, history=False)
        control_parents[name] = p
        event_time, event_step = handover(p)
        error = abs(event_time - main_time)
        controls.append({"control": name, "handover_time_s": event_time, "timing_error_s": error, "parent_step": event_step})
    control_frame = pd.DataFrame(controls)

    target = np.sign(displacement_delta) * movement_log
    # A feature at slice i predicts the movement from slice i+1 to i+2.
    # This keeps the recorder causal and prevents x_M/direction_M from
    # containing the response it is asked to predict.
    train_index = np.arange(1, split - 1)
    test_index = np.arange(split - 1, n - 1)
    train_target = target[train_index + 1]
    test_target = target[test_index + 1]
    feature_sets = {
        "two_axis_directional": np.column_stack([xc, xm, dir_c, dir_m]),
        "direction_blind": np.column_stack([xc, xm]),
        "connection_only": np.column_stack([xc, dir_c]),
        "movement_only": np.column_stack([xm, dir_m]),
    }
    predictions = {}
    metric_rows = []
    for name, features in feature_sets.items():
        prediction = knn_predict(features[train_index], train_target, features[test_index])
        predictions[name] = prediction
        metrics = prediction_metrics(test_target, prediction)
        metrics["method"] = name
        metric_rows.append(metrics)
    wrong_target = np.roll(train_target, len(train_index) // 4)
    prediction = knn_predict(feature_sets["two_axis_directional"][train_index], wrong_target, feature_sets["two_axis_directional"][test_index])
    predictions["wrong_pair"] = prediction
    metrics = prediction_metrics(test_target, prediction)
    metrics["method"] = "wrong_pair"
    metric_rows.append(metrics)
    prediction = target[test_index]
    predictions["persistence"] = prediction
    metrics = prediction_metrics(test_target, prediction)
    metrics["method"] = "persistence"
    metric_rows.append(metrics)
    prediction_frame = pd.DataFrame(metric_rows).set_index("method").reset_index()
    prediction_rows = pd.DataFrame(
        {
            "feature_index": test_index,
            "feature_time_s": time[test_index],
            "target_index": test_index + 1,
            "target_time_s": time[test_index + 1],
            "actual_next_signed_log_increment": test_target,
            **{f"predicted_{name}": values for name, values in predictions.items()},
        }
    )

    primary_prediction = predictions["two_axis_directional"]
    main_test_location = int(np.flatnonzero(test_index == main_index - 1)[0])
    main_risk = float(abs(primary_prediction[main_test_location]))
    risk_percentile = float(np.mean(np.abs(primary_prediction) <= main_risk))

    replication = coupling_replication()
    dry_pass = int(replication.query("medium == 'dry'")["final_20_percent"].sum())
    fluid_pass = int(replication.query("medium == 'fluid'")["final_20_percent"].sum())
    replication_pass = int(replication["final_20_percent"].sum())

    parent_occupancy = parent["quadrant"].value_counts().to_dict()
    g1_quadrants = sum(value >= 0.01 * n for value in physical_occupancy.values())
    g2_quadrants = sum(value >= 3 for value in parent_occupancy.values())
    nonprimary = prediction_frame.query("method != 'two_axis_directional'")
    primary_metrics = prediction_frame.query("method == 'two_axis_directional'").iloc[0]

    gates = [
        {
            "gate": "G1 independent physical traversal",
            "passed": bool(source_qa and abs(raw_correlation) < 0.98 and g1_quadrants >= 3),
            "observed": f"source QA={source_qa}; |r|={abs(raw_correlation):.4f}; qualifying quadrants={g1_quadrants}/4",
        },
        {
            "gate": "G2 Irrationality parent traversal",
            "passed": bool(g2_quadrants >= 2 and real_timing_error <= 1.024),
            "observed": f"qualifying quadrants={g2_quadrants}/4; timing error={real_timing_error:.3f} s",
        },
        {
            "gate": "G3 broken-geometry discrimination",
            "passed": bool(
                real_timing_error < np.median(shuffle_errors)
                and all(real_timing_error < float(control_frame.query("control == @name")["timing_error_s"].iloc[0]) for name in ["wrong_pair", "connection_only", "movement_only"])
            ),
            "observed": (
                f"real={real_timing_error:.3f} s; shuffle median={np.median(shuffle_errors):.3f} s; "
                + "; ".join(
                    f"{name}={float(control_frame.query('control == @name')['timing_error_s'].iloc[0]):.3f} s"
                    for name in ["wrong_pair", "connection_only", "movement_only"]
                )
            ),
        },
        {
            "gate": "G4 two-axis movement record",
            "passed": bool(
                primary_metrics["RMSE"] <= 0.90 * float(nonprimary["RMSE"].min())
                and primary_metrics["direction_agreement"] >= 0.65
            ),
            "observed": f"primary RMSE={primary_metrics['RMSE']:.4f}; best control={float(nonprimary['RMSE'].min()):.4f}; direction={primary_metrics['direction_agreement']:.3f}",
        },
        {
            "gate": "G5 held-out rupture localization",
            "passed": bool(risk_percentile >= 0.99),
            "observed": f"main-slip predicted-risk percentile={risk_percentile:.4f}",
        },
        {
            "gate": "G6 repeated connection handover",
            "passed": bool(replication_pass >= 12 and dry_pass >= 8 and fluid_pass >= 4),
            "observed": f"all={replication_pass}/15; dry={dry_pass}/10; fluid={fluid_pass}/5",
        },
    ]
    overall = bool(all(row["passed"] for row in gates))

    source_rows = pd.DataFrame(
        {
            "time_s": time,
            "time_to_main_slip_s": time - main_time,
            "stress_mpa": stress,
            "displacement_micrometre": displacement,
            "signed_displacement_increment": displacement_delta,
            "x_C": xc,
            "x_M": xm,
            "direction_C": dir_c,
            "direction_M": dir_m,
            "quadrant": physical_q,
        }
    )
    source_rows.to_csv(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_TIMESERIES.csv", index=False)
    parent.to_csv(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_PARENT_WINDOWS.csv", index=False)
    control_frame.to_csv(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_CONTROLS.csv", index=False)
    prediction_frame.to_csv(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_PREDICTORS.csv", index=False)
    prediction_rows.to_csv(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_PREDICTION_PATH.csv", index=False)
    replication.to_csv(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_REPLICATION.csv", index=False)
    pd.DataFrame(gates).to_csv(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_FROZEN_GATES.csv", index=False)
    qa_frame.to_csv(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_SOURCE_QA.csv", index=False)

    result = {
        "test": "T362 laboratory-fault Irrationality Di-ARA",
        "run_date": "2026-08-12",
        "verdict": "SUPPORTED ON THIS PHYSICAL ARCHIVE" if overall else "NOT SUPPORTED ON THIS PHYSICAL ARCHIVE",
        "all_gates_passed": overall,
        "main_slip_time_s": main_time,
        "ara_handover_time_s": ara_time,
        "ara_timing_error_s": real_timing_error,
        "raw_axis_correlation_excluding_rupture": raw_correlation,
        "physical_quadrant_occupancy": physical_occupancy,
        "parent_quadrant_occupancy": parent_occupancy,
        "main_slip_risk_percentile": risk_percentile,
        "gates": gates,
        "prediction_metrics": prediction_frame.to_dict(orient="records"),
        "replication": {"all": replication_pass, "dry": dry_pass, "fluid": fluid_pass},
        "frozen_hashes": EXPECTED_SHA256,
    }
    with (HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    make_figure(
        time,
        stress,
        displacement,
        xc,
        xm,
        main_time,
        ara_time,
        parent,
        prediction_frame,
        replication,
        gates,
    )
    print(json.dumps(result, indent=2))


def make_figure(
    time: np.ndarray,
    stress: np.ndarray,
    displacement: np.ndarray,
    xc: np.ndarray,
    xm: np.ndarray,
    main_time: float,
    ara_time: float,
    parent: pd.DataFrame,
    predictors: pd.DataFrame,
    replication: pd.DataFrame,
    gates: list[dict],
) -> None:
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig, axes = plt.subplots(3, 2, figsize=(18, 15), constrained_layout=True)
    fig.suptitle("T362 — laboratory-fault Irrationality Di-ARA", fontsize=20, fontweight="bold")

    relative = time - main_time
    ax = axes[0, 0]
    ax.plot(relative, stress, color="#2f6ea5", lw=0.8, label="local shear stress (connection)")
    ax.set_xlabel("time to main slip (s)")
    ax.set_ylabel("shear stress (MPa)", color="#2f6ea5")
    ax2 = ax.twinx()
    ax2.plot(relative, displacement, color="#e0902d", lw=1.0, label="local displacement (movement)")
    ax2.set_ylabel("fault displacement (µm)", color="#e0902d")
    ax.axvline(0, color="#bf3f3f", lw=1.5, label="main slip")
    ax.axvline(ara_time - main_time, color="#6d4bb3", lw=1.5, ls="--", label="ARA handover")
    ax.set_title("Independent physical channels through the rupture")
    ax.legend(loc="upper left", frameon=False)

    ax = axes[0, 1]
    sample = np.arange(0, len(xc), max(1, len(xc) // 5000))
    color = relative[sample]
    points = ax.scatter(xc[sample], xm[sample], c=color, s=7, cmap="viridis", alpha=0.65)
    ax.axvline(1, color="#777", lw=1)
    ax.axhline(1, color="#777", lw=1)
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="x_C — connection loading", ylabel="x_M — movement", title="Physical 0–2 Di-ARA trajectory")
    ax.set_aspect("equal")
    for x, y, text in [(1.72, 1.86, "Ab"), (1.72, 0.12, "aB"), (0.12, 0.12, "bA"), (0.12, 1.86, "Ba")]:
        ax.text(x, y, text, ha="center", va="center", fontweight="bold")
    fig.colorbar(points, ax=ax, label="time to main slip (s)")

    ax = axes[1, 0]
    points = ax.scatter(parent["x_P"], parent["x_R"], c=parent["end_time_s"] - main_time, cmap="plasma", s=28)
    ax.plot(parent["x_P"], parent["x_R"], color="#888", lw=0.6, alpha=0.5)
    ax.axvline(1, color="#777", lw=1)
    ax.axhline(1, color="#777", lw=1)
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="x_P — reused ↔ open addresses", ylabel="x_R — determined ↔ residual", title="Irrationality parent: chronological window path")
    ax.set_aspect("equal")
    fig.colorbar(points, ax=ax, label="window end relative to slip (s)")

    ax = axes[1, 1]
    order = predictors.sort_values("RMSE")
    colors = ["#2f6ea5" if name == "two_axis_directional" else "#aab3bd" for name in order["method"]]
    ax.barh(order["method"], order["RMSE"], color=colors)
    for i, row in enumerate(order.itertuples()):
        ax.text(row.RMSE, i, f"  RMSE {row.RMSE:.3f} · dir {row.direction_agreement:.2f}", va="center", fontsize=9)
    ax.set_xlabel("held-out next-movement RMSE (lower is better)")
    ax.set_title("Frozen movement-record controls")

    ax = axes[2, 0]
    groups = replication.copy()
    groups["row"] = np.arange(len(groups))
    colors = groups["medium"].map({"dry": "#a36a2d", "fluid": "#2d87a3"})
    ax.scatter(groups["handover_time_s"], groups["row"], c=colors, s=70)
    ax.axvspan(-10, 0, color="#d4efd7", alpha=0.8, label="frozen final-20% gate")
    ax.axvline(0, color="#bf3f3f", lw=1)
    ax.set_yticks(groups["row"], [f"{m} {e}" for m, e in zip(groups["medium"], groups["event"])])
    ax.set(xlim=(-50, 1), xlabel="connection-handover time to mainshock (s)", title="15 independent connection-side histories")
    ax.legend(frameon=False)

    ax = axes[2, 1]
    ax.axis("off")
    rows = [[g["gate"].split()[0], "PASS" if g["passed"] else "FAIL", g["observed"]] for g in gates]
    table = ax.table(cellText=rows, colLabels=["Gate", "Result", "Observed"], colWidths=[0.10, 0.13, 0.77], cellLoc="left", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 2.1)
    for row_number, gate in enumerate(gates, start=1):
        table[(row_number, 1)].set_facecolor("#cfe9d3" if gate["passed"] else "#f3c9c9")
        table[(row_number, 1)].set_text_props(fontweight="bold")
    ax.set_title("Frozen gates — visuals cannot rescue a failed gate", pad=12)

    fig.savefig(HERE / "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_FIGURE.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
