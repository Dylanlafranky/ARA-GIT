#!/usr/bin/env python3
"""Independent arithmetic/source validator for frozen Q60 outputs.

This validator does not import the primary runner.  It reconstructs the
per-sweep ARA phase from the raw MAT files using the frozen detector axis and
mean-wave parameters recorded in the result, then recomputes the score table
and headline verdict conditions.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.io import loadmat


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "public_data" / "extracted" / "AllopticalSCQreadout_data" / "Fig_4b" / "T2_errorbars"
ARCHIVE = HERE / "public_data" / "AllopticalSCQreadout_data.zip"
PROTOCOL = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_PROTOCOL_v1_FROZEN.md"
PHASES = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_PHASES.csv.gz"
SCORES = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_SCORES.csv"
RESULTS = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_RESULTS.json"
OUT = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_VALIDATION.json"

PROTOCOL_SHA = "68701DE96A6539D2B4A9BB3DB59A7BF2D874B868C5134B8766741C37AEFCF598"
ARCHIVE_SHA = "73F3E2CA7B3658452B4C171532C751E96D7392DCB8741B87A18E28C7073D67FD"
TOL = 2e-10


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def signed_circle(values: np.ndarray) -> np.ndarray:
    return (values + 1.0) % 2.0 - 1.0


def score(files: dict[str, np.ndarray], candidate: float) -> float:
    losses = []
    for x in files.values():
        d = np.diff(x) % 2.0
        losses.append(float(np.median(np.abs(signed_circle(d - candidate)))))
    return float(np.mean(losses))


def add(checks: list[dict], name: str, ok: bool, detail: object = None) -> None:
    checks.append({"check": name, "pass": bool(ok), "detail": detail})


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks: list[dict] = []
    add(checks, "protocol hash", sha256(PROTOCOL) == PROTOCOL_SHA, sha256(PROTOCOL))
    add(checks, "source archive hash", sha256(ARCHIVE) == ARCHIVE_SHA, sha256(ARCHIVE))
    add(checks, "recorded protocol hash", result["protocol_sha256"] == PROTOCOL_SHA)
    add(checks, "recorded source hash", result["source_archive_sha256"] == ARCHIVE_SHA)

    phase_rows: dict[str, list[dict]] = {}
    with gzip.open(PHASES, "rt", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            phase_rows.setdefault(row["file"], []).append(row)

    quality = {row["file"]: row for row in result["file_quality"]}
    reconstructed: dict[str, dict[str, np.ndarray]] = {}
    for name, q in quality.items():
        path = SOURCE / name
        raw = loadmat(path)
        I = np.squeeze(np.asarray(raw["I"], dtype=float))
        Q = np.squeeze(np.asarray(raw["Q"], dtype=float))
        t = np.squeeze(np.asarray(raw["t_ns"], dtype=float))
        add(checks, f"{name}: raw schema", I.shape == Q.shape == (2000, 126) and t.shape == (126,), [I.shape, Q.shape, t.shape])
        order = np.argsort(t)
        t = t[order] - np.min(t)
        Y = I[:, order] * float(q["detector_direction"][0]) + Q[:, order] * float(q["detector_direction"][1])
        env = np.exp(-t / float(q["tau_ns"]))
        design = np.column_stack((np.ones_like(t), env * np.cos(float(q["omega_rad_per_ns"]) * t), env * np.sin(float(q["omega_rad_per_ns"]) * t)))
        beta, *_ = np.linalg.lstsq(design, Y.T, rcond=None)
        beta = beta.T
        x = (np.arctan2(beta[:, 2], beta[:, 1]) % (2.0 * np.pi)) / np.pi
        amp = np.hypot(beta[:, 1], beta[:, 2])
        exported = phase_rows[name]
        x_out = np.array([float(r["x"]) for r in exported])
        amp_out = np.array([float(r["amplitude"]) for r in exported])
        step_out = np.array([float(r["step_to_next"]) if r["step_to_next"] else np.nan for r in exported])
        add(checks, f"{name}: 2000 exported phases", len(exported) == 2000, len(exported))
        add(checks, f"{name}: phase reconstruction", float(np.max(np.abs(signed_circle(x - x_out)))) < TOL, float(np.max(np.abs(signed_circle(x - x_out)))))
        add(checks, f"{name}: amplitude reconstruction", bool(np.allclose(amp, amp_out, rtol=1e-10, atol=1e-12)), float(np.max(np.abs(amp - amp_out))))
        add(checks, f"{name}: ordered steps", bool(np.allclose(np.diff(x) % 2.0, step_out[:-1], rtol=0, atol=TOL)), float(np.nanmax(np.abs((np.diff(x) % 2.0) - step_out[:-1]))))
        reconstructed.setdefault(q["split"], {})[name] = x

    stored_scores = {}
    with SCORES.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stored_scores[(row["split"], row["candidate"])] = float(row["primary_loss"])

    for split in ("calibration", "evaluation", "holdout"):
        for candidate, step in result["candidate_steps"].items():
            got = score(reconstructed[split], float(step))
            expected = stored_scores[(split, candidate)]
            add(checks, f"{split}: {candidate} score", abs(got - expected) < 2e-12, {"recomputed": got, "stored": expected})

    cal_steps = []
    for x in reconstructed["calibration"].values():
        cal_steps.append(np.mean(np.exp(1j * np.pi * (np.diff(x) % 2.0))))
    z = np.mean(cal_steps)
    fitted = (np.angle(z) / np.pi) % 2.0
    add(checks, "calibration fitted step", abs(signed_circle(np.array([fitted - result["calibration_fitted_step"]]))[0]) < 2e-12, {"recomputed": fitted, "stored": result["calibration_fitted_step"]})

    for split in ("evaluation", "holdout"):
        p = stored_scores[(split, "persistence")]
        f = stored_scores[(split, "phi_2_over_phi")]
        fit = stored_scores[(split, "calibration_fitted")]
        add(checks, f"{split}: Phi worse than persistence", f > p, {"phi": f, "persistence": p})
        add(checks, f"{split}: Phi outside 5% fitted compatibility", f > 1.05 * fit, {"phi": f, "fitted": fit})

    add(checks, "stored G0", result["gates"]["G0_usable_phase_reconstruction"] is True)
    add(checks, "stored G1 false", result["gates"]["G1_ordered_phase_transport"] is False)
    add(checks, "stored G2 false", result["gates"]["G2_phi_compatibility"] is False)
    add(checks, "stored G3 false", result["gates"]["G3_phi_identification"] is False)

    payload = {
        "validator": "independent raw-MAT reconstruction and exported-score audit",
        "checks": len(checks),
        "passed": sum(c["pass"] for c in checks),
        "failed": sum(not c["pass"] for c in checks),
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "details": checks,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Q60 validation: {payload['status']} ({payload['passed']}/{payload['checks']} checks)")
    if payload["failed"]:
        for c in checks:
            if not c["pass"]:
                print("FAIL:", c["check"], c["detail"])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
