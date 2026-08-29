from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys
import urllib.request

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(pathlib.Path(__file__).resolve().parent / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from scipy import ndimage, stats


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MANIFEST = ROOT / "T432_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
PROTOCOL = ROOT / "T432_FROZEN_PROTOCOL.md"
LOCK = ROOT / "T432_FREEZE_LOCK.json"
CACHE = pathlib.Path("F:/SystemFormulaFolder/_data_cache/GWOSC/T432")
AUDIT = RESULTS / "T432_SOURCE_AUDIT.json"

T431_ROOT = ROOT.parent / "T431_connection_transfer_ledger"
sys.path.insert(0, str(T431_ROOT))
import t431_connection_transfer_ledger as t431  # noqa: E402


ANALYSIS_INTERVAL = (-0.50, 0.75)
ACTIVE_INTERVAL = (-0.15, 0.15)
LATE_INTERVAL = (0.35, 0.75)
MAX_LAG_FRAMES = 16
CONTROL_CENTRES = np.concatenate([
    np.arange(-10.75, -4.74, 0.25),
    np.arange(4.50, 11.26, 0.25),
])
EPS = 1e-12
SEED = 43220260826

DEVELOPMENT_EVENTS = (
    ("GW150914", 1126259462.4, "T427"),
    ("GW170104", 1167559936.6, "T427"),
    ("GW170608", 1180922494.5, "T427"),
    ("GW170809", 1186302519.8, "T427"),
    ("GW170814", 1186741861.5, "T427"),
    ("GW170818", 1187058327.1, "T427"),
    ("GW151012", 1128678900.4, "T430"),
    ("GW151226", 1135136350.6, "T430"),
    ("GW170729", 1185389807.3, "T430"),
    ("GW170823", 1187529256.5, "T430"),
    ("GW190412", 1239082262.2, "T431"),
    ("GW190521_074359", 1242459857.5, "T431"),
    ("GW190727_060333", 1248242632.0, "T431"),
    ("GW190828_063405", 1251009263.8, "T431"),
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def interval_mask(times: np.ndarray, interval: tuple[float, float], centre: float = 0.0) -> np.ndarray:
    relative = np.asarray(times, dtype=float) - centre
    return (relative >= interval[0]) & (relative <= interval[1])


def finite_spearman(a: np.ndarray, b: np.ndarray) -> float:
    valid = np.isfinite(a) & np.isfinite(b)
    if np.sum(valid) < 12 or np.nanstd(a[valid]) < EPS or np.nanstd(b[valid]) < EPS:
        return float("nan")
    return float(stats.spearmanr(a[valid], b[valid]).statistic)


def lag_pair(a: np.ndarray, b: np.ndarray, lag: int) -> tuple[np.ndarray, np.ndarray]:
    if lag > 0:
        return a[:-lag], b[lag:]
    if lag < 0:
        return a[-lag:], b[:lag]
    return a, b


def percentile_high(value: float, controls: np.ndarray) -> float:
    controls = np.asarray(controls, dtype=float)
    controls = controls[np.isfinite(controls)]
    if not np.isfinite(value) or len(controls) == 0:
        return float("nan")
    return float((np.sum(controls < value) + 0.5 * np.sum(controls == value)) / len(controls))


def percentile_low(value: float, controls: np.ndarray) -> float:
    controls = np.asarray(controls, dtype=float)
    controls = controls[np.isfinite(controls)]
    if not np.isfinite(value) or len(controls) == 0:
        return float("nan")
    return float((np.sum(controls > value) + 0.5 * np.sum(controls == value)) / len(controls))


def network_coordinates(view: dict[str, object]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    matrix = np.asarray(view["matrix"], dtype=float)
    coherence = np.asarray(view["phase_coherence"], dtype=float)
    connection = ndimage.median_filter(
        np.nanmean(np.column_stack([matrix[:, 0], matrix[:, 1], coherence]), axis=1),
        size=t431.SMOOTH_FRAMES,
        mode="nearest",
    )
    movement = ndimage.median_filter(matrix[:, 2], size=t431.SMOOTH_FRAMES, mode="nearest")
    unresolved = np.maximum(0.0, 2.0 - connection - movement)
    return connection, movement, unresolved


def detector_coordinates(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    matrix = np.asarray(matrix, dtype=float)
    connection = ndimage.median_filter(
        np.nanmean(matrix[:, :2], axis=1), size=t431.SMOOTH_FRAMES, mode="nearest"
    )
    movement = ndimage.median_filter(matrix[:, 2], size=t431.SMOOTH_FRAMES, mode="nearest")
    unresolved = np.maximum(0.0, 2.0 - connection - movement)
    return connection, movement, unresolved


def score_coordinates(
    times: np.ndarray,
    connection: np.ndarray,
    movement: np.ndarray,
    unresolved: np.ndarray,
    centre: float,
) -> tuple[dict[str, float], pd.DataFrame]:
    mask = interval_mask(times, ANALYSIS_INTERVAL, centre)
    rel = np.asarray(times[mask], dtype=float) - centre
    c = np.asarray(connection[mask], dtype=float)
    m = np.asarray(movement[mask], dtype=float)
    h = np.asarray(unresolved[mask], dtype=float)
    valid = np.isfinite(rel) & np.isfinite(c) & np.isfinite(m) & np.isfinite(h)
    rel, c, m, h = rel[valid], c[valid], m[valid], h[valid]
    if len(rel) < 100:
        raise ValueError(f"insufficient frames around centre {centre}: {len(rel)}")

    dt = float(np.nanmedian(np.diff(rel)))
    dc = ndimage.median_filter(np.gradient(c, dt), size=3, mode="nearest")
    dm = ndimage.median_filter(np.gradient(m, dt), size=3, mode="nearest")

    best = {"score": -np.inf, "lag": 0, "rho": np.nan, "occupancy": np.nan, "gain": np.nan}
    for lag in range(-MAX_LAG_FRAMES, MAX_LAG_FRAMES + 1):
        a, b = lag_pair(dc, dm, lag)
        rho = finite_spearman(a, b)
        if not np.isfinite(rho):
            continue
        opposed = np.isfinite(a) & np.isfinite(b) & (a * b < 0)
        occupancy = float(np.mean(opposed))
        score = max(0.0, -rho) * occupancy
        if np.sum(opposed) >= 8:
            gain = float(np.nanmedian(np.abs(b[opposed]) / (np.abs(a[opposed]) + EPS)))
        else:
            gain = float("nan")
        if score > best["score"]:
            best = {"score": score, "lag": lag, "rho": rho, "occupancy": occupancy, "gain": gain}

    speed = np.sqrt(dc**2 + dm**2)
    active = (rel >= ACTIVE_INTERVAL[0]) & (rel <= ACTIVE_INTERVAL[1])
    late = (rel >= LATE_INTERVAL[0]) & (rel <= LATE_INTERVAL[1])
    active_speed = float(np.nanmedian(speed[active]))
    late_speed = float(np.nanmedian(speed[late]))
    speed_settlement = float((active_speed - late_speed) / (active_speed + late_speed + EPS))

    late_centre = np.array([float(np.nanmedian(m[late])), float(np.nanmedian(c[late]))])
    radius = np.sqrt((m - late_centre[0]) ** 2 + (c - late_centre[1]) ** 2)
    active_radius = float(np.nanmedian(radius[active]))
    late_radius = float(np.nanmedian(radius[late]))
    radius_settlement = float((active_radius - late_radius) / (active_radius + late_radius + EPS))

    x = m - float(np.nanmedian(m))
    y = c - float(np.nanmedian(c))
    signed_area = float(0.5 * np.nansum(x[:-1] * y[1:] - x[1:] * y[:-1]))
    top_left = (m <= 0.5) & (c >= 1.5)
    distance = np.sqrt(m**2 + (2.0 - c) ** 2)
    h_active = float(np.nanmedian(h[active]))
    h_late = float(np.nanmedian(h[late]))

    metrics = {
        "pushpull_score": float(best["score"]),
        "opposition_rho": float(best["rho"]),
        "opposition_occupancy": float(best["occupancy"]),
        "best_lag_ms": float(best["lag"] * t431.t427.HOP_SECONDS * 1000.0),
        "transfer_gain": float(best["gain"]),
        "signed_loop_area": signed_area,
        "loop_orientation": float(np.sign(signed_area)),
        "active_speed": active_speed,
        "late_speed": late_speed,
        "speed_settlement": speed_settlement,
        "active_radius": active_radius,
        "late_radius": late_radius,
        "radius_settlement": radius_settlement,
        "top_left_occupancy": float(np.mean(top_left)),
        "top_left_distance_q10": float(np.nanquantile(distance, 0.10)),
        "h_active": h_active,
        "h_late": h_late,
        "h_change": h_late - h_active,
        "median_connection": float(np.nanmedian(c)),
        "median_movement": float(np.nanmedian(m)),
        "n_frames": int(len(rel)),
    }
    history = pd.DataFrame({
        "time_s": rel,
        "connection_C": c,
        "movement_M": m,
        "unresolved_H": h,
        "dC_dt": dc,
        "dM_dt": dm,
        "trajectory_speed": speed,
        "radius_to_late_centroid": radius,
        "top_left_zone": top_left,
    })
    return metrics, history


def matched_controls(view: dict[str, object], coordinate_kind: str = "network") -> list[dict[str, float]]:
    times = np.asarray(view["times"], dtype=float)
    if coordinate_kind == "network":
        c, m, h = network_coordinates(view)
    elif coordinate_kind == "H1":
        c, m, h = detector_coordinates(np.asarray(view["h_matrix"], dtype=float))
    elif coordinate_kind == "L1":
        c, m, h = detector_coordinates(np.asarray(view["l_matrix"], dtype=float))
    else:
        raise ValueError(coordinate_kind)
    return [score_coordinates(times, c, m, h, float(centre))[0] for centre in CONTROL_CENTRES]


def score_event(event: str, view: dict[str, object], role: str) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    times = np.asarray(view["times"], dtype=float)
    c, m, h = network_coordinates(view)
    metrics, history = score_coordinates(times, c, m, h, 0.0)
    controls = matched_controls(view, "network")
    control_frame = pd.DataFrame(controls)

    metrics.update({
        "event": event,
        "role": role,
        "offsource_n": len(control_frame),
        "pushpull_percentile": percentile_high(metrics["pushpull_score"], control_frame["pushpull_score"].to_numpy()),
        "speed_settlement_percentile": percentile_high(metrics["speed_settlement"], control_frame["speed_settlement"].to_numpy()),
        "radius_settlement_percentile": percentile_high(metrics["radius_settlement"], control_frame["radius_settlement"].to_numpy()),
        "corner_avoidance_percentile": percentile_low(metrics["top_left_occupancy"], control_frame["top_left_occupancy"].to_numpy()),
        "loop_area_percentile": percentile_high(abs(metrics["signed_loop_area"]), np.abs(control_frame["signed_loop_area"].to_numpy())),
    })

    for detector in ("H1", "L1"):
        matrix = np.asarray(view["h_matrix" if detector == "H1" else "l_matrix"], dtype=float)
        dc, dm, dh = detector_coordinates(matrix)
        detector_metric, _ = score_coordinates(times, dc, dm, dh, 0.0)
        detector_controls = pd.DataFrame(matched_controls(view, detector))
        metrics[f"{detector}_pushpull_score"] = detector_metric["pushpull_score"]
        metrics[f"{detector}_pushpull_percentile"] = percentile_high(
            detector_metric["pushpull_score"], detector_controls["pushpull_score"].to_numpy()
        )

    metrics["detector_replication"] = bool(
        metrics["H1_pushpull_percentile"] >= 0.90 and metrics["L1_pushpull_percentile"] >= 0.90
    )
    metrics["dynamic_p95"] = bool(metrics["pushpull_percentile"] >= 0.95)
    metrics["settlement_joint_p90"] = bool(
        metrics["speed_settlement_percentile"] >= 0.90
        and metrics["radius_settlement_percentile"] >= 0.90
    )
    metrics["corner_avoidance_p90"] = bool(metrics["corner_avoidance_percentile"] >= 0.90)

    history.insert(0, "event", event)
    history.insert(1, "role", role)
    control_frame.insert(0, "event", event)
    control_frame.insert(1, "role", "matched_offsource")
    control_frame.insert(2, "control_id", np.arange(len(control_frame)))
    return metrics, history, control_frame


def source_files_from_directory(directory: pathlib.Path) -> dict[str, pathlib.Path]:
    selected: dict[str, pathlib.Path] = {}
    for detector in ("H1", "L1"):
        matches = sorted(directory.glob(f"{detector[0]}-{detector}_*-32.hdf5"))
        if not matches:
            matches = sorted(directory.glob(f"{detector[0]}-{detector}_*.hdf5"))
        if not matches:
            raise FileNotFoundError(f"no {detector} HDF file in {directory}")
        selected[detector] = matches[0]
    return selected


def load_development_sources() -> tuple[list[dict[str, object]], dict[str, dict[str, pathlib.Path]]]:
    base = pathlib.Path("F:/SystemFormulaFolder/_data_cache/GWOSC")
    events: list[dict[str, object]] = []
    files: dict[str, dict[str, pathlib.Path]] = {}
    for event, gps, source in DEVELOPMENT_EVENTS:
        events.append({"event": event, "gps": gps, "role": "opened_development"})
        files[event] = source_files_from_directory(base / source / event)
    return events, files


def verify_freeze() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    checks = {
        "protocol_sha256": sha256(PROTOCOL),
        "source_manifest_sha256": sha256(MANIFEST),
        "analysis_script_sha256_at_freeze": sha256(pathlib.Path(__file__)),
    }
    for key, observed in checks.items():
        expected = str(lock[key]).lower()
        if observed.lower() != expected:
            raise RuntimeError(f"freeze mismatch for {key}: expected {expected}, observed {observed}")


def fetch_json(url: str) -> dict[str, object]:
    request = urllib.request.Request(
        url.replace("format=api", "format=json"),
        headers={"User-Agent": "ARA-T432/1.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_files(endpoint: str) -> dict[str, dict[str, object]]:
    selected: dict[str, dict[str, object]] = {}
    url: str | None = endpoint
    while url:
        page = fetch_json(url)
        for row in page.get("results", []):
            detector = str(row.get("detector", ""))
            if (
                detector in {"H1", "L1"}
                and int(row.get("sample_rate_kHz", -1)) == 4
                and int(row.get("duration", -1)) == 32
                and str(row.get("file_format", "")).upper() == "HDF"
            ):
                selected.setdefault(detector, row)
        url = page.get("next") if len(selected) < 2 else None
    if set(selected) != {"H1", "L1"}:
        raise RuntimeError(f"could not resolve H1/L1 4 kHz 32 s HDF files from {endpoint}")
    return selected


def download_file(url: str, destination: pathlib.Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "ARA-T432/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response, destination.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def download_confirmation() -> None:
    verify_freeze()
    RESULTS.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit: list[dict[str, object]] = []
    for event in manifest["confirmation_events"]:
        name = str(event["event"])
        event_json = fetch_json(str(event["event_url"]))
        gps = float(event_json["gps"])
        event_dir = CACHE / name
        event_dir.mkdir(parents=True, exist_ok=True)
        event_json_path = event_dir / f"{name}_eventapi.json"
        event_json_path.write_text(json.dumps(event_json, indent=2), encoding="utf-8")
        resolved = resolve_files(str(event["strain_files_url"]))
        for detector in ("H1", "L1"):
            row = resolved[detector]
            url = str(row["download_url"])
            destination = event_dir / pathlib.PurePosixPath(url).name
            download_file(url, destination)
            audit.append({
                "event": name,
                "uid": event["uid"],
                "role": event["role"],
                "gps": gps,
                "detector": detector,
                "event_url": event["event_url"],
                "strain_files_url": event["strain_files_url"],
                "download_url": url,
                "local_path": destination.as_posix(),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
                "event_json_path": event_json_path.as_posix(),
                "event_json_sha256": sha256(event_json_path),
            })
    AUDIT.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps({"files": len(audit), "audit_sha256": sha256(AUDIT)}, indent=2))


def load_confirmation_sources() -> tuple[list[dict[str, object]], dict[str, dict[str, pathlib.Path]]]:
    rows = json.loads(AUDIT.read_text(encoding="utf-8"))
    events: dict[str, dict[str, object]] = {}
    files: dict[str, dict[str, pathlib.Path]] = {}
    for row in rows:
        name = str(row["event"])
        events.setdefault(name, {"event": name, "gps": float(row["gps"]), "role": "untouched_confirmation"})
        files.setdefault(name, {})[str(row["detector"])] = pathlib.Path(str(row["local_path"]))
    return [events[name] for name in sorted(events)], files


def analyse(phase: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    if phase == "development":
        events, files = load_development_sources()
    elif phase == "confirmation":
        verify_freeze()
        events, files = load_confirmation_sources()
    else:
        raise ValueError(phase)

    event_rows: list[dict[str, object]] = []
    histories: list[pd.DataFrame] = []
    controls: list[pd.DataFrame] = []
    qa_rows: list[dict[str, object]] = []
    for index, event in enumerate(events, start=1):
        name = str(event["event"])
        print(f"[{phase}] {index}/{len(events)} {name}", flush=True)
        view = t431.build_network(event, files[name])
        metrics, history, control = score_event(name, view, str(event["role"]))
        metrics.update({
            "gps": float(event["gps"]),
            "lag_alignment_ms": float(view["lag_ms"]),
            "lag_alignment_corr": float(view["lag_corr"]),
        })
        event_rows.append(metrics)
        histories.append(history)
        controls.append(control)
        for detector, qa in view["qa"].items():
            qa_rows.append({"event": name, "detector": detector, **qa})

    event_frame = pd.DataFrame(event_rows).sort_values("event").reset_index(drop=True)
    history_frame = pd.concat(histories, ignore_index=True)
    control_frame = pd.concat(controls, ignore_index=True)
    qa_frame = pd.DataFrame(qa_rows)

    gates = {
        "phase": phase,
        "n_events": len(event_frame),
        "dynamic_p95_count": int(event_frame["dynamic_p95"].sum()),
        "settlement_joint_p90_count": int(event_frame["settlement_joint_p90"].sum()),
        "detector_replication_count": int(event_frame["detector_replication"].sum()),
        "corner_avoidance_p90_count": int(event_frame["corner_avoidance_p90"].sum()),
        "G1_dynamic_4_of_6": bool(len(event_frame) == 6 and int(event_frame["dynamic_p95"].sum()) >= 4),
        "G2_settlement_4_of_6": bool(len(event_frame) == 6 and int(event_frame["settlement_joint_p90"].sum()) >= 4),
        "G3_detector_3_of_6": bool(len(event_frame) == 6 and int(event_frame["detector_replication"].sum()) >= 3),
        "G4_corner_4_of_6": bool(len(event_frame) == 6 and int(event_frame["corner_avoidance_p90"].sum()) >= 4),
    }
    gates["dynamic_handover_supported"] = bool(gates["G1_dynamic_4_of_6"] and gates["G2_settlement_4_of_6"])

    prefix = f"T432_{phase.upper()}"
    event_frame.to_csv(RESULTS / f"{prefix}_EVENTS.csv", index=False)
    history_frame.to_csv(RESULTS / f"{prefix}_HISTORIES.csv", index=False)
    control_frame.to_csv(RESULTS / f"{prefix}_OFFSOURCE_CONTROLS.csv", index=False)
    qa_frame.to_csv(RESULTS / f"{prefix}_SOURCE_QA.csv", index=False)
    (RESULTS / f"{prefix}_GATES.json").write_text(json.dumps(gates, indent=2), encoding="utf-8")
    return event_frame, history_frame, control_frame, gates


def style() -> None:
    plt.style.use("dark_background")
    plt.rcParams.update({
        "figure.facecolor": "#0b1220",
        "axes.facecolor": "#111827",
        "axes.edgecolor": "#94a3b8",
        "axes.labelcolor": "#e5e7eb",
        "text.color": "#e5e7eb",
        "xtick.color": "#cbd5e1",
        "ytick.color": "#cbd5e1",
        "grid.color": "#334155",
        "font.size": 10,
    })


def plot_trajectory_gallery(phase: str, events: pd.DataFrame, histories: pd.DataFrame) -> pathlib.Path:
    style()
    names = events["event"].tolist()
    cols = 3
    rows = int(np.ceil(len(names) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(16, 5.2 * rows), squeeze=False)
    norm = Normalize(vmin=ANALYSIS_INTERVAL[0], vmax=ANALYSIS_INTERVAL[1])
    for ax, name in zip(axes.flat, names):
        part = histories.loc[histories.event == name].sort_values("time_s")
        ax.fill_between([0, 0.5], 1.5, 2.0, color="#f59e0b", alpha=0.12, label="nominal top-left pure zone")
        ax.plot(part.movement_M, part.connection_C, color="#64748b", lw=0.8, alpha=0.65)
        scatter = ax.scatter(
            part.movement_M, part.connection_C, c=part.time_s, cmap="viridis", norm=norm,
            s=17, alpha=0.85, linewidths=0,
        )
        nearest_zero = part.iloc[(part.time_s.abs()).argmin()]
        ax.scatter([nearest_zero.movement_M], [nearest_zero.connection_C], marker="*", s=130,
                   color="#f8fafc", edgecolor="#0f172a", zorder=5, label="published event GPS")
        row = events.loc[events.event == name].iloc[0]
        ax.set_title(
            f"{name}\npush/pull pct {100*row.pushpull_percentile:.1f}% · "
            f"settle {100*row.speed_settlement_percentile:.1f}/{100*row.radius_settlement_percentile:.1f}%"
        )
        ax.axvline(1.0, color="#cbd5e1", ls="--", lw=0.8, alpha=0.5)
        ax.axhline(1.0, color="#cbd5e1", ls="--", lw=0.8, alpha=0.5)
        ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.grid(alpha=0.25)
        ax.set_xlabel("Movement-facing child M (0–2)")
        ax.set_ylabel("Connection-facing child C (0–2)")
    for ax in axes.flat[len(names):]:
        ax.axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False)
    cbar = fig.colorbar(scatter, ax=axes.ravel().tolist(), fraction=0.025, pad=0.02)
    cbar.set_label("Seconds relative to published event GPS")
    fig.suptitle(f"T432 {phase}: fixed M-by-C ARA trajectories", fontsize=19, fontweight="bold", y=0.995)
    fig.subplots_adjust(top=0.92, bottom=0.08, wspace=0.23, hspace=0.32)
    path = RESULTS / f"T432_{phase.upper()}_TRAJECTORY_GALLERY.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_percentiles(phase: str, events: pd.DataFrame) -> pathlib.Path:
    style()
    names = events.event.tolist()
    y = np.arange(len(names))
    metrics = [
        ("pushpull_percentile", "lagged push/pull", "#60a5fa"),
        ("speed_settlement_percentile", "speed settlement", "#f59e0b"),
        ("radius_settlement_percentile", "radius settlement", "#34d399"),
        ("corner_avoidance_percentile", "top-left avoidance", "#c084fc"),
    ]
    fig, ax = plt.subplots(figsize=(13, max(6, 0.52 * len(names) + 2)))
    offsets = np.linspace(-0.24, 0.24, len(metrics))
    for offset, (field, label, color) in zip(offsets, metrics):
        ax.scatter(100 * events[field], y + offset, s=55, label=label, color=color)
    ax.axvline(95, color="#ef4444", ls="--", lw=1.2, label="primary 95th-percentile gate")
    ax.axvline(90, color="#f8fafc", ls=":", lw=1.1, label="secondary 90th-percentile gate")
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.set_xlim(0, 100); ax.set_xlabel("Within-file percentile versus matched off-source windows")
    ax.set_title(f"T432 {phase}: source specificity of each ARA component", fontsize=16, fontweight="bold")
    ax.grid(axis="x", alpha=0.3); ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.19), frameon=False)
    fig.tight_layout()
    path = RESULTS / f"T432_{phase.upper()}_PERCENTILES.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_strongest_history(phase: str, events: pd.DataFrame, histories: pd.DataFrame) -> pathlib.Path:
    style()
    row = events.sort_values("pushpull_percentile", ascending=False).iloc[0]
    name = str(row.event)
    part = histories.loc[histories.event == name].sort_values("time_s")
    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    axes[0].plot(part.time_s, part.connection_C, color="#f59e0b", label="connection C")
    axes[0].plot(part.time_s, part.movement_M, color="#60a5fa", label="movement M")
    axes[0].plot(part.time_s, part.unresolved_H, color="#c084fc", label="unresolved H", alpha=0.85)
    axes[0].axhline(1, color="#f8fafc", ls=":", alpha=0.6); axes[0].set_ylabel("ARA coordinate (0–2)")
    axes[0].legend(ncol=3, frameon=False)
    axes[1].plot(part.time_s, part.dC_dt, color="#f59e0b", label="dC/dt")
    axes[1].plot(part.time_s, part.dM_dt, color="#60a5fa", label="dM/dt")
    axes[1].axhline(0, color="#f8fafc", ls=":", alpha=0.6); axes[1].set_ylabel("Coordinate change per second")
    axes[1].legend(ncol=2, frameon=False)
    axes[2].plot(part.time_s, part.trajectory_speed, color="#34d399", label="trajectory speed")
    axes[2].plot(part.time_s, part.radius_to_late_centroid, color="#f472b6", label="distance to late centroid")
    axes[2].set_ylabel("Derived magnitude"); axes[2].set_xlabel("Seconds relative to published event GPS")
    axes[2].legend(ncol=2, frameon=False)
    for ax in axes:
        ax.axvline(0, color="#f8fafc", ls="--", lw=1)
        ax.axvspan(ACTIVE_INTERVAL[0], ACTIVE_INTERVAL[1], color="#ef4444", alpha=0.08, label="active interval")
        ax.axvspan(LATE_INTERVAL[0], LATE_INTERVAL[1], color="#22c55e", alpha=0.08, label="late interval")
        ax.grid(alpha=0.25)
    fig.suptitle(
        f"T432 {phase}: strongest source-specific push/pull history — {name}\n"
        f"best lag {row.best_lag_ms:.0f} ms · opposition rho {row.opposition_rho:.3f} · "
        f"push/pull percentile {100*row.pushpull_percentile:.1f}%",
        fontsize=16, fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = RESULTS / f"T432_{phase.upper()}_STRONGEST_HISTORY.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def make_figures(phase: str, events: pd.DataFrame, histories: pd.DataFrame) -> list[pathlib.Path]:
    return [
        plot_trajectory_gallery(phase, events, histories),
        plot_percentiles(phase, events),
        plot_strongest_history(phase, events, histories),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "download", "confirmation", "all"), required=True)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)

    if args.stage in {"development", "all"}:
        events, histories, _, gates = analyse("development")
        figures = make_figures("development", events, histories)
        print(json.dumps({"development_gates": gates, "figures": [str(p) for p in figures]}, indent=2))
    if args.stage in {"download", "all"}:
        download_confirmation()
    if args.stage in {"confirmation", "all"}:
        events, histories, _, gates = analyse("confirmation")
        figures = make_figures("confirmation", events, histories)
        print(json.dumps({"confirmation_gates": gates, "figures": [str(p) for p in figures]}, indent=2))


if __name__ == "__main__":
    main()
