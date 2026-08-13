"""Independent validation for T356."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

from pendulum_common import load_triple, load_triple_driven, rest_centered


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_PROTOCOL_v1_FROZEN.md"
EVENTS = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_EVENTS.csv"
RESULTS = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_RESULTS.json"
OUT = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_VALIDATION.json"
EXPECTED_SHA = "CEA75E318D0FBFA28F0869F2BBDFFF7FAFEAC369698C3A058F4B6598709D8289"


def med(x):
    a = np.asarray(x, float)
    a = a[np.isfinite(a)]
    return float(np.median(a))


def pct(x, p):
    a = np.asarray(x, float)
    a = a[np.isfinite(a)]
    return float(np.quantile(a, p))


def close(a, b, tol=1e-12):
    return bool(abs(float(a) - float(b)) <= tol)


def independent_raw_rows():
    rows = []
    prominence = 0.02 * math.pi
    for regime, run in [("free", "run1"), ("free", "run2"), ("free", "run3"), ("driven", "triple1")]:
        t, raw, vel, fs = load_triple_driven(run, 10) if regime == "driven" else load_triple(run, 10)
        centred = rest_centered(raw)
        distance = int(round(0.4 * 1.333 * fs))
        for arm in (1, 2, 3):
            x = centred[arm]
            speed = np.abs(np.asarray(vel[arm], float))
            hi = find_peaks(x, prominence=prominence, distance=distance)[0]
            lo = find_peaks(-x, prominence=prominence, distance=distance)[0]
            turns = sorted([(int(i), 1) for i in hi] + [(int(i), -1) for i in lo])
            local = []
            for j in range(len(turns) - 1):
                (left, lk), (right, rk) = turns[j], turns[j + 1]
                if lk == rk or right - left < 6:
                    continue
                interior = speed[left + 1:right]
                if len(interior) < 5 or not np.all(np.isfinite(interior)):
                    continue
                target = left + 1 + int(np.argmax(interior))
                duration = right - left
                pred = 0.5 * (left + right)
                pred_speed = float(np.interp(pred, np.arange(len(speed)), speed))
                local.append({
                    "regime": regime,
                    "run": run,
                    "arm": arm,
                    "direction": "increasing" if x[right] > x[left] else "decreasing",
                    "left": left,
                    "right": right,
                    "target": target,
                    "error_plain": abs(pred-target)/duration,
                    "error_left": abs(left-target)/duration,
                    "error_right": abs(right-target)/duration,
                    "flow_fraction": pred_speed/speed[target],
                    "error_wrong": float("nan"),
                })
            for i in range(len(local)-1):
                wrong = 0.5*(local[i]["left"]+local[i+1]["right"])
                local[i]["error_wrong"] = abs(wrong-local[i]["target"])/(local[i]["right"]-local[i]["left"])
            rows.extend(local)
    return rows


def main():
    published = json.loads(RESULTS.read_text(encoding="utf-8"))
    raw = independent_raw_rows()
    free = [r for r in raw if r["regime"] == "free"]
    driven = [r for r in raw if r["regime"] == "driven"]
    stored = list(csv.DictReader(EVENTS.open(encoding="utf-8")))
    digest = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest().upper()

    checks = {}
    checks["protocol_hash"] = digest == EXPECTED_SHA == published["protocol_sha256"]
    checks["raw_event_count"] = len(raw) == len(stored)
    checks["free_event_count"] = len(free) == published["free"]["n"]
    checks["driven_event_count"] = len(driven) == published["driven_transfer"]["n"]

    for key in ("error_plain", "error_left", "error_right", "error_wrong", "flow_fraction"):
        checks[f"free_{key}"] = close(med([r[key] for r in free]), published["free"][f"median_{key}"])
        checks[f"driven_{key}"] = close(med([r[key] for r in driven]), published["driven_transfer"][f"median_{key}"])
    checks["free_p95"] = close(pct([r["error_plain"] for r in free], .95), published["free"]["p95_error_plain"])
    checks["driven_p95"] = close(pct([r["error_plain"] for r in driven], .95), published["driven_transfer"]["p95_error_plain"])

    for direction in ("increasing", "decreasing"):
        z = [r for r in free if r["direction"] == direction]
        checks[f"direction_{direction}_n"] = len(z) == published["directions"][direction]["n"]
        checks[f"direction_{direction}_error"] = close(med([r["error_plain"] for r in z]), published["directions"][direction]["median_error_plain"])
        checks[f"direction_{direction}_flow"] = close(med([r["flow_fraction"] for r in z]), published["directions"][direction]["median_flow_fraction"])

    group_map = {(g["run"], int(g["arm"])): g for g in published["free_groups"]}
    for run in ("run1", "run2", "run3"):
        for arm in (1, 2, 3):
            z = [r for r in free if r["run"] == run and r["arm"] == arm]
            g = group_map[(run, arm)]
            checks[f"group_{run}_a{arm}_n"] = len(z) == g["n"]
            checks[f"group_{run}_a{arm}_error"] = close(med([r["error_plain"] for r in z]), g["median_error_plain"])

    gates = {
        "G1_absolute_location": med([r["error_plain"] for r in free]) < .10,
        "G2_tail": pct([r["error_plain"] for r in free], .95) < .25,
        "G3_two_child_necessity": med([r["error_plain"] for r in free]) <= .5*med([r["error_left"] for r in free]) and med([r["error_plain"] for r in free]) <= .5*med([r["error_right"] for r in free]),
        "G4_correct_relation": med([r["error_plain"] for r in free]) <= .5*med([r["error_wrong"] for r in free]),
        "G5_directional_transfer": all(med([r["error_plain"] for r in free if r["direction"] == d]) < .12 for d in ("increasing", "decreasing")),
        "G6_replication": sum(med([r["error_plain"] for r in free if r["run"] == run and r["arm"] == arm]) < .12 for run in ("run1", "run2", "run3") for arm in (1,2,3)) >= 8,
        "G7_physical_ridge": med([r["flow_fraction"] for r in free]) > .90,
    }
    for name, value in gates.items():
        checks[f"gate_{name}"] = value == published["gates"][name]
    checks["verdict"] = published["verdict"] == ("SUPPORTED IN THIS PENDULUM CUT" if all(gates.values()) else "NOT SUPPORTED")

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": int(sum(checks.values())),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
