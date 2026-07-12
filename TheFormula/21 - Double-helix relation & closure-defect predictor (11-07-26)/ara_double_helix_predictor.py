#!/usr/bin/env python3
"""Strict-causal test of the preregistered ARA double-helix predictor.

The equations, records, preprocessing, horizons, and pass conditions are frozen in
PREREGISTRATION.md. Do not tune this script after inspecting the primary result;
create a separately named v2 instead.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import wfdb
from scipy.signal import find_peaks


HERE = Path(__file__).resolve().parent
WORKSPACE = Path(__file__).resolve().parents[4]
DATA_DIR = WORKSPACE / "normal-sinus-rhythm-rr-interval-database-1.0.0"
OUT_JSON = HERE / "ara_double_helix_prediction_result.json"
OUT_MD = HERE / "ARA_DOUBLE_HELIX_PREDICTION_RESULT.md"

PRIMARY = "nsr047"
REPLICATION = "nsr053"
RECORDS = (PRIMARY, REPLICATION)
TRAIN_FRAC = 0.70
BLOCK = 10
HORIZONS = (1, 3, 6, 12, 24, 48)
LAGS = (0, 1, 2, 3, 6, 12, 24, 48)
N_PERIODS = 3
MIN_PERIOD = 8
MAX_PERIOD = 512
PERIOD_SEPARATION = 1.20
LOCAL_WINDOW_CYCLES = 4
RIDGE_ALPHA = 1.0
EPS = 1e-12


def load_rr(record: str) -> np.ndarray:
    ann = wfdb.rdann(str(DATA_DIR / record), "ecg")
    rr = np.diff(np.asarray(ann.sample, dtype=float)) / float(ann.fs) * 1000.0
    rr = rr[np.isfinite(rr) & (rr >= 300.0) & (rr <= 2000.0)]
    n = (len(rr) // BLOCK) * BLOCK
    if n < BLOCK * 2000:
        raise RuntimeError(f"{record}: too few usable RR intervals ({n})")
    return np.median(rr[:n].reshape(-1, BLOCK), axis=1)


def select_periods(train: np.ndarray) -> list[int]:
    x = np.asarray(train, dtype=float)
    t = np.arange(len(x), dtype=float)
    a = np.column_stack([np.ones(len(x)), t - t.mean()])
    beta = np.linalg.lstsq(a, x, rcond=None)[0]
    z = (x - a @ beta) * np.hanning(len(x))
    power = np.abs(np.fft.rfft(z)) ** 2
    freq = np.fft.rfftfreq(len(z))
    candidates: list[tuple[float, int]] = []
    for i in range(1, len(freq)):
        if freq[i] <= 0:
            continue
        period = 1.0 / freq[i]
        if MIN_PERIOD <= period <= MAX_PERIOD:
            candidates.append((float(power[i]), int(round(period))))
    candidates.sort(reverse=True)
    selected: list[int] = []
    for _, period in candidates:
        if all(max(period, p) / min(period, p) >= PERIOD_SEPARATION for p in selected):
            selected.append(period)
        if len(selected) == N_PERIODS:
            break
    if len(selected) != N_PERIODS:
        raise RuntimeError(f"Could not select {N_PERIODS} separated periods: {selected}")
    return sorted(selected)


def release_fraction(train: np.ndarray, period: int) -> float:
    distance = max(2, int(round(0.40 * period)))
    prominence = max(EPS, 0.10 * float(np.std(train)))
    peaks, _ = find_peaks(train, distance=distance, prominence=prominence)
    fractions: list[float] = []
    for left, right in zip(peaks[:-1], peaks[1:]):
        span = int(right - left)
        if span < max(3, int(0.45 * period)) or span > int(2.5 * period):
            continue
        trough = int(left + np.argmin(train[left : right + 1]))
        frac = (trough - left) / span
        if 0.10 <= frac <= 0.90:
            fractions.append(float(frac))
    if len(fractions) < 4:
        return 0.5
    return float(np.clip(np.median(fractions), 0.20, 0.80))


def harmonic_design(n: int, periods: list[int]) -> np.ndarray:
    t = np.arange(n, dtype=float)
    cols = [np.ones(n)]
    for p in periods:
        w = 2.0 * np.pi / p
        cols.extend([np.cos(w * t), np.sin(w * t)])
    return np.column_stack(cols)


def causal_local_coefficients(y: np.ndarray, periods: list[int]) -> tuple[np.ndarray, int]:
    n = len(y)
    x = harmonic_design(n, periods)
    d = x.shape[1]
    window = int(LOCAL_WINDOW_CYCLES * max(periods))
    outer = np.einsum("ni,nj->nij", x, x)
    xy = x * y[:, None]
    c_outer = np.concatenate([np.zeros((1, d, d)), np.cumsum(outer, axis=0)], axis=0)
    c_xy = np.concatenate([np.zeros((1, d)), np.cumsum(xy, axis=0)], axis=0)
    coeff = np.full((n, d), np.nan, dtype=float)
    penalty = np.eye(d) * 1e-6
    penalty[0, 0] = 0.0
    for t in range(window - 1, n):
        lo = t - window + 1
        xtx = c_outer[t + 1] - c_outer[lo]
        xty = c_xy[t + 1] - c_xy[lo]
        coeff[t] = np.linalg.solve(xtx + penalty, xty)
    return coeff, window


def states_from_coefficients(coeff: np.ndarray, periods: list[int]) -> np.ndarray:
    n = len(coeff)
    states = np.full((n, len(periods), 2), np.nan, dtype=float)
    t = np.arange(n, dtype=float)
    for j, p in enumerate(periods):
        w = 2.0 * np.pi / p
        a = coeff[:, 1 + 2 * j]
        b = coeff[:, 2 + 2 * j]
        cs = np.cos(w * t)
        sn = np.sin(w * t)
        states[:, j, 0] = a * cs + b * sn
        states[:, j, 1] = a * sn - b * cs
    return states


def rotate(u: np.ndarray, angle: float) -> np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    return np.asarray([c * u[0] - s * u[1], s * u[0] + c * u[1]], dtype=float)


def shaped_cosine(theta: float, release: float) -> float:
    phase = theta % (2.0 * math.pi)
    boundary = 2.0 * math.pi * release
    if phase <= boundary:
        warped = math.pi * phase / max(boundary, EPS)
    else:
        warped = math.pi + math.pi * (phase - boundary) / max(2.0 * math.pi - boundary, EPS)
    return math.cos(warped)


def deterministic_forecasts(
    coeff: np.ndarray,
    states: np.ndarray,
    periods: list[int],
    releases: list[float],
    origins: np.ndarray,
    horizon: int,
) -> dict[str, np.ndarray]:
    out = {k: [] for k in ("rolling_circle", "shape_only", "relation_only", "ara_helix", "mean_kappa", "mean_closure")}
    for t in origins:
        intercept = float(coeff[t, 0])
        circle_sum = shape_sum = relation_sum = helix_sum = 0.0
        kappas: list[float] = []
        closures: list[float] = []
        for j, p in enumerate(periods):
            u = states[t, j]
            half = int(round(p / 2.0))
            v = -states[t - half, j]
            closure = u - states[t - p, j]
            denom = float(np.linalg.norm(u) * np.linalg.norm(v))
            kappa = 0.0 if denom < EPS else float(np.clip(np.dot(u, v) / denom, 0.0, 1.0))
            consensus = 0.5 * (u + v)
            relation_state = (1.0 - kappa) * u + kappa * consensus
            pitch_state = relation_state + (float(horizon) / float(p)) * closure
            angle = 2.0 * math.pi * horizon / p
            circle_future = rotate(u, angle)
            relation_future = rotate(pitch_state, angle)
            circle_sum += float(circle_future[0])
            relation_sum += float(relation_future[0])
            shape_sum += float(np.linalg.norm(circle_future)) * shaped_cosine(
                math.atan2(circle_future[1], circle_future[0]), releases[j]
            )
            helix_sum += float(np.linalg.norm(relation_future)) * shaped_cosine(
                math.atan2(relation_future[1], relation_future[0]), releases[j]
            )
            kappas.append(kappa)
            closures.append(float(np.linalg.norm(closure)))
        out["rolling_circle"].append(intercept + circle_sum)
        out["shape_only"].append(intercept + shape_sum)
        out["relation_only"].append(intercept + relation_sum)
        out["ara_helix"].append(intercept + helix_sum)
        out["mean_kappa"].append(float(np.mean(kappas)))
        out["mean_closure"].append(float(np.mean(closures)))
    return {k: np.asarray(v, dtype=float) for k, v in out.items()}


def ridge_fit_predict(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
    mu = np.mean(x_train, axis=0)
    sd = np.std(x_train, axis=0)
    sd[sd < EPS] = 1.0
    a = (x_train - mu) / sd
    b = (x_test - mu) / sd
    a = np.column_stack([np.ones(len(a)), a])
    b = np.column_stack([np.ones(len(b)), b])
    reg = np.eye(a.shape[1]) * RIDGE_ALPHA
    reg[0, 0] = 0.0
    beta = np.linalg.solve(a.T @ a + reg, a.T @ y_train)
    return b @ beta


def lag_matrix(y: np.ndarray, origins: np.ndarray) -> np.ndarray:
    return np.asarray([[y[t - lag] for lag in LAGS] for t in origins], dtype=float)


def quadrant(position: np.ndarray, movement: np.ndarray, center: float) -> np.ndarray:
    return np.column_stack([np.where(position >= center, 1, -1), np.where(movement >= 0.0, 1, -1)])


def score(y: np.ndarray, origins: np.ndarray, horizon: int, pred: np.ndarray, center: float) -> dict:
    truth = y[origins + horizon]
    current = y[origins]
    corr = float(np.corrcoef(truth, pred)[0, 1]) if np.std(pred) > EPS else 0.0
    mae = float(np.mean(np.abs(truth - pred)))
    actual_change = truth - current
    predicted_change = pred - current
    direction = float(np.mean(np.sign(actual_change) == np.sign(predicted_change)))
    q_current = quadrant(current, current - y[origins - 1], center)
    q_truth = quadrant(truth, actual_change, center)
    q_pred = quadrant(pred, predicted_change, center)
    q_acc = float(np.mean(np.all(q_truth == q_pred, axis=1)))
    transition = np.any(q_truth != q_current, axis=1)
    transition_direction = (
        float(np.mean(np.sign(actual_change[transition]) == np.sign(predicted_change[transition])))
        if np.any(transition)
        else None
    )
    truth_std = float(np.std(actual_change))
    amp_ratio = float(np.std(predicted_change) / truth_std) if truth_std > EPS else None
    return {
        "n": int(len(truth)),
        "corr": corr,
        "mae": mae,
        "direction": direction,
        "quadrant_accuracy": q_acc,
        "transition_n": int(np.sum(transition)),
        "transition_direction": transition_direction,
        "amplitude_ratio": amp_ratio,
    }


def run_record(record: str) -> dict:
    y = load_rr(record)
    cutoff = int(len(y) * TRAIN_FRAC)
    train = y[:cutoff]
    periods = select_periods(train)
    releases = [release_fraction(train, p) for p in periods]
    ara_coordinates = [2.0 * (1.0 - r) for r in releases]
    coeff, local_window = causal_local_coefficients(y, periods)
    states = states_from_coefficients(coeff, periods)
    start = max(local_window - 1 + max(periods), max(LAGS) + 1)
    center = float(np.median(train))
    horizon_results = {}

    for h in HORIZONS:
        train_origins = np.arange(start, cutoff - h, dtype=int)
        test_origins = np.arange(max(cutoff, start), len(y) - h, dtype=int)
        if len(train_origins) < 100 or len(test_origins) < 100:
            raise RuntimeError(f"{record} h={h}: insufficient origins")
        train_det = deterministic_forecasts(coeff, states, periods, releases, train_origins, h)
        test_det = deterministic_forecasts(coeff, states, periods, releases, test_origins, h)
        xtr_lag = lag_matrix(y, train_origins)
        xte_lag = lag_matrix(y, test_origins)
        ytr = y[train_origins + h]
        pred = {
            "persistence": y[test_origins].copy(),
            "ar_ridge": ridge_fit_predict(xtr_lag, ytr, xte_lag),
            "rolling_circle": test_det["rolling_circle"],
            "shape_only": test_det["shape_only"],
            "relation_only": test_det["relation_only"],
            "ara_helix": test_det["ara_helix"],
            "ar_plus_circle": ridge_fit_predict(
                np.column_stack([xtr_lag, train_det["rolling_circle"]]),
                ytr,
                np.column_stack([xte_lag, test_det["rolling_circle"]]),
            ),
            "ar_plus_ara": ridge_fit_predict(
                np.column_stack([xtr_lag, train_det["ara_helix"]]),
                ytr,
                np.column_stack([xte_lag, test_det["ara_helix"]]),
            ),
        }
        horizon_results[str(h)] = {
            "scores": {name: score(y, test_origins, h, values, center) for name, values in pred.items()},
            "diagnostics": {
                "mean_kappa": float(np.mean(test_det["mean_kappa"])),
                "mean_closure": float(np.mean(test_det["mean_closure"])),
            },
        }
    return {
        "record": record,
        "n_downsampled": int(len(y)),
        "cutoff": int(cutoff),
        "periods": periods,
        "release_fractions": releases,
        "ara_coordinates": ara_coordinates,
        "local_window": int(local_window),
        "horizons": horizon_results,
    }


def causal_prefix_audit(record: str, result: dict) -> dict:
    y = load_rr(record)
    cutoff = int(result["cutoff"])
    periods = [int(p) for p in result["periods"]]
    full_coeff, _ = causal_local_coefficients(y, periods)
    prefix_end = min(len(y), cutoff + 128)
    prefix_coeff, _ = causal_local_coefficients(y[:prefix_end], periods)
    valid = np.isfinite(prefix_coeff[:, 0])
    delta = np.nanmax(np.abs(full_coeff[:prefix_end][valid] - prefix_coeff[valid]))
    return {"prefix_end": int(prefix_end), "max_coefficient_difference": float(delta), "passed": bool(delta < 1e-10)}


def verdict(records: dict) -> dict:
    details = {}
    mean_lifts = {}
    transition_lifts = {}
    for record, result in records.items():
        wins_both = 0
        corr_lifts = []
        trans_lifts = []
        for h in HORIZONS:
            scores = result["horizons"][str(h)]["scores"]
            circle = scores["ar_plus_circle"]
            ara = scores["ar_plus_ara"]
            corr_lift = ara["corr"] - circle["corr"]
            mae_lift = circle["mae"] - ara["mae"]
            trans_lift = (ara["transition_direction"] or 0.0) - (circle["transition_direction"] or 0.0)
            corr_lifts.append(corr_lift)
            trans_lifts.append(trans_lift)
            wins_both += int(corr_lift > 0.0 and mae_lift > 0.0)
        details[record] = {"wins_both": wins_both}
        mean_lifts[record] = float(np.mean(corr_lifts))
        transition_lifts[record] = float(np.mean(trans_lifts))
    primary_pass = details[PRIMARY]["wins_both"] >= 3 and all(v > 0.0 for v in mean_lifts.values())
    partial = (not primary_pass) and all(v >= 0.05 for v in transition_lifts.values())
    return {
        "status": "PASS" if primary_pass else ("PARTIAL_SUPPORT" if partial else "FAIL"),
        "details": details,
        "mean_corr_lift_ar_plus_ara_vs_circle": mean_lifts,
        "mean_transition_direction_lift": transition_lifts,
    }


def fmt(v: float | None, digits: int = 3) -> str:
    return "n/a" if v is None else f"{v:+.{digits}f}"


def write_markdown(payload: dict) -> None:
    lines = [
        "# ARA Double-Helix Prediction Result",
        "",
        "**Date:** 2026-07-11  ",
        "**Protocol:** frozen in PREREGISTRATION.md before primary/replication scoring  ",
        f"**Verdict:** **{payload['verdict']['status']}**",
        "",
        "## What was tested",
        "",
        "The ARA model used the same causal local harmonic states as the rolling-circle control, then added:",
        "",
        "- half-cycle phase/anti-phase consensus;",
        "- full-cycle closure defect as helix pitch;",
        "- train-only asymmetric accumulation/release projection;",
        "- no fitted relation or closure weights.",
        "",
    ]
    for record, result in payload["records"].items():
        lines.extend([
            f"## {record}",
            "",
            f"Selected periods: {result['periods']} downsampled steps.  ",
            f"Release fractions: {[round(x, 4) for x in result['release_fractions']]}.  ",
            f"ARA coordinates: {[round(x, 4) for x in result['ara_coordinates']]}.",
            "",
            "| h | circle corr | ARA corr | corr lift | circle MAE | ARA MAE | MAE lift | circle dir | ARA dir | transition lift |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for h in HORIZONS:
            scores = result["horizons"][str(h)]["scores"]
            circle = scores["ar_plus_circle"]
            ara = scores["ar_plus_ara"]
            lines.append(
                f"| {h} | {fmt(circle['corr'])} | {fmt(ara['corr'])} | {fmt(ara['corr']-circle['corr'])} "
                f"| {circle['mae']:.3f} | {ara['mae']:.3f} | {circle['mae']-ara['mae']:+.3f} "
                f"| {circle['direction']:.3f} | {ara['direction']:.3f} "
                f"| {fmt((ara['transition_direction'] or 0.0)-(circle['transition_direction'] or 0.0))} |"
            )
        lines.extend(["", "### Full model comparison", "", "| h | model | corr | MAE | direction | quadrant | amp ratio |", "|---:|---|---:|---:|---:|---:|---:|"])
        for h in HORIZONS:
            scores = result["horizons"][str(h)]["scores"]
            for model in ("persistence", "ar_ridge", "rolling_circle", "shape_only", "relation_only", "ara_helix", "ar_plus_circle", "ar_plus_ara"):
                s = scores[model]
                lines.append(
                    f"| {h} | {model} | {fmt(s['corr'])} | {s['mae']:.3f} | {s['direction']:.3f} "
                    f"| {s['quadrant_accuracy']:.3f} | {s['amplitude_ratio']:.3f} |"
                )
        lines.extend(["", f"Causal prefix audit: {payload['causal_audits'][record]}", ""])
    v = payload["verdict"]
    lines.extend([
        "## Preregistered decision",
        "",
        f"- Primary horizons winning both correlation and MAE: **{v['details'][PRIMARY]['wins_both']}/6**.",
        f"- Mean correlation lift, primary: **{fmt(v['mean_corr_lift_ar_plus_ara_vs_circle'][PRIMARY])}**.",
        f"- Mean correlation lift, replication: **{fmt(v['mean_corr_lift_ar_plus_ara_vs_circle'][REPLICATION])}**.",
        f"- Mean transition-direction lift, primary: **{fmt(v['mean_transition_direction_lift'][PRIMARY])}**.",
        f"- Mean transition-direction lift, replication: **{fmt(v['mean_transition_direction_lift'][REPLICATION])}**.",
        "",
        "The verdict above is mechanical under the frozen pass/failure rules. Any reinterpretation belongs in a separately labelled follow-up, not in this result.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    records = {record: run_record(record) for record in RECORDS}
    audits = {record: causal_prefix_audit(record, records[record]) for record in RECORDS}
    if not all(a["passed"] for a in audits.values()):
        raise RuntimeError(f"Causal prefix audit failed: {audits}")
    payload = {"date": "2026-07-11", "protocol": "PREREGISTRATION.md", "records": records, "causal_audits": audits}
    payload["verdict"] = verdict(records)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_markdown(payload)
    print(json.dumps(payload["verdict"], indent=2))


if __name__ == "__main__":
    main()
