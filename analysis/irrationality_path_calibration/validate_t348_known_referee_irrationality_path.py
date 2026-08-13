"""Independent artifact-level validation for frozen T348 outputs.

This validator does not import the measurement script.  It recomputes the
registered gates from the emitted CSVs, verifies provenance hashes and table
cardinalities, and records useful secondary diagnostics that were not gates.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
LENGTH = 4096
EXPECTED_SECTOR = {
    "periodic rational": (0, 0),
    "irrational rotation": (1, 0),
    "deterministic chaos": (1, 0),
    "finite stochastic": (0, 1),
    "continuous stochastic": (1, 1),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_expected_hash(path: Path) -> str:
    return path.read_text(encoding="utf-8").split()[0].upper()


def paired_delta(frame: pd.DataFrame, family: str, column: str) -> float:
    part = frame[frame["family"] == family]
    chronological = part[part["control"] == "chronological"].set_index("path_id")
    shuffled = part[part["control"] == "shuffled"].set_index("path_id")
    ids = chronological.index.intersection(shuffled.index)
    return float(np.median(shuffled.loc[ids, column] - chronological.loc[ids, column]))


def main() -> None:
    metrics = pd.read_csv(HERE / "T348_IRRATIONALITY_PATH_METRICS.csv")
    closure = pd.read_csv(HERE / "T348_IRRATIONALITY_CLOSURE_SUMMARY.csv")
    curves = pd.read_csv(HERE / "T348_IRRATIONALITY_CLOSURE_CURVES.csv")
    summary = pd.read_csv(HERE / "T348_IRRATIONALITY_FAMILY_SUMMARY.csv")
    gates = pd.read_csv(HERE / "T348_IRRATIONALITY_FROZEN_GATES.csv")
    result = json.loads((HERE / "T348_IRRATIONALITY_PATH_RESULTS.json").read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}
    checks["metrics row count = 2016 paths x 8 rows"] = len(metrics) == 16_128
    checks["closure row count = 2016 paths x 2 controls"] = len(closure) == 4_032
    checks["curve row count = 2 splits x 5 families x 2 controls x 512 lags"] = len(curves) == 10_240
    checks["metrics natural key unique"] = not metrics.duplicated(
        ["path_id", "horizon", "control"]
    ).any()
    checks["closure natural key unique"] = not closure.duplicated(["path_id", "control"]).any()
    checks["all coordinates in [0,2]"] = bool(
        metrics["x_p"].between(0, 2).all() and metrics["x_r"].between(0, 2).all()
    )
    checks["all losses non-negative"] = bool(
        metrics["local_loss"].ge(0).all() and metrics["null_loss"].ge(0).all()
    )
    checks["all closure coherence in [0,1] within tolerance"] = bool(
        curves["median_rho"].between(-1e-12, 1 + 1e-12).all()
    )

    protocol_hash = sha256(HERE / "T348_IRRATIONALITY_PATH_KNOWN_REFEREE_PROTOCOL_v1_FROZEN.md")
    claim_hash = sha256(HERE / "T348_IRRATIONALITY_PATH_KNOWN_REFEREE_CLAIM_PACKET_v1.md")
    checks["protocol hash matches sidecar"] = protocol_hash == load_expected_hash(
        HERE / "T348_IRRATIONALITY_PATH_KNOWN_REFEREE_PROTOCOL_v1_FROZEN.sha256"
    )
    checks["claim hash matches sidecar"] = claim_hash == load_expected_hash(
        HERE / "T348_IRRATIONALITY_PATH_KNOWN_REFEREE_CLAIM_PACKET_v1.sha256"
    )
    checks["protocol hash matches result"] = protocol_hash == result["protocol_sha256"]
    checks["claim hash matches result"] = claim_hash == result["claim_sha256"]

    final = metrics[
        (metrics["split"] == "holdout")
        & (metrics["horizon"] == LENGTH)
        & (metrics["control"] == "chronological")
    ].copy()
    final["sector_correct"] = [
        int((row.x_p >= 1) == EXPECTED_SECTOR[row.family][0]
            and (row.x_r >= 1) == EXPECTED_SECTOR[row.family][1])
        for row in final.itertuples()
    ]
    overall_accuracy = float(final["sector_correct"].mean())
    family_accuracy = final.groupby("family", sort=False)["sector_correct"].mean()
    macro_accuracy = float(family_accuracy.mean())
    parameter_accuracy = (
        final.groupby(["family", "parameter"], sort=False)["sector_correct"].mean().reset_index()
    )

    hsum = summary[summary["split"] == "holdout"].set_index("family")
    g1 = {
        "periodic rational x_P < 0.75": hsum.loc["periodic rational", "median_x_p"] < 0.75,
        "finite stochastic x_P < 0.75": hsum.loc["finite stochastic", "median_x_p"] < 0.75,
        "irrational rotation x_P > 1.25": hsum.loc["irrational rotation", "median_x_p"] > 1.25,
        "deterministic chaos x_P > 1.25": hsum.loc["deterministic chaos", "median_x_p"] > 1.25,
        "continuous stochastic x_P > 1.25": hsum.loc["continuous stochastic", "median_x_p"] > 1.25,
    }
    g2 = {
        "periodic rational x_R < 0.75": hsum.loc["periodic rational", "median_x_r"] < 0.75,
        "irrational rotation x_R < 0.75": hsum.loc["irrational rotation", "median_x_r"] < 0.75,
        "deterministic chaos x_R < 1.25": hsum.loc["deterministic chaos", "median_x_r"] < 1.25,
        "finite stochastic x_R > 1.25": hsum.loc["finite stochastic", "median_x_r"] > 1.25,
        "continuous stochastic x_R > 1.25": hsum.loc["continuous stochastic", "median_x_r"] > 1.25,
    }

    hold_closure = closure[(closure["split"] == "holdout") & (closure["control"] == "chronological")]
    g4 = {
        "periodic median rho > 0.90": hsum.loc["periodic rational", "median_mean_rho"] > 0.90,
        "irrational median rho > 0.90": hsum.loc["irrational rotation", "median_mean_rho"] > 0.90,
        "chaos median rho < 0.25": hsum.loc["deterministic chaos", "median_mean_rho"] < 0.25,
        "finite stochastic median rho < 0.25": hsum.loc["finite stochastic", "median_mean_rho"] < 0.25,
        "continuous stochastic median rho < 0.25": hsum.loc["continuous stochastic", "median_mean_rho"] < 0.25,
        "periodic exact closure share >= 0.95": hold_closure.loc[
            hold_closure["family"] == "periodic rational", "exact_closure_64"
        ].mean() >= 0.95,
    }
    irrational = hold_closure[hold_closure["family"] == "irrational rotation"]
    valid_miss = irrational[["best_miss_64", "best_miss_512"]].dropna()
    improvement_share = float((valid_miss["best_miss_512"] < valid_miss["best_miss_64"]).mean())
    g4["irrational no exact closure share >= 0.95"] = 1 - irrational["exact_closure_64"].mean() >= 0.95
    g4["irrational miss improvement share >= 0.80"] = improvement_share >= 0.80

    hold_controls = metrics[(metrics["split"] == "holdout") & (metrics["horizon"] == LENGTH)]
    shuffled_closure = closure[(closure["split"] == "holdout") & (closure["control"] == "shuffled")]
    g5: dict[str, bool] = {}
    for family in ("periodic rational", "irrational rotation", "deterministic chaos"):
        g5[f"{family} delta x_R >= 0.50"] = paired_delta(hold_controls, family, "x_r") >= 0.50
        g5[f"{family} abs delta x_P < 0.10"] = abs(paired_delta(hold_controls, family, "x_p")) < 0.10
    for family in ("periodic rational", "irrational rotation"):
        chronological = hold_closure[hold_closure["family"] == family].set_index("path_id")
        shuffled = shuffled_closure[shuffled_closure["family"] == family].set_index("path_id")
        ids = chronological.index.intersection(shuffled.index)
        rho_drop = float(np.median(chronological.loc[ids, "mean_rho"] - shuffled.loc[ids, "mean_rho"]))
        g5[f"{family} rho drop >= 0.50"] = rho_drop >= 0.50

    recomputed_gates = {
        "G1 potential orientation": bool(all(g1.values())),
        "G2 residual orientation": bool(all(g2.values())),
        "G3 broad-sector recovery": bool(overall_accuracy >= 0.85),
        "G4 closure independence": bool(all(g4.values())),
        "G5 order-destruction control": bool(all(g5.values())),
    }
    emitted_gates = dict(zip(gates["gate"], gates["passed"].astype(bool)))
    checks["independently recomputed gates match emitted gates"] = recomputed_gates == emitted_gates
    checks["reported holdout accuracy independently matches"] = bool(
        abs(overall_accuracy - float(result["sector_accuracy_holdout"])) < 1e-15
    )

    image_info = {}
    for name in ("T348_IRRATIONALITY_PATH_FIGURE.png", "T348_IRRATIONALITY_CIRCLE_EXAMPLES.png"):
        with Image.open(HERE / name) as image:
            image.verify()
        with Image.open(HERE / name) as image:
            image_info[name] = {"width": image.width, "height": image.height, "mode": image.mode}
            checks[f"{name} has nontrivial dimensions"] = image.width >= 1000 and image.height >= 400

    validation = {
        "test": "T348 independent artifact validation",
        "all_checks_passed": bool(all(checks.values())),
        "checks": checks,
        "recomputed_gates": recomputed_gates,
        "overall_holdout_sector_accuracy": overall_accuracy,
        "macro_family_holdout_sector_accuracy": macro_accuracy,
        "family_holdout_sector_accuracy": {k: float(v) for k, v in family_accuracy.items()},
        "parameter_holdout_sector_accuracy": parameter_accuracy.to_dict(orient="records"),
        "irrational_best_miss_improvement_share": improvement_share,
        "image_info": image_info,
        "provenance": {"protocol_sha256": protocol_hash, "claim_sha256": claim_hash},
    }
    (HERE / "T348_IRRATIONALITY_PATH_VALIDATION.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )

    lines = [
        "# T348 independent artifact validation",
        "",
        f"**All checks passed:** {'YES' if validation['all_checks_passed'] else 'NO'}",
        "",
        f"- Overall holdout sector accuracy: {overall_accuracy:.4%}",
        f"- Macro family holdout sector accuracy: {macro_accuracy:.4%}",
        f"- Irrational best-miss improvement share: {improvement_share:.4%}",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- [{'x' if value else ' '}] {key}" for key, value in checks.items())
    lines.extend(["", "## Family holdout sector accuracy", ""])
    lines.extend(f"- {key}: {float(value):.4%}" for key, value in family_accuracy.items())
    lines.extend(["", "## Interpretation boundary", "", "This validates the frozen synthetic instrument calibration artifacts. It does not establish a universal physical law.", ""])
    (HERE / "T348_IRRATIONALITY_PATH_VALIDATION.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "all_checks_passed": validation["all_checks_passed"],
        "overall_accuracy": overall_accuracy,
        "macro_accuracy": macro_accuracy,
        "family_accuracy": validation["family_holdout_sector_accuracy"],
        "recomputed_gates": recomputed_gates,
    }, indent=2))


if __name__ == "__main__":
    main()
