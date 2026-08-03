#!/usr/bin/env python3
"""Run T329: the frozen actual bubble-handover Phi seam test."""

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
RESULTS = HERE / "results"
EVENT_SOURCE = RESULTS / "vertical_ara_bubble_events.csv"
PROTOCOL = HERE / "T329_ACTUAL_HANDOVER_PHI_SEAM_PROTOCOL_v1_FROZEN.md"
PREFIX = "T329_ACTUAL_HANDOVER_PHI_SEAM"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_DELTA = 2.0 / PHI
MIN_STEP_M = 0.0005
BOOTSTRAPS = 5_000
SEED = 20260802 + 329

CANDIDATES = OrderedDict(
    [
        ("persistence", 0.0),
        ("ridge", 1.0),
        ("silver_conjugate", 2.0 - 2.0 * (math.sqrt(2.0) - 1.0)),
        ("two_fifths", 6.0 / 5.0),
        ("phi", PHI_DELTA),
        ("fibonacci_8_21", 26.0 / 21.0),
        ("three_eighths_grid", 5.0 / 4.0),
        ("one_over_e", 2.0 - 2.0 / math.e),
        ("one_third", 4.0 / 3.0),
    ]
)


@dataclass
class Seam:
    split: str
    video: str
    file: str
    frame: int
    inherited_id: int
    joining_id: int
    theta_pre: float
    theta_contact: float
    theta_post: float
    contact_sign: float
    pre_magnitude: float
    post_magnitude: float
    x_aa: float
    x_ab: float
    x_ba: float
    x_preordinary: float

    @property
    def key(self) -> str:
        return f"{self.video}:{self.frame}:{self.inherited_id}:{self.joining_id}"


def split_for_video(video: str) -> str:
    number = int(video[1:])
    if number <= 7:
        return "calibration"
    if number <= 28:
        return "evaluation"
    return "holdout"


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


def vector(left: Bubble, right: Bubble) -> np.ndarray:
    return np.asarray([right.x - left.x, right.y - left.y], dtype=float)


def magnitude(value: np.ndarray) -> float:
    return float(np.linalg.norm(value))


def theta(value: np.ndarray) -> float:
    return math.atan2(float(value[1]), float(value[0]))


def signed_angle(left: float, right: float) -> float:
    return math.atan2(math.sin(right - left), math.cos(right - left))


def d2(left, right):
    difference = np.abs(np.asarray(left, dtype=float) - np.asarray(right, dtype=float))
    return np.minimum(difference, 2.0 - difference)


def oriented_coordinate(start: float, end: float, sign: float) -> float:
    return float((sign * signed_angle(start, end) / math.pi) % 2.0)


def load_primary_event_rows() -> list[dict[str, str]]:
    with EVENT_SOURCE.open("r", newline="", encoding="utf-8-sig") as handle:
        return [row for row in csv.DictReader(handle) if row["detector"] == "primary"]


def extract_seams() -> tuple[list[Seam], dict]:
    primary_rows = load_primary_event_rows()
    rows_by_file: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in primary_rows:
        rows_by_file[row["file"]].append(row)

    diagnostics: dict[str, int | float] = defaultdict(int)
    seams: list[Seam] = []
    for filename, rows in sorted(rows_by_file.items()):
        run = load_run(SOURCE / filename)
        split = split_for_video(run.video)
        diagnostics[f"{split}_primary_events"] += len(rows)
        for row in sorted(rows, key=lambda item: int(item["frame"])):
            child_ids = [int(row["child_small_id"]), int(row["child_large_id"])]
            parent_id = int(row["parent_id"])
            matching = [ident for ident in child_ids if ident == parent_id]
            if len(matching) != 1:
                diagnostics[f"{split}_no_exact_inherited_id"] += 1
                continue
            inherited_id = matching[0]
            joining_id = child_ids[0] if child_ids[1] == inherited_id else child_ids[1]
            frame = int(row["frame"])
            inherited_track = run.tracks[inherited_id]
            joining_track = run.tracks[joining_id]
            required = [frame - 1, frame, frame + 1, frame + 2]
            if any(item not in inherited_track for item in required) or frame not in joining_track:
                diagnostics[f"{split}_missing_required_frames"] += 1
                continue

            pre_vector = vector(inherited_track[frame - 1], inherited_track[frame])
            post_vector = vector(inherited_track[frame + 1], inherited_track[frame + 2])
            contact_vector = vector(inherited_track[frame], joining_track[frame])
            pre_magnitude = magnitude(pre_vector)
            post_magnitude = magnitude(post_vector)
            if pre_magnitude < MIN_STEP_M or post_magnitude < MIN_STEP_M:
                diagnostics[f"{split}_subresolution"] += 1
                continue
            if magnitude(contact_vector) <= 0.0:
                diagnostics[f"{split}_undefined_contact"] += 1
                continue

            theta_pre = theta(pre_vector)
            theta_contact = theta(contact_vector)
            theta_post = theta(post_vector)
            side_value = math.sin(theta_contact - theta_pre)
            if abs(side_value) <= 1e-15:
                diagnostics[f"{split}_zero_contact_side"] += 1
                continue
            contact_sign = 1.0 if side_value > 0 else -1.0

            x_aa = oriented_coordinate(theta_pre, theta_post, contact_sign)
            x_ab = oriented_coordinate(theta_pre, theta_contact, contact_sign)
            x_ba = oriented_coordinate(theta_contact, theta_post, contact_sign)

            x_preordinary = float("nan")
            if frame - 2 in inherited_track:
                prior_vector = vector(inherited_track[frame - 2], inherited_track[frame - 1])
                if magnitude(prior_vector) >= MIN_STEP_M:
                    x_preordinary = oriented_coordinate(theta(prior_vector), theta_pre, contact_sign)

            seams.append(
                Seam(
                    split=split,
                    video=run.video,
                    file=filename,
                    frame=frame,
                    inherited_id=inherited_id,
                    joining_id=joining_id,
                    theta_pre=theta_pre,
                    theta_contact=theta_contact,
                    theta_post=theta_post,
                    contact_sign=contact_sign,
                    pre_magnitude=pre_magnitude,
                    post_magnitude=post_magnitude,
                    x_aa=x_aa,
                    x_ab=x_ab,
                    x_ba=x_ba,
                    x_preordinary=x_preordinary,
                )
            )
            diagnostics[f"{split}_eligible"] += 1

    diagnostics["total_primary_events"] = len(primary_rows)
    diagnostics["total_eligible"] = len(seams)
    diagnostics["information3_max_identity_error"] = max(
        float(d2(item.x_aa, (item.x_ab + item.x_ba) % 2.0)) for item in seams
    )
    return seams, dict(diagnostics)


def cluster_bootstrap_difference(records: list[tuple[str, float]], offset: int) -> dict:
    by_video: dict[str, list[float]] = defaultdict(list)
    for video, value in records:
        if math.isfinite(value):
            by_video[video].append(float(value))
    videos = sorted(by_video)
    if not videos:
        return {
            "mean": float("nan"),
            "ci_low": float("nan"),
            "ci_high": float("nan"),
            "events": 0,
            "videos": 0,
        }
    sums = np.asarray([sum(by_video[video]) for video in videos], dtype=float)
    counts = np.asarray([len(by_video[video]) for video in videos], dtype=float)
    rng = np.random.default_rng(SEED + offset)
    draws = rng.integers(0, len(videos), size=(BOOTSTRAPS, len(videos)))
    sampled = np.sum(sums[draws], axis=1) / np.sum(counts[draws], axis=1)
    return {
        "mean": float(sums.sum() / counts.sum()),
        "ci_low": float(np.quantile(sampled, 0.025)),
        "ci_high": float(np.quantile(sampled, 0.975)),
        "events": int(counts.sum()),
        "videos": len(videos),
    }


def candidate_scores(seams: list[Seam], *, mirrored: bool = False) -> tuple[list[dict], dict]:
    score_rows: list[dict] = []
    summary: dict = {}
    for seam in seams:
        coordinate = (2.0 - seam.x_aa) % 2.0 if mirrored else seam.x_aa
        for candidate, increment in CANDIDATES.items():
            score_rows.append(
                {
                    "split": seam.split,
                    "video": seam.video,
                    "frame": seam.frame,
                    "inherited_id": seam.inherited_id,
                    "candidate": candidate,
                    "increment": increment,
                    "loss": float(d2(coordinate, increment)),
                }
            )
    for split in ("calibration", "evaluation", "holdout"):
        summary[split] = {}
        for candidate in CANDIDATES:
            values = [
                float(row["loss"])
                for row in score_rows
                if row["split"] == split and row["candidate"] == candidate
            ]
            summary[split][candidate] = {
                "events": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
            }
        summary[split]["winner_mean"] = min(
            CANDIDATES, key=lambda name: summary[split][name]["mean"]
        )
    return score_rows, summary


def phi_candidate_comparisons(score_rows: list[dict]) -> dict:
    indexed = {
        (row["split"], row["video"], row["frame"], row["inherited_id"], row["candidate"]): row
        for row in score_rows
    }
    result: dict = {}
    for split_index, split in enumerate(("evaluation", "holdout")):
        result[split] = {}
        phi_rows = [row for row in score_rows if row["split"] == split and row["candidate"] == "phi"]
        for candidate_index, candidate in enumerate(CANDIDATES):
            if candidate == "phi":
                continue
            differences = []
            for row in phi_rows:
                rival = indexed[
                    (split, row["video"], row["frame"], row["inherited_id"], candidate)
                ]
                differences.append((row["video"], float(row["loss"]) - float(rival["loss"])))
            result[split][candidate] = cluster_bootstrap_difference(
                differences, 100 + split_index * 20 + candidate_index
            )
    return result


def build_controls(seams: list[Seam]) -> tuple[list[dict], dict]:
    by_split_video: dict[tuple[str, str], list[Seam]] = defaultdict(list)
    for seam in seams:
        by_split_video[(seam.split, seam.video)].append(seam)
    for group in by_split_video.values():
        group.sort(key=lambda item: (item.frame, item.inherited_id))

    control_rows: list[dict] = []
    for (split, video), group in sorted(by_split_video.items()):
        for index, seam in enumerate(group):
            phi_real = float(d2(seam.x_aa, PHI_DELTA))
            row = {
                "split": split,
                "video": video,
                "frame": seam.frame,
                "inherited_id": seam.inherited_id,
                "phi_real": phi_real,
                "phi_broken": float("nan"),
                "phi_contact_scramble": float("nan"),
                "phi_preordinary": (
                    float(d2(seam.x_preordinary, PHI_DELTA))
                    if math.isfinite(seam.x_preordinary)
                    else float("nan")
                ),
            }
            if len(group) >= 2:
                partner = group[(index + 1) % len(group)]
                broken_x = oriented_coordinate(seam.theta_pre, partner.theta_post, seam.contact_sign)
                scramble_x = oriented_coordinate(seam.theta_pre, seam.theta_post, partner.contact_sign)
                row["phi_broken"] = float(d2(broken_x, PHI_DELTA))
                row["phi_contact_scramble"] = float(d2(scramble_x, PHI_DELTA))
            row["real_minus_broken"] = row["phi_real"] - row["phi_broken"]
            row["real_minus_contact_scramble"] = row["phi_real"] - row["phi_contact_scramble"]
            row["real_minus_preordinary"] = row["phi_real"] - row["phi_preordinary"]
            control_rows.append(row)

    summary: dict = {}
    fields = (
        "real_minus_broken",
        "real_minus_contact_scramble",
        "real_minus_preordinary",
    )
    for split_index, split in enumerate(("evaluation", "holdout")):
        subset = [row for row in control_rows if row["split"] == split]
        summary[split] = {}
        for field_index, field in enumerate(fields):
            summary[split][field] = cluster_bootstrap_difference(
                [(row["video"], float(row[field])) for row in subset],
                300 + split_index * 10 + field_index,
            )
        for level in ("phi_real", "phi_broken", "phi_contact_scramble", "phi_preordinary"):
            values = [float(row[level]) for row in subset if math.isfinite(float(row[level]))]
            summary[split][f"{level}_mean"] = statistics.mean(values) if values else float("nan")
            summary[split][f"{level}_events"] = len(values)
    return control_rows, summary


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


def resolution_audit(seams: list[Seam]) -> dict:
    pixel = pixel_scale_m()
    grains = []
    for seam in seams:
        pre_grain = math.atan2(math.sqrt(2.0) * pixel, seam.pre_magnitude) / math.pi
        post_grain = math.atan2(math.sqrt(2.0) * pixel, seam.post_magnitude) / math.pi
        grains.append(math.sqrt(pre_grain * pre_grain + post_grain * post_grain))
    nearest_name = min(
        (name for name in CANDIDATES if name != "phi"),
        key=lambda name: float(d2(PHI_DELTA, CANDIDATES[name])),
    )
    separation = float(d2(PHI_DELTA, CANDIDATES[nearest_name]))
    median_grain = float(np.median(grains))
    return {
        "pixel_scale_m": pixel,
        "median_turn_grain_ara": median_grain,
        "turn_grain_95": [float(np.quantile(grains, 0.025)), float(np.quantile(grains, 0.975))],
        "nearest_fixed_candidate": nearest_name,
        "nearest_increment_ara": CANDIDATES[nearest_name],
        "one_step_separation_ara": separation,
        "one_step_exact_phi_resolution": bool(separation > median_grain),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def event_rows(seams: list[Seam]) -> list[dict]:
    rows = []
    for seam in seams:
        rows.append(
            {
                "split": seam.split,
                "video": seam.video,
                "file": seam.file,
                "frame": seam.frame,
                "inherited_id": seam.inherited_id,
                "joining_id": seam.joining_id,
                "contact_sign": seam.contact_sign,
                "pre_magnitude_m": seam.pre_magnitude,
                "post_magnitude_m": seam.post_magnitude,
                "theta_pre_rad": seam.theta_pre,
                "theta_contact_rad": seam.theta_contact,
                "theta_post_rad": seam.theta_post,
                "x_AA": seam.x_aa,
                "x_AB": seam.x_ab,
                "x_BA": seam.x_ba,
                "x_preordinary": seam.x_preordinary,
                "information3_identity_error": float(d2(seam.x_aa, (seam.x_ab + seam.x_ba) % 2.0)),
            }
        )
    return rows


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_figure(
    seams: list[Seam],
    candidate_summary: dict,
    control_summary: dict,
    resolution: dict,
    verdict: str,
    path: Path,
) -> None:
    width, height = 1900, 1250
    image = Image.new("RGB", (width, height), "#f7f9fc")
    draw = ImageDraw.Draw(image)
    title_font = font(42, True)
    subtitle_font = font(23)
    panel_title = font(25, True)
    body = font(19)
    small = font(16)
    draw.text((60, 35), "T329 — actual bubble-handover Phi seam", fill="#172033", font=title_font)
    draw.text((60, 92), verdict, fill="#5a6475", font=subtitle_font)

    panels = [(60, 150, 910, 610), (990, 150, 1840, 610), (60, 690, 910, 1150), (990, 690, 1840, 1150)]
    for box in panels:
        draw.rounded_rectangle(box, radius=18, fill="white", outline="#d7deea", width=2)

    # Panel 1: observed contact-oriented coordinates.
    x0, y0, x1, y1 = panels[0]
    draw.text((x0 + 25, y0 + 18), "Observed same-phase seam coordinates", fill="#172033", font=panel_title)
    draw.text((x0 + 445, y0 + 27), "blue: evaluation | orange: holdout", fill="#5a6475", font=small)
    plot = (x0 + 70, y0 + 80, x1 - 35, y1 - 65)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill="#344054", width=3)
    bins = np.linspace(0.0, 2.0, 25)
    histograms = {}
    for split in ("evaluation", "holdout"):
        values = [item.x_aa for item in seams if item.split == split]
        histograms[split], _ = np.histogram(values, bins=bins)
    maximum = max(max(histograms["evaluation"]), max(histograms["holdout"]), 1)
    bin_width = (plot[2] - plot[0]) / len(histograms["evaluation"])
    for split_index, (split, color) in enumerate((("evaluation", "#4776c5"), ("holdout", "#e19b2d"))):
        for index, count in enumerate(histograms[split]):
            full_left = plot[0] + index * bin_width
            bx0 = int(full_left + split_index * bin_width / 2.0)
            bx1 = int(full_left + (split_index + 1) * bin_width / 2.0) - 1
            bar_height = int((plot[3] - plot[1]) * 0.82 * count / maximum)
            draw.rectangle((bx0, plot[3] - bar_height, bx1, plot[3]), fill=color)
    for value, color, label in ((0.0, "#2f3b4e", "0 persistence"), (1.0, "#777777", "1 ridge"), (PHI_DELTA, "#d64d35", "2/phi")):
        px = plot[0] + int(value / 2.0 * (plot[2] - plot[0]))
        draw.line((px, plot[1], px, plot[3]), fill=color, width=3)
        draw.text((px + 5, plot[1] + 5), label, fill=color, font=small)
    for value in (0.0, 0.5, 1.0, 1.5, 2.0):
        px = plot[0] + int(value / 2.0 * (plot[2] - plot[0]))
        draw.text((px - 12, plot[3] + 18), f"{value:g}", fill="#344054", font=small)

    # Panel 2: candidate mean loss ranking.
    x0, y0, x1, y1 = panels[1]
    draw.text((x0 + 25, y0 + 18), "Frozen candidate mean loss", fill="#172033", font=panel_title)
    names = sorted(CANDIDATES, key=lambda name: candidate_summary["evaluation"][name]["mean"])
    maximum = max(candidate_summary["evaluation"][name]["mean"] for name in names) * 1.1
    for index, name in enumerate(names):
        yy = y0 + 82 + index * 38
        value = candidate_summary["evaluation"][name]["mean"]
        bar_width = int((x1 - x0 - 300) * value / maximum)
        color = "#d64d35" if name == "phi" else "#87a4cd"
        draw.text((x0 + 28, yy), name.replace("_", " "), fill="#344054", font=small)
        draw.rectangle((x0 + 205, yy + 2, x0 + 205 + bar_width, yy + 22), fill=color)
        draw.text((x0 + 215 + bar_width, yy), f"{value:.4f}", fill="#344054", font=small)

    # Panel 3: Information3 legs.
    x0, y0, x1, y1 = panels[2]
    draw.text((x0 + 25, y0 + 18), "Information³ seam decomposition", fill="#172033", font=panel_title)
    plot = (x0 + 70, y0 + 80, x1 - 45, y1 - 65)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill="#344054", width=2)
    draw.line((plot[0], plot[1], plot[0], plot[3]), fill="#344054", width=2)
    for seam in seams:
        px = plot[0] + int(seam.x_ab / 2.0 * (plot[2] - plot[0]))
        py = plot[3] - int(seam.x_ba / 2.0 * (plot[3] - plot[1]))
        color = "#4776c5" if seam.split == "evaluation" else "#e19b2d" if seam.split == "holdout" else "#aeb9c8"
        draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=color)
    draw.text((plot[0], plot[3] + 22), "x_AB: inherited direction → joining contact", fill="#344054", font=small)
    draw.text((plot[0] + 5, plot[1] + 5), "x_BA", fill="#344054", font=small)

    # Panel 4: controls and resolution.
    x0, y0, x1, y1 = panels[3]
    draw.text((x0 + 25, y0 + 18), "Phi loss controls and exact resolution", fill="#172033", font=panel_title)
    labels = ("phi_real", "phi_broken", "phi_contact_scramble", "phi_preordinary")
    pretty = ("real seam", "broken lineage", "side scramble", "pre-event turn")
    values = [control_summary["evaluation"].get(f"{label}_mean", float("nan")) for label in labels]
    finite = [value for value in values if math.isfinite(value)]
    maximum = max(finite) * 1.15 if finite else 1.0
    base_y = y1 - 120
    bar_area = x1 - x0 - 120
    for index, (label, value) in enumerate(zip(pretty, values)):
        bx0 = x0 + 55 + index * (bar_area // 4)
        bx1 = bx0 + 105
        top = base_y - int((base_y - y0 - 105) * value / maximum) if math.isfinite(value) else base_y
        draw.rectangle((bx0, top, bx1, base_y), fill="#d64d35" if index == 0 else "#aeb9c8")
        draw.text((bx0, base_y + 10), label, fill="#344054", font=small)
        if math.isfinite(value):
            draw.text((bx0 + 10, top - 24), f"{value:.3f}", fill="#344054", font=small)
    draw.text((x0 + 30, y1 - 58), f"Phi vs nearest rival: {resolution['one_step_separation_ara']:.6f} ARA", fill="#344054", font=small)
    draw.text((x0 + 30, y1 - 34), f"median seam grain: {resolution['median_turn_grain_ara']:.6f} ARA", fill="#344054", font=small)
    image.save(path)


def main() -> None:
    if not PROTOCOL.exists():
        raise FileNotFoundError("Frozen protocol is required before scoring")
    RESULTS.mkdir(parents=True, exist_ok=True)
    seams, diagnostics = extract_seams()
    score_rows, candidate_summary = candidate_scores(seams)
    mirrored_rows, mirrored_summary = candidate_scores(seams, mirrored=True)
    comparisons = phi_candidate_comparisons(score_rows)
    control_rows, control_summary = build_controls(seams)
    resolution = resolution_audit(seams)

    evaluation_phi_winner = candidate_summary["evaluation"]["winner_mean"] == "phi"
    holdout_phi_winner = candidate_summary["holdout"]["winner_mean"] == "phi"
    evaluation_phi_beats_all = all(
        record["ci_high"] < 0.0 for record in comparisons["evaluation"].values()
    )
    lineage_gate = (
        control_summary["evaluation"]["real_minus_broken"]["ci_high"] < 0.0
        and control_summary["evaluation"]["real_minus_contact_scramble"]["ci_high"] < 0.0
        and control_summary["holdout"]["real_minus_broken"]["mean"] < 0.0
        and control_summary["holdout"]["real_minus_contact_scramble"]["mean"] < 0.0
    )
    event_gate = (
        control_summary["evaluation"]["real_minus_preordinary"]["ci_high"] < 0.0
        and control_summary["holdout"]["real_minus_preordinary"]["mean"] < 0.0
    )
    resolution_gate = resolution["one_step_exact_phi_resolution"]
    gates = {
        "evaluation_phi_winner": evaluation_phi_winner,
        "holdout_phi_winner_underpowered": holdout_phi_winner,
        "evaluation_phi_beats_all_with_cluster_interval": evaluation_phi_beats_all,
        "lineage_and_contact_side_specificity": lineage_gate,
        "event_specificity_vs_pre_event_turn": event_gate,
        "exact_constant_resolution": resolution_gate,
        "strict_holdout_sufficient": diagnostics.get("holdout_eligible", 0) >= 20,
        "multi_handover_fibonacci_test_available": False,
    }
    if evaluation_phi_winner and evaluation_phi_beats_all and lineage_gate and event_gate:
        verdict = "PARTIAL — ONE-STEP PHI SEAM, EXACT CONSTANT/HOLDOUT LIMITS APPLY"
    else:
        verdict = "NOT SUPPORTED — ACTUAL HANDOVER PHI SEAM"

    event_output = RESULTS / f"{PREFIX}_EVENTS.csv"
    score_output = RESULTS / f"{PREFIX}_CANDIDATE_SCORES.csv"
    mirrored_output = RESULTS / f"{PREFIX}_MIRRORED_SCORES.csv"
    control_output = RESULTS / f"{PREFIX}_CONTROLS.csv"
    write_csv(event_output, event_rows(seams))
    write_csv(score_output, score_rows)
    write_csv(mirrored_output, mirrored_rows)
    write_csv(control_output, control_rows)

    result = {
        "test": "T329 actual bubble-handover Phi seam",
        "run_date": "2026-08-02",
        "verdict": verdict,
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "source_event_sha256": sha256(EVENT_SOURCE),
        "source_csv_set_sha256": source_sha256(list(SOURCE.glob("*.csv"))),
        "constants": {
            "phi": PHI,
            "phi_increment": PHI_DELTA,
            "min_step_m": MIN_STEP_M,
            "bootstraps": BOOTSTRAPS,
            "seed": SEED,
        },
        "candidates": CANDIDATES,
        "diagnostics": diagnostics,
        "candidate_summary": candidate_summary,
        "mirrored_candidate_summary": mirrored_summary,
        "phi_candidate_comparisons": comparisons,
        "control_summary": control_summary,
        "resolution": resolution,
        "gates": gates,
        "boundaries": [
            "The archive was used in prior bubble analyses; T329 freezes a new contact-oriented coordinate.",
            "Only 16 eligible holdout seams were available, below the strict 20-event boundary.",
            "Only three repeated primary merger lineages existed before scoring, so Fibonacci near-returns are not tested.",
            "The result concerns released centroid directions around independently detected binary merger seams.",
        ],
        "artifacts": {
            "events": event_output.name,
            "candidate_scores": score_output.name,
            "mirrored_scores": mirrored_output.name,
            "controls": control_output.name,
        },
    }
    result_path = HERE / f"{PREFIX}_RESULTS.json"
    result_path.write_text(json.dumps(result, indent=2, allow_nan=True), encoding="utf-8")

    figure_path = HERE / f"{PREFIX}_FIGURE.png"
    draw_figure(seams, candidate_summary, control_summary, resolution, verdict, figure_path)

    report_lines = [
        "# T329 actual bubble-handover Phi seam report",
        "",
        "**Run date:** 2 August 2026  ",
        f"**Frozen protocol:** `{PROTOCOL.name}`  ",
        f"**Verdict:** **{verdict}**",
        "",
        "## Answer first",
        "",
        "T329 followed only independently detected binary mergers in which one released bubble ID",
        "continued from child to parent. The inherited bubble's direction immediately before the merger",
        "was compared with its direction immediately after it. Left/right mergers were reflected using",
        "the observed side of the joining child, never by selecting the sign closest to Phi.",
        "",
        f"Eligible seams were `{diagnostics.get('calibration_eligible', 0)}` calibration,",
        f"`{diagnostics.get('evaluation_eligible', 0)}` evaluation and",
        f"`{diagnostics.get('holdout_eligible', 0)}` holdout.",
        "",
        "## Frozen candidate ranking",
        "",
        "Lower circular distance is better.",
        "",
        "| split | rank | candidate | increment | mean loss | median loss |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for split in ("evaluation", "holdout"):
        ranked = sorted(CANDIDATES, key=lambda name: candidate_summary[split][name]["mean"])
        for rank, candidate in enumerate(ranked, 1):
            record = candidate_summary[split][candidate]
            report_lines.append(
                f"| {split} | {rank} | {candidate} | {CANDIDATES[candidate]:.9f} | "
                f"{record['mean']:.6f} | {record['median']:.6f} |"
            )
    report_lines.extend(
        [
            "",
            "## Phi comparisons",
            "",
            "Phi-minus-rival differences are negative when Phi is better.",
            "",
            "| split | rival | mean difference | 95% video-cluster interval |",
            "|---|---|---:|---:|",
        ]
    )
    for split in ("evaluation", "holdout"):
        for rival, record in comparisons[split].items():
            report_lines.append(
                f"| {split} | {rival} | {record['mean']:+.6f} | "
                f"[{record['ci_low']:+.6f}, {record['ci_high']:+.6f}] |"
            )
    report_lines.extend(["", "## Frozen controls", ""])
    for split in ("evaluation", "holdout"):
        report_lines.append(f"### {split}")
        report_lines.append("")
        for field in ("real_minus_broken", "real_minus_contact_scramble", "real_minus_preordinary"):
            record = control_summary[split][field]
            report_lines.append(
                f"- `{field}`: `{record['mean']:+.6f}` "
                f"(95% `{record['ci_low']:+.6f}` to `{record['ci_high']:+.6f}`; "
                f"{record['events']} events, {record['videos']} videos)."
            )
        report_lines.append("")
    report_lines.extend(
        [
            "## Information³ bookkeeping",
            "",
            "The declared contact decomposition satisfied",
            "",
            "\\[",
            "x_{AA}=(x_{AB}+x_{BA})\\bmod2",
            "\\]",
            "",
            f"with maximum numerical discrepancy `{diagnostics['information3_max_identity_error']:.3e}`.",
            "This validates the decomposition but is not evidence for Phi.",
            "",
            "## Resolution and scope",
            "",
            f"The nearest fixed candidate was `{resolution['nearest_fixed_candidate']}`. Its one-step",
            f"separation from exact Phi was `{resolution['one_step_separation_ara']:.9f}` ARA, while the",
            f"median estimated seam-turn grain was `{resolution['median_turn_grain_ara']:.9f}` ARA.",
            "",
            "The archive contains too few repeated merger lineages for a Fibonacci near-return test.",
            "Therefore T329 is a one-step handover test only.",
            "",
            "## Frozen gates",
            "",
        ]
    )
    for gate, value in gates.items():
        report_lines.append(f"- `{gate}`: **{value}**")
    report_lines.extend(
        [
            "",
            "## Reproduction",
            "",
            f"- production: `work/{Path(__file__).name}`",
            "- independent validator: `work/validate_t329_actual_handover_phi_seam.py`",
            f"- result JSON: `{result_path.name}`",
            f"- validation JSON: `{PREFIX}_VALIDATION.json`",
            f"- events: `results/{event_output.name}`",
            f"- candidate scores: `results/{score_output.name}`",
            f"- controls: `results/{control_output.name}`",
            f"- figure: `{figure_path.name}`",
            "",
        ]
    )
    report_path = HERE / f"{PREFIX}_REPORT_2026-08-02.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "gates": gates, "diagnostics": diagnostics}, indent=2))


if __name__ == "__main__":
    main()
