"""Independent saved-artifact validation for frozen T345.

This validator does not import the analysis module and does not trust its JSON
verdicts.  It reconstructs Gates A--D from the contrast CSVs, verifies the
frozen protocol and public-source hashes, and then scores the predeclared
laboratory-to-numerical Gate E transfer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
LAB = "T345_LINE_CIRCLE_TWO_LEDGER"
NUM = f"{LAB}_NUMERICAL_REPLICATION"
CONDITIONS = ("low", "medium", "high")
PROTOCOL = "T345_LINE_CIRCLE_TWO_LEDGER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = "65770ca22b4be2cdca94eecbb976f31d139b9df30847bec509b26920f52a7a23"
EXPECTED_SOURCE = {
    "lab": {
        "low": "bf6bf4536bccabb6cb1991db52b2b630bed65de25475482d229bf1552cfbf549",
        "medium": "d42724a1f136a3b3b4d1e37a90cfb9e9bc2c4319d86392a89ff34e1ab62a70a7",
        "high": "2dfd229ac0561a5fc6601ddf9052f13d391b8e54862ea5e09d099a40af91064e",
    },
    "num": {
        "low": "6b4b30f532cfca965da92d73f92c100ed429cd5a2078a7c7dfc18d1eaf7bdfdd",
        "medium": "feb38f39468a64df5ef50d292b8edbe716f9a4bdd1d76782147d11c0b43a6632",
        "high": "4a3e737bfdb66ad913d08fe182d563e573648820e105da73726b88af6eb07eab",
    },
}
COMPONENTS = (
    "A1 structured minus random circularity",
    "A2 closure minus structured directness",
    "B1 closure minus structured connection",
    "B2 structured minus random connection",
    "C circle-like minus crooked movement info",
    "D1 circle-like future connection change",
    "D2 circle-like minus crooked connection change",
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def as_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def reconstruct(prefix: str) -> dict:
    contrasts = pd.read_csv(HERE / f"{prefix}_CONTRASTS.csv").set_index("component")
    closure = pd.read_csv(HERE / f"{prefix}_CLOSURE_SUMMARY.csv")
    paths = pd.read_csv(HERE / f"{prefix}_PATH_SUMMARY.csv")
    optimisers = pd.read_csv(HERE / f"{prefix}_OPTIMISERS.csv")
    saved = json.loads((HERE / f"{prefix}_RESULTS.json").read_text(encoding="utf-8"))

    require(set(contrasts.index) == set(COMPONENTS), f"{prefix}: component set mismatch")
    component_pass = {}
    component_sign = {}
    for name in COMPONENTS:
        row = contrasts.loc[name]
        directions = sum(float(row[c]) > 0 for c in CONDITIONS)
        rebuilt = bool(as_bool(row["eligible"]) and directions >= 2 and float(row["ci_low"]) > 0)
        require(rebuilt == as_bool(row["pass"]), f"{prefix}: CSV verdict mismatch for {name}")
        require(rebuilt == bool(saved["components"][name]["pass"]), f"{prefix}: JSON verdict mismatch for {name}")
        require(int(row["bootstrap_valid"]) == 2000, f"{prefix}: incomplete bootstrap for {name}")
        component_pass[name] = rebuilt
        estimate = float(row["estimate"])
        component_sign[name] = 1 if estimate > 0 else -1 if estimate < 0 else 0

    gates = {
        "A": component_pass[COMPONENTS[0]] and component_pass[COMPONENTS[1]],
        "B": component_pass[COMPONENTS[2]] and component_pass[COMPONENTS[3]],
        "C": component_pass[COMPONENTS[4]],
        "D": component_pass[COMPONENTS[5]] and component_pass[COMPONENTS[6]],
    }
    require(gates == {key: bool(value["pass"]) for key, value in saved["gates"].items()}, f"{prefix}: gate mismatch")
    require(set(closure["window"].astype(int)) == {8, 15, 30}, f"{prefix}: W sensitivity incomplete")
    require(set(paths["path_class"].astype(int)) == {1, 2}, f"{prefix}: path classes incomplete")
    require(set(paths["condition"]) == set(CONDITIONS), f"{prefix}: condition coverage incomplete")
    require(optimisers["success"].astype(bool).all(), f"{prefix}: optimiser failure")
    require((HERE / f"{prefix}_FIGURE.png").exists(), f"{prefix}: missing figure")

    return {
        "gates": gates,
        "components": component_pass,
        "signs": component_sign,
        "tracks": int(saved["tracks"]),
        "primary_windows": int(saved["primary_windows"]),
        "optimisers_all_converged": True,
    }


def main() -> None:
    protocol_actual = digest(HERE / PROTOCOL)
    require(protocol_actual == PROTOCOL_SHA, "frozen T345 protocol hash mismatch")

    source_hashes = {}
    for representation, expected_by_condition in EXPECTED_SOURCE.items():
        source_hashes[representation] = {}
        for condition, expected in expected_by_condition.items():
            path = HERE / "source_baw_weir" / f"Spheres_{representation}_{condition}.xlsx"
            actual = digest(path)
            require(actual == expected, f"{representation}/{condition}: public-source hash mismatch")
            source_hashes[representation][condition] = {"expected": expected, "actual": actual, "match": True}

    lab = reconstruct(LAB)
    numerical = reconstruct(NUM)
    gate_agreement = {key: lab["gates"][key] == numerical["gates"][key] for key in "ABCD"}
    sign_agreement = {name: lab["signs"][name] == numerical["signs"][name] for name in COMPONENTS}
    full_transfer = bool(all(gate_agreement.values()) and all(sign_agreement.values()))

    validation = {
        "validation": "independent_saved_artifact_reconstruction",
        "valid": True,
        "protocol_sha256": {"expected": PROTOCOL_SHA, "actual": protocol_actual, "match": True},
        "source_hashes": source_hashes,
        "laboratory": lab,
        "numerical": numerical,
        "gate_e": {
            "full_transfer": full_transfer,
            "gate_agreement": gate_agreement,
            "component_sign_agreement": sign_agreement,
        },
    }
    (HERE / f"{LAB}_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")

    lines = [
        "# T345 independent validation",
        "",
        "**Status: VALIDATED.** Saved artifacts independently reconstruct the frozen gates.",
        "",
        f"- Frozen protocol hash: **PASS** (`{PROTOCOL_SHA}`).",
        "- Six public-source hashes: **PASS**.",
        f"- Laboratory Gates A/B/C/D: **{' / '.join('PASS' if lab['gates'][k] else 'FAIL' for k in 'ABCD')}**.",
        f"- Numerical Gates A/B/C/D: **{' / '.join('PASS' if numerical['gates'][k] else 'FAIL' for k in 'ABCD')}**.",
        f"- Gate E full transfer: **{'PASS' if full_transfer else 'FAIL'}**.",
        f"- Laboratory tracks/windows: **{lab['tracks']:,} / {lab['primary_windows']:,}**.",
        f"- Numerical tracks/windows: **{numerical['tracks']:,} / {numerical['primary_windows']:,}**.",
        "",
        "This validation does not reinterpret failed gates and does not promote T345",
        "from a post-T344 diagnostic to an independent confirmation.",
    ]
    (HERE / f"{LAB}_VALIDATION_2026-08-07.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(validation["gate_e"], indent=2))


if __name__ == "__main__":
    main()
