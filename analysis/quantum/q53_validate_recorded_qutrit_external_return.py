"""Independent arithmetic and artifact validation for Q53."""

from __future__ import annotations

import hashlib
import json
import math
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
SOURCE = (
    pathlib.Path(r"F:\SystemFormulaFolder\external_data\quantum")
    / "eth_single_ion_contextuality_2017"
    / "ExpDataYuOh.csv"
)
RESULTS = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_RESULTS.json"
METADATA = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EXTRACTION.json"
FIGURE = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN.png"
OUTPUT = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_VALIDATION.json"
EXPECTED_SHA = "5410775C307EDEA9F68E95133CF0A733B6CD34E7D9D774B6509472FACE74D55D"
PHI = (1 + math.sqrt(5)) / 2
LEFT = 1 / math.e
WIDTH = (PHI - 1) - LEFT
ARC_STARTS = np.mod(LEFT + np.arange(4) / 4, 1)
ARC_NAMES = ("declared", "rotated_1", "rotated_2", "rotated_3")
PLANES = ("psi0_psi1", "psi1_psi2", "psi2_psi0")
DTYPE = np.dtype(
    [
        ("time", "<i8"),
        ("residual", "<f8"),
        ("circle_heading", "<f8"),
        ("circle_strength", "<f8"),
        ("centroid_heading", "<f8"),
        ("centroid_strength", "<f8"),
        ("extrema_heading", "<f8"),
        ("extrema_strength", "<f8"),
    ]
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def in_arc(values: np.ndarray, start: float) -> np.ndarray:
    return np.mod(values - start, 1.0) <= WIDTH


def slow_returns(values: np.ndarray, start: float) -> int:
    state = 0
    count = 0
    for value in values:
        delta = (float(value) - start) % 1.0
        if delta > WIDTH:
            state = 0
            continue
        x = 2.0 * delta / WIDTH
        if state == 0:
            if x <= 0.25:
                state = 1
        elif state == 1:
            if x >= 1.75:
                state = 2
        elif x <= 0.25:
            count += 1
            state = 0
    return count


def fast_returns(values: np.ndarray, start: float) -> int:
    delta = np.mod(values - start, 1.0)
    inside = delta <= WIDTH
    extreme = inside & ((delta <= 0.125 * WIDTH) | (delta >= 0.875 * WIDTH))
    indices = np.flatnonzero(extreme)
    if not indices.size:
        return 0
    segments = np.cumsum(~inside, dtype=np.int64)[indices]
    labels = (delta[indices] >= 0.875 * WIDTH).astype(np.int8)
    keep = np.ones(indices.size, dtype=bool)
    keep[1:] = (segments[1:] != segments[:-1]) | (labels[1:] != labels[:-1])
    segments = segments[keep]
    labels = labels[keep]
    _, starts, counts = np.unique(segments, return_index=True, return_counts=True)
    return int(
        np.sum(np.where(labels[starts] == 0, (counts + 1) // 4, counts // 4))
    )


def check(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"name": name, "pass": bool(passed), "detail": detail}


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []
    checks.append(check("source hash", sha256(SOURCE) == EXPECTED_SHA, sha256(SOURCE)))
    checks.append(
        check(
            "source population",
            metadata["measurements"] == 53_459_987
            and metadata["valid_rows"] == 53_301
            and metadata["omitted_rows"] == 1_062,
            {
                key: metadata[key]
                for key in ("measurements", "valid_rows", "omitted_rows")
            },
        )
    )
    checks.append(
        check("unit norms", metadata["unit_norm_failures"] == 0, metadata["unit_norm_failures"])
    )

    recomputed: dict[str, object] = {}
    plane_arrays: dict[str, np.ndarray] = {}
    for plane in PLANES:
        path = HERE / f"Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_{plane}.bin"
        records = np.fromfile(path, dtype=DTYPE)
        plane_arrays[plane] = records
        expected = int(metadata["extraction"][plane]["external_events"])
        checks.append(
            check(
                f"{plane} binary record integrity",
                path.stat().st_size == expected * DTYPE.itemsize
                and records.size == expected,
                {
                    "bytes": path.stat().st_size,
                    "records": int(records.size),
                    "expected": expected,
                },
            )
        )
        checks.append(
            check(
                f"{plane} finite primary events",
                bool(
                    np.all(np.isfinite(records["circle_strength"]))
                    and np.all(records["circle_strength"] >= 0)
                ),
                int(records.size),
            )
        )
        active = (
            np.isfinite(records["circle_heading"])
            & np.isfinite(records["circle_strength"])
            & (records["circle_strength"] >= 0.01)
        )
        headings = records["circle_heading"][active]
        occupancy = {
            name: int(np.sum(in_arc(headings, float(start))))
            for name, start in zip(ARC_NAMES, ARC_STARTS)
        }
        returns = {
            name: slow_returns(headings, float(start))
            for name, start in zip(ARC_NAMES, ARC_STARTS)
        }
        saved = result["planes"][plane]["circle"]["0.010"]
        checks.append(
            check(
                f"{plane} active count",
                int(headings.size) == int(saved["active_events"]),
                {"recomputed": int(headings.size), "saved": saved["active_events"]},
            )
        )
        checks.append(
            check(
                f"{plane} arc occupancy",
                occupancy == saved["arc_occupancy"],
                {"recomputed": occupancy, "saved": saved["arc_occupancy"]},
            )
        )
        checks.append(
            check(
                f"{plane} ordered returns",
                returns == saved["return_counts"],
                {"recomputed": returns, "saved": saved["return_counts"]},
            )
        )
        recomputed[plane] = {
            "active_events": int(headings.size),
            "arc_occupancy": occupancy,
            "return_counts": returns,
        }

    rng = np.random.default_rng(53_005_300)
    stress_ok = True
    for _ in range(500):
        values = rng.random(int(rng.integers(0, 2_000)))
        for start in ARC_STARTS:
            if slow_returns(values, float(start)) != fast_returns(values, float(start)):
                stress_ok = False
                break
        if not stress_ok:
            break
    checks.append(check("return counter stress test", stress_ok, "500 random sequences x 4 arcs"))

    g1_cuts = []
    g2_cuts = []
    g3_cuts = []
    g4_cuts = []
    for plane in PLANES:
        primary = recomputed[plane]
        occ = primary["arc_occupancy"]
        ret = primary["return_counts"]
        g1_cuts.append(
            occ["declared"] > max(occ["rotated_1"], occ["rotated_2"], occ["rotated_3"])
        )
        thirds = result["planes"][plane]["chronological_thirds"]
        g2_cuts.append(all(thirds[f"third_{i}"]["observed_declared_returns"] > 0 for i in range(1, 4)))
        g3_cuts.append(
            all(
                thirds[f"third_{i}"]["observed_declared_returns"]
                > thirds[f"third_{i}"]["shuffle_p99"]
                for i in range(1, 4)
            )
        )
        g4_cuts.append(
            ret["declared"] > max(ret["rotated_1"], ret["rotated_2"], ret["rotated_3"])
        )
    gates = {
        "G0_source_and_reconstruction_integrity": True,
        "G1_declared_directional_location": sum(g1_cuts) >= 2,
        "G2_complete_ordered_return": sum(g2_cuts) >= 2,
        "G3_time_order": sum(g3_cuts) >= 2,
        "G4_landmark_specificity": sum(g4_cuts) >= 2,
    }
    checks.append(
        check(
            "gate arithmetic",
            all(result["gates"][key] == value for key, value in gates.items()),
            {"recomputed": gates, "saved": result["gates"]},
        )
    )
    substantive = sum(gates[key] for key in list(gates)[1:])
    verdict = (
        "INVALID / NOT TESTABLE"
        if not gates["G0_source_and_reconstruction_integrity"]
        else "SUPPORTED"
        if substantive == 4
        else "MIXED"
        if substantive >= 2
        else "NOT SUPPORTED"
    )
    checks.append(
        check(
            "verdict arithmetic",
            verdict == result["verdict"],
            {"recomputed": verdict, "saved": result["verdict"]},
        )
    )
    checks.append(check("figure exists", FIGURE.exists() and FIGURE.stat().st_size > 0, FIGURE.stat().st_size))

    passed = sum(item["pass"] for item in checks)
    validation = {
        "test": "Q53 recorded qutrit external-return validation",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()

