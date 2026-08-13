#!/usr/bin/env python3
"""Post-result T343 audit of circular-shift temporal leakage.

The frozen T343 result is never changed here. This audit asks whether a
circularly shifted current-state axis can contain values from later native
times, then repeats the broken-pair comparison with past-only, no-wrap lags
and a matched intact comparator on exactly the same retained transitions.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

import t343_intact_vs_broken_di_ara_parent_coupling as t343


STEM = "T343_BROKEN_CONTROL_TEMPORAL_LEAKAGE_AUDIT"
OUT_RESULTS = HERE / f"{STEM}_RESULTS.json"
OUT_CONTROLS = HERE / f"{STEM}_CONTROLS.csv"
OUT_SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
OUT_FIGURE = HERE / f"{STEM}_FIGURE.png"
OUT_REPORT = HERE / f"{STEM}_REPORT_2026-08-05.md"
REPS = t343.BROKEN_CONTROLS
SEED = t343.SHIFT_SEED
ALPHA = t343.ALPHA
DOMAINS = (
    ("pendulum", t343.base.load_pendulum),
    ("hydraulic", t343.base.load_hydraulic),
    ("bubbles", t343.base.load_bubbles),
    ("cold_room", t343.base.load_cold_room),
    ("acoustics", t343.base.load_acoustics),
    ("qutrit", t343.base.load_qutrit),
    ("river", t343.base.load_river),
)


def probabilities(counts: np.ndarray) -> np.ndarray:
    x = counts.astype(float) + ALPHA
    return x / x.sum(axis=1, keepdims=True)


def loss(counts: np.ndarray, p: np.ndarray) -> float:
    n = int(counts.sum())
    return float(-np.sum(counts * np.log(p)) / n) if n else float("nan")


def grouped(blocks: list[t343.base.Block]) -> dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    by_length: dict[int, list[t343.base.Block]] = defaultdict(list)
    for block in blocks:
        if len(block.a) >= 3:
            by_length[len(block.a)].append(block)
    answer = {}
    for n, items in by_length.items():
        aa = np.stack([(x.a >= 0).astype(np.int8) for x in items])
        bb = np.stack([(x.b >= 0).astype(np.int8) for x in items])
        qq = np.where(bb, np.where(aa, 2, 3), np.where(aa, 1, 0)).astype(np.int8)
        answer[n] = (aa, bb, qq)
    return answer


def causal_tables(groups: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]], fractions: np.ndarray):
    cache = {}
    for n, (aa, bb, qq) in groups.items():
        for rep, fraction in enumerate(fractions):
            axis = 0 if (rep + 1) % 2 else 1
            # A causal lag must leave at least one t -> t+1 transition.
            k = max(1, min(n - 2, int(round(float(fraction) * n))))
            key = (axis, n, k)
            if key in cache:
                continue
            if axis == 0:
                ca, cb = aa[:, : n - 1 - k], bb[:, k : n - 1]
            else:
                ca, cb = aa[:, k : n - 1], bb[:, : n - 1 - k]
            broken_current = np.where(cb, np.where(ca, 2, 3), np.where(ca, 1, 0)).astype(np.int8)
            intact_current = qq[:, k : n - 1]
            target = qq[:, k + 1 : n]
            broken_codes = 4 * broken_current.ravel() + target.ravel()
            intact_codes = 4 * intact_current.ravel() + target.ravel()
            cache[key] = (
                np.bincount(broken_codes, minlength=16).reshape(4, 4),
                np.bincount(intact_codes, minlength=16).reshape(4, 4),
            )
    return cache


def original_exposure(groups: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]], fraction: float) -> tuple[float, float, int]:
    future = direct = total = 0
    for n, (aa, _bb, _qq) in groups.items():
        blocks = len(aa)
        k = max(1, min(n - 1, int(round(float(fraction) * n))))
        current = np.arange(n - 1)
        source = (current - k) % n
        future += int(np.count_nonzero(source > current)) * blocks
        direct += int(np.count_nonzero(source == current + 1)) * blocks
        total += (n - 1) * blocks
    if not total:
        return float("nan"), float("nan"), 0
    return future / total, direct / total, total


def audit_domain(domain: str, blocks: list[t343.base.Block], fractions: np.ndarray):
    selected = t343.base.cap_blocks(blocks)
    cal = grouped([x for x in selected if x.split == "calibration"])
    hold = grouped([x for x in selected if x.split == "holdout"])
    cal_cache = causal_tables(cal, fractions)
    hold_cache = causal_tables(hold, fractions)
    lengths = sorted(set(cal) | set(hold))
    rows = []
    for rep, fraction in enumerate(fractions):
        axis = 0 if (rep + 1) % 2 else 1
        cb_cal = np.zeros((4, 4), dtype=np.int64)
        ci_cal = np.zeros((4, 4), dtype=np.int64)
        cb_hold = np.zeros((4, 4), dtype=np.int64)
        ci_hold = np.zeros((4, 4), dtype=np.int64)
        for n in lengths:
            k = max(1, min(n - 2, int(round(float(fraction) * n))))
            if (axis, n, k) in cal_cache:
                b, i = cal_cache[(axis, n, k)]; cb_cal += b; ci_cal += i
            if (axis, n, k) in hold_cache:
                b, i = hold_cache[(axis, n, k)]; cb_hold += b; ci_hold += i
        causal_broken = loss(cb_hold, probabilities(cb_cal))
        matched_intact = loss(ci_hold, probabilities(ci_cal))
        future, direct, original_n = original_exposure(hold, float(fraction))
        rows.append({
            "domain": domain,
            "replicate": rep + 1,
            "axis_shifted": "radial_a" if axis == 0 else "angular_b",
            "shift_fraction": float(fraction),
            "original_circular_future_share": future,
            "original_circular_direct_target_share": direct,
            "original_holdout_transitions": original_n,
            "causal_holdout_transitions": int(ci_hold.sum()),
            "matched_intact_log_loss": matched_intact,
            "causal_broken_log_loss": causal_broken,
            "causal_delta": causal_broken - matched_intact,
        })
    frame = pd.DataFrame(rows)
    valid = frame[np.isfinite(frame.causal_delta) & (frame.causal_holdout_transitions >= 1000)]
    p = float((1 + np.count_nonzero(valid.causal_delta.to_numpy(float) <= 0)) / (len(valid) + 1)) if len(valid) else float("nan")
    summary = {
        "domain": domain,
        "controls": len(frame),
        "eligible_causal_controls": len(valid),
        "median_original_future_share": float(frame.original_circular_future_share.median()),
        "q95_original_future_share": float(frame.original_circular_future_share.quantile(0.95)),
        "median_original_direct_target_share": float(frame.original_circular_direct_target_share.median()),
        "controls_with_direct_target_share_over_05": int((frame.original_circular_direct_target_share > 0.05).sum()),
        "median_causal_delta": float(valid.causal_delta.median()) if len(valid) else float("nan"),
        "q05_causal_delta": float(valid.causal_delta.quantile(0.05)) if len(valid) else float("nan"),
        "q95_causal_delta": float(valid.causal_delta.quantile(0.95)) if len(valid) else float("nan"),
        "p_causal_broken_not_worse": p,
        "causal_pairing_pass": bool(len(valid) >= 100 and valid.causal_delta.median() > 0 and p <= 0.05),
    }
    return frame, summary


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(str(path), size)


def draw(summary: pd.DataFrame) -> None:
    w, h = 1700, 980
    img = Image.new("RGB", (w, h), "#f5f7fa")
    d = ImageDraw.Draw(img)
    d.text((55, 35), "T343 broken-control temporal leakage audit", fill="#172033", font=font(40, True))
    d.text((55, 92), "Frozen circular controls versus post-result past-only matched controls", fill="#5b687d", font=font(20))
    d.rounded_rectangle((55, 140, 1645, 250), 18, fill="#e7eef7")
    d.text((82, 164), "A circular shift can move later axis values to earlier current states.", fill="#172033", font=font(25, True))
    d.text((82, 205), "Gold measures future exposure in the frozen null; blue measures the causal broken-minus-intact loss.", fill="#5b687d", font=font(17))
    max_delta = max(0.01, float(np.nanmax(np.abs(summary.median_causal_delta.to_numpy(float)))))
    for i, row in enumerate(summary.itertuples(index=False)):
        y = 300 + i * 86
        d.text((60, y), row.domain, fill="#172033", font=font(18, True))
        d.text((230, y), f"future {100*row.median_original_future_share:5.1f}%", fill="#8b5a00", font=font(16))
        d.rectangle((390, y + 2, 800, y + 23), fill="#e3e7ed")
        d.rectangle((390, y + 2, 390 + 410 * row.median_original_future_share, y + 23), fill="#d89a28")
        zero = 1140
        d.line((zero, y - 5, zero, y + 34), fill="#263246", width=2)
        if math.isfinite(row.median_causal_delta):
            end = zero + row.median_causal_delta / max_delta * 340
            d.line((zero, y + 14, end, y + 14), fill="#4c78a8", width=10)
            d.text((1500, y), f"{row.median_causal_delta:+.3f}", fill="#172033", font=font(16, True))
        d.text((825, y + 34), f"direct-target controls {row.controls_with_direct_target_share_over_05}/1000", fill="#5b687d", font=font(15))
    d.text((55, 925), "Positive blue = exact intact pairing predicts better on the same causal transitions. Post-result diagnostic only.", fill="#5b687d", font=font(16))
    img.save(OUT_FIGURE)


def clean(value):
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list): return [clean(v) for v in value]
    if isinstance(value, (np.bool_, bool)): return bool(value)
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, (np.floating, float)): return None if not math.isfinite(float(value)) else float(value)
    return value


def main() -> None:
    fractions = np.random.default_rng(SEED).uniform(0.10, 0.90, REPS)
    all_rows = []
    summaries = []
    for domain, loader in DOMAINS:
        print(f"auditing {domain}...", flush=True)
        blocks, _quality, _paths = loader()
        controls, summary = audit_domain(domain, blocks, fractions)
        all_rows.append(controls); summaries.append(summary)
    controls = pd.concat(all_rows, ignore_index=True)
    summary = pd.DataFrame(summaries)
    controls.to_csv(OUT_CONTROLS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    result = {
        "audit_id": "T343-post-result-circular-shift-temporal-leakage-v1",
        "status": "post-result diagnostic; frozen T343 score unchanged",
        "finding": "The frozen circular-shift null exposes current predictors to later native axis values. Past-only no-wrap matched controls are the appropriate causal sensitivity check.",
        "domains": summary.to_dict("records"),
    }
    OUT_RESULTS.write_text(json.dumps(clean(result), indent=2), encoding="utf-8")
    draw(summary)
    lines = [
        "# T343 broken-control temporal-leakage audit",
        "",
        "**Run:** 5 August 2026  ",
        "**Status:** post-result diagnostic; the frozen T343 score and protocol remain unchanged",
        "",
        "## Result first",
        "",
        "The circular-shift null is not a clean causal broken-pair control for a next-state target. For part of every shifted block it places later native axis values at earlier current states. Large shifts can place the actual next axis value directly in the predictor. The frozen `1/6` result remains the correct score for its registered construction, but its broken-pair gate must not be interpreted as a leakage-free causal test of intact coupling.",
        "",
        "## Audit table",
        "",
        "| domain | median frozen future share | frozen controls >5% direct target | eligible causal controls | median causal broken-intact delta | causal p | sensitivity pass |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary.itertuples(index=False):
        status = "PASS" if row.causal_pairing_pass else "NO PASS"
        lines.append(f"| {row.domain} | {100*row.median_original_future_share:.2f}% | {row.controls_with_direct_target_share_over_05}/1000 | {row.eligible_causal_controls} | {row.median_causal_delta:+.6f} | {row.p_causal_broken_not_worse:.4f} | {status} |")
    lines += [
        "",
        "Positive causal delta means the past-only broken pairing had higher loss than the intact pairing on exactly the same retained transitions. Both calibration fitting and holdout scoring use the same no-wrap subset for that replicate.",
        "",
        "## Evidence fence",
        "",
        "This audit was conceived after the frozen result was visible. It cannot replace, rescue or overturn T343. It diagnoses the control and defines a better future design. The causal sensitivity is itself post-result and must be independently frozen on a new source battery before being used as confirmatory evidence.",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
