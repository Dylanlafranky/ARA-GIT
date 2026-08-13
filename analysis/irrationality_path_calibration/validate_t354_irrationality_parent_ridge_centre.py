#!/usr/bin/env python3
"""Independent artifact-level validation for T354."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PREFIX = "T354_IRRATIONALITY_PARENT_RIDGE_CENTRE"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def check(name: str, passed: bool, detail: str) -> dict[str, object]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def close(left: float, right: float, tolerance: float = 1e-8) -> bool:
    return bool(np.isclose(left, right, atol=tolerance, rtol=tolerance))


def main() -> None:
    protocol = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
    results = json.loads((HERE / f"{PREFIX}_RESULTS.json").read_text(encoding="utf-8"))
    series = pd.read_csv(HERE / f"{PREFIX}_SERIES.csv")
    profiles = pd.read_csv(HERE / f"{PREFIX}_PROFILES.csv")
    identities = pd.read_csv(HERE / f"{PREFIX}_IDENTITIES.csv")
    controls = pd.read_csv(HERE / f"{PREFIX}_WRONG_TIME_CONTROLS.csv")
    gates = pd.read_csv(HERE / f"{PREFIX}_FROZEN_GATES.csv")
    checks: list[dict[str, object]] = []

    actual_hash = digest(protocol)
    checks.append(check("protocol hash", actual_hash == results["protocol_sha256"], actual_hash))
    checks.append(check("series row count", len(series) == results["series_rows"] == 864, str(len(series))))
    checks.append(check("profile row count", len(profiles) == results["profile_rows"] == 102816, str(len(profiles))))
    checks.append(check("identity row count", len(identities) == results["identity_rows"] == 216, str(len(identities))))
    checks.append(check("four windows", sorted(series.window.unique().tolist()) == [128, 256, 384, 512], str(sorted(series.window.unique().tolist()))))
    checks.append(check("both directions", series.direction.nunique() == 2, str(series.direction.value_counts().to_dict())))
    checks.append(check("matched modes", series["mode"].nunique() == 2, str(series["mode"].value_counts().to_dict())))
    checks.append(check("distributed referee centres", series.true_center.nunique() == 54, f"n={series.true_center.nunique()}"))
    checks.append(check("all predictions finite", bool(np.isfinite(series.predicted_ridge).all()), f"finite={np.isfinite(series.predicted_ridge).mean():.6f}"))

    recomputed_rows = []
    for (path_id, direction, mode), group in series.groupby(["path_id", "direction", "mode"]):
        predicted = group.predicted_ridge.to_numpy(float)
        true_center = float(group.true_center.iloc[0])
        recomputed_rows.append(
            {
                "path_id": path_id,
                "direction": direction,
                "mode": mode,
                "predicted_ridge_median": float(np.median(predicted)),
                "abs_error_median": abs(float(np.median(predicted)) - true_center),
                "centre_range": float(np.max(predicted) - np.min(predicted)),
            }
        )
    recomputed = pd.DataFrame(recomputed_rows)
    merged = identities.merge(recomputed, on=["path_id", "direction", "mode"], suffixes=("_saved", "_recomputed"))
    identity_match = all(
        np.allclose(
            merged[f"{column}_saved"], merged[f"{column}_recomputed"], atol=1e-8, rtol=1e-8
        )
        for column in ("predicted_ridge_median", "abs_error_median", "centre_range")
    )
    checks.append(check("identity summaries recompute", identity_match, f"rows={len(merged)}"))

    expected_headlines = {
        ("irrational_to_rational", "ordered"): (325.2231030928165, 166.32844317656338),
        ("irrational_to_rational", "abrupt"): (107.03249162831344, 172.07540300744836),
        ("rational_to_irrational", "ordered"): (320.3270847886845, 165.8611795235006),
        ("rational_to_irrational", "abrupt"): (104.89366530980374, 173.07059159711912),
    }
    for key, (expected_error, expected_range) in expected_headlines.items():
        direction, mode = key
        part = identities[(identities.direction == direction) & (identities["mode"] == mode)]
        observed_error = float(part.abs_error_median.median())
        observed_range = float(part.centre_range.median())
        checks.append(check(f"headline {direction} {mode}", close(observed_error, expected_error) and close(observed_range, expected_range), f"error={observed_error:.12f}; range={observed_range:.12f}"))

    grouped_separation = series.groupby(["direction", "mode", "window"]).endpoint_separation.median()
    r1 = grouped_separation.min() >= 0.75 and series.predicted.mean() >= 0.95
    checks.append(check("R1 recompute", bool(r1) == bool(gates.loc[gates.gate == "R1 endpoint separation", "passed"].iloc[0]), f"minimum={grouped_separation.min():.12f}"))
    checks.append(check("official verdict", results["verdict"] == "RIDGE NOT RESOLVED" and results["passed_gates"] == int(gates.passed.sum()) == 1, f"{results['verdict']}; {int(gates.passed.sum())}/6"))
    checks.append(check("figure exists", (HERE / f"{PREFIX}_FIGURE.png").exists(), str(HERE / f"{PREFIX}_FIGURE.png")))

    pair_keys = ["q", "d", "duration", "replicate", "mode", "window", "true_center"]
    paired = series.pivot(index=pair_keys, columns="direction", values="predicted_ridge").reset_index()
    paired["paired_ridge"] = (paired["irrational_to_rational"] + paired["rational_to_irrational"]) / 2.0
    paired["paired_abs_error"] = np.abs(paired.paired_ridge - paired.true_center)
    posthoc = {}
    for mode in ("ordered", "abrupt"):
        part = paired[paired["mode"] == mode]
        posthoc[mode] = {
            "median_paired_abs_error": float(part.paired_abs_error.median()),
            "p95_paired_abs_error": float(part.paired_abs_error.quantile(0.95)),
        }
    checks.append(check("posthoc direction-pair calculation reproducible", posthoc["ordered"]["median_paired_abs_error"] < 3 and posthoc["abrupt"]["median_paired_abs_error"] < 3, json.dumps(posthoc)))

    passed = sum(bool(item["passed"]) for item in checks)
    validation = {
        "test": "T354",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "passed_checks": passed,
        "total_checks": len(checks),
        "posthoc_not_a_frozen_gate": posthoc,
        "checks": checks,
    }
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    lines = [
        "# T354 independent validation",
        "",
        f"**Status:** **{validation['status']}** ({passed}/{len(checks)} checks)",
        "",
        "The frozen result is reproducible: the one-direction `x_P=1` midpoint does not localize the known centre and moves with observer width. The official verdict remains `RIDGE NOT RESOLVED`.",
        "",
        "## Checks",
        "",
        "| check | result | detail |",
        "|---|---|---|",
    ]
    for item in checks:
        lines.append(f"| {item['check']} | {'PASS' if item['passed'] else 'FAIL'} | `{str(item['detail'])[:160]}` |")
    lines.extend(
        [
            "",
            "## Post-hoc observation - not a frozen T354 gate",
            "",
            "The forward and reverse one-direction biases are almost exactly opposite. Averaging the two independently predicted directional centres gives a median absolute error below three states in both modes. This is hypothesis-generating only and requires a newly frozen direction-pair test.",
            "",
            f"- ordered paired median absolute error: `{posthoc['ordered']['median_paired_abs_error']:.6f}` states",
            f"- abrupt paired median absolute error: `{posthoc['abrupt']['median_paired_abs_error']:.6f}` states",
        ]
    )
    (HERE / f"{PREFIX}_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": f"{passed}/{len(checks)}", "posthoc": posthoc}, indent=2))


if __name__ == "__main__":
    main()
