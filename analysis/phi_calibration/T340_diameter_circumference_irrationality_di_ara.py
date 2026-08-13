"""T340: frozen diameter/circumference Irrationality Di-ARA test.

The implementation follows the frozen T340 protocol.  It reuses checksum-
locked event extractions from T307 and T333--T335 and applies one common score
to the radial and angular parts of q = z[n+1] / z[n].
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

PROTOCOL = HERE / "T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"
QUTRIT = REPO / "analysis" / "quantum" / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EVENTS.npz"
BUBBLES = (
    REPO
    / "analysis"
    / "vertical_ara_bubbles"
    / "results"
    / "T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_EVENTS.csv"
)
RIVER = (
    REPO
    / "analysis"
    / "hydraulics"
    / "results"
    / "T335_RIVER_IRRATIONALITY_DI_ARA_EVENTS.csv"
)
MUON = REPO / "analysis" / "muon" / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_STEPS.csv"

STEM = "T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA"
OUT_JSON = HERE / f"{STEM}_RESULTS.json"
OUT_SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
OUT_CELLS = HERE / f"{STEM}_CELLS.csv"
OUT_FIGURE = HERE / f"{STEM}_FIGURE.png"
OUT_REPORT = HERE / f"{STEM}_REPORT_2026-08-04.md"

EXPECTED_HASHES = {
    PROTOCOL: "12CEE15FB825BAC1047AE96194528A0AC1653955E979E2B62977C50DBA2D8451",
    QUTRIT: "B84918CFF03F2D268DF1C8317CFE16BD93B507BD8CF4CA44A0DBAC79F9F0CE12",
    BUBBLES: "262DC32FEE54973223FB4BF4F0D544EAAAB6449761852A3A29F0DCF8AC3D3BA7",
    RIVER: "A50C13E1F93C0E0115897DDE7F7763B93DC880DBD2DF5BAA6E0EE66FD394FC26",
    MUON: "C1F0E60F21C8DF1CECEF8FD6A225C0B0B00E8972A98ADE98FDA65847CC9BB222",
}

PHI = (1.0 + math.sqrt(5.0)) / 2.0
TAU_PHI = 1.0 / (PHI * PHI)
PLASTIC = 1.324717957244746

RADIAL_CANDIDATES = {
    "plastic": PLASTIC,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "octave": 2.0,
    "e": math.e,
}

ANGULAR_CANDIDATES = {
    "quarter": 1.0 / 4.0,
    "third": 1.0 / 3.0,
    "one_over_e": 1.0 / math.e,
    "three_eighths": 3.0 / 8.0,
    "phi_inverse_squared": TAU_PHI,
    "two_fifths": 2.0 / 5.0,
    "sqrt2_minus_1": math.sqrt(2.0) - 1.0,
}

PLANES = ("psi0_psi1", "psi1_psi2", "psi2_psi0")
QUTRIT_LAGS = (1, 2, 4, 8, 16, 32, 64)
EPS = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_inputs() -> dict[str, dict[str, object]]:
    output: dict[str, dict[str, object]] = {}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"checksum mismatch: {path}\n{actual}\n{expected}")
        output[str(path.relative_to(REPO))] = {
            "sha256": actual,
            "bytes": path.stat().st_size,
        }
    return output


def wrap_angle(values: np.ndarray) -> np.ndarray:
    return np.arctan2(np.sin(values), np.cos(values))


def radial_score(m_minus: float, m_plus: float, alpha: float) -> float:
    return 0.5 * (
        abs(math.log(m_minus) + math.log(alpha))
        + abs(math.log(m_plus) - math.log(alpha))
    )


def angular_score(a_minus: float, a_plus: float, tau: float) -> float:
    return 0.5 * (abs(a_minus - tau) + abs(a_plus - tau))


def fitted_alpha(radial: np.ndarray) -> float:
    logs = np.log(radial)
    minus = logs[logs < -EPS]
    plus = logs[logs > EPS]
    if minus.size == 0 or plus.size == 0:
        return float("nan")
    return float(math.exp(0.5 * (float(np.median(plus)) - float(np.median(minus)))))


def fitted_tau(delta: np.ndarray) -> float:
    turns = wrap_angle(delta) / (2.0 * math.pi)
    minus = -turns[turns < -EPS]
    plus = turns[turns > EPS]
    if minus.size == 0 or plus.size == 0:
        return float("nan")
    return float(0.5 * (float(np.median(minus)) + float(np.median(plus))))


def metric_row(
    domain: str,
    population: str,
    split: str,
    radial: Iterable[float],
    delta: Iterable[float],
    alpha_cal: float | None,
    tau_cal: float | None,
    evidence_role: str,
    cell: str = "pooled",
) -> dict[str, object]:
    radial_array = np.asarray(radial, dtype=float)
    delta_array = wrap_angle(np.asarray(delta, dtype=float))
    valid = (
        np.isfinite(radial_array)
        & (radial_array > 0.0)
        & np.isfinite(delta_array)
    )
    radial_array = radial_array[valid]
    delta_array = delta_array[valid]
    contraction = radial_array[radial_array < 1.0 - EPS]
    expansion = radial_array[radial_array > 1.0 + EPS]
    reverse = -delta_array[delta_array < -EPS] / (2.0 * math.pi)
    forward = delta_array[delta_array > EPS] / (2.0 * math.pi)
    if min(contraction.size, expansion.size, reverse.size, forward.size) == 0:
        raise RuntimeError(f"missing direction in {domain}/{population}/{split}/{cell}")

    m_minus = float(np.median(contraction))
    m_plus = float(np.median(expansion))
    a_minus = float(np.median(reverse))
    a_plus = float(np.median(forward))
    r_scores = {
        name: radial_score(m_minus, m_plus, value)
        for name, value in RADIAL_CANDIDATES.items()
    }
    c_scores = {
        name: angular_score(a_minus, a_plus, value)
        for name, value in ANGULAR_CANDIDATES.items()
    }
    r_winner = min(r_scores, key=r_scores.get)
    c_winner = min(c_scores, key=c_scores.get)
    row: dict[str, object] = {
        "domain": domain,
        "population": population,
        "split": split,
        "cell": cell,
        "evidence_role": evidence_role,
        "n": int(radial_array.size),
        "n_contracting": int(contraction.size),
        "n_expanding": int(expansion.size),
        "n_reverse": int(reverse.size),
        "n_forward": int(forward.size),
        "radial_median_contracting": m_minus,
        "radial_median_expanding": m_plus,
        "radial_reciprocal_product": m_minus * m_plus,
        "radial_implied_alpha": fitted_alpha(radial_array),
        "angular_median_reverse_turns": a_minus,
        "angular_median_forward_turns": a_plus,
        "angular_implied_tau": 0.5 * (a_minus + a_plus),
        "radial_fixed_winner": r_winner,
        "angular_fixed_winner": c_winner,
        "radial_e_pass": r_winner == "e",
        "angular_phi_pass": c_winner == "phi_inverse_squared",
        "joint_fixed_pass": r_winner == "e" and c_winner == "phi_inverse_squared",
    }
    for name, score in r_scores.items():
        row[f"radial_score_{name}"] = score
    for name, score in c_scores.items():
        row[f"angular_score_{name}"] = score
    if alpha_cal is not None and math.isfinite(alpha_cal):
        row["radial_alpha_cal"] = alpha_cal
        row["radial_score_fitted_cal"] = radial_score(m_minus, m_plus, alpha_cal)
        row["radial_e_beats_fitted"] = r_scores["e"] <= row["radial_score_fitted_cal"]
    else:
        row["radial_alpha_cal"] = float("nan")
        row["radial_score_fitted_cal"] = float("nan")
        row["radial_e_beats_fitted"] = False
    if tau_cal is not None and math.isfinite(tau_cal):
        row["angular_tau_cal"] = tau_cal
        row["angular_score_fitted_cal"] = angular_score(a_minus, a_plus, tau_cal)
        row["angular_phi_beats_fitted"] = (
            c_scores["phi_inverse_squared"] <= row["angular_score_fitted_cal"]
        )
    else:
        row["angular_tau_cal"] = float("nan")
        row["angular_score_fitted_cal"] = float("nan")
        row["angular_phi_beats_fitted"] = False
    row["strong_transfer_pass"] = bool(
        row["joint_fixed_pass"]
        and row["radial_e_beats_fitted"]
        and row["angular_phi_beats_fitted"]
    )
    return row


def qutrit_data() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    archive = np.load(QUTRIT)
    by_split: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {
        "calibration": [],
        "holdout": [],
    }
    cells_raw: list[tuple[str, str, np.ndarray, np.ndarray]] = []
    for plane in PLANES:
        time = np.asarray(archive[f"{plane}_time"], dtype=np.int64)
        residual = np.asarray(archive[f"{plane}_residual"], dtype=float)
        amp = np.asarray(archive[f"{plane}_circle_strength"], dtype=float)
        heading = np.asarray(archive[f"{plane}_circle_heading"], dtype=float)
        eligible = (
            np.isfinite(amp)
            & np.isfinite(heading)
            & np.isfinite(residual)
            & (amp >= 0.01)
            & (residual <= 0.25)
        )
        prefix = np.concatenate(
            (np.zeros(1, dtype=np.int64), np.cumsum(np.diff(time) > 2200))
        )
        midpoint = len(time) // 2
        for split, start, stop in (
            ("calibration", 0, midpoint),
            ("holdout", midpoint, len(time)),
        ):
            for lag in QUTRIT_LAGS:
                index = np.arange(start, stop - lag, dtype=np.int64)
                keep = (
                    eligible[index]
                    & eligible[index + lag]
                    & ((prefix[index + lag] - prefix[index]) == 0)
                )
                left = index[keep]
                right = left + lag
                radial = amp[right] / amp[left]
                delta = wrap_angle(2.0 * math.pi * (heading[right] - heading[left]))
                finite = np.isfinite(radial) & (radial > 0.0) & np.isfinite(delta)
                radial = radial[finite]
                delta = delta[finite]
                by_split[split].append((radial, delta))
                cells_raw.append((split, f"{plane}:lag{lag}", radial, delta))

    cal_radial = np.concatenate([pair[0] for pair in by_split["calibration"]])
    cal_delta = np.concatenate([pair[1] for pair in by_split["calibration"]])
    alpha_cal = fitted_alpha(cal_radial)
    tau_cal = fitted_tau(cal_delta)
    summary: list[dict[str, object]] = []
    for split, pieces in by_split.items():
        summary.append(
            metric_row(
                "recorded_qutrit",
                "three_planes_circle",
                split,
                np.concatenate([pair[0] for pair in pieces]),
                np.concatenate([pair[1] for pair in pieces]),
                alpha_cal,
                tau_cal,
                "real_data_primary",
            )
        )
    cells = [
        metric_row(
            "recorded_qutrit",
            "three_planes_circle",
            split,
            radial,
            delta,
            alpha_cal,
            tau_cal,
            "real_data_primary",
            cell,
        )
        for split, cell, radial, delta in cells_raw
    ]
    return summary, cells


def frame_data(
    frame: pd.DataFrame,
    domain: str,
    population: str,
    radial_col: str,
    delta_col: str,
    evidence_role: str,
    cell_col: str | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    split_order = [value for value in ("calibration", "evaluation", "holdout", "development") if value in set(frame["split"])]
    calibration = frame[frame["split"] == "calibration"]
    alpha_cal = fitted_alpha(calibration[radial_col].to_numpy(float)) if len(calibration) else None
    tau_cal = fitted_tau(calibration[delta_col].to_numpy(float)) if len(calibration) else None
    summary: list[dict[str, object]] = []
    cells: list[dict[str, object]] = []
    for split in split_order:
        part = frame[frame["split"] == split]
        summary.append(
            metric_row(
                domain,
                population,
                split,
                part[radial_col],
                part[delta_col],
                alpha_cal,
                tau_cal,
                evidence_role,
            )
        )
        if cell_col is not None:
            for cell_value, cell_part in part.groupby(cell_col, sort=True):
                try:
                    cells.append(
                        metric_row(
                            domain,
                            population,
                            split,
                            cell_part[radial_col],
                            cell_part[delta_col],
                            alpha_cal,
                            tau_cal,
                            evidence_role,
                            f"{cell_col}={cell_value}",
                        )
                    )
                except RuntimeError:
                    # A small cell lacking one direction is retained through
                    # its pooled split but cannot define the two-sided score.
                    continue
    return summary, cells


def bubble_data() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    frame = pd.read_csv(BUBBLES)
    frame = frame[frame["source_kind"] == "observed"].copy()
    return frame_data(
        frame,
        "recorded_bubbles",
        "octave_relative_roots",
        "u",
        "delta_rad",
        "real_data_transfer",
        "level",
    )


def river_data() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    frame = pd.read_csv(RIVER)
    frame = frame[frame["source_kind"] == "observed"].copy()
    primary = frame[frame["path_type"] == "thalweg"].copy()
    controls = frame[frame["path_type"] == "control"].copy()
    summary_a, cells_a = frame_data(
        primary,
        "recorded_river",
        "thalweg_rank1",
        "scale_ratio_s",
        "turn_delta_rad",
        "real_data_primary",
    )
    summary_b, cells_b = frame_data(
        controls,
        "recorded_river",
        "matched_rank_controls",
        "scale_ratio_s",
        "turn_delta_rad",
        "real_data_control",
        "elevation_rank",
    )
    return summary_a + summary_b, cells_a + cells_b


def muon_data() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    frame = pd.read_csv(MUON)
    valid = frame["valid"].astype(str).str.lower().eq("true")
    frame = frame[valid & (frame["pair"] == "parent_phi_time_vs_e")].copy()
    frame["split"] = "development"
    return frame_data(
        frame,
        "muon_fusion_model",
        "parent_phi_time_vs_e",
        "s",
        "delta_rad",
        "construction_positive_only",
        "family",
    )


def clean_json(value):
    if isinstance(value, dict):
        return {str(key): clean_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_json(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def make_figure(summary: pd.DataFrame, cross_verdict: str) -> None:
    width, height = 2400, 1600
    image = Image.new("RGB", (width, height), "#f7f9fc")
    draw = ImageDraw.Draw(image)
    ink = "#15263a"
    muted = "#627184"
    blue = "#3977c3"
    gold = "#d99b2b"
    pink = "#c85176"
    green = "#3c9b71"
    grid = "#d7dee8"
    title_f = font(48, True)
    subtitle_f = font(24)
    panel_f = font(28, True)
    body_f = font(22)
    small_f = font(18)
    draw.text((70, 40), "T340 — diameter/circumference Irrationality Di-ARA", fill=ink, font=title_f)
    draw.text((70, 105), "Radial 1/e↔e and circumferential golden-step hypotheses scored independently", fill=muted, font=subtitle_f)

    boxes = [(60, 170, 1170, 760), (1230, 170, 2340, 760), (60, 820, 1170, 1510), (1230, 820, 2340, 1510)]
    for box in boxes:
        draw.rounded_rectangle(box, radius=18, fill="white", outline=grid, width=2)

    real = summary[summary["evidence_role"].isin(["real_data_primary", "real_data_transfer"])]
    plot_rows = real[real["split"].isin(["evaluation", "holdout"])].copy()
    if len(plot_rows) == 0:
        plot_rows = real.copy()
    labels = [f"{r.domain.replace('recorded_', '')}:{r.split[:4]}" for r in plot_rows.itertuples()]
    colors = [blue, gold, pink, green, "#8357b5", "#2f8e9c"]

    # Panel 1: radial implied reciprocal alpha.
    box = boxes[0]
    draw.text((box[0] + 24, box[1] + 20), "Diameter / radial result", fill=ink, font=panel_f)
    draw.text((box[0] + 24, box[1] + 62), "Implied reciprocal amplitude α; e is the frozen target", fill=muted, font=small_f)
    x0, x1 = box[0] + 300, box[2] - 70
    y0, y1 = box[1] + 110, box[3] - 70
    xmin, xmax = 1.0, 3.0
    def rx(value: float) -> int:
        return int(x0 + (value - xmin) / (xmax - xmin) * (x1 - x0))
    draw.line((x0, y1, x1, y1), fill=ink, width=2)
    for candidate in (1.5, PHI, 2.0, math.e):
        xx = rx(candidate)
        draw.line((xx, y0, xx, y1), fill=grid, width=2)
        draw.text((xx - 20, y1 + 12), f"{candidate:.2f}", fill=muted, font=small_f)
    draw.line((rx(math.e), y0, rx(math.e), y1), fill=pink, width=5)
    row_h = max(38, int((y1 - y0) / max(len(plot_rows), 1)))
    for i, row in enumerate(plot_rows.itertuples()):
        yy = y0 + i * row_h + row_h // 2
        draw.text((box[0] + 24, yy - 12), labels[i], fill=ink, font=small_f)
        xx = rx(float(row.radial_implied_alpha))
        draw.ellipse((xx - 8, yy - 8, xx + 8, yy + 8), fill=colors[i % len(colors)], outline=ink)
        draw.text((xx + 14, yy - 12), f"{row.radial_implied_alpha:.3f} · {row.radial_fixed_winner}", fill=muted, font=small_f)

    # Panel 2: angular implied fraction.
    box = boxes[1]
    draw.text((box[0] + 24, box[1] + 20), "Circumference / angular result", fill=ink, font=panel_f)
    draw.text((box[0] + 24, box[1] + 62), "Median principal-turn magnitude τ; φ⁻² is the frozen target", fill=muted, font=small_f)
    x0, x1 = box[0] + 300, box[2] - 70
    y0, y1 = box[1] + 110, box[3] - 70
    xmin, xmax = 0.0, 0.5
    def ax(value: float) -> int:
        return int(x0 + (value - xmin) / (xmax - xmin) * (x1 - x0))
    draw.line((x0, y1, x1, y1), fill=ink, width=2)
    for candidate in (0.25, 1/3, 1/math.e, 3/8, TAU_PHI, 0.4):
        xx = ax(candidate)
        draw.line((xx, y0, xx, y1), fill=grid, width=2)
    draw.line((ax(TAU_PHI), y0, ax(TAU_PHI), y1), fill=pink, width=5)
    draw.text((ax(TAU_PHI)-28, y1+12), "φ⁻²", fill=pink, font=small_f)
    for i, row in enumerate(plot_rows.itertuples()):
        yy = y0 + i * row_h + row_h // 2
        draw.text((box[0] + 24, yy - 12), labels[i], fill=ink, font=small_f)
        xx = ax(float(row.angular_implied_tau))
        draw.ellipse((xx - 8, yy - 8, xx + 8, yy + 8), fill=colors[i % len(colors)], outline=ink)
        draw.text((xx + 14, yy - 12), f"{row.angular_implied_tau:.3f} · {row.angular_fixed_winner}", fill=muted, font=small_f)

    # Panel 3: pass matrix.
    box = boxes[2]
    draw.text((box[0] + 24, box[1] + 20), "Frozen fixed-constant gates", fill=ink, font=panel_f)
    headers = ["population", "radial e", "angular φ", "joint", "beats fitted"]
    xs = [box[0]+24, box[0]+470, box[0]+630, box[0]+810, box[0]+930]
    for xx, header in zip(xs, headers):
        draw.text((xx, box[1]+70), header, fill=muted, font=small_f)
    y = box[1] + 115
    for row in plot_rows.itertuples():
        name = f"{row.domain.replace('recorded_', '')}:{row.split}"
        values = [row.radial_e_pass, row.angular_phi_pass, row.joint_fixed_pass, row.strong_transfer_pass]
        draw.text((xs[0], y), name, fill=ink, font=small_f)
        for xx, value in zip(xs[1:], values):
            color = green if value else "#d96b68"
            draw.rounded_rectangle((xx, y-2, xx+82, y+26), radius=8, fill=color)
            draw.text((xx+17, y+2), "PASS" if value else "NO", fill="white", font=small_f)
        y += 50
    draw.text((box[0]+24, box[3]-90), f"Cross-domain verdict: {cross_verdict}", fill=pink if "NOT" in cross_verdict else green, font=panel_f)
    draw.text((box[0]+24, box[3]-48), "Muon model excluded from empirical pass count.", fill=muted, font=small_f)

    # Panel 4: geometry and interpretation.
    box = boxes[3]
    draw.text((box[0] + 24, box[1] + 20), "Frozen geometry", fill=ink, font=panel_f)
    cx, cy = (box[0]+box[2])//2, (box[1]+box[3])//2 + 20
    radius = 230
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=grid, width=5)
    draw.line((cx-radius-80, cy, cx+radius+80, cy), fill=blue, width=8)
    draw.line((cx, cy-radius-80, cx, cy+radius+80), fill=gold, width=8)
    draw.text((cx-radius-70, cy+18), "1/e", fill=blue, font=body_f)
    draw.text((cx+radius+18, cy+18), "e", fill=blue, font=body_f)
    draw.text((cx+18, cy-radius-76), "+φ turn", fill=gold, font=body_f)
    draw.text((cx+18, cy+radius+40), "−φ turn", fill=gold, font=body_f)
    draw.arc((cx-radius+35, cy-radius+35, cx+radius-35, cy+radius-35), 205, 335, fill=pink, width=10)
    draw.polygon([(cx+190, cy-100), (cx+160, cy-112), (cx+172, cy-82)], fill=pink)
    draw.text((box[0]+35, box[3]-80), "q = s·exp(iΔθ): length and direction are perpendicular observables", fill=muted, font=body_f)

    image.save(OUT_FIGURE)


def make_report(summary: pd.DataFrame, results: dict[str, object]) -> None:
    display = summary[
        summary["evidence_role"].isin(
            ["real_data_primary", "real_data_transfer", "construction_positive_only"]
        )
    ].copy()
    lines = [
        "# T340 — diameter/circumference Irrationality Di-ARA result",
        "",
        "**Run:** 4 August 2026  ",
        "**Protocol:** `T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md`  ",
        f"**Protocol SHA-256:** `{results['protocol_sha256']}`  ",
        f"**Cross-domain verdict:** **{results['cross_domain_verdict']}**",
        "",
        "## Frozen question",
        "",
        "Does one complex ARA step separate into an exponential radial/diameter axis "
        "(`1/e <-> e`) and a golden circumferential axis (principal step magnitude "
        "`phi^-2` turns, orientation-equivalent to `1/phi` the other way)?",
        "",
        "## Results",
        "",
        "| Domain | Split | N | implied radial alpha | radial winner | implied angular tau | angular winner | joint |",
        "|---|---:|---:|---:|---|---:|---|---|",
    ]
    for row in display.itertuples():
        lines.append(
            f"| {row.domain}/{row.population} | {row.split} | {row.n:,} | "
            f"{row.radial_implied_alpha:.6f} | {row.radial_fixed_winner} | "
            f"{row.angular_implied_tau:.6f} | {row.angular_fixed_winner} | "
            f"{'PASS' if row.joint_fixed_pass else 'no'} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        results["plain_language"],
        "",
        "The two axes remain a valid and useful decomposition regardless of the fixed-constant verdict. "
        "A radial failure does not become an angular success, and a nearby `3/8` result is not renamed Phi.",
        "",
        "## Evidence boundary",
        "",
        "The qutrit, bubble and river archives were opened before T340. They test a frozen new interpretation "
        "on inherited measurements, not a pristine discovery. The muon-Fusion population is a construction-positive "
        "check only because its idealised schedule already contains exponential and Phi components.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        "$python = 'C:\\Users\\Dylan\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe'",
        "& $python analysis/phi_calibration/T340_diameter_circumference_irrationality_di_ara.py",
        "& $python analysis/phi_calibration/validate_t340_diameter_circumference_irrationality_di_ara.py",
        "```",
        "",
        "Outputs:",
        "",
        f"- `{OUT_JSON.name}`",
        f"- `{OUT_SUMMARY.name}`",
        f"- `{OUT_CELLS.name}`",
        f"- `{OUT_FIGURE.name}`",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    source_audit = verify_inputs()
    all_summary: list[dict[str, object]] = []
    all_cells: list[dict[str, object]] = []
    for loader in (qutrit_data, bubble_data, river_data, muon_data):
        summary, cells = loader()
        all_summary.extend(summary)
        all_cells.extend(cells)

    summary_frame = pd.DataFrame(all_summary)
    cell_frame = pd.DataFrame(all_cells)
    primary_holdouts = summary_frame[
        summary_frame["domain"].isin(["recorded_qutrit", "recorded_bubbles", "recorded_river"])
        & summary_frame["population"].isin(["three_planes_circle", "octave_relative_roots", "thalweg_rank1"])
        & (summary_frame["split"] == "holdout")
    ]
    joint_holdout_domains = int(primary_holdouts["joint_fixed_pass"].sum())
    supported = joint_holdout_domains >= 2
    cross_verdict = "SUPPORTED" if supported else "NOT SUPPORTED"

    if supported:
        plain = (
            "At least two real-data holdouts independently selected both the fixed exponential radial pair "
            "and the golden circumferential step. This supports the frozen placement within the reuse boundary; "
            "a pristine replication is still required."
        )
    else:
        radial_count = int(primary_holdouts["radial_e_pass"].sum())
        angular_count = int(primary_holdouts["angular_phi_pass"].sum())
        plain = (
            f"The fixed universal placement was not supported: among the three primary real-data holdouts, "
            f"{radial_count} selected e on the radial axis, {angular_count} selected the golden step on the "
            f"circumference axis, and {joint_holdout_domains} selected both. The result can still support the "
            "two-axis Di-ARA decomposition while requiring identity-specific radial and angular landmarks."
        )

    results = {
        "test": "T340 diameter/circumference Irrationality Di-ARA",
        "run_date": "2026-08-04",
        "protocol_sha256": EXPECTED_HASHES[PROTOCOL],
        "sources": source_audit,
        "constants": {
            "phi": PHI,
            "phi_inverse": 1.0 / PHI,
            "phi_inverse_squared": TAU_PHI,
            "one_over_e": 1.0 / math.e,
            "e": math.e,
        },
        "primary_holdout_rows": primary_holdouts.to_dict(orient="records"),
        "joint_holdout_domains": joint_holdout_domains,
        "required_joint_holdout_domains": 2,
        "cross_domain_supported": supported,
        "cross_domain_verdict": cross_verdict,
        "plain_language": plain,
        "summary_rows": len(summary_frame),
        "cell_rows": len(cell_frame),
        "outputs": {
            "summary": OUT_SUMMARY.name,
            "cells": OUT_CELLS.name,
            "figure": OUT_FIGURE.name,
            "report": OUT_REPORT.name,
        },
        "caveats": [
            "All real-data archives were opened before T340.",
            "The muon-Fusion model embeds exponential/Phi ingredients and is excluded from empirical support.",
            "Principal-angle scoring treats 1/phi and 1/phi^2 as orientation-equivalent turn directions, not identical scalar ARA positions.",
            "The fixed constants may fail even when the two-axis Di-ARA decomposition remains useful.",
        ],
    }
    summary_frame.to_csv(OUT_SUMMARY, index=False, float_format="%.12g")
    cell_frame.to_csv(OUT_CELLS, index=False, float_format="%.12g")
    OUT_JSON.write_text(json.dumps(clean_json(results), indent=2) + "\n", encoding="utf-8")
    make_figure(summary_frame, cross_verdict)
    make_report(summary_frame, results)
    print(json.dumps({
        "verdict": cross_verdict,
        "joint_holdout_domains": joint_holdout_domains,
        "summary": str(OUT_SUMMARY),
        "report": str(OUT_REPORT),
        "figure": str(OUT_FIGURE),
    }, indent=2))


if __name__ == "__main__":
    main()
