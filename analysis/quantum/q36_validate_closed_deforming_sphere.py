"""Independent validation for Q36 closed/deforming-sphere test outputs.

This script deliberately does not import the primary Q36 implementation.
It reconstructs source hashes, event summaries, eligibility, selected event
times, and raw-matrix tensor metrics from the frozen source arrays.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q34_cross_archive_greedy"
CONNECTED = DATA / "q34_connected_cache.npy"
DERIVED = DATA / "q34_derived_cache.npz"
METRICS = DATA / "q36_tensor_metric_cache.npz"
EVENTS = HERE / "Q36_CLOSED_DEFORMING_SPHERE_EVENTS.csv.gz"
RESULTS = HERE / "Q36_CLOSED_DEFORMING_SPHERE_RESULTS.json"
PROTOCOL = HERE / "Q36_CLOSED_DEFORMING_SPHERE_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q36_CLOSED_DEFORMING_SPHERE_FIDELITY_v1.md"
OUTPUT = HERE / "Q36_CLOSED_DEFORMING_SPHERE_VALIDATION.json"

EXPECTED = {
    "connected": "8b02fa7d186e9e6debb60b501297cf39f2d55de11511fe116775d0eb6b4abde7",
    "derived": "ab32ad22e207b9913eb69352f52ba9422e18ffb9bf8304d46412d80374428e3c",
    "protocol": "7ca57a9a8fcf54ae186f8f6af14597445fa1dc38b944026ab4efd832eef454e4",
    "fidelity": "01f4f7619f10a87bd8bf80d3a8b957dc0a1a026b39d69a3cb0e5f07b8949311d",
}
OFFSETS = np.asarray(list(range(-7, 0)) + list(range(1, 8)))
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def median(values: list[float]) -> float:
    return float(np.nanmedian(np.asarray(values, dtype=np.float64)))


def circulation(z: np.ndarray) -> float:
    phase = z / np.abs(z)
    good = np.isfinite(phase[:-1].real) & np.isfinite(phase[1:].real)
    turn = np.angle(np.conj(phase[:-1][good]) * phase[1:][good])
    turn = turn[np.abs(turn) > 1e-10]
    return float(abs(np.mean(np.sign(turn)))) if turn.size else 0.0


def reconstruct_eligibility(closure: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Reconstruct the frozen Q35 complete-loop mask without Q36 code."""
    dev = np.asarray(closure[0, :, :250, :], dtype=np.float64)
    delta = np.diff(dev, axis=1)
    lo = np.quantile(dev, 0.05, axis=1)
    hi = np.quantile(dev, 0.95, axis=1)
    centre = (lo + hi) / 2
    radius = (hi - lo) / 2
    flow = np.quantile(np.abs(delta), 0.95, axis=1)
    u = (dev[:, :249] - centre[:, None]) / radius[:, None]
    v = delta / flow[:, None]
    z = u + 1j * v
    mask = np.zeros((100, 66), dtype=bool)
    coherence = np.full((100, 66), np.nan)
    for seed in range(100):
        for pair in range(66):
            line = z[seed, :, pair]
            valid = np.isfinite(line.real) & np.isfinite(line.imag)
            if float(np.mean(valid)) < 0.95:
                continue
            quadrants = (
                2 * (line.real[valid] >= 0).astype(np.int8)
                + (line.imag[valid] >= 0).astype(np.int8)
            )
            minimum = min(float(np.mean(quadrants == q)) for q in range(4))
            coherence[seed, pair] = circulation(line[valid])
            mask[seed, pair] = minimum >= 0.05 and coherence[seed, pair] >= 0.80
    return mask, coherence


def selected_times(line: np.ndarray, threshold: float) -> list[int]:
    selected: list[int] = []
    for time in range(258, 492):
        if not (
            line[time - 1] > line[time]
            and line[time] <= line[time + 1]
            and line[time] <= threshold
        ):
            continue
        if selected and time - selected[-1] < 7:
            continue
        selected.append(time)
    return selected


def raw_metrics(
    matrix: np.ndarray,
    closure: np.ndarray,
    seed: int,
    pair: int,
    time: int,
) -> dict[str, float]:
    local_t = time + OFFSETS

    def base_quantities(t: int) -> tuple[float, float, float, float, float, float]:
        c = np.asarray(matrix[0, seed, t, pair], dtype=np.float64)
        amplitude = float(np.linalg.norm(c))
        singular = np.linalg.svd(c, compute_uv=False)
        energy = amplitude * amplitude
        probabilities = singular * singular / energy
        effective_rank = float(1 / np.sum(probabilities * probabilities))
        lattice = float(np.clip(3 * float(closure[0, seed, t, pair]) ** 2 / energy, 0, 1))
        q = c @ c.T / energy
        before = np.asarray(matrix[0, seed, t - 1, pair], dtype=np.float64)
        after = np.asarray(matrix[0, seed, t + 1, pair], dtype=np.float64)
        qb = before @ before.T / float(np.sum(before * before))
        qa = after @ after.T / float(np.sum(after * after))
        wobble = float(np.linalg.norm(qa - qb))
        return amplitude, lattice, 1 - lattice, effective_rank, float(singular[-1]), wobble

    event = base_quantities(time)
    local = [base_quantities(int(t)) for t in local_t]
    a_base = median([x[0] for x in local])
    h_base = median([float(closure[0, seed, int(t), pair]) for t in local_t])
    s3_base = median([x[4] for x in local])
    wobble_base = median([x[5] for x in local])
    h_event = float(closure[0, seed, time, pair])
    reclosure = float(
        np.max(closure[0, seed, time + 1 : time + 8, pair]) / h_base
    )
    return {
        "amplitude_retention": event[0] / a_base,
        "closure_retention": h_event / h_base,
        "selective_gap": event[0] / a_base - h_event / h_base,
        "lattice_share": event[1],
        "deforming_share": event[2],
        "effective_rank": event[3],
        "weakest_axis_retention": event[4] / s3_base,
        "wobble_ratio": event[5] / wobble_base,
        "reclosure_ratio": reclosure,
    }


def close_enough(left: float, right: float, atol: float = 2e-5) -> bool:
    return bool(np.isclose(left, right, rtol=2e-5, atol=atol, equal_nan=True))


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with gzip.open(EVENTS, "rt", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))

    hashes = {
        "connected": sha256(CONNECTED),
        "derived": sha256(DERIVED),
        "protocol": sha256(PROTOCOL),
        "fidelity": sha256(FIDELITY),
    }
    hashes_pass = hashes == EXPECTED

    closure = np.load(DERIVED)["closure"]
    matrix = np.load(CONNECTED, mmap_mode="r")
    eligibility, coherence = reconstruct_eligibility(closure)

    grouped: dict[tuple[int, int], list[int]] = {}
    for row in rows:
        key = (int(row["seed"]), int(row["source_pair"]))
        grouped.setdefault(key, []).append(int(row["time"]))

    lineage_keys = sorted(grouped)
    selected_lineages = [
        lineage_keys[int(index)]
        for index in np.linspace(0, len(lineage_keys) - 1, 24, dtype=int)
    ]
    event_reconstruction_checks = []
    for seed, pair in selected_lineages:
        threshold = float(np.quantile(closure[0, seed, :250, pair], 0.20))
        reconstructed = selected_times(closure[0, seed, :, pair], threshold)
        saved = grouped[(seed, pair)]
        event_reconstruction_checks.append(
            {
                "seed": seed,
                "pair": pair,
                "eligible": bool(eligibility[seed, pair]),
                "circulation": float(coherence[seed, pair]),
                "saved_events": saved,
                "reconstructed_events": reconstructed,
                "pass": saved == reconstructed,
            }
        )

    sample_indices = np.linspace(0, len(rows) - 1, 24, dtype=int)
    raw_checks = []
    fields = (
        "amplitude_retention",
        "closure_retention",
        "selective_gap",
        "lattice_share",
        "deforming_share",
        "effective_rank",
        "weakest_axis_retention",
        "wobble_ratio",
        "reclosure_ratio",
    )
    for index in sample_indices:
        row = rows[int(index)]
        seed = int(row["seed"])
        pair = int(row["source_pair"])
        time = int(row["time"])
        recalculated = raw_metrics(matrix, closure, seed, pair, time)
        deltas = {
            field: abs(
                recalculated[field] - float(row[f"exact_{field}"])
            )
            for field in fields
        }
        raw_checks.append(
            {
                "row": int(index),
                "seed": seed,
                "pair": pair,
                "time": time,
                "max_absolute_difference": float(max(deltas.values())),
                "pass": all(
                    close_enough(
                        recalculated[field],
                        float(row[f"exact_{field}"]),
                    )
                    for field in fields
                ),
            }
        )

    summary_checks = {}
    for variant in ("exact", "time", "pair", "network"):
        measures = {
            "median_amplitude_retention": median(
                [float(row[f"{variant}_amplitude_retention"]) for row in rows]
            ),
            "median_closure_retention": median(
                [float(row[f"{variant}_closure_retention"]) for row in rows]
            ),
            "median_selective_gap": median(
                [float(row[f"{variant}_selective_gap"]) for row in rows]
            ),
            "median_deforming_share": median(
                [float(row[f"{variant}_deforming_share"]) for row in rows]
            ),
            "median_wobble_ratio": median(
                [float(row[f"{variant}_wobble_ratio"]) for row in rows]
            ),
            "median_reclosure_ratio": median(
                [float(row[f"{variant}_reclosure_ratio"]) for row in rows]
            ),
        }
        differences = {
            key: abs(measures[key] - float(result["summary"][variant][key]))
            for key in measures
        }
        summary_checks[variant] = {
            "recalculated": measures,
            "max_absolute_difference": float(max(differences.values())),
            "pass": all(value < 1e-10 for value in differences.values()),
        }

    validations = {
        "hashes": hashes_pass,
        "eligibility_count": int(np.sum(eligibility))
        == int(result["eligibility"]["q35_complete_c2_lineages"]),
        "represented_lineages": len(grouped)
        == int(result["eligibility"]["represented_lineages"]),
        "event_count": len(rows)
        == int(result["eligibility"]["retained_trough_events"]),
        "event_reconstruction": all(x["pass"] for x in event_reconstruction_checks),
        "raw_matrix_metrics": all(x["pass"] for x in raw_checks),
        "summary_reconstruction": all(
            x["pass"] for x in summary_checks.values()
        ),
    }
    output = {
        "test_id": "Q36-CLOSED-DEFORMING-SPHERE-v1-independent-validation",
        "date": "2026-07-27",
        "validation_pass": all(validations.values()),
        "validations": validations,
        "hashes": hashes,
        "counts": {
            "eligible_lineages": int(np.sum(eligibility)),
            "represented_lineages": len(grouped),
            "events": len(rows),
            "sampled_raw_rows": len(raw_checks),
            "sampled_event_lineages": len(event_reconstruction_checks),
        },
        "summary_checks": summary_checks,
        "raw_metric_checks": raw_checks,
        "event_reconstruction_checks": event_reconstruction_checks,
        "note": (
            "Validation reconstructs source eligibility and selected events, "
            "then recalculates sampled tensor metrics directly from raw 3x3 matrices."
        ),
    }
    OUTPUT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
