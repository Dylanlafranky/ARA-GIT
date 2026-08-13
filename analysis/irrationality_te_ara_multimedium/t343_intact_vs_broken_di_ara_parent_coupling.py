#!/usr/bin/env python3
"""T343: frozen intact-versus-broken Di-ARA parent-coupling test."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VENDOR = HERE / "vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))
sys.path.insert(0, str(HERE))

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

import t342_multimedium_irrationality_te_ara as base


STEM = "T343_INTACT_VS_BROKEN_DI_ARA_PARENT_COUPLING"
PROTOCOL = HERE / f"{STEM}_PROTOCOL_v1_FROZEN.md"
COMP_ADDENDUM = HERE / f"{STEM}_COMPUTATIONAL_ADDENDUM_v1_FROZEN.md"
INF_ADDENDUM = HERE / f"{STEM}_INFERENCE_ADDENDUM_v1_FROZEN.md"
EXPECTED_PROTOCOL_HASH = "4820C769B1B54377A6B6A9250A86DB5053F1777825A20F8D57C9C67DF98E6212"
EXPECTED_COMP_HASH = "90C41E1DA2781F4233C2633EAB8AACA4AE6CB41838C72688FD1B82830E9ECBBC"
EXPECTED_INF_HASH = "6C867E57F1F0FE3BDDEFFE41439F0B12D4C0B2503CE9AE9F953A002BB85680EC"

OUT_RESULTS = HERE / f"{STEM}_RESULTS.json"
OUT_SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
OUT_MODEL_COUNTS = HERE / f"{STEM}_MODEL_COUNTS.csv"
OUT_BROKEN = HERE / f"{STEM}_BROKEN_NULLS.csv"
OUT_BLOCK_EFFECTS = HERE / f"{STEM}_BLOCK_EFFECTS.csv"
OUT_TRANSITIONS = HERE / f"{STEM}_TRANSITIONS.csv"
OUT_SAMPLES = HERE / f"{STEM}_VISUAL_SAMPLES.csv"
OUT_QUALITY = HERE / f"{STEM}_DATA_QUALITY.csv"
OUT_MANIFEST = HERE / f"{STEM}_SOURCE_MANIFEST.json"
OUT_FIGURE = HERE / f"{STEM}_FIGURE.png"
OUT_EXPLORER = HERE / f"{STEM}_EXPLORER_3D.html"
OUT_REPORT = HERE / f"{STEM}_REPORT_2026-08-05.md"
DOMAIN_FIGURES = HERE / "t343_domain_figures"

ALPHA = 0.5
BROKEN_CONTROLS = 1000
SIGN_FLIPS = 10_000
SHIFT_SEED = 34320260805
SIGN_SEED = 34320260806
EPS = 1e-12
LABELS = ("bA", "aB", "Ab", "Ba")
NEUTRAL_NAMES = base.SECTOR_NAMES


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def sectors(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Frozen cyclic encoding: bA=0, aB=1, Ab=2, Ba=3."""
    r = np.asarray(a) >= 0
    c = np.asarray(b) >= 0
    return np.where(c, np.where(r, 2, 3), np.where(r, 1, 0)).astype(np.int8)


def ara_xy(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(a, dtype=float)
    # Stable logistic equivalent to 2*exp(a)/(1+exp(a)).
    x = np.empty_like(a)
    pos = a >= 0
    x[pos] = 2.0 / (1.0 + np.exp(-a[pos]))
    ea = np.exp(a[~pos])
    x[~pos] = 2.0 * ea / (1.0 + ea)
    y = 1.0 + np.asarray(b, dtype=float) / math.pi
    return x, y


def transition_counts(blocks: list[base.Block], mode: str) -> np.ndarray:
    rows = 4 if mode == "parent" else 2
    out = np.zeros((rows, 4), dtype=np.int64)
    for block in blocks:
        q = sectors(block.a, block.b)
        if len(q) < 2:
            continue
        if mode == "parent":
            current = q[:-1]
        elif mode == "radial":
            current = (block.a[:-1] >= 0).astype(np.int8)
        elif mode == "angular":
            current = (block.b[:-1] >= 0).astype(np.int8)
        else:
            raise KeyError(mode)
        out += np.bincount(4 * current + q[1:], minlength=rows * 4).reshape(rows, 4)
    return out


def fitted_probabilities(counts: np.ndarray) -> np.ndarray:
    smoothed = counts.astype(float) + ALPHA
    return smoothed / smoothed.sum(axis=1, keepdims=True)


def log_loss_from_counts(counts: np.ndarray, probabilities: np.ndarray) -> float:
    n = int(counts.sum())
    return float(-np.sum(counts * np.log(probabilities)) / n) if n else float("nan")


def per_block_effects(
    blocks: list[base.Block],
    p_parent: np.ndarray,
    p_radial: np.ndarray,
    p_angular: np.ndarray,
) -> list[dict]:
    rows = []
    for number, block in enumerate(blocks):
        q = sectors(block.a, block.b)
        if len(q) < 2:
            continue
        target = q[1:]
        lp = -np.log(p_parent[q[:-1], target])
        lr = -np.log(p_radial[(block.a[:-1] >= 0).astype(np.int8), target])
        lc = -np.log(p_angular[(block.b[:-1] >= 0).astype(np.int8), target])
        rows.append({
            "lineage": block.lineage,
            "block_start": int(block.start),
            "block_number": number,
            "transitions": len(target),
            "parent_loss": float(np.mean(lp)),
            "radial_loss": float(np.mean(lr)),
            "angular_loss": float(np.mean(lc)),
            "delta_radial": float(np.mean(lr - lp)),
            "delta_angular": float(np.mean(lc - lp)),
        })
    return rows


def sign_flip_p(values: np.ndarray, seed: int) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    observed = float(np.mean(values)) if len(values) else float("nan")
    if not len(values):
        return observed, float("nan")
    rng = np.random.default_rng(seed)
    exceed = 0
    remaining = SIGN_FLIPS
    while remaining:
        batch = min(250, remaining)
        signs = rng.integers(0, 2, size=(batch, len(values)), dtype=np.int8) * 2 - 1
        null = np.mean(signs * values[None, :], axis=1)
        exceed += int(np.count_nonzero(null >= observed))
        remaining -= batch
    return observed, float((1 + exceed) / (SIGN_FLIPS + 1))


def grouped_bits(blocks: list[base.Block]) -> dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    grouped: dict[int, list[base.Block]] = defaultdict(list)
    for block in blocks:
        if len(block.a) >= 2:
            grouped[len(block.a)].append(block)
    out = {}
    for n, items in grouped.items():
        aa = np.stack([(x.a >= 0).astype(np.int8) for x in items])
        bb = np.stack([(x.b >= 0).astype(np.int8) for x in items])
        qq = np.where(bb, np.where(aa, 2, 3), np.where(aa, 1, 0)).astype(np.int8)
        out[n] = (aa, bb, qq)
    return out


def needed_shifts(fractions: np.ndarray, n: int) -> dict[int, set[int]]:
    answer = {0: set(), 1: set()}
    for rep, fraction in enumerate(fractions):
        axis = 0 if (rep + 1) % 2 == 1 else 1  # odd control shifts a; even shifts b
        k = max(1, min(n - 1, int(round(float(fraction) * n))))
        answer[axis].add(k)
    return answer


def broken_table_cache(
    grouped: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]],
    fractions: np.ndarray,
) -> dict[tuple[int, int, int], np.ndarray]:
    cache: dict[tuple[int, int, int], np.ndarray] = {}
    for n, (aa, bb, intact_q) in grouped.items():
        for axis, shifts in needed_shifts(fractions, n).items():
            for k in shifts:
                if axis == 0:
                    sa, sb = np.roll(aa, k, axis=1), bb
                else:
                    sa, sb = aa, np.roll(bb, k, axis=1)
                broken_q = np.where(sb, np.where(sa, 2, 3), np.where(sa, 1, 0)).astype(np.int8)
                codes = 4 * broken_q[:, :-1].ravel() + intact_q[:, 1:].ravel()
                cache[(axis, n, k)] = np.bincount(codes, minlength=16).reshape(4, 4)
    return cache


def broken_nulls(
    cal_blocks: list[base.Block],
    hold_blocks: list[base.Block],
    fractions: np.ndarray,
) -> tuple[list[dict], dict]:
    cal_groups = grouped_bits(cal_blocks)
    hold_groups = grouped_bits(hold_blocks)
    cal_cache = broken_table_cache(cal_groups, fractions)
    hold_cache = broken_table_cache(hold_groups, fractions)
    rows = []
    exemplar = {}
    lengths = sorted(set(cal_groups) | set(hold_groups))
    for rep, fraction in enumerate(fractions):
        axis = 0 if (rep + 1) % 2 == 1 else 1
        cal = np.zeros((4, 4), dtype=np.int64)
        hold = np.zeros((4, 4), dtype=np.int64)
        for n in lengths:
            k = max(1, min(n - 1, int(round(float(fraction) * n))))
            if (axis, n, k) in cal_cache:
                cal += cal_cache[(axis, n, k)]
            if (axis, n, k) in hold_cache:
                hold += hold_cache[(axis, n, k)]
        loss = log_loss_from_counts(hold, fitted_probabilities(cal))
        rows.append({
            "replicate": rep + 1,
            "shift_fraction": float(fraction),
            "axis_shifted": "radial_a" if axis == 0 else "angular_b",
            "holdout_log_loss": loss,
            "holdout_transitions": int(hold.sum()),
        })
        if rep == 0:
            exemplar = {"axis": axis, "fraction": float(fraction)}
    return rows, exemplar


def transition_rows(domain: str, split: str, table: np.ndarray) -> list[dict]:
    return [
        {
            "domain": domain,
            "split": split,
            "from_state": LABELS[i],
            "to_state": LABELS[j],
            "count": int(table[i, j]),
        }
        for i in range(4) for j in range(4)
    ]


def model_count_rows(domain: str, split: str, model: str, counts: np.ndarray) -> list[dict]:
    current_labels = LABELS if model == "parent" else (("A-", "A+") if model == "radial" else ("B-", "B+"))
    return [
        {
            "domain": domain,
            "split": split,
            "model": model,
            "current_state": current_labels[i],
            "target_state": LABELS[j],
            "count": int(counts[i, j]),
        }
        for i in range(counts.shape[0]) for j in range(4)
    ]


def sample_visuals(domain: str, hold_blocks: list[base.Block], exemplar: dict) -> list[dict]:
    flat = [(block, i) for block in hold_blocks for i in range(len(block.a))]
    if not flat:
        return []
    picks = np.unique(np.linspace(0, len(flat) - 1, min(1200, len(flat))).round().astype(int))
    axis = int(exemplar.get("axis", 0))
    fraction = float(exemplar.get("fraction", 0.5))
    broken_lookup = {}
    for block in hold_blocks:
        n = len(block.a)
        k = max(1, min(n - 1, int(round(fraction * n))))
        aa, bb = np.asarray(block.a), np.asarray(block.b)
        if axis == 0:
            ba, btheta = np.roll(aa, k), bb
        else:
            ba, btheta = aa, np.roll(bb, k)
        broken_lookup[id(block)] = (ba, btheta)
    rows = []
    for order, pick in enumerate(picks):
        block, i = flat[int(pick)]
        ba, btheta = broken_lookup[id(block)]
        for kind, av, bv in (("intact", float(block.a[i]), float(block.b[i])), ("broken", float(ba[i]), float(btheta[i]))):
            x, y = ara_xy(np.array([av]), np.array([bv]))
            q = int(sectors(np.array([av]), np.array([bv]))[0])
            rows.append({
                "domain": domain,
                "kind": kind,
                "sample_order": order,
                "native_fraction": order / max(1, len(picks) - 1),
                "lineage": block.lineage,
                "block_start": int(block.start),
                "x_ara": float(x[0]),
                "y_ara": float(y[0]),
                "state": LABELS[q],
            })
    return rows


def analyze_domain(domain: str, blocks: list[base.Block], quality: list[dict], offset: int, fractions: np.ndarray):
    selected = base.cap_blocks(blocks)
    cal = [x for x in selected if x.split == "calibration"]
    hold = [x for x in selected if x.split == "holdout"]

    counts = {}
    model_rows = []
    for split, part in (("calibration", cal), ("holdout", hold)):
        for model in ("parent", "radial", "angular"):
            table = transition_counts(part, model)
            counts[(split, model)] = table
            model_rows.extend(model_count_rows(domain, split, model, table))

    p_parent = fitted_probabilities(counts[("calibration", "parent")])
    p_radial = fitted_probabilities(counts[("calibration", "radial")])
    p_angular = fitted_probabilities(counts[("calibration", "angular")])
    loss_parent = log_loss_from_counts(counts[("holdout", "parent")], p_parent)
    loss_radial = log_loss_from_counts(counts[("holdout", "radial")], p_radial)
    loss_angular = log_loss_from_counts(counts[("holdout", "angular")], p_angular)

    effects = per_block_effects(hold, p_parent, p_radial, p_angular)
    er = np.array([x["delta_radial"] for x in effects])
    ec = np.array([x["delta_angular"] for x in effects])
    block_delta_r, p_r = sign_flip_p(er, SIGN_SEED + offset * 2)
    block_delta_c, p_c = sign_flip_p(ec, SIGN_SEED + offset * 2 + 1)
    # The frozen point estimate is the transition-weighted holdout loss
    # difference. Non-overlapping block means are the inference units only.
    delta_r = float(loss_radial - loss_parent)
    delta_c = float(loss_angular - loss_parent)

    null_rows, exemplar = broken_nulls(cal, hold, fractions)
    null_losses = np.array([x["holdout_log_loss"] for x in null_rows])
    p_b = float((1 + np.count_nonzero(null_losses <= loss_parent)) / (BROKEN_CONTROLS + 1))
    broken_median = float(np.median(null_losses))

    states = np.concatenate([sectors(x.a, x.b) for x in hold]) if hold else np.empty(0, dtype=np.int8)
    state_counts = np.bincount(states, minlength=4)
    hold_transitions = int(counts[("holdout", "parent")].sum())
    lineages = len({x.lineage for x in hold})
    eligible = bool(
        hold_transitions >= 1000
        and len(hold) >= 20
        and np.all(state_counts >= 20)
        and all(math.isfinite(x) for x in (loss_parent, loss_radial, loss_angular, broken_median, p_b, p_r, p_c))
    )
    passed = bool(
        eligible
        and delta_r > 0 and p_r <= 0.05
        and delta_c > 0 and p_c <= 0.05
        and broken_median > loss_parent and p_b <= 0.05
    )
    row = {
        "domain": domain,
        "calibration_blocks": len(cal),
        "holdout_blocks": len(hold),
        "holdout_lineages": lineages,
        "holdout_states": int(len(states)),
        "holdout_transitions": hold_transitions,
        **{f"states_{LABELS[i]}": int(state_counts[i]) for i in range(4)},
        "parent_log_loss": loss_parent,
        "radial_child_log_loss": loss_radial,
        "angular_child_log_loss": loss_angular,
        "delta_radial": delta_r,
        "delta_angular": delta_c,
        "block_mean_delta_radial": block_delta_r,
        "block_mean_delta_angular": block_delta_c,
        "p_radial": p_r,
        "p_angular": p_c,
        "broken_median_log_loss": broken_median,
        "broken_q05_log_loss": float(np.quantile(null_losses, 0.05)),
        "broken_q95_log_loss": float(np.quantile(null_losses, 0.95)),
        "delta_broken_median": broken_median - loss_parent,
        "p_broken": p_b,
        "eligible": eligible,
        "domain_pass": passed,
    }
    for x in null_rows:
        x["domain"] = domain
    for x in effects:
        x["domain"] = domain
    trans = transition_rows(domain, "calibration", counts[("calibration", "parent")])
    trans += transition_rows(domain, "holdout", counts[("holdout", "parent")])
    visual = sample_visuals(domain, hold, exemplar)
    quality_row = {
        "domain": domain,
        "raw_quality_rows": len(quality),
        "selected_blocks": len(selected),
        "calibration_blocks": len(cal),
        "holdout_blocks": len(hold),
        "holdout_named_lineages": lineages,
        "holdout_transitions": hold_transitions,
        "four_region_coverage": bool(np.all(state_counts > 0)),
        "minimum_region_states": int(state_counts.min()),
        "finite_primary_scores": bool(all(math.isfinite(x) for x in (loss_parent, loss_radial, loss_angular, broken_median))),
    }
    return row, model_rows, null_rows, effects, trans, visual, quality_row


def font_factory():
    roots = [Path("C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/arial.ttf")]
    normal = next((x for x in roots if x.exists()), None)
    bold = Path("C:/Windows/Fonts/segoeuib.ttf")
    def f(size, is_bold=False):
        path = bold if is_bold and bold.exists() else normal
        return ImageFont.truetype(str(path), size) if path else ImageFont.load_default()
    return f


def draw_summary(summary: pd.DataFrame, verdict: str) -> None:
    W, H = 1800, 1280
    img = Image.new("RGB", (W, H), "#f6f7f9")
    d = ImageDraw.Draw(img)
    f = font_factory()
    d.text((60, 38), "T343 — intact versus broken Di-ARA parent coupling", fill="#172033", font=f(43, True))
    d.text((60, 98), "Identity-specific 4×4 parents · child-only projections · 1,000 broken-pair controls", fill="#596579", font=f(23))
    eligible = int(summary.eligible.sum()); passed = int(summary.domain_pass.sum())
    d.rounded_rectangle((60, 145, 1740, 245), radius=18, fill="#e7edf6")
    d.text((90, 162), f"Frozen verdict: {verdict}", fill="#172033", font=f(27, True))
    d.text((90, 207), f"{passed}/{eligible} eligible domains pass · no universal quadrant order was imposed", fill="#596579", font=f(20, True))

    x0, y0, card_w, card_h, gap = 65, 285, 237, 400, 10
    for k, row in enumerate(summary.sort_values("domain").itertuples()):
        x = x0 + k * (card_w + gap)
        d.rounded_rectangle((x, y0, x + card_w, y0 + card_h), radius=14, fill="white", outline="#d4dbe5")
        d.text((x + 14, y0 + 14), row.domain, fill="#172033", font=f(19, True))
        label = "PASS" if row.domain_pass else ("INELIGIBLE" if not row.eligible else "NO PASS")
        color = "#245b8a" if row.domain_pass else ("#8a6d1d" if not row.eligible else "#a35b20")
        d.text((x + 14, y0 + 47), label, fill=color, font=f(16, True))
        vals = [
            ("parent loss", row.parent_log_loss),
            ("radial child", row.radial_child_log_loss),
            ("angular child", row.angular_child_log_loss),
            ("broken median", row.broken_median_log_loss),
        ]
        top = y0 + 95
        vmax = max(v for _, v in vals) if vals else 1
        for i, (name, value) in enumerate(vals):
            yy = top + i * 55
            d.text((x + 14, yy), name, fill="#4d596d", font=f(14))
            d.rounded_rectangle((x + 14, yy + 22, x + 218, yy + 37), radius=5, fill="#e4e8ef")
            width = 200 * value / vmax if vmax else 0
            fill = "#4c78a8" if name == "parent loss" else ("#d79a2b" if name == "broken median" else "#9da8b6")
            d.rounded_rectangle((x + 14, yy + 22, x + 14 + width, yy + 37), radius=5, fill=fill)
            d.text((x + 161, yy), f"{value:.3f}", fill="#172033", font=f(14))
        d.text((x + 14, y0 + 325), f"Δ radial {row.delta_radial:+.3f}", fill="#172033", font=f(15))
        d.text((x + 14, y0 + 350), f"Δ angular {row.delta_angular:+.3f}", fill="#172033", font=f(15))
        d.text((x + 14, y0 + 375), f"Δ broken {row.delta_broken_median:+.3f}", fill="#172033", font=f(15))

    d.text((65, 735), "Parent advantage by medium", fill="#172033", font=f(28, True))
    d.text((65, 775), "Positive bars favour the intact parent; each domain keeps its own movement grammar", fill="#596579", font=f(18))
    plot_x0, plot_x1, plot_y0 = 350, 1710, 835
    max_abs = max(0.01, float(np.max(np.abs(summary[["delta_radial", "delta_angular", "delta_broken_median"]].to_numpy()))))
    zero = (plot_x0 + plot_x1) / 2
    d.line((zero, plot_y0 - 20, zero, 1190), fill="#172033", width=2)
    d.text((zero - 6, 1200), "0", fill="#596579", font=f(14))
    for i, row in enumerate(summary.sort_values("domain").itertuples()):
        yy = plot_y0 + i * 48
        d.text((65, yy), row.domain, fill="#172033", font=f(17, True))
        for j, (name, val, col) in enumerate((
            ("radial", row.delta_radial, "#4c78a8"),
            ("angular", row.delta_angular, "#88a8c7"),
            ("broken", row.delta_broken_median, "#d79a2b"),
        )):
            ybar = yy + j * 11
            end = zero + (val / max_abs) * (plot_x1 - plot_x0) * 0.46
            d.line((zero, ybar, end, ybar), fill=col, width=7)
        d.text((1715, yy), "pass" if row.domain_pass else ("small" if not row.eligible else "no"), fill="#596579", font=f(15))
    d.text((65, 1240), "Blue = advantage over each child axis · gold = advantage over broken pair median · lower log loss is better", fill="#6b7484", font=f(16))
    img.save(OUT_FIGURE)


def draw_domain_figure(domain: str, summary_row: pd.Series, samples: pd.DataFrame, transitions: pd.DataFrame, broken: pd.DataFrame) -> None:
    W, H = 1600, 1000
    img = Image.new("RGB", (W, H), "#f6f7f9")
    d = ImageDraw.Draw(img); f = font_factory()
    d.text((50, 28), f"T343 — {domain} Di-ARA parent coupling", fill="#172033", font=f(35, True))
    d.text((50, 78), "Intact and broken geometry share the same axes; the test asks what information pairing preserves", fill="#596579", font=f(19))

    colors = {"bA": "#4c78a8", "aB": "#e5892e", "Ab": "#6e9f67", "Ba": "#c26b77"}
    for panel, kind in enumerate(("intact", "broken")):
        left = 55 + panel * 510; top = 145; size = 430
        d.text((left, 115), f"{kind.capitalize()} relation plane", fill="#172033", font=f(20, True))
        d.rectangle((left, top, left + size, top + size), fill="white", outline="#cbd3df")
        d.line((left + size/2, top, left + size/2, top + size), fill="#6b7484", width=2)
        d.line((left, top + size/2, left + size, top + size/2), fill="#6b7484", width=2)
        part = samples[samples.kind == kind]
        prev = None
        previous_key = None
        for row in part.itertuples():
            x = left + float(row.x_ara) / 2 * size
            y = top + (2 - float(row.y_ara)) / 2 * size
            key = (row.lineage, int(row.block_start))
            if prev is not None and key == previous_key:
                d.line((prev[0], prev[1], x, y), fill="#c2c9d3", width=1)
            d.ellipse((x-2, y-2, x+2, y+2), fill=colors[row.state])
            prev = (x, y)
            previous_key = key
        for label, xx, yy in (("Ba",.05,.06),("Ab",.87,.06),("bA",.05,.91),("aB",.87,.91)):
            d.text((left + xx*size, top + yy*size), label, fill="#172033", font=f(15, True))

    # Leave a dedicated title/column-label band above the matrix.
    left, top, cell = 1090, 190, 92
    d.text((left, 115), "Identity-specific 4×4 holdout transitions", fill="#172033", font=f(19, True))
    table = transitions[transitions.split == "holdout"].pivot(index="from_state", columns="to_state", values="count").reindex(index=LABELS, columns=LABELS).fillna(0)
    maximum = max(1, int(table.to_numpy().max()))
    for i, fr in enumerate(LABELS):
        d.text((left-38, top+i*cell+35), fr, fill="#596579", font=f(14, True))
        d.text((left+i*cell+38, top-25), fr, fill="#596579", font=f(14, True))
        for j, to in enumerate(LABELS):
            val = int(table.loc[fr,to]); shade = int(245 - 155 * val / maximum)
            fill = (shade, min(245,shade+20), min(255,shade+38))
            d.rectangle((left+j*cell, top+i*cell, left+(j+1)*cell-5, top+(i+1)*cell-5), fill=fill)
            d.text((left+j*cell+12, top+i*cell+36), f"{val:,}", fill="#172033", font=f(13))

    d.text((55, 630), "Holdout log loss", fill="#172033", font=f(22, True))
    vals = [("intact parent",summary_row.parent_log_loss,"#4c78a8"),("radial child",summary_row.radial_child_log_loss,"#9da8b6"),("angular child",summary_row.angular_child_log_loss,"#bac2cd"),("broken median",summary_row.broken_median_log_loss,"#d79a2b")]
    vmax = max(x[1] for x in vals)
    for i,(name,value,color) in enumerate(vals):
        yy=680+i*52; d.text((55,yy),name,fill="#465269",font=f(16)); d.rectangle((230,yy,690,yy+24),fill="#e2e6ec"); d.rectangle((230,yy,230+450*value/vmax,yy+24),fill=color); d.text((705,yy),f"{value:.5f}",fill="#172033",font=f(16))

    d.text((900, 630), "Broken-pair null distribution", fill="#172033", font=f(22, True))
    values = broken.holdout_log_loss.to_numpy(float)
    lo, hi = float(values.min()), float(values.max())
    hist, edges = np.histogram(values, bins=30)
    bx0, by0, bw, bh = 900, 690, 620, 210
    d.rectangle((bx0,by0,bx0+bw,by0+bh),fill="white",outline="#cbd3df")
    for i,h in enumerate(hist):
        x1=bx0+i*bw/len(hist); x2=bx0+(i+1)*bw/len(hist)-2; height=bh*0.86*h/max(1,hist.max()); d.rectangle((x1,by0+bh-height,x2,by0+bh),fill="#d79a2b")
    px=bx0+(summary_row.parent_log_loss-lo)/max(EPS,hi-lo)*bw
    d.line((px,by0,px,by0+bh),fill="#172033",width=4)
    d.text((bx0,915),f"broken range {lo:.5f}–{hi:.5f}",fill="#596579",font=f(15)); d.text((bx0+360,915),f"intact {summary_row.parent_log_loss:.5f}",fill="#172033",font=f(15,True))
    d.text((55, 950), f"Frozen result: {'PASS' if summary_row.domain_pass else ('INELIGIBLE' if not summary_row.eligible else 'NO PASS')} · p radial={summary_row.p_radial:.4f} · p angular={summary_row.p_angular:.4f} · p broken={summary_row.p_broken:.4f}", fill="#172033", font=f(17, True))
    img.save(DOMAIN_FIGURES / f"T343_{domain}_PARENT_COUPLING.png")


def write_explorer(summary: pd.DataFrame, samples: pd.DataFrame, transitions: pd.DataFrame, broken: pd.DataFrame) -> None:
    data = {
        "summary": summary.replace({np.nan: None}).to_dict("records"),
        "samples": samples.replace({np.nan: None}).to_dict("records"),
        "transitions": transitions[transitions.split == "holdout"].replace({np.nan: None}).to_dict("records"),
        "broken": broken.replace({np.nan: None}).to_dict("records"),
    }
    payload = json.dumps(data, separators=(",", ":"))
    html = r'''<!doctype html><html><head><meta charset="utf-8"><title>T343 Di-ARA parent coupling explorer</title><style>
body{margin:0;background:#0d1118;color:#e6edf3;font-family:Segoe UI,Arial,sans-serif}.wrap{max-width:1500px;margin:auto;padding:24px}h1{margin:0 0 6px}.sub{color:#9ba7b6}.controls{display:flex;gap:14px;align-items:center;margin:18px 0;flex-wrap:wrap}select,button{background:#172130;color:#fff;border:1px solid #39485e;padding:9px 13px;border-radius:8px}.grid{display:grid;grid-template-columns:1.25fr .75fr;gap:16px}.card{background:#131b27;border:1px solid #27354a;border-radius:14px;padding:16px}canvas{width:100%;height:auto;background:#0f1620;border-radius:9px}.metrics{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}.metric{background:#0f1620;padding:11px;border-radius:8px}.v{font-size:22px;font-weight:700}.k{color:#93a1b4;font-size:12px}.note{color:#8996a8;font-size:13px}@media(max-width:900px){.grid{grid-template-columns:1fr}}
</style></head><body><div class="wrap"><h1>T343 — Di-ARA parent coupling in 3D</h1><div class="sub">X and Y are the two ARA waves; Z is native ordered progression. Drag to rotate. Toggle intact versus locally broken coupling.</div><div class="controls"><label>Medium <select id="domain"></select></label><button id="kind">showing: intact</button><button id="reset">reset view</button><span id="verdict"></span></div><div class="grid"><div class="card"><canvas id="plot" width="900" height="720"></canvas><div class="note">Ridge planes: X=1 and Y=1. Raw selected ordered points remain visible; no smoothing controls the result.</div></div><div><div class="card"><h2>Parent comparison</h2><div class="metrics" id="metrics"></div></div><div class="card" style="margin-top:16px"><h2>Identity-specific transitions</h2><canvas id="matrix" width="560" height="480"></canvas></div><div class="card" style="margin-top:16px"><h2>Broken-pair loss distribution</h2><canvas id="hist" width="560" height="260"></canvas></div></div></div></div><script>
const D=JSON.parse(''' + payload + r'''), sel=document.querySelector('#domain');D.summary.forEach(x=>sel.add(new Option(x.domain,x.domain)));let kind='intact',yaw=-.7,pitch=.55,drag=false,last=null;const colors={bA:'#6ea0d5',aB:'#eea24b',Ab:'#79ad72',Ba:'#d88390'};function proj(x,y,z,w,h){x-=1;y-=1;z=(z-.5)*2;let cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);let X=cy*x+sy*z,Z=-sy*x+cy*z,Y=cp*y-sp*Z;Z=sp*y+cp*Z;let sc=230/(2.5+Z);return[w/2+X*sc,h/2-Y*sc]};function draw(){let dom=sel.value,s=D.summary.find(x=>x.domain===dom);document.querySelector('#verdict').textContent=s.domain_pass?'PASS':(s.eligible?'NO PASS':'INELIGIBLE');let c=document.querySelector('#plot'),g=c.getContext('2d');g.clearRect(0,0,c.width,c.height);g.strokeStyle='#344255';g.lineWidth=1;for(let v=0;v<=2;v+=.25){for(const plane of [0,1]){let p1=plane?proj(1,v,0,c.width,c.height):proj(v,1,0,c.width,c.height),p2=plane?proj(1,v,1,c.width,c.height):proj(v,1,1,c.width,c.height);g.beginPath();g.moveTo(...p1);g.lineTo(...p2);g.stroke()}}let pts=D.samples.filter(x=>x.domain===dom&&x.kind===kind);let prev=null;pts.forEach(p=>{let q=proj(p.x_ara,p.y_ara,p.native_fraction,c.width,c.height);if(prev){g.strokeStyle='rgba(160,170,185,.18)';g.beginPath();g.moveTo(...prev);g.lineTo(...q);g.stroke()}g.fillStyle=colors[p.state];g.globalAlpha=.7;g.fillRect(q[0]-2,q[1]-2,4,4);prev=q});g.globalAlpha=1;g.fillStyle='#dce4ee';g.fillText('Ba | Ab / upper',20,25);g.fillText('bA | aB / lower',20,45);document.querySelector('#metrics').innerHTML=[['parent loss',s.parent_log_loss],['radial child',s.radial_child_log_loss],['angular child',s.angular_child_log_loss],['broken median',s.broken_median_log_loss],['Δ radial',s.delta_radial],['Δ angular',s.delta_angular],['Δ broken',s.delta_broken_median],['p broken',s.p_broken]].map(v=>`<div class=metric><div class=v>${Number(v[1]).toFixed(4)}</div><div class=k>${v[0]}</div></div>`).join('');drawMatrix(dom);drawHist(dom)}function drawMatrix(dom){let c=document.querySelector('#matrix'),g=c.getContext('2d');g.clearRect(0,0,c.width,c.height);let names=['bA','aB','Ab','Ba'],rows=D.transitions.filter(x=>x.domain===dom),mx=Math.max(...rows.map(x=>x.count),1);rows.forEach(r=>{let i=names.indexOf(r.from_state),j=names.indexOf(r.to_state),x=125+j*92,y=45+i*92,a=.12+.88*r.count/mx;g.fillStyle=`rgba(76,120,168,${a})`;g.fillRect(x,y,82,82);g.fillStyle='#fff';g.fillText(r.count.toLocaleString(),x+8,y+43)});g.fillStyle='#9ba7b6';names.forEach((n,i)=>{g.fillText(n,157+i*92,425);g.fillText(n,55,90+i*92)})}function drawHist(dom){let c=document.querySelector('#hist'),g=c.getContext('2d'),s=D.summary.find(x=>x.domain===dom),v=D.broken.filter(x=>x.domain===dom).map(x=>x.holdout_log_loss),lo=Math.min(...v),hi=Math.max(...v),bins=30,h=Array(bins).fill(0);v.forEach(x=>h[Math.min(bins-1,Math.floor((x-lo)/(hi-lo+1e-12)*bins))]++);g.clearRect(0,0,c.width,c.height);let mx=Math.max(...h);h.forEach((n,i)=>{g.fillStyle='#d79a2b';g.fillRect(35+i*16,235-190*n/mx,14,190*n/mx)});let px=35+(s.parent_log_loss-lo)/(hi-lo+1e-12)*bins*16;g.strokeStyle='#e6edf3';g.lineWidth=3;g.beginPath();g.moveTo(px,30);g.lineTo(px,235);g.stroke();g.fillStyle='#9ba7b6';g.fillText('vertical line = intact parent',330,22)}sel.onchange=draw;document.querySelector('#kind').onclick=()=>{kind=kind==='intact'?'broken':'intact';document.querySelector('#kind').textContent='showing: '+kind;draw()};document.querySelector('#reset').onclick=()=>{yaw=-.7;pitch=.55;draw()};let canvas=document.querySelector('#plot');canvas.onmousedown=e=>{drag=true;last=[e.clientX,e.clientY]};window.onmouseup=()=>drag=false;window.onmousemove=e=>{if(!drag)return;yaw+=(e.clientX-last[0])*.008;pitch+=(e.clientY-last[1])*.008;last=[e.clientX,e.clientY];draw()};draw();
</script></body></html>'''
    # Do not draw artificial bridges between separately frozen blocks in 3D.
    html = html.replace(
        "let prev=null;pts.forEach(p=>{let q=proj(p.x_ara,p.y_ara,p.native_fraction,c.width,c.height);if(prev){",
        "let prev=null,prevKey=null;pts.forEach(p=>{let q=proj(p.x_ara,p.y_ara,p.native_fraction,c.width,c.height),key=p.lineage+'|'+p.block_start;if(prev&&key===prevKey){",
    ).replace(
        "g.fillRect(q[0]-2,q[1]-2,4,4);prev=q});g.globalAlpha=1;",
        "g.fillRect(q[0]-2,q[1]-2,4,4);prev=q;prevKey=key});g.globalAlpha=1;",
    )
    OUT_EXPLORER.write_text(html, encoding="utf-8")


def write_report(summary: pd.DataFrame, verdict: str, results: dict) -> None:
    lines = [
        "# T343 — intact-versus-broken Di-ARA parent coupling",
        "",
        "**Run:** 5 August 2026  ",
        f"**Frozen verdict:** **{verdict}**  ",
        f"**Eligible/pass:** `{results['eligible_domains']}` eligible, `{results['passing_domains']}` pass",
        "",
        "## Result first",
        "",
        results["result_first"],
        "",
        "T343 allowed every domain its own complete `4×4` movement relation. It did not require adjacency, clockwise movement, one cadence or one universal quadrant order.",
        "",
        "## Holdout results",
        "",
        "| domain | parent loss | radial child | angular child | broken median | Δ radial | Δ angular | Δ broken | p broken | verdict |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary.sort_values("domain").itertuples():
        status = "PASS" if row.domain_pass else ("INELIGIBLE" if not row.eligible else "NO PASS")
        lines.append(f"| {row.domain} | {row.parent_log_loss:.6f} | {row.radial_child_log_loss:.6f} | {row.angular_child_log_loss:.6f} | {row.broken_median_log_loss:.6f} | {row.delta_radial:+.6f} | {row.delta_angular:+.6f} | {row.delta_broken_median:+.6f} | {row.p_broken:.4f} | {status} |")
    lines += [
        "",
        "Positive deltas favour the intact parent. Parent-versus-child p-values use 10,000 sign flips of non-overlapping block means. Broken-pair p-values use 1,000 circular shifts of one ARA axis inside every frozen block.",
        "",
        "## What is load-bearing",
        "",
        results["interpretation"],
        "",
        "The four-region map and TE-ARA complements remain geometric bookkeeping. The empirical result is the out-of-sample information advantage, or lack of it, over same-data controls.",
        "",
        "## Evidence boundary",
        "",
        "This is a frozen cross-question test on the T342 source battery, not an untouched-source discovery. Two pre-score addenda corrected the measured child rung and the inference unit before any T343 endpoint was calculated. Named lineages are reported; block-level inference remains a dependence caveat for future independent replication.",
        "",
        "Exact `e`, Phi and anti-Phi locations were excluded from scoring. T343 tests whether the two declared axes couple, not whether their numerical landmarks are universal.",
        "",
        "## Post-result control audit",
        "",
        "A later data-quality audit found that the registered circular shifts can wrap later native axis values into earlier predictor states. The frozen `1/6` score remains unchanged, but its broken-pair gate is not a leakage-free causal test. A past-only/no-wrap matched sensitivity passed in bubbles, cold room and qutrit—the same three eligible domains that beat both one-axis children. That `3/6` pattern is post-result and cannot replace or rescue T343; it requires a new frozen replication. See `T343_BROKEN_CONTROL_TEMPORAL_LEAKAGE_AUDIT_REPORT_2026-08-05.md`.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        "$env:PYTHONPATH='analysis/irrationality_te_ara_multimedium/vendor'",
        "& 'C:/Users/Dylan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/irrationality_te_ara_multimedium/t343_intact_vs_broken_di_ara_parent_coupling.py",
        "& 'C:/Users/Dylan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/irrationality_te_ara_multimedium/validate_t343_intact_vs_broken_di_ara_parent_coupling.py",
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def clean_json(value):
    if isinstance(value, dict): return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list): return [clean_json(v) for v in value]
    if isinstance(value, (np.bool_, bool)): return bool(value)
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, (np.floating, float)): return None if not math.isfinite(float(value)) else float(value)
    return value


def main() -> None:
    for path, expected in ((PROTOCOL, EXPECTED_PROTOCOL_HASH), (COMP_ADDENDUM, EXPECTED_COMP_HASH), (INF_ADDENDUM, EXPECTED_INF_HASH)):
        if sha256(path) != expected:
            raise RuntimeError(f"Frozen hash mismatch: {path.name}")

    rng = np.random.default_rng(SHIFT_SEED)
    fractions = rng.uniform(0.10, 0.90, size=BROKEN_CONTROLS)
    loaders = [
        ("pendulum", base.load_pendulum), ("hydraulic", base.load_hydraulic),
        ("bubbles", base.load_bubbles), ("cold_room", base.load_cold_room),
        ("acoustics", base.load_acoustics), ("qutrit", base.load_qutrit),
        ("river", base.load_river),
    ]
    summary_rows=[]; model_rows=[]; broken_rows=[]; effect_rows=[]; trans_rows=[]; sample_rows=[]; quality_rows=[]; source_paths={}
    for offset,(domain,loader) in enumerate(loaders):
        print(f"loading {domain}...", flush=True)
        blocks, quality, paths = loader(); source_paths[domain]=paths
        print(f"  scoring intact, children, and {BROKEN_CONTROLS} broken pairings", flush=True)
        row, models, nulls, effects, trans, visual, qrow = analyze_domain(domain, blocks, quality, offset, fractions)
        summary_rows.append(row); model_rows.extend(models); broken_rows.extend(nulls); effect_rows.extend(effects); trans_rows.extend(trans); sample_rows.extend(visual); quality_rows.append(qrow)
        del blocks

    summary = pd.DataFrame(summary_rows)
    models = pd.DataFrame(model_rows); broken = pd.DataFrame(broken_rows); effects = pd.DataFrame(effect_rows)
    transitions = pd.DataFrame(trans_rows); samples = pd.DataFrame(sample_rows); quality = pd.DataFrame(quality_rows)
    eligible = int(summary.eligible.sum()); passing = int(summary.domain_pass.sum())
    if eligible >= 5 and passing / eligible >= 0.70:
        verdict = "SUPPORTED AS A TRANSFERABLE PARENT-COUPLING RULE"
    elif passing >= 2:
        verdict = "PARTIAL / PAIR-SPECIFIC"
    else:
        verdict = "NOT SUPPORTED BY THIS CONSTRUCTION"
    result_first = f"The intact Di-ARA parent passed all child-only and broken-pair gates in {passing}/{eligible} eligible domains. The frozen cross-domain verdict is **{verdict}**."
    pass_domains = summary.loc[summary.domain_pass, "domain"].tolist()
    fail_domains = summary.loc[summary.eligible & ~summary.domain_pass, "domain"].tolist()
    interpretation = (
        f"Passing domains: {', '.join(pass_domains) if pass_domains else 'none'}. "
        f"Eligible non-passing domains: {', '.join(fail_domains) if fail_domains else 'none'}. "
        "A pass means the intact joint address transferred more future-state information than both one-axis projections and at least 95% of matched broken pairings."
    )
    results = {
        "test_id": "T343-INTACT-VS-BROKEN-DI-ARA-PARENT-COUPLING-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "computational_addendum_sha256": sha256(COMP_ADDENDUM),
        "inference_addendum_sha256": sha256(INF_ADDENDUM),
        "verdict": verdict,
        "eligible_domains": eligible,
        "passing_domains": passing,
        "pass_domains": pass_domains,
        "result_first": result_first,
        "interpretation": interpretation,
        "domain_results": summary.replace({np.nan: None}).to_dict("records"),
        "evidence_class": "Frozen cross-question test on previously opened T342 sources; not an untouched-source discovery.",
        "framework_boundary": "Common Di-ARA geometry does not require a common gait. Exact e/Phi landmarks were not scored.",
        "post_result_control_audit": "Circular-shift controls contained future exposure. Frozen score unchanged; past-only sensitivity passed bubbles, cold room and qutrit (3/6), post-result only.",
    }
    manifest = base.file_manifest(source_paths)
    manifest.update({
        "t343_protocol_sha256": sha256(PROTOCOL),
        "t343_computational_addendum_sha256": sha256(COMP_ADDENDUM),
        "t343_inference_addendum_sha256": sha256(INF_ADDENDUM),
    })
    OUT_RESULTS.write_text(json.dumps(clean_json(results), indent=2), encoding="utf-8")
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    summary.to_csv(OUT_SUMMARY,index=False); models.to_csv(OUT_MODEL_COUNTS,index=False); broken.to_csv(OUT_BROKEN,index=False); effects.to_csv(OUT_BLOCK_EFFECTS,index=False); transitions.to_csv(OUT_TRANSITIONS,index=False); samples.to_csv(OUT_SAMPLES,index=False); quality.to_csv(OUT_QUALITY,index=False)
    DOMAIN_FIGURES.mkdir(exist_ok=True)
    draw_summary(summary, verdict)
    for row in summary.itertuples():
        draw_domain_figure(row.domain, summary[summary.domain==row.domain].iloc[0], samples[samples.domain==row.domain], transitions[transitions.domain==row.domain], broken[broken.domain==row.domain])
    write_explorer(summary, samples, transitions, broken)
    write_report(summary, verdict, results)
    print(json.dumps(clean_json(results), indent=2), flush=True)


if __name__ == "__main__":
    main()
