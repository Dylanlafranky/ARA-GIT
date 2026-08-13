#!/usr/bin/env python3
"""Independent artifact and arithmetic validator for T351."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
EXPECTED_PROTOCOL_HASH = "8BF4382F69BB278F22E9848C346A36FBA001F60A7CB36AEFC2DD2CD90234DBBB"
EXPECTED_CLAIM_HASH = "2353B43F143969F565CFB10A4666508602A822786B49E7755CD59971DBC3ABC0"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def ranks(values: np.ndarray) -> np.ndarray:
    return pd.Series(values).rank(method="average").to_numpy(float)


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    r = ranks(np.r_[pos, neg])
    u = float(r[: len(pos)].sum()) - len(pos) * (len(pos) + 1) / 2.0
    return u / (len(pos) * len(neg))


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return bool(abs(float(a) - float(b)) <= tol)


def main() -> None:
    protocol = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_PROTOCOL_v1_FROZEN.md"
    claim = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_CLAIM_PACKET_v1.md"
    summary = pd.read_csv(HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_EVENT_SUMMARY.csv")
    times = pd.read_csv(HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_TIMESERIES.csv")
    teeth = pd.read_csv(HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_TEETH.csv")
    gates = pd.read_csv(HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_FROZEN_GATES.csv")
    result = json.loads((HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_RESULTS.json").read_text(encoding="utf-8"))
    report = (HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_REPORT_2026-08-11.md").read_text(encoding="utf-8")
    figure = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_FIGURE.png"

    checks: list[tuple[str, bool, str]] = []
    checks.append(("protocol hash", sha256(protocol) == EXPECTED_PROTOCOL_HASH, sha256(protocol)))
    checks.append(("claim hash", sha256(claim) == EXPECTED_CLAIM_HASH, sha256(claim)))
    checks.append(("event count", len(summary) == 384, str(len(summary))))
    checks.append(("time-series count", len(times) == 355200, str(len(times))))
    checks.append(("two splits", set(summary.split) == {"calibration", "holdout"}, str(sorted(summary.split.unique()))))
    checks.append(("six regime-mode rows per config", bool((summary.groupby(["split", "case_id"]).size() == 6).all()), "expected 6"))
    checks.append(("phase-scale bounds", bool(times.candidate_geometry.between(0, 1).all()), "candidate geometry in [0,1]"))
    checks.append(("response bounds", bool(times.connection_response.between(0, 1).all()), "connection response in [0,1]"))
    checks.append(("figure exists", figure.exists() and figure.stat().st_size > 10000, str(figure.stat().st_size if figure.exists() else 0)))
    checks.append(("report evidence boundary", "synthetic known-referee" in report, "boundary stated"))

    h = summary[summary.split == "holdout"]
    fwd = h[h["mode"] == "forward"]
    prog = fwd[fwd.regime == "progressive"]
    memory = fwd[fwd.regime == "memory-only"]
    late = fwd[fwd.regime == "late-snap"]
    false = fwd[fwd.regime == "false-seam"]
    pause = h[(h.regime == "progressive") & (h["mode"] == "pause")]
    reverse = h[(h.regime == "progressive") & (h["mode"] == "reverse")]
    r = result["results"]

    recomputed = {
        "z1_connection_share_at_80": float(prog.connection_share_at_80.median()),
        "z2_lock_order_spearman": float(prog.lock_order_spearman.median()),
        "z3_median_k_minus_g_onset_lag": float(prog.median_k_minus_g_onset_lag.median()),
        "z4_pause_connection_gain": float(pause.pause_connection_gain.median()),
        "z4_pause_front_velocity": float(pause.pause_front_velocity.median()),
        "z5_reverse_unlock_spearman": float(reverse.reverse_unlock_spearman.median()),
        "z6_progressive_post_front_response": float(prog.post_front_response.median()),
        "z6_memory_post_front_response": float(memory.post_front_response.median()),
        "z7_response_auroc": auc(prog.response_score.to_numpy(), memory.response_score.to_numpy()),
        "geometry_only_auroc": auc(prog.geometry_score.to_numpy(), memory.geometry_score.to_numpy()),
        "late_snap_share_at_80": float(late.connection_share_at_80.median()),
        "false_seam_response_gap": float(prog.post_front_response.median() - false.post_front_response.median()),
    }
    for key, value in recomputed.items():
        checks.append((f"recompute {key}", close(value, r[key]), f"{value:.15g}"))

    expected_primary = (
        r["z1_connection_share_at_80"] >= 0.55
        and r["z2_lock_order_spearman"] >= 0.80
        and 0.0 <= r["z3_median_k_minus_g_onset_lag"] <= 0.15
        and r["z4_pause_connection_gain"] >= 0.05
        and r["z4_pause_front_velocity"] < 1e-10
        and r["z5_reverse_unlock_spearman"] <= -0.75
        and r["z6_progressive_post_front_response"] >= 0.65
        and r["z6_memory_post_front_response"] <= 0.25
        and r["z7_response_auroc"] >= 0.90
    )
    expected_boundary = 0.49 <= r["geometry_only_auroc"] <= 0.51 and r["geometry_max_difference"] <= 1e-12
    expected_control = r["late_snap_share_at_80"] < 0.15 and r["false_seam_response_gap"] >= 0.25
    checks.append(("primary verdict arithmetic", bool(r["primary_pass"]) == expected_primary, str(expected_primary)))
    checks.append(("boundary verdict arithmetic", bool(r["boundary_pass"]) == expected_boundary, str(expected_boundary)))
    checks.append(("control verdict arithmetic", bool(r["control_pass"]) == expected_control, str(expected_control)))
    checks.append(("gate families complete", set(gates.family) == {"primary", "boundary", "control"}, str(sorted(gates.family.unique()))))
    checks.append(("gate failure preserved", bool((~gates.passed).any()) and result["verdict"] == "NOT SUPPORTED", result["verdict"]))
    checks.append(("tooth records present", len(teeth) > 10000, str(len(teeth))))

    validation = pd.DataFrame(checks, columns=["check", "passed", "detail"])
    passed = int(validation.passed.sum())
    total = len(validation)
    status = "PASSED" if passed == total else "FAILED"
    validation.to_csv(HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_VALIDATION.csv", index=False)
    payload = {"status": status, "checks_passed": passed, "checks_total": total}
    (HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# T351 independent validation",
        "",
        f"**Status:** **{status} — {passed}/{total} checks passed**",
        "",
        "The validator independently reloaded saved CSV/JSON artifacts, recomputed headline medians and AUROCs, verified frozen hashes and checked that the failed verdict was preserved.",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
    (HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if status != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

