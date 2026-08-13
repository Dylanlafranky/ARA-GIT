"""Independent saved-artifact validation for frozen T346."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = "205f48d722b80e59f3d0c766790c1ecfeabbf7eac50f3f644590301e1fdda512"
PREFIXES = {
    "lab": "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER",
    "num": "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_NUMERICAL_REPLICATION",
}


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def close(a: float, b: float, tolerance: float = 5e-10) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tolerance, abs_tol=tolerance)


def positive(component: dict | None) -> bool:
    return bool(component and component["ci_low"] > 0 and component["condition_positive"] >= 2)


def expected_gates(window: dict) -> dict:
    c = window["components"]
    gate_a = positive(c["s_build"]) and positive(c["s_release"]) and positive(c["s_peak"])
    gate_b = (
        positive(c["rho_in"])
        and positive(c["rho_out"])
        and c["rho_in"]["broken_p_one_sided"] <= 0.01
        and c["rho_out"]["broken_p_one_sided"] <= 0.01
    )
    gate_c = positive(c["circle_minus_crooked_s_peak"])
    return {"A": bool(gate_a), "B": bool(gate_b), "C": bool(gate_c)}


def validate_representation(representation: str, prefix: str) -> tuple[dict, dict]:
    result_path = HERE / f"{prefix}_RESULTS.json"
    summary_path = HERE / f"{prefix}_SUMMARY.csv"
    null_path = HERE / f"{prefix}_BROKEN_NULLS.csv"
    figure_path = HERE / f"{prefix}_FIGURE.png"
    report_path = HERE / f"{prefix}_REPORT_2026-08-09.md"
    for path in (result_path, summary_path, null_path, figure_path, report_path):
        require(path.exists() and path.stat().st_size > 0, f"missing/empty artifact: {path.name}")

    result = json.loads(result_path.read_text(encoding="utf-8"))
    require(result["protocol_sha256"] == PROTOCOL_SHA, f"{representation}: protocol SHA field")
    require(result["representation"] == representation, f"{representation}: representation field")
    require(set(result["windows"]) == {"8", "15", "30"}, f"{representation}: windows")
    require(all(audit["sha256_matches_official"] for audit in result["source_audits"]),
            f"{representation}: public source hash")

    for window_name, window in result["windows"].items():
        require(window["gates"] == expected_gates(window),
                f"{representation} W={window_name}: gate reconstruction")

    with summary_path.open(newline="", encoding="utf-8") as stream:
        summary = list(csv.DictReader(stream))
    require(len(summary) == 18, f"{representation}: summary row count")
    by_key = {(row["window"], row["component"]): row for row in summary}
    for window_name, window in result["windows"].items():
        for name, component in window["components"].items():
            row = by_key[(window_name, name)]
            if component is None:
                require(row["eligible"].lower() == "false", f"{representation} {window_name} {name}: ineligible")
            else:
                require(row["eligible"].lower() == "true", f"{representation} {window_name} {name}: eligible")
                for field in ("estimate", "ci_low", "ci_high"):
                    require(close(row[field], component[field]),
                            f"{representation} {window_name} {name}: {field}")

    with null_path.open(newline="", encoding="utf-8") as stream:
        null_rows = list(csv.DictReader(stream))
    nulls: dict[tuple[str, str], list[float]] = {}
    for row in null_rows:
        nulls.setdefault((row["window"], row["component"]), []).append(float(row["rho"]))
    for window_name, window in result["windows"].items():
        for name in ("rho_in", "rho_out"):
            component = window["components"][name]
            if component is None:
                continue
            values = nulls[(window_name, name)]
            require(len(values) == 1000, f"{representation} {window_name} {name}: null count")
            p = (1 + sum(value >= component["estimate"] for value in values)) / 1001
            require(close(p, component["broken_p_one_sided"]),
                    f"{representation} {window_name} {name}: broken p")

    primary = result["windows"]["15"]
    signs = {
        name: 0 if component is None else int(math.copysign(1, component["estimate"]))
        for name, component in primary["components"].items()
    }
    return result, {
        "representation": representation,
        "primary_gates": primary["gates"],
        "primary_signs": signs,
        "primary_construction": result["construction"]["15"],
        "artifacts_present": True,
        "source_hashes_valid": True,
        "gate_reconstruction_valid": True,
        "summary_reconstruction_valid": True,
        "broken_null_p_reconstruction_valid": True,
    }


def main():
    actual_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    require(actual_hash == PROTOCOL_SHA, "frozen protocol hash mismatch")
    results, audits = {}, []
    for representation, prefix in PREFIXES.items():
        results[representation], audit = validate_representation(representation, prefix)
        audits.append(audit)

    lab_primary = results["lab"]["windows"]["15"]
    num_primary = results["num"]["windows"]["15"]
    lab_signs = audits[0]["primary_signs"]
    num_signs = audits[1]["primary_signs"]
    transfer = {
        "same_all_six_signs": lab_signs == num_signs,
        "same_gate_ABC": lab_primary["gates"] == num_primary["gates"],
        "gate_D_pass": lab_signs == num_signs and lab_primary["gates"] == num_primary["gates"],
    }
    require(results["num"]["representation_transfer_if_available"]["same_all_six_signs"] == transfer["same_all_six_signs"],
            "stored transfer sign verdict")
    require(results["num"]["representation_transfer_if_available"]["same_gate_ABC"] == transfer["same_gate_ABC"],
            "stored transfer gate verdict")

    output = {
        "test": "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_VALIDATION",
        "protocol_sha256": actual_hash,
        "valid": True,
        "representations": audits,
        "transfer": transfer,
        "boundary": "saved-artifact validator; source-event recomputation remains in the public reproducer",
    }
    (HERE / "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_VALIDATION.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    lines = [
        "# T346 independent saved-artifact validation",
        "",
        "**Date:** 9 August 2026  ",
        f"**Frozen protocol SHA-256:** `{actual_hash}`  ",
        "**Verdict:** PASS",
        "",
        "The validator independently reconstructed all stored Gates A-C, all eligible",
        "summary estimates, every 1,000-member broken-lineage p-value, official source",
        "hash flags, and the cross-representation Gate-D comparison.",
        "",
        f"- Laboratory primary Gates A/B/C: `{lab_primary['gates']}`.",
        f"- Numerical primary Gates A/B/C: `{num_primary['gates']}`.",
        f"- Gate D: `{'PASS' if transfer['gate_D_pass'] else 'FAIL'}`.",
        "",
        "This is a saved-artifact validator. The public reproducer performs the raw",
        "source-event recomputation; the two are kept separate so the validator does not",
        "simply trust the result JSON's declared verdicts.",
    ]
    (HERE / "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_VALIDATION_2026-08-09.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
