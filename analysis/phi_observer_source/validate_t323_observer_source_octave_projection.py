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


TARGETS = {
    "direct": 0.0,
    "thirty": 30.0,
    "phi": 36.0,
    "pure_delay": 45.0,
    "phi_complement": 54.0,
    "ridge_half": 60.0,
    "perpendicular": 90.0,
}
FILES = {
    "NH2": HERE / "data" / "ARI_NH2_hrtf_M_dtf_256.sofa",
    "NH4": HERE / "data" / "ARI_NH4_hrtf_M_dtf_256.sofa",
}
RESULT_JSON = HERE / "results" / "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_RESULTS.json"
PATH_CSV = HERE / "results" / "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_PATHS.csv"
OUT = HERE / "results" / "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_VALIDATION.json"


def stable_seed(*parts: object) -> int:
    raw = "|".join(map(str, parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "little")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(1 << 20)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def folded(parallel: np.ndarray, octave: np.ndarray) -> np.ndarray:
    return np.rad2deg(np.arctan2(np.abs(octave), np.abs(parallel)))


def rms(values: np.ndarray, target: float) -> float:
    return float(np.sqrt(np.mean(np.square(values - target))))


def calculate_dataset(label: str, path: Path):
    with h5py.File(path, "r") as f:
        ir = np.array(f["Data.IR"], dtype=np.float64)
        fs = float(np.array(f["Data.SamplingRate"])[0])
        pos = np.array(f["SourcePosition"], dtype=np.float64)
        latency = np.array(f["MeasurementAudioLatency"], dtype=np.float64)
    spec = np.fft.rfft(ir, axis=-1)
    magnitude = np.absolute(spec)
    phase = np.unwrap(np.angle(spec), axis=-1)
    peak = np.max(magnitude[:, :, 1:], axis=-1)
    ks_all = np.arange(2, phase.shape[-1] // 2 + 1)
    order = np.lexsort((pos[:, 2], pos[:, 1], pos[:, 0]))
    neighbor = np.empty(len(order), dtype=int)
    neighbor[order] = np.roll(order, -1)
    paths = []
    bin_values = {int(k): [] for k in ks_all}
    event_count = 0
    for m in range(ir.shape[0]):
        for ear in range(ir.shape[1]):
            p = phase[m, ear]
            valid = (
                (magnitude[m, ear, ks_all] >= 0.01 * peak[m, ear])
                & (magnitude[m, ear, 2 * ks_all] >= 0.01 * peak[m, ear])
                & (np.abs(p[ks_all]) >= 0.05)
            )
            ks = ks_all[valid]
            theta = folded(p[ks], p[2 * ks] - p[ks])
            event_count += len(theta)
            for k, value in zip(ks, theta):
                bin_values[int(k)].append(float(value))
            paths.append(
                {
                    "source_index": m,
                    "ear": ear,
                    "eligible_pairs": len(theta),
                    "free_angle_deg": float(np.mean(theta)),
                    "median_angle_deg": float(np.median(theta)),
                    "median_ara_x": float(np.median(2 * np.cos(np.deg2rad(theta)))),
                    **{f"loss_{name}": rms(theta, target) for name, target in TARGETS.items()},
                }
            )

    latency_phase = phase - latency[:, :, None] * (2 * np.pi * np.arange(phase.shape[-1]) / ir.shape[-1])[None, None, :]
    latency_rows = []
    for m in range(ir.shape[0]):
        for ear in range(ir.shape[1]):
            p = latency_phase[m, ear]
            valid = (
                (magnitude[m, ear, ks_all] >= 0.01 * peak[m, ear])
                & (magnitude[m, ear, 2 * ks_all] >= 0.01 * peak[m, ear])
                & (np.abs(p[ks_all]) >= 0.05)
            )
            ks = ks_all[valid]
            theta = folded(p[ks], p[2 * ks] - p[ks])
            latency_rows.append(
                {
                    "free": float(np.mean(theta)),
                    "ara": float(np.median(2 * np.cos(np.deg2rad(theta)))),
                    **{name: rms(theta, target) for name, target in TARGETS.items()},
                }
            )
    return {
        "phase": phase,
        "magnitude": magnitude,
        "peak": peak,
        "pos": pos,
        "neighbor": neighbor,
        "ks_all": ks_all,
        "paths": paths,
        "event_count": event_count,
        "bin_values": bin_values,
        "latency_rows": latency_rows,
        "sha256": digest(path),
    }


def main() -> None:
    recorded = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    with PATH_CSV.open("r", encoding="utf-8", newline="") as fh:
        csv_rows = list(csv.DictReader(fh))
    csv_lookup = {
        (row["dataset"], int(row["source_index"]), int(row["ear"])): row
        for row in csv_rows
    }
    checks = []
    errors = []

    def check(name: str, condition: bool, detail: str = ""):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            errors.append(name + (": " + detail if detail else ""))

    for label, path in FILES.items():
        calc = calculate_dataset(label, path)
        summary = recorded["primary_summaries"][label]
        check(label + " sha256", calc["sha256"] == recorded["metadata"][label]["sha256"])
        check(label + " path count", len(calc["paths"]) == summary["paths"])
        check(label + " event count", calc["event_count"] == summary["events"])
        free = float(np.median([row["free_angle_deg"] for row in calc["paths"]]))
        ara = float(np.median([row["median_ara_x"] for row in calc["paths"]]))
        check(label + " free angle", abs(free - summary["median_free_angle_deg"]) < 1e-10, f"{free}")
        check(label + " ARA x", abs(ara - summary["median_ara_x"]) < 1e-10, f"{ara}")
        for target in TARGETS:
            value = float(np.median([row[f"loss_{target}"] for row in calc["paths"]]))
            expected = summary["median_target_losses"][target]
            check(label + " loss " + target, abs(value - expected) < 1e-10, f"{value}")

        lat = calc["latency_rows"]
        ls = recorded["posthoc_latency_sensitivity"][label]
        lat_free = float(np.median([row["free"] for row in lat]))
        lat_ara = float(np.median([row["ara"] for row in lat]))
        check(label + " latency free", abs(lat_free - ls["median_free_angle_deg"]) < 1e-10, f"{lat_free}")
        check(label + " latency ARA", abs(lat_ara - ls["median_ara_x"]) < 1e-10, f"{lat_ara}")

        for m in [0, 17, 309, 777, 1549]:
            for ear in [0, 1]:
                row = calc["paths"][m * 2 + ear]
                saved = csv_lookup[(label, m, ear)]
                for field in ["free_angle_deg", "median_angle_deg", "median_ara_x", "loss_phi", "loss_pure_delay", "loss_phi_complement"]:
                    check(
                        f"{label} spot {m}/{ear} {field}",
                        abs(float(saved[field]) - float(row[field])) < 1e-10,
                    )

                # Independently reconstruct broken and scrambled controls for
                # the same audited path.
                p = calc["phase"][m, ear]
                q = calc["neighbor"][m]
                pn = calc["phase"][q, ear]
                ks_all = calc["ks_all"]
                valid = (
                    (calc["magnitude"][m, ear, ks_all] >= 0.01 * calc["peak"][m, ear])
                    & (calc["magnitude"][q, ear, 2 * ks_all] >= 0.01 * calc["peak"][q, ear])
                    & (np.abs(p[ks_all]) >= 0.05)
                )
                ks = ks_all[valid]
                broken = rms(folded(p[ks], pn[2 * ks] - p[ks]), 36.0)
                check(f"{label} broken spot {m}/{ear}", abs(float(saved["broken_phi_loss"]) - broken) < 1e-10)

                original_valid = (
                    (calc["magnitude"][m, ear, ks_all] >= 0.01 * calc["peak"][m, ear])
                    & (calc["magnitude"][m, ear, 2 * ks_all] >= 0.01 * calc["peak"][m, ear])
                    & (np.abs(p[ks_all]) >= 0.05)
                )
                oks = ks_all[original_valid]
                inc = np.diff(p)
                values = []
                for rep in range(64):
                    rng = np.random.default_rng(stable_seed("T323", label, m, ear, rep))
                    sp = np.r_[0.0, np.cumsum(rng.permutation(inc))]
                    values.append(rms(folded(sp[oks], sp[2 * oks] - sp[oks]), 36.0))
                scrambled = float(np.mean(values))
                check(f"{label} scrambled spot {m}/{ear}", abs(float(saved["scrambled_phi_loss"]) - scrambled) < 1e-10)

        wins = {name: 0 for name in TARGETS}
        for values in calc["bin_values"].values():
            if not values:
                continue
            med = float(np.median(values))
            winner = min(TARGETS, key=lambda name: abs(med - TARGETS[name]))
            wins[winner] += 1
        check(label + " bin wins", wins == summary["bin_target_wins"], str(wins))

    check("recorded verdict", recorded["verdict"] == "NOT SUPPORTED")
    check("recorded gates", all(value is False for value in recorded["gates"].values()))
    output = {
        "validator": "independent raw-SOFA recomputation and control spot checks",
        "checks": len(checks),
        "passed": sum(item["passed"] for item in checks),
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
        "details": checks,
    }
    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({k: output[k] for k in ["checks", "passed", "errors", "status"]}, indent=2))


if __name__ == "__main__":
    main()
