from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from run_vertical_ara_dyadic_chain import Root, extract_roots
from run_vertical_ara_spiral_scale import complex_parent_vectors, eligible_vectors


BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "source_data"
RESULTS = BASE / "results"
PROTOCOL = BASE / "T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_HASH = "E827F7907FBE7B12699EA035453A60A3AC7DF5F4BA7A350B5686051D87C0023C"
DATA_ZIP_HASH = "11F050285C740CCA7B4248E64F24304317E0563E61D39DC5A9F2A7F39BA86BC0"
SOURCE_MANIFEST_HASH = "D712AA9BB5935C400AE76DA50B93DB97F5FEFD1E1E8814E5DC8322BD66076C7F"

OUT_STEM = "T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT"
PRIMARY_CARRIER = 2.0
SHUFFLES = 500
BOOTSTRAPS = 5000
SEED = 20260803
BOUNDARY_EPS = 1e-12

PHI = (1.0 + math.sqrt(5.0)) / 2.0
FIXED_CANDIDATES = {
    "plastic": 1.324717957244746,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "t333_qutrit": 1.809114052291864,
    "two": 2.0,
    "e": math.e,
}
SPLITS = ("calibration", "evaluation", "holdout")
LEVELS = (0, 1, 2, 3)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def source_manifest_hash() -> str:
    lines = []
    for path in sorted(SOURCE.glob("*.csv")):
        lines.append(f"{path.name}:{sha256(path)}")
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest().upper()


def wrap_angle(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def quadrant(log_u: float, delta: float) -> str:
    if abs(log_u) <= BOUNDARY_EPS or abs(delta) <= BOUNDARY_EPS:
        return "boundary"
    radial = "expanding" if log_u > 0 else "contracting"
    direction = "forward" if delta > 0 else "reverse"
    return f"{radial}_{direction}"


def root_key(root: Root) -> str:
    return f"{root.video}:{root.track_id}:{root.start_frame}"


def event_rows_for_vectors(
    root: Root,
    vectors: list[complex],
    carrier: float = PRIMARY_CARRIER,
    source_kind: str = "observed",
) -> list[dict]:
    rows = []
    for level in LEVELS:
        q = vectors[level + 1] / vectors[level]
        scale = abs(q)
        delta = wrap_angle(math.atan2(q.imag, q.real))
        u = scale / carrier
        log_u = math.log(u)
        rows.append(
            {
                "split": root.split,
                "video": root.video,
                "file": root.file,
                "root_key": root_key(root),
                "track_id": root.track_id,
                "start_frame": root.start_frame,
                "level": level,
                "child_frames": 2 ** (level + 1),
                "parent_frames": 2 ** (level + 2),
                "source_kind": source_kind,
                "raw_scale": scale,
                "carrier": carrier,
                "u": u,
                "log_u": log_u,
                "delta_rad": delta,
                "delta_deg": math.degrees(delta),
                "quadrant": quadrant(log_u, delta),
                "raw_quadrant": quadrant(math.log(scale), delta),
            }
        )
    return rows


def build_observed_roots() -> tuple[list[tuple[Root, list[complex]]], list[dict], dict]:
    roots, extraction_diagnostics = extract_roots(SOURCE)
    retained: list[tuple[Root, list[complex]]] = []
    rows: list[dict] = []
    exclusions = defaultdict(int)
    for root in roots:
        vectors = complex_parent_vectors(root.steps)
        if not eligible_vectors(vectors):
            exclusions[f"{root.split}_spiral_resolution_exclusions"] += 1
            continue
        retained.append((root, vectors))
        rows.extend(event_rows_for_vectors(root, vectors))
    diagnostics = {
        "source_extraction": extraction_diagnostics,
        "t334_exclusions": dict(exclusions),
        "retained_roots": {
            split: sum(root.split == split for root, _ in retained) for split in SPLITS
        },
        "retained_events": {
            split: sum(row["split"] == split for row in rows) for split in SPLITS
        },
    }
    return retained, rows, diagnostics


def endpoint_record(rows: list[dict], carrier: float, alpha: float | None = None) -> dict:
    values = np.asarray([float(row["raw_scale"]) / carrier for row in rows], dtype=float)
    lower = values[values < 1.0 - BOUNDARY_EPS]
    upper = values[values > 1.0 + BOUNDARY_EPS]
    boundary_count = int(values.size - lower.size - upper.size)
    if lower.size == 0 or upper.size == 0:
        return {
            "count": int(values.size),
            "lower_count": int(lower.size),
            "upper_count": int(upper.size),
            "boundary_count": boundary_count,
            "u_minus": float("nan"),
            "u_plus": float("nan"),
            "product": float("nan"),
            "implied_alpha": float("nan"),
            "midpoint_log": float("nan"),
            "score": None if alpha is None else float("nan"),
        }
    log_minus = float(np.median(np.log(lower)))
    log_plus = float(np.median(np.log(upper)))
    u_minus = float(np.median(lower))
    u_plus = float(np.median(upper))
    implied_alpha = math.exp((log_plus - log_minus) / 2.0)
    score = None
    if alpha is not None:
        score = 0.5 * (abs(log_minus + math.log(alpha)) + abs(log_plus - math.log(alpha)))
    return {
        "count": int(values.size),
        "lower_count": int(lower.size),
        "upper_count": int(upper.size),
        "boundary_count": boundary_count,
        "u_minus": u_minus,
        "u_plus": u_plus,
        "product": u_minus * u_plus,
        "implied_alpha": implied_alpha,
        "midpoint_log": 0.5 * (log_minus + log_plus),
        "score": score,
    }


def candidate_scores(record: dict, candidates: dict[str, float]) -> dict[str, float]:
    if not math.isfinite(float(record["u_minus"])):
        return {name: float("nan") for name in candidates}
    log_minus = math.log(float(record["u_minus"]))
    log_plus = math.log(float(record["u_plus"]))
    return {
        name: 0.5 * (abs(log_minus + math.log(alpha)) + abs(log_plus - math.log(alpha)))
        for name, alpha in candidates.items()
    }


def build_cell_table(rows: list[dict], carrier: float, alpha_cal: float, carrier_name: str) -> list[dict]:
    candidates = dict(FIXED_CANDIDATES)
    candidates["fitted_calibration"] = alpha_cal
    cells = []
    for split in SPLITS:
        split_rows = [row for row in rows if row["split"] == split]
        for level_name, level in [("pooled", None), *((str(level), level) for level in LEVELS)]:
            subset = split_rows if level is None else [row for row in split_rows if row["level"] == level]
            record = endpoint_record(subset, carrier)
            scores = candidate_scores(record, candidates)
            finite = {name: value for name, value in scores.items() if math.isfinite(value)}
            winner = min(finite, key=finite.get) if finite else "none"
            cell = {
                "carrier_name": carrier_name,
                "carrier": carrier,
                "split": split,
                "level": level_name,
                **record,
                "winner": winner,
            }
            for name, value in scores.items():
                cell[f"score_{name}"] = value
            cells.append(cell)
    return cells


def quadrant_table(rows: list[dict], carrier: float, carrier_name: str) -> list[dict]:
    names = (
        "contracting_reverse",
        "contracting_forward",
        "expanding_reverse",
        "expanding_forward",
        "boundary",
    )
    output = []
    for split in SPLITS:
        subset = [row for row in rows if row["split"] == split]
        counts = {name: 0 for name in names}
        for row in subset:
            log_u = math.log(float(row["raw_scale"]) / carrier)
            label = quadrant(log_u, float(row["delta_rad"]))
            counts[label] += 1
        denominator = len(subset) - counts["boundary"]
        for name in names:
            output.append(
                {
                    "carrier_name": carrier_name,
                    "carrier": carrier,
                    "split": split,
                    "quadrant": name,
                    "count": counts[name],
                    "share_nonboundary": counts[name] / denominator if denominator and name != "boundary" else 0.0,
                    "events": len(subset),
                }
            )
    return output


def attach_broken_roots(retained: list[tuple[Root, list[complex]]]) -> list[dict]:
    by_video: dict[str, list[tuple[Root, list[complex]]]] = defaultdict(list)
    for item in retained:
        by_video[item[0].video].append(item)
    rows = []
    for video, group in by_video.items():
        group.sort(key=lambda item: (item[0].start_frame, item[0].track_id, item[0].segment_index))
        if len(group) < 2:
            continue
        for index, (root, vectors) in enumerate(group):
            partner_vectors = group[(index + 1) % len(group)][1]
            for level in LEVELS:
                q = partner_vectors[level + 1] / vectors[level]
                scale = abs(q)
                delta = wrap_angle(math.atan2(q.imag, q.real))
                rows.append(
                    {
                        "split": root.split,
                        "video": video,
                        "root_key": root_key(root),
                        "level": level,
                        "raw_scale": scale,
                        "delta_rad": delta,
                    }
                )
    return rows


def score_for_rows(rows: list[dict], carrier: float, alpha: float) -> float:
    return float(endpoint_record(rows, carrier, alpha)["score"])


def cluster_bootstrap_comparison(
    observed: list[dict], broken: list[dict], split: str, carrier: float, alpha: float, seed_offset: int
) -> dict:
    obs_by_video: dict[str, list[dict]] = defaultdict(list)
    broken_by_video: dict[str, list[dict]] = defaultdict(list)
    for row in observed:
        if row["split"] == split:
            obs_by_video[row["video"]].append(row)
    for row in broken:
        if row["split"] == split:
            broken_by_video[row["video"]].append(row)
    videos = sorted(set(obs_by_video) & set(broken_by_video))
    observed_score = score_for_rows([row for video in videos for row in obs_by_video[video]], carrier, alpha)
    broken_score = score_for_rows([row for video in videos for row in broken_by_video[video]], carrier, alpha)
    rng = np.random.default_rng(SEED + seed_offset)
    draws = []
    for _ in range(BOOTSTRAPS):
        chosen = rng.integers(0, len(videos), size=len(videos))
        obs_rows = []
        broken_rows = []
        for position in chosen:
            video = videos[int(position)]
            obs_rows.extend(obs_by_video[video])
            broken_rows.extend(broken_by_video[video])
        draws.append(score_for_rows(obs_rows, carrier, alpha) - score_for_rows(broken_rows, carrier, alpha))
    array = np.asarray(draws, dtype=float)
    return {
        "videos": len(videos),
        "observed_score": observed_score,
        "broken_score": broken_score,
        "observed_minus_broken": observed_score - broken_score,
        "ci_low": float(np.quantile(array, 0.025)),
        "ci_high": float(np.quantile(array, 0.975)),
    }


def cluster_bootstrap_product(rows: list[dict], split: str, carrier: float, seed_offset: int) -> dict:
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["split"] == split:
            by_video[row["video"]].append(row)
    videos = sorted(by_video)
    point = float(endpoint_record([row for video in videos for row in by_video[video]], carrier)["product"])
    rng = np.random.default_rng(SEED + seed_offset)
    draws = []
    for _ in range(BOOTSTRAPS):
        chosen = rng.integers(0, len(videos), size=len(videos))
        sampled = []
        for position in chosen:
            sampled.extend(by_video[videos[int(position)]])
        draws.append(float(endpoint_record(sampled, carrier)["product"]))
    array = np.asarray(draws, dtype=float)
    return {
        "product": point,
        "ci_low": float(np.quantile(array, 0.025)),
        "ci_high": float(np.quantile(array, 0.975)),
        "videos": len(videos),
    }


def shuffled_steps(steps: list[tuple[float, float]], key: str, draw: int) -> list[tuple[float, float]]:
    digest = hashlib.sha256(f"{SEED}:{draw}:{key}".encode("utf-8")).digest()
    rng = random.Random(int.from_bytes(digest[:8], "big"))
    indices = list(range(len(steps)))
    rng.shuffle(indices)
    return [steps[index] for index in indices]


def temporal_nulls(
    retained: list[tuple[Root, list[complex]]], alpha_cal: float
) -> tuple[list[dict], dict]:
    observed_scores = {}
    observed_rows = [row for root, vectors in retained for row in event_rows_for_vectors(root, vectors)]
    for split in ("evaluation", "holdout"):
        observed_scores[split] = score_for_rows(
            [row for row in observed_rows if row["split"] == split], PRIMARY_CARRIER, alpha_cal
        )

    null_rows = []
    incomplete_by_split = defaultdict(int)
    for draw in range(SHUFFLES):
        rows_by_split: dict[str, list[dict]] = defaultdict(list)
        for root, _ in retained:
            if root.split not in ("evaluation", "holdout"):
                continue
            permuted = shuffled_steps(root.steps, root_key(root), draw)
            vectors = complex_parent_vectors(permuted)
            if not eligible_vectors(vectors):
                incomplete_by_split[root.split] += 1
                continue
            rows_by_split[root.split].extend(event_rows_for_vectors(root, vectors, source_kind="shuffle"))
        for split in ("evaluation", "holdout"):
            score = score_for_rows(rows_by_split[split], PRIMARY_CARRIER, alpha_cal)
            null_rows.append(
                {
                    "draw": draw,
                    "split": split,
                    "score": score,
                    "events": len(rows_by_split[split]),
                    "observed_score": observed_scores[split],
                }
            )

    summary = {}
    for split in ("evaluation", "holdout"):
        values = np.asarray([row["score"] for row in null_rows if row["split"] == split], dtype=float)
        observed = observed_scores[split]
        summary[split] = {
            "observed_score": observed,
            "null_mean": float(np.mean(values)),
            "null_p05": float(np.quantile(values, 0.05)),
            "null_median": float(np.median(values)),
            "null_p95": float(np.quantile(values, 0.95)),
            "nulls_as_close_or_closer": int(np.sum(values <= observed)),
            "empirical_p": float((1 + np.sum(values <= observed)) / (SHUFFLES + 1)),
            "incomplete_root_controls_total": int(incomplete_by_split[split]),
        }
    return null_rows, summary


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows for {path}")
    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def json_clean(value):
    if isinstance(value, dict):
        return {key: json_clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_clean(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, np.integer):
        return int(value)
    return value


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_figure(
    observed_rows: list[dict], cells: list[dict], quadrants: list[dict], null_rows: list[dict],
    alpha_cal: float, output: Path
) -> None:
    image = Image.new("RGB", (2400, 1700), "#f7f8fa")
    draw = ImageDraw.Draw(image)
    ink, grid = "#20262e", "#d8dde3"
    blue, red, orange = "#4777b8", "#bd5b55", "#d9972f"
    green = "#62976b"
    title_f, panel_f, label_f, small_f = font(38, True), font(24, True), font(17), font(14)
    draw.text((65, 38), "T334 — bubble octave-relative complex ARA breathing", fill=ink, font=title_f)
    draw.text((68, 88), "Recorded bubble trajectories · carrier 2 retained · frozen evaluation + holdout", fill="#66717d", font=label_f)
    boxes = [(60, 145, 1165, 805), (1235, 145, 2340, 805), (60, 875, 1165, 1605), (1235, 875, 2340, 1605)]

    def panel(box, title):
        draw.rounded_rectangle(box, radius=16, fill="white", outline="#c9cfd6", width=2)
        draw.text((box[0] + 24, box[1] + 18), title, fill=ink, font=panel_f)
        return (box[0] + 92, box[1] + 88, box[2] - 35, box[3] - 82)

    # Panel 1: polar residual plane. Unit circle is the retained octave carrier.
    x0, y0, x1, y1 = panel(boxes[0], "Evaluation residual movement plane")
    eval_rows = [row for row in observed_rows if row["split"] == "evaluation"]
    sample = eval_rows[:: max(1, len(eval_rows) // 4500)]
    xs = np.asarray([row["u"] * math.cos(row["delta_rad"]) for row in sample])
    ys = np.asarray([row["u"] * math.sin(row["delta_rad"]) for row in sample])
    limit = max(1.15, float(np.quantile(np.abs(np.concatenate((xs, ys))), 0.97)))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    scale = min(x1 - x0, y1 - y0) / (2.15 * limit)
    draw.line((x0, cy, x1, cy), fill=grid, width=2)
    draw.line((cx, y0, cx, y1), fill=grid, width=2)
    for xx, yy in zip(xs, ys):
        if abs(xx) <= limit and abs(yy) <= limit:
            px, py = int(cx + xx * scale), int(cy - yy * scale)
            draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=blue)
    radius = scale
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=orange, width=3)
    draw.text((x0 + 8, y0 + 8), "orange circle: u=1 octave-relative ridge", fill=orange, font=small_f)
    draw.text((boxes[0][0] + 365, boxes[0][3] - 48), "radial breath × cos(turn)", fill=ink, font=label_f)
    draw.text((boxes[0][0] + 14, boxes[0][1] + 340), "radial breath × sin(turn)", fill=ink, font=small_f)

    # Panel 2: endpoint medians on a log coordinate.
    x0, y0, x1, y1 = panel(boxes[1], "Octave-relative radial endpoints")
    subset_by_split = {}
    all_values = [1.0 / alpha_cal, alpha_cal, 1.0 / PHI, PHI]
    for split in ("evaluation", "holdout"):
        subset = [row for row in cells if row["carrier_name"] == "primary_two" and row["split"] == split]
        subset.sort(key=lambda row: -1 if row["level"] == "pooled" else int(row["level"]))
        subset_by_split[split] = subset
        all_values.extend([float(row["u_minus"]) for row in subset])
        all_values.extend([float(row["u_plus"]) for row in subset])
    log_lo, log_hi = math.log(min(all_values) * 0.88), math.log(max(all_values) * 1.12)

    def py(value):
        return int(y1 - (math.log(float(value)) - log_lo) / (log_hi - log_lo) * (y1 - y0))

    for value, color, label, width in [
        (1.0 / alpha_cal, ink, "calibration reciprocal", 2),
        (alpha_cal, ink, "", 2),
        (1.0 / PHI, orange, "1/Phi · Phi", 2),
        (PHI, orange, "", 2),
        (1.0, grid, "ridge 1", 2),
    ]:
        yy = py(value)
        draw.line((x0, yy, x1, yy), fill=color, width=width)
        if label:
            draw.text((x0 + 4, yy - 20), label, fill=color, font=small_f)
    colors, offsets = {"evaluation": blue, "holdout": red}, {"evaluation": -10, "holdout": 10}
    labels = ["pooled", "2→4", "4→8", "8→16", "16→32"]
    for split in ("evaluation", "holdout"):
        for index, row in enumerate(subset_by_split[split]):
            xx = int(x0 + (index + 0.5) / 5 * (x1 - x0)) + offsets[split]
            yy_minus, yy_plus = py(row["u_minus"]), py(row["u_plus"])
            draw.ellipse((xx - 5, yy_minus - 5, xx + 5, yy_minus + 5), fill=colors[split])
            draw.rectangle((xx - 5, yy_plus - 5, xx + 5, yy_plus + 5), fill=colors[split])
    for index, label in enumerate(labels):
        xx = int(x0 + (index + 0.5) / 5 * (x1 - x0))
        draw.text((xx - 28, y1 + 14), label, fill=ink, font=small_f)
    draw.text((x1 - 250, y0 + 8), "blue evaluation · red holdout", fill=ink, font=small_f)

    # Panel 3: quadrant shares.
    x0, y0, x1, y1 = panel(boxes[2], "Four octave-relative complex quadrants")
    order = ["contracting_reverse", "contracting_forward", "expanding_reverse", "expanding_forward"]
    palette = ["#5f7396", blue, "#b56e58", orange]
    bar_width = 250
    for split_index, split in enumerate(("evaluation", "holdout")):
        left = x0 + 170 + split_index * 430
        bottom = y1
        for label, color in zip(order, palette):
            row = next(item for item in quadrants if item["carrier_name"] == "primary_two" and item["split"] == split and item["quadrant"] == label)
            height = float(row["share_nonboundary"]) * (y1 - y0)
            top = bottom - height
            draw.rectangle((left, top, left + bar_width, bottom), fill=color)
            bottom = top
        draw.text((left + 65, y1 + 14), split, fill=ink, font=label_f)
    for index, (label, color) in enumerate(zip(order, palette)):
        lx = x0 + (index % 2) * 430
        ly = y0 + 15 + (index // 2) * 30
        draw.rectangle((lx, ly, lx + 18, ly + 18), fill=color)
        draw.text((lx + 27, ly - 2), label.replace("_", " "), fill=ink, font=small_f)
    draw.text((boxes[2][0] + 400, boxes[2][3] - 48), "each bar sums to one", fill=ink, font=label_f)

    # Panel 4: temporal nulls.
    x0, y0, x1, y1 = panel(boxes[3], "Recorded order versus step-order shuffles")
    all_scores = [float(row["score"]) for row in null_rows]
    observed_values = [float(next(row["observed_score"] for row in null_rows if row["split"] == split)) for split in ("evaluation", "holdout")]
    lo, hi = min(all_scores + observed_values), max(all_scores + observed_values)
    bins = np.linspace(lo, hi, 32)
    for split, color in (("evaluation", blue), ("holdout", red)):
        values = np.asarray([float(row["score"]) for row in null_rows if row["split"] == split])
        hist, edges = np.histogram(values, bins=bins)
        max_count = max(int(hist.max()), 1)
        for index, count in enumerate(hist):
            left = x0 + (edges[index] - lo) / max(hi - lo, 1e-12) * (x1 - x0)
            right = x0 + (edges[index + 1] - lo) / max(hi - lo, 1e-12) * (x1 - x0)
            top = y1 - count / max_count * (y1 - y0)
            draw.rectangle((left, top, right, y1), fill=color)
        observed = float(next(row["observed_score"] for row in null_rows if row["split"] == split))
        ox = x0 + (observed - lo) / max(hi - lo, 1e-12) * (x1 - x0)
        draw.line((ox, y0, ox, y1), fill=color, width=5)
    draw.text((x0 + 8, y0 + 8), "vertical lines: recorded evaluation (blue), holdout (red)", fill=ink, font=small_f)
    draw.text((boxes[3][0] + 210, boxes[3][3] - 48), "score to calibration-fitted reciprocal breath (lower is better)", fill=ink, font=small_f)

    draw.text((70, 1655), "Source: Pandey et al., Zenodo 10.5281/zenodo.15102957 · no smoothing or Fourier processing", fill="#59636e", font=small_f)
    image.save(output)


def main() -> None:
    if sha256(PROTOCOL) != PROTOCOL_HASH:
        raise SystemExit("Frozen protocol hash mismatch")
    if sha256(BASE / "data.zip") != DATA_ZIP_HASH:
        raise SystemExit("data.zip hash mismatch")
    if source_manifest_hash() != SOURCE_MANIFEST_HASH:
        raise SystemExit("source manifest hash mismatch")

    retained, observed_rows, diagnostics = build_observed_roots()
    calibration_rows = [row for row in observed_rows if row["split"] == "calibration"]
    carrier_cal = math.exp(statistics.median(math.log(float(row["raw_scale"])) for row in calibration_rows))
    calibration_primary = endpoint_record(calibration_rows, PRIMARY_CARRIER)
    alpha_cal = float(calibration_primary["implied_alpha"])

    primary_cells = build_cell_table(observed_rows, PRIMARY_CARRIER, alpha_cal, "primary_two")
    sensitivity_cells = build_cell_table(observed_rows, carrier_cal, alpha_cal, "sensitivity_calibration_carrier")
    cells = primary_cells + sensitivity_cells
    quadrants = quadrant_table(observed_rows, PRIMARY_CARRIER, "primary_two")
    quadrants += quadrant_table(observed_rows, carrier_cal, "sensitivity_calibration_carrier")

    broken_rows = attach_broken_roots(retained)
    identity_control = {
        split: cluster_bootstrap_comparison(observed_rows, broken_rows, split, PRIMARY_CARRIER, alpha_cal, 100 + index)
        for index, split in enumerate(("evaluation", "holdout"))
    }
    product_bootstrap = {
        split: cluster_bootstrap_product(observed_rows, split, PRIMARY_CARRIER, 200 + index)
        for index, split in enumerate(("evaluation", "holdout"))
    }
    null_rows, temporal_null = temporal_nulls(retained, alpha_cal)

    primary_lookup = {(row["split"], row["level"]): row for row in primary_cells}
    quadrant_lookup = {
        (row["split"], row["quadrant"]): row
        for row in quadrants
        if row["carrier_name"] == "primary_two"
    }
    core_quadrants = (
        "contracting_reverse",
        "contracting_forward",
        "expanding_reverse",
        "expanding_forward",
    )
    g1 = all(
        quadrant_lookup[(split, name)]["share_nonboundary"] >= 0.05
        for split in ("evaluation", "holdout") for name in core_quadrants
    )
    g2 = True
    for split in ("evaluation", "holdout"):
        pooled_product = float(primary_lookup[(split, "pooled")]["product"])
        level_products = [float(primary_lookup[(split, str(level))]["product"]) for level in LEVELS]
        g2 = g2 and 0.90 <= pooled_product <= 1.10 and sum(0.85 <= value <= 1.15 for value in level_products) >= 3

    g3 = True
    for split in ("evaluation", "holdout"):
        pooled = primary_lookup[(split, "pooled")]
        fitted_score = float(pooled["score_fitted_calibration"])
        g3 = g3 and all(fitted_score < float(pooled[f"score_{name}"]) for name in FIXED_CANDIDATES)
        g3 = g3 and abs(math.log(float(pooled["implied_alpha"]) / alpha_cal)) <= math.log(1.10)

    g4 = all(temporal_null[split]["empirical_p"] <= 0.05 for split in ("evaluation", "holdout"))
    g5 = (
        identity_control["evaluation"]["ci_high"] < 0
        and identity_control["holdout"]["observed_minus_broken"] < 0
    )

    fixed_winners = {
        split: min(FIXED_CANDIDATES, key=lambda name: primary_lookup[(split, "pooled")][f"score_{name}"])
        for split in ("evaluation", "holdout")
    }
    results = {
        "test": "T334 bubble octave-relative irrationality quadrant",
        "date": "2026-08-03",
        "protocol": PROTOCOL.name,
        "protocol_sha256": PROTOCOL_HASH,
        "data_zip_sha256": DATA_ZIP_HASH,
        "source_manifest_sha256": SOURCE_MANIFEST_HASH,
        "source": "Pandey et al., Zenodo 10.5281/zenodo.15102957",
        "primary_carrier": PRIMARY_CARRIER,
        "calibration_sensitivity_carrier": carrier_cal,
        "calibration_fitted_reciprocal_alpha": alpha_cal,
        "fixed_candidates": FIXED_CANDIDATES,
        "diagnostics": diagnostics,
        "primary_pooled": {
            split: primary_lookup[(split, "pooled")] for split in SPLITS
        },
        "primary_level_products": {
            split: {str(level): primary_lookup[(split, str(level))]["product"] for level in LEVELS}
            for split in SPLITS
        },
        "fixed_candidate_pooled_winners": fixed_winners,
        "quadrant_shares": {
            split: {
                name: quadrant_lookup[(split, name)]["share_nonboundary"] for name in core_quadrants
            }
            for split in SPLITS
        },
        "reciprocal_product_bootstrap": product_bootstrap,
        "temporal_null": temporal_null,
        "identity_control": identity_control,
        "gates": {
            "G0_integrity": "pending independent validator",
            "G1_four_quadrants": g1,
            "G2_reciprocal_closure": g2,
            "G3_calibration_transfer": g3,
            "G4_recorded_order": g4,
            "G5_intact_identity": g5,
        },
        "verdict": {
            "complex_residual_quadrant_supported": g1,
            "octave_relative_reciprocal_breath_supported": g1 and g2,
            "stable_ordered_identity_preserving_breath_supported": g1 and g2 and g3 and g4 and g5,
            "universal_phi_endpoint_supported": fixed_winners["evaluation"] == "phi" and fixed_winners["holdout"] == "phi",
            "universal_t333_endpoint_supported": fixed_winners["evaluation"] == "t333_qutrit" and fixed_winners["holdout"] == "t333_qutrit",
        },
        "boundaries": [
            "The archive was already opened for earlier Vertical-ARA and Phi tests.",
            "The primary residual divides cumulative centroid scale by the pre-existing octave carrier 2.",
            "A reciprocal product near one is not sufficient without transfer and order/identity controls.",
            "The result does not establish a universal cosmic Time wave.",
        ],
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    event_path = RESULTS / f"{OUT_STEM}_EVENTS.csv"
    cell_path = RESULTS / f"{OUT_STEM}_CELLS.csv"
    quadrant_path = RESULTS / f"{OUT_STEM}_QUADRANTS.csv"
    null_path = RESULTS / f"{OUT_STEM}_NULLS.csv"
    result_path = BASE / f"{OUT_STEM}_RESULTS.json"
    figure_path = BASE / f"{OUT_STEM}_FIGURE.png"

    write_csv(event_path, observed_rows)
    write_csv(cell_path, cells)
    write_csv(quadrant_path, quadrants)
    write_csv(null_path, null_rows)
    result_path.write_text(json.dumps(json_clean(results), indent=2, allow_nan=False), encoding="utf-8")
    make_figure(observed_rows, cells, quadrants, null_rows, alpha_cal, figure_path)

    print(json.dumps({
        "retained_roots": diagnostics["retained_roots"],
        "retained_events": diagnostics["retained_events"],
        "carrier_cal": carrier_cal,
        "alpha_cal": alpha_cal,
        "primary_pooled": results["primary_pooled"],
        "fixed_winners": fixed_winners,
        "temporal_null": temporal_null,
        "identity_control": identity_control,
        "gates": results["gates"],
        "verdict": results["verdict"],
    }, indent=2))


if __name__ == "__main__":
    main()
