"""PN7A: phase-referenced occurrence analysis using only native sieve records.

The adult p29-conditioned survival curve supplies the Phase-A coordinate.  The
independent observable is where removals occur in the raw ordered number line.
No spectral decomposition, smoothing, fitted shift, or sign selection is used
for the registered endpoints.
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
INPUT = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_AGGREGATES.npz"
OUTPUT_JSON = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_RESULTS.json"
OUTPUT_CSV = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_CURVES.csv"
OUTPUT_FIGURE = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_FIGURE.png"

RUNGS = (7, 8, 9, 10, 11)
ALIGN_RUNGS = (9, 10, 11)
ENTITIES = ("candidate", "edge")
GATE_CELLS = 24
POSITION_BINS = 64


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def theta_from_survival(s: np.ndarray | float) -> np.ndarray:
    s_arr = np.asarray(s, dtype=float)
    return np.arccos(np.clip(2.0 * s_arr - 1.0, -1.0, 1.0))


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 3:
        return float("nan")
    aa = a[mask] - np.mean(a[mask])
    bb = b[mask] - np.mean(b[mask])
    den = math.sqrt(float(np.dot(aa, aa) * np.dot(bb, bb)))
    if den == 0.0:
        return float("nan")
    return float(np.dot(aa, bb) / den)


def occurrence_coefficients(stage_position: np.ndarray, exposure: np.ndarray):
    deaths = np.asarray(stage_position[:GATE_CELLS], dtype=float)
    exposure = np.asarray(exposure, dtype=float)
    alive_before = exposure[None, :] - np.vstack(
        [np.zeros((1, POSITION_BINS)), np.cumsum(deaths[:-1], axis=0)]
    )
    coeffs: dict[int, np.ndarray] = {}
    for depth in (0, 1, 2):
        node_count = 2**depth
        node_width = POSITION_BINS // node_count
        out = np.full((GATE_CELLS, node_count), np.nan, dtype=float)
        for node in range(node_count):
            lo = node * node_width
            mid = lo + node_width // 2
            hi = lo + node_width
            d_left = deaths[:, lo:mid].sum(axis=1)
            d_right = deaths[:, mid:hi].sum(axis=1)
            n_left = alive_before[:, lo:mid].sum(axis=1)
            n_right = alive_before[:, mid:hi].sum(axis=1)
            h_left = np.divide(d_left, n_left, out=np.zeros_like(d_left), where=n_left > 0)
            h_right = np.divide(d_right, n_right, out=np.zeros_like(d_right), where=n_right > 0)
            denom = h_left + h_right
            out[:, node] = np.divide(
                h_right - h_left,
                denom,
                out=np.zeros_like(denom),
                where=denom > 0,
            )
        coeffs[depth] = out

    terminal = np.asarray(stage_position[GATE_CELLS], dtype=float)
    mid = POSITION_BINS // 2
    h_left = terminal[:mid].sum() / exposure[:mid].sum()
    h_right = terminal[mid:].sum() / exposure[mid:].sum()
    terminal_lean = (h_right - h_left) / (h_right + h_left)
    return coeffs, float(terminal_lean), alive_before


def line_points(values, rect, y_min, y_max, x_values=None, x_min=None, x_max=None):
    x0, y0, x1, y1 = rect
    values = np.asarray(values, dtype=float)
    if x_values is None:
        x_values = np.arange(values.size, dtype=float)
    else:
        x_values = np.asarray(x_values, dtype=float)
    if x_min is None:
        x_min = float(np.nanmin(x_values))
    if x_max is None:
        x_max = float(np.nanmax(x_values))
    dx = max(x_max - x_min, 1e-12)
    dy = max(y_max - y_min, 1e-12)
    pts = []
    for xx, yy in zip(x_values, values):
        px = x0 + (float(xx) - x_min) / dx * (x1 - x0)
        py = y1 - (float(yy) - y_min) / dy * (y1 - y0)
        pts.append((px, py))
    return pts


def draw_panel(draw, rect, title, subtitle, series, zero=True):
    x0, y0, x1, y1 = rect
    title_font = ImageFont.truetype("arialbd.ttf", 23)
    text_font = ImageFont.truetype("arial.ttf", 17)
    small_font = ImageFont.truetype("arial.ttf", 14)
    draw.text((x0, y0), title, fill="#17212b", font=title_font)
    draw.text((x0, y0 + 31), subtitle, fill="#5b6570", font=text_font)
    plot = (x0 + 54, y0 + 76, x1 - 18, y1 - 42)
    all_y = np.concatenate([np.asarray(s[1], dtype=float) for s in series])
    finite = all_y[np.isfinite(all_y)]
    ymin, ymax = float(finite.min()), float(finite.max())
    pad = max((ymax - ymin) * 0.12, 1e-6)
    ymin -= pad
    ymax += pad
    if zero:
        ymin, ymax = min(ymin, 0.0), max(ymax, 0.0)
    draw.rectangle(plot, outline="#ccd3d9", width=1)
    if ymin <= 0 <= ymax:
        z = plot[3] - (0 - ymin) / (ymax - ymin) * (plot[3] - plot[1])
        draw.line((plot[0], z, plot[2], z), fill="#8f98a1", width=1)
    yfmt = (lambda v: f"{v:+.1e}") if max(abs(ymin), abs(ymax)) < 0.01 else (lambda v: f"{v:+.3f}")
    draw.text((plot[0] - 61, plot[1] - 8), yfmt(ymax), fill="#606a73", font=small_font)
    draw.text((plot[0] - 61, plot[3] - 10), yfmt(ymin), fill="#606a73", font=small_font)
    legend_x = plot[0]
    for label, values, color, style, xvals in series:
        pts = line_points(values, plot, ymin, ymax, xvals)
        if style == "dashed":
            for i in range(len(pts) - 1):
                if i % 2 == 0:
                    draw.line((pts[i], pts[i + 1]), fill=color, width=3)
        else:
            draw.line(pts, fill=color, width=3)
        for px, py in pts:
            draw.ellipse((px - 2.5, py - 2.5, px + 2.5, py + 2.5), fill=color)
        draw.line((legend_x, y1 - 22, legend_x + 24, y1 - 22), fill=color, width=3)
        draw.text((legend_x + 30, y1 - 32), label, fill="#37424c", font=small_font)
        legend_x += 34 + draw.textlength(label, font=small_font) + 30


def main():
    data = np.load(INPUT)
    series: dict[str, dict[int, dict]] = {e: {} for e in ENTITIES}
    for entity in ENTITIES:
        for rung in RUNGS:
            prefix = f"r{rung}__{entity}"
            exposure = data[f"{prefix}_exposure"].astype(float)
            matrix = data[f"{prefix}_stage_position"].astype(float)
            before_total = np.r_[exposure.sum(), exposure.sum() - np.cumsum(matrix[:GATE_CELLS].sum(axis=1))[:-1]]
            after_total = exposure.sum() - np.cumsum(matrix[:GATE_CELLS].sum(axis=1))
            s_before = before_total / exposure.sum()
            s_after = after_total / exposure.sum()
            theta_before = theta_from_survival(s_before)
            theta_after = theta_from_survival(s_after)
            theta_event = 0.5 * (theta_before + theta_after)
            coeffs, terminal_lean, _ = occurrence_coefficients(matrix, exposure)
            series[entity][rung] = {
                "initial": int(exposure.sum()),
                "terminal": int(matrix[GATE_CELLS].sum()),
                "s_after": s_after,
                "theta_after": theta_after,
                "theta_event": theta_event,
                "root": coeffs[0][:, 0],
                "coeffs": coeffs,
                "terminal_lean": terminal_lean,
            }

    common_low = max(
        float(series[e][r]["theta_event"].min()) for e in ENTITIES for r in ALIGN_RUNGS
    )
    common_high = min(
        float(series[e][r]["theta_event"].max()) for e in ENTITIES for r in ALIGN_RUNGS
    )
    phase_grid = np.linspace(common_low, common_high, GATE_CELLS)
    for entity in ENTITIES:
        for rung in ALIGN_RUNGS:
            rec = series[entity][rung]
            rec["root_aligned"] = np.interp(phase_grid, rec["theta_event"], rec["root"])

    pair_names = ((9, 10), (10, 11), (9, 11))
    recurrence = {}
    for entity in ENTITIES:
        raw = {f"r{a}_r{b}": corr(series[entity][a]["root"], series[entity][b]["root"]) for a, b in pair_names}
        aligned = {
            f"r{a}_r{b}": corr(series[entity][a]["root_aligned"], series[entity][b]["root_aligned"])
            for a, b in pair_names
        }
        recurrence[entity] = {
            "raw": raw,
            "phase_aligned": aligned,
            "raw_mean": float(np.nanmean(list(raw.values()))),
            "phase_aligned_mean": float(np.nanmean(list(aligned.values()))),
        }
        recurrence[entity]["alignment_gain"] = recurrence[entity]["phase_aligned_mean"] - recurrence[entity]["raw_mean"]

    candidate_edge = {
        f"r{r}": corr(series["candidate"][r]["root_aligned"], series["edge"][r]["root_aligned"])
        for r in ALIGN_RUNGS
    }

    vertical_lateral = {}
    vertical_curves = {e: {} for e in ENTITIES}
    for entity in ENTITIES:
        for rung in (10, 11):
            current = series[entity][rung]
            previous = series[entity][rung - 1]
            vertical = current["theta_after"] - previous["theta_after"]
            vertical_aligned = np.interp(phase_grid, current["theta_after"], vertical)
            vertical_curves[entity][rung] = vertical_aligned
            vertical_lateral[f"{entity}_r{rung}"] = corr(current["root_aligned"], vertical_aligned)

    vertical_recurrence = {
        entity: corr(vertical_curves[entity][10], vertical_curves[entity][11]) for entity in ENTITIES
    }

    depth_energy = {}
    terminal_lean = {}
    for entity in ENTITIES:
        depth_energy[entity] = {}
        terminal_lean[entity] = {}
        for rung in RUNGS:
            depth_energy[entity][f"r{rung}"] = {
                f"depth_{d}": float(np.nanmean(series[entity][rung]["coeffs"][d] ** 2)) for d in (0, 1, 2)
            }
            terminal_lean[entity][f"r{rung}"] = series[entity][rung]["terminal_lean"]

    conditions = {
        "phase_recurrence_gt_0_50_both": all(recurrence[e]["phase_aligned_mean"] > 0.50 for e in ENTITIES),
        "alignment_gain_positive_both": all(recurrence[e]["alignment_gain"] > 0.0 for e in ENTITIES),
        "candidate_edge_gt_0_50_r10_r11": all(candidate_edge[f"r{r}"] > 0.50 for r in (10, 11)),
        "vertical_lateral_consistent_abs_gt_0_25": False,
        "depth0_dominates_r10_r11_both": True,
    }
    vl_values = list(vertical_lateral.values())
    conditions["vertical_lateral_consistent_abs_gt_0_25"] = (
        all(abs(v) > 0.25 for v in vl_values)
        and (all(v > 0 for v in vl_values) or all(v < 0 for v in vl_values))
    )
    for entity in ENTITIES:
        for rung in (10, 11):
            energies = depth_energy[entity][f"r{rung}"]
            conditions["depth0_dominates_r10_r11_both"] &= (
                energies["depth_0"] > energies["depth_1"]
                and energies["depth_0"] > energies["depth_2"]
            )

    strict_pass = all(conditions.values())
    partial_pass = all(
        conditions[k]
        for k in (
            "phase_recurrence_gt_0_50_both",
            "alignment_gain_positive_both",
            "candidate_edge_gt_0_50_r10_r11",
        )
    )

    # Registered endpoints are sealed above.  This scan only locates a possible
    # displaced relation for a future frozen test; it cannot change PN7A status.
    exploratory_locator = {}
    for entity in ENTITIES:
        for rung in (10, 11):
            lateral = series[entity][rung]["root_aligned"]
            vertical = vertical_curves[entity][rung]
            scans = []
            for lag in range(-8, 9):
                if lag < 0:
                    cc = corr(lateral[-lag:], vertical[:lag])
                elif lag > 0:
                    cc = corr(lateral[:-lag], vertical[lag:])
                else:
                    cc = corr(lateral, vertical)
                scans.append((lag, cc))
            lag, cc = max(scans, key=lambda z: abs(z[1]) if math.isfinite(z[1]) else -1)
            phase_step = (common_high - common_low) / (GATE_CELLS - 1)
            exploratory_locator[f"{entity}_r{rung}"] = {
                "best_grid_lag": lag,
                "phase_offset_radians": lag * phase_step,
                "correlation": cc,
                "relation_sign": "opposite" if cc < 0 else "same",
            }

    results = {
        "test_id": "PN7A/PHASE-REFERENCED-OCCURRENCE/OPENED-DEVELOPMENT-v1",
        "status": "strict_support" if strict_pass else ("partial_occurrence_structure" if partial_pass else "not_supported"),
        "scope": "R7-R11 already-open development intervals; p31/R12 protected",
        "input": {"file": INPUT.name, "sha256": sha256(INPUT)},
        "phase_grid": {"points": GATE_CELLS, "theta_low": common_low, "theta_high": common_high},
        "adult_phase": {
            e: {
                f"r{r}": {
                    "initial": series[e][r]["initial"],
                    "terminal": series[e][r]["terminal"],
                    "terminal_survival": series[e][r]["terminal"] / series[e][r]["initial"],
                    "terminal_theta": float(theta_from_survival(series[e][r]["terminal"] / series[e][r]["initial"])),
                }
                for r in RUNGS
            }
            for e in ENTITIES
        },
        "vertical_recurrence": vertical_recurrence,
        "lateral_recurrence": recurrence,
        "candidate_edge_phase_agreement": candidate_edge,
        "vertical_lateral_correlation": vertical_lateral,
        "depth_energy": depth_energy,
        "terminal_lean": terminal_lean,
        "registered_conditions": conditions,
        "strict_pass": strict_pass,
        "partial_first_three_pass": partial_pass,
        "exploratory_post_endpoint_locator": exploratory_locator,
        "interpretation_rule": (
            "Strict support requires all five registered conditions. The first three alone support "
            "phase-referenced occurrence structure, not an independently recurring opposite Time wave."
        ),
    }

    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write("\n")

    q_ends = {r: data[f"r{r}__q_end"] for r in RUNGS}
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "entity", "rung", "gate_cell", "q_end", "survival_after", "theta_after",
                "theta_event", "occurrence_root", "phase_grid", "occurrence_root_aligned",
                "vertical_phase_change_aligned",
            ]
        )
        for entity in ENTITIES:
            for rung in RUNGS:
                rec = series[entity][rung]
                for i in range(GATE_CELLS):
                    aligned = rec.get("root_aligned", np.full(GATE_CELLS, np.nan))[i]
                    vertical = vertical_curves[entity].get(rung, np.full(GATE_CELLS, np.nan))[i]
                    writer.writerow(
                        [
                            entity, rung, i + 1, int(q_ends[rung][i]), rec["s_after"][i],
                            rec["theta_after"][i], rec["theta_event"][i], rec["root"][i],
                            phase_grid[i] if rung in ALIGN_RUNGS else "",
                            aligned if rung in ALIGN_RUNGS else "",
                            vertical if rung in (10, 11) else "",
                        ]
                    )

    # Static report figure.  Single blue root plus gold comparator; line style
    # preserves identification in greyscale.
    img = Image.new("RGB", (1800, 1250), "#f7f8fa")
    draw = ImageDraw.Draw(img)
    head = ImageFont.truetype("arialbd.ttf", 34)
    sub = ImageFont.truetype("arial.ttf", 20)
    draw.text((70, 38), "PN7A phase-referenced occurrence", fill="#111a22", font=head)
    draw.text(
        (70, 84),
        "Direct p29-conditioned sieve records; R9-R11 alignment uses the adult ARA angle, not a fitted shift",
        fill="#52606b",
        font=sub,
    )
    blue, gold, grey = "#2867a8", "#c58b26", "#626b73"
    draw_panel(
        draw,
        (70, 140, 875, 640),
        "Adult Phase-A coordinate",
        "Candidate angle after each of 24 later-prime gate cells",
        [
            ("R9", series["candidate"][9]["theta_after"], blue, "solid", None),
            ("R10", series["candidate"][10]["theta_after"], gold, "solid", None),
            ("R11", series["candidate"][11]["theta_after"], grey, "dashed", None),
        ],
        zero=False,
    )
    draw_panel(
        draw,
        (925, 140, 1730, 640),
        "Lateral occurrence after phase alignment",
        "Root ARA lean: right-half vs left-half removal hazard",
        [
            ("Candidate R11", series["candidate"][11]["root_aligned"], blue, "solid", phase_grid),
            ("Edge R11", series["edge"][11]["root_aligned"], gold, "dashed", phase_grid),
        ],
        zero=True,
    )
    draw_panel(
        draw,
        (70, 690, 875, 1190),
        "Cross-rung movement and occurrence",
        "R11 candidate: z-scores compare shape only; registered test uses original units",
        [
            (
                "Lateral lean",
                (series["candidate"][11]["root_aligned"] - np.mean(series["candidate"][11]["root_aligned"]))
                / np.std(series["candidate"][11]["root_aligned"]),
                blue,
                "solid",
                phase_grid,
            ),
            (
                "Vertical change",
                (vertical_curves["candidate"][11] - np.mean(vertical_curves["candidate"][11]))
                / np.std(vertical_curves["candidate"][11]),
                gold,
                "dashed",
                phase_grid,
            ),
        ],
        zero=True,
    )
    cond_labels = [
        ("Phase recurrence > 0.50 (candidate + edge)", conditions["phase_recurrence_gt_0_50_both"]),
        ("Phase alignment improves recurrence", conditions["alignment_gain_positive_both"]),
        ("Candidate-edge agreement > 0.50", conditions["candidate_edge_gt_0_50_r10_r11"]),
        ("Vertical-lateral lock is consistent", conditions["vertical_lateral_consistent_abs_gt_0_25"]),
        ("Adult/root scale dominates child scales", conditions["depth0_dominates_r10_r11_both"]),
    ]
    x0, y0 = 925, 690
    draw.text((x0, y0), "Registered decision", fill="#17212b", font=ImageFont.truetype("arialbd.ttf", 23))
    draw.text((x0, y0 + 31), "All five conditions are required for the opposite-wave claim", fill="#5b6570", font=ImageFont.truetype("arial.ttf", 17))
    body = ImageFont.truetype("arial.ttf", 19)
    bold = ImageFont.truetype("arialbd.ttf", 24)
    for i, (label, passed) in enumerate(cond_labels):
        yy = y0 + 95 + i * 66
        symbol = "PASS" if passed else "FAIL"
        fill = blue if passed else "#a35a32"
        draw.rounded_rectangle((x0, yy, x0 + 82, yy + 36), radius=7, fill=fill)
        draw.text((x0 + 13, yy + 6), symbol, fill="white", font=ImageFont.truetype("arialbd.ttf", 16))
        draw.text((x0 + 103, yy + 6), label, fill="#2b353e", font=body)
    final_status = "STRICT SUPPORT" if strict_pass else ("PARTIAL ONLY" if partial_pass else "NOT SUPPORTED")
    draw.text((x0, y0 + 448), final_status, fill=blue if strict_pass else "#a35a32", font=bold)
    img.save(OUTPUT_FIGURE, quality=95)

    print(json.dumps({
        "status": results["status"],
        "registered_conditions": conditions,
        "lateral_recurrence": recurrence,
        "candidate_edge": candidate_edge,
        "vertical_lateral": vertical_lateral,
        "vertical_recurrence": vertical_recurrence,
        "outputs": [OUTPUT_JSON.name, OUTPUT_CSV.name, OUTPUT_FIGURE.name],
    }, indent=2))


if __name__ == "__main__":
    main()
