#!/usr/bin/env python3
"""Run the frozen T328 Phi circle-train test on raw bubble trajectories."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from bubble_lineage import Bubble, load_run


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "source_data"
PROTOCOL = HERE / "T328_PHI_CIRCLE_TRAIN_BUBBLE_PROTOCOL_v1_FROZEN.md"
PREFIX = "T328_PHI_CIRCLE_TRAIN_BUBBLES"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_DELTA = 2.0 / PHI
ROOT_STEPS = 32
MIN_STEP_M = 0.0005
N_NULL = 10_000
BOOTSTRAPS = 5_000
SEED = 20260802
LAGS = (2, 3, 5, 8, 13, 21)

# All nonzero values use the same positive/major orientation as +2/phi.
CANDIDATES = OrderedDict(
    [
        ("persistence", 0.0),
        ("ridge", 1.0),
        ("silver_conjugate", 2.0 - 2.0 * (math.sqrt(2.0) - 1.0)),
        ("two_fifths", 2.0 - 4.0 / 5.0),
        ("phi", PHI_DELTA),
        ("fibonacci_8_21", 2.0 - 16.0 / 21.0),
        ("three_eighths", 2.0 - 3.0 / 4.0),
        ("one_over_e", 2.0 - 2.0 / math.e),
        ("one_third", 2.0 - 2.0 / 3.0),
    ]
)


@dataclass
class Root:
    split: str
    video: str
    file: str
    track_id: int
    segment_index: int
    start_frame: int
    points: np.ndarray
    steps: np.ndarray
    headings: np.ndarray

    @property
    def key(self) -> str:
        return f"{self.video}:{self.track_id}:{self.start_frame}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def source_sha256(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest().upper()


def split_for_video(video: str) -> str:
    number = int(video[1:])
    if number <= 7:
        return "calibration"
    if number <= 28:
        return "evaluation"
    return "holdout"


def contiguous_segments(track: dict[int, Bubble]) -> list[list[Bubble]]:
    frames = sorted(track)
    if not frames:
        return []
    result: list[list[Bubble]] = []
    current = [track[frames[0]]]
    for previous, frame in zip(frames, frames[1:]):
        if frame == previous + 1:
            current.append(track[frame])
        else:
            result.append(current)
            current = [track[frame]]
    result.append(current)
    return result


def headings_from_steps(steps: np.ndarray) -> np.ndarray:
    return np.mod(np.arctan2(steps[:, 1], steps[:, 0]) / math.pi, 2.0)


def d2(left, right):
    difference = np.abs(np.asarray(left, dtype=float) - np.asarray(right, dtype=float))
    return np.minimum(difference, 2.0 - difference)


def score_heading_path(headings: np.ndarray, delta: float) -> dict[str, float]:
    turns = np.mod(np.diff(headings), 2.0)
    local_positive = float(np.median(d2(turns, delta)))
    local_negative = float(np.median(d2(turns, (-delta) % 2.0)))

    horizons = np.arange(1, len(headings), dtype=float)
    positive_prediction = np.mod(headings[0] + horizons * delta, 2.0)
    negative_prediction = np.mod(headings[0] - horizons * delta, 2.0)
    parent_positive = float(np.median(d2(headings[1:], positive_prediction)))
    parent_negative = float(np.median(d2(headings[1:], negative_prediction)))

    return {
        "local_directed": local_positive,
        "parent_directed": parent_positive,
        "local_reverse_orientation": local_negative,
        "parent_reverse_orientation": parent_negative,
        "local_reversible": min(local_positive, local_negative),
        "parent_reversible": min(parent_positive, parent_negative),
        "local_reversible_sign": 1.0 if local_positive <= local_negative else -1.0,
        "parent_reversible_sign": 1.0 if parent_positive <= parent_negative else -1.0,
    }


def return_loss(headings: np.ndarray, delta: float) -> tuple[float, dict[int, tuple[float, float, float]]]:
    records: dict[int, tuple[float, float, float]] = {}
    errors = []
    for lag in LAGS:
        observed = float(np.median(d2(headings[lag:], headings[:-lag])))
        predicted = float(d2(0.0, (lag * delta) % 2.0))
        error = abs(observed - predicted)
        records[lag] = (observed, predicted, error)
        errors.append(error)
    return float(np.mean(errors)), records


def extract_roots() -> tuple[list[Root], dict]:
    roots: list[Root] = []
    diagnostics: dict[str, int | float] = defaultdict(int)
    for path in sorted(SOURCE.glob("*.csv")):
        run = load_run(path)
        split = split_for_video(run.video)
        diagnostics[f"{split}_source_videos"] += 1
        for track_id, track in sorted(run.tracks.items()):
            for segment_index, segment in enumerate(contiguous_segments(track)):
                for start in range(0, len(segment) - ROOT_STEPS, ROOT_STEPS):
                    diagnostics[f"{split}_candidate_roots"] += 1
                    block = segment[start : start + ROOT_STEPS + 1]
                    points = np.asarray([(item.x, item.y) for item in block], dtype=float)
                    steps = np.diff(points, axis=0)
                    magnitudes = np.linalg.norm(steps, axis=1)
                    if np.any(magnitudes < MIN_STEP_M):
                        diagnostics[f"{split}_resolution_exclusions"] += 1
                        continue
                    roots.append(
                        Root(
                            split=split,
                            video=run.video,
                            file=path.name,
                            track_id=track_id,
                            segment_index=segment_index,
                            start_frame=block[0].frame,
                            points=points,
                            steps=steps,
                            headings=headings_from_steps(steps),
                        )
                    )
                    diagnostics[f"{split}_eligible_roots"] += 1
    return roots, dict(diagnostics)


def score_roots(roots: list[Root]) -> tuple[list[dict], list[dict]]:
    score_rows: list[dict] = []
    return_rows: list[dict] = []
    for root in roots:
        for candidate, delta in CANDIDATES.items():
            scores = score_heading_path(root.headings, delta)
            fingerprint, lag_records = return_loss(root.headings, delta)
            score_rows.append(
                {
                    "split": root.split,
                    "video": root.video,
                    "file": root.file,
                    "track_id": root.track_id,
                    "segment_index": root.segment_index,
                    "start_frame": root.start_frame,
                    "candidate": candidate,
                    "increment_ara": delta,
                    **scores,
                    "return_mae": fingerprint,
                }
            )
            for lag, (observed, predicted, error) in lag_records.items():
                return_rows.append(
                    {
                        "split": root.split,
                        "video": root.video,
                        "track_id": root.track_id,
                        "start_frame": root.start_frame,
                        "candidate": candidate,
                        "lag": lag,
                        "observed_return_ara": observed,
                        "predicted_return_ara": predicted,
                        "absolute_error_ara": error,
                    }
                )
    return score_rows, return_rows


def candidate_summary(score_rows: list[dict]) -> tuple[dict, list[dict]]:
    summary: dict[str, dict] = {}
    table: list[dict] = []
    for split in ("calibration", "evaluation", "holdout"):
        summary[split] = {}
        for candidate in CANDIDATES:
            rows = [
                row for row in score_rows
                if row["split"] == split and row["candidate"] == candidate
            ]
            record = {
                "increment_ara": CANDIDATES[candidate],
                "roots": len(rows),
                "videos": len({row["video"] for row in rows}),
            }
            for field in (
                "local_directed",
                "parent_directed",
                "local_reversible",
                "parent_reversible",
                "return_mae",
            ):
                values = [float(row[field]) for row in rows]
                record[f"{field}_mean"] = statistics.mean(values)
                record[f"{field}_median"] = statistics.median(values)
            summary[split][candidate] = record
            table.append({"split": split, "candidate": candidate, **record})
        for endpoint in ("local_directed_mean", "parent_directed_mean", "return_mae_mean"):
            winner = min(CANDIDATES, key=lambda name: summary[split][name][endpoint])
            summary[split][f"winner_{endpoint}"] = winner
    return summary, table


def cluster_bootstrap_difference(records: list[tuple[str, float]], offset: int) -> dict:
    by_video: dict[str, list[float]] = defaultdict(list)
    for video, value in records:
        if math.isfinite(value):
            by_video[video].append(value)
    videos = sorted(by_video)
    if not videos:
        return {"mean": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"), "roots": 0, "videos": 0}
    sums = np.asarray([sum(by_video[video]) for video in videos], dtype=float)
    counts = np.asarray([len(by_video[video]) for video in videos], dtype=float)
    rng = np.random.default_rng(SEED + offset)
    draws = rng.integers(0, len(videos), size=(BOOTSTRAPS, len(videos)))
    sampled = np.sum(sums[draws], axis=1) / np.sum(counts[draws], axis=1)
    return {
        "mean": float(sums.sum() / counts.sum()),
        "ci_low": float(np.quantile(sampled, 0.025)),
        "ci_high": float(np.quantile(sampled, 0.975)),
        "roots": int(counts.sum()),
        "videos": len(videos),
    }


def phi_candidate_comparisons(score_rows: list[dict]) -> dict:
    indexed = {
        (row["split"], row["video"], row["track_id"], row["start_frame"], row["candidate"]): row
        for row in score_rows
    }
    result = {}
    for split_index, split in enumerate(("evaluation", "holdout")):
        result[split] = {}
        phi_rows = [
            row for row in score_rows
            if row["split"] == split and row["candidate"] == "phi"
        ]
        for candidate_index, candidate in enumerate(CANDIDATES):
            if candidate == "phi":
                continue
            differences = []
            for row in phi_rows:
                rival = indexed[(split, row["video"], row["track_id"], row["start_frame"], candidate)]
                differences.append((row["video"], float(row["parent_directed"]) - float(rival["parent_directed"])))
            result[split][candidate] = cluster_bootstrap_difference(
                differences, 100 + split_index * 20 + candidate_index
            )
    return result


def reconstruct_from_turns(anchor: float, turns: np.ndarray) -> np.ndarray:
    return np.r_[anchor, np.mod(anchor + np.cumsum(turns), 2.0)]


def phi_parent_score(headings: np.ndarray) -> float:
    return float(score_heading_path(headings, PHI_DELTA)["parent_directed"])


def shuffled_null(roots: list[Root], split: str, offset: int) -> dict:
    subset = [root for root in roots if root.split == split]
    observed = float(np.mean([phi_parent_score(root.headings) for root in subset]))
    rng = np.random.default_rng(SEED + offset)
    accumulated = np.zeros(N_NULL, dtype=float)
    horizons = np.arange(1, ROOT_STEPS, dtype=float)
    for root in subset:
        turns = np.mod(np.diff(root.headings), 2.0)
        order = np.argsort(rng.random((N_NULL, len(turns))), axis=1)
        permuted = turns[order]
        reconstructed = np.mod(root.headings[0] + np.cumsum(permuted, axis=1), 2.0)
        prediction = np.mod(root.headings[0] + horizons * PHI_DELTA, 2.0)
        accumulated += np.median(d2(reconstructed, prediction[None, :]), axis=1)
    null = accumulated / len(subset)
    return {
        "observed_mean": observed,
        "null_median": float(np.median(null)),
        "null_95": [float(np.quantile(null, 0.025)), float(np.quantile(null, 0.975))],
        "p_lower": float((1 + np.sum(null <= observed)) / (N_NULL + 1)),
        "values": null,
    }


def reversed_heading_path(root: Root) -> np.ndarray:
    reversed_steps = -root.steps[::-1]
    return headings_from_steps(reversed_steps)


def control_scores(roots: list[Root]) -> tuple[list[dict], dict]:
    by_video: dict[str, list[Root]] = defaultdict(list)
    for root in roots:
        by_video[root.video].append(root)
    partner_for: dict[str, Root] = {}
    for video, group in by_video.items():
        group.sort(key=lambda item: (item.start_frame, item.track_id, item.segment_index))
        if len(group) < 2:
            continue
        for index, root in enumerate(group):
            partner_for[root.key] = group[(index + 1) % len(group)]

    rows = []
    for root in roots:
        real = phi_parent_score(root.headings)
        reverse = phi_parent_score(reversed_heading_path(root))
        broken = float("nan")
        if root.key in partner_for:
            turns = np.mod(np.diff(root.headings), 2.0)
            partner_turns = np.mod(np.diff(partner_for[root.key].headings), 2.0)
            broken_headings = reconstruct_from_turns(root.headings[0], np.r_[turns[:15], partner_turns[15:]])
            broken = phi_parent_score(broken_headings)
        rows.append(
            {
                "split": root.split,
                "video": root.video,
                "track_id": root.track_id,
                "start_frame": root.start_frame,
                "phi_parent_real": real,
                "phi_parent_reversed_time": reverse,
                "phi_parent_broken_lineage": broken,
                "real_minus_reversed": real - reverse,
                "real_minus_broken": real - broken if math.isfinite(broken) else float("nan"),
            }
        )

    summary = {}
    for split_index, split in enumerate(("evaluation", "holdout")):
        subset = [row for row in rows if row["split"] == split]
        summary[split] = {
            "real_mean": statistics.mean(float(row["phi_parent_real"]) for row in subset),
            "reversed_time_mean": statistics.mean(float(row["phi_parent_reversed_time"]) for row in subset),
            "broken_lineage_mean": statistics.mean(
                float(row["phi_parent_broken_lineage"])
                for row in subset if math.isfinite(float(row["phi_parent_broken_lineage"]))
            ),
            "real_minus_reversed": cluster_bootstrap_difference(
                [(row["video"], float(row["real_minus_reversed"])) for row in subset],
                300 + split_index,
            ),
            "real_minus_broken": cluster_bootstrap_difference(
                [(row["video"], float(row["real_minus_broken"])) for row in subset],
                310 + split_index,
            ),
        }
    return rows, summary


def pixel_scale_m() -> float:
    ratios = []
    for path in sorted(SOURCE.glob("*.csv")):
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                for px_name, m_name in (("cx_pos [px]", "cx_pos [m]"), ("cy_pos [px]", "cy_pos [m]")):
                    pixels = float(row[px_name])
                    metres = float(row[m_name])
                    if pixels != 0 and metres != 0:
                        ratios.append(abs(metres / pixels))
                if len(ratios) >= 10_000:
                    break
        if len(ratios) >= 10_000:
            break
    return float(np.median(ratios))


def resolution_audit(roots: list[Root]) -> dict:
    pixel = pixel_scale_m()
    magnitudes = np.concatenate([np.linalg.norm(root.steps, axis=1) for root in roots])
    grains = np.arctan2(math.sqrt(2.0) * pixel, magnitudes) / math.pi
    nearest_name = min(
        (name for name in CANDIDATES if name != "phi"),
        key=lambda name: float(d2(PHI_DELTA, CANDIDATES[name])),
    )
    nearest = CANDIDATES[nearest_name]
    grain = float(np.median(grains))
    horizons = []
    for horizon in (1, 2, 3, 5, 8, 13, 21):
        separation = float(d2((horizon * PHI_DELTA) % 2.0, (horizon * nearest) % 2.0))
        horizons.append(
            {
                "horizon": horizon,
                "candidate_separation_ara": separation,
                "resolves_median_heading_grain": bool(separation > grain),
            }
        )
    first_resolved = next(
        (row["horizon"] for row in horizons if row["resolves_median_heading_grain"]), None
    )
    return {
        "pixel_scale_m": pixel,
        "median_heading_grain_ara": grain,
        "heading_grain_95": [float(np.quantile(grains, 0.025)), float(np.quantile(grains, 0.975))],
        "nearest_fixed_candidate": nearest_name,
        "phi_increment_ara": PHI_DELTA,
        "nearest_increment_ara": nearest,
        "one_step_separation_ara": float(d2(PHI_DELTA, nearest)),
        "one_step_exact_phi_resolution": bool(float(d2(PHI_DELTA, nearest)) > grain),
        "horizons": horizons,
        "first_resolved_horizon": first_resolved,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_results(
    roots: list[Root],
    candidate_table: list[dict],
    shuffles: dict,
    resolution: dict,
    path: Path,
) -> None:
    width, height = 1900, 1250
    image = Image.new("RGB", (width, height), "#f5f7fb")
    draw = ImageDraw.Draw(image)
    regular = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 18)
    small = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 14)
    bold = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 22)
    title_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 34)
    draw.text((65, 35), "T328 - bubble movement on the ARA Phi circle train", fill="#182238", font=title_font)

    panels = [(55, 105, 925, 610), (975, 105, 1845, 610), (55, 680, 925, 1185), (975, 680, 1845, 1185)]

    def frame(box, title, xlabel, ylabel, xlim, ylim):
        left, top, right, bottom = box
        draw.rounded_rectangle(box, radius=14, fill="white", outline="#c8d0dc", width=2)
        draw.text((left + 20, top + 15), title, fill="#182238", font=bold)
        plot = (left + 80, top + 65, right - 28, bottom - 70)
        draw.line((plot[0], plot[3], plot[2], plot[3]), fill="#566071", width=2)
        draw.line((plot[0], plot[1], plot[0], plot[3]), fill="#566071", width=2)
        draw.text((plot[0] + (plot[2] - plot[0]) // 2 - 60, bottom - 45), xlabel, fill="#343b49", font=small)
        draw.text((left + 10, top + 45), ylabel, fill="#343b49", font=small)
        return plot, xlim, ylim

    def point(panel, x, y):
        plot, xlim, ylim = panel
        px = plot[0] + (float(x) - xlim[0]) / max(xlim[1] - xlim[0], 1e-12) * (plot[2] - plot[0])
        py = plot[3] - (float(y) - ylim[0]) / max(ylim[1] - ylim[0], 1e-12) * (plot[3] - plot[1])
        return int(px), int(py)

    def line(panel, xs, ys, color, width_px=3, dots=True):
        pts = [point(panel, x, y) for x, y in zip(xs, ys)]
        if len(pts) > 1:
            draw.line(pts, fill=color, width=width_px, joint="curve")
        if dots:
            for px, py in pts:
                draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=color)

    example = next(root for root in roots if root.split == "evaluation")
    horizons = np.arange(ROOT_STEPS)
    prediction = np.mod(example.headings[0] + horizons * PHI_DELTA, 2.0)
    panel = frame(panels[0], f"One frozen root: {example.key}", "time slice", "ARA direction", (0, 31), (0, 2))
    ridge_y = point(panel, 0, 1.0)[1]
    draw.line((panel[0][0], ridge_y, panel[0][2], ridge_y), fill="#9aa2ae", width=2)
    line(panel, horizons, example.headings, "#2b72b5", 3)
    line(panel, horizons, prediction, "#dc8b24", 2)
    draw.text((panel[0][0] + 10, panel[0][1] + 8), "blue observed | orange +2/phi", fill="#343b49", font=small)

    evaluation = [row for row in candidate_table if row["split"] == "evaluation"]
    evaluation.sort(key=lambda row: float(row["parent_directed_mean"]))
    y_max = max(float(row["parent_directed_mean"]) for row in evaluation) * 1.12
    panel = frame(panels[1], "Frozen candidate ranking - evaluation", "candidate", "parent loss", (0, len(evaluation)), (0, y_max))
    bar_width = (panel[0][2] - panel[0][0]) / len(evaluation)
    for index, row in enumerate(evaluation):
        left = panel[0][0] + index * bar_width + 5
        right = panel[0][0] + (index + 1) * bar_width - 5
        top = point(panel, 0, row["parent_directed_mean"])[1]
        color = "#dc8b24" if row["candidate"] == "phi" else "#7696c4"
        draw.rectangle((int(left), top, int(right), panel[0][3]), fill=color)
        label = row["candidate"].replace("fibonacci_", "fib_").replace("silver_conjugate", "silver")
        draw.text((int(left), panel[0][3] + 7), label[:10], fill="#343b49", font=small)

    null = shuffles["evaluation"]["values"]
    counts, edges = np.histogram(null, bins=45)
    panel = frame(panels[2], "10,000 turn-order shuffles - evaluation", "mean Phi parent loss", "count", (float(edges[0]), float(edges[-1])), (0, float(max(counts)) * 1.08))
    for index, count in enumerate(counts):
        x0, _ = point(panel, edges[index], 0)
        x1, y1 = point(panel, edges[index + 1], count)
        draw.rectangle((x0, y1, max(x0 + 1, x1 - 1), panel[0][3]), fill="#9a80b8")
    observed_x = point(panel, shuffles["evaluation"]["observed_mean"], 0)[0]
    draw.line((observed_x, panel[0][1], observed_x, panel[0][3]), fill="#111111", width=4)
    draw.text((panel[0][0] + 10, panel[0][1] + 8), "black = observed order", fill="#343b49", font=small)

    hs = [row["horizon"] for row in resolution["horizons"]]
    sep = [row["candidate_separation_ara"] for row in resolution["horizons"]]
    y_max = max(max(sep), resolution["median_heading_grain_ara"]) * 1.15
    panel = frame(panels[3], "Exact-constant resolution by horizon", "horizon", "ARA separation", (1, 21), (0, y_max))
    line(panel, hs, sep, "#dc8b24", 4)
    grain_y = point(panel, 1, resolution["median_heading_grain_ara"])[1]
    draw.line((panel[0][0], grain_y, panel[0][2], grain_y), fill="#333333", width=3)
    draw.text((panel[0][0] + 10, panel[0][1] + 8), "orange Phi-vs-rival | black median grain", fill="#343b49", font=small)

    image.save(path)


def main() -> None:
    roots, diagnostics = extract_roots()
    if not roots:
        raise SystemExit("No eligible 32-step roots")
    score_rows, return_rows = score_roots(roots)
    candidates, candidate_table = candidate_summary(score_rows)
    comparisons = phi_candidate_comparisons(score_rows)
    control_rows, controls = control_scores(roots)
    shuffles = {
        "evaluation": shuffled_null(roots, "evaluation", 500),
        "holdout": shuffled_null(roots, "holdout", 600),
    }
    resolution = resolution_audit(roots)

    holdout_roots = [root for root in roots if root.split == "holdout"]
    holdout_sufficient = len(holdout_roots) >= 20 and len({root.video for root in holdout_roots}) >= 3
    parent_winner = all(
        candidates[split]["winner_parent_directed_mean"] == "phi"
        for split in ("evaluation", "holdout")
    )
    all_rivals = (
        all(record["ci_high"] < 0 for record in comparisons["evaluation"].values())
        and all(record["mean"] < 0 for record in comparisons["holdout"].values())
    )
    shuffle_pass = all(shuffles[split]["p_lower"] < 0.05 for split in ("evaluation", "holdout"))
    broken_pass = (
        controls["evaluation"]["real_minus_broken"]["ci_high"] < 0
        and controls["holdout"]["real_minus_broken"]["mean"] < 0
    )
    return_pass = all(
        candidates[split]["winner_return_mae_mean"] == "phi"
        for split in ("evaluation", "holdout")
    )
    resolution_pass = resolution["first_resolved_horizon"] is not None

    gates = {
        "holdout_sufficient": holdout_sufficient,
        "phi_parent_winner_evaluation_and_holdout": parent_winner,
        "phi_beats_every_rival_with_registered_uncertainty": all_rivals,
        "observed_order_beats_shuffle_evaluation_and_holdout": shuffle_pass,
        "real_lineage_beats_broken_lineage": broken_pass,
        "phi_fibonacci_return_winner_evaluation_and_holdout": return_pass,
        "multistep_exact_constant_resolution": resolution_pass,
    }
    substantive = [parent_winner, all_rivals, shuffle_pass, broken_pass, return_pass]
    if not holdout_sufficient:
        verdict = "DATA INSUFFICIENT"
    elif all(gates.values()):
        verdict = "SUPPORTED IN THIS BUBBLE-DIRECTION REPRESENTATION"
    elif any(substantive):
        verdict = "PARTIAL / MIXED"
    else:
        verdict = "NOT SUPPORTED"

    result = {
        "test_id": "T328-PHI-CIRCLE-TRAIN-BUBBLES-v1",
        "run_date": "2026-08-02",
        "source": "Pandey et al., Zenodo 10.5281/zenodo.15102957",
        "protocol_sha256": sha256(PROTOCOL),
        "source_aggregate_sha256": source_sha256(list(SOURCE.glob("*.csv"))),
        "operator": "x[n+1] = (x[n] + 2/phi) mod 2",
        "verdict": verdict,
        "diagnostics": diagnostics,
        "candidate_summary": candidates,
        "phi_parent_comparisons": comparisons,
        "controls": controls,
        "shuffle": {
            split: {key: value for key, value in record.items() if key != "values"}
            for split, record in shuffles.items()
        },
        "resolution": resolution,
        "gates": gates,
    }

    results_dir = HERE / "results"
    write_csv(results_dir / f"{PREFIX}_ROOT_SCORES.csv", score_rows)
    write_csv(results_dir / f"{PREFIX}_RETURN_PROFILES.csv", return_rows)
    write_csv(results_dir / f"{PREFIX}_CANDIDATE_SUMMARY.csv", candidate_table)
    write_csv(results_dir / f"{PREFIX}_CONTROL_SCORES.csv", control_rows)
    np.savez_compressed(
        results_dir / f"{PREFIX}_SHUFFLE_NULLS.npz",
        evaluation=shuffles["evaluation"]["values"],
        holdout=shuffles["holdout"]["values"],
    )
    result_path = HERE / f"{PREFIX}_RESULTS.json"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    figure_path = HERE / f"{PREFIX}_FIGURE.png"
    plot_results(roots, candidate_table, shuffles, resolution, figure_path)

    ranking_lines = []
    for split in ("evaluation", "holdout"):
        ranking = sorted(
            (
                (name, record["increment_ara"], record["parent_directed_mean"], record["return_mae_mean"])
                for name, record in candidates[split].items() if isinstance(record, dict)
            ),
            key=lambda row: row[2],
        )
        for rank, (name, delta, parent, returns) in enumerate(ranking, 1):
            ranking_lines.append(f"| {split} | {rank} | {name} | {delta:.9f} | {parent:.6f} | {returns:.6f} |")
    gate_lines = "\n".join(f"- `{name}`: **{value}**" for name, value in gates.items())
    report = f"""# T328 bubble Phi circle-train report

**Run date:** 2 August 2026  
**Frozen protocol:** `T328_PHI_CIRCLE_TRAIN_BUBBLE_PROTOCOL_v1_FROZEN.md`  
**Verdict:** **{verdict}**

## Answer first

The exact positive operator `x[n+1] = (x[n] + 2/phi) mod 2` was applied to
the raw movement headings of uninterrupted bubble identities. It was not
applied to bubble area, speed, radius, merger ratios, or a processed Phi
coordinate.

There were **{diagnostics.get('evaluation_eligible_roots', 0)} evaluation**
roots and **{diagnostics.get('holdout_eligible_roots', 0)} holdout** roots.
The evaluation parent winner was
**{candidates['evaluation']['winner_parent_directed_mean']}** and the holdout
winner was **{candidates['holdout']['winner_parent_directed_mean']}**. The
evaluation return-fingerprint winner was
**{candidates['evaluation']['winner_return_mae_mean']}**; holdout was
**{candidates['holdout']['winner_return_mae_mean']}**.

The observed-order shuffle p-values were
`{shuffles['evaluation']['p_lower']:.6f}` (evaluation) and
`{shuffles['holdout']['p_lower']:.6f}` (holdout). A small value would mean the
recorded ordering carries the proposed Phi carrier more strongly than the
same turns rearranged.

## Frozen candidate ranking

| split | rank | candidate | increment | parent loss | return MAE |
|---|---:|---|---:|---:|---:|
{chr(10).join(ranking_lines)}

## Controls

- Evaluation real-minus-broken mean:
  `{controls['evaluation']['real_minus_broken']['mean']:.6f}`
  (95% `{controls['evaluation']['real_minus_broken']['ci_low']:.6f}` to
  `{controls['evaluation']['real_minus_broken']['ci_high']:.6f}`).
- Holdout real-minus-broken mean:
  `{controls['holdout']['real_minus_broken']['mean']:.6f}`.
- Negative values favour the real lineage.
- Reversed time is reported separately and never used to choose the primary
  direction.

## Resolution

The nearest fixed candidate was **{resolution['nearest_fixed_candidate']}**.
Its one-step separation from Phi was
`{resolution['one_step_separation_ara']:.9f}` ARA, versus median estimated
heading grain `{resolution['median_heading_grain_ara']:.9f}` ARA. The first
registered horizon exceeding that grain was
**{resolution['first_resolved_horizon']}**.

## Frozen gates

{gate_lines}

## Boundaries

- This archive was used in earlier bubble tests; T328 is a newly frozen
  operator, not an unopened-data claim.
- The result concerns centroid movement direction at 50 fps.
- No smoothing, interpolation, Fourier processing, eventwise sign selection,
  or carrier reanchoring was used.
- Failure here rejects this particular observable placement, not Phi in every
  bubble property and not the full ARA framework.
"""
    report_path = HERE / f"{PREFIX}_REPORT_2026-08-02.md"
    report_path.write_text(report, encoding="utf-8")

    printable = dict(result)
    printable["candidate_summary"] = {
        split: {
            "parent_winner": candidates[split]["winner_parent_directed_mean"],
            "local_winner": candidates[split]["winner_local_directed_mean"],
            "return_winner": candidates[split]["winner_return_mae_mean"],
            "phi_parent_mean": candidates[split]["phi"]["parent_directed_mean"],
        }
        for split in ("calibration", "evaluation", "holdout")
    }
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    for path in (result_path, report_path, figure_path):
        print(f"{path.name}\t{sha256(path)}")


if __name__ == "__main__":
    main()
