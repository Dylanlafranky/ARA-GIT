#!/usr/bin/env python3
"""T308 frozen Phi temporal-ruler orbital probe.

Downloads public geometric vector tables from NASA/JPL Horizons, retains the
raw responses, and evaluates the frozen reconstruction in the T308 protocol.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data" / "t308"
RESULTS_PATH = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_RESULTS.json"
ROWS_PATH = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_ROWS.csv"
FIGURE_PATH = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE.png"
REPORT_PATH = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_REPORT_2026-07-31.md"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
CANDIDATES = [
    ("1.25", 1.25),
    ("sqrt2", math.sqrt(2.0)),
    ("1.5", 1.5),
    ("phi", PHI),
    ("1.75", 1.75),
    ("2", 2.0),
    ("e", math.e),
]
HORIZON_RATIOS = [0.25, 0.375, 0.5, 0.75, 1.0, 1.5, 2.0]
START = "2000-01-01"
STOP = "2026-01-01"
SPLIT_JD = 2456293.5  # 2013-01-01 00:00 TDB


@dataclass(frozen=True)
class SystemSpec:
    key: str
    label: str
    command: str
    center: str


SYSTEMS = [
    SystemSpec("moon_earth", "Moon relative to Earth", "301", "500@399"),
    SystemSpec("earth_sun", "Earth relative to Sun", "399", "500@10"),
]


def horizons_url(spec: SystemSpec) -> str:
    params = {
        "format": "text",
        "COMMAND": f"'{spec.command}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'VECTORS'",
        "CENTER": f"'{spec.center}'",
        "START_TIME": f"'{START}'",
        "STOP_TIME": f"'{STOP}'",
        "STEP_SIZE": "'1d'",
        "TIME_TYPE": "'TDB'",
        "REF_PLANE": "'ECLIPTIC'",
        "REF_SYSTEM": "'ICRF'",
        "OUT_UNITS": "'KM-S'",
        "VEC_TABLE": "'2'",
        "VEC_CORR": "'NONE'",
        "CSV_FORMAT": "'YES'",
        "VEC_LABELS": "'YES'",
    }
    return "https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(
        params, safe="'@"
    )


def fetch_system(spec: SystemSpec, force: bool = False) -> tuple[Path, Path]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = DATA_DIR / f"{spec.key}_horizons_raw.txt"
    csv_path = DATA_DIR / f"{spec.key}_vectors.csv"
    if raw_path.exists() and csv_path.exists() and not force:
        return raw_path, csv_path

    request = urllib.request.Request(
        horizons_url(spec),
        headers={"User-Agent": "ARA-T308-reproducible-public-data-probe/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        raw = response.read().decode("utf-8")
    if "$$SOE" not in raw or "$$EOE" not in raw:
        raise RuntimeError(f"Horizons response for {spec.key} has no ephemeris block")
    raw_path.write_text(raw, encoding="utf-8")

    body = raw.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    parsed_rows = []
    for row in csv.reader(io.StringIO(body.strip())):
        if not row or len(row) < 8:
            continue
        parsed_rows.append(
            {
                "jd_tdb": float(row[0]),
                "calendar_tdb": row[1].strip(),
                "x_km": float(row[2]),
                "y_km": float(row[3]),
                "z_km": float(row[4]),
                "vx_km_s": float(row[5]),
                "vy_km_s": float(row[6]),
                "vz_km_s": float(row[7]),
            }
        )
    if len(parsed_rows) < 9000:
        raise RuntimeError(
            f"Unexpectedly short Horizons table for {spec.key}: {len(parsed_rows)}"
        )
    pd.DataFrame(parsed_rows).to_csv(csv_path, index=False)
    return raw_path, csv_path


def load_system(spec: SystemSpec) -> pd.DataFrame:
    path = DATA_DIR / f"{spec.key}_vectors.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}; rerun with --fetch")
    frame = pd.read_csv(path)
    phase = np.unwrap(np.arctan2(frame["y_km"].to_numpy(), frame["x_km"].to_numpy()))
    if np.median(np.diff(phase)) < 0:
        phase = -phase
    frame["phase_unwrapped"] = phase
    return frame


def estimate_period_days(frame: pd.DataFrame) -> float:
    calibration = frame[frame["jd_tdb"] < SPLIT_JD]
    omega = np.diff(calibration["phase_unwrapped"].to_numpy()) / np.diff(
        calibration["jd_tdb"].to_numpy()
    )
    omega = omega[np.isfinite(omega) & (omega > 0)]
    return float(2.0 * np.pi / np.median(omega))


def phase_at(frame: pd.DataFrame, query_jd: np.ndarray) -> np.ndarray:
    return np.interp(
        query_jd,
        frame["jd_tdb"].to_numpy(),
        frame["phase_unwrapped"].to_numpy(),
    )


def evaluate_half(
    spec: SystemSpec,
    frame: pd.DataFrame,
    period_days: float,
    half: str,
    candidates: list[tuple[str, float]] = CANDIDATES,
) -> pd.DataFrame:
    jd = frame["jd_tdb"].to_numpy()
    if half == "calibration":
        anchors = jd[jd < SPLIT_JD]
    elif half == "evaluation":
        anchors = jd[jd >= SPLIT_JD]
    else:
        raise ValueError(half)

    max_horizon = period_days * max(HORIZON_RATIOS)
    anchors = anchors[anchors + max_horizon <= jd[-1]]
    anchor_phase = phase_at(frame, anchors)
    output: list[dict[str, float | str]] = []

    for horizon_ratio in HORIZON_RATIOS:
        horizon_days = period_days * horizon_ratio
        q3 = phase_at(frame, anchors + horizon_days) - anchor_phase
        x3 = 1.0 - np.cos(q3)
        branch3 = np.sign(np.sin(q3))

        for candidate_name, lam in candidates:
            t1 = horizon_days / (lam * lam)
            t2 = horizon_days / lam
            q1 = phase_at(frame, anchors + t1) - anchor_phase
            q2 = phase_at(frame, anchors + t2) - anchor_phase
            qhat = q2 + lam * (q2 - q1)
            xhat = 1.0 - np.cos(qhat)
            branch_hat = np.sign(np.sin(qhat))

            phase_error = np.abs(qhat - q3)
            ara_error = np.abs(xhat - x3)
            denom = (horizon_days - t1) * (horizon_days - t2)
            curvature_error = phase_error / denom
            branch_match = (branch_hat == branch3).astype(float)

            for idx in range(len(anchors)):
                output.append(
                    {
                        "system": spec.key,
                        "system_label": spec.label,
                        "half": half,
                        "anchor_jd": float(anchors[idx]),
                        "horizon_ratio": float(horizon_ratio),
                        "horizon_days": float(horizon_days),
                        "candidate": candidate_name,
                        "lambda": float(lam),
                        "q1": float(q1[idx]),
                        "q2": float(q2[idx]),
                        "q3_true": float(q3[idx]),
                        "q3_pred": float(qhat[idx]),
                        "x3_true": float(x3[idx]),
                        "x3_pred": float(xhat[idx]),
                        "phase_abs_error": float(phase_error[idx]),
                        "ara_abs_error": float(ara_error[idx]),
                        "curvature_norm_error": float(curvature_error[idx]),
                        "branch_match": float(branch_match[idx]),
                    }
                )
    return pd.DataFrame(output)


def summarise_rows(rows: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        rows.groupby(["system", "system_label", "half", "candidate", "lambda"])
        .agg(
            n=("phase_abs_error", "size"),
            median_phase_error=("phase_abs_error", "median"),
            median_ara_error=("ara_abs_error", "median"),
            median_curvature_error=("curvature_norm_error", "median"),
            branch_accuracy=("branch_match", "mean"),
        )
        .reset_index()
    )
    grouped["curvature_rank"] = grouped.groupby(["system", "half"])[
        "median_curvature_error"
    ].rank(method="min")
    grouped["raw_phase_rank"] = grouped.groupby(["system", "half"])[
        "median_phase_error"
    ].rank(method="min")
    return grouped


def horizon_summary(rows: pd.DataFrame) -> pd.DataFrame:
    return (
        rows.groupby(
            [
                "system",
                "system_label",
                "half",
                "horizon_ratio",
                "candidate",
                "lambda",
            ]
        )
        .agg(
            median_phase_error=("phase_abs_error", "median"),
            median_ara_error=("ara_abs_error", "median"),
            median_curvature_error=("curvature_norm_error", "median"),
            branch_accuracy=("branch_match", "mean"),
        )
        .reset_index()
    )


def block_bootstrap_phi_vs_best(
    rows: pd.DataFrame, system: str, seed: int = 308, repetitions: int = 2000
) -> dict:
    evaluation = rows[(rows["system"] == system) & (rows["half"] == "evaluation")]
    candidate_medians = (
        evaluation.groupby("candidate")["curvature_norm_error"].median().sort_values()
    )
    controls = candidate_medians.drop(index="phi")
    best_control = str(controls.index[0])

    per_anchor = (
        evaluation[evaluation["candidate"].isin(["phi", best_control])]
        .groupby(["anchor_jd", "candidate"])["curvature_norm_error"]
        .median()
        .unstack()
        .dropna()
        .sort_index()
    )
    per_anchor["block"] = np.arange(len(per_anchor)) // 30
    blocks = [group[["phi", best_control]] for _, group in per_anchor.groupby("block")]
    rng = np.random.default_rng(seed)
    differences = []
    for _ in range(repetitions):
        chosen = rng.integers(0, len(blocks), size=len(blocks))
        sample = pd.concat([blocks[i] for i in chosen], ignore_index=True)
        differences.append(
            float(np.median(sample["phi"]) - np.median(sample[best_control]))
        )
    differences = np.asarray(differences)
    observed = float(
        np.median(per_anchor["phi"]) - np.median(per_anchor[best_control])
    )
    return {
        "best_control": best_control,
        "observed_phi_minus_control": observed,
        "bootstrap_ci95": [
            float(np.quantile(differences, 0.025)),
            float(np.quantile(differences, 0.975)),
        ],
        "probability_phi_lower": float(np.mean(differences < 0.0)),
        "n_anchor_rows": int(len(per_anchor)),
        "block_days": 30,
        "repetitions": repetitions,
    }


def run_sweep(spec: SystemSpec, frame: pd.DataFrame, period_days: float) -> pd.DataFrame:
    jd = frame["jd_tdb"].to_numpy()
    max_horizon = period_days * max(HORIZON_RATIOS)
    # The continuous sweep is explicitly exploratory. Weekly anchors keep this
    # diagnostic bounded without changing the frozen fixed-candidate test.
    anchors = jd[(jd >= SPLIT_JD) & (jd + max_horizon <= jd[-1])][::7]
    anchor_phase = phase_at(frame, anchors)
    records = []
    for lam in np.arange(1.20, 2.801, 0.01):
        phase_errors = []
        ara_errors = []
        curvature_errors = []
        branch_matches = []
        for horizon_ratio in HORIZON_RATIOS:
            horizon_days = period_days * horizon_ratio
            q1 = phase_at(frame, anchors + horizon_days / (lam * lam)) - anchor_phase
            q2 = phase_at(frame, anchors + horizon_days / lam) - anchor_phase
            q3 = phase_at(frame, anchors + horizon_days) - anchor_phase
            qhat = q2 + lam * (q2 - q1)
            phase_error = np.abs(qhat - q3)
            ara_error = np.abs((1.0 - np.cos(qhat)) - (1.0 - np.cos(q3)))
            denom = (
                (horizon_days - horizon_days / (lam * lam))
                * (horizon_days - horizon_days / lam)
            )
            phase_errors.append(phase_error)
            ara_errors.append(ara_error)
            curvature_errors.append(phase_error / denom)
            branch_matches.append(
                (np.sign(np.sin(qhat)) == np.sign(np.sin(q3))).astype(float)
            )
        records.append(
            {
                "candidate": f"{lam:.3f}",
                "lambda": float(lam),
                "median_phase_error": float(np.median(np.concatenate(phase_errors))),
                "median_ara_error": float(np.median(np.concatenate(ara_errors))),
                "median_curvature_error": float(
                    np.median(np.concatenate(curvature_errors))
                ),
                "branch_accuracy": float(np.mean(np.concatenate(branch_matches))),
            }
        )
    return pd.DataFrame(records).sort_values("lambda")


def build_figure(
    summary: pd.DataFrame, horizon: pd.DataFrame, sweep: dict[str, pd.DataFrame]
) -> None:
    evaluation = summary[summary["half"] == "evaluation"].copy()
    colors = {"moon_earth": (76, 120, 168), "earth_sun": (227, 156, 54)}
    candidate_order = [name for name, _ in CANDIDATES]
    image = Image.new("RGB", (2400, 1600), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    bold_path = Path("C:/Windows/Fonts/arialbd.ttf")
    font = ImageFont.truetype(str(font_path), 27)
    small = ImageFont.truetype(str(font_path), 22)
    tiny = ImageFont.truetype(str(font_path), 18)
    bold = ImageFont.truetype(str(bold_path), 31)
    title_font = ImageFont.truetype(str(bold_path), 42)

    draw.text(
        (70, 35),
        "T308 — Phi temporal-ruler orbital probe",
        fill=(25, 31, 40),
        font=title_font,
    )
    draw.text(
        (72, 88),
        "JPL Horizons geometric vectors · evaluation half 2013–2025",
        fill=(80, 88, 100),
        font=font,
    )

    panels = [
        (70, 150, 1150, 780),
        (1250, 150, 2330, 780),
        (70, 875, 1150, 1505),
        (1250, 875, 2330, 1505),
    ]

    def panel_frame(box: tuple[int, int, int, int], title: str, subtitle: str):
        left, top, right, bottom = box
        draw.rounded_rectangle(
            box, radius=18, fill=(249, 250, 252), outline=(210, 215, 223), width=2
        )
        draw.text((left + 28, top + 22), title, fill=(35, 42, 52), font=bold)
        draw.text((left + 28, top + 64), subtitle, fill=(95, 103, 114), font=small)
        return left + 95, top + 120, right - 35, bottom - 80

    def bar_panel(
        box: tuple[int, int, int, int],
        metric: str,
        title: str,
        subtitle: str,
        log_scale: bool,
    ):
        x0, y0, x1, y1 = panel_frame(box, title, subtitle)
        draw.line((x0, y1, x1, y1), fill=(80, 85, 94), width=2)
        draw.line((x0, y0, x0, y1), fill=(80, 85, 94), width=2)
        values = []
        system_values = {}
        for system in ["moon_earth", "earth_sun"]:
            subset = (
                evaluation[evaluation["system"] == system]
                .set_index("candidate")
                .reindex(candidate_order)
            )
            arr = subset[metric].to_numpy(dtype=float)
            if log_scale:
                arr = np.log10(np.maximum(arr, 1e-20))
            system_values[system] = arr
            values.extend(arr.tolist())
        vmin = min(values)
        vmax = max(values)
        pad = max((vmax - vmin) * 0.12, 1e-12)
        vmin -= pad
        vmax += pad
        group_width = (x1 - x0) / len(candidate_order)
        bar_width = group_width * 0.27
        phi_index = candidate_order.index("phi")
        phi_left = x0 + phi_index * group_width
        draw.rectangle(
            (phi_left, y0, phi_left + group_width, y1),
            fill=(235, 246, 228),
        )
        for idx, candidate in enumerate(candidate_order):
            center = x0 + (idx + 0.5) * group_width
            for offset, system in [(-0.65, "moon_earth"), (0.05, "earth_sun")]:
                value = system_values[system][idx]
                height = (value - vmin) / (vmax - vmin) * (y1 - y0)
                bx0 = center + offset * bar_width
                bx1 = bx0 + bar_width
                by0 = y1 - height
                draw.rectangle((bx0, by0, bx1, y1), fill=colors[system])
            label_box = draw.textbbox((0, 0), candidate, font=tiny)
            label_w = label_box[2] - label_box[0]
            draw.text(
                (center - label_w / 2, y1 + 15),
                candidate,
                fill=(55, 61, 70),
                font=tiny,
            )
        for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
            yy = y1 - frac * (y1 - y0)
            draw.line((x0, yy, x1, yy), fill=(225, 228, 234), width=1)
            value = vmin + frac * (vmax - vmin)
            label = f"10^{value:.1f}" if log_scale else f"{value:.4g}"
            draw.text((x0 - 82, yy - 10), label, fill=(100, 106, 115), font=tiny)

    bar_panel(
        panels[0],
        "median_curvature_error",
        "Curvature-normalised phase error",
        "Distance-compensated · lower is better · log scale",
        True,
    )
    bar_panel(
        panels[1],
        "median_phase_error",
        "Raw directed-phase error",
        "Median absolute radians · lower is better · log scale",
        True,
    )
    bar_panel(
        panels[2],
        "median_ara_error",
        "ARA-diameter error",
        "Median |predicted − observed| · lower is better",
        False,
    )

    x0, y0, x1, y1 = panel_frame(
        panels[3],
        "Exploratory multiplier sweep",
        "Weekly evaluation anchors · lower is better · log scale",
    )
    draw.line((x0, y1, x1, y1), fill=(80, 85, 94), width=2)
    draw.line((x0, y0, x0, y1), fill=(80, 85, 94), width=2)
    sweep_logs = []
    for frame in sweep.values():
        sweep_logs.extend(
            np.log10(np.maximum(frame["median_curvature_error"].to_numpy(), 1e-20))
        )
    log_min, log_max = min(sweep_logs), max(sweep_logs)
    log_pad = (log_max - log_min) * 0.08
    log_min -= log_pad
    log_max += log_pad
    for system, frame in sweep.items():
        points = []
        for _, row in frame.iterrows():
            px = x0 + (float(row["lambda"]) - 1.2) / (2.8 - 1.2) * (x1 - x0)
            py = y1 - (
                (math.log10(max(float(row["median_curvature_error"]), 1e-20)) - log_min)
                / (log_max - log_min)
                * (y1 - y0)
            )
            points.append((px, py))
        draw.line(points, fill=colors[system], width=4)
        best = frame.loc[frame["median_curvature_error"].idxmin()]
        bx = x0 + (float(best["lambda"]) - 1.2) / (2.8 - 1.2) * (x1 - x0)
        by = y1 - (
            (math.log10(float(best["median_curvature_error"])) - log_min)
            / (log_max - log_min)
            * (y1 - y0)
        )
        draw.ellipse((bx - 8, by - 8, bx + 8, by + 8), fill=colors[system])
    phi_x = x0 + (PHI - 1.2) / (2.8 - 1.2) * (x1 - x0)
    for yy in range(y0, y1, 20):
        draw.line((phi_x, yy, phi_x, min(yy + 10, y1)), fill=(100, 163, 75), width=3)
    draw.text((phi_x + 8, y0 + 5), "φ", fill=(76, 133, 55), font=bold)
    for value in [1.2, 1.6, 2.0, 2.4, 2.8]:
        xx = x0 + (value - 1.2) / (2.8 - 1.2) * (x1 - x0)
        draw.text((xx - 18, y1 + 15), f"{value:.1f}", fill=(80, 86, 95), font=tiny)
    draw.text((x0, y1 + 47), "temporal multiplier λ", fill=(70, 77, 86), font=small)

    draw.rectangle((1620, 110, 1655, 135), fill=colors["moon_earth"])
    draw.text((1665, 108), "Moon/Earth", fill=(60, 66, 75), font=small)
    draw.rectangle((1860, 110, 1895, 135), fill=colors["earth_sun"])
    draw.text((1905, 108), "Earth/Sun", fill=(60, 66, 75), font=small)
    image.save(FIGURE_PATH, quality=95)


SYSTEM_LABELS = {spec.key: spec.label for spec in SYSTEMS}


def verdict(summary: pd.DataFrame, bootstraps: dict[str, dict]) -> tuple[str, list[str]]:
    evaluation = summary[summary["half"] == "evaluation"]
    notes = []
    supported = True
    for spec in SYSTEMS:
        subset = evaluation[evaluation["system"] == spec.key].sort_values(
            "median_curvature_error"
        )
        winner = str(subset.iloc[0]["candidate"])
        phi_row = subset[subset["candidate"] == "phi"].iloc[0]
        notes.append(
            f"{spec.label}: curvature winner {winner}; "
            f"Phi rank {int(phi_row['curvature_rank'])}/7."
        )
        if winner != "phi":
            supported = False
        ci = bootstraps[spec.key]["bootstrap_ci95"]
        if not (ci[1] < 0.0):
            supported = False
    if supported:
        return "SUPPORTED BY THIS PROBE", notes

    phi_wins = 0
    for spec in SYSTEMS:
        subset = evaluation[evaluation["system"] == spec.key]
        phi_rank = int(
            subset[subset["candidate"] == "phi"]["curvature_rank"].iloc[0]
        )
        phi_wins += int(phi_rank == 1)
    if phi_wins == 1:
        return "PARTIAL", notes
    return "NOT SUPPORTED BY THIS PROBE", notes


def write_report(results: dict, summary: pd.DataFrame, horizon: pd.DataFrame) -> None:
    evaluation = summary[summary["half"] == "evaluation"]
    lines = [
        "# T308 — Phi Temporal-Ruler Orbital Probe",
        "",
        "**Date:** 31 July 2026  ",
        f"**Frozen verdict:** **{results['verdict']}**",
        "",
        "## Plain-language result",
        "",
        results["plain_language"],
        "",
        "This was a probe of one specific interpretation: two earlier, geometrically",
        "spaced time slices were used to reconstruct a third orbital state. The",
        "physical orbit was not treated as climbing a structural octave.",
        "",
        "## Post-result methodology diagnosis",
        "",
        results["post_result_diagnosis"],
        "",
        "The frozen verdict is retained. This diagnosis limits its scope: the result",
        "is a rejection of this reconstruction as evidence for Phi, not strong",
        "evidence that no Phi temporal relation exists.",
        "",
        "## Fixed-candidate evaluation results",
        "",
        "| System | Ruler | λ | Phase error | ARA error | Curvature-normalised error | A/B accuracy | Curvature rank |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for spec in SYSTEMS:
        subset = evaluation[evaluation["system"] == spec.key].sort_values("lambda")
        for _, row in subset.iterrows():
            lines.append(
                f"| {spec.label} | {row['candidate']} | {row['lambda']:.6f} | "
                f"{row['median_phase_error']:.8f} | {row['median_ara_error']:.8f} | "
                f"{row['median_curvature_error']:.10g} | {row['branch_accuracy']:.4f} | "
                f"{int(row['curvature_rank'])} |"
            )

    lines.extend(
        [
            "",
            "## Bootstrap comparison",
            "",
        ]
    )
    for spec in SYSTEMS:
        boot = results["bootstrap_phi_vs_best_control"][spec.key]
        lines.append(
            f"- **{spec.label}:** best fixed control `{boot['best_control']}`; "
            f"Phi minus control = `{boot['observed_phi_minus_control']:.10g}`; "
            f"95% block-bootstrap interval "
            f"`[{boot['bootstrap_ci95'][0]:.10g}, {boot['bootstrap_ci95'][1]:.10g}]`; "
            f"P(Phi lower) = `{boot['probability_phi_lower']:.4f}`."
        )

    lines.extend(
        [
            "",
            "## Horizon stability",
            "",
            "| System | H/P | Phi curvature rank | Phi / best-control error |",
            "|---|---:|---:|---:|",
        ]
    )
    eval_horizon = horizon[horizon["half"] == "evaluation"].copy()
    for spec in SYSTEMS:
        for ratio in HORIZON_RATIOS:
            subset = eval_horizon[
                (eval_horizon["system"] == spec.key)
                & (eval_horizon["horizon_ratio"] == ratio)
            ].sort_values("median_curvature_error")
            phi_error = float(
                subset[subset["candidate"] == "phi"][
                    "median_curvature_error"
                ].iloc[0]
            )
            controls = subset[subset["candidate"] != "phi"]
            best_error = float(controls["median_curvature_error"].iloc[0])
            rank = int(
                subset["median_curvature_error"].rank(method="min")[
                    subset["candidate"] == "phi"
                ].iloc[0]
            )
            lines.append(
                f"| {spec.label} | {ratio:.3f} | {rank}/7 | {phi_error / best_error:.4f} |"
            )

    lines.extend(
        [
            "",
            "## What this means for ARA",
            "",
            results["ara_interpretation"],
            "",
            "## Boundaries",
            "",
            "- The result concerns one frozen reconstruction rule, not every possible",
            "  meaning of a Phi handover or temporal-tension path.",
            "- The orbit was reduced through ecliptic longitude and",
            "  `x = 1 − cos(Δθ)`. A different physically declared ARA cut is a new test.",
            "- Daily vectors require linear interpolation for fractional-day Phi slices.",
            "- Daily anchors overlap heavily. The reported uncertainty therefore uses",
            "  30-day block resampling rather than treating every row as independent.",
            "- The continuous multiplier sweep is exploratory and cannot replace the",
            "  frozen fixed-candidate verdict.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python t308_phi_temporal_ruler_orbital_probe.py --fetch",
            "python validate_t308_phi_temporal_ruler_orbital_probe.py",
            "```",
            "",
            "Source: NASA/JPL Horizons geometric vector tables retained under",
            "`analysis/phi_calibration/data/t308/`.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--force-fetch", action="store_true")
    args = parser.parse_args()

    if args.fetch or args.force_fetch:
        for spec in SYSTEMS:
            fetch_system(spec, force=args.force_fetch)

    all_rows = []
    periods = {}
    source_files = {}
    sweep_results: dict[str, pd.DataFrame] = {}
    for spec in SYSTEMS:
        frame = load_system(spec)
        period_days = estimate_period_days(frame)
        periods[spec.key] = period_days
        source_files[spec.key] = {
            "raw": str((DATA_DIR / f"{spec.key}_horizons_raw.txt").relative_to(HERE)),
            "parsed": str((DATA_DIR / f"{spec.key}_vectors.csv").relative_to(HERE)),
            "rows": int(len(frame)),
            "start_jd": float(frame["jd_tdb"].iloc[0]),
            "stop_jd": float(frame["jd_tdb"].iloc[-1]),
        }
        all_rows.append(evaluate_half(spec, frame, period_days, "calibration"))
        all_rows.append(evaluate_half(spec, frame, period_days, "evaluation"))
        sweep_results[spec.key] = run_sweep(spec, frame, period_days)

    rows = pd.concat(all_rows, ignore_index=True)
    rows.to_csv(ROWS_PATH, index=False)
    summary = summarise_rows(rows)
    horizon = horizon_summary(rows)
    bootstraps = {
        spec.key: block_bootstrap_phi_vs_best(rows, spec.key) for spec in SYSTEMS
    }
    frozen_verdict, verdict_notes = verdict(summary, bootstraps)

    sweep_summary = {}
    for spec in SYSTEMS:
        sweep_frame = sweep_results[spec.key]
        best = sweep_frame.loc[sweep_frame["median_curvature_error"].idxmin()]
        sweep_summary[spec.key] = {
            "best_lambda": float(best["lambda"]),
            "best_curvature_error": float(best["median_curvature_error"]),
            "phi_curvature_error_interpolated_nearest_grid": float(
                sweep_frame.iloc[(sweep_frame["lambda"] - PHI).abs().argsort()[:1]][
                    "median_curvature_error"
                ].iloc[0]
            ),
        }

    if frozen_verdict == "SUPPORTED BY THIS PROBE":
        plain = (
            "Phi was the strongest fixed temporal spacing on both declared orbital "
            "systems after compensating for slice-to-target distance. Under this "
            "specific reconstruction, the result supports a Phi temporal ruler."
        )
        ara_interpretation = (
            "The tested Phi-spaced slices behaved like an unusually stable temporal "
            "information lock while structural scale remained fixed. Replication on "
            "a non-orbital continuous system is still required."
        )
    elif frozen_verdict == "PARTIAL":
        plain = (
            "Phi was favoured in only part of the frozen comparison. The probe does "
            "not establish a general Phi temporal ruler, but it identifies a bounded "
            "system or horizon where the relation may be worth decomposing."
        )
        ara_interpretation = (
            "The data distinguish temporal spacing from structural octave, but the "
            "same Phi rule did not transfer cleanly across both orbital identities."
        )
    else:
        plain = (
            "Phi did not uniquely outperform the declared alternative temporal "
            "rulers across both orbital systems. This particular way of turning "
            "Phi-spaced time slices into an information lock is therefore not "
            "supported."
        )
        ara_interpretation = (
            "The null is narrow but useful: merely placing two prior observations on "
            "a Phi ladder is not enough to recover the next ARA state of these "
            "orbits. A better Phi test would need a separately declared handover or "
            "coupling observable rather than temporal spacing alone."
        )

    evaluation_summary = summary[summary["half"] == "evaluation"].copy()
    monotonicity = {}
    for spec in SYSTEMS:
        subset = evaluation_summary[
            evaluation_summary["system"] == spec.key
        ].sort_values("lambda")
        raw_values = subset["median_phase_error"].to_numpy()
        curvature_values = subset["median_curvature_error"].to_numpy()
        monotonicity[spec.key] = {
            "raw_phase_error_strictly_increases_with_lambda": bool(
                np.all(np.diff(raw_values) > 0)
            ),
            "curvature_error_strictly_decreases_with_lambda": bool(
                np.all(np.diff(curvature_values) < 0)
            ),
            "sweep_best_at_upper_boundary": bool(
                sweep_summary[spec.key]["best_lambda"] >= 2.79
            ),
        }
    post_result_diagnosis = (
        "The metric family did not reveal an interior preferred multiplier. In both "
        "systems, raw phase error increased monotonically with λ, while the "
        "distance-normalised curvature error decreased monotonically with λ. The "
        "exploratory sweep then selected its upper boundary (about 2.8). Phi's "
        "fourth-place position is therefore the middle of two opposing monotonic "
        "effects, not evidence that the data naturally settled on another special "
        "constant. This confirms the user's pre-run concern that the probe was "
        "reasonable but probably not the best operationalisation of the geometry."
    )

    results = {
        "test": "T308",
        "frozen_protocol": "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_PROTOCOL_v1_FROZEN.md",
        "date": "2026-07-31",
        "source": {
            "provider": "NASA/JPL Horizons",
            "api_documentation": "https://ssd-api.jpl.nasa.gov/doc/horizons.html",
            "query_interval": [START, STOP],
            "step": "1 day",
            "frame": "ecliptic J2000 / ICRF",
            "correction": "NONE (geometric vectors)",
            "files": source_files,
        },
        "period_days": periods,
        "candidate_lambdas": {name: value for name, value in CANDIDATES},
        "horizon_period_ratios": HORIZON_RATIOS,
        "verdict": frozen_verdict,
        "verdict_notes": verdict_notes,
        "plain_language": plain,
        "ara_interpretation": ara_interpretation,
        "post_result_diagnosis": post_result_diagnosis,
        "metric_monotonicity": monotonicity,
        "summary": summary.to_dict(orient="records"),
        "horizon_summary": horizon.to_dict(orient="records"),
        "bootstrap_phi_vs_best_control": bootstraps,
        "exploratory_sweep": sweep_summary,
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    build_figure(summary, horizon, sweep_results)
    write_report(results, summary, horizon)
    print(json.dumps(
        {
            "verdict": frozen_verdict,
            "period_days": periods,
            "notes": verdict_notes,
            "bootstrap": bootstraps,
            "sweep": sweep_summary,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
