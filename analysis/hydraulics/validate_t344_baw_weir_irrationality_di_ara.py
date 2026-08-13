"""Independent artifact-level validation for frozen T344.

This script does not import the analysis module and does not trust its JSON verdicts.
It verifies source/protocol hashes and reconstructs gates A-D from saved CSV outputs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
PREFIX = "T344_BAW_WEIR_IRRATIONALITY_DI_ARA"
CONDITIONS = ("low", "medium", "high")
EXPECTED_SOURCE = {
    "low": "bf6bf4536bccabb6cb1991db52b2b630bed65de25475482d229bf1552cfbf549",
    "medium": "d42724a1f136a3b3b4d1e37a90cfb9e9bc2c4319d86392a89ff34e1ab62a70a7",
    "high": "2dfd229ac0561a5fc6601ddf9052f13d391b8e54862ea5e09d099a40af91064e",
}
EXPECTED_FROZEN = {
    "T344_BAW_WEIR_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md": "998a9a2aaa640b725e8c48bdec4e9bfc933ab4e611d3c56f74ec3ba52ef12919",
    "T344_BAW_WEIR_IRRATIONALITY_DI_ARA_COMPUTATIONAL_ADDENDUM_v1_FROZEN.md": "1e26103fc3fa89ac0f3b953cd653f1595ef229e6bd2361693d7a1e8437d23d36",
    "T344_BAW_WEIR_IRRATIONALITY_DI_ARA_RUNTIME_ADDENDUM_v1_FROZEN.md": "fffcccb64f876d5adf2f3726c7202a95c22b6cab84b99a52ef47917af34a65b4",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> None:
    quality = pd.read_csv(HERE / f"{PREFIX}_DATA_QUALITY.csv")
    sectors = pd.read_csv(HERE / f"{PREFIX}_SECTORS.csv")
    models = pd.read_csv(HERE / f"{PREFIX}_MODEL_SCORES.csv")
    boot = pd.read_csv(HERE / f"{PREFIX}_BOOTSTRAPS.csv").set_index("comparison")
    gate_d = pd.read_csv(HERE / f"{PREFIX}_IRRATIONALITY_GATE.csv").set_index(["condition", "comparison"])
    optimisers = pd.read_csv(HERE / f"{PREFIX}_OPTIMISERS.csv")
    windows = pd.read_csv(HERE / f"{PREFIX}_WINDOW_SUMMARY.csv")

    source_hashes = {}
    for condition, expected in EXPECTED_SOURCE.items():
        actual = digest(HERE / "source_baw_weir" / f"Spheres_lab_{condition}.xlsx")
        source_hashes[condition] = {"expected": expected, "actual": actual, "match": actual == expected}
    frozen_hashes = {}
    for name, expected in EXPECTED_FROZEN.items():
        actual = digest(HERE / name)
        frozen_hashes[name] = {"expected": expected, "actual": actual, "match": actual == expected}

    require(all(item["match"] for item in source_hashes.values()), "source hash mismatch")
    require(all(item["match"] for item in frozen_hashes.values()), "frozen protocol hash mismatch")
    require(set(quality["condition"]) == set(CONDITIONS), "condition mismatch")
    require(quality["sha256_matches_official"].astype(bool).all(), "recorded source hash failure")
    require((quality["tracks_without_overlap"] == 0).all(), "non-overlapping trajectory retained")
    require((quality["duplicate_join_frames"] == 0).all(), "duplicate joined frame retained")
    require(optimisers["success"].astype(bool).all(), "an optimiser did not converge")

    gate_a = True
    for condition in CONDITIONS:
        present = sectors[(sectors["condition"] == condition) & sectors["sector"].isin(["Ba", "Ab", "bA", "aB"])]
        gate_a &= len(present) == 4 and (present["events"] > 0).all()

    gate_b_parts = {}
    for name in ("intact_vs_radial_child", "intact_vs_turn_child", "intact_vs_broken_parent"):
        row = boot.loc[name]
        passed = bool(row["fold_wins"] >= 2 and row["ci_low"] > 0)
        gate_b_parts[name] = passed
    gate_b = all(gate_b_parts.values())

    row_c = boot.loc["intact_vs_additive_children"]
    gate_c = bool(row_c["fold_wins"] >= 2 and row_c["ci_low"] > 0)

    info_effects = [float(gate_d.loc[(condition, "structured_minus_random_information"), "estimate"]) for condition in CONDITIONS]
    traversal_effects = [float(gate_d.loc[(condition, "structured_minus_closure_traversal"), "estimate"]) for condition in CONDITIONS]
    pooled_info = gate_d.loc[("pooled", "structured_minus_random_information")]
    pooled_traversal = gate_d.loc[("pooled", "structured_minus_closure_traversal")]
    gate_d_pass = bool(
        sum(value > 0 for value in info_effects) >= 2
        and sum(value > 0 for value in traversal_effects) >= 2
        and pooled_info["ci_low"] > 0
        and pooled_traversal["ci_low"] > 0
    )

    # Fold-level direction check independent of bootstrap labels.
    score = models.pivot(index="test_condition", columns="model", values="log_loss").reindex(CONDITIONS)
    fold_checks = {
        baseline: {condition: bool(score.loc[condition, "intact_parent"] < score.loc[condition, baseline]) for condition in CONDITIONS}
        for baseline in ("radial_child", "turn_child", "additive_children", "broken_parent", "persistence")
    }

    require(gate_a, "Gate A reconstruction failed")
    require(gate_b, "Gate B reconstruction failed")
    require(gate_c, "Gate C reconstruction failed")
    require(not gate_d_pass, "Gate D unexpectedly reconstructed as pass")
    require(all(all(per_fold.values()) for per_fold in fold_checks.values()), "intact model did not beat a baseline in every fold")
    require(set(windows["window"].astype(int)) == {8, 15, 30}, "window sensitivity output incomplete")

    validation = {
        "validation": "independent_saved_artifact_reconstruction",
        "valid": True,
        "source_hashes": source_hashes,
        "frozen_hashes": frozen_hashes,
        "counts": {
            "laboratory_tracks": int(quality["joined_tracks"].sum()),
            "ara_events": int(quality["ara_events"].sum()),
        },
        "optimisers_all_converged": True,
        "fold_checks_intact_lower_log_loss": fold_checks,
        "reconstructed_gates": {
            "A_four_sectors": bool(gate_a),
            "B_intact_parent": bool(gate_b),
            "C_coupling_asymmetry": bool(gate_c),
            "D_structured_nonclosure": bool(gate_d_pass),
        },
        "gate_d_directions": {
            "information": dict(zip(CONDITIONS, info_effects)),
            "traversal": dict(zip(CONDITIONS, traversal_effects)),
            "pooled_information_ci": [float(pooled_info["ci_low"]), float(pooled_info["ci_high"])],
            "pooled_traversal_ci": [float(pooled_traversal["ci_low"]), float(pooled_traversal["ci_high"])],
        },
    }
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    lines = [
        "# T344 independent validation",
        "",
        "**Status: VALIDATED.** The saved artifacts independently reconstruct Gates A-C as passes and Gate D as a failure.",
        "",
        f"- Official source hashes: **{'PASS' if all(x['match'] for x in source_hashes.values()) else 'FAIL'}**",
        f"- Frozen protocol/addendum hashes: **{'PASS' if all(x['match'] for x in frozen_hashes.values()) else 'FAIL'}**",
        f"- Laboratory tracks: **{validation['counts']['laboratory_tracks']:,}**",
        f"- Native ARA events: **{validation['counts']['ara_events']:,}**",
        "- All 18 optimisations converged: **PASS**",
        "- Intact parent lower held-out log loss than every named baseline in every condition: **PASS**",
        "- Gate A / B / C / D: **PASS / PASS / PASS / FAIL**",
        "",
        "The validation does not reinterpret Gate D. Its failed direction remains frozen.",
    ]
    (HERE / f"{PREFIX}_VALIDATION_2026-08-06.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
