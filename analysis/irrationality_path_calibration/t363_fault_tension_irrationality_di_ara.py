"""T363 frozen fault-tension Irrationality Di-ARA physical test."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
NPZ = HERE / "T362_SOURCE_EVENT101_QA_2MS.npz"
EVENT_SOURCE = HERE / "T363_SOURCE_ACOSTA_STRESS_EVENTS_15.csv"
EVENT_META = HERE / "T363_SOURCE_ACOSTA_STRESS_EVENTS_META.csv"
EVENT_SCALES = HERE / "T363_SOURCE_ACOSTA_STRESS_MEDIUM_SCALES.csv"
CLAIM = HERE / "T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md"
PROTOCOL = HERE / "T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"
PREFIX = "T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_"

EXPECTED_SHA256 = {
    CLAIM.name: "6CA197872CBF3324CDCAE13E41BAB21C3EE75BD6A2B7D8DB1301275C3548806B",
    PROTOCOL.name: "C746FAD21356EAE0A8B95DECABCE5F218DD667160BBC11B88AD13939E0D5BC80",
}
EXPECTED_MD5 = {
    "T362_SOURCE_Event101_ShearStress_Time.txt": "8F380689AFBCB9C092D48808A04CB1E7",
    "T362_SOURCE_Event101_ShearStress_S20_x73.15mm.txt": "F9C64F17BD62C6B037E1D25D5EE26954",
    "T362_SOURCE_Event101_FaultDisplacement_Time.txt": "CE02B3D212B3E1CA03B4876399783FAD",
    "T362_SOURCE_Event101_FaultDisplacement_L3_x70mm.txt": "973C817C03C95A63F0E3B82BA6B5C247",
    "T362_SOURCE_Acosta_2019_Figure1Data.xlsx": "EBB1D8B290AD1324DAC1E3AAB3B9D308",
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def trailing_mean(values: np.ndarray, width: int) -> np.ndarray:
    total = np.cumsum(np.insert(values, 0, 0.0))
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    return (total[index + 1] - total[start]) / (index - start + 1)


def trailing_sum(values: np.ndarray, width: int) -> np.ndarray:
    total = np.cumsum(np.insert(values, 0, 0.0))
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    return total[index + 1] - total[start]


def robust_map(values: np.ndarray, q05: float, q95: float) -> np.ndarray:
    return np.clip(2 * (values - q05) / (q95 - q05), 0, 2)


def tension_coordinates(stress: np.ndarray, smooth_width: int, transfer_width: int, q05: float, q95: float):
    smooth = trailing_mean(stress, smooth_width)
    delta = np.diff(smooth, prepend=smooth[0])
    accumulation = trailing_sum(np.maximum(delta, 0), transfer_width)
    release = trailing_sum(np.maximum(-delta, 0), transfer_width)
    activity = accumulation + release
    xf = np.divide(2 * release, activity, out=np.ones_like(release), where=activity > 1e-15)
    xs = robust_map(smooth, q05, q95)
    return smooth, delta, accumulation, release, activity, xs, xf


def circular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs((a - b + 0.5) % 1 - 0.5)


def quadrant(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.select(
        [(x >= 1) & (y >= 1), (x >= 1) & (y < 1), (x < 1) & (y < 1), (x < 1) & (y >= 1)],
        ["Ab", "aB", "bA", "Ba"],
        default="ridge",
    )


def parent_window(xs: np.ndarray, xf: np.ndarray, history: bool) -> dict:
    z = np.mod(np.arctan2(xf - 1, xs - 1) / (2 * np.pi), 1)
    resolutions = np.array([8, 16, 32, 64, 128], dtype=float)
    occupied = [np.unique(np.floor(z * int(r)).astype(int) % int(r)).size for r in resolutions]
    xp = float(np.clip(2 * np.polyfit(np.log(resolutions), np.log(np.maximum(occupied, 1)), 1)[0], 0, 2))
    half = len(z) // 2
    source, target = z[: half - 1], z[1:half]
    test_source, test_target = z[half:-1], z[half + 1 :]
    train_xy = np.column_stack([np.cos(2 * np.pi * source), np.sin(2 * np.pi * source)])
    test_xy = np.column_stack([np.cos(2 * np.pi * test_source), np.sin(2 * np.pi * test_source)])
    neighbour = cKDTree(train_xy).query(test_xy, k=9)[1]
    target_complex = np.exp(2j * np.pi * target)
    prediction = np.mod(np.angle(np.mean(target_complex[neighbour], axis=1)) / (2 * np.pi), 1)
    loss = float(np.mean(circular_distance(prediction, test_target)))
    null = np.mod(np.angle(np.mean(target_complex)) / (2 * np.pi), 1)
    null_loss = float(np.mean(circular_distance(null, test_target)))
    out = {
        "x_P": xp,
        "x_R": float(np.clip(2 * loss / max(null_loss, 1e-12), 0, 2)),
        "successor_loss": loss,
        "successor_null_loss": null_loss,
        "radius_mean": float(np.mean(np.hypot(xs - 1, xf - 1))),
    }
    if history:
        coherence = []
        for lag in range(1, 65):
            delta = np.mod(z[lag:] - z[:-lag], 1)
            coherence.append(abs(np.mean(np.exp(2j * np.pi * delta))))
        out.update(
            history_coherence_mean=float(np.mean(coherence)),
            history_coherence_peak=float(np.max(coherence)),
            history_peak_lag=int(np.argmax(coherence) + 1),
        )
    return out


def parent_series(xs: np.ndarray, xf: np.ndarray, position: np.ndarray, history: bool) -> pd.DataFrame:
    rows = []
    for end in range(255, len(xs), 16):
        row = parent_window(xs[end - 255 : end + 1], xf[end - 255 : end + 1], history)
        row.update(end_index=end, end_position=float(position[end]))
        rows.append(row)
    result = pd.DataFrame(rows)
    result["quadrant"] = quadrant(result["x_P"].to_numpy(), result["x_R"].to_numpy())
    result["parent_step"] = np.hypot(result["x_P"].diff(), result["x_R"].diff()).fillna(0)
    return result


def strongest(parent: pd.DataFrame) -> tuple[float, float]:
    row = parent.loc[parent["parent_step"].idxmax()]
    return float(row["end_position"]), float(row["parent_step"])


def replication() -> tuple[pd.DataFrame, pd.DataFrame]:
    source = pd.read_csv(EVENT_SOURCE)
    scales = pd.read_csv(EVENT_SCALES).set_index("medium")
    event_rows, parent_rows = [], []
    for (medium, event), group in source.groupby(["medium", "event"], sort=True):
        group = group.sort_values("relative_row")
        rel = group["relative_row"].to_numpy(int)
        stress = group["stress_mpa"].to_numpy(float)
        q05 = float(scales.loc[medium, "smoothed_stress_q05_mpa"])
        q95 = float(scales.loc[medium, "smoothed_stress_q95_mpa"])
        smooth, delta, accumulation, release, activity, xs, xf = tension_coordinates(stress, 31, 101, q05, q95)
        q = quadrant(xs, xf)
        counts = {name: int(np.sum(q == name)) for name in ["Ab", "aB", "bA", "Ba"]}
        qualifying = sum(value >= 0.005 * len(rel) for value in counts.values())
        pre = float(np.median(xs[(rel >= -512) & (rel <= -32)]))
        post = float(np.median(xs[(rel >= 32) & (rel <= 512)]))
        near_release = float(np.max(xf[np.abs(rel) <= 100]))
        reconnect_candidates = rel[(rel >= 0) & (rel <= 512) & (xf < 1)]
        reconnect = int(reconnect_candidates[0]) if len(reconnect_candidates) else None
        child_pass = qualifying >= 3 and pre - post >= 0.25 and near_release >= 1.5 and reconnect is not None

        parent = parent_series(xs, xf, rel, history=False)
        parent_counts = parent["quadrant"].value_counts().to_dict()
        parent_qualifying = sum(value >= 3 for value in parent_counts.values())
        handover, handover_step = strongest(parent)
        parent_pass = parent_qualifying >= 2 and abs(handover) <= 128
        event_rows.append(
            {
                "medium": medium,
                "event": int(event),
                "quadrants_qualifying": qualifying,
                **{f"child_{name}_bins": counts[name] for name in counts},
                "pre_storage": pre,
                "post_storage": post,
                "storage_drop": pre - post,
                "near_drop_max_x_F": near_release,
                "reconnect_relative_row": reconnect,
                "child_tension_pass": bool(child_pass),
                "parent_quadrants_qualifying": parent_qualifying,
                "parent_handover_relative_row": handover,
                "parent_handover_step": handover_step,
                "parent_pass": bool(parent_pass),
            }
        )
        for row in parent.itertuples(index=False):
            parent_rows.append({"medium": medium, "event": int(event), **row._asdict()})
    return pd.DataFrame(event_rows), pd.DataFrame(parent_rows)


def main() -> None:
    qa = []
    for name, expected in EXPECTED_MD5.items():
        actual = digest(HERE / name, "md5")
        qa.append({"item": name, "algorithm": "MD5", "expected": expected, "actual": actual, "passed": actual == expected})
    for name, expected in EXPECTED_SHA256.items():
        actual = digest(HERE / name, "sha256")
        qa.append({"item": name, "algorithm": "SHA256", "expected": expected, "actual": actual, "passed": actual == expected})
    qa_frame = pd.DataFrame(qa)
    source_pass = bool(qa_frame["passed"].all())

    raw = np.load(NPZ)
    time = raw["time"]
    stress = raw["stress_mean"]
    displacement = raw["disp_mean"]
    n = len(time)
    split = int(0.8 * n)
    calibration_smooth = trailing_mean(stress, 10)[:split]
    q05, q95 = np.quantile(calibration_smooth, [0.05, 0.95])
    smooth, delta, accumulation, release, activity, xs, xf = tension_coordinates(stress, 10, 50, q05, q95)
    displacement_delta = np.diff(displacement, append=displacement[-1])
    main_index = int(np.argmax(displacement_delta))
    main_time = float(time[main_index + 1])
    release_index = int(np.argmax(release))
    release_time = float(time[release_index])
    release_error = abs(release_time - main_time)
    exclude = np.abs(time - main_time) > 0.1
    raw_r = float(np.corrcoef(xs[exclude], xf[exclude])[0, 1])
    q = quadrant(xs, xf)
    q_counts = {name: int(np.sum(q == name)) for name in ["Ab", "aB", "bA", "Ba"]}
    q_qualifying = sum(value >= 0.005 * n for value in q_counts.values())
    relative = time - main_time
    pre_storage = float(np.median(xs[(relative >= -0.10) & (relative <= -0.02)]))
    post_storage = float(np.median(xs[(relative >= 0.02) & (relative <= 0.10)]))
    near_release = float(np.max(xf[np.abs(relative) <= 0.1]))
    reconnect_candidates = np.flatnonzero((relative >= 0) & (relative <= 0.3) & (xf < 1))
    reconnect_index = int(reconnect_candidates[0]) if len(reconnect_candidates) else None
    reconnect_time = float(relative[reconnect_index]) if reconnect_index is not None else None

    parent = parent_series(xs, xf, time, history=True)
    parent_counts = parent["quadrant"].value_counts().to_dict()
    parent_qualifying = sum(value >= 3 for value in parent_counts.values())
    handover_time, handover_step = strongest(parent)
    handover_error = abs(handover_time - main_time)
    release_parent_index = int(np.argmin(np.abs(parent["end_position"] - release_time)))
    release_parent_step = float(parent.iloc[release_parent_index]["parent_step"])
    release_parent_percentile = float(np.mean(parent["parent_step"] <= release_parent_step))

    controls = []
    rng = np.random.default_rng(363)
    for number in range(100):
        order = rng.permutation(n)
        p = parent_series(xs[order], xf[order], time, history=False)
        event_time, event_step = strongest(p)
        controls.append({"control": f"time_shuffle_{number:03d}", "marker_time": main_time, "handover_time": event_time, "timing_error_s": abs(event_time - main_time), "parent_step": event_step})
    for name, control_xs, control_xf in [
        ("reversal", xs[::-1], xf[::-1]),
        ("storage_only", xs, np.ones_like(xf)),
        ("signless_transfer", xs, np.ones_like(xf)),
    ]:
        p = parent_series(control_xs, control_xf, time, history=False)
        event_time, event_step = strongest(p)
        controls.append({"control": name, "marker_time": main_time, "handover_time": event_time, "timing_error_s": abs(event_time - main_time), "parent_step": event_step})
    for fraction in [0.25, 0.50, 0.75]:
        marker_index = (main_index + int(fraction * n)) % n
        marker_time = float(time[marker_index])
        controls.append({"control": f"wrong_marker_{fraction:.2f}", "marker_time": marker_time, "handover_time": handover_time, "timing_error_s": abs(handover_time - marker_time), "parent_step": handover_step})
    control_frame = pd.DataFrame(controls)

    events, event_parents = replication()
    child_all = int(events["child_tension_pass"].sum())
    child_dry = int(events.query("medium == 'dry'")["child_tension_pass"].sum())
    child_fluid = int(events.query("medium == 'fluid'")["child_tension_pass"].sum())
    parent_all = int(events["parent_pass"].sum())
    parent_dry = int(events.query("medium == 'dry'")["parent_pass"].sum())
    parent_fluid = int(events.query("medium == 'fluid'")["parent_pass"].sum())

    shuffle_median = float(control_frame[control_frame["control"].str.startswith("time_shuffle")]["timing_error_s"].median())
    required_controls = ["reversal", "storage_only", "signless_transfer", "wrong_marker_0.25", "wrong_marker_0.50", "wrong_marker_0.75"]
    control_errors = {name: float(control_frame.loc[control_frame["control"] == name, "timing_error_s"].iloc[0]) for name in required_controls}

    gates = [
        {"gate": "G1 source and identity QA", "passed": bool(source_pass and abs(raw_r) < 0.98 and release_error <= 0.10), "observed": f"source={source_pass}; |r|={abs(raw_r):.4f}; release/slip error={release_error:.4f} s"},
        {"gate": "G2 dense child tension handover", "passed": bool(q_qualifying >= 3 and pre_storage - post_storage >= 0.25 and near_release >= 1.5 and reconnect_time is not None and reconnect_time <= 0.30), "observed": f"quadrants={q_qualifying}/4; storage drop={pre_storage-post_storage:.3f}; max x_F={near_release:.3f}; reconnect={reconnect_time}"},
        {"gate": "G3 dense Irrationality parent", "passed": bool(parent_qualifying >= 2 and handover_error <= 0.512 and release_parent_percentile >= 0.99), "observed": f"quadrants={parent_qualifying}/4; handover error={handover_error:.4f} s; release-step percentile={release_parent_percentile:.4f}"},
        {"gate": "G4 chronology and marker specificity", "passed": bool(handover_error + 1e-9 < shuffle_median and all(handover_error + 1e-9 < value for value in control_errors.values())), "observed": f"real={handover_error:.4f} s; shuffle median={shuffle_median:.4f} s; " + "; ".join(f"{k}={v:.4f}" for k, v in control_errors.items())},
        {"gate": "G5 repeated child tension handover", "passed": bool(child_all >= 12 and child_dry >= 8 and child_fluid >= 4), "observed": f"all={child_all}/15; dry={child_dry}/10; fluid={child_fluid}/5"},
        {"gate": "G6 repeated Irrationality parent", "passed": bool(parent_all >= 12 and parent_dry >= 8 and parent_fluid >= 4), "observed": f"all={parent_all}/15; dry={parent_dry}/10; fluid={parent_fluid}/5"},
    ]
    overall = bool(all(row["passed"] for row in gates))

    dense = pd.DataFrame({
        "time_s": time, "time_to_slip_s": relative, "stress_mpa": stress, "smoothed_stress_mpa": smooth,
        "displacement_micrometre": displacement, "displacement_increment": displacement_delta,
        "stress_change_mpa": delta, "accumulation_A": accumulation, "release_R": release,
        "transfer_activity": activity, "x_S": xs, "x_F": xf, "quadrant": q,
    })
    dense.to_csv(HERE / f"{PREFIX}TIMESERIES.csv", index=False)
    parent.to_csv(HERE / f"{PREFIX}PARENT_WINDOWS.csv", index=False)
    control_frame.to_csv(HERE / f"{PREFIX}CONTROLS.csv", index=False)
    events.to_csv(HERE / f"{PREFIX}REPLICATION_EVENTS.csv", index=False)
    event_parents.to_csv(HERE / f"{PREFIX}REPLICATION_PARENT_WINDOWS.csv", index=False)
    pd.DataFrame(gates).to_csv(HERE / f"{PREFIX}FROZEN_GATES.csv", index=False)
    qa_frame.to_csv(HERE / f"{PREFIX}SOURCE_QA.csv", index=False)

    result = {
        "test": "T363 fault-tension Irrationality Di-ARA",
        "run_date": "2026-08-12",
        "verdict": "SUPPORTED ON THIS PHYSICAL ARCHIVE" if overall else "NOT SUPPORTED ON THIS PHYSICAL ARCHIVE",
        "all_gates_passed": overall,
        "main_slip_time_s": main_time,
        "tension_release_time_s": release_time,
        "release_slip_error_s": release_error,
        "parent_handover_time_s": handover_time,
        "parent_handover_error_s": handover_error,
        "raw_axis_correlation": raw_r,
        "physical_quadrant_occupancy": q_counts,
        "parent_quadrant_occupancy": parent_counts,
        "pre_storage": pre_storage, "post_storage": post_storage,
        "near_slip_max_x_F": near_release, "reconnect_time_after_slip_s": reconnect_time,
        "release_parent_step_percentile": release_parent_percentile,
        "replication": {"child": {"all": child_all, "dry": child_dry, "fluid": child_fluid}, "parent": {"all": parent_all, "dry": parent_dry, "fluid": parent_fluid}},
        "gates": gates, "frozen_hashes": EXPECTED_SHA256,
    }
    (HERE / f"{PREFIX}RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_figure(dense, parent, control_frame, events, gates, main_time, release_time, handover_time)
    print(json.dumps(result, indent=2))


def make_figure(dense, parent, controls, events, gates, main_time, release_time, handover_time):
    fig, axes = plt.subplots(3, 2, figsize=(18, 15), constrained_layout=True)
    fig.suptitle("T363 — fault-tension Irrationality Di-ARA", fontsize=20, fontweight="bold")
    focus = dense[(dense["time_to_slip_s"] >= -1.5) & (dense["time_to_slip_s"] <= 0.32)]
    ax = axes[0, 0]
    ax.plot(focus["time_to_slip_s"], focus["x_S"], label="x_S stored tension", color="#2f6ea5")
    ax.plot(focus["time_to_slip_s"], focus["x_F"], label="x_F release share", color="#e0902d")
    ax.axhline(1, color="#777", lw=1)
    ax.axvline(0, color="#bf3f3f", label="displacement-marked slip")
    ax.axvline(release_time-main_time, color="#d19b28", ls="--", label="tension release")
    ax.axvline(handover_time-main_time, color="#6d4bb3", ls=":", label="parent handover")
    ax.set(xlabel="time to main slip (s)", ylabel="ARA coordinate", ylim=(0, 2.05), title="Stored tension and signed transfer through slip")
    ax.legend(frameon=False, ncol=2)
    ax2 = ax.twinx()
    ax2.plot(focus["time_to_slip_s"], focus["transfer_activity"], color="#8b8b8b", alpha=.35)
    ax2.set_ylabel("transfer activity (MPa, 0.1 s window)", color="#777")

    ax = axes[0, 1]
    sample = dense.iloc[::max(1, len(dense)//6000)]
    sc = ax.scatter(sample["x_S"], sample["x_F"], c=sample["time_to_slip_s"], cmap="viridis", s=7, alpha=.65)
    ax.axhline(1, color="#777"); ax.axvline(1, color="#777")
    ax.set(xlim=(0,2), ylim=(0,2), xlabel="x_S — low ↔ high stored tension", ylabel="x_F — accumulation ↔ release", title="Physical tension Di-ARA path")
    ax.set_aspect("equal")
    for x,y,t in [(1.8,1.85,"Ab"),(1.8,.12,"aB"),(.12,.12,"bA"),(.12,1.85,"Ba")]: ax.text(x,y,t,ha="center",fontweight="bold")
    fig.colorbar(sc, ax=ax, label="time to main slip (s)")

    ax = axes[1, 0]
    sc = ax.scatter(parent["x_P"], parent["x_R"], c=parent["end_position"]-main_time, cmap="plasma", s=25)
    ax.plot(parent["x_P"], parent["x_R"], color="#888", lw=.5, alpha=.5)
    ax.axhline(1,color="#777"); ax.axvline(1,color="#777")
    ax.set(xlim=(0,2),ylim=(0,2),xlabel="x_P — reused ↔ open",ylabel="x_R — determined ↔ residual",title="Higher Irrationality parent")
    ax.set_aspect("equal"); fig.colorbar(sc,ax=ax,label="window end to slip (s)")

    ax = axes[1, 1]
    named = controls[~controls["control"].str.startswith("time_shuffle")].copy()
    summary = pd.concat([pd.DataFrame([{"control":"real chronology","timing_error_s":abs(handover_time-main_time)}]), named[["control","timing_error_s"]]])
    summary = summary.sort_values("timing_error_s")
    ax.barh(summary["control"], summary["timing_error_s"], color=["#2f6ea5" if x=="real chronology" else "#aab3bd" for x in summary["control"]])
    ax.set(xlabel="absolute handover-to-marker error (s)", title="Chronology, coordinate and marker controls")

    ax = axes[2, 0]
    y = np.arange(len(events))
    child = events["child_tension_pass"].astype(int).to_numpy()
    parent_pass = events["parent_pass"].astype(int).to_numpy()
    matrix = np.column_stack([child,parent_pass])
    ax.imshow(matrix,aspect="auto",cmap=plt.matplotlib.colors.ListedColormap(["#f3c9c9","#cfe9d3"]),vmin=0,vmax=1)
    ax.set_xticks([0,1],["child tension ARA","Irrationality parent"])
    ax.set_yticks(y,[f"{m} {e}" for m,e in zip(events["medium"],events["event"])])
    ax.set_title("15-event replication")
    for i in range(len(events)):
        for j in range(2): ax.text(j,i,"PASS" if matrix[i,j] else "FAIL",ha="center",va="center",fontsize=8,fontweight="bold")

    ax=axes[2,1]; ax.axis("off")
    rows=[[g["gate"].split()[0],"PASS" if g["passed"] else "FAIL",g["observed"]] for g in gates]
    table=ax.table(cellText=rows,colLabels=["Gate","Result","Observed"],colWidths=[.1,.13,.77],cellLoc="left",loc="center")
    table.auto_set_font_size(False); table.set_fontsize(8.2); table.scale(1,2.1)
    for i,g in enumerate(gates,1): table[(i,1)].set_facecolor("#cfe9d3" if g["passed"] else "#f3c9c9")
    ax.set_title("Frozen gates")
    fig.savefig(HERE / f"{PREFIX}FIGURE.png",dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
