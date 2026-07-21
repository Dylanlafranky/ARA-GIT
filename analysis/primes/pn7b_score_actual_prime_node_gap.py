"""Score the frozen PN7B actual-prime node/gap test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_PROTOCOL.md"
EXPECTED_PROTOCOL_SHA256 = "9B42C13E4042B7698FC95A3A32B203CFAE5BE2873F28C0BD3ACC4653BC866F26"
AGG = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.npz"
META = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.json"
OUT_JSON = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_RESULTS.json"
OUT_CSV = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_CURVES.csv"
OUT_FIGURE = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_FIGURE.png"
RUNGS = (7, 8, 9, 10, 11)
PRIMARY_BINS = 24


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest().upper()


def aggregate_hist(values: np.ndarray, bins: int) -> np.ndarray:
    factor = 48 // bins
    return values.reshape(bins, factor).sum(axis=1)


def aggregate_plane(values: np.ndarray, bins: int) -> np.ndarray:
    factor = 48 // bins
    return values.reshape(bins, factor, bins, factor).sum(axis=(1, 3))


def probability(counts: np.ndarray) -> np.ndarray:
    counts = np.asarray(counts, dtype=float)
    return counts / counts.sum()


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a - a.mean()
    b = b - b.mean()
    den = math.sqrt(float(np.dot(a, a) * np.dot(b, b)))
    return float(np.dot(a, b) / den)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    return float(np.dot(a, b) / math.sqrt(float(np.dot(a, a) * np.dot(b, b))))


def jsd_bits(a: np.ndarray, b: np.ndarray) -> float:
    p, q = probability(a), probability(b)
    m = 0.5 * (p + q)
    pmask = p > 0
    qmask = q > 0
    left = np.sum(p[pmask] * np.log2(p[pmask] / m[pmask]))
    right = np.sum(q[qmask] * np.log2(q[qmask] / m[qmask]))
    return float(0.5 * (left + right))


def tv(a: np.ndarray, b: np.ndarray) -> float:
    return float(0.5 * np.abs(probability(a).ravel() - probability(b).ravel()).sum())


def cross_entropy_bits(model_counts: np.ndarray, target_counts: np.ndarray, alpha: float = 0.5) -> float:
    model = np.asarray(model_counts, dtype=float)
    target = probability(target_counts)
    p = (model + alpha) / (model.sum() + alpha * model.size)
    return float(-np.sum(target * np.log2(p)))


def line_points(values, rect, ymin, ymax):
    x0, y0, x1, y1 = rect
    values = np.asarray(values, dtype=float)
    out = []
    for i, value in enumerate(values):
        px = x0 + i / max(len(values) - 1, 1) * (x1 - x0)
        py = y1 - (float(value) - ymin) / max(ymax - ymin, 1e-15) * (y1 - y0)
        out.append((px, py))
    return out


def draw_line_panel(draw, rect, title, subtitle, lines):
    x0, y0, x1, y1 = rect
    title_font = ImageFont.truetype("arialbd.ttf", 23)
    text_font = ImageFont.truetype("arial.ttf", 16)
    small = ImageFont.truetype("arial.ttf", 14)
    draw.text((x0, y0), title, fill="#17212b", font=title_font)
    draw.text((x0, y0 + 32), subtitle, fill="#5b6570", font=text_font)
    plot = (x0 + 56, y0 + 76, x1 - 18, y1 - 48)
    all_values = np.concatenate([np.asarray(v, dtype=float) for _, v, _, _ in lines])
    ymin, ymax = 0.0, float(all_values.max()) * 1.08
    draw.rectangle(plot, outline="#cbd2d8", width=1)
    draw.text((plot[0] - 50, plot[1] - 8), f"{ymax:.3f}", fill="#67717a", font=small)
    draw.text((plot[0] - 40, plot[3] - 8), "0", fill="#67717a", font=small)
    legend_x = plot[0]
    for label, values, color, dashed in lines:
        pts = line_points(values, plot, ymin, ymax)
        if dashed:
            for i in range(len(pts) - 1):
                if i % 2 == 0:
                    draw.line((pts[i], pts[i + 1]), fill=color, width=3)
        else:
            draw.line(pts, fill=color, width=3)
        for px, py in pts:
            draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=color)
        draw.line((legend_x, y1 - 25, legend_x + 24, y1 - 25), fill=color, width=3)
        draw.text((legend_x + 30, y1 - 34), label, fill="#37424c", font=small)
        legend_x += int(draw.textlength(label, font=small)) + 78


def draw_heatmap(draw, rect, title, subtitle, matrix):
    x0, y0, x1, y1 = rect
    title_font = ImageFont.truetype("arialbd.ttf", 23)
    text_font = ImageFont.truetype("arial.ttf", 16)
    small = ImageFont.truetype("arial.ttf", 14)
    draw.text((x0, y0), title, fill="#17212b", font=title_font)
    draw.text((x0, y0 + 32), subtitle, fill="#5b6570", font=text_font)
    plot = (x0 + 74, y0 + 76, x1 - 40, y1 - 48)
    matrix = np.asarray(matrix, dtype=float)
    vmax = float(np.max(np.abs(matrix)))
    n = matrix.shape[0]
    cell_w = (plot[2] - plot[0]) / n
    cell_h = (plot[3] - plot[1]) / n
    for iy in range(n):
        for ix in range(n):
            value = matrix[iy, ix] / max(vmax, 1e-15)
            if value >= 0:
                base = (42, 103, 168)
            else:
                base = (197, 139, 38)
            strength = abs(value) ** 0.5
            rgb = tuple(int(245 + strength * (c - 245)) for c in base)
            left = plot[0] + ix * cell_w
            top = plot[1] + (n - 1 - iy) * cell_h
            draw.rectangle((left, top, left + cell_w + 1, top + cell_h + 1), fill=rgb)
    draw.rectangle(plot, outline="#aeb7bf", width=1)
    draw.text((plot[0], plot[3] + 8), "incoming larger  x<1", fill="#5b6570", font=small)
    draw.text((plot[2] - 115, plot[3] + 8), "x>1  outgoing larger", fill="#5b6570", font=small)
    draw.text((x0, plot[1] + (plot[3] - plot[1]) / 2 - 8), "next", fill="#5b6570", font=small)


def main():
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Protocol changed after freeze")
    z = np.load(AGG)
    meta = json.loads(META.read_text(encoding="utf-8"))
    if sha256(AGG) != meta["aggregate_npz_sha256"]:
        raise RuntimeError("Aggregate hash mismatch")

    all_resolutions = {}
    primary_objects = None
    for bins in (12, 24, 48):
        objects = {}
        for rung in RUNGS:
            key = f"r{rung}"
            objects[rung] = {
                "f": aggregate_hist(z[f"{key}__frequency48"], bins),
                "f_half": np.stack([aggregate_hist(row, bins) for row in z[f"{key}__frequency_half48"]]),
                "t": aggregate_plane(z[f"{key}__transition48"], bins),
                "t_half": np.stack([aggregate_plane(row, bins) for row in z[f"{key}__transition_half48"]]),
                "f_control": aggregate_hist(z[f"{key}__gap_offset_frequency48"], bins),
                "t_control": aggregate_plane(z[f"{key}__state_offset_transition48"], bins),
            }
        rung_pairs = {}
        for a, b in ((7, 8), (8, 9), (9, 10), (10, 11)):
            rung_pairs[f"r{a}_r{b}"] = {
                "frequency_correlation": corr(objects[a]["f"], objects[b]["f"]),
                "frequency_jsd_bits": jsd_bits(objects[a]["f"], objects[b]["f"]),
                "transition_cosine": cosine(objects[a]["t"], objects[b]["t"]),
                "transition_jsd_bits": jsd_bits(objects[a]["t"], objects[b]["t"]),
            }
        local = {}
        for rung in (10, 11):
            o = objects[rung]
            local[f"r{rung}"] = {
                "frequency_direct_control_tv": tv(o["f"], o["f_control"]),
                "frequency_split_half_tv": tv(o["f_half"][0], o["f_half"][1]),
                "frequency_control_to_noise_ratio": tv(o["f"], o["f_control"]) / tv(o["f_half"][0], o["f_half"][1]),
                "transition_direct_control_tv": tv(o["t"], o["t_control"]),
                "transition_split_half_tv": tv(o["t_half"][0], o["t_half"][1]),
                "transition_control_to_noise_ratio": tv(o["t"], o["t_control"]) / tv(o["t_half"][0], o["t_half"][1]),
                "mirror_correlation": corr(o["f"], o["f"][::-1]),
            }
        transfer = {
            "r10_model_on_r11_bits": cross_entropy_bits(objects[10]["f"], objects[11]["f"]),
            "r9_model_on_r11_bits": cross_entropy_bits(objects[9]["f"], objects[11]["f"]),
            "r10_offset_control_on_r11_bits": cross_entropy_bits(objects[10]["f_control"], objects[11]["f"]),
        }
        all_resolutions[str(bins)] = {"rung_pairs": rung_pairs, "local": local, "transfer": transfer}
        if bins == PRIMARY_BINS:
            primary_objects = objects

    primary = all_resolutions[str(PRIMARY_BINS)]
    r10r11 = primary["rung_pairs"]["r10_r11"]
    r9r10 = primary["rung_pairs"]["r9_r10"]
    p = {
        "P1_frequency_recurrence": r10r11["frequency_correlation"] >= 0.995 and r10r11["frequency_jsd_bits"] <= 0.002,
        "P2_ordered_handover_recurrence": r10r11["transition_cosine"] >= 0.990 and r10r11["transition_jsd_bits"] <= 0.010,
        "P3_local_pair_not_inventory_only": all(primary["local"][f"r{r}"]["frequency_control_to_noise_ratio"] > 5 for r in (10, 11)),
        "P4_immediate_handover_not_frequency_only": all(primary["local"][f"r{r}"]["transition_control_to_noise_ratio"] > 5 for r in (10, 11)),
        "P5_rung_transfer": (
            primary["transfer"]["r10_model_on_r11_bits"] < primary["transfer"]["r9_model_on_r11_bits"]
            and primary["transfer"]["r10_model_on_r11_bits"] < primary["transfer"]["r10_offset_control_on_r11_bits"]
        ),
        "P6_scale_convergence": (
            r10r11["frequency_jsd_bits"] < r9r10["frequency_jsd_bits"]
            and r10r11["transition_jsd_bits"] < r9r10["transition_jsd_bits"]
        ),
        "P7_reversible_ridge_symmetry": all(
            primary["local"][f"r{r}"]["mirror_correlation"] >= 0.995
            and abs(meta["rungs"][f"r{r}"]["mean_asymmetry"]) <= 0.002
            for r in (10, 11)
        ),
    }
    core = all(p[k] for k in (
        "P1_frequency_recurrence", "P2_ordered_handover_recurrence",
        "P3_local_pair_not_inventory_only", "P4_immediate_handover_not_frequency_only",
    ))

    # Post-endpoint audit only. The registered P7 uses the frozen even-bin
    # mirror. Exact pair transposition isolates the x=1 ridge instead of
    # assigning that point mass to one side of an even-bin boundary.
    ridge_audit = {}
    for rung in (10, 11):
        pair = z[f"r{rung}__gap_pair_inventory"].astype(float)
        equal = float(np.trace(pair))
        incoming_larger = float(np.tril(pair, -1).sum())
        outgoing_larger = float(np.triu(pair, 1).sum())
        ridge_audit[f"r{rung}"] = {
            "status": "post-endpoint diagnostic; cannot rescue registered P7",
            "exact_equal_gap_share": equal / pair.sum(),
            "off_ridge_directional_asymmetry": (outgoing_larger - incoming_larger) / (outgoing_larger + incoming_larger),
            "exact_pair_transpose_tv": tv(pair, pair.T),
            "exact_pair_transpose_cosine": cosine(pair, pair.T),
        }

    results = {
        "test_id": "PN7B/ACTUAL-PRIME-NODE-GAP/OPENED-R10-R11-v1",
        "status": "direct_pair_core_supported" if core else "direct_pair_core_not_supported",
        "evidence_class": "registered structural test on already-open windows; not a prime predictor",
        "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "aggregate_sha256": sha256(AGG),
        "primary_bins": PRIMARY_BINS,
        "control_offset": 257,
        "registered_conditions": p,
        "criteria_passed": sum(p.values()),
        "criteria_total": len(p),
        "direct_pair_core_supported": core,
        "primary": primary,
        "sensitivity": all_resolutions,
        "rung_metadata": meta["rungs"],
        "post_endpoint_exact_ridge_audit": ridge_audit,
        "interpretation_fence": (
            "A pass supports a recurring actual-prime node/gap shape and immediate order beyond matched inventories. "
            "It does not generate primes or show information absent from raw gaps."
        ),
    }
    OUT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ara_bin", "x_low", "x_high", "x_center",
            *[f"r{r}_frequency" for r in RUNGS],
            "r10_offset_control", "r11_offset_control", "r10_mirror", "r11_mirror",
        ])
        for b in range(PRIMARY_BINS):
            writer.writerow([
                b, 2 * b / PRIMARY_BINS, 2 * (b + 1) / PRIMARY_BINS, (2 * b + 1) / PRIMARY_BINS,
                *[probability(primary_objects[r]["f"])[b] for r in RUNGS],
                probability(primary_objects[10]["f_control"])[b],
                probability(primary_objects[11]["f_control"])[b],
                probability(primary_objects[10]["f"])[::-1][b],
                probability(primary_objects[11]["f"])[::-1][b],
            ])

    blue, gold, grey = "#2867a8", "#c58b26", "#68727b"
    img = Image.new("RGB", (1800, 1260), "#f7f8fa")
    draw = ImageDraw.Draw(img)
    draw.text((70, 38), "PN7B actual-prime node / traversal-gap ARA", fill="#111a22", font=ImageFont.truetype("arialbd.ttf", 34))
    draw.text((70, 84), "Every internal actual prime; direct incoming/outgoing gap relation; 24-bin registered view", fill="#52606b", font=ImageFont.truetype("arial.ttf", 20))
    draw_line_panel(
        draw, (70, 140, 875, 635), "Node-gap frequency by rung",
        "Share of actual-prime nodes at each ARA mix; x=1 is equal incoming/outgoing gap",
        [("R9", probability(primary_objects[9]["f"]), grey, True),
         ("R10", probability(primary_objects[10]["f"]), gold, False),
         ("R11", probability(primary_objects[11]["f"]), blue, False)],
    )
    draw_line_panel(
        draw, (925, 140, 1730, 635), "Immediate node pair versus distant control",
        "R11 direct adjacent gaps compared with the same gap inventory paired 257 positions apart",
        [("Direct node", probability(primary_objects[11]["f"]), blue, False),
         ("Gap offset 257", probability(primary_objects[11]["f_control"]), gold, True)],
    )
    direct_plane = probability(primary_objects[11]["t"])
    control_plane = probability(primary_objects[11]["t_control"])
    draw_heatmap(
        draw, (70, 685, 875, 1190), "Ordered handover residual",
        "R11 direct consecutive-state plane minus state-offset-257 control; blue positive, gold negative",
        direct_plane - control_plane,
    )
    x0, y0 = 925, 685
    draw.text((x0, y0), "Registered decision", fill="#17212b", font=ImageFont.truetype("arialbd.ttf", 23))
    draw.text((x0, y0 + 32), "P1-P4 form the direct pair core", fill="#5b6570", font=ImageFont.truetype("arial.ttf", 17))
    labels = [
        ("P1 frequency wave recurs", p["P1_frequency_recurrence"]),
        ("P2 ordered handover recurs", p["P2_ordered_handover_recurrence"]),
        ("P3 local pair exceeds inventory control", p["P3_local_pair_not_inventory_only"]),
        ("P4 immediate order exceeds frequency control", p["P4_immediate_handover_not_frequency_only"]),
        ("P5 R10 transfers best to R11", p["P5_rung_transfer"]),
        ("P6 rung distances converge", p["P6_scale_convergence"]),
        ("P7 reversible ridge symmetry", p["P7_reversible_ridge_symmetry"]),
    ]
    body = ImageFont.truetype("arial.ttf", 18)
    for i, (label, passed) in enumerate(labels):
        yy = y0 + 85 + i * 52
        fill = blue if passed else "#ad5a32"
        draw.rounded_rectangle((x0, yy, x0 + 82, yy + 34), radius=7, fill=fill)
        draw.text((x0 + 13, yy + 6), "PASS" if passed else "FAIL", fill="white", font=ImageFont.truetype("arialbd.ttf", 15))
        draw.text((x0 + 104, yy + 5), label, fill="#2b353e", font=body)
    draw.text(
        (x0, y0 + 470),
        f"CORE {'SUPPORTED' if core else 'NOT SUPPORTED'}  |  {sum(p.values())}/7 total",
        fill=blue if core else "#ad5a32",
        font=ImageFont.truetype("arialbd.ttf", 24),
    )
    img.save(OUT_FIGURE)

    print(json.dumps({
        "status": results["status"],
        "criteria": p,
        "passed": results["criteria_passed"],
        "frequency_r10_r11": {k: r10r11[k] for k in ("frequency_correlation", "frequency_jsd_bits")},
        "transition_r10_r11": {k: r10r11[k] for k in ("transition_cosine", "transition_jsd_bits")},
        "local": primary["local"],
        "transfer": primary["transfer"],
        "post_endpoint_exact_ridge_audit": ridge_audit,
    }, indent=2))


if __name__ == "__main__":
    main()
