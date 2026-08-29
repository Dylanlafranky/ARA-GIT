from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import urllib.request

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MANIFEST = ROOT / "T431_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
LOCK = ROOT / "T431_FREEZE_LOCK.json"
PROTOCOL = ROOT / "T431_FROZEN_PROTOCOL.md"
CORE = ROOT / "t431_connection_transfer_ledger.py"
CACHE = pathlib.Path("F:/SystemFormulaFolder/_data_cache/GWOSC/T431")
AUDIT = RESULTS / "T431_SOURCE_AUDIT.json"
sys.path.insert(0, str(ROOT))
import t431_connection_transfer_ledger as t431  # noqa: E402


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_freeze() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    checks = {
        "protocol_sha256": sha256(PROTOCOL),
        "source_manifest_sha256": sha256(MANIFEST),
        "analysis_script_sha256_at_freeze": sha256(CORE),
    }
    for key, observed in checks.items():
        expected = str(lock[key]).lower()
        if observed.lower() != expected:
            raise RuntimeError(f"freeze mismatch for {key}: expected {expected}, observed {observed}")


def fetch_json(url: str) -> dict[str, object]:
    url = url.replace("format=api", "format=json")
    request = urllib.request.Request(url, headers={"User-Agent": "ARA-T431/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str, destination: pathlib.Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "ARA-T431/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response, destination.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def resolve_files(endpoint: str) -> dict[str, dict[str, object]]:
    selected: dict[str, dict[str, object]] = {}
    url: str | None = endpoint
    while url:
        page = fetch_json(url)
        for row in page.get("results", []):
            detector = str(row.get("detector", ""))
            sample_rate = int(row.get("sample_rate_kHz", -1))
            duration = int(row.get("duration", -1))
            file_format = str(row.get("file_format", "")).upper()
            if detector in {"H1", "L1"} and sample_rate == 4 and duration == 32 and file_format == "HDF":
                selected.setdefault(detector, row)
        url = page.get("next") if len(selected) < 2 else None
    if set(selected) != {"H1", "L1"}:
        raise RuntimeError(f"could not resolve H1/L1 4 kHz 32 s HDF files from {endpoint}")
    return selected


def download_sources() -> None:
    verify_freeze()
    RESULTS.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit_rows: list[dict[str, object]] = []
    for event in manifest["events"]:
        event_name = str(event["event"])
        event_dir = CACHE / event_name
        event_dir.mkdir(parents=True, exist_ok=True)
        event_json = fetch_json(str(event["event_url"]))
        event_json_path = event_dir / f"{event_name}_eventapi.json"
        event_json_path.write_text(json.dumps(event_json, indent=2), encoding="utf-8")
        resolved = resolve_files(str(event["strain_files_url"]))
        for detector in ("H1", "L1"):
            row = resolved[detector]
            url = str(row["download_url"])
            destination = event_dir / pathlib.PurePosixPath(url).name
            download_file(url, destination)
            audit_rows.append({
                "event": event_name,
                "uid": event["uid"],
                "role": event["role"],
                "gps": float(event["gps"]),
                "detector": detector,
                "event_url": event["event_url"],
                "strain_files_url": event["strain_files_url"],
                "url": url,
                "local_path": destination.as_posix(),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
                "event_json_path": event_json_path.as_posix(),
                "event_json_sha256": sha256(event_json_path),
                "gps_matches_api": abs(float(event_json["gps"]) - float(event["gps"])) <= 0.11,
            })
    AUDIT.write_text(json.dumps(audit_rows, indent=2), encoding="utf-8")
    print(json.dumps({"downloaded_files": len(audit_rows), "audit_sha256": sha256(AUDIT)}, indent=2))


def load_confirmation_sources() -> tuple[list[dict[str, object]], dict[str, dict[str, pathlib.Path]]]:
    rows = json.loads(AUDIT.read_text(encoding="utf-8"))
    events: dict[str, dict[str, object]] = {}
    files: dict[str, dict[str, pathlib.Path]] = {}
    for row in rows:
        event = str(row["event"])
        events.setdefault(event, {"event": event, "gps": float(row["gps"]), "role": "untouched_confirmation"})
        files.setdefault(event, {})[str(row["detector"])] = pathlib.Path(str(row["local_path"]))
    return [events[name] for name in sorted(events)], files


def score_confirmation() -> None:
    verify_freeze()
    if not AUDIT.exists():
        raise FileNotFoundError("run --stage download first")
    events, files = load_confirmation_sources()
    views = {str(event["event"]): t431.build_network(event, files[str(event["event"])]) for event in events}
    event_rows: list[dict[str, object]] = []
    control_rows: list[dict[str, object]] = []
    histories: list[pd.DataFrame] = []
    for event, view in sorted(views.items()):
        metrics, history = t431.ledger_score(view, 0.0)
        controls: list[dict[str, object]] = []
        for control_id, centre in enumerate(t431.offsource_centres()):
            row, _ = t431.ledger_score(view, centre)
            row.update({"event": event, "role": "matched_offsource", "control_id": control_id})
            controls.append(row)
            control_rows.append(row)
        null_strength = np.asarray([float(row["ledger_strength"]) for row in controls])
        null_coherence = np.asarray([float(row["median_phase_coherence_ARA"]) for row in controls])
        strength = float(metrics["ledger_strength"])
        coherence = float(metrics["median_phase_coherence_ARA"])
        metrics.update({
            "event": event,
            "role": "untouched_confirmation",
            "offsource_n": len(controls),
            "ledger_empirical_p": float((1 + np.sum(null_strength >= strength)) / (len(null_strength) + 1)),
            "ledger_offsource_percentile": float(np.mean(null_strength < strength)),
            "phase_coherence_offsource_percentile": float(np.mean(null_coherence < coherence)),
            "unresolved_mobile_excess": float(metrics["H_unresolved_mobile"]) - float(metrics["H_unresolved_old_new_mean"]),
        })
        event_rows.append(metrics)
        history.insert(0, "event", event)
        histories.append(history)

    event_df = pd.DataFrame(event_rows)
    control_df = pd.DataFrame(control_rows)
    history_df = pd.concat(histories, ignore_index=True)
    event_df.to_csv(RESULTS / "T431_CONFIRMATION_EVENTS.csv", index=False)
    control_df.to_csv(RESULTS / "T431_CONFIRMATION_CONTROLS.csv", index=False)
    history_df.to_csv(RESULTS / "T431_CONFIRMATION_HISTORIES.csv", index=False)
    gates = {
        "gate_1_network_shape_3_of_4": int(event_df["network_shape_pass"].sum()) >= 3,
        "gate_2_source_specific_3_of_4": int((event_df["ledger_empirical_p"] <= 0.05).sum()) >= 3,
        "gate_3_detector_replication_2_of_4": int(event_df["detector_replication_pass"].sum()) >= 2,
        "gate_4_unresolved_mobile_3_of_4": int((event_df["unresolved_mobile_excess"] > 0).sum()) >= 3,
        "gate_5_phase_coherence_3_of_4": int((event_df["phase_coherence_offsource_percentile"] >= 0.90).sum()) >= 3,
    }
    summary = {
        "verdict": "SUPPORTED" if all(gates.values()) else "NOT SUPPORTED",
        "n_events": len(event_df),
        "counts": {
            "network_shape": int(event_df["network_shape_pass"].sum()),
            "source_specific_p_le_0_05": int((event_df["ledger_empirical_p"] <= 0.05).sum()),
            "detector_replication": int(event_df["detector_replication_pass"].sum()),
            "unresolved_mobile": int((event_df["unresolved_mobile_excess"] > 0).sum()),
            "phase_coherence_ge_p90": int((event_df["phase_coherence_offsource_percentile"] >= 0.90).sum()),
        },
        "gates": gates,
        "protocol_sha256": sha256(PROTOCOL),
        "manifest_sha256": sha256(MANIFEST),
        "core_sha256": sha256(CORE),
        "source_audit_sha256": sha256(AUDIT),
    }
    (RESULTS / "T431_CONFIRMATION_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    make_figures(event_df, control_df, history_df)
    print(json.dumps(summary, indent=2))


def make_figures(events: pd.DataFrame, controls: pd.DataFrame, histories: pd.DataFrame) -> None:
    plt.style.use("dark_background")
    colours = {"C": "#ff9f1c", "M": "#4ea1ff", "H": "#b889ff"}
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=True, sharey=True)
    for ax, event in zip(axes.flat, events["event"]):
        h = histories[histories["event"] == event]
        row = events[events["event"] == event].iloc[0]
        ax.plot(h["time_s"], h["connection_C"], color=colours["C"], lw=2.0, label="connection C")
        ax.plot(h["time_s"], h["movement_M"], color=colours["M"], lw=2.0, label="movement M")
        ax.plot(h["time_s"], h["unresolved_H"], color=colours["H"], lw=1.5, label="unresolved H")
        for key, colour, label in (("pre_time_s", colours["C"], "old"), ("mobile_time_s", colours["M"], "mobile"), ("post_time_s", colours["C"], "new")):
            ax.axvline(float(row[key]), color=colour, ls="--", alpha=0.7)
        ax.axhline(1.0, color="white", ls=":", alpha=0.55)
        ax.set_title(f"{event} · p={float(row['ledger_empirical_p']):.3f} · off-source pct={100*float(row['ledger_offsource_percentile']):.1f}%")
        ax.set_ylim(0, 2)
        ax.grid(alpha=0.18)
    axes[0, 0].legend(ncol=3, fontsize=9)
    for ax in axes[-1, :]:
        ax.set_xlabel("seconds relative to published event GPS")
    for ax in axes[:, 0]:
        ax.set_ylabel("independent ARA coordinate (0–2)")
    fig.suptitle("T431 confirmation: connection → mobile/unresolved → reclosure histories", fontsize=17, weight="bold")
    fig.tight_layout()
    fig.savefig(RESULTS / "T431_CONFIRMATION_HISTORIES.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13, 11), sharex=True, sharey=True)
    for ax, event in zip(axes.flat, events["event"]):
        h = histories[histories["event"] == event]
        colour = h["time_s"].to_numpy()
        points = ax.scatter(h["connection_C"], h["movement_M"], c=colour, cmap="viridis", s=22, alpha=0.85)
        ax.plot(h["connection_C"], h["movement_M"], color="#86a9c9", alpha=0.25, lw=0.8)
        row = events[events["event"] == event].iloc[0]
        ax.scatter([row["C_old"], row["C_mobile"], row["C_new"]], [row["M_old"], row["M_mobile"], row["M_new"]],
                   s=[100, 125, 100], c=[colours["C"], colours["M"], colours["C"]], edgecolor="white", linewidth=1.0)
        ax.axvline(1, color="white", ls=":", alpha=0.5)
        ax.axhline(1, color="white", ls=":", alpha=0.5)
        ax.set_title(str(event))
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.grid(alpha=0.18)
    for ax in axes[-1, :]:
        ax.set_xlabel("connection C (0–2)")
    for ax in axes[:, 0]:
        ax.set_ylabel("movement M (0–2)")
    fig.colorbar(points, ax=axes.ravel().tolist(), label="seconds relative to event GPS", shrink=0.82)
    fig.suptitle("T431 time-facing ARA paths; orange/blue/orange are frozen ledger landmarks", fontsize=16, weight="bold")
    fig.savefig(RESULTS / "T431_CONFIRMATION_ARA_PLANES.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(13, 6.5))
    positions = np.arange(len(events))
    for i, event in enumerate(events["event"]):
        null = controls[controls["event"] == event]["ledger_strength"].astype(float)
        ax.violinplot(null, positions=[i], widths=0.72, showextrema=False)
    ax.scatter(positions, events["ledger_strength"].astype(float), color="#ffcc33", s=90, edgecolor="white", zorder=3, label="event")
    ax.set_xticks(positions, events["event"], rotation=15)
    ax.set_ylabel("connection-transfer ledger strength")
    ax.set_title("Event ledger strength against identically searched matched off-source windows")
    ax.grid(axis="y", alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "T431_CONFIRMATION_EVENT_VS_CONTROLS.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("download", "confirm"), required=True)
    args = parser.parse_args()
    if args.stage == "download":
        download_sources()
    else:
        score_confirmation()


if __name__ == "__main__":
    main()
