#!/usr/bin/env python3
"""Reproduce T315/H2 from the public Rønne Å Level-3 files.

The script downloads and checks the registered source archives when absent,
extracts the untouched cross-section peaks, scores the frozen landmarks, and
writes tables, a JSON result, and a diagnostic figure.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_ronne_aa"

DOWNLOADS = {
    "Readme.txt": (
        "https://ndownloader.figshare.com/files/46579429",
        "9c75f7b197e9c19450346af41c8f553c",
    ),
    "Ground_truth_bathymetry_Level_3.zip": (
        "https://ndownloader.figshare.com/files/46539463",
        "5b1dd21c4f8f47f1314d9187f6552751",
    ),
    "Ground_truth_velocimetry_OttMFPro_Level_3.zip": (
        "https://ndownloader.figshare.com/files/46539469",
        "fe3987c878caa430627c76418ed20db3",
    ),
    "Image_velocimetry_Level_3.zip": (
        "https://ndownloader.figshare.com/files/46539562",
        "51abc7e2198f87c682fec7c36db890e8",
    ),
}

PAIRED_SECTIONS = (1, 2, 3, 5, 6)
PHI = (1.0 + math.sqrt(5.0)) / 2.0
ANTI_PHI = 2.0 - PHI
THREE_EIGHTHS = 3.0 / 8.0
LANDMARK_GAP = ANTI_PHI - THREE_EIGHTHS
CANDIDATES = {
    "one_third": 1.0 / 3.0,
    "three_eighths": THREE_EIGHTHS,
    "anti_phi": ANTI_PHI,
    "two_fifths": 0.4,
    "half": 0.5,
    "ridge": 1.0,
}


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ensure_sources() -> dict[str, dict[str, object]]:
    SOURCE.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict[str, object]] = {}
    for name, (url, expected) in DOWNLOADS.items():
        path = SOURCE / name
        if not path.exists():
            urllib.request.urlretrieve(url, path)
        actual = md5(path)
        if actual.lower() != expected.lower():
            raise RuntimeError(f"MD5 mismatch for {name}: {actual} != {expected}")
        manifest[name] = {
            "url": url,
            "bytes": path.stat().st_size,
            "md5": actual,
        }
        if path.suffix.lower() == ".zip":
            dest = SOURCE / path.stem
            if not dest.exists():
                with zipfile.ZipFile(path) as zf:
                    zf.extractall(dest)
    return manifest


def source_dir(stem: str) -> Path:
    outer = SOURCE / stem
    inner = outer / stem
    return inner if inner.exists() else outer


def section_number(path: Path) -> int:
    match = re.search(r"XS(\d+)", path.name)
    if not match:
        raise ValueError(path.name)
    return int(match.group(1))


def chainage(path: Path) -> float:
    match = re.search(r"Chainage_([0-9.]+)", path.name)
    if not match:
        return float("nan")
    return float(match.group(1).rstrip("."))


def ara_coordinate(position: float, left_bank: float, right_bank: float) -> float:
    return 2.0 * (position - left_bank) / (right_bank - left_bank)


def sample_resolution_ara(values: pd.Series, width: float) -> float:
    unique = np.sort(np.unique(values.to_numpy(dtype=float)))
    steps = np.diff(unique)
    steps = steps[steps > 1e-12]
    if len(steps) == 0:
        return float("nan")
    return 2.0 * float(np.median(steps)) / width


def candidate_distance(x: float, low: float) -> float:
    if math.isclose(low, 1.0):
        return abs(x - 1.0)
    return min(abs(x - low), abs(x - (2.0 - low)))


def score_candidates(rows: pd.DataFrame, value_col: str, field: str) -> pd.DataFrame:
    out = []
    values = rows[value_col].to_numpy(dtype=float)
    for name, low in CANDIDATES.items():
        distances = np.array([candidate_distance(x, low) for x in values])
        out.append(
            {
                "field": field,
                "candidate": name,
                "low_landmark": low,
                "high_landmark": 2.0 - low if low != 1.0 else 1.0,
                "n": len(values),
                "mean_abs_distance": float(distances.mean()),
                "median_abs_distance": float(np.median(distances)),
                "max_abs_distance": float(distances.max()),
            }
        )
    result = pd.DataFrame(out).sort_values("mean_abs_distance", ignore_index=True)
    result["rank"] = np.arange(1, len(result) + 1)
    return result


def bootstrap_delta(values: np.ndarray, iterations: int = 20000) -> dict[str, float]:
    """Delta = mean distance(Phi) - mean distance(3/8); negative favours Phi."""
    per_row = np.array(
        [
            candidate_distance(x, ANTI_PHI)
            - candidate_distance(x, THREE_EIGHTHS)
            for x in values
        ]
    )
    rng = np.random.default_rng(315)
    draws = rng.choice(per_row, size=(iterations, len(per_row)), replace=True).mean(axis=1)
    return {
        "observed": float(per_row.mean()),
        "ci95_low": float(np.quantile(draws, 0.025)),
        "ci95_high": float(np.quantile(draws, 0.975)),
        "bootstrap_probability_phi_closer": float(np.mean(draws < 0.0)),
    }


def nested_landmark_audit(values: np.ndarray) -> dict[str, object]:
    folded = np.minimum(values, 2.0 - values)
    above_phi = folded >= ANTI_PHI
    below_three_eighths = folded <= THREE_EIGHTHS
    between = ~(above_phi | below_three_eighths)
    return {
        "n": int(len(values)),
        "folded_at_or_above_anti_phi": int(above_phi.sum()),
        "folded_at_or_below_three_eighths": int(below_three_eighths.sum()),
        "folded_between_the_two": int(between.sum()),
        "warning": (
            "For any folded coordinate at or above anti-Phi, distance(Phi) minus "
            "distance(3/8) is forced to equal -(anti-Phi-3/8). This is nested-landmark "
            "arithmetic, not an empirical preference. Coordinates below 3/8 force the "
            "opposite sign. Only coordinates within the 0.006966 interval can distinguish "
            "the two by location alone, and then only if measurement resolution permits."
        ),
    }


def extract_direct_and_bed() -> tuple[pd.DataFrame, dict[int, pd.DataFrame], dict[int, pd.DataFrame]]:
    vdir = source_dir("Ground_truth_velocimetry_OttMFPro_Level_3")
    bdir = source_dir("Ground_truth_bathymetry_Level_3")
    vfiles = {section_number(p): p for p in vdir.glob("*.csv")}
    bfiles = {section_number(p): p for p in bdir.glob("*.csv")}
    rows = []
    velocity_profiles: dict[int, pd.DataFrame] = {}
    bed_profiles: dict[int, pd.DataFrame] = {}

    for section in PAIRED_SECTIONS:
        v = pd.read_csv(vfiles[section])
        b = pd.read_csv(bfiles[section])
        v.columns = [c.strip() for c in v.columns]
        b.columns = [c.strip() for c in b.columns]
        lateral = v["Distance along line (m)"].astype(float)
        speed = v["Surface velocity (cm/s)"].astype(float)
        left = float(lateral.min())
        right = float(lateral.max())
        width = right - left
        endpoint_speeds = speed[(lateral == left) | (lateral == right)].to_numpy()
        if len(endpoint_speeds) != 2 or not np.allclose(endpoint_speeds, 0.0):
            raise RuntimeError(f"XS{section} does not have two zero-velocity wet-bank endpoints")

        flow_candidates = v.loc[speed == speed.max(), "Distance along line (m)"].astype(float)
        flow_position = float(flow_candidates.median())
        flow_ara = ara_coordinate(flow_position, left, right)

        wet_bed = b[
            (b["XS coordinate (m)"].astype(float) >= left)
            & (b["XS coordinate (m)"].astype(float) <= right)
        ].copy()
        minimum = wet_bed["Elevation"].astype(float).min()
        depth_candidates = wet_bed.loc[
            wet_bed["Elevation"].astype(float) == minimum,
            "XS coordinate (m)",
        ].astype(float)
        depth_position = float(depth_candidates.median())
        depth_ara = ara_coordinate(depth_position, left, right)

        v_profile = pd.DataFrame(
            {
                "ara": [ara_coordinate(x, left, right) for x in lateral],
                "speed": speed,
            }
        ).sort_values("ara")
        b_profile = pd.DataFrame(
            {
                "ara": [
                    ara_coordinate(x, left, right)
                    for x in wet_bed["XS coordinate (m)"].astype(float)
                ],
                "elevation": wet_bed["Elevation"].astype(float),
            }
        ).sort_values("ara")
        velocity_profiles[section] = v_profile
        bed_profiles[section] = b_profile

        flow_resolution = sample_resolution_ara(lateral, width)
        depth_resolution = sample_resolution_ara(
            wet_bed["XS coordinate (m)"].astype(float), width
        )
        rows.append(
            {
                "section": f"XS{section}",
                "section_number": section,
                "chainage_m": chainage(vfiles[section]),
                "left_bank_m": left,
                "right_bank_m": right,
                "wet_width_m": width,
                "flow_position_m": flow_position,
                "flow_ara": flow_ara,
                "flow_resolution_ara": flow_resolution,
                "flow_halfstep_ara": flow_resolution / 2.0,
                "depth_position_m": depth_position,
                "depth_ara": depth_ara,
                "depth_resolution_ara": depth_resolution,
                "depth_halfstep_ara": depth_resolution / 2.0,
                "flow_depth_signed_separation_ara": flow_ara - depth_ara,
                "flow_depth_abs_separation_ara": abs(flow_ara - depth_ara),
                "flow_phi_distance": candidate_distance(flow_ara, ANTI_PHI),
                "flow_three_eighths_distance": candidate_distance(flow_ara, THREE_EIGHTHS),
                "depth_phi_distance": candidate_distance(depth_ara, ANTI_PHI),
                "depth_three_eighths_distance": candidate_distance(depth_ara, THREE_EIGHTHS),
            }
        )
    return pd.DataFrame(rows), velocity_profiles, bed_profiles


def extract_piv(bank_rows: pd.DataFrame) -> pd.DataFrame:
    pdir = source_dir("Image_velocimetry_Level_3")
    pfiles = {section_number(p): p for p in pdir.glob("XS*.csv")}
    out = []
    for section in PAIRED_SECTIONS:
        p = pd.read_csv(pfiles[section])
        p.columns = [c.strip() for c in p.columns]
        left = float(bank_rows.loc[bank_rows.section_number == section, "left_bank_m"].iloc[0])
        right = float(bank_rows.loc[bank_rows.section_number == section, "right_bank_m"].iloc[0])
        width = right - left
        p = p[
            (p["Distance along line (m)"].astype(float) >= left)
            & (p["Distance along line (m)"].astype(float) <= right)
        ].copy()
        p["line_key"] = p["Distance along line (m)"].astype(float).round(6)
        p["abs_offset"] = p["Distance from line (m)"].astype(float).abs()
        nearest_idx = p.groupby("line_key", sort=True)["abs_offset"].idxmin()
        cut = p.loc[nearest_idx].copy().sort_values("line_key")
        vmax = cut["total velocity"].astype(float).max()
        peak = cut.loc[cut["total velocity"].astype(float) == vmax, "line_key"].astype(float)
        peak_position = float(peak.median())
        resolution = sample_resolution_ara(cut["line_key"].astype(float), width)
        out.append(
            {
                "section": f"XS{section}",
                "section_number": section,
                "piv_peak_position_m": peak_position,
                "piv_flow_ara": ara_coordinate(peak_position, left, right),
                "piv_resolution_ara": resolution,
                "piv_halfstep_ara": resolution / 2.0,
                "piv_points_on_nearest_line_cut": int(len(cut)),
                "piv_phi_distance": candidate_distance(
                    ara_coordinate(peak_position, left, right), ANTI_PHI
                ),
                "piv_three_eighths_distance": candidate_distance(
                    ara_coordinate(peak_position, left, right), THREE_EIGHTHS
                ),
            }
        )
    return pd.DataFrame(out)


def leave_one_out_winners(rows: pd.DataFrame, column: str) -> list[str]:
    winners = []
    for held in rows.index:
        train = rows.drop(index=held)
        scores = score_candidates(train, column, "loo")
        winners.append(str(scores.iloc[0]["candidate"]))
    return winners


def plot_result(
    rows: pd.DataFrame,
    piv: pd.DataFrame,
    scores: pd.DataFrame,
    vprofiles: dict[int, pd.DataFrame],
    bprofiles: dict[int, pd.DataFrame],
) -> None:
    width, height = 2400, 1750
    image = Image.new("RGB", (width, height), "#f7f9fc")
    draw = ImageDraw.Draw(image)
    font_path = Path(r"C:\Windows\Fonts\arial.ttf")
    bold_path = Path(r"C:\Windows\Fonts\arialbd.ttf")

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        path = bold_path if bold else font_path
        return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()

    title_font, panel_font, body_font, small_font = font(42, True), font(26, True), font(20), font(17)
    orange, blue, purple, green, charcoal = "#df8b2f", "#2f6eae", "#8e44ad", "#27966a", "#364152"
    draw.text((70, 35), "T315 / H2 — Rønne Å motion, accumulated structure, and the thalweg", fill="#172033", font=title_font)
    draw.text((70, 90), "Untouched public cross-sections · lower candidate distance is better · thalweg view is not double-counted", fill="#536174", font=body_font)

    panels = [(55, 145, 1180, 865), (1220, 145, 2345, 865), (55, 905, 1180, 1685), (1220, 905, 2345, 1685)]
    for box in panels:
        draw.rounded_rectangle(box, radius=22, fill="white", outline="#ccd5e2", width=2)

    def ara_x(x: float, left: int, right: int) -> float:
        return left + (right - left) * x / 2.0

    def landmark_lines(box: tuple[int, int, int, int], horizontal: bool = False) -> None:
        x0, y0, x1, y1 = box
        if not horizontal:
            for value, colour in [(ANTI_PHI, purple), (PHI, purple), (THREE_EIGHTHS, green), (2 - THREE_EIGHTHS, green), (1.0, charcoal)]:
                px = ara_x(value, x0, x1)
                draw.line((px, y0, px, y1), fill=colour, width=2)
        else:
            for value, colour in [(ANTI_PHI, purple), (PHI, purple), (THREE_EIGHTHS, green), (2 - THREE_EIGHTHS, green), (1.0, charcoal)]:
                py = y1 - (y1 - y0) * value / 2.0
                draw.line((x0, py, x1, py), fill=colour, width=2)

    # A — raw profiles.
    box = panels[0]
    draw.text((box[0] + 25, box[1] + 20), "A. Five raw ARA diameter cuts", fill="#172033", font=panel_font)
    draw.text((box[0] + 25, box[1] + 58), "orange rises with speed · blue falls with bed depth", fill="#536174", font=small_font)
    plot = (box[0] + 85, box[1] + 105, box[2] - 35, box[3] - 65)
    landmark_lines(plot)
    offsets = np.linspace(plot[1] + 55, plot[3] - 55, len(rows))
    for cy, row in zip(offsets, rows.itertuples()):
        sec = int(row.section_number)
        vp, bp = vprofiles[sec], bprofiles[sec]
        speed = vp["speed"].to_numpy(dtype=float)
        speed = speed / max(speed.max(), 1e-12)
        elev = bp["elevation"].to_numpy(dtype=float)
        depth = (elev.max() - elev) / max(elev.max() - elev.min(), 1e-12)
        vpoints = [(ara_x(float(x), plot[0], plot[2]), cy - 28 * float(v)) for x, v in zip(vp["ara"], speed)]
        bpoints = [(ara_x(float(x), plot[0], plot[2]), cy + 28 * float(v)) for x, v in zip(bp["ara"], depth)]
        draw.line(vpoints, fill=orange, width=4)
        draw.line(bpoints, fill=blue, width=4)
        draw.text((plot[0] - 55, cy - 10), row.section, fill=charcoal, font=small_font)
        for x, colour, shift in [(row.flow_ara, orange, -28), (row.depth_ara, blue, 28)]:
            px = ara_x(float(x), plot[0], plot[2])
            draw.ellipse((px - 6, cy + shift - 6, px + 6, cy + shift + 6), fill=colour)
    draw.text((plot[0], plot[3] + 17), "0", fill=charcoal, font=small_font)
    draw.text((ara_x(1, plot[0], plot[2]) - 5, plot[3] + 17), "1", fill=charcoal, font=small_font)
    draw.text((plot[2] - 10, plot[3] + 17), "2", fill=charcoal, font=small_font)

    # B — peak locations and resolution.
    box = panels[1]
    draw.text((box[0] + 25, box[1] + 20), "B. Peak locations and sampling resolution", fill="#172033", font=panel_font)
    draw.text((box[0] + 25, box[1] + 58), "error bars are half one raw sampling step", fill="#536174", font=small_font)
    plot = (box[0] + 110, box[1] + 115, box[2] - 35, box[3] - 90)
    landmark_lines(plot)
    ys = np.linspace(plot[1] + 50, plot[3] - 50, len(rows))
    for cy, row in zip(ys, rows.itertuples()):
        draw.text((plot[0] - 60, cy - 10), row.section, fill=charcoal, font=small_font)
        for value, halfstep, colour, dy in [
            (row.flow_ara, row.flow_halfstep_ara, orange, -14),
            (row.depth_ara, row.depth_halfstep_ara, blue, 14),
        ]:
            px, lo, hi = ara_x(value, plot[0], plot[2]), ara_x(value - halfstep, plot[0], plot[2]), ara_x(value + halfstep, plot[0], plot[2])
            draw.line((lo, cy + dy, hi, cy + dy), fill=colour, width=4)
            draw.line((lo, cy + dy - 6, lo, cy + dy + 6), fill=colour, width=3)
            draw.line((hi, cy + dy - 6, hi, cy + dy + 6), fill=colour, width=3)
            draw.ellipse((px - 7, cy + dy - 7, px + 7, cy + dy + 7), fill=colour)
        pvalue = float(piv.loc[piv.section_number == row.section_number, "piv_flow_ara"].iloc[0])
        px = ara_x(pvalue, plot[0], plot[2])
        draw.line((px - 7, cy - 34, px + 7, cy - 20), fill="#9a5b0a", width=3)
        draw.line((px - 7, cy - 20, px + 7, cy - 34), fill="#9a5b0a", width=3)
    draw.text((plot[0], plot[3] + 17), "orange: direct motion   blue: thalweg point   ×: image-motion proxy", fill="#536174", font=small_font)

    # C — thalweg path.
    box = panels[2]
    draw.text((box[0] + 25, box[1] + 20), "C. Dedicated longitudinal thalweg cut", fill="#172033", font=panel_font)
    draw.text((box[0] + 25, box[1] + 58), "deepest points linked in source chainage order — diagnostic, not a second sample", fill="#536174", font=small_font)
    plot = (box[0] + 95, box[1] + 110, box[2] - 40, box[3] - 75)
    landmark_lines(plot, horizontal=True)
    ordered = rows.sort_values("chainage_m")
    cmin, cmax = float(ordered.chainage_m.min()), float(ordered.chainage_m.max())
    points = []
    for row in ordered.itertuples():
        px = plot[0] + (plot[2] - plot[0]) * (row.chainage_m - cmin) / max(cmax - cmin, 1e-12)
        py = plot[3] - (plot[3] - plot[1]) * row.depth_ara / 2.0
        points.append((px, py))
    draw.line(points, fill=blue, width=6)
    for (px, py), row in zip(points, ordered.itertuples()):
        draw.ellipse((px - 9, py - 9, px + 9, py + 9), fill=blue)
        draw.text((px + 8, py - 27), row.section, fill=charcoal, font=small_font)
    draw.text((plot[0], plot[3] + 20), f"chainage {cmin:.0f} m", fill=charcoal, font=small_font)
    draw.text((plot[2] - 145, plot[3] + 20), f"{cmax:.0f} m", fill=charcoal, font=small_font)
    draw.text((plot[0], plot[1] - 25), "ARA 2", fill=charcoal, font=small_font)
    draw.text((plot[0], plot[3] + 2), "ARA 0", fill=charcoal, font=small_font)

    # D — candidate losses.
    box = panels[3]
    draw.text((box[0] + 25, box[1] + 20), "D. Frozen candidate competition", fill="#172033", font=panel_font)
    draw.text((box[0] + 25, box[1] + 58), "mean symmetric landmark distance · lower is better", fill="#536174", font=small_font)
    plot = (box[0] + 90, box[1] + 120, box[2] - 35, box[3] - 105)
    fields = [("direct_flow", orange), ("bed_structure", blue), ("piv_flow_proxy", "#9a5b0a")]
    max_value = float(scores["mean_abs_distance"].max()) * 1.08
    names = list(CANDIDATES)
    group_width = (plot[2] - plot[0]) / len(names)
    bar_width = group_width * 0.22
    for j, name in enumerate(names):
        centre = plot[0] + group_width * (j + 0.5)
        for k, (field_name, colour) in enumerate(fields):
            value = float(scores[(scores.field == field_name) & (scores.candidate == name)]["mean_abs_distance"].iloc[0])
            bh = (plot[3] - plot[1]) * value / max_value
            bx0 = centre + (k - 1) * bar_width - bar_width / 2
            draw.rectangle((bx0, plot[3] - bh, bx0 + bar_width, plot[3]), fill=colour)
        label = {"one_third": "1/3", "three_eighths": "3/8", "anti_phi": "2−φ", "two_fifths": "0.4", "half": "0.5", "ridge": "ridge"}[name]
        draw.text((centre - 18, plot[3] + 16), label, fill=charcoal, font=small_font)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill=charcoal, width=2)
    draw.text((plot[0], plot[3] + 55), "orange direct flow   blue bed/thalweg   brown image-flow proxy", fill="#536174", font=small_font)

    image.save(HERE / "H2_RONNE_AA_PHI_THREE_EIGHTHS_FIGURE.png")


def main() -> None:
    manifest = ensure_sources()
    rows, vprofiles, bprofiles = extract_direct_and_bed()
    piv = extract_piv(rows)
    rows = rows.merge(piv, on=["section", "section_number"], how="left")

    score_parts = [
        score_candidates(rows, "flow_ara", "direct_flow"),
        score_candidates(rows, "depth_ara", "bed_structure"),
        score_candidates(rows, "piv_flow_ara", "piv_flow_proxy"),
    ]
    scores = pd.concat(score_parts, ignore_index=True)

    loo = {
        "direct_flow": leave_one_out_winners(rows, "flow_ara"),
        "bed_structure": leave_one_out_winners(rows, "depth_ara"),
        "piv_flow_proxy": leave_one_out_winners(rows, "piv_flow_ara"),
    }
    resolution = {
        "landmark_gap_ara": LANDMARK_GAP,
        "required_full_step_smaller_than_gap": True,
        "direct_flow_sections_passing": int((rows["flow_resolution_ara"] < LANDMARK_GAP).sum()),
        "bed_sections_passing": int((rows["depth_resolution_ara"] < LANDMARK_GAP).sum()),
        "piv_sections_passing": int((rows["piv_resolution_ara"] < LANDMARK_GAP).sum()),
        "eligible_sections": int(len(rows)),
    }

    winners = {}
    for field in ("direct_flow", "bed_structure", "piv_flow_proxy"):
        field_scores = scores[scores.field == field].sort_values("mean_abs_distance")
        winners[field] = {
            "winner": str(field_scores.iloc[0]["candidate"]),
            "runner_up": str(field_scores.iloc[1]["candidate"]),
            "winner_mean_distance": float(field_scores.iloc[0]["mean_abs_distance"]),
            "runner_up_mean_distance": float(field_scores.iloc[1]["mean_abs_distance"]),
            "leave_one_out_winners": loo[field],
        }

    result = {
        "test_id": "T315/H2",
        "source_doi": "10.11583/DTU.24168960",
        "source_manifest": manifest,
        "constants": {
            "phi": PHI,
            "anti_phi": ANTI_PHI,
            "three_eighths": THREE_EIGHTHS,
            "absolute_gap": LANDMARK_GAP,
        },
        "n_paired_sections": int(len(rows)),
        "resolution_gate": resolution,
        "candidate_winners": winners,
        "phi_minus_three_eighths_distance_delta": {
            "direct_flow": bootstrap_delta(rows["flow_ara"].to_numpy()),
            "bed_structure": bootstrap_delta(rows["depth_ara"].to_numpy()),
            "piv_flow_proxy": bootstrap_delta(rows["piv_flow_ara"].to_numpy()),
        },
        "nested_landmark_artifact_audit": {
            "direct_flow": nested_landmark_audit(rows["flow_ara"].to_numpy()),
            "bed_structure": nested_landmark_audit(rows["depth_ara"].to_numpy()),
            "piv_flow_proxy": nested_landmark_audit(rows["piv_flow_ara"].to_numpy()),
        },
        "dedicated_thalweg": {
            "ordered_sections": rows.sort_values("chainage_m")["section"].tolist(),
            "ordered_ara": rows.sort_values("chainage_m")["depth_ara"].tolist(),
            "is_independent_of_bed_structure": False,
            "reason": "The public Level-3 ground-truth bathymetry supplies six discrete cross-sections, not a dense longitudinal bed field; XS4 lacks paired measured wet-bank endpoints and is excluded from normalized scoring.",
        },
        "benchmark_verdict": "The source is valid and reproducible. Direct flow is closest to ridge 1 in the pooled score and all five leave-one-out folds; bed/thalweg is closest to the mirrored half pair overall; the image-flow proxy is also closest to half in all five leave-one-out folds.",
        "geometry_verdict": "NOT SUPPORTED for the frozen claim that flow cores occupy Phi and accumulated structure occupies 3/8, because fixed rivals win by much larger margins. Separately, the exact Phi-versus-3/8 numerical distinction is INCONCLUSIVE for the primary direct measures because no section resolves their 0.006966-ARA gap.",
    }

    rows.to_csv(HERE / "H2_RONNE_AA_PHI_THREE_EIGHTHS_SECTION_RESULTS.csv", index=False)
    scores.to_csv(HERE / "H2_RONNE_AA_PHI_THREE_EIGHTHS_CANDIDATE_SUMMARY.csv", index=False)
    with (HERE / "H2_RONNE_AA_PHI_THREE_EIGHTHS_RESULTS.json").open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    plot_result(rows, piv, scores, vprofiles, bprofiles)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
