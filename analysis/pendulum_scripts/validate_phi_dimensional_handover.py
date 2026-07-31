"""Independent row-level validation of the frozen Phi handover outputs."""
from __future__ import annotations

import csv
import json
import os
from collections import defaultdict

import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "phi_dimensional_handover_results.json")
CSV_PATH = os.path.join(HERE, "phi_dimensional_handover_events.csv")

PHI = (1.0 + np.sqrt(5.0)) / 2.0
U = 2.0 - PHI


def linear_dist(x, landmarks):
    x = np.asarray(x)
    landmarks = np.asarray(landmarks)
    return np.min(np.abs(x[:, None] - landmarks[None, :]), axis=1)


def circ_dist(x, landmarks):
    x = np.asarray(x)
    landmarks = np.asarray(landmarks)
    d = np.abs(x[:, None] - landmarks[None, :])
    return np.min(np.minimum(d, 1.0 - d), axis=1)


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        saved = json.load(f)
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["run"]].append(row)

    checks = []
    audit = {}
    for run in ("run1", "run2", "run3", "triple1"):
        rr = grouped[run]
        x = np.array([float(r["diameter_x"]) for r in rr])
        u = np.array([float(r["cycle_u"]) for r in rr])
        retention = np.array([float(r["parent_retention"]) for r in rr])
        joint = np.array([float(r["joint_phi_proximity"]) for r in rr])

        s = saved["runs"][run]["summary"]
        recomputed = {
            "n": len(rr),
            "median_joint": float(np.median(joint)),
            "median_retention": float(np.median(retention)),
            "diameter_phi": float(np.median(linear_dist(x, [U, 2.0 - U]))),
            "circular_phi": float(np.median(circ_dist(u, [U, 1.0 - U]))),
            # Post-verdict audit; this was omitted from the frozen alternatives.
            "diameter_poles": float(np.median(linear_dist(x, [0.0, 2.0]))),
        }
        expected = {
            "n": s["n_events"],
            "median_joint": s["median_joint_phi_proximity"],
            "median_retention": s["median_identity_retention"],
            "diameter_phi": s["diameter_landmark_median_distance"]["phi"],
            "circular_phi": s["circular_landmark_median_distance"]["phi"],
        }
        for key, value in expected.items():
            if key == "n":
                ok = recomputed[key] == value
            else:
                ok = abs(recomputed[key] - value) < 1e-12
            checks.append((run, key, ok, recomputed[key], value))
        audit[run] = recomputed

    failures = [x for x in checks if not x[2]]
    result = {
        "validator": "validate_phi_dimensional_handover.py",
        "row_count": len(rows),
        "checks": len(checks),
        "failures": len(failures),
        "post_verdict_pole_control": audit,
        "saved_verdict": saved["frozen_evaluation_verdict"],
    }
    print(json.dumps(result, indent=2))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
