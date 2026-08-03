#!/usr/bin/env python3
"""T307: frozen complex-quadrant test in the muon-Fusion overlap model."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

import t305_phi_temporal_carrier_fusion as t305


HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_RESULTS.json"
OUT_SERIES = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_SERIES.csv"
OUT_STEPS = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_STEPS.csv"
OUT_PREDICTION = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_PREDICTION.csv"
OUT_RADIAL = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_RADIAL.csv"
OUT_FIG = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
E_INV = 1.0 / math.e
PHI_TIME = PHI - 1.0
ANTI_PHI = PHI ** -2
SQRT2M1 = math.sqrt(2.0) - 1.0
PI_M3 = math.pi - 3.0

PREFIXES = np.arange(257, 1025, dtype=int)
TRAIN_MAX = 640
HOLDOUT_MIN = 641
WIDTH = 0.15 / 1024.0
PHASES = np.linspace(0.0, 2.0 * math.pi, 128, endpoint=False)
FAMILIES = ["beam7", "beam7_cycle23", "beam7_decay"]
SHUFFLES = 1000
SHUFFLE_SEED = 3072026
BROKEN_SHIFTS = [17, 31, 47]
RADIAL_LAGS = [1, 2, 4, 8, 16, 32, 64]

ALPHAS = {
    "phi_time": PHI_TIME,
    "anti_phi": ANTI_PHI,
    "one_over_e": E_INV,
    "sqrt2_minus_1": SQRT2M1,
    "pi_minus_3": PI_M3,
}

PAIRS = {
    "parent_phi_time_vs_e": ("phi_time", "one_over_e"),
    "child_anti_phi_vs_e": ("anti_phi", "one_over_e"),
    "control_phi_time_vs_sqrt2": ("phi_time", "sqrt2_minus_1"),
    "control_e_vs_sqrt2": ("one_over_e", "sqrt2_minus_1"),
    "control_phi_time_vs_pi3": ("phi_time", "pi_minus_3"),
    "control_e_vs_pi3": ("one_over_e", "pi_minus_3"),
    "control_sqrt2_vs_pi3": ("sqrt2_minus_1", "pi_minus_3"),
}

PRIMARY = "parent_phi_time_vs_e"
STATE_NAMES = [
    "contracting_reverse",
    "contracting_forward",
    "expanding_reverse",
    "expanding_forward",
]


def exp_integral(intervals: list[tuple[float, float]], z: complex) -> complex:
    return sum((np.exp(z * hi) - np.exp(z * lo)) / z for lo, hi in intervals)


def harmonic_integral(
    intervals: list[tuple[float, float]], frequency: float
) -> complex:
    return exp_integral(intervals, complex(0.0, 2.0 * math.pi * frequency))


def arrival_overlap_fast(
    intervals: list[tuple[float, float]], family: str
) -> np.ndarray:
    """Algebraically equivalent vectorized form of T305's overlap function."""
    length = t305.union_length(intervals)
    if family == "beam7":
        h7 = harmonic_integral(intervals, 7.0)
        values = length + 0.85 * np.real(np.exp(1j * PHASES) * h7)
        return np.clip(values, 0.0, 1.0)
    if family == "beam7_cycle23":
        d = 0.6
        values = (
            length
            + d * np.real(np.exp(1j * PHASES) * harmonic_integral(intervals, 7.0))
            + d
            * np.real(
                np.exp(1.7j * PHASES) * harmonic_integral(intervals, 23.0)
            )
            + 0.5
            * d
            * d
            * np.real(
                np.exp(-0.7j * PHASES) * harmonic_integral(intervals, 16.0)
            )
            + 0.5
            * d
            * d
            * np.real(
                np.exp(2.7j * PHASES) * harmonic_integral(intervals, 30.0)
            )
        )
        return np.clip(values, 0.0, 1.0)
    if family == "beam7_decay":
        tau = 0.45
        d = 0.85
        z0 = complex(-1.0 / tau, 0.0)
        z1 = complex(-1.0 / tau, 2.0 * math.pi * 7.0)
        base = float(np.real(exp_integral(intervals, z0)))
        harmonic = exp_integral(intervals, z1)
        numerator = base + d * np.real(np.exp(1j * PHASES) * harmonic)
        full = [(0.0, 1.0)]
        norm_base = float(np.real(exp_integral(full, z0)))
        norm_harmonic = exp_integral(full, z1)
        denominator = norm_base + d * np.real(
            np.exp(1j * PHASES) * norm_harmonic
        )
        return np.clip(numerator / denominator, 0.0, 1.0)
    raise KeyError(family)


def generate_raw() -> tuple[dict[tuple[str, int, str], np.ndarray], dict]:
    raw: dict[tuple[str, int, str], np.ndarray] = {}
    bounds_min = math.inf
    bounds_max = -math.inf
    interval_counts: list[int] = []
    for candidate, alpha in ALPHAS.items():
        for n in PREFIXES:
            centres = t305.carrier_centres(alpha, int(n))
            intervals = t305.merged_intervals(centres, WIDTH)
            interval_counts.append(len(intervals))
            for family in FAMILIES:
                values = arrival_overlap_fast(intervals, family)
                raw[(candidate, int(n), family)] = values
                bounds_min = min(bounds_min, float(np.min(values)))
                bounds_max = max(bounds_max, float(np.max(values)))
    return raw, {
        "min_overlap": bounds_min,
        "max_overlap": bounds_max,
        "min_merged_intervals": int(min(interval_counts)),
        "max_merged_intervals": int(max(interval_counts)),
    }


def complex_state(left: np.ndarray, right: np.ndarray) -> complex:
    contrast = left - right
    return complex(2.0 * np.mean(contrast * np.exp(-1j * PHASES)))


def pair_series(
    raw: dict[tuple[str, int, str], np.ndarray],
    pair_name: str,
    family: str,
    right_shift: int = 0,
) -> np.ndarray:
    left_name, right_name = PAIRS[pair_name]
    left = [raw[(left_name, int(n), family)] for n in PREFIXES]
    right = [raw[(right_name, int(n), family)] for n in PREFIXES]
    if right_shift:
        split = int(np.searchsorted(PREFIXES, HOLDOUT_MIN))
        right_train = np.roll(np.asarray(right[:split]), right_shift, axis=0)
        right_hold = np.roll(np.asarray(right[split:]), right_shift, axis=0)
        right = list(right_train) + list(right_hold)
    return np.asarray(
        [complex_state(l, r) for l, r in zip(left, right)], dtype=complex
    )


def quadrant(log_s: float, delta: float, eps: float = 1e-12) -> str:
    if abs(log_s) <= eps or abs(delta) <= eps:
        return "boundary"
    radial = "expanding" if log_s > 0.0 else "contracting"
    direction = "forward" if delta > 0.0 else "reverse"
    return f"{radial}_{direction}"


def step_records(pair: str, family: str, z: np.ndarray) -> tuple[list[dict], dict]:
    amplitudes = np.abs(z)
    floor = max(1e-12, 1e-6 * float(np.median(amplitudes)))
    rows: list[dict] = []
    counts = {name: 0 for name in STATE_NAMES}
    counts["boundary"] = 0
    valid = 0
    for i in range(len(z) - 1):
        amp_valid = bool(amplitudes[i] > floor and amplitudes[i + 1] > floor)
        if amp_valid:
            q = z[i + 1] / z[i]
            log_s = float(math.log(abs(q)))
            delta = float(np.angle(q))
            state = quadrant(log_s, delta)
            valid += 1
            counts[state] += 1
        else:
            q = complex(math.nan, math.nan)
            log_s = math.nan
            delta = math.nan
            state = "invalid"
        rows.append(
            {
                "pair": pair,
                "family": family,
                "n_from": int(PREFIXES[i]),
                "n_to": int(PREFIXES[i + 1]),
                "amplitude_floor": floor,
                "valid": amp_valid,
                "q_real": float(q.real),
                "q_imag": float(q.imag),
                "s": float(abs(q)),
                "log_s": log_s,
                "delta_rad": delta,
                "quadrant": state,
            }
        )
    return rows, {
        "amplitude_floor": floor,
        "valid_steps": valid,
        "total_steps": len(z) - 1,
        "valid_fraction": valid / (len(z) - 1),
        "quadrant_counts": counts,
    }


def component_median(values: np.ndarray) -> complex:
    return complex(float(np.median(values.real)), float(np.median(values.imag)))


def normalized_mae(actual: np.ndarray, predicted: np.ndarray) -> tuple[float, float]:
    absolute = float(np.mean(np.abs(actual - predicted)))
    scale = max(1e-15, float(np.median(np.abs(actual))))
    return absolute, absolute / scale


def predictor_score(z: np.ndarray, shuffle_seed: int) -> dict:
    amp = np.abs(z)
    floor = max(1e-12, 1e-6 * float(np.median(amp)))
    q = np.full(len(z) - 1, np.nan + 1j * np.nan, dtype=complex)
    q_valid = (amp[:-1] > floor) & (amp[1:] > floor)
    q[q_valid] = z[1:][q_valid] / z[:-1][q_valid]
    q_state = np.array(
        [
            quadrant(float(math.log(abs(value))), float(np.angle(value)))
            if ok
            else "invalid"
            for value, ok in zip(q, q_valid)
        ],
        dtype=object,
    )

    # Target q[i] predicts z[i+1]; q[i-1]'s state is the available ARA state.
    target_indices = np.arange(1, len(q))
    valid_prediction = q_valid[1:] & q_valid[:-1]
    train = (
        valid_prediction
        & (PREFIXES[target_indices + 1] <= TRAIN_MAX)
    )
    hold = (
        valid_prediction
        & (PREFIXES[target_indices + 1] >= HOLDOUT_MIN + 1)
    )
    train_idx = target_indices[train]
    hold_idx = target_indices[hold]
    if len(train_idx) < 20 or len(hold_idx) < 20:
        return {"valid": False, "reason": "insufficient valid train/holdout steps"}

    global_q = component_median(q[train_idx])
    medians: dict[str, complex] = {}
    training_state_counts: dict[str, int] = {}
    for state in STATE_NAMES:
        selected = np.array([i for i in train_idx if q_state[i - 1] == state])
        training_state_counts[state] = int(len(selected))
        medians[state] = component_median(q[selected]) if len(selected) else global_q

    actual = z[hold_idx + 1]
    ara_q = np.asarray([medians.get(q_state[i - 1], global_q) for i in hold_idx])
    pred_ara = ara_q * z[hold_idx]
    pred_persistence = z[hold_idx]
    pred_local = q[hold_idx - 1] * z[hold_idx]
    pred_global = global_q * z[hold_idx]

    # Generic affine complex AR(2): z[i+1] = c + a*z[i] + b*z[i-1].
    x_train = np.column_stack(
        [np.ones(len(train_idx)), z[train_idx], z[train_idx - 1]]
    )
    beta = np.linalg.lstsq(x_train, z[train_idx + 1], rcond=None)[0]
    x_hold = np.column_stack(
        [np.ones(len(hold_idx)), z[hold_idx], z[hold_idx - 1]]
    )
    pred_ar2 = x_hold @ beta

    predictions = {
        "ara_quadrant": pred_ara,
        "persistence": pred_persistence,
        "local_ratio": pred_local,
        "global_ratio": pred_global,
        "affine_ar2": pred_ar2,
    }
    errors = {}
    for name, pred in predictions.items():
        absolute, normalized = normalized_mae(actual, pred)
        errors[name] = {"mae": absolute, "normalized_mae": normalized}

    rng = np.random.default_rng(shuffle_seed)
    train_targets = q[train_idx].copy()
    train_prev_states = np.asarray([q_state[i - 1] for i in train_idx])
    shuffle_errors = []
    for _ in range(SHUFFLES):
        shuffled = rng.permutation(train_targets)
        shuffled_medians = {}
        for state in STATE_NAMES:
            values = shuffled[train_prev_states == state]
            shuffled_medians[state] = (
                component_median(values) if len(values) else global_q
            )
        pred_q = np.asarray(
            [shuffled_medians.get(q_state[i - 1], global_q) for i in hold_idx]
        )
        _, shuffled_error = normalized_mae(actual, pred_q * z[hold_idx])
        shuffle_errors.append(shuffled_error)
    shuffle_errors = np.asarray(shuffle_errors)

    # A separate categorical readout; not a frozen pass gate.
    transition_counts = np.zeros((4, 4), dtype=int)
    for i in train_idx:
        previous = q_state[i - 1]
        current = q_state[i]
        if previous in STATE_NAMES and current in STATE_NAMES:
            transition_counts[STATE_NAMES.index(previous), STATE_NAMES.index(current)] += 1
    predicted_states = {}
    for row, state in enumerate(STATE_NAMES):
        predicted_states[state] = STATE_NAMES[int(np.argmax(transition_counts[row]))]
    actual_states = [q_state[i] for i in hold_idx]
    state_predictions = [predicted_states.get(q_state[i - 1], STATE_NAMES[0]) for i in hold_idx]
    state_accuracy = float(np.mean(np.asarray(actual_states) == np.asarray(state_predictions)))
    majority = max(actual_states.count(state) for state in STATE_NAMES) / len(actual_states)
    persistence_accuracy = float(
        np.mean(np.asarray(actual_states) == np.asarray([q_state[i - 1] for i in hold_idx]))
    )

    return {
        "valid": True,
        "amplitude_floor": floor,
        "train_predictions": int(len(train_idx)),
        "holdout_predictions": int(len(hold_idx)),
        "training_state_counts": training_state_counts,
        "state_transition_counts": transition_counts.tolist(),
        "state_prediction_accuracy": state_accuracy,
        "state_majority_accuracy": majority,
        "state_persistence_accuracy": persistence_accuracy,
        "global_q": {"real": global_q.real, "imag": global_q.imag},
        "affine_ar2": [
            {"real": float(value.real), "imag": float(value.imag)} for value in beta
        ],
        "errors": errors,
        "shuffle_error_p05": float(np.percentile(shuffle_errors, 5)),
        "shuffle_error_median": float(np.median(shuffle_errors)),
        "shuffle_error_p95": float(np.percentile(shuffle_errors, 95)),
        "ara_shuffle_percentile": float(
            np.mean(shuffle_errors <= errors["ara_quadrant"]["normalized_mae"])
        ),
    }


def radial_audit(pair: str, family: str, z: np.ndarray) -> list[dict]:
    rows = []
    amp = np.abs(z)
    floor = max(1e-12, 1e-6 * float(np.median(amp)))
    model_targets = {
        "lead_e_phi": (-1.0, math.log(PHI)),
        "reciprocal_e": (-1.0, 1.0),
        "reciprocal_phi": (-math.log(PHI), math.log(PHI)),
    }
    for lag in RADIAL_LAGS:
        valid = (amp[:-lag] > floor) & (amp[lag:] > floor)
        s = amp[lag:][valid] / amp[:-lag][valid]
        logs = np.log(s)
        model_errors = {}
        for name, (contract, expand) in model_targets.items():
            targets = np.where(logs < 0.0, contract, expand)
            model_errors[name] = float(np.median(np.abs(logs - targets)))
        model_errors["unity"] = float(np.median(np.abs(logs)))
        winner = min(model_errors, key=model_errors.get)
        ara_x = 2.0 * (s - E_INV) / (PHI - E_INV)
        rows.append(
            {
                "pair": pair,
                "family": family,
                "lag": lag,
                "valid_ratios": int(len(s)),
                "median_s": float(np.median(s)),
                "median_log_s": float(np.median(logs)),
                "median_ara_x": float(np.median(ara_x)),
                "fraction_inside_e_phi": float(np.mean((s >= E_INV) & (s <= PHI))),
                "lead_e_phi_error": model_errors["lead_e_phi"],
                "reciprocal_e_error": model_errors["reciprocal_e"],
                "reciprocal_phi_error": model_errors["reciprocal_phi"],
                "unity_error": model_errors["unity"],
                "winner": winner,
            }
        )
    return rows


def post_hoc_primary_pooled_radial(series: pd.DataFrame) -> dict:
    """Exploratory only: pooled reciprocal-Phi proximity and order shuffle."""
    arrays = []
    for family in FAMILIES:
        part = series[
            (series["pair"] == PRIMARY) & (series["family"] == family)
        ].sort_values("n")
        arrays.append(part["amplitude"].to_numpy(dtype=float))

    def summarize(values: list[np.ndarray]) -> tuple[float, float, float]:
        contracting: list[float] = []
        expanding: list[float] = []
        for amplitudes in values:
            for lag in RADIAL_LAGS:
                ratios = amplitudes[lag:] / amplitudes[:-lag]
                contracting.extend(ratios[ratios < 1.0])
                expanding.extend(ratios[ratios > 1.0])
        median_contracting = float(np.median(contracting))
        median_expanding = float(np.median(expanding))
        log_distance = abs(math.log(median_contracting) + math.log(PHI)) + abs(
            math.log(median_expanding) - math.log(PHI)
        )
        return median_contracting, median_expanding, log_distance

    observed = summarize(arrays)
    rng = np.random.default_rng(SHUFFLE_SEED)
    shuffle_rows = [summarize([rng.permutation(values) for values in arrays]) for _ in range(SHUFFLES)]
    shuffle = np.asarray(shuffle_rows)
    scores = shuffle[:, 2]
    return {
        "status": "post_hoc_exploratory_does_not_change_frozen_gates",
        "pooled_lags": RADIAL_LAGS,
        "observed_median_contracting": observed[0],
        "observed_median_expanding": observed[1],
        "reciprocal_phi": 1.0 / PHI,
        "phi": PHI,
        "contracting_relative_difference_from_reciprocal_phi": observed[0] / (1.0 / PHI) - 1.0,
        "expanding_relative_difference_from_phi": observed[1] / PHI - 1.0,
        "observed_two_endpoint_log_distance": observed[2],
        "shuffle_log_distance_p05": float(np.percentile(scores, 5)),
        "shuffle_log_distance_median": float(np.median(scores)),
        "shuffle_log_distance_p95": float(np.percentile(scores, 95)),
        "observed_shuffle_percentile": float(np.mean(scores <= observed[2])),
        "shuffle_count": SHUFFLES,
    }


def direct_spot_checks(
    raw: dict[tuple[str, int, str], np.ndarray]
) -> dict:
    checks = [
        ("phi_time", 257, "beam7"),
        ("one_over_e", 641, "beam7_cycle23"),
        ("sqrt2_minus_1", 1024, "beam7_decay"),
    ]
    rows = []
    for candidate, n, family in checks:
        intervals = t305.merged_intervals(
            t305.carrier_centres(ALPHAS[candidate], n), WIDTH
        )
        direct = t305.arrival_overlap(intervals, family, PHASES)
        observed = raw[(candidate, n, family)]
        rows.append(
            {
                "candidate": candidate,
                "n": n,
                "family": family,
                "max_abs_error": float(np.max(np.abs(direct - observed))),
            }
        )
    return {
        "checks": rows,
        "max_abs_error": max(row["max_abs_error"] for row in rows),
    }


def make_figure(
    series: pd.DataFrame,
    steps: pd.DataFrame,
    prediction: pd.DataFrame,
    radial: pd.DataFrame,
) -> None:
    width, height = 2400, 1700
    image = Image.new("RGB", (width, height), "#f7f8fa")
    draw = ImageDraw.Draw(image)

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        names = ["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]
        for name in names:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                pass
        return ImageFont.load_default()

    title_font = font(38, True)
    panel_font = font(25, True)
    label_font = font(18)
    small_font = font(15)
    palette = {
        "beam7": "#3568a8",
        "beam7_cycle23": "#d79b2e",
        "beam7_decay": "#7f8f42",
    }
    ink = "#222831"
    grid = "#d8dde3"
    draw.text(
        (80, 42),
        "T307 — complex irrationality quadrant in the muon-Fusion overlap model",
        fill=ink,
        font=title_font,
    )
    draw.text(
        (82, 92),
        "Fresh prefixes 257–1024 · 128 source phases · idealised scheduling model",
        fill="#66717d",
        font=label_font,
    )

    panels = [
        (70, 150, 1160, 800),
        (1240, 150, 2330, 800),
        (70, 880, 1160, 1590),
        (1240, 880, 2330, 1590),
    ]

    def panel(box: tuple[int, int, int, int], title: str) -> tuple[int, int, int, int]:
        x0, y0, x1, y1 = box
        draw.rounded_rectangle(box, radius=16, fill="white", outline="#c9cfd6", width=2)
        draw.text((x0 + 26, y0 + 20), title, fill=ink, font=panel_font)
        plot = (x0 + 105, y0 + 82, x1 - 30, y1 - 78)
        px0, py0, px1, py1 = plot
        draw.line((px0, py1, px1, py1), fill=ink, width=2)
        draw.line((px0, py0, px0, py1), fill=ink, width=2)
        return plot

    def bounds(values: np.ndarray, pad: float = 0.05) -> tuple[float, float]:
        lo, hi = float(np.nanmin(values)), float(np.nanmax(values))
        if not math.isfinite(lo) or not math.isfinite(hi):
            return -1.0, 1.0
        if abs(hi - lo) < 1e-15:
            return lo - 1.0, hi + 1.0
        margin = pad * (hi - lo)
        return lo - margin, hi + margin

    def mapper(plot, xlim, ylim):
        x0, y0, x1, y1 = plot
        def point(x, y):
            px = x0 + (float(x) - xlim[0]) / (xlim[1] - xlim[0]) * (x1 - x0)
            py = y1 - (float(y) - ylim[0]) / (ylim[1] - ylim[0]) * (y1 - y0)
            return int(px), int(py)
        return point

    # Panel 1: complex trajectory.
    plot = panel(panels[0], "Primary joint handover trajectory")
    primary = series[series["pair"] == PRIMARY]
    xlim = bounds(primary["u"].to_numpy())
    ylim = bounds(primary["v"].to_numpy())
    point = mapper(plot, xlim, ylim)
    if xlim[0] <= 0 <= xlim[1]:
        draw.line((*point(0, ylim[0]), *point(0, ylim[1])), fill=grid, width=2)
    if ylim[0] <= 0 <= ylim[1]:
        draw.line((*point(xlim[0], 0), *point(xlim[1], 0)), fill=grid, width=2)
    for family in FAMILIES:
        part = primary[primary["family"] == family]
        pts = [point(x, y) for x, y in zip(part["u"], part["v"])]
        if len(pts) > 1:
            draw.line(pts, fill=palette[family], width=3)
        sx, sy = pts[0]
        ex, ey = pts[-1]
        draw.ellipse((sx - 7, sy - 7, sx + 7, sy + 7), outline=palette[family], width=3)
        draw.ellipse((ex - 6, ey - 6, ex + 6, ey + 6), fill=palette[family])
    draw.text((panels[0][0] + 390, panels[0][3] - 50), "cosine cut u", fill=ink, font=label_font)
    draw.text((panels[0][0] + 18, panels[0][1] + 350), "sine cut v", fill=ink, font=label_font)

    # Panel 2: q quadrants, robustly cropped only for drawing (CSV is unclamped).
    plot = panel(panels[1], "Adjacent-step complex ARA quadrants")
    primary_steps = steps[(steps["pair"] == PRIMARY) & steps["valid"]]
    xv = primary_steps["log_s"].to_numpy()
    yv = primary_steps["delta_rad"].to_numpy()
    xlim = (float(np.percentile(xv, 0.5)), float(np.percentile(xv, 99.5)))
    ylim = (-math.pi, math.pi)
    point = mapper(plot, xlim, ylim)
    if xlim[0] <= 0 <= xlim[1]:
        draw.line((*point(0, ylim[0]), *point(0, ylim[1])), fill=ink, width=2)
    draw.line((*point(xlim[0], 0), *point(xlim[1], 0)), fill=ink, width=2)
    for reference, color in [(-1.0, "#777777"), (math.log(PHI), "#aa6e00")]:
        if xlim[0] <= reference <= xlim[1]:
            p0, p1 = point(reference, ylim[0]), point(reference, ylim[1])
            for yy in range(p1[1], p0[1], 14):
                draw.line((p0[0], yy, p0[0], min(yy + 7, p0[1])), fill=color, width=2)
    for family in FAMILIES:
        part = primary_steps[primary_steps["family"] == family]
        for x, y in zip(part["log_s"], part["delta_rad"]):
            if xlim[0] <= x <= xlim[1]:
                px, py = point(x, y)
                draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=palette[family])
    draw.text((panels[1][0] + 400, panels[1][3] - 50), "radial change log(s)", fill=ink, font=label_font)
    draw.text((panels[1][0] + 12, panels[1][1] + 340), "signed phase", fill=ink, font=label_font)

    # Panel 3: holdout error bars.
    plot = panel(panels[2], "Frozen holdout prediction")
    pred = prediction[prediction["pair"] == PRIMARY]
    methods = ["ara_quadrant", "persistence", "local_ratio", "global_ratio", "affine_ar2"]
    method_colors = ["#3568a8", "#b9c0c8", "#d79b2e", "#8f99a4", "#7f8f42"]
    all_values = pred[pred["method"].isin(methods)]["normalized_mae"].to_numpy()
    ymax = max(1e-12, float(np.max(all_values)) * 1.08)
    px0, py0, px1, py1 = plot
    group_width = (px1 - px0) / len(FAMILIES)
    bar_width = group_width * 0.13
    for group, family in enumerate(FAMILIES):
        centre = px0 + (group + 0.5) * group_width
        for j, (method, color) in enumerate(zip(methods, method_colors)):
            value = float(pred[(pred["family"] == family) & (pred["method"] == method)]["normalized_mae"].iloc[0])
            left = centre + (j - 2.5) * bar_width
            top = py1 - value / ymax * (py1 - py0)
            draw.rectangle((int(left), int(top), int(left + bar_width * 0.86), py1), fill=color, outline="#49515a")
        draw.text((int(centre - 75), py1 + 14), family, fill=ink, font=small_font)
    legend_y = panels[2][1] + 53
    legend_x = panels[2][0] + 300
    for j, (method, color) in enumerate(zip(methods, method_colors)):
        lx = legend_x + (j % 3) * 240
        ly = legend_y + (j // 3) * 25
        draw.rectangle((lx, ly, lx + 16, ly + 12), fill=color)
        draw.text((lx + 22, ly - 3), method, fill=ink, font=small_font)
    draw.text((panels[2][0] + 12, panels[2][1] + 355), "normalised MAE", fill=ink, font=label_font)

    # Panel 4: radial landmark audit.
    plot = panel(panels[3], "Post-gate radial landmark audit")
    primary_radial = radial[radial["pair"] == PRIMARY]
    models = ["lead_e_phi_error", "reciprocal_e_error", "reciprocal_phi_error", "unity_error"]
    model_labels = ["1/e–Phi", "1/e–e", "1/Phi–Phi", "unity"]
    model_colors = ["#d79b2e", "#7f8f42", "#3568a8", "#aeb5bd"]
    grouped_values = {
        model: primary_radial.groupby("lag")[model].median().reindex(RADIAL_LAGS).to_numpy()
        for model in models
    }
    ymax = max(float(np.max(v)) for v in grouped_values.values()) * 1.08
    point = mapper(plot, (0, len(RADIAL_LAGS) - 1), (0, max(ymax, 1e-12)))
    for model, label, color in zip(models, model_labels, model_colors):
        pts = [point(i, value) for i, value in enumerate(grouped_values[model])]
        draw.line(pts, fill=color, width=4)
        for px, py in pts:
            draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=color)
    for i, lag in enumerate(RADIAL_LAGS):
        px, _ = point(i, 0)
        draw.text((px - 12, plot[3] + 14), str(lag), fill=ink, font=small_font)
    legend_y = panels[3][1] + 54
    for j, (label, color) in enumerate(zip(model_labels, model_colors)):
        lx = panels[3][0] + 330 + (j % 2) * 260
        ly = legend_y + (j // 2) * 25
        draw.line((lx, ly + 7, lx + 22, ly + 7), fill=color, width=4)
        draw.text((lx + 30, ly - 3), label, fill=ink, font=small_font)
    draw.text((panels[3][0] + 470, panels[3][3] - 50), "prefix lag", fill=ink, font=label_font)
    draw.text((panels[3][0] + 10, panels[3][1] + 360), "log-distance", fill=ink, font=label_font)

    # Shared legend for arrival families.
    lx, ly = 94, 816
    for family in FAMILIES:
        draw.line((lx, ly + 8, lx + 28, ly + 8), fill=palette[family], width=5)
        draw.text((lx + 36, ly - 3), family, fill=ink, font=small_font)
        lx += 260

    image.save(OUT_FIG)


def main() -> None:
    raw, raw_stats = generate_raw()
    spot = direct_spot_checks(raw)
    series_rows = []
    step_rows = []
    step_stats = {}
    scores: dict[tuple[str, str], dict] = {}
    broken_scores: dict[tuple[str, int], dict] = {}
    radial_rows = []

    for pair in PAIRS:
        for family_index, family in enumerate(FAMILIES):
            z = pair_series(raw, pair, family)
            for n, value in zip(PREFIXES, z):
                series_rows.append(
                    {
                        "pair": pair,
                        "family": family,
                        "n": int(n),
                        "u": float(value.real),
                        "v": float(value.imag),
                        "amplitude": float(abs(value)),
                        "phase_rad": float(np.angle(value)),
                    }
                )
            rows, stats = step_records(pair, family, z)
            step_rows.extend(rows)
            step_stats[f"{pair}|{family}"] = stats
            scores[(pair, family)] = predictor_score(
                z, SHUFFLE_SEED + 101 * family_index + 1009 * list(PAIRS).index(pair)
            )
            radial_rows.extend(radial_audit(pair, family, z))

    for family_index, family in enumerate(FAMILIES):
        for shift in BROKEN_SHIFTS:
            z = pair_series(raw, PRIMARY, family, right_shift=shift)
            broken_scores[(family, shift)] = predictor_score(
                z, SHUFFLE_SEED + 100_000 + 101 * family_index + shift
            )

    series = pd.DataFrame(series_rows)
    steps = pd.DataFrame(step_rows)
    radial = pd.DataFrame(radial_rows)
    radial_winner_counts = {
        str(pair): {
            str(name): int(count)
            for name, count in group["winner"].value_counts().items()
        }
        for pair, group in radial.groupby("pair")
    }
    radial_winner_counts["__all_pairs__"] = {
        str(name): int(count) for name, count in radial["winner"].value_counts().items()
    }
    post_hoc_radial = post_hoc_primary_pooled_radial(series)

    prediction_rows = []
    for (pair, family), score in scores.items():
        if not score.get("valid"):
            continue
        baseline_best = min(
            score["errors"][name]["normalized_mae"]
            for name in ["persistence", "global_ratio", "affine_ar2"]
        )
        for method, error in score["errors"].items():
            prediction_rows.append(
                {
                    "pair": pair,
                    "family": family,
                    "method": method,
                    "mae": error["mae"],
                    "normalized_mae": error["normalized_mae"],
                    "best_fixed_baseline": baseline_best,
                    "ara_improvement_over_best_fixed": (
                        baseline_best - score["errors"]["ara_quadrant"]["normalized_mae"]
                    ),
                    "shuffle_p05": score["shuffle_error_p05"],
                    "shuffle_median": score["shuffle_error_median"],
                    "ara_shuffle_percentile": score["ara_shuffle_percentile"],
                }
            )
    for (family, shift), score in broken_scores.items():
        if not score.get("valid"):
            continue
        prediction_rows.append(
            {
                "pair": f"broken_primary_shift_{shift}",
                "family": family,
                "method": "ara_quadrant",
                "mae": score["errors"]["ara_quadrant"]["mae"],
                "normalized_mae": score["errors"]["ara_quadrant"]["normalized_mae"],
                "best_fixed_baseline": math.nan,
                "ara_improvement_over_best_fixed": math.nan,
                "shuffle_p05": score["shuffle_error_p05"],
                "shuffle_median": score["shuffle_error_median"],
                "ara_shuffle_percentile": score["ara_shuffle_percentile"],
            }
        )
    prediction = pd.DataFrame(prediction_rows)

    g0 = bool(
        raw_stats["min_overlap"] >= -1e-12
        and raw_stats["max_overlap"] <= 1.0 + 1e-12
        and spot["max_abs_error"] <= 1e-10
        and not series.duplicated(["pair", "family", "n"]).any()
        and not steps.duplicated(["pair", "family", "n_from", "n_to"]).any()
    )

    g1_families = []
    for family in FAMILIES:
        stats = step_stats[f"{PRIMARY}|{family}"]
        nonzero = sum(stats["quadrant_counts"][state] > 0 for state in STATE_NAMES)
        if stats["valid_fraction"] >= 0.90 and nonzero == 4:
            g1_families.append(family)
    g1 = len(g1_families) >= 2

    g2_families = []
    for family in FAMILIES:
        score = scores[(PRIMARY, family)]
        if not score.get("valid"):
            continue
        ara = score["errors"]["ara_quadrant"]["normalized_mae"]
        if (
            ara < score["errors"]["persistence"]["normalized_mae"]
            and ara < score["errors"]["global_ratio"]["normalized_mae"]
            and ara < score["errors"]["affine_ar2"]["normalized_mae"]
            and ara < score["shuffle_error_p05"]
        ):
            g2_families.append(family)
    g2 = len(g2_families) >= 2

    improvements = {}
    g3_winners = []
    for family in FAMILIES:
        family_improvements = {}
        for pair in PAIRS:
            score = scores[(pair, family)]
            if not score.get("valid"):
                family_improvements[pair] = -math.inf
                continue
            best = min(
                score["errors"][name]["normalized_mae"]
                for name in ["persistence", "global_ratio", "affine_ar2"]
            )
            family_improvements[pair] = (
                best - score["errors"]["ara_quadrant"]["normalized_mae"]
            )
        winner = max(family_improvements, key=family_improvements.get)
        improvements[family] = family_improvements
        if winner == PRIMARY:
            g3_winners.append(family)
    g3 = len(g3_winners) >= 2

    g4_families = []
    broken_comparison = {}
    for family in FAMILIES:
        intact = scores[(PRIMARY, family)]["errors"]["ara_quadrant"]["normalized_mae"]
        broken = {
            str(shift): broken_scores[(family, shift)]["errors"]["ara_quadrant"]["normalized_mae"]
            for shift in BROKEN_SHIFTS
        }
        broken_comparison[family] = {"intact": intact, "broken": broken}
        if all(intact < value for value in broken.values()):
            g4_families.append(family)
    g4 = len(g4_families) >= 2

    if not g0:
        verdict = "INVALID"
    elif g0 and g1 and g2 and g3 and g4:
        verdict = "QUADRANT STRUCTURE SUPPORTED IN THIS MODEL"
    elif g0 and g1 and g2:
        verdict = "GENERIC COMPLEX STRUCTURE ONLY"
    elif g0 and g1:
        verdict = "COORDINATE RECOVERED WITHOUT PREDICTIVE SUPPORT"
    else:
        verdict = "NOT SUPPORTED"

    series.to_csv(OUT_SERIES, index=False, float_format="%.12g")
    steps.to_csv(OUT_STEPS, index=False, float_format="%.12g")
    prediction.to_csv(OUT_PREDICTION, index=False, float_format="%.12g")
    radial.to_csv(OUT_RADIAL, index=False, float_format="%.12g")
    make_figure(series, steps, prediction, radial)

    payload = {
        "test": "T307 complex irrationality quadrant in muon-Fusion overlap model",
        "fresh_range": {"min": 257, "max": 1024, "count": len(PREFIXES)},
        "train_holdout": {"train_max": TRAIN_MAX, "holdout_min": HOLDOUT_MIN},
        "source_phases": len(PHASES),
        "pulse_width": WIDTH,
        "families": FAMILIES,
        "primary_pair": {"name": PRIMARY, "left": "phi_time", "right": "one_over_e"},
        "raw_stats": raw_stats,
        "spot_checks": spot,
        "step_stats": step_stats,
        "scores": {f"{pair}|{family}": score for (pair, family), score in scores.items()},
        "broken_scores": {
            f"{family}|shift_{shift}": score
            for (family, shift), score in broken_scores.items()
        },
        "improvements": improvements,
        "broken_comparison": broken_comparison,
        "radial_winner_counts": radial_winner_counts,
        "post_hoc_primary_pooled_radial": post_hoc_radial,
        "gates": {
            "G0_implementation": g0,
            "G1_four_quadrant_coordinate": g1,
            "G1_passing_families": g1_families,
            "G2_ordered_lineage": g2,
            "G2_passing_families": g2_families,
            "G3_primary_specificity": g3,
            "G3_primary_winner_families": g3_winners,
            "G4_intact_vs_broken": g4,
            "G4_passing_families": g4_families,
        },
        "verdict": verdict,
        "artifacts": {
            "series": OUT_SERIES.name,
            "steps": OUT_STEPS.name,
            "prediction": OUT_PREDICTION.name,
            "radial": OUT_RADIAL.name,
            "figure": OUT_FIG.name,
        },
        "boundary": (
            "Idealized scheduling model only; not laboratory muon data and not "
            "evidence for a universal physical 1/e-to-Phi mechanism."
        ),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "gates": payload["gates"]}, indent=2))


if __name__ == "__main__":
    main()
