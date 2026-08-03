"""T333: reciprocal radial breathing on recorded trapped-qutrit vectors.

This runner follows the frozen T333 protocol.  It consumes the checksum-locked
Q53 external-vector extraction and never imports the Q53 or T307 runners.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
QUANTUM = REPO / "analysis" / "quantum"
SOURCE = (
    REPO.parents[1]
    / "external_data"
    / "quantum"
    / "eth_single_ion_contextuality_2017"
    / "ExpDataYuOh.csv"
)
EVENTS = QUANTUM / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EVENTS.npz"
PROTOCOL = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_PROTOCOL_v1_FROZEN.md"

OUT_RESULTS = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_RESULTS.json"
OUT_CELLS = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_CELLS.csv"
OUT_QUADRANTS = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_QUADRANTS.csv"
OUT_NULLS = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_NULLS.csv"
OUT_FIGURE = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING.png"

SOURCE_SHA256 = "5410775c307edea9f68e95133cf0a733b6cd34e7d9d774b6509472face74d55d"
PROTOCOL_SHA256 = "81a05e47746d6cc2829f658af7376b78e2c0f90e12001fecbea420c8c0e03f93"
EXPECTED_EVENTS = {
    "psi0_psi1": 168_399,
    "psi1_psi2": 169_035,
    "psi2_psi0": 168_456,
}
PLANES = tuple(EXPECTED_EVENTS)
ESTIMATORS = ("circle", "centroid", "extrema")
PRIMARY = "circle"
LAGS = (1, 2, 4, 8, 16, 32, 64)
MAX_GAP = 2200
MIN_STRENGTH = 0.01
MAX_RESIDUAL = 0.25
SHUFFLES = 500
SHUFFLE_BLOCK = 10_000
SHUFFLE_SEED = 3_332_026

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PLASTIC = 1.324717957244746
CANDIDATES = {
    "plastic": PLASTIC,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "octave": 2.0,
    "e": math.e,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def as_native(value):
    if isinstance(value, dict):
        return {str(key): as_native(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [as_native(item) for item in value]
    if isinstance(value, np.ndarray):
        return [as_native(item) for item in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def load_planes() -> dict[str, dict[str, np.ndarray]]:
    archive = np.load(EVENTS)
    planes: dict[str, dict[str, np.ndarray]] = {}
    for plane in PLANES:
        arrays = {
            "time": np.asarray(archive[f"{plane}_time"], dtype=np.int64),
            "residual": np.asarray(archive[f"{plane}_residual"], dtype=float),
        }
        for estimator in ESTIMATORS:
            arrays[f"{estimator}_heading"] = np.asarray(
                archive[f"{plane}_{estimator}_heading"], dtype=float
            )
            arrays[f"{estimator}_strength"] = np.asarray(
                archive[f"{plane}_{estimator}_strength"], dtype=float
            )
        planes[plane] = arrays
    return planes


def eligible(arrays: dict[str, np.ndarray], estimator: str) -> np.ndarray:
    amp = arrays[f"{estimator}_strength"]
    heading = arrays[f"{estimator}_heading"]
    return (
        np.isfinite(amp)
        & np.isfinite(heading)
        & np.isfinite(arrays["residual"])
        & (amp >= MIN_STRENGTH)
        & (arrays["residual"] <= MAX_RESIDUAL)
    )


def continuity_prefix(time: np.ndarray) -> np.ndarray:
    broken = np.diff(time) > MAX_GAP
    return np.concatenate((np.zeros(1, dtype=np.int64), np.cumsum(broken)))


def lag_indices(
    arrays: dict[str, np.ndarray],
    estimator: str,
    start: int,
    stop: int,
    lag: int,
) -> tuple[np.ndarray, np.ndarray]:
    valid = eligible(arrays, estimator)
    index = np.arange(start, stop - lag, dtype=np.int64)
    prefix = continuity_prefix(arrays["time"])
    continuous = (prefix[index + lag] - prefix[index]) == 0
    keep = valid[index] & valid[index + lag] & continuous
    left = index[keep]
    return left, left + lag


def lag_values(
    arrays: dict[str, np.ndarray],
    estimator: str,
    start: int,
    stop: int,
    lag: int,
    amp_override: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    amp = (
        arrays[f"{estimator}_strength"]
        if amp_override is None
        else amp_override
    )
    heading = arrays[f"{estimator}_heading"]
    left, right = lag_indices(arrays, estimator, start, stop, lag)
    ratio = amp[right] / amp[left]
    phase = 2.0 * math.pi * (heading[right] - heading[left])
    delta = np.arctan2(np.sin(phase), np.cos(phase))
    finite = np.isfinite(ratio) & (ratio > 0.0) & np.isfinite(delta)
    return ratio[finite], delta[finite]


def endpoint_metrics(ratios: np.ndarray) -> dict[str, object]:
    contracting = ratios[ratios < 1.0]
    expanding = ratios[ratios > 1.0]
    if contracting.size == 0 or expanding.size == 0:
        raise RuntimeError("both radial directions are required")
    m_minus = float(np.median(contracting))
    m_plus = float(np.median(expanding))
    scores = {
        name: abs(math.log(m_minus) + math.log(alpha))
        + abs(math.log(m_plus) - math.log(alpha))
        for name, alpha in CANDIDATES.items()
    }
    winner = min(scores, key=scores.get)
    return {
        "n": int(ratios.size),
        "n_contracting": int(contracting.size),
        "n_expanding": int(expanding.size),
        "median_contracting": m_minus,
        "median_expanding": m_plus,
        "reciprocal_product": m_minus * m_plus,
        "scores": scores,
        "winner": winner,
        "asymmetric_e_phi_score": abs(math.log(m_minus) + 1.0)
        + abs(math.log(m_plus) - math.log(PHI)),
    }


def pooled_ratios(
    arrays: dict[str, np.ndarray],
    estimator: str,
    start: int,
    stop: int,
    amp_override: np.ndarray | None = None,
) -> np.ndarray:
    values = [
        lag_values(arrays, estimator, start, stop, lag, amp_override)[0]
        for lag in LAGS
    ]
    return np.concatenate(values)


def fit_train_alpha(ratios: np.ndarray) -> float:
    logs = np.log(ratios)
    contraction = logs[logs < 0.0]
    expansion = logs[logs > 0.0]
    return float(
        math.exp(0.5 * (float(np.median(expansion)) - float(np.median(contraction))))
    )


def score_alpha(metrics: dict[str, object], alpha: float) -> float:
    m_minus = float(metrics["median_contracting"])
    m_plus = float(metrics["median_expanding"])
    return abs(math.log(m_minus) + math.log(alpha)) + abs(
        math.log(m_plus) - math.log(alpha)
    )


def quadrant_record(
    plane: str, ratios: np.ndarray, delta: np.ndarray
) -> dict[str, object]:
    log_s = np.log(ratios)
    labels = {
        "contracting_reverse": (log_s < 0.0) & (delta < 0.0),
        "contracting_forward": (log_s < 0.0) & (delta > 0.0),
        "expanding_reverse": (log_s > 0.0) & (delta < 0.0),
        "expanding_forward": (log_s > 0.0) & (delta > 0.0),
    }
    usable = np.ones(ratios.size, dtype=bool)
    usable &= log_s != 0.0
    usable &= delta != 0.0
    total = int(np.sum(usable))
    row: dict[str, object] = {"plane": plane, "valid_steps": total}
    for name, mask in labels.items():
        count = int(np.sum(mask & usable))
        row[f"{name}_count"] = count
        row[f"{name}_share"] = count / total if total else math.nan
    return row


def shuffle_amplitudes(
    amp: np.ndarray,
    valid: np.ndarray,
    start: int,
    stop: int,
    rng: np.random.Generator,
) -> np.ndarray:
    shuffled = amp.copy()
    for left in range(start, stop, SHUFFLE_BLOCK):
        right = min(stop, left + SHUFFLE_BLOCK)
        positions = np.flatnonzero(valid[left:right]) + left
        if positions.size > 1:
            shuffled[positions] = rng.permutation(shuffled[positions])
    return shuffled


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_figure(
    planes: dict[str, dict[str, np.ndarray]],
    cells: list[dict[str, object]],
    quadrants: list[dict[str, object]],
    null_rows: list[dict[str, object]],
    results: dict[str, object],
) -> None:
    image = Image.new("RGB", (2400, 1700), "#f7f8fa")
    draw = ImageDraw.Draw(image)
    ink = "#20262e"
    grid = "#d8dde3"
    blue = "#4777b8"
    orange = "#d9972f"
    green = "#62976b"
    red = "#bd5b55"
    title_f = font(38, True)
    panel_f = font(24, True)
    label_f = font(17)
    small_f = font(14)
    draw.text((65, 38), "T333 — reciprocal radial breathing on recorded qutrit data", fill=ink, font=title_f)
    draw.text((68, 88), "Real sequential hardware record · three fixed sphere cuts · frozen holdout", fill="#66717d", font=label_f)

    boxes = [(60, 145, 1165, 805), (1235, 145, 2340, 805), (60, 875, 1165, 1605), (1235, 875, 2340, 1605)]

    def panel(box, title):
        draw.rounded_rectangle(box, radius=16, fill="white", outline="#c9cfd6", width=2)
        draw.text((box[0] + 24, box[1] + 18), title, fill=ink, font=panel_f)
        return (box[0] + 92, box[1] + 82, box[2] - 30, box[3] - 78)

    # 1: sampled complex external-vector trajectory.
    plot = panel(boxes[0], "Recorded whole-circle movement vectors")
    arrays = planes[PLANES[0]]
    n = len(arrays["time"])
    start = n // 2
    ids = np.linspace(start, n - 1, 3500, dtype=int)
    amp = arrays["circle_strength"][ids]
    angle = 2.0 * math.pi * arrays["circle_heading"][ids]
    x = amp * np.cos(angle)
    y = amp * np.sin(angle)
    limit = float(np.percentile(np.abs(np.concatenate((x, y))), 99.0))
    x0, y0, x1, y1 = plot
    scale = min((x1 - x0), (y1 - y0)) / (2.2 * max(limit, 1e-9))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    draw.line((x0, cy, x1, cy), fill=grid, width=2)
    draw.line((cx, y0, cx, y1), fill=grid, width=2)
    pts = [(int(cx + xx * scale), int(cy - yy * scale)) for xx, yy in zip(x, y) if abs(xx) <= limit and abs(yy) <= limit]
    for px, py in pts:
        draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=blue)
    draw.text((boxes[0][0] + 330, boxes[0][3] - 48), "external connection cut u", fill=ink, font=label_f)
    draw.text((boxes[0][0] + 14, boxes[0][1] + 335), "perpendicular cut v", fill=ink, font=label_f)

    # 2: cell endpoint medians.
    plot = panel(boxes[1], "Holdout radial endpoints across lags")
    primary = [row for row in cells if row["split"] == "holdout" and row["estimator"] == PRIMARY]
    x0, y0, x1, y1 = plot
    ymin, ymax = 0.35, 2.35
    def py(value):
        return int(y1 - (float(value) - ymin) / (ymax - ymin) * (y1 - y0))
    for val, color, label in [(1.0 / PHI, orange, "1/Phi"), (1.0, grid, "ridge 1"), (PHI, orange, "Phi")]:
        yy = py(val)
        draw.line((x0, yy, x1, yy), fill=color, width=2)
        draw.text((x0 + 4, yy - 20), label, fill=color, font=small_f)
    colors = {PLANES[0]: blue, PLANES[1]: green, PLANES[2]: red}
    for plane_i, plane in enumerate(PLANES):
        rows = [r for r in primary if r["plane"] == plane]
        for lag_i, row in enumerate(rows):
            xx = int(x0 + (lag_i + 0.5 + 0.14 * (plane_i - 1)) / len(LAGS) * (x1 - x0))
            draw.ellipse((xx - 5, py(row["median_contracting"]) - 5, xx + 5, py(row["median_contracting"]) + 5), fill=colors[plane])
            draw.ellipse((xx - 5, py(row["median_expanding"]) - 5, xx + 5, py(row["median_expanding"]) + 5), fill=colors[plane])
    for lag_i, lag in enumerate(LAGS):
        xx = int(x0 + (lag_i + 0.5) / len(LAGS) * (x1 - x0))
        draw.text((xx - 10, y1 + 12), str(lag), fill=ink, font=small_f)
    draw.text((boxes[1][0] + 470, boxes[1][3] - 48), "event lag", fill=ink, font=label_f)

    # 3: quadrant shares.
    plot = panel(boxes[2], "Lag-one complex ARA quadrant shares")
    x0, y0, x1, y1 = plot
    categories = ("contracting_reverse", "contracting_forward", "expanding_reverse", "expanding_forward")
    cat_colors = ("#5c6f91", blue, "#b26c58", orange)
    bar_w = (x1 - x0) / (len(PLANES) * 1.55)
    for pi, row in enumerate(quadrants):
        left = x0 + pi * (x1 - x0) / len(PLANES) + 25
        bottom = y1
        for category, color in zip(categories, cat_colors):
            share = float(row[f"{category}_share"])
            top = bottom - share * (y1 - y0)
            draw.rectangle((left, top, left + bar_w, bottom), fill=color)
            bottom = top
        draw.text((left, y1 + 14), row["plane"].replace("psi", "p"), fill=ink, font=small_f)
    draw.text((boxes[2][0] + 370, boxes[2][3] - 48), "each bar sums to one", fill=ink, font=label_f)

    # 4: temporal-order null.
    plot = panel(boxes[3], "Temporal-order null: lower Phi distance is better")
    x0, y0, x1, y1 = plot
    pooled = np.asarray([float(r["phi_score"]) for r in null_rows if r["plane"] == "pooled"], dtype=float)
    observed = float(results["holdout"]["pooled_primary"]["scores"]["phi"])
    lo = min(float(np.min(pooled)), observed)
    hi = max(float(np.max(pooled)), observed)
    bins = np.linspace(lo, hi, 36)
    hist, edges = np.histogram(pooled, bins=bins)
    max_count = max(int(hist.max()), 1)
    for i, count in enumerate(hist):
        left = x0 + (edges[i] - lo) / max(hi - lo, 1e-12) * (x1 - x0)
        right = x0 + (edges[i + 1] - lo) / max(hi - lo, 1e-12) * (x1 - x0)
        top = y1 - count / max_count * (y1 - y0)
        draw.rectangle((left, top, right, y1), fill="#aeb8c4")
    ox = x0 + (observed - lo) / max(hi - lo, 1e-12) * (x1 - x0)
    draw.line((ox, y0, ox, y1), fill=orange, width=5)
    draw.text((min(int(ox + 8), x1 - 180), y0 + 12), "observed", fill=orange, font=label_f)
    draw.text((boxes[3][0] + 365, boxes[3][3] - 48), "reciprocal-Phi log distance", fill=ink, font=label_f)
    draw.text((x0, y1 + 14), f"p={results['gates']['g4_pooled_empirical_p']:.4f}", fill=ink, font=label_f)

    draw.text((70, 1655), "Source: ETH Zürich recorded trapped-qutrit measurements; T333 uses the frozen Q53 whole-circle external-vector extraction.", fill="#59636e", font=small_f)
    image.save(OUT_FIGURE)


def main() -> None:
    source_hash = sha256(SOURCE)
    protocol_hash = sha256(PROTOCOL)
    event_hash = sha256(EVENTS)
    planes = load_planes()

    source_ok = source_hash == SOURCE_SHA256
    protocol_ok = protocol_hash == PROTOCOL_SHA256
    counts_ok = all(len(planes[name]["time"]) == EXPECTED_EVENTS[name] for name in PLANES)
    arrays_ok = all(
        all(len(value) == EXPECTED_EVENTS[name] for value in arrays.values())
        for name, arrays in planes.items()
    )
    g0_primary = source_ok and protocol_ok and counts_ok and arrays_ok

    cell_rows: list[dict[str, object]] = []
    pools: dict[tuple[str, str, str], np.ndarray] = {}
    for estimator in ESTIMATORS:
        for plane, arrays in planes.items():
            midpoint = len(arrays["time"]) // 2
            for split, start, stop in (
                ("calibration", 0, midpoint),
                ("holdout", midpoint, len(arrays["time"])),
            ):
                pooled: list[np.ndarray] = []
                for lag in LAGS:
                    ratios, _ = lag_values(arrays, estimator, start, stop, lag)
                    metrics = endpoint_metrics(ratios)
                    row: dict[str, object] = {
                        "plane": plane,
                        "estimator": estimator,
                        "split": split,
                        "lag": lag,
                        "n": metrics["n"],
                        "n_contracting": metrics["n_contracting"],
                        "n_expanding": metrics["n_expanding"],
                        "median_contracting": metrics["median_contracting"],
                        "median_expanding": metrics["median_expanding"],
                        "reciprocal_product": metrics["reciprocal_product"],
                        "winner": metrics["winner"],
                        "asymmetric_e_phi_score": metrics["asymmetric_e_phi_score"],
                    }
                    for candidate, score in metrics["scores"].items():
                        row[f"score_{candidate}"] = score
                    cell_rows.append(row)
                    pooled.append(ratios)
                pools[(plane, estimator, split)] = np.concatenate(pooled)

    train_primary = np.concatenate([pools[(plane, PRIMARY, "calibration")] for plane in PLANES])
    holdout_primary = np.concatenate([pools[(plane, PRIMARY, "holdout")] for plane in PLANES])
    fitted_alpha = fit_train_alpha(train_primary)
    train_metrics = endpoint_metrics(train_primary)
    holdout_metrics = endpoint_metrics(holdout_primary)
    fitted_holdout_score = score_alpha(holdout_metrics, fitted_alpha)

    plane_metrics: dict[str, dict[str, object]] = {}
    quadrant_rows: list[dict[str, object]] = []
    for plane, arrays in planes.items():
        midpoint = len(arrays["time"]) // 2
        metrics = endpoint_metrics(pools[(plane, PRIMARY, "holdout")])
        plane_metrics[plane] = metrics
        ratios, delta = lag_values(arrays, PRIMARY, midpoint, len(arrays["time"]), 1)
        quadrant_rows.append(quadrant_record(plane, ratios, delta))

    rng = np.random.default_rng(SHUFFLE_SEED)
    null_rows: list[dict[str, object]] = []
    holdout_indices = {
        plane: [
            lag_indices(
                arrays,
                PRIMARY,
                len(arrays["time"]) // 2,
                len(arrays["time"]),
                lag,
            )
            for lag in LAGS
        ]
        for plane, arrays in planes.items()
    }
    for replicate in range(SHUFFLES):
        pooled_replicate: list[np.ndarray] = []
        for plane, arrays in planes.items():
            midpoint = len(arrays["time"]) // 2
            amp = arrays[f"{PRIMARY}_strength"]
            shuffled = shuffle_amplitudes(
                amp, eligible(arrays, PRIMARY), midpoint, len(amp), rng
            )
            ratios = np.concatenate(
                [shuffled[right] / shuffled[left] for left, right in holdout_indices[plane]]
            )
            metrics = endpoint_metrics(ratios)
            null_rows.append(
                {
                    "replicate": replicate,
                    "plane": plane,
                    "phi_score": metrics["scores"]["phi"],
                    "median_contracting": metrics["median_contracting"],
                    "median_expanding": metrics["median_expanding"],
                }
            )
            pooled_replicate.append(ratios)
        pooled_metrics = endpoint_metrics(np.concatenate(pooled_replicate))
        null_rows.append(
            {
                "replicate": replicate,
                "plane": "pooled",
                "phi_score": pooled_metrics["scores"]["phi"],
                "median_contracting": pooled_metrics["median_contracting"],
                "median_expanding": pooled_metrics["median_expanding"],
            }
        )

    null_summary: dict[str, dict[str, float]] = {}
    for name in (*PLANES, "pooled"):
        scores = np.asarray(
            [float(row["phi_score"]) for row in null_rows if row["plane"] == name],
            dtype=float,
        )
        observed = (
            float(holdout_metrics["scores"]["phi"])
            if name == "pooled"
            else float(plane_metrics[name]["scores"]["phi"])
        )
        null_summary[name] = {
            "observed": observed,
            "p05": float(np.percentile(scores, 5.0)),
            "median": float(np.median(scores)),
            "p95": float(np.percentile(scores, 95.0)),
            "empirical_p": float((1 + int(np.sum(scores <= observed))) / (SHUFFLES + 1)),
        }

    primary_holdout_cells = [
        row
        for row in cell_rows
        if row["split"] == "holdout" and row["estimator"] == PRIMARY
    ]
    phi_wins = sum(row["winner"] == "phi" for row in primary_holdout_cells)
    g1 = all(
        min(float(row[f"{name}_share"]) for name in (
            "contracting_reverse",
            "contracting_forward",
            "expanding_reverse",
            "expanding_forward",
        )) >= 0.05
        for row in quadrant_rows
    )
    g2 = phi_wins >= 15
    plane_absolute: dict[str, dict[str, object]] = {}
    for plane, metrics in plane_metrics.items():
        contraction_rel = float(metrics["median_contracting"]) / (1.0 / PHI) - 1.0
        expansion_rel = float(metrics["median_expanding"]) / PHI - 1.0
        product_error = abs(float(metrics["reciprocal_product"]) - 1.0)
        passed = abs(contraction_rel) <= 0.10 and abs(expansion_rel) <= 0.10 and product_error <= 0.05
        plane_absolute[plane] = {
            "contraction_relative_error": contraction_rel,
            "expansion_relative_error": expansion_rel,
            "reciprocal_product_error": product_error,
            "pass": passed,
        }
    g3_passes = sum(bool(item["pass"]) for item in plane_absolute.values())
    g3 = g3_passes >= 2
    g4_plane_passes = sum(
        summary["observed"] < summary["p05"]
        for plane, summary in null_summary.items()
        if plane != "pooled"
    )
    g4_pooled_p = null_summary["pooled"]["empirical_p"]
    g4 = g4_plane_passes >= 2 and g4_pooled_p < 0.05
    g5 = float(holdout_metrics["scores"]["phi"]) <= fitted_holdout_score

    sensitivity: dict[str, object] = {}
    for estimator in ESTIMATORS:
        all_ratios = np.concatenate([pools[(plane, estimator, "holdout")] for plane in PLANES])
        metrics = endpoint_metrics(all_ratios)
        wins = sum(
            row["winner"] == "phi"
            for row in cell_rows
            if row["split"] == "holdout" and row["estimator"] == estimator
        )
        sensitivity[estimator] = {"pooled": metrics, "phi_wins_of_21": wins}

    substantive = {"g2": g2, "g3": g3, "g4": g4, "g5": g5}
    if not g0_primary or any(int(row["valid_steps"]) < 1000 for row in quadrant_rows):
        verdict = "INVALID / NO TEST"
    elif g1 and all(substantive.values()):
        verdict = "SUPPORTED ON THIS RECORDED EXTERNAL VECTOR"
    elif g1 and sum(substantive.values()) >= 2:
        verdict = "PARTIAL / COORDINATE ONLY"
    else:
        verdict = "NOT SUPPORTED"

    results: dict[str, object] = {
        "test": "T333 recorded-qutrit reciprocal radial breathing",
        "date": "2026-08-03",
        "verdict_before_independent_validation": verdict,
        "source": {
            "path": str(SOURCE),
            "sha256": source_hash,
            "expected_sha256": SOURCE_SHA256,
            "q53_events_path": str(EVENTS),
            "q53_events_sha256": event_hash,
            "counts": {plane: len(arrays["time"]) for plane, arrays in planes.items()},
        },
        "protocol": {"path": str(PROTOCOL), "sha256": protocol_hash, "expected_sha256": PROTOCOL_SHA256},
        "configuration": {
            "primary_estimator": PRIMARY,
            "lags": LAGS,
            "max_gap": MAX_GAP,
            "min_strength": MIN_STRENGTH,
            "max_residual": MAX_RESIDUAL,
            "shuffles": SHUFFLES,
            "shuffle_seed": SHUFFLE_SEED,
            "candidates": CANDIDATES,
        },
        "calibration": {
            "fitted_reciprocal_alpha": fitted_alpha,
            "pooled_primary": train_metrics,
        },
        "holdout": {
            "pooled_primary": holdout_metrics,
            "fitted_alpha_score": fitted_holdout_score,
            "planes": plane_metrics,
            "plane_absolute_checks": plane_absolute,
            "sensitivity": sensitivity,
        },
        "quadrants": quadrant_rows,
        "temporal_null": null_summary,
        "gates": {
            "g0_primary_source_and_implementation": g0_primary,
            "g1_four_quadrants": g1,
            "g2_phi_wins": g2,
            "g2_phi_wins_of_21": phi_wins,
            "g3_absolute_endpoints": g3,
            "g3_plane_passes_of_3": g3_passes,
            "g4_temporal_order": g4,
            "g4_plane_passes_of_3": g4_plane_passes,
            "g4_pooled_empirical_p": g4_pooled_p,
            "g5_beats_train_fitted": g5,
        },
        "artifacts": {
            "cells": OUT_CELLS.name,
            "quadrants": OUT_QUADRANTS.name,
            "nulls": OUT_NULLS.name,
            "figure": OUT_FIGURE.name,
        },
        "boundary": "New exact radial question on a previously opened external archive; second-archive replication remains required.",
    }

    write_csv(OUT_CELLS, cell_rows)
    write_csv(OUT_QUADRANTS, quadrant_rows)
    write_csv(OUT_NULLS, null_rows)
    OUT_RESULTS.write_text(json.dumps(as_native(results), indent=2) + "\n", encoding="utf-8")
    make_figure(planes, cell_rows, quadrant_rows, null_rows, results)

    print(json.dumps({
        "verdict": verdict,
        "gates": results["gates"],
        "fitted_alpha": fitted_alpha,
        "holdout_contracting": holdout_metrics["median_contracting"],
        "holdout_expanding": holdout_metrics["median_expanding"],
        "holdout_phi_score": holdout_metrics["scores"]["phi"],
        "holdout_fitted_score": fitted_holdout_score,
    }, indent=2))


if __name__ == "__main__":
    main()
