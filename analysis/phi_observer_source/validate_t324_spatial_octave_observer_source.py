from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_deps"))

import h5py
import numpy as np


DATA = HERE / "data" / "qu_kemar_anechoic_radius_0.5_1_2_3_m.sofa"
PROTOCOL = HERE / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "results" / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_RESULTS.json"
PATHS = HERE / "results" / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_PATHS.csv"
RATIOS = HERE / "results" / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_RATIOS.csv"
FREQUENCIES = HERE / "results" / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_FREQUENCIES.csv"
FIGURE = HERE / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE.png"
OUTPUT = HERE / "results" / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_VALIDATION.json"

SOURCE_HASH = "4d11740336d936ad129473029fadce5320f7455f0475634fed4d5519b2878a42"
PHI = (1 + math.sqrt(5)) / 2
RADII = (0.5, 1.0, 2.0, 3.0)
TARGETS = {
    "direct": 0.0,
    "thirty": 30.0,
    "phi": 36.0,
    "ordinary_octave": 45.0,
    "phi_reversed": 54.0,
    "ridge_half": 60.0,
    "perpendicular": 90.0,
}
NON_OCTAVE = {
    "ordinary_non_octave": math.degrees(math.atan(0.5)),
    "phi": 36.0,
    "ordinary_octave": 45.0,
    "phi_reversed": 54.0,
}
FREQ_MIN = 500.0
FREQ_MAX = 8000.0
MAG_FLOOR = 0.01
PHASE_FLOOR = 0.05
MIN_BINS = 8
TOL = 1e-9


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def close(a: float, b: float, tol: float = TOL) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol


def read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def reconstruct() -> dict:
    with h5py.File(DATA, "r") as f:
        flat_ir = np.asarray(f["Data.IR"], dtype=float)
        source = np.asarray(f["SourcePosition"], dtype=float)
        fs = float(np.asarray(f["Data.SamplingRate"]).reshape(-1)[0])
        data_delay = np.asarray(f["Data.Delay"], dtype=float)
        latency_present = "MeasurementAudioLatency" in f
    keys = sorted({(round(float(a), 6), round(float(e), 6)) for a, e in source[:, :2]})
    lookup = {
        (round(float(a), 6), round(float(e), 6), round(float(r), 6)): idx
        for idx, (a, e, r) in enumerate(source)
    }
    ir = np.asarray(
        [
            [flat_ir[lookup[(az, el, radius)]] for radius in RADII]
            for az, el in keys
        ],
        dtype=float,
    )
    h = np.fft.rfft(ir, axis=-1)
    mag = np.abs(h)
    phase = np.unwrap(np.angle(h), axis=-1)
    freqs = np.fft.rfftfreq(ir.shape[-1], 1 / fs)
    band = np.flatnonzero((freqs >= FREQ_MIN) & (freqs <= FREQ_MAX))
    max_mag = np.max(mag[..., 1:], axis=-1)
    return {
        "flat_ir": flat_ir,
        "source": source,
        "ir": ir,
        "mag": mag,
        "phase": phase,
        "freqs": freqs,
        "band": band,
        "max_mag": max_mag,
        "keys": keys,
        "fs": fs,
        "data_delay": data_delay,
        "latency_present": latency_present,
    }


def independent_angle(data: dict, lower: int, upper: int, targets: dict[str, float]) -> dict:
    phase = data["phase"]
    mag = data["mag"]
    band = data["band"]
    max_mag = data["max_mag"]
    rows = []
    events = []
    for d in range(phase.shape[0]):
        for ear in range(phase.shape[2]):
            p0 = phase[d, lower, ear]
            p1 = phase[d, upper, ear]
            valid = (
                (mag[d, lower, ear, band] >= MAG_FLOOR * max_mag[d, lower, ear])
                & (mag[d, upper, ear, band] >= MAG_FLOOR * max_mag[d, upper, ear])
            )
            ks = band[valid]
            parallel = p0[ks]
            change = p1[ks] - p0[ks]
            stable = (np.abs(parallel) >= PHASE_FLOOR) & (np.abs(change) >= PHASE_FLOOR)
            theta = np.degrees(
                np.arctan2(np.abs(change[stable]), np.abs(parallel[stable]))
            )
            if len(theta) < MIN_BINS:
                continue
            row = {
                "direction": d,
                "ear": ear,
                "free": float(np.mean(theta)),
                "median": float(np.median(theta)),
            }
            for name, target in targets.items():
                row[name] = float(np.sqrt(np.mean((theta - target) ** 2)))
            rows.append(row)
            events.append(theta)
    all_events = np.concatenate(events)
    loss = {name: float(np.median([row[name] for row in rows])) for name in targets}
    return {
        "paths": len(rows),
        "events": len(all_events),
        "median_event": float(np.median(all_events)),
        "median_free": float(np.median([row["free"] for row in rows])),
        "losses": loss,
        "closest": min(loss, key=loss.get),
        "within_5deg_phi_fraction": float(np.mean(np.abs(all_events - 36.0) <= 5.0)),
        "within_5deg_zero_fraction": float(np.mean(all_events <= 5.0)),
    }


def independent_ratios(data: dict) -> dict:
    phase = data["phase"]
    mag = data["mag"]
    band = data["band"]
    max_mag = data["max_mag"]
    rho_paths = []
    eta_paths = []
    rho_events = []
    eta_events = []
    for d in range(phase.shape[0]):
        for ear in range(phase.shape[2]):
            p = phase[d, :, ear]
            valid_mag = np.ones(len(band), dtype=bool)
            for radius in range(4):
                valid_mag &= mag[d, radius, ear, band] >= MAG_FLOOR * max_mag[d, radius, ear]
            a = p[1, band] - p[0, band]
            b = p[2, band] - p[1, band]
            c = p[3, band] - p[2, band]
            rho_ok = valid_mag & (np.abs(a) >= PHASE_FLOOR) & (np.abs(b) >= PHASE_FLOOR)
            eta_ok = valid_mag & (np.abs(b) >= PHASE_FLOOR) & (np.abs(c) >= PHASE_FLOOR)
            rho = np.abs(b[rho_ok]) / np.abs(a[rho_ok])
            eta = np.abs(c[eta_ok]) / np.abs(b[eta_ok])
            if len(rho) < MIN_BINS or len(eta) < MIN_BINS:
                continue
            rho_paths.append(float(np.median(rho)))
            eta_paths.append(float(np.median(eta)))
            rho_events.append(rho)
            eta_events.append(eta)
    rho = np.concatenate(rho_events)
    eta = np.concatenate(eta_events)
    return {
        "paths": len(rho_paths),
        "rho_events": len(rho),
        "eta_events": len(eta),
        "median_event_rho": float(np.median(rho)),
        "median_path_rho": float(np.median(rho_paths)),
        "median_event_eta": float(np.median(eta)),
        "median_path_eta": float(np.median(eta_paths)),
        "rho_within_10pct_phi_fraction": float(np.mean(np.abs(rho / PHI - 1.0) <= 0.1)),
        "rho_within_10pct_two_fraction": float(np.mean(np.abs(rho / 2.0 - 1.0) <= 0.1)),
        "rho_below_phi_fraction": float(np.mean(rho < PHI)),
    }


def main() -> None:
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    paths_csv = read_csv(PATHS)
    ratios_csv = read_csv(RATIOS)
    frequencies_csv = read_csv(FREQUENCIES)
    data = reconstruct()
    angle = {
        "0.5_to_1": independent_angle(data, 0, 1, TARGETS),
        "1_to_2": independent_angle(data, 1, 2, TARGETS),
        "2_to_3": independent_angle(data, 2, 3, NON_OCTAVE),
    }
    ratios = independent_ratios(data)

    checks: list[dict] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("source hash", hash_file(DATA) == SOURCE_HASH, hash_file(DATA))
    check("protocol hash", hash_file(PROTOCOL) == saved["protocol_sha256"], hash_file(PROTOCOL))
    check("flat shape", list(data["flat_ir"].shape) == [1440, 2, 2048], list(data["flat_ir"].shape))
    check("matched shape", list(data["ir"].shape) == [360, 4, 2, 2048], list(data["ir"].shape))
    check("360 directions", len(data["keys"]) == 360, len(data["keys"]))
    check("four radii", sorted(np.unique(data["source"][:, 2]).tolist()) == list(RADII), np.unique(data["source"][:, 2]).tolist())
    check("sampling rate", close(data["fs"], 44100.0), data["fs"])
    check("Data.Delay zero", bool(np.all(data["data_delay"] == 0.0)), data["data_delay"].tolist())
    check("latency absent", not data["latency_present"], data["latency_present"])
    check("path CSV rows", len(paths_csv) == 2160, len(paths_csv))
    check("ratio CSV rows", len(ratios_csv) == 1440, len(ratios_csv))
    check("frequency CSV nonempty", len(frequencies_csv) > 1000, len(frequencies_csv))
    check("figure exists", FIGURE.exists() and FIGURE.stat().st_size > 50000, FIGURE.stat().st_size if FIGURE.exists() else 0)

    for label, independent in angle.items():
        stored = saved["angle_summaries"][label]
        check(f"{label} paths", independent["paths"] == stored["paths"], [independent["paths"], stored["paths"]])
        check(f"{label} events", independent["events"] == stored["events"], [independent["events"], stored["events"]])
        check(f"{label} median event", close(independent["median_event"], stored["median_event_angle_deg"]), [independent["median_event"], stored["median_event_angle_deg"]])
        check(f"{label} median free", close(independent["median_free"], stored["median_free_path_angle_deg"]), [independent["median_free"], stored["median_free_path_angle_deg"]])
        check(f"{label} closest target", independent["closest"] == stored["closest_loss_target"], [independent["closest"], stored["closest_loss_target"]])
        for target, value in independent["losses"].items():
            check(f"{label} loss {target}", close(value, stored["median_target_losses"][target]), [value, stored["median_target_losses"][target]])

    stored_ratio = saved["ratio_summary"]
    for key in ("paths", "rho_events", "eta_events"):
        check(f"ratio {key}", ratios[key] == stored_ratio[key], [ratios[key], stored_ratio[key]])
    for key in ("median_event_rho", "median_path_rho", "median_event_eta", "median_path_eta"):
        check(f"ratio {key}", close(ratios[key], stored_ratio[key]), [ratios[key], stored_ratio[key]])

    null = saved["analytic_free_field_null"]
    check("analytic 0.5->1 angle 45", close(null["angles_deg"]["0.5_to_1"], 45.0), null["angles_deg"]["0.5_to_1"])
    check("analytic 1->2 angle 45", close(null["angles_deg"]["1_to_2"], 45.0), null["angles_deg"]["1_to_2"])
    check("analytic 2->3 angle atan half", close(null["angles_deg"]["2_to_3"], math.degrees(math.atan(0.5))), null["angles_deg"]["2_to_3"])
    check("analytic rho 2", close(null["median_rho"], 2.0), null["median_rho"])
    check("analytic eta 1", close(null["median_eta"], 1.0), null["median_eta"])
    check("frozen verdict 2/5", saved["verdict"]["passed"] == 2 and saved["verdict"]["verdict"] == "NOT SUPPORTED", saved["verdict"])

    diagnostics = {
        "angle_proximity": {
            label: {
                "within_5deg_phi_fraction": values["within_5deg_phi_fraction"],
                "within_5deg_zero_fraction": values["within_5deg_zero_fraction"],
            }
            for label, values in angle.items()
        },
        "ratio_proximity": {
            key: ratios[key]
            for key in (
                "rho_within_10pct_phi_fraction",
                "rho_within_10pct_two_fraction",
                "rho_below_phi_fraction",
            )
        },
        "interpretive_warning": (
            "G2 and G4 can pass by relative ranking even when the observed value is far "
            "from every registered nonzero target. They are formal frozen-gate passes, "
            "not evidence of absolute Phi proximity."
        ),
    }
    passed = sum(item["passed"] for item in checks)
    result = {
        "validation": "PASS" if passed == len(checks) else "FAIL",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "diagnostics": diagnostics,
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "validation": result["validation"],
        "passed": passed,
        "total": len(checks),
        "diagnostics": diagnostics,
    }, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

