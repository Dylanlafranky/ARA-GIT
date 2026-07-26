#!/usr/bin/env python3
"""Independent artifact and calculation validation for frozen T262/Q4."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "public_data" / "q4_bell_tomography" / "UPUP-DOWNDOWN.zip"
PROTOCOL = HERE / "Q4_BELL_PARENT_CHILD_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q4_BELL_PARENT_CHILD_PROTOCOL_v1_FROZEN.sha256"
RECORDS = HERE / "Q4_BELL_PARENT_CHILD_RECORDS.csv"
PROJECTIONS = HERE / "Q4_BELL_PARENT_CHILD_PROJECTIONS.csv"
BOOTSTRAP = HERE / "Q4_BELL_PARENT_CHILD_BOOTSTRAP.csv"
RESULTS = HERE / "Q4_BELL_PARENT_CHILD_RESULTS.json"
VALIDATION = HERE / "Q4_BELL_PARENT_CHILD_VALIDATION.json"
ARCHIVE_MD5 = "8cd8a5f2b3b9a2ccd090e47312bcc390"
ORIENTATIONS = ("II", "IX", "IY", "XI", "XX", "XY", "YI", "YX", "YY")
LOCAL = ("YI", "XI", "IY", "IX", "ZI", "IZ")
SAME = ("XX", "YY", "ZZ")
MIXED = ("YZ", "XZ", "ZY", "ZX", "YX", "XY")
BELL = {
    "Phi-plus": {"XX": 1.0, "YY": -1.0, "ZZ": 1.0},
    "Phi-minus": {"XX": -1.0, "YY": 1.0, "ZZ": 1.0},
    "Psi-plus": {"XX": 1.0, "YY": 1.0, "ZZ": -1.0},
    "Psi-minus": {"XX": -1.0, "YY": -1.0, "ZZ": -1.0},
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    archive_hash = digest(ARCHIVE, "md5")
    protocol_hash = digest(PROTOCOL, "sha256")
    expected_protocol_hash = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    check("archive checksum", archive_hash == ARCHIVE_MD5, archive_hash)
    check(
        "frozen protocol checksum",
        protocol_hash == expected_protocol_hash,
        protocol_hash,
    )

    with RECORDS.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    with PROJECTIONS.open(encoding="utf-8", newline="") as handle:
        projections = list(csv.DictReader(handle))
    with BOOTSTRAP.open(encoding="utf-8", newline="") as handle:
        bootstrap = list(csv.DictReader(handle))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))

    check("record row count", len(records) == 9 * 80 * 4, str(len(records)))
    check("projection row count", len(projections) == 15, str(len(projections)))
    check("bootstrap row count", len(bootstrap) == 2000, str(len(bootstrap)))

    record_keys = {
        (
            row["orientation"],
            int(row["record_index"]),
            row["outcome"],
        )
        for row in records
    }
    check(
        "record key uniqueness",
        len(record_keys) == len(records),
        f"{len(record_keys)} unique",
    )
    orientation_coverage = all(
        sum(row["orientation"] == orientation for row in records) == 80 * 4
        for orientation in ORIENTATIONS
    )
    check(
        "orientation coverage",
        orientation_coverage,
        "80 records x four outcomes for all nine orientations",
    )
    fraction_grid_ok = all(
        close(float(row["segment_tunnelling_fraction"]) * 40, round(float(row["segment_tunnelling_fraction"]) * 40))
        for row in records
    )
    check("segment fractions use 40-readout grid", fraction_grid_ok, "all rows")
    classification_ok = all(
        int(row["classified_present"])
        == int(float(row["segment_tunnelling_fraction"]) > 0.5)
        for row in records
    )
    check("state threshold reproduction", classification_ok, "strictly greater than 0.5")

    outcomes = ("DOWNDOWN", "DOWNUP", "UPDOWN", "UPUP")
    probabilities: dict[str, list[float]] = {}
    for orientation in ORIENTATIONS:
        probabilities[orientation] = [
            sum(
                int(row["classified_present"])
                for row in records
                if row["orientation"] == orientation and row["outcome"] == outcome
            )
            / 80.0
            for outcome in outcomes
        ]

    ii, ix, iy, xi, xx, xy, yi, yx, yy = (
        probabilities[label] for label in ORIENTATIONS
    )
    recomputed = {
        "II": sum(ii),
        "IX": ix[0] + ix[1] - ix[2] - ix[3],
        "IY": iy[0] + iy[1] - iy[2] - iy[3],
        "IZ": ii[0] + ii[1] - ii[2] - ii[3],
        "XI": xi[0] - xi[1] + xi[2] - xi[3],
        "XX": xx[0] - xx[1] - xx[2] + xx[3],
        "XY": xy[0] - xy[1] - xy[2] + xy[3],
        "XZ": xi[0] - xi[1] - xi[2] + xi[3],
        "YI": yi[0] - yi[1] + yi[2] - yi[3],
        "YX": yx[0] - yx[1] - yx[2] + yx[3],
        "YY": yy[0] - yy[1] - yy[2] + yy[3],
        "YZ": yi[0] - yi[1] - yi[2] + yi[3],
        "ZI": ii[0] - ii[1] + ii[2] - ii[3],
        "ZX": ix[0] - ix[1] - ix[2] + ix[3],
        "ZY": iy[0] - iy[1] - iy[2] + iy[3],
        "ZZ": ii[0] - ii[1] - ii[2] + ii[3],
    }
    recorded_expectations = {
        label: float(value) for label, value in results["expectations"].items()
    }
    check(
        "all Pauli expectations recomputed from records",
        all(close(recomputed[label], recorded_expectations[label]) for label in recomputed),
        "16/16 including II normalization",
    )
    check(
        "II normalization",
        close(recomputed["II"], 1.0),
        f"{recomputed['II']:.15f}",
    )

    projection_by_label = {row["projection"]: row for row in projections}
    projection_values_ok = all(
        close(float(row["expectation"]), recomputed[row["projection"]])
        for row in projections
    )
    affine_ok = all(
        close(
            float(row["ara_coordinate"]),
            1.0 - float(row["expectation"]),
        )
        for row in projections
    )
    reversal_ok = all(
        close(
            float(row["ara_coordinate"])
            + float(row["reversed_ara_coordinate"]),
            2.0,
        )
        for row in projections
    )
    check("projection table values", projection_values_ok, "15/15")
    check("ARA affine identity", affine_ok, "15/15")
    check("pole-reversal identity", reversal_ok, "15/15")

    local_mean = sum(abs(recomputed[label]) for label in LOCAL) / len(LOCAL)
    same_mean = sum(abs(recomputed[label]) for label in SAME) / len(SAME)
    same_min = min(abs(recomputed[label]) for label in SAME)
    mixed_mean = sum(abs(recomputed[label]) for label in MIXED) / len(MIXED)
    correlation_product = math.prod(recomputed[label] for label in SAME)
    metrics = results["metrics"]
    metrics_ok = (
        close(local_mean, float(metrics["local_child_mean_abs"]))
        and close(same_mean, float(metrics["same_axis_mean_abs"]))
        and close(same_min, float(metrics["same_axis_min_abs"]))
        and close(same_mean - local_mean, float(metrics["same_minus_local"]))
        and close(mixed_mean, float(metrics["mixed_pair_mean_abs"]))
        and close(correlation_product, float(metrics["correlation_product"]))
    )
    check("group metrics independently recomputed", metrics_ok, "6/6")

    maes = {
        name: sum(
            abs(recomputed[label] - pattern[label]) for label in SAME
        )
        / 3.0
        for name, pattern in BELL.items()
    }
    ranked = sorted(maes.items(), key=lambda item: item[1])
    bell_ok = (
        ranked[0][0] == results["closest_bell"] == "Phi-minus"
        and close(ranked[1][1] - ranked[0][1], float(results["bell_margin"]))
    )
    check(
        "Bell-pattern ranking",
        bell_ok,
        f"{ranked[0][0]} margin {ranked[1][1] - ranked[0][1]:.6f}",
    )

    gates = {
        "G1_local_child_mean_abs_at_most_0p20": local_mean <= 0.20,
        "G2_same_axis_signs": recomputed["XX"] < 0
        and recomputed["YY"] > 0
        and recomputed["ZZ"] > 0,
        "G3_weakest_same_axis_abs_at_least_0p50": same_min >= 0.50,
        "G4_same_minus_local_at_least_0p40": same_mean - local_mean >= 0.40,
        "G5_mixed_pair_mean_abs_at_most_0p25": mixed_mean <= 0.25,
        "G6_correlation_product_at_most_negative_0p125": correlation_product
        <= -0.125,
        "G7_phi_minus_closest_with_margin": ranked[0][0] == "Phi-minus"
        and ranked[1][1] - ranked[0][1] >= 0.20,
        "G8_affine_and_reversal_residuals": affine_ok and reversal_ok,
    }
    recorded_gates = {
        name: bool(value["pass"]) for name, value in results["gates"].items()
    }
    check(
        "all frozen gates independently recomputed",
        gates == recorded_gates and all(gates.values()),
        f"{sum(gates.values())}/8",
    )
    check(
        "verdict follows gates",
        results["verdict"] == "SUPPORTED"
        and int(results["gates_passed"]) == 8,
        results["verdict"],
    )

    bootstrap_indices_ok = sorted(int(row["replicate"]) for row in bootstrap) == list(
        range(2000)
    )
    bootstrap_finite = all(
        math.isfinite(float(value))
        for row in bootstrap
        for key, value in row.items()
        if key != "replicate"
    )
    check("bootstrap index coverage", bootstrap_indices_ok, "0 through 1999")
    check("bootstrap finite values", bootstrap_finite, "all metrics")

    group_labels_ok = (
        all(projection_by_label[label]["group"] == "local_child" for label in LOCAL)
        and all(
            projection_by_label[label]["group"] == "same_axis_parent"
            for label in SAME
        )
        and all(
            projection_by_label[label]["group"] == "mixed_pair_control"
            for label in MIXED
        )
    )
    check("projection group assignment", group_labels_ok, "15/15")

    passed = sum(int(item["pass"]) for item in checks)
    output = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "confidence": "Share with caveats",
        "required_caveat": (
            "The archive contains one complete tomography set. Record-level bootstrap "
            "does not replace independent state/device replication, and the Bell/Pauli "
            "pattern is established quantum physics rather than an ARA discovery."
        ),
    }
    VALIDATION.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
