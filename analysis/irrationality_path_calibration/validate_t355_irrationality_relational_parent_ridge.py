#!/usr/bin/env python3
"""Independent artifact-level validation for T355."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PREFIX = "T355_IRRATIONALITY_RELATIONAL_PARENT_RIDGE"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def item(name: str, passed: bool, detail: str) -> dict[str, object]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    protocol = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
    results = json.loads((HERE / f"{PREFIX}_RESULTS.json").read_text(encoding="utf-8"))
    audit = pd.read_csv(HERE / f"{PREFIX}_ASYMMETRY_AUDIT.csv")
    children = pd.read_csv(HERE / f"{PREFIX}_CHILDREN.csv")
    pairs = pd.read_csv(HERE / f"{PREFIX}_PAIRS.csv")
    identities = pd.read_csv(HERE / f"{PREFIX}_IDENTITIES.csv")
    gates = pd.read_csv(HERE / f"{PREFIX}_FROZEN_GATES.csv")
    checks: list[dict[str, object]] = []

    checks.append(item("protocol hash", digest(protocol) == results["protocol_sha256"], digest(protocol)))
    checks.append(item("audit rows", len(audit) == results["audit_rows"] == 144, str(len(audit))))
    checks.append(item("child rows", len(children) == results["child_rows"] == 1152, str(len(children))))
    checks.append(item("pair rows", len(pairs) == results["pair_rows"] == 576, str(len(pairs))))
    checks.append(item("identity rows", len(identities) == results["identity_rows"] == 144, str(len(identities))))
    checks.append(item("72 unique pair identities", children.pair_id.nunique() == 72, str(children.pair_id.nunique())))
    checks.append(item("two construction conditions", set(children.condition.unique()) == {"clean", "asymmetric"}, str(sorted(children.condition.unique()))))
    checks.append(item("two directional children", set(children.direction.unique()) == {"irrational_to_rational", "rational_to_irrational"}, str(children.direction.value_counts().to_dict())))
    checks.append(item("four observation windows", sorted(children.window.unique().tolist()) == [128, 256, 384, 512], str(sorted(children.window.unique().tolist()))))
    checks.append(item("all child predictions finite", bool(np.isfinite(children.predicted_ridge).all()), f"finite={np.isfinite(children.predicted_ridge).mean():.6f}"))

    pair_keys = ["pair_id", "q", "d", "duration", "replicate", "condition", "window", "true_center"]
    reconstructed = children.pivot(index=pair_keys, columns="direction", values="predicted_ridge").reset_index()
    reconstructed["parent_ridge_check"] = (reconstructed.irrational_to_rational + reconstructed.rational_to_irrational) / 2.0
    compare = pairs.merge(reconstructed[pair_keys + ["parent_ridge_check"]], on=pair_keys, how="left", validate="one_to_one")
    checks.append(item("parent midpoint formula", bool(np.allclose(compare.parent_ridge, compare.parent_ridge_check, atol=1e-10, rtol=1e-10)), f"max delta={np.max(np.abs(compare.parent_ridge - compare.parent_ridge_check)):.3e}"))

    clean_mix = float(audit[audit.condition == "clean"].mix_rms.median())
    asym_mix = float(audit[audit.condition == "asymmetric"].mix_rms.median())
    asym_advance = float(audit[audit.condition == "asymmetric"].advance_complement_rms.median())
    checks.append(item("clean paths are mirror control", clean_mix <= 1e-12, f"mix RMS={clean_mix:.12f}"))
    checks.append(item("asymmetric profiles are non-mirrored", asym_mix >= 0.05, f"mix RMS={asym_mix:.12f}"))
    checks.append(item("asymmetric advances fail exact complement", asym_advance >= 0.01, f"advance RMS={asym_advance:.12f}"))

    min_separation = float(children.groupby(["condition", "direction", "window"]).endpoint_separation.median().min())
    prediction_rate = float(children.predicted.mean())
    checks.append(item("endpoint recovery", min_separation >= 0.75 and prediction_rate >= 0.95, f"minimum={min_separation:.12f}; prediction rate={prediction_rate:.6f}"))

    expected = {
        "clean": {"paired": 1.425888672470819, "range": 2.5104554617771555, "single": 335.2735210367788, "wrong": 302.2476832838746},
        "asymmetric": {"paired": 6.67426726261084, "range": 2.938798484799122, "single": 389.4613788471742, "wrong": 290.91775158827625},
    }
    for condition, values in expected.items():
        part = identities[identities.condition == condition]
        observed = {
            "paired": float(part.paired_abs_error_median.median()),
            "range": float(part.paired_parent_range.median()),
            "single": float(part.better_single_error_median.median()),
            "wrong": float(part.wrong_pair_abs_error_median.median()),
        }
        passed = all(np.isclose(observed[key], values[key], atol=1e-8, rtol=1e-8) for key in values)
        checks.append(item(f"headline recompute {condition}", passed, json.dumps(observed)))
        checks.append(item(f"paired localization gate {condition}", observed["paired"] <= 32, f"paired median={observed['paired']:.6f}"))
        checks.append(item(f"window invariance gate {condition}", observed["range"] <= 32, f"range median={observed['range']:.6f}"))
        checks.append(item(f"single-child control {condition}", observed["paired"] <= 0.25 * observed["single"], f"paired={observed['paired']:.6f}; single={observed['single']:.6f}"))
        checks.append(item(f"wrong-pair control {condition}", observed["paired"] <= 0.25 * observed["wrong"], f"paired={observed['paired']:.6f}; wrong={observed['wrong']:.6f}"))

    for condition in ("clean", "asymmetric"):
        medians = pairs[pairs.condition == condition].groupby("window").parent_abs_error.median()
        checks.append(item(f"all window medians below frozen threshold {condition}", bool((medians <= 32).all()), json.dumps({str(k): float(v) for k, v in medians.items()})))

    checks.append(item("official gate count", int(gates.passed.sum()) == results["passed_gates"] == 6, f"{int(gates.passed.sum())}/6"))
    checks.append(item("official verdict", results["verdict"] == "SUPPORTED [SYNTHETIC RELATIONAL PARENT-RIDGE INSTRUMENT ONLY]", results["verdict"]))
    checks.append(item("figure exists", (HERE / f"{PREFIX}_FIGURE.png").exists(), str(HERE / f"{PREFIX}_FIGURE.png")))

    passed_count = sum(bool(check["passed"]) for check in checks)
    validation = {
        "test": "T355",
        "status": "PASS" if passed_count == len(checks) else "FAIL",
        "passed_checks": passed_count,
        "total_checks": len(checks),
        "checks": checks,
    }
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    lines = [
        "# T355 independent validation",
        "",
        f"**Status:** **{validation['status']}** ({passed_count}/{len(checks)} checks)",
        "",
        "The saved child readings independently reproduce the frozen unweighted parent midpoint. The non-mirror audit, endpoint recovery, localization, observer-width invariance, single-child comparison and wrong-pair specificity all recompute from the exported tables.",
        "",
        "## Checks",
        "",
        "| check | result | detail |",
        "|---|---|---|",
    ]
    for check in checks:
        lines.append(f"| {check['check']} | {'PASS' if check['passed'] else 'FAIL'} | `{str(check['detail'])[:170]}` |")
    lines.extend(
        [
            "",
            "## Required caveat",
            "",
            "The paired reconstruction is not algebraically defined from the true centre, but both children were generated around a supplied common seam. This is a valid synthetic instrument calibration, not independent physical evidence for a universal relational ridge.",
        ]
    )
    (HERE / f"{PREFIX}_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": f"{passed_count}/{len(checks)}"}, indent=2))


if __name__ == "__main__":
    main()
