"""Independent validation and laboratory/numerical comparison for T344 Gate E."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
LAB = "T344_BAW_WEIR_IRRATIONALITY_DI_ARA"
NUM = f"{LAB}_NUMERICAL_REPLICATION"
CONDITIONS = ("low", "medium", "high")
EXPECTED_SOURCE = {
    "low": "6b4b30f532cfca965da92d73f92c100ed429cd5a2078a7c7dfc18d1eaf7bdfdd",
    "medium": "feb38f39468a64df5ef50d292b8edbe716f9a4bdd1d76782147d11c0b43a6632",
    "high": "4a3e737bfdb66ad913d08fe182d563e573648820e105da73726b88af6eb07eab",
}
ADDENDUM_HASH = "c089fd1e739fb723336a3c6b9adae9af575ca6be3d7160098ca61840b58c3672"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def reconstruct(prefix: str) -> dict:
    sectors = pd.read_csv(HERE / f"{prefix}_SECTORS.csv")
    boot = pd.read_csv(HERE / f"{prefix}_BOOTSTRAPS.csv").set_index("comparison")
    gate_d = pd.read_csv(HERE / f"{prefix}_IRRATIONALITY_GATE.csv").set_index(["condition", "comparison"])
    optimisers = pd.read_csv(HERE / f"{prefix}_OPTIMISERS.csv")
    quality = pd.read_csv(HERE / f"{prefix}_DATA_QUALITY.csv")
    gate_a = all(
        len(sectors[(sectors["condition"] == condition) & sectors["sector"].isin(["Ba", "Ab", "bA", "aB"])]) == 4
        and (sectors[(sectors["condition"] == condition) & sectors["sector"].isin(["Ba", "Ab", "bA", "aB"])]["events"] > 0).all()
        for condition in CONDITIONS
    )
    b_names = ("intact_vs_radial_child", "intact_vs_turn_child", "intact_vs_broken_parent")
    b_effects = {name: {condition: float(boot.loc[name, condition]) for condition in CONDITIONS} for name in b_names}
    gate_b = all(boot.loc[name, "fold_wins"] >= 2 and boot.loc[name, "ci_low"] > 0 for name in b_names)
    c = boot.loc["intact_vs_additive_children"]
    gate_c = bool(c["fold_wins"] >= 2 and c["ci_low"] > 0)
    info = {condition: float(gate_d.loc[(condition, "structured_minus_random_information"), "estimate"]) for condition in CONDITIONS}
    traversal = {condition: float(gate_d.loc[(condition, "structured_minus_closure_traversal"), "estimate"]) for condition in CONDITIONS}
    pooled_info = gate_d.loc[("pooled", "structured_minus_random_information")]
    pooled_traversal = gate_d.loc[("pooled", "structured_minus_closure_traversal")]
    gate_d_pass = bool(
        sum(value > 0 for value in info.values()) >= 2
        and sum(value > 0 for value in traversal.values()) >= 2
        and pooled_info["ci_low"] > 0
        and pooled_traversal["ci_low"] > 0
    )
    return {
        "gates": {"A": bool(gate_a), "B": bool(gate_b), "C": bool(gate_c), "D": bool(gate_d_pass)},
        "b_effects": b_effects,
        "c_effects": {condition: float(c[condition]) for condition in CONDITIONS},
        "d_information": info,
        "d_traversal": traversal,
        "optimisers_all_converged": bool(optimisers["success"].astype(bool).all()),
        "tracks": int(quality["joined_tracks"].sum()),
        "ara_events": int(quality["ara_events"].sum()),
    }


def signs(values: dict[str, float]) -> dict[str, int]:
    return {key: 1 if value > 0 else -1 if value < 0 else 0 for key, value in values.items()}


def main() -> None:
    hashes = {
        condition: digest(HERE / "source_baw_weir" / f"Spheres_num_{condition}.xlsx")
        for condition in CONDITIONS
    }
    assert hashes == EXPECTED_SOURCE, "official numerical source hash mismatch"
    assert digest(HERE / "T344_BAW_WEIR_NUMERICAL_REPLICATION_ADDENDUM_v1_FROZEN.md") == ADDENDUM_HASH

    lab = reconstruct(LAB)
    num = reconstruct(NUM)
    assert num["optimisers_all_converged"]
    assert num["gates"] == {"A": True, "B": False, "C": True, "D": False}

    direction_agreement = {}
    for comparison in num["b_effects"]:
        direction_agreement[comparison] = {
            condition: signs(lab["b_effects"][comparison])[condition] == signs(num["b_effects"][comparison])[condition]
            for condition in CONDITIONS
        }
    direction_agreement["intact_vs_additive_children"] = {
        condition: signs(lab["c_effects"])[condition] == signs(num["c_effects"])[condition]
        for condition in CONDITIONS
    }
    direction_agreement["structured_minus_random_information"] = {
        condition: signs(lab["d_information"])[condition] == signs(num["d_information"])[condition]
        for condition in CONDITIONS
    }
    direction_agreement["structured_minus_closure_traversal"] = {
        condition: signs(lab["d_traversal"])[condition] == signs(num["d_traversal"])[condition]
        for condition in CONDITIONS
    }
    gate_e = all(all(values.values()) for values in direction_agreement.values())
    assert not gate_e, "Gate E unexpectedly passed full direction agreement"

    result = {
        "valid": True,
        "source_hashes_match": True,
        "replication_addendum_hash_match": True,
        "laboratory": lab,
        "numerical": num,
        "direction_agreement": direction_agreement,
        "Gate_E_full_direction_agreement": gate_e,
        "interpretation": {
            "replicated": [
                "all four sectors",
                "intact beats turn child",
                "intact beats causally broken parent",
                "interaction beats additive children",
                "structured nonclosure is less direct than closure",
                "frozen structured-nonclosure gate fails",
            ],
            "not_replicated": [
                "intact beats radial child",
                "condition-level information direction in low and medium",
            ],
        },
    }
    (HERE / f"{NUM}_VALIDATION.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    report = f"""# T344 numerical replication validation

**Status: VALIDATED, PARTIAL REPLICATION. Gate E full-direction criterion: FAIL.**

- Official numerical hashes: **PASS**
- Frozen numerical mapping addendum hash: **PASS**
- Numerical tracks / ARA events: **{num['tracks']:,} / {num['ara_events']:,}**
- All numerical optimisations converged: **PASS**
- Numerical Gates A / B / C / D: **PASS / FAIL / PASS / FAIL**

The four sectors, turn-child advantage, causal-pairing advantage, coupling-asymmetry
advantage and failed traversal direction replicated. The stronger parent-over-either-child
claim did not: the numerical radial child beat the intact parent in all three conditions.
The numerical structured-nonclosing information effect was negative in all three settings,
whereas the laboratory effect was positive in low and medium and negative in high.

No numerical row was pooled with a laboratory row, and the partial replication is not
averaged into a pass.
"""
    (HERE / f"{NUM}_VALIDATION_2026-08-06.md").write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
