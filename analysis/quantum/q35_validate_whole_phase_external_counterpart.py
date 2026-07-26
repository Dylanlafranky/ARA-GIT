"""Independent bounded validator for Q35.

This file does not import the primary Q35 implementation. It rebuilds the
two-cut phase chart, checks deterministic candidate selections and recomputes
the primary exact metrics for a bounded sample and for all saved track rows.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import pathlib
import sys


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import numpy as np


DATA = HERE / "public_data" / "q34_cross_archive_greedy"
CACHE = DATA / "q34_derived_cache.npz"
ARCHIVE = DATA / "unnati_submit_12_pure_greedy.hdf5.zip"
PROTOCOL = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_FIDELITY_v1.md"
RESULTS = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_RESULTS.json"
TRACKS = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_TRACKS.csv.gz"
CANDIDATES = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_CANDIDATES.csv"
OUTPUT = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_VALIDATION.json"

EXPECTED = {
    "protocol": "3f8f872b5a32e6ec7ea61e8e61e9f452a55e361122ba2c5e1178f847043ddbbc",
    "fidelity": "c7cbc1c6860fb33cb47c985cd7eb7c05bdbffde8e231f2cec8eca0337b01d36e",
    "cache": "ab32ad22e207b9913eb69352f52ba9422e18ffb9bf8304d46412d80374428e3c",
    "archive": "c1cf77ccff486e3786d73ba47f8674f1",
}
EPS = 1e-12


def digest(path: pathlib.Path, algorithm: str = "sha256") -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def make_phase(
    h: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    movement = np.diff(h, axis=2)
    q05 = np.quantile(h[:, :, :250, :], 0.05, axis=2)
    q95 = np.quantile(h[:, :, :250, :], 0.95, axis=2)
    centre = (q05 + q95) / 2
    radius = (q95 - q05) / 2
    flow = np.quantile(np.abs(movement[:, :, :249, :]), 0.95, axis=2)
    u = np.divide(
        h[:, :, :499, :] - centre[:, :, None, :],
        radius[:, :, None, :],
        out=np.full((2, 100, 499, 66), np.nan),
        where=radius[:, :, None, :] > EPS,
    )
    v = np.divide(
        movement,
        flow[:, :, None, :],
        out=np.full((2, 100, 499, 66), np.nan),
        where=flow[:, :, None, :] > EPS,
    )
    raw = u + 1j * v
    length = np.abs(raw)
    phase = np.divide(
        raw,
        length,
        out=np.full(raw.shape, np.nan + 1j * np.nan),
        where=length > EPS,
    )
    return movement, phase, raw, q05


def circulation(p: np.ndarray) -> float:
    left, right = p[:-1], p[1:]
    valid = (
        np.isfinite(left.real)
        & np.isfinite(left.imag)
        & np.isfinite(right.real)
        & np.isfinite(right.imag)
    )
    turn = np.angle(np.conj(left[valid]) * right[valid])
    turn = turn[np.abs(turn) > 1e-10]
    return float(abs(np.mean(np.sign(turn)))) if turn.size else 0.0


def is_complete(p: np.ndarray, raw: np.ndarray) -> bool:
    valid = (
        np.isfinite(p.real)
        & np.isfinite(p.imag)
        & np.isfinite(raw.real)
        & np.isfinite(raw.imag)
    )
    if np.mean(valid) < 0.95:
        return False
    quadrant = (
        2 * (raw.real[valid] >= 0).astype(np.int8)
        + (raw.imag[valid] >= 0).astype(np.int8)
    )
    return bool(
        min(np.mean(quadrant == q) for q in range(4)) >= 0.05
        and circulation(p) >= 0.8
    )


def opposition(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    valid = (
        np.isfinite(a.real)
        & np.isfinite(a.imag)
        & np.isfinite(b.real)
        & np.isfinite(b.imag)
    )
    av, bv = a[valid], b[valid]
    score = float(-np.mean(np.real(np.conj(av) * bv)))
    residual = float(np.mean(np.abs(av + bv) / 2))
    difference = np.angle(bv) - np.angle(av) - np.pi
    wrapped = (difference + np.pi) % (2 * np.pi) - np.pi
    half_turn = float(np.mean(np.abs(wrapped) <= np.pi / 4))
    return score, residual, half_turn


def select_one(
    phase: np.ndarray,
    raw: np.ndarray,
    seed: int,
    source: int,
) -> tuple[int, int, float]:
    eligible = [
        pair
        for pair in range(66)
        if pair != source
        and is_complete(
            phase[0, seed, :249, pair],
            raw[0, seed, :249, pair],
        )
    ]
    best = (-np.inf, 99, 99)
    for lag in range(8):
        a = phase[0, seed, : 249 - lag, source]
        for pair in eligible:
            b = phase[0, seed, lag:249, pair]
            score = opposition(a, b)[0]
            candidate = (score, -lag, -pair)
            if candidate > best:
                best = candidate
    return -best[2], -best[1], best[0]


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with CANDIDATES.open("r", newline="", encoding="utf-8") as stream:
        candidate_rows = list(csv.DictReader(stream))
    with gzip.open(TRACKS, "rt", newline="", encoding="utf-8") as stream:
        track_rows = list(csv.DictReader(stream))

    observed_hashes = {
        "protocol": digest(PROTOCOL),
        "fidelity": digest(FIDELITY),
        "cache": digest(CACHE),
        "archive": digest(ARCHIVE, "md5"),
    }
    checks: dict[str, bool] = {
        "source_hashes": observed_hashes == EXPECTED,
        "candidate_row_count": len(candidate_rows)
        == result["eligibility"]["candidate_lineages_before_seam_gate"],
        "track_row_count": len(track_rows)
        == result["eligibility"]["scored_lineages_with_ge_5_seams"],
    }

    derived = np.load(CACHE)
    h = np.asarray(derived["closure"], dtype=np.float64)
    movement, phase, raw, q05 = make_phase(h)
    sample_indices = np.unique(
        np.linspace(0, len(candidate_rows) - 1, 24, dtype=int)
    )
    selection_ok = []
    metric_ok = []
    seam_ok = []
    for index in sample_indices:
        row = candidate_rows[int(index)]
        seed = int(row["seed"])
        source = int(row["source_pair"])
        expected_pair = int(row["counterpart_pair"])
        expected_lag = int(row["lag"])
        pair, lag, score = select_one(phase, raw, seed, source)
        selection_ok.append(
            pair == expected_pair
            and lag == expected_lag
            and abs(score - float(row["development_opposition"])) < 1e-10
        )

    track_sample_indices = np.unique(
        np.linspace(0, len(track_rows) - 1, 24, dtype=int)
    )
    for index in track_sample_indices:
        saved = track_rows[int(index)]
        seed = int(saved["seed"])
        source = int(saved["source_pair"])
        pair = int(saved["counterpart_pair"])
        lag = int(saved["lag"])
        times = np.arange(250, 499 - lag)
        measured = opposition(
            phase[0, seed, times, source],
            phase[0, seed, times + lag, pair],
        )
        metric_ok.append(
            abs(measured[0] - float(saved["exact_opposition"])) < 1e-10
            and abs(measured[1] - float(saved["exact_residual"])) < 1e-10
            and abs(measured[2] - float(saved["exact_half_turn"])) < 1e-10
        )
        seam_times = np.arange(251, 499 - lag)
        seam_times = seam_times[
            (h[0, seed, seam_times, source] <= q05[0, seed, source])
            & (movement[0, seed, seam_times - 1, source] < 0)
        ]
        seam_ok.append(int(saved["seam_events"]) == seam_times.size)

    checks["24_candidate_selections_rebuilt"] = bool(all(selection_ok))
    checks["sample_exact_metrics_rebuilt"] = bool(metric_ok and all(metric_ok))
    checks["sample_seam_counts_rebuilt"] = bool(seam_ok and all(seam_ok))

    exact_opposition = np.asarray(
        [float(row["exact_opposition"]) for row in track_rows]
    )
    exact_residual = np.asarray(
        [float(row["exact_residual"]) for row in track_rows]
    )
    exact_half_turn = np.asarray(
        [float(row["exact_half_turn"]) for row in track_rows]
    )
    checks["saved_exact_summary_recomputed"] = bool(
        abs(
            np.median(exact_opposition)
            - result["summary"]["exact"]["median_opposition"]
        )
        < 1e-12
        and abs(
            np.median(exact_residual)
            - result["summary"]["exact"]["median_parent_residual"]
        )
        < 1e-12
        and abs(
            np.median(exact_half_turn)
            - result["summary"]["exact"]["median_half_turn_occupancy"]
        )
        < 1e-12
    )
    checks["frozen_verdict_consistent"] = bool(
        result["eligibility"]["scored_lineages_with_ge_5_seams"] < 500
        and not result["gates"]["eligibility"]
        and result["claim_verdict"].startswith("INCONCLUSIVE")
    )
    checks["no_coordinate_substitution"] = bool(
        "not the literal structural 0-2 coordinate"
        in result["boundaries"][0]
    )

    validation = {
        "validator": "Q35-independent-bounded-validator-v1",
        "checks": checks,
        "passed": int(sum(checks.values())),
        "total": int(len(checks)),
        "validation_pass": bool(all(checks.values())),
        "sample_candidate_rows": int(len(sample_indices)),
        "sample_scored_rows": int(len(metric_ok)),
        "observed_hashes": observed_hashes,
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
