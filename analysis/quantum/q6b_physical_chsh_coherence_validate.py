#!/usr/bin/env python3
"""Independent validator for T265/Q6B; does not import the primary runner."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_PROTOCOL_v1_FROZEN.sha256"
Q5_RESULTS = HERE / "Q5_BELL_FOUR_STATE_RESULTS.json"
BOOTSTRAP_CSV = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_BOOTSTRAP.csv"
RESULTS_JSON = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_RESULTS.json"
VALIDATION_JSON = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_VALIDATION.json"
DATA_DIR = HERE / "public_data" / "q4_bell_tomography"

STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
CONTROLS = ("Phi-classical", "Psi-classical", "Bell-uniform-mixed")
ENTITIES = (*STATES, *CONTROLS)
WEIGHTS = {
    "Phi-classical": {"Phi-plus": 0.5, "Phi-minus": 0.5},
    "Psi-classical": {"Psi-plus": 0.5, "Psi-minus": 0.5},
    "Bell-uniform-mixed": {
        "Phi-plus": 0.25,
        "Phi-minus": 0.25,
        "Psi-plus": 0.25,
        "Psi-minus": 0.25,
    },
}
ARCHIVES = {
    "Phi-plus": ("UPUP+DOWNDOWN.zip", "3275210b912d51e5f10ba99d93ad6ca5"),
    "Phi-minus": ("UPUP-DOWNDOWN.zip", "8cd8a5f2b3b9a2ccd090e47312bcc390"),
    "Psi-plus": ("UPDOWN+DOWNUP.zip", "43f782ed4404b01393fb57a2da5d1534"),
    "Psi-minus": ("UPDOWN-DOWNUP.zip", "1724b4484ffb88e41dbac5f50981e91a"),
}
P = {
    "I": np.asarray([[1, 0], [0, 1]], dtype=complex),
    "X": np.asarray([[0, 1], [1, 0]], dtype=complex),
    "Y": np.asarray([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.asarray([[1, 0], [0, -1]], dtype=complex),
}
AXES = ("X", "Y", "Z")


def file_hash(path: Path, kind: str) -> str:
    h = hashlib.new(kind)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def density(exp: dict[str, float]) -> np.ndarray:
    rho = np.zeros((4, 4), dtype=complex)
    for a in ("I", *AXES):
        for b in ("I", *AXES):
            rho += exp[a + b] * np.kron(P[a], P[b])
    rho = 0.25 * rho
    rho = 0.5 * (rho + rho.conj().T)
    vals, vecs = np.linalg.eigh(rho)
    ordered = np.sort(vals)[::-1]
    cssv = np.cumsum(ordered)
    mask = ordered - (cssv - 1.0) / np.arange(1, 5) > 0
    active = int(np.flatnonzero(mask)[-1] + 1)
    shift = (cssv[active - 1] - 1.0) / active
    vals = np.maximum(vals - shift, 0.0)
    return (vecs * vals) @ vecs.conj().T


def summarize(rho: np.ndarray) -> dict[str, object]:
    tensor = np.array(
        [
            [
                np.trace(rho @ np.kron(P[a], P[b])).real
                for b in AXES
            ]
            for a in AXES
        ]
    )
    s = np.sort(np.linalg.svd(tensor, compute_uv=False))[::-1]
    return {
        "tensor": tensor,
        "singular": s,
        "chsh": 2.0 * np.sqrt(s[0] ** 2 + s[1] ** 2),
        "axes": int((s >= 0.5).sum()),
        "trace_error": abs(np.trace(rho) - 1.0),
        "minimum_eigenvalue": np.linalg.eigvalsh(rho).min(),
        "hermiticity": np.max(np.abs(rho - rho.conj().T)),
    }


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return bool(abs(float(a) - float(b)) <= tolerance)


def main() -> None:
    q5 = json.loads(Q5_RESULTS.read_text(encoding="utf-8"))
    result = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    expected_protocol = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    checks["protocol_sha"] = (
        file_hash(PROTOCOL, "sha256") == expected_protocol
        and result["protocol_sha256"] == expected_protocol
    )
    checks["protocol_and_ledger_ids"] = (
        result["protocol_id"] == "Q6B-PHYSICAL-CHSH-v1"
        and result["ledger_id"] == "T265"
    )
    checks["source_doi_and_license"] = (
        result["source"]["doi"] == "10.6084/m9.figshare.14160476.v2"
        and result["source"]["license"] == "CC BY 4.0"
    )
    checks["all_four_archive_md5s"] = all(
        file_hash(DATA_DIR / archive, "md5") == checksum
        and result["source"]["archive_md5s"][state] == checksum
        for state, (archive, checksum) in ARCHIVES.items()
    )

    rhos = {}
    for state in STATES:
        rhos[state] = density(q5["states"][state]["expectations"])
    for control, weights in WEIGHTS.items():
        rhos[control] = sum(
            (weight * rhos[state] for state, weight in weights.items()),
            start=np.zeros((4, 4), dtype=complex),
        )

    independent = {entity: summarize(rhos[entity]) for entity in ENTITIES}
    checks["all_point_tensors_match"] = all(
        np.allclose(
            independent[entity]["tensor"],
            np.asarray(result["entities"][entity]["tensor"]),
            atol=1e-10,
            rtol=0,
        )
        for entity in ENTITIES
    )
    checks["all_point_singular_values_match"] = all(
        np.allclose(
            independent[entity]["singular"],
            np.asarray(result["entities"][entity]["singular_values"]),
            atol=1e-10,
            rtol=0,
        )
        for entity in ENTITIES
    )
    checks["all_point_chsh_values_match"] = all(
        close(independent[entity]["chsh"], result["entities"][entity]["chsh_smax"])
        for entity in ENTITIES
    )
    checks["all_point_axis_counts_match"] = all(
        independent[entity]["axes"]
        == result["entities"][entity]["retained_axes_at_0p50"]
        for entity in ENTITIES
    )
    checks["all_states_physical"] = all(
        independent[entity]["trace_error"] <= 1e-12
        and independent[entity]["minimum_eigenvalue"] >= -1e-12
        and independent[entity]["hermiticity"] <= 1e-12
        for entity in ENTITIES
    )
    checks["all_states_respect_tsirelson"] = all(
        independent[entity]["chsh"] <= 2.0 * np.sqrt(2.0) + 1e-12
        for entity in ENTITIES
    )
    checks["axis_sequence_is_3333110"] = [
        independent[entity]["axes"] for entity in ENTITIES
    ] == [3, 3, 3, 3, 1, 1, 0]

    bootstrap: dict[str, dict[str, list[float]]] = {
        entity: defaultdict(list) for entity in ENTITIES
    }
    with BOOTSTRAP_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    checks["bootstrap_row_count"] = len(rows) == 35000
    for row in rows:
        entity = row["entity"]
        bootstrap[entity]["chsh"].append(float(row["chsh_smax"]))
        bootstrap[entity]["s1"].append(float(row["s1"]))
        bootstrap[entity]["s2"].append(float(row["s2"]))
        bootstrap[entity]["s3"].append(float(row["s3"]))
        bootstrap[entity]["axes"].append(int(row["retained_axes_at_0p50"]))

    checks["bootstrap_5000_each"] = all(
        len(bootstrap[entity]["chsh"]) == 5000 for entity in ENTITIES
    )
    checks["bootstrap_chsh_intervals_match"] = all(
        np.allclose(
            np.percentile(bootstrap[entity]["chsh"], [2.5, 97.5]),
            result["entities"][entity]["chsh_95ci"],
            atol=1e-10,
            rtol=0,
        )
        for entity in ENTITIES
    )
    checks["bootstrap_singular_intervals_match"] = all(
        np.allclose(
            np.percentile(bootstrap[entity][field], [2.5, 97.5]),
            result["entities"][entity][field + "_95ci"],
            atol=1e-10,
            rtol=0,
        )
        for entity in ENTITIES
        for field in ("s1", "s2", "s3")
    )
    checks["bootstrap_above_2_fractions_match"] = all(
        close(
            np.mean(np.asarray(bootstrap[entity]["chsh"]) > 2.0),
            result["entities"][entity]["fraction_chsh_above_2p00"],
        )
        for entity in ENTITIES
    )
    checks["bootstrap_below_2p1_fractions_match"] = all(
        close(
            np.mean(np.asarray(bootstrap[entity]["chsh"]) <= 2.1),
            result["entities"][entity]["fraction_chsh_at_most_2p10"],
        )
        for entity in ENTITIES
    )
    checks["bootstrap_below_0p6_fractions_match"] = all(
        close(
            np.mean(np.asarray(bootstrap[entity]["chsh"]) <= 0.6),
            result["entities"][entity]["fraction_chsh_at_most_0p60"],
        )
        for entity in ENTITIES
    )
    checks["all_reported_gates_pass"] = all(
        gate["pass"] for gate in result["gates"].values()
    )
    checks["gate_count_20_of_20"] = (
        result["gates_passed"] == 20
        and result["gates_total"] == 20
        and len(result["gates"]) == 20
    )
    checks["verdict_supported"] = result["verdict"] == "SUPPORTED"
    checks["prepared_and_reconstructed_types_separated"] = all(
        result["entities"][entity]["entity_type"]
        == ("physically_prepared" if entity in STATES else "equal_weight_reconstruction")
        for entity in ENTITIES
    )
    checks["bell_bootstrap_all_above_boundary"] = all(
        result["entities"][state]["fraction_chsh_above_2p00"] == 1.0
        for state in STATES
    )
    checks["classical_bootstrap_all_below_2p1"] = all(
        result["entities"][state]["fraction_chsh_at_most_2p10"] == 1.0
        for state in ("Phi-classical", "Psi-classical")
    )
    checks["uniform_bootstrap_all_below_0p6"] = (
        result["entities"]["Bell-uniform-mixed"][
            "fraction_chsh_at_most_0p60"
        ]
        == 1.0
    )
    checks["raw_physicality_failure_preserved_in_diagnostics"] = (
        result["physical_projection"]["point_state_diagnostics"]["Phi-minus"][
            "linear_minimum_eigenvalue"
        ]
        < 0
    )

    passed = sum(checks.values())
    total = len(checks)
    payload = {
        "validator": "independent point reconstruction plus bootstrap-artifact audit",
        "passed": passed,
        "total": total,
        "verdict": "PASS" if passed == total else "FAIL",
        "checks": checks,
    }
    VALIDATION_JSON.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
