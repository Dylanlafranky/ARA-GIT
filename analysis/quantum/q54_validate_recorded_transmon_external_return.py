"""Independent validation for Q54.

This file does not import the primary implementation.  It independently
parses the recorded T2 files, reconstructs the frozen mean-trace circles and
external tangents, and checks the saved population and invalid verdict.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = Path(
    r"F:\SystemFormulaFolder\external_data\quantum"
    r"\zenodo_ist_transmon_2023\subset"
)
MANIFEST = DATA / "Q54_ZENODO_SUBSET_MANIFEST.json"
RESULTS = HERE / "Q54_RECORDED_TRANSMON_EXTERNAL_RETURN_RESULTS.json"
CENTRES = HERE / "Q54_RECORDED_TRANSMON_CENTRES.csv.gz"
EVENTS = HERE / "Q54_RECORDED_TRANSMON_EVENTS.csv.gz"
FIGURE = HERE / "Q54_RECORDED_TRANSMON_EXTERNAL_RETURN.png"
OUTPUT = HERE / "Q54_RECORDED_TRANSMON_EXTERNAL_RETURN_VALIDATION.json"

LEFT = 1.0 / math.e
PHI = (1.0 + math.sqrt(5.0)) / 2.0
WIDTH = PHI - 1.0 - LEFT
MIN_POINTS = 6
MIN_SPAN = 1.8 * math.pi
MIN_RADIUS_FRACTION = 0.20
MAX_RESIDUAL = 0.25
MIN_MOVEMENT = 0.01
EPS = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def vectors(path: Path) -> list[np.ndarray]:
    output = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        try:
            output.append(
                np.asarray([float(value) for value in line.split()], dtype=np.float64)
            )
        except ValueError:
            continue
    return output


def parse(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    rows = vectors(path)
    if len(rows) < 4:
        return None
    repeats = rows[0].size
    if len(rows) != 2 + 2 * repeats:
        return None
    delay = rows[1]
    if any(row.size != delay.size for row in rows[2:]):
        return None
    i_rows = np.vstack(rows[2 : 2 + repeats])
    q_rows = np.vstack(rows[2 + repeats : 2 + 2 * repeats])
    if (
        delay.size != 101
        or repeats < 9
        or i_rows.shape != q_rows.shape
        or i_rows.shape[1] != delay.size
        or not np.all(np.diff(delay) > 0)
        or not np.all(np.isfinite(i_rows))
        or not np.all(np.isfinite(q_rows))
    ):
        return None
    return delay, i_rows, q_rows


def orient(i_rows: np.ndarray, q_rows: np.ndarray) -> np.ndarray:
    z = np.mean(i_rows + 1j * q_rows, axis=0)
    origin = np.mean(z[-20:])
    z = z - origin
    anchor = np.mean(z[:5])
    z = z * np.exp(-1j * np.angle(anchor))
    if float(np.median(np.diff(np.unwrap(np.angle(z))))) < 0:
        z = np.conj(z)
    return z


def fit(points: np.ndarray) -> tuple[complex, float, float] | None:
    x = points.real
    y = points.imag
    matrix = np.column_stack((2 * x, 2 * y, np.ones(points.size)))
    target = x * x + y * y
    solution, _, rank, _ = np.linalg.lstsq(matrix, target, rcond=None)
    if rank < 3:
        return None
    centre = complex(float(solution[0]), float(solution[1]))
    radius_sq = float(solution[2] + abs(centre) ** 2)
    if radius_sq <= EPS:
        return None
    radius = math.sqrt(radius_sq)
    residual = float(
        np.median(np.abs(np.abs(points - centre) - radius)) / radius
    )
    return centre, radius, residual


def circles(z: np.ndarray) -> list[tuple[int, complex, float]]:
    phase = np.unwrap(np.angle(z))
    start_phase = float(phase[0])
    previous = 0
    crossings = [0]
    step = 1
    while start_phase + step * 2 * math.pi <= float(np.max(phase)) + EPS:
        candidates = np.flatnonzero(
            (np.arange(phase.size) > previous)
            & (phase >= start_phase + step * 2 * math.pi)
        )
        if not candidates.size:
            break
        previous = int(candidates[0])
        crossings.append(previous)
        step += 1
    output = []
    first_radius = None
    for index, (start, end) in enumerate(zip(crossings[:-1], crossings[1:])):
        points = z[start : end + 1]
        if points.size < MIN_POINTS or phase[end] - phase[start] < MIN_SPAN:
            continue
        fitted = fit(points)
        if fitted is None:
            continue
        centre, radius, residual = fitted
        if first_radius is None:
            first_radius = radius
        if radius < MIN_RADIUS_FRACTION * first_radius or residual > MAX_RESIDUAL:
            continue
        output.append((index, centre, radius))
    return output


def reconstruct() -> dict[str, object]:
    hashes = set()
    primary_files = []
    primary_centres = []
    primary_events = []
    for path in sorted((DATA / "Fig6").rglob("T2_*.txt")):
        digest = sha256(path)
        duplicate = digest in hashes
        hashes.add(digest)
        device = next(
            (part for part in path.parts if part in {"Device A", "Device B", "Device C"}),
            "unknown",
        )
        parsed = parse(path)
        if (
            parsed is None
            or duplicate
            or device not in {"Device B", "Device C"}
        ):
            continue
        primary_files.append(path)
        delay, i_rows, q_rows = parsed
        retained = circles(orient(i_rows, q_rows))
        primary_centres.extend(
            (str(path.relative_to(DATA).as_posix()), *row) for row in retained
        )
        for left_index in range(1, len(retained) - 1):
            previous, current, following = retained[left_index - 1 : left_index + 2]
            consecutive = (
                current[0] == previous[0] + 1
                and following[0] == current[0] + 1
            )
            radii = np.asarray([previous[2], current[2], following[2]])
            delta = following[1] - previous[1]
            strength = float(abs(delta) / np.mean(radii))
            angle = (
                float((math.atan2(delta.imag, delta.real) / (2 * math.pi)) % 1)
                if abs(delta) > EPS
                else math.nan
            )
            primary_events.append(
                {
                    "path": str(path.relative_to(DATA).as_posix()),
                    "consecutive": consecutive,
                    "strength": strength,
                    "heading": angle,
                }
            )
    eligible = [
        row
        for row in primary_events
        if row["consecutive"]
        and row["strength"] >= MIN_MOVEMENT
        and math.isfinite(row["heading"])
    ]
    declared = sum(
        ((row["heading"] - LEFT) % 1.0) <= WIDTH for row in eligible
    )
    control3_start = (LEFT + 0.75) % 1.0
    control3 = sum(
        ((row["heading"] - control3_start) % 1.0) <= WIDTH for row in eligible
    )
    return {
        "primary_files": len(primary_files),
        "primary_mean_centres": len(primary_centres),
        "primary_mean_events": len(primary_events),
        "eligible_primary_mean": len(eligible),
        "declared_count": int(declared),
        "rotated_3_count": int(control3),
        "eligible_files": len({row["path"] for row in eligible}),
    }


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reconstructed = reconstruct()
    with gzip.open(CENTRES, "rt", encoding="utf-8", newline="") as stream:
        centre_rows = list(csv.DictReader(stream))
    with gzip.open(EVENTS, "rt", encoding="utf-8", newline="") as stream:
        event_rows = list(csv.DictReader(stream))

    manifest_hashes = {
        Path(item["local_path"]).resolve(): item["sha256"]
        for item in manifest["files"]
        if Path(item["local_path"]).suffix.lower() == ".txt"
    }
    raw_hashes_ok = all(
        path.exists() and sha256(path) == expected
        for path, expected in manifest_hashes.items()
    )

    checks = {
        "manifest_file_count_100": manifest["extracted_file_count"] == 100,
        "manifest_raw_hashes_match": raw_hashes_ok,
        "independent_primary_files_21": reconstructed["primary_files"] == 21,
        "independent_primary_mean_centres_18": (
            reconstructed["primary_mean_centres"]
            == result["population"]["centres_primary_mean"]
            == 18
        ),
        "independent_primary_events_1": (
            reconstructed["primary_mean_events"] == 1
        ),
        "independent_eligible_event_1": (
            reconstructed["eligible_primary_mean"]
            == result["population"]["eligible_primary_mean"]
            == 1
        ),
        "independent_declared_count_0": (
            reconstructed["declared_count"]
            == result["arc_occupancy"]["mean"]["pooled"]["counts"]["declared"]
            == 0
        ),
        "independent_rotated_3_count_1": (
            reconstructed["rotated_3_count"]
            == result["arc_occupancy"]["mean"]["pooled"]["counts"]["rotated_3"]
            == 1
        ),
        "saved_centre_rows_47": len(centre_rows) == result["population"]["centres_all"] == 47,
        "saved_event_rows_2": len(event_rows) == result["population"]["events_all"] == 2,
        "g0_false": result["gates"]["G0_valid_hardware_object"] is False,
        "all_verdicts_invalid": all(
            value == "INVALID" for value in result["verdicts"].values()
        ),
        "figure_exists_nonempty": FIGURE.exists() and FIGURE.stat().st_size > 10_000,
    }
    output = {
        "test": "Q54 independent validation",
        "reconstructed": reconstructed,
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "verdict": "PASS" if all(checks.values()) else "FAIL",
        "implementation_independence": (
            "This validator does not import q54_recorded_transmon_external_return.py."
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
