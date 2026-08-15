#!/usr/bin/env python3
"""T385: causal Irrationality Di-ARA detector-proxy test on BUAP waveforms.

The analysis is frozen by
T385_BUAP_CAUSAL_IRRATIONALITY_DI_ARA_PROTOCOL_2026-08-15.md.
It intentionally treats the waveform as a Class-D detector proxy.  It does
not identify the waveform coordinates as unobserved muon/neutrino children.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
VENDOR = HERE / "_vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))
MPL_CONFIG = HERE / "_matplotlib_cache"
MPL_CONFIG.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG))

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit


RAW = Path(
    r"F:\SystemFormulaFolder\DataTEsted(TOBEDELETEDBEFOREGIT)\muon_buap\MD10000Last.csv"
)
OUT = HERE / "T385_buap_causal_irrationality_di_ara"
PROTOCOL = HERE / "T385_BUAP_CAUSAL_IRRATIONALITY_DI_ARA_PROTOCOL_2026-08-15.md"

EXPECTED_RAW_SHA256 = "C2DC1E012FBDF0F3C5EC305E2D8E4DD1D87B05DF5CBA39B492189C0F7D5454CD"
EXPECTED_PROTOCOL_SHA256 = "8ADFC0A09DC03E70B07F2A68B8EE950F87CCA218A344B21DDED1FAAE2003499C"

DT_NS = 8
VETO_NS = 150
MIN_AMP_MV = 10.0
W = 16
STRIDE = 8
LAG = 2
EPS_MV = 0.05
RECOVERY = 32
GUARD = 16
POSITIVE_MAX_LEAD = 48
NEGATIVE_MIN_LEAD = 80
SEED = 385

SPLITS = (
    (0, 500, "engineering"),
    (500, 2000, "calibration"),
    (2000, 3500, "validation"),
    (3500, 10**9, "evaluation"),
)

META_RE = re.compile(
    r"^(?P<date>\d{8})-(?P<time>\d{6}) (?:Evt number: |Evt:)(?P<event>\d+)"
)

FEATURES = {
    "M0": [],
    "MT": ["elapsed_us"],
    "MG": [
        "elapsed_us",
        "rms_current",
        "rms_previous",
        "mean_current",
        "std_current",
        "total_variation",
        "direct_path",
        "total_path",
    ],
    "MA": [
        "elapsed_us",
        "rms_current",
        "rms_previous",
        "mean_current",
        "std_current",
        "total_variation",
        "direct_path",
        "total_path",
        "x_radial",
        "x_history",
        "ridge_product",
        "dx_radial",
        "dx_history",
    ],
    "MLEAK": [
        "elapsed_us",
        "rms_current",
        "rms_previous",
        "mean_current",
        "std_current",
        "total_variation",
        "direct_path",
        "total_path",
        "row_samples",
        "remaining_to_end_us",
    ],
}


@dataclass
class Event:
    row: int
    split: str
    event_id: int
    timestamp: str
    values: np.ndarray
    label_baseline: float
    causal_baseline: float
    first_index: int
    second_index: int
    first_amp: float
    second_amp: float
    eligible: bool
    exclusion: str

    @property
    def delay_ns(self) -> int:
        return int((self.second_index - self.first_index) * DT_NS)


@dataclass
class LogisticModel:
    name: str
    features: list[str]
    mean: np.ndarray
    scale: np.ndarray
    coef: np.ndarray
    success: bool

    def matrix(self, rows: list[dict]) -> np.ndarray:
        if not self.features:
            return np.ones((len(rows), 1), dtype=float)
        x = np.asarray([[r[k] for k in self.features] for r in rows], dtype=float)
        x = (x - self.mean) / self.scale
        return np.column_stack([np.ones(len(x)), x])

    def predict(self, rows: list[dict]) -> np.ndarray:
        return expit(self.matrix(rows) @ self.coef)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def split_for_row(row: int) -> str:
    for start, end, name in SPLITS:
        if start <= row < end:
            return name
    raise ValueError(row)


def locate_pulses(values_mv: np.ndarray) -> tuple[float, int, int, float, float]:
    """Reproduce the public two-minimum logic without its trailing-size column."""
    baseline1 = float(np.mean(values_mv[1:11]))
    baseline2 = float(np.mean(values_mv[-11:-1]))
    baseline = max(baseline1, baseline2)
    usable = values_mv[:-1]
    strongest = int(np.argmin(usable))
    index = np.arange(len(usable))
    allowed = index[np.abs(index - strongest) > VETO_NS / DT_NS]
    if len(allowed) == 0:
        return baseline, -1, -1, math.nan, math.nan
    other = int(allowed[np.argmin(values_mv[allowed])])
    first, second = sorted((strongest, other))
    return (
        baseline,
        first,
        second,
        float(baseline - values_mv[first]),
        float(baseline - values_mv[second]),
    )


def parse_event(row: int, line: str) -> Event:
    parts = line.rstrip("\r\n").split(",")
    meta = META_RE.search(parts[0])
    if meta is None or len(parts) < 40:
        return Event(
            row,
            split_for_row(row),
            -1,
            "",
            np.asarray([], dtype=float),
            math.nan,
            math.nan,
            -1,
            -1,
            math.nan,
            math.nan,
            False,
            "parse_failure",
        )
    try:
        values = np.asarray(parts[1:-1], dtype=float) * 1000.0
    except ValueError:
        values = np.asarray([], dtype=float)
    if len(values) < 40 or not np.all(np.isfinite(values)):
        return Event(
            row,
            split_for_row(row),
            int(meta.group("event")),
            meta.group("date") + "-" + meta.group("time"),
            values,
            math.nan,
            math.nan,
            -1,
            -1,
            math.nan,
            math.nan,
            False,
            "nonfinite_or_short",
        )
    baseline, first, second, a1, a2 = locate_pulses(values)
    reason = ""
    if first < 15:
        reason = "insufficient_prepulse"
    elif min(a1, a2) < MIN_AMP_MV:
        reason = "pulse_below_10mV"
    elif second - first < RECOVERY + 2 * W + GUARD:
        reason = "insufficient_interpulse"
    causal_baseline = (
        float(np.mean(values[first - 15 : first - 5])) if first >= 15 else math.nan
    )
    return Event(
        row=row,
        split=split_for_row(row),
        event_id=int(meta.group("event")),
        timestamp=meta.group("date") + "-" + meta.group("time"),
        values=values,
        label_baseline=baseline,
        causal_baseline=causal_baseline,
        first_index=first,
        second_index=second,
        first_amp=a1,
        second_amp=a2,
        eligible=not reason,
        exclusion=reason or "eligible",
    )


def load_events(path: Path = RAW) -> list[Event]:
    events: list[Event] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for row, line in enumerate(handle):
            if line.strip():
                events.append(parse_event(row, line))
    return events


def path_metrics(current: np.ndarray) -> tuple[float, float, float]:
    z = np.column_stack([current[LAG:], current[:-LAG]])
    if len(z) < 2:
        return 0.0, 0.0, 0.0
    total = float(np.linalg.norm(np.diff(z, axis=0), axis=1).sum())
    direct = float(np.linalg.norm(z[-1] - z[0]))
    x_history = float(np.clip(2.0 * direct / (total + EPS_MV), 0.0, 2.0))
    return direct, total, x_history


def event_windows(event: Event, reverse: bool = False) -> list[dict]:
    if not event.eligible:
        return []
    y = event.values - event.causal_baseline
    start = event.first_index + RECOVERY
    last = event.second_index - GUARD
    if last - start + 1 < 2 * W:
        return []
    if reverse:
        y = y.copy()
        y[start : last + 1] = y[start : last + 1][::-1]
    rows: list[dict] = []
    previous_xr = 1.0
    previous_xh = 1.0
    for endpoint in range(start + 2 * W - 1, last + 1, STRIDE):
        current = y[endpoint - W + 1 : endpoint + 1]
        previous = y[endpoint - 2 * W + 1 : endpoint - W + 1]
        rms_current = float(np.sqrt(np.mean(current**2)))
        rms_previous = float(np.sqrt(np.mean(previous**2)))
        s = (rms_current + EPS_MV) / (rms_previous + EPS_MV)
        x_radial = float(2.0 * s / (1.0 + s))
        direct, total, x_history = path_metrics(current)
        lead_samples = event.second_index - endpoint
        if GUARD <= lead_samples < POSITIVE_MAX_LEAD:
            target = 1
        elif lead_samples >= NEGATIVE_MIN_LEAD:
            target = 0
        else:
            target = -1
        rows.append(
            {
                "row": event.row,
                "event_id": event.event_id,
                "split": event.split,
                "endpoint": endpoint,
                "target": target,
                "lead_ns": float(lead_samples * DT_NS),
                "elapsed_us": float((endpoint - event.first_index) * DT_NS / 1000.0),
                "rms_current": rms_current,
                "rms_previous": rms_previous,
                "mean_current": float(np.mean(current)),
                "std_current": float(np.std(current)),
                "total_variation": float(np.sum(np.abs(np.diff(current)))),
                "direct_path": direct,
                "total_path": total,
                "x_radial": x_radial,
                "x_history": x_history,
                "ridge_product": float((x_radial - 1.0) * (x_history - 1.0)),
                "dx_radial": float(x_radial - previous_xr),
                "dx_history": float(x_history - previous_xh),
                "row_samples": float(len(event.values)),
                "remaining_to_end_us": float(
                    (len(event.values) - 1 - endpoint) * DT_NS / 1000.0
                ),
            }
        )
        previous_xr, previous_xh = x_radial, x_history
    return rows


def balance_weights(rows: list[dict]) -> None:
    grouped: dict[int, dict[int, list[int]]] = {}
    for i, row in enumerate(rows):
        if row["target"] not in (0, 1):
            continue
        grouped.setdefault(row["row"], {0: [], 1: []})[row["target"]].append(i)
    for row in rows:
        row["weight"] = 0.0
    for classes in grouped.values():
        if not classes[0] or not classes[1]:
            continue
        for target in (0, 1):
            weight = 0.5 / len(classes[target])
            for i in classes[target]:
                rows[i]["weight"] = weight


def model_rows(rows: Iterable[dict]) -> list[dict]:
    return [r for r in rows if r["target"] in (0, 1) and r.get("weight", 0) > 0]


def weighted_mean_scale(x: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if x.shape[1] == 0:
        return np.asarray([], dtype=float), np.asarray([], dtype=float)
    wn = w / w.sum()
    mean = np.sum(x * wn[:, None], axis=0)
    var = np.sum((x - mean) ** 2 * wn[:, None], axis=0)
    return mean, np.maximum(np.sqrt(var), 1e-8)


def fit_logistic(name: str, rows: list[dict], l2: float = 1e-4) -> LogisticModel:
    features = FEATURES[name]
    y = np.asarray([r["target"] for r in rows], dtype=float)
    w = np.asarray([r["weight"] for r in rows], dtype=float)
    if features:
        raw = np.asarray([[r[k] for k in features] for r in rows], dtype=float)
        mean, scale = weighted_mean_scale(raw, w)
        x = (raw - mean) / scale
        design = np.column_stack([np.ones(len(x)), x])
    else:
        mean = np.asarray([], dtype=float)
        scale = np.asarray([], dtype=float)
        design = np.ones((len(rows), 1), dtype=float)

    def objective(beta: np.ndarray) -> tuple[float, np.ndarray]:
        z = design @ beta
        loss = float(np.sum(w * (np.logaddexp(0.0, z) - y * z)) / w.sum())
        grad = design.T @ (w * (expit(z) - y)) / w.sum()
        if len(beta) > 1:
            loss += 0.5 * l2 * float(np.sum(beta[1:] ** 2))
            grad[1:] += l2 * beta[1:]
        return loss, grad

    result = minimize(
        lambda b: objective(b)[0],
        np.zeros(design.shape[1]),
        jac=lambda b: objective(b)[1],
        method="L-BFGS-B",
        options={"maxiter": 1000, "ftol": 1e-12},
    )
    return LogisticModel(name, list(features), mean, scale, result.x, bool(result.success))


def weighted_auc(y: np.ndarray, p: np.ndarray, w: np.ndarray) -> float:
    order = np.argsort(p, kind="mergesort")
    y, p, w = y[order], p[order], w[order]
    total_pos = float(w[y == 1].sum())
    total_neg = float(w[y == 0].sum())
    if total_pos == 0 or total_neg == 0:
        return math.nan
    starts = np.r_[0, np.flatnonzero(np.diff(p) != 0) + 1]
    tie_pos = np.add.reduceat(w * (y == 1), starts)
    tie_neg = np.add.reduceat(w * (y == 0), starts)
    cumulative_neg_before = np.cumsum(tie_neg) - tie_neg
    numerator = float(np.sum(tie_pos * (cumulative_neg_before + 0.5 * tie_neg)))
    return numerator / (total_pos * total_neg)


def score_predictions(rows: list[dict], pred: np.ndarray) -> dict[str, float]:
    y = np.asarray([r["target"] for r in rows], dtype=float)
    w = np.asarray([r["weight"] for r in rows], dtype=float)
    p = np.clip(np.asarray(pred, dtype=float), 1e-9, 1 - 1e-9)
    return {
        "auc": float(weighted_auc(y, p, w)),
        "logloss": float(-np.sum(w * (y * np.log(p) + (1 - y) * np.log(1 - p))) / w.sum()),
        "brier": float(np.sum(w * (p - y) ** 2) / w.sum()),
        "n_windows": int(len(rows)),
        "n_events": int(len({r["row"] for r in rows})),
    }


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    return float(values[np.searchsorted(np.cumsum(weights), 0.5 * weights.sum())])


def bootstrap_delta(
    rows: list[dict], pred_g: np.ndarray, pred_a: np.ndarray, n_boot: int = 500
) -> np.ndarray:
    """Cluster bootstrap using pre-aggregated per-event loss differences."""
    rng = np.random.default_rng(SEED)
    y = np.asarray([r["target"] for r in rows], dtype=float)
    w = np.asarray([r["weight"] for r in rows], dtype=float)
    pg = np.clip(np.asarray(pred_g, dtype=float), 1e-9, 1 - 1e-9)
    pa = np.clip(np.asarray(pred_a, dtype=float), 1e-9, 1 - 1e-9)
    loss_g = -(y * np.log(pg) + (1 - y) * np.log(1 - pg))
    loss_a = -(y * np.log(pa) + (1 - y) * np.log(1 - pa))
    event_ids = np.asarray([r["row"] for r in rows], dtype=int)
    per_event = []
    for event in np.unique(event_ids):
        mask = event_ids == event
        per_event.append(float(np.sum(w[mask] * (loss_g[mask] - loss_a[mask])) / np.sum(w[mask])))
    per_event = np.asarray(per_event, dtype=float)
    deltas = np.empty(n_boot, dtype=float)
    for _ in range(n_boot):
        deltas[_] = float(np.mean(rng.choice(per_event, size=len(per_event), replace=True)))
    return deltas


def paired_lead_values(rows: list[dict], near: float = 256, far: float = 1024) -> np.ndarray:
    grouped: dict[int, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["row"], []).append(row)
    diffs = []
    for group in grouped.values():
        n = min(group, key=lambda r: abs(r["lead_ns"] - near))
        f = min(group, key=lambda r: abs(r["lead_ns"] - far))
        if abs(n["lead_ns"] - near) <= 32 and abs(f["lead_ns"] - far) <= 32:
            diffs.append(n["x_radial"] - f["x_radial"])
    return np.asarray(diffs, dtype=float)


def median_bootstrap_ci(values: np.ndarray, n_boot: int = 1000) -> tuple[float, float]:
    if len(values) == 0:
        return math.nan, math.nan
    rng = np.random.default_rng(SEED + 1)
    stats = [np.median(rng.choice(values, len(values), replace=True)) for _ in range(n_boot)]
    return float(np.quantile(stats, 0.025)), float(np.quantile(stats, 0.975))


def lead_profile(rows: list[dict]) -> list[dict]:
    leads = [128, 256, 512, 1024]
    grouped: dict[int, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["row"], []).append(row)
    output = []
    for lead in leads:
        chosen = []
        for group in grouped.values():
            item = min(group, key=lambda r: abs(r["lead_ns"] - lead))
            if abs(item["lead_ns"] - lead) <= 32:
                chosen.append(item)
        for axis in ("x_radial", "x_history"):
            values = np.asarray([r[axis] for r in chosen], dtype=float)
            output.append(
                {
                    "lead_ns": lead,
                    "axis": axis,
                    "n": int(len(values)),
                    "median": float(np.median(values)) if len(values) else math.nan,
                    "q25": float(np.quantile(values, 0.25)) if len(values) else math.nan,
                    "q75": float(np.quantile(values, 0.75)) if len(values) else math.nan,
                }
            )
    return output


def quadrant_counts(rows: list[dict]) -> list[dict]:
    labels = {(1, 1): "Ab", (1, -1): "aB", (-1, 1): "Ba", (-1, -1): "bA"}
    output = []
    for target, target_name in ((1, "imminent"), (0, "open")):
        selected = [r for r in rows if r["target"] == target]
        total = len(selected)
        counts = {name: 0 for name in labels.values()}
        ridge = 0
        for r in selected:
            sx = 1 if r["x_radial"] > 1 else -1 if r["x_radial"] < 1 else 0
            sy = 1 if r["x_history"] > 1 else -1 if r["x_history"] < 1 else 0
            if sx == 0 or sy == 0:
                ridge += 1
            else:
                counts[labels[(sx, sy)]] += 1
        for name, count in counts.items():
            output.append(
                {
                    "target": target_name,
                    "quadrant": name,
                    "count": count,
                    "share": count / total if total else math.nan,
                }
            )
        output.append(
            {
                "target": target_name,
                "quadrant": "ridge",
                "count": ridge,
                "share": ridge / total if total else math.nan,
            }
        )
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def model_metric_rows(metrics: dict[str, dict[str, dict]]) -> list[dict]:
    rows = []
    for split, models in metrics.items():
        for model, values in models.items():
            rows.append({"split": split, "model": model, **values})
    return rows


def select_example(events: list[Event]) -> Event:
    eligible = [e for e in events if e.split == "evaluation" and e.eligible]
    delays = np.asarray([e.delay_ns for e in eligible], dtype=float)
    median = float(np.median(delays))
    return min(eligible, key=lambda e: abs(e.delay_ns - median))


def make_figure(
    events: list[Event],
    rows_by_split: dict[str, list[dict]],
    metrics: dict[str, dict[str, dict]],
    profiles: list[dict],
    bootstrap: np.ndarray,
    controls: dict[str, float],
    path: Path,
) -> None:
    blue = "#3F6FAE"
    orange = "#D89432"
    charcoal = "#202833"
    grey = "#98A2AE"
    light_blue = "#BFD0E7"
    light_orange = "#F1D6AD"
    fig, axes = plt.subplots(3, 2, figsize=(16, 15), constrained_layout=True)
    fig.patch.set_facecolor("#FAFBFC")
    for ax in axes.ravel():
        ax.set_facecolor("#FFFFFF")
        ax.grid(True, color="#E5E9EF", linewidth=0.8)
        ax.tick_params(colors=charcoal)
        for spine in ax.spines.values():
            spine.set_color("#B7C0CA")

    example = select_example(events)
    ax = axes[0, 0]
    t = (np.arange(len(example.values)) - example.first_index) * DT_NS / 1000.0
    y = example.values - example.causal_baseline
    lo = max(0, example.first_index - 25)
    hi = min(len(y), example.second_index + 30)
    ax.plot(t[lo:hi], y[lo:hi], color=blue, linewidth=1.2, label="baseline-subtracted waveform")
    ax.axvline(0, color=charcoal, linestyle="--", label="first pulse")
    second_us = example.delay_ns / 1000.0
    ax.axvline(second_us, color=orange, linestyle="-", label="second-pulse minimum")
    ax.axvspan(second_us - 0.128, second_us, color=light_orange, alpha=0.55, label="excluded 128 ns guard")
    ax.set_title("Representative eligible double-pulse waveform", loc="left", fontweight="bold")
    ax.set_xlabel("Time since first-pulse minimum (µs)")
    ax.set_ylabel("Baseline-subtracted voltage (mV)")
    ax.legend(frameon=False, fontsize=8, ncol=2)

    ax = axes[0, 1]
    for axis_name, color, label in (
        ("x_radial", blue, "radial activity x_R"),
        ("x_history", orange, "open/recurrent path x_H"),
    ):
        items = sorted([r for r in profiles if r["axis"] == axis_name], key=lambda r: r["lead_ns"], reverse=True)
        x = np.asarray([r["lead_ns"] for r in items])
        med = np.asarray([r["median"] for r in items])
        q25 = np.asarray([r["q25"] for r in items])
        q75 = np.asarray([r["q75"] for r in items])
        ax.plot(x, med, marker="o", color=color, linewidth=2, label=label)
        ax.fill_between(x, q25, q75, color=color, alpha=0.18)
    ax.axhline(1, color=charcoal, linewidth=1.4, label="ARA ridge 1.0")
    ax.axhline(1.25, color=grey, linestyle="--", linewidth=1.2, label="secondary 1.25")
    ax.set_xlim(1070, 90)
    ax.set_ylim(0, 2)
    ax.set_title("Causal ARA coordinates before release", loc="left", fontweight="bold")
    ax.set_xlabel("Lead before second-pulse minimum (ns)")
    ax.set_ylabel("Native ARA coordinate (0–2)")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    eval_rows = rows_by_split["evaluation"]
    imminent = [r for r in eval_rows if r["target"] == 1]
    open_rows = [r for r in eval_rows if r["target"] == 0]
    rng = np.random.default_rng(SEED)
    for group, color, marker, label, size in (
        (open_rows, orange, "o", "open windows (lead ≥640 ns)", 1000),
        (imminent, blue, "^", "imminent windows (lead 128–384 ns)", 1000),
    ):
        if len(group) > size:
            group = [group[i] for i in rng.choice(len(group), size=size, replace=False)]
        ax.scatter(
            [r["x_radial"] for r in group],
            [r["x_history"] for r in group],
            s=13,
            alpha=0.35,
            c=color,
            marker=marker,
            label=label,
            edgecolors="none",
        )
    ax.axvline(1, color=charcoal, linewidth=1)
    ax.axhline(1, color=charcoal, linewidth=1)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_title("Internal-evaluation Irrationality Di-ARA", loc="left", fontweight="bold")
    ax.set_xlabel("Radial activity x_R (0 contraction – 2 expansion)")
    ax.set_ylabel("Path history x_H (0 recurrent – 2 open)")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    models = ["MT", "MG", "MA"]
    x = np.arange(len(models))
    width = 0.34
    for j, split in enumerate(("validation", "evaluation")):
        vals = [metrics[split][m]["auc"] for m in models]
        ax.bar(x + (j - 0.5) * width, vals, width, color=blue if split == "evaluation" else light_blue, edgecolor=charcoal, label=split)
        for xx, val in zip(x + (j - 0.5) * width, vals):
            ax.text(xx, val + 0.008, f"{val:.3f}", ha="center", va="bottom", fontsize=8)
    ax.axhline(0.5, color=charcoal, linestyle="--", linewidth=1)
    ax.set_ylim(0.45, 1.02)
    ax.set_xticks(x, models)
    ax.set_title("Imminent-release discrimination", loc="left", fontweight="bold")
    ax.set_xlabel("Frozen model")
    ax.set_ylabel("Weighted AUROC (0.5 = chance)")
    ax.legend(frameon=False)

    ax = axes[2, 0]
    splits = ["validation", "evaluation"]
    delta_ll = [metrics[s]["MG"]["logloss"] - metrics[s]["MA"]["logloss"] for s in splits]
    delta_br = [metrics[s]["MG"]["brier"] - metrics[s]["MA"]["brier"] for s in splits]
    x = np.arange(2)
    ax.bar(x - 0.18, delta_ll, 0.36, color=blue, edgecolor=charcoal, label="log-loss improvement")
    ax.bar(x + 0.18, delta_br, 0.36, color=orange, edgecolor=charcoal, label="Brier improvement")
    ax.axhline(0, color=charcoal, linewidth=1)
    for xx, val in zip(x - 0.18, delta_ll):
        ax.text(xx, val, f"{val:+.4f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=8)
    for xx, val in zip(x + 0.18, delta_br):
        ax.text(xx, val, f"{val:+.4f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=8)
    ci = np.quantile(bootstrap, [0.025, 0.5, 0.975])
    ax.text(0.02, 0.97, f"Evaluation Δlog-loss bootstrap\nmedian {ci[1]:+.5f}, 95% CI [{ci[0]:+.5f}, {ci[2]:+.5f}]", transform=ax.transAxes, va="top", fontsize=9, color=charcoal)
    ax.set_xticks(x, splits)
    ax.set_title("ARA increment over raw detector baseline", loc="left", fontweight="bold")
    ax.set_xlabel("Chronological split")
    ax.set_ylabel("MG metric − MA metric (positive favours ARA)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")

    ax = axes[2, 1]
    names = ["primary MA", "time reversal", "ARA mirror", "label permutation", "forbidden leakage"]
    vals = [controls[n] for n in names]
    colors = [blue, grey, grey, grey, orange]
    bars = ax.barh(np.arange(len(names)), vals, color=colors, edgecolor=charcoal)
    ax.axvline(0.5, color=charcoal, linestyle="--", linewidth=1)
    ax.set_xlim(0.4, 1.0)
    ax.set_yticks(np.arange(len(names)), names)
    ax.invert_yaxis()
    ax.set_title("Frozen controls and acquisition leakage", loc="left", fontweight="bold")
    ax.set_xlabel("Internal-evaluation weighted AUROC")
    for bar, val in zip(bars, vals):
        ax.text(val + 0.008, bar.get_y() + bar.get_height() / 2, f"{val:.3f}", va="center", fontsize=8)

    fig.suptitle(
        "T385 — BUAP causal Irrationality Di-ARA pre-release test\n"
        "Class-D liquid-scintillator detector proxy · 8 ns samples · 128 ns visible-pulse guard",
        fontsize=18,
        fontweight="bold",
        color=charcoal,
    )
    fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def make_report(results: dict, path: Path) -> None:
    status = results["decision"]["status"]
    gates = results["decision"]["gates"]
    metric_rows = model_metric_rows(results["metrics"])
    status_color = "#2D6A4F" if status == "SUPPORTED" else "#A33D32"
    rows_html = "".join(
        "<tr>"
        f"<td>{html.escape(r['split'])}</td><td>{html.escape(r['model'])}</td>"
        f"<td>{r['auc']:.4f}</td><td>{r['logloss']:.5f}</td><td>{r['brier']:.5f}</td>"
        f"<td>{r['n_events']}</td><td>{r['n_windows']}</td></tr>"
        for r in metric_rows
    )
    gate_html = "".join(
        f"<li class={'pass' if value else 'fail'}>{'PASS' if value else 'FAIL'} — {html.escape(name.replace('_', ' '))}</li>"
        for name, value in gates.items()
    )
    exclusion_rows = "".join(
        f"<tr><td>{html.escape(r['split'])}</td><td>{html.escape(r['reason'])}</td><td>{r['count']}</td></tr>"
        for r in results["eligibility"]
    )
    body = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>T385 BUAP causal Irrationality Di-ARA</title>
<style>
body{{font-family:Arial,sans-serif;background:#f4f6f8;color:#202833;margin:0}}main{{max-width:1220px;margin:auto;padding:28px}}
.card{{background:white;border:1px solid #d9dee5;border-radius:14px;padding:22px;margin:18px 0;box-shadow:0 2px 8px #0000000d}}
h1,h2{{margin-top:0}}.status{{color:{status_color};font-weight:800}}img{{width:100%;height:auto;border:1px solid #d9dee5}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}th,td{{padding:8px;border-bottom:1px solid #e5e9ef;text-align:right}}th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){{text-align:left}}
.pass{{color:#2D6A4F}}.fail{{color:#A33D32}}code{{background:#eef1f4;padding:2px 5px;border-radius:4px}}
</style></head><body><main>
<div class="card"><h1>T385 — BUAP causal Irrationality Di-ARA pre-release test</h1>
<p class="status">{status}</p>
<p><b>Question:</b> Does causal inter-pulse detector geometry predict the later decay-electron handover outside a 128 ns visible-pulse guard?</p>
<p><b>Claim ceiling:</b> Class-D detector proxy conditional on a recorded double pulse. Neutrinos were not observed and the cohort excludes unrecorded daughters.</p>
<p><b>Frozen orientation:</b> movement/release is <code>0 → 2</code>. The <code>1.25</code> liquid landmark is descriptive only.</p></div>
<div class="card"><img src="T385_BUAP_CAUSAL_IRRATIONALITY_DI_ARA_FIGURE.png" alt="T385 six-panel result figure"></div>
<div class="card"><h2>Decision gates</h2><ul>{gate_html}</ul></div>
<div class="card"><h2>Model scores</h2><table><thead><tr><th>Split</th><th>Model</th><th>AUROC</th><th>Log loss</th><th>Brier</th><th>Events</th><th>Windows</th></tr></thead><tbody>{rows_html}</tbody></table></div>
<div class="card"><h2>Eligibility ledger</h2><table><thead><tr><th>Split</th><th>Reason</th><th>Count</th></tr></thead><tbody>{exclusion_rows}</tbody></table></div>
<div class="card"><h2>Interpretation boundary</h2><p>{html.escape(results['decision']['interpretation'])}</p>
<p>Source: <a href="https://ciiec.buap.mx/Muon-Decay">BUAP Real Time Muon Lifetime Experiment</a>. Development file hash: <code>{results['source']['sha256']}</code>.</p></div>
</main></body></html>"""
    path.write_text(body, encoding="utf-8")


def run(write_outputs: bool = True) -> dict:
    if not RAW.exists():
        raise FileNotFoundError(RAW)
    raw_hash = sha256(RAW)
    protocol_hash = sha256(PROTOCOL)
    if raw_hash != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"Raw hash mismatch: {raw_hash}")
    if protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"Protocol hash mismatch: {protocol_hash}")

    events = load_events()
    all_normal: dict[str, list[dict]] = {name: [] for _, _, name in SPLITS}
    all_reverse: dict[str, list[dict]] = {name: [] for _, _, name in SPLITS}
    for event in events:
        all_normal[event.split].extend(event_windows(event, reverse=False))
        all_reverse[event.split].extend(event_windows(event, reverse=True))
    for split in all_normal:
        balance_weights(all_normal[split])
        balance_weights(all_reverse[split])
    normal = {split: model_rows(rows) for split, rows in all_normal.items()}
    reverse = {split: model_rows(rows) for split, rows in all_reverse.items()}

    train = normal["calibration"]
    models = {name: fit_logistic(name, train) for name in FEATURES}
    metrics: dict[str, dict[str, dict]] = {}
    predictions: dict[str, dict[str, np.ndarray]] = {}
    for split in ("calibration", "validation", "evaluation"):
        metrics[split] = {}
        predictions[split] = {}
        for name, model in models.items():
            pred = model.predict(normal[split])
            predictions[split][name] = pred
            metrics[split][name] = score_predictions(normal[split], pred)

    evaluation = normal["evaluation"]
    pred_g = predictions["evaluation"]["MG"]
    pred_a = predictions["evaluation"]["MA"]
    boot = bootstrap_delta(evaluation, pred_g, pred_a)

    reverse_pred = models["MA"].predict(reverse["evaluation"])
    reverse_auc = score_predictions(reverse["evaluation"], reverse_pred)["auc"]

    mirrored = [dict(r) for r in evaluation]
    for row in mirrored:
        row["x_radial"] = 2.0 - row["x_radial"]
        row["dx_radial"] = -row["dx_radial"]
        row["ridge_product"] = (row["x_radial"] - 1.0) * (row["x_history"] - 1.0)
    mirror_auc = score_predictions(mirrored, models["MA"].predict(mirrored))["auc"]

    rng = np.random.default_rng(SEED)
    perm_aucs = []
    y_original = np.asarray([r["target"] for r in evaluation], dtype=int)
    elapsed = np.asarray([r["elapsed_us"] for r in evaluation], dtype=float)
    bins = np.quantile(elapsed, np.linspace(0, 1, 11))
    for _ in range(200):
        y = y_original.copy()
        for k in range(10):
            if k == 9:
                idx = np.where((elapsed >= bins[k]) & (elapsed <= bins[k + 1]))[0]
            else:
                idx = np.where((elapsed >= bins[k]) & (elapsed < bins[k + 1]))[0]
            y[idx] = rng.permutation(y[idx])
        perm_rows = [dict(r, target=int(target)) for r, target in zip(evaluation, y)]
        perm_aucs.append(score_predictions(perm_rows, pred_a)["auc"])
    permutation_auc = float(np.median(perm_aucs))

    controls = {
        "primary MA": metrics["evaluation"]["MA"]["auc"],
        "time reversal": float(reverse_auc),
        "ARA mirror": float(mirror_auc),
        "label permutation": permutation_auc,
        "forbidden leakage": metrics["evaluation"]["MLEAK"]["auc"],
    }

    eval_weights = np.asarray([r["weight"] for r in evaluation], dtype=float)
    eval_xr = np.asarray([r["x_radial"] for r in evaluation], dtype=float)
    eval_y = np.asarray([r["target"] for r in evaluation], dtype=int)
    median_imminent = weighted_median(eval_xr[eval_y == 1], eval_weights[eval_y == 1])
    median_open = weighted_median(eval_xr[eval_y == 0], eval_weights[eval_y == 0])
    diffs = paired_lead_values(all_normal["evaluation"])
    diff_ci = median_bootstrap_ci(diffs)
    median_diff = float(np.median(diffs)) if len(diffs) else math.nan

    val_auc_gain = metrics["validation"]["MA"]["auc"] - metrics["validation"]["MG"]["auc"]
    eval_auc_gain = metrics["evaluation"]["MA"]["auc"] - metrics["evaluation"]["MG"]["auc"]
    val_ll_gain = metrics["validation"]["MG"]["logloss"] - metrics["validation"]["MA"]["logloss"]
    eval_ll_gain = metrics["evaluation"]["MG"]["logloss"] - metrics["evaluation"]["MA"]["logloss"]
    val_br_gain = metrics["validation"]["MG"]["brier"] - metrics["validation"]["MA"]["brier"]
    eval_br_gain = metrics["evaluation"]["MG"]["brier"] - metrics["evaluation"]["MA"]["brier"]
    boot_ci = np.quantile(boot, [0.025, 0.5, 0.975])

    normal_auc = controls["primary MA"]
    control_best = max(reverse_auc, mirror_auc, permutation_auc)
    gates = {
        "movement_side_and_positive_gradient": bool(
            median_imminent > 1.0 and median_diff > 0 and diff_ci[0] > 0
        ),
        "logloss_and_brier_improve_both_splits": bool(
            min(val_ll_gain, eval_ll_gain, val_br_gain, eval_br_gain) > 0
        ),
        "auc_gain_at_least_0p02_both_splits": bool(
            min(val_auc_gain, eval_auc_gain) >= 0.02
        ),
        "evaluation_bootstrap_delta_above_zero": bool(boot_ci[0] > 0),
        "ordered_orientation_beats_controls_by_0p02": bool(normal_auc - control_best >= 0.02),
        "causal_guard_and_acquisition_fields_excluded": True,
    }
    supported = all(gates.values())

    eligibility = []
    for split in ("engineering", "calibration", "validation", "evaluation"):
        split_events = [e for e in events if e.split == split]
        for reason in sorted({e.exclusion for e in split_events}):
            eligibility.append(
                {
                    "split": split,
                    "reason": reason,
                    "count": sum(e.exclusion == reason for e in split_events),
                }
            )

    profiles = lead_profile(all_normal["evaluation"])
    quadrants = quadrant_counts(evaluation)
    secondary = {
        "weighted_median_x_radial_imminent": median_imminent,
        "weighted_median_x_radial_open": median_open,
        "distance_of_imminent_median_from_1p25": median_imminent - 1.25,
        "paired_256_minus_1024_median": median_diff,
        "paired_difference_95ci": list(diff_ci),
        "paired_event_count": int(len(diffs)),
    }
    interpretation = (
        "All frozen gates passed for advance detector-proxy information outside the visible-pulse guard. "
        "This warrants same-medium external replication but does not identify a neutrino or internal muon child."
        if supported
        else
        "The frozen detector-proxy test did not pass every advance-prediction gate. Any movement-side or 1.25 proximity is descriptive unless it also improves held-out prediction beyond raw detector covariates and survives the controls."
    )
    results = {
        "test": "T385",
        "source": {
            "url": "https://ciiec.buap.mx/Muon-Decay/Datos/MD10000Last.csv",
            "local_path": str(RAW),
            "sha256": raw_hash,
            "protocol_sha256": protocol_hash,
            "rows": len(events),
            "sampling_interval_ns": DT_NS,
            "medium": "95 L liquid scintillator",
            "capability": "Class D detector proxy; selected double-pulse cohort",
        },
        "eligibility": eligibility,
        "metrics": metrics,
        "controls": controls,
        "bootstrap_logloss_delta": {
            "n": len(boot),
            "q025": float(boot_ci[0]),
            "median": float(boot_ci[1]),
            "q975": float(boot_ci[2]),
        },
        "secondary_landmarks": secondary,
        "lead_profile": profiles,
        "quadrants": quadrants,
        "decision": {
            "status": "SUPPORTED" if supported else "NOT SUPPORTED",
            "gates": gates,
            "interpretation": interpretation,
        },
    }

    if write_outputs:
        OUT.mkdir(exist_ok=True)
        (OUT / "T385_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        write_csv(OUT / "T385_MODEL_SCORES.csv", model_metric_rows(metrics))
        write_csv(OUT / "T385_LEAD_PROFILE.csv", profiles)
        write_csv(OUT / "T385_QUADRANT_OCCUPANCY.csv", quadrants)
        write_csv(OUT / "T385_ELIGIBILITY.csv", eligibility)
        write_csv(
            OUT / "T385_BOOTSTRAP_LOGLOSS_DELTA.csv",
            [{"replicate": i, "delta_logloss": float(v)} for i, v in enumerate(boot)],
        )
        figure = OUT / "T385_BUAP_CAUSAL_IRRATIONALITY_DI_ARA_FIGURE.png"
        make_figure(events, normal, metrics, profiles, boot, controls, figure)
        make_report(results, OUT / "T385_BUAP_CAUSAL_IRRATIONALITY_DI_ARA_REPORT.html")
    return results


if __name__ == "__main__":
    result = run(write_outputs=True)
    print(json.dumps({"status": result["decision"]["status"], "gates": result["decision"]["gates"], "controls": result["controls"], "secondary": result["secondary_landmarks"]}, indent=2))
