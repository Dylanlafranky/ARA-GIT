"""Independent validator for Q15 unresolved-component self-identity.

The validator reads the source CSVs and published Q15 outputs directly. It does
not import the test script.
"""

from __future__ import annotations

import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_PROTOCOL_v1_FROZEN.md"
PROTOCOL_HASH = HERE / (
    "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_PROTOCOL_v1_FROZEN.sha256"
)
Q8 = HERE / "Q8_BELL_RELATION_PLANE_RECORDS.csv"
Q9 = HERE / "Q9_INFORMATION3_BELL_ALLOCATIONS.csv"
Q11 = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
RESULTS = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_RESULTS.json"
IDENTITY_CSV = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_METRICS.csv"
HANDOVER_CSV = HERE / "Q15_UNRESOLVED_PHASE_B_HANDOVER_RECORDS.csv"
FIGURE = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA.svg"
VALIDATION = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_VALIDATION.json"

CONDITIONS = ("Ramsey", "Hahn")
STATES = ("Phi-minus", "Phi-plus", "Psi-minus", "Psi-plus")
DRAWS = 9_999
SEED = 20_260_724
TOLERANCE = 1e-12


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def close(a: float, b: float, tolerance: float = TOLERANCE) -> bool:
    return bool(abs(a - b) <= tolerance)


def share(matrix: np.ndarray) -> float:
    centre = np.mean(matrix, axis=0)
    numerator = matrix.shape[0] * np.sum(centre * centre)
    denominator = numerator + np.sum((matrix - centre) ** 2)
    return float(numerator / denominator)


def loso(matrix: np.ndarray) -> float:
    prediction = np.stack(
        [
            np.mean(np.delete(matrix, held_out, axis=0), axis=0)
            for held_out in range(matrix.shape[0])
        ]
    )
    return float(
        1
        - np.sum((matrix - prediction) ** 2)
        / np.sum((matrix - np.mean(matrix)) ** 2)
    )


def condition_arrays(
    rows: list[dict[str, str]], field: str
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["condition"], row["state"])].append(row)

    output: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for condition in CONDITIONS:
        all_values: list[np.ndarray] = []
        reference_waits: np.ndarray | None = None
        for state in STATES:
            ordered = sorted(
                grouped[(condition, state)],
                key=lambda row: int(row["wait_index"]),
            )
            waits = np.asarray([float(row["wait_us"]) for row in ordered])
            values = np.asarray([float(row[field]) for row in ordered])
            if reference_waits is None:
                reference_waits = waits
            else:
                assert np.array_equal(waits, reference_waits)
            all_values.append(values)
        assert reference_waits is not None
        output[condition] = (reference_waits, np.asarray(all_values))
    return output


def recompute_identity(
    arrays: dict[str, tuple[np.ndarray, np.ndarray]],
    rng: np.random.Generator,
) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for condition in CONDITIONS:
        waits, unresolved = arrays[condition]
        change = unresolved - unresolved[:, :1]
        rate = np.gradient(unresolved, waits, axis=1, edge_order=2)
        interval_rate = np.diff(unresolved, axis=1) / np.diff(waits)
        eta_change = share(change)
        eta_rate = share(rate)
        eta_self = min(eta_change, eta_rate)

        exceed = 0
        for _ in range(DRAWS):
            permuted = np.asarray(
                [row[rng.permutation(len(row))] for row in unresolved]
            )
            permuted_change = permuted - permuted[:, :1]
            permuted_rate = np.gradient(
                permuted, waits, axis=1, edge_order=2
            )
            null_self = min(
                share(permuted_change), share(permuted_rate)
            )
            exceed += int(null_self >= eta_self)

        output[condition] = {
            "eta_change": eta_change,
            "eta_rate": eta_rate,
            "eta_self_conservative": eta_self,
            "te_ara_self": 2 * eta_self,
            "te_ara_other": 2 * (1 - eta_self),
            "loso_r2_change_pooled": loso(change),
            "loso_r2_rate_pooled": loso(rate),
            "permutation_p_self": (1 + exceed) / (DRAWS + 1),
            "alternate_first_difference_rate_share": share(interval_rate),
        }
    return output


def handover_null(
    records: list[dict[str, str]], rng: np.random.Generator
) -> tuple[float, float]:
    observed_u = np.asarray(
        [float(row["delta_unresolved"]) for row in records]
    )
    observed_v = np.asarray(
        [float(row["delta_visible"]) for row in records]
    )
    observed = float(np.corrcoef(observed_u, observed_v)[0, 1])

    by_state: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in records:
        by_state[row["state"]].append(row)
    exceed = 0
    for _ in range(DRAWS):
        null_u: list[float] = []
        null_v: list[float] = []
        for state in STATES:
            group = sorted(
                by_state[state], key=lambda row: float(row["ramsey_wait_us"])
            )
            permutation = rng.permutation(len(group))
            for ramsey, hahn_position in zip(group, permutation):
                hahn = group[int(hahn_position)]
                null_u.append(
                    float(ramsey["ramsey_unresolved"])
                    - float(hahn["hahn_unresolved"])
                )
                null_v.append(
                    float(hahn["hahn_visible"])
                    - float(ramsey["ramsey_visible"])
                )
        value = float(np.corrcoef(null_u, null_v)[0, 1])
        exceed += int(value >= observed)
    return observed, (1 + exceed) / (DRAWS + 1)


def main() -> None:
    failures: list[str] = []
    notes: list[str] = []
    published = json.loads(RESULTS.read_text(encoding="utf-8"))

    expected_hash = PROTOCOL_HASH.read_text(encoding="utf-8").split()[0].lower()
    actual_hash = digest(PROTOCOL)
    if expected_hash != actual_hash:
        failures.append("Frozen protocol hash does not match sidecar")
    if published["protocol_sha256"].lower() != actual_hash:
        failures.append("Published result protocol hash does not match protocol")

    q8_rows = read_csv(Q8)
    q9_rows = read_csv(Q9)
    q11_rows = read_csv(Q11)
    if not (len(q8_rows) == len(q9_rows) == len(q11_rows) == 88):
        failures.append("Expected 88 rows in each Q8/Q9/Q11 source")

    for rows, name in ((q8_rows, "Q8"), (q9_rows, "Q9"), (q11_rows, "Q11")):
        keys = [
            (row["condition"], row["state"], int(row["wait_index"]))
            for row in rows
        ]
        if len(keys) != len(set(keys)):
            failures.append(f"{name} contains duplicate condition/state/wait keys")

    q9_index = {
        (row["condition"], row["state"], int(row["wait_index"])): row
        for row in q9_rows
    }
    purity_errors: list[float] = []
    q11_q9_errors: list[float] = []
    for row in q11_rows:
        key = (row["condition"], row["state"], int(row["wait_index"]))
        q9 = q9_index[key]
        expected = 2 * (1 - float(q9["purity"]))
        actual = float(row["target_purity_loss"])
        purity_errors.append(abs(expected - actual))
        q11_q9_errors.append(
            abs(actual - float(q9["i_unresolved_half_scale"]))
        )
    if max(purity_errors) > 2e-12:
        failures.append("Q11 target is not 2*(1-purity) from Q9")
    if max(q11_q9_errors) > 2e-12:
        failures.append("Q11 target does not match Q9 unresolved half scale")

    arrays = condition_arrays(q11_rows, "target_purity_loss")
    rng = np.random.default_rng(SEED)
    recomputed = recompute_identity(arrays, rng)
    for condition in CONDITIONS:
        source = published["primary_identity_metrics"][condition]
        for field in (
            "eta_change",
            "eta_rate",
            "eta_self_conservative",
            "te_ara_self",
            "te_ara_other",
            "loso_r2_change_pooled",
            "loso_r2_rate_pooled",
            "permutation_p_self",
        ):
            if not close(recomputed[condition][field], float(source[field])):
                failures.append(
                    f"{condition} {field} does not independently reproduce"
                )
        if not close(
            float(source["te_ara_self"]) + float(source["te_ara_other"]),
            2.0,
        ):
            failures.append(f"{condition} TE-ARA participation does not close to 2")

    handover_rows = read_csv(HANDOVER_CSV)
    if len(handover_rows) != 16:
        failures.append("Expected 16 approximately common Ramsey/Hahn records")
    observed_correlation, rematching_p = handover_null(handover_rows, rng)
    published_handover = published["conditional_handover"]
    if not close(
        observed_correlation, float(published_handover["delta_correlation"])
    ):
        failures.append("Handover correlation does not reproduce")
    if not close(
        rematching_p,
        float(
            published_handover["rematching_permutation_p_correlation"]
        ),
    ):
        failures.append("Handover rematching probability does not reproduce")

    identity_rows = read_csv(IDENTITY_CSV)
    if len(identity_rows) != 4:
        failures.append("Identity metrics CSV should contain four rows")
    try:
        ET.parse(FIGURE)
    except (ET.ParseError, OSError) as error:
        failures.append(f"SVG is not well formed: {error}")

    expected_verdict = "COHERENT_BUT_MIXED_PHASE_B_NOT_PROMOTED"
    if published["classification"]["verdict"] != expected_verdict:
        failures.append("Verdict differs from independently expected classification")
    if published["classification"]["dominant_coherent_identity_gate"]:
        failures.append("Dominant identity gate should fail because Hahn is mixed")
    if not published["classification"]["coherent_but_mixed_gate"]:
        failures.append("Coherent-but-mixed gate should pass")
    if published["classification"]["conditional_handover_gate"]:
        failures.append("Conditional handover gate should fail rematching control")

    notes.append(
        "First-difference rate shares are an unfrozen numerical robustness "
        "check; they do not alter the frozen classification."
    )
    validation = {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "notes": notes,
        "source_checks": {
            "rows_each_q8_q9_q11": [len(q8_rows), len(q9_rows), len(q11_rows)],
            "maximum_q9_purity_formula_error": max(purity_errors),
            "maximum_q11_q9_target_error": max(q11_q9_errors),
            "protocol_sha256": actual_hash,
        },
        "independently_recomputed_primary_metrics": recomputed,
        "independently_recomputed_handover": {
            "correlation": observed_correlation,
            "rematching_permutation_p": rematching_p,
        },
        "validated_verdict": expected_verdict,
    }
    VALIDATION.write_text(
        json.dumps(validation, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
