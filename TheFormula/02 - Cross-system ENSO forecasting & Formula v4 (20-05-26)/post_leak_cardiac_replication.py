#!/usr/bin/env python3
"""Reproduce and audit the 2026-04-30 nsr050 ARA-vs-Fourier test.

The reproduction path is deliberately faithful to the recovered transcript.
It also reports two different forecast questions:

1. online_one_step: every true beat may update the prediction of the next beat;
2. cold_25_percent: no observation after the 75% split may update predictions.

The original +0.686 versus +0.308 result belongs to (1), despite having been
described at the time as a 5.99-hour cold forecast.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import wfdb


PHI = (1.0 + math.sqrt(5.0)) / 2.0
GAMMA = 1.0 / PHI**3
FS = 128.0

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[3]
DB_DIR = WORKSPACE / "normal-sinus-rhythm-rr-interval-database-1.0.0"


def ara_to_t(ara: float, period: float) -> tuple[float, float]:
    return period / (2.0 * (1.0 + ara)), ara * period / (2.0 * (1.0 + ara))


def polarity(ara: float) -> float:
    return max(0.0, 1.0 - abs(ara - 1.0) / (PHI - 1.0))


def value_at_times(
    t: np.ndarray, ara: float, amp: float, period: float, t_ref: float = 0.0
) -> np.ndarray:
    """Exact waveform definition used by the original map_heart_v3.py."""
    a = max(0.05, ara)
    pol = polarity(ara)
    t_acc, t_rel = ara_to_t(a, period)
    out = np.zeros_like(t, dtype=float)
    x = np.mod(t - t_ref, period)
    m1 = x < t_rel
    m2 = (x >= t_rel) & (x < t_rel + t_acc)
    m3 = (x >= t_rel + t_acc) & (x < 2.0 * t_rel + t_acc)
    m4 = x >= 2.0 * t_rel + t_acc
    out[m1] = amp * (1.0 - np.power(np.clip(x[m1] / t_rel, 0, 1), a))
    out[m2] = -amp * pol * np.power(
        np.clip((x[m2] - t_rel) / t_acc, 0, 1), 1.0 / a
    )
    out[m3] = -amp * pol * (
        1.0
        - np.power(
            np.clip((x[m3] - t_rel - t_acc) / t_rel, 0, 1), a
        )
    )
    out[m4] = amp * np.power(
        np.clip((x[m4] - 2.0 * t_rel - t_acc) / t_acc, 0, 1), 1.0 / a
    )
    return out


def overflow_envelope(
    t: np.ndarray, ara: float, amp: float, period: float, t_ref: float = 0.0
) -> np.ndarray:
    return np.maximum(value_at_times(t, ara, amp, period, t_ref), 0.0)


def classify_coupling(rung: int) -> int:
    return 1 if abs(rung - 1) <= 1 else 2


def coupling_strength(rung: int, ctype: int) -> float:
    distance = abs(rung - 1)
    return PHI ** (-distance * (1 if ctype == 1 else 2))


def load_rr(subject: str) -> tuple[np.ndarray, np.ndarray]:
    annotation = wfdb.rdann(str(DB_DIR / subject), "ecg")
    beat_times = np.asarray(annotation.sample, dtype=float) / FS
    rr = np.diff(beat_times) * 1000.0
    times = beat_times[1:]
    keep = (rr >= 300.0) & (rr <= 1800.0)
    times = times[keep]
    rr = rr[keep]
    return times - times[0], rr


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def metrics(pred: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    return {
        "corr": safe_corr(pred, actual),
        "mae_ms": float(np.mean(np.abs(pred - actual))),
        "std_ratio": float(np.std(pred) / np.std(actual)),
    }


def fast_search(
    t: np.ndarray, residual: np.ndarray, period: float, ctype: int
) -> dict[str, float]:
    """Exact 6-by-5 grid used in the full-resolution follow-up."""
    ara_grid = np.linspace(0.1, 2.0, 6)
    tref_grid = np.linspace(0.0, period, 5, endpoint=False)
    best: dict[str, float] = {"corr": -2.0}
    signal_fn = value_at_times if ctype == 1 else overflow_envelope
    for ara in ara_grid:
        for t_ref in tref_grid:
            signal = signal_fn(t, ara, 1.0, period, t_ref)
            denominator = float(np.sum(signal * signal))
            if denominator < 1e-9:
                continue
            amplitude = float(np.sum(signal * residual) / denominator)
            prediction = amplitude * signal
            if np.std(prediction) < 1e-9:
                continue
            corr = safe_corr(prediction, residual)
            if np.isfinite(corr) and corr > best["corr"]:
                best = {
                    "ara": float(ara),
                    "amp": amplitude,
                    "period": float(period),
                    "t_ref": float(t_ref),
                    "corr": corr,
                    "mae": float(np.mean(np.abs(prediction - residual))),
                }
    return best


def fit_ara(
    t: np.ndarray, values: np.ndarray, candidate_rungs: list[int]
) -> dict[str, object]:
    """Exact greedy selection and joint amplitude refit from the transcript."""
    centerline = float(np.mean(values))
    residual = values - centerline
    candidates: list[dict[str, float | int]] = []
    for rung in candidate_rungs:
        period = PHI**rung
        ctype = classify_coupling(rung)
        candidate: dict[str, float | int] = fast_search(t, residual, period, ctype)
        candidate.update(
            rung=rung,
            ctype=ctype,
            kappa=coupling_strength(rung, ctype),
        )
        candidates.append(candidate)
    candidates.sort(key=lambda candidate: abs(float(candidate["corr"])), reverse=True)

    chosen: list[dict[str, float | int]] = []
    current_residual = residual.copy()
    for candidate in candidates:
        if len(chosen) >= 10:
            break
        refit: dict[str, float | int] = fast_search(
            t,
            current_residual,
            float(candidate["period"]),
            int(candidate["ctype"]),
        )
        if abs(float(refit["corr"])) < 0.05:
            continue
        refit.update(
            rung=int(candidate["rung"]),
            ctype=int(candidate["ctype"]),
            kappa=float(candidate["kappa"]),
        )
        signal_fn = value_at_times if int(refit["ctype"]) == 1 else overflow_envelope
        current_residual -= signal_fn(
            t,
            float(refit["ara"]),
            float(refit["amp"]),
            float(refit["period"]),
            float(refit["t_ref"]),
        )
        chosen.append(refit)

    if chosen:
        design = np.zeros((len(t), len(chosen) + 1))
        design[:, 0] = 1.0
        for index, subsystem in enumerate(chosen):
            signal_fn = (
                value_at_times if int(subsystem["ctype"]) == 1 else overflow_envelope
            )
            design[:, index + 1] = float(subsystem["kappa"]) * signal_fn(
                t,
                float(subsystem["ara"]),
                1.0,
                float(subsystem["period"]),
                float(subsystem["t_ref"]),
            )
        coefficients, *_ = np.linalg.lstsq(design, values, rcond=None)
        centerline = float(coefficients[0])
        for index, subsystem in enumerate(chosen):
            subsystem["amp_raw"] = float(coefficients[index + 1])
            subsystem["amp"] = float(
                coefficients[index + 1] * float(subsystem["kappa"])
            )

    fit = {"centerline": centerline, "subsystems": chosen}
    train_prediction = predict_ara(t, fit)
    fit["train_metrics"] = metrics(train_prediction, values)
    return fit


def predict_ara(t: np.ndarray, fit: dict[str, object]) -> np.ndarray:
    prediction = np.full_like(t, float(fit["centerline"]), dtype=float)
    for subsystem in fit["subsystems"]:  # type: ignore[union-attr]
        signal_fn = value_at_times if int(subsystem["ctype"]) == 1 else overflow_envelope
        prediction += float(subsystem["amp_raw"]) * float(subsystem["kappa"]) * signal_fn(
            t,
            float(subsystem["ara"]),
            1.0,
            float(subsystem["period"]),
            float(subsystem["t_ref"]),
        )
    return prediction


def fit_fourier(
    t_train: np.ndarray, values_train: np.ndarray, n_frequencies: int
) -> dict[str, object]:
    centered = values_train - np.mean(values_train)
    uniform_t = np.linspace(t_train[0], t_train[-1], len(t_train))
    uniform_v = np.interp(uniform_t, t_train, centered)
    fft_values = np.fft.rfft(uniform_v)
    fft_frequencies = np.fft.rfftfreq(
        len(uniform_v), d=float(np.mean(np.diff(uniform_t)))
    )
    amplitudes = np.abs(fft_values)
    allowed = (fft_frequencies > 1.0 / (t_train[-1] / 2.0)) & (
        fft_frequencies < 0.5
    )
    ranked = np.where(allowed, amplitudes, 0.0)
    top_indices = np.argsort(ranked)[::-1][:n_frequencies]
    periods = 1.0 / fft_frequencies[top_indices]
    design = fourier_design(t_train, periods)
    coefficients, *_ = np.linalg.lstsq(design, values_train, rcond=None)
    return {"periods": periods, "coefficients": coefficients}


def fourier_design(t: np.ndarray, periods: np.ndarray) -> np.ndarray:
    design = np.zeros((len(t), 2 * len(periods) + 1))
    design[:, 0] = 1.0
    for index, period in enumerate(periods):
        omega = 2.0 * np.pi / period
        design[:, 1 + 2 * index] = np.cos(omega * t)
        design[:, 2 + 2 * index] = np.sin(omega * t)
    return design


def predict_fourier(t: np.ndarray, fit: dict[str, object]) -> np.ndarray:
    return fourier_design(t, fit["periods"]) @ fit["coefficients"]  # type: ignore[operator]


def online_residual_update(
    static_prediction: np.ndarray, observed: np.ndarray, gamma: float = GAMMA
) -> np.ndarray:
    """Original rule: actual observation i-1 updates prediction i."""
    updated = static_prediction.copy()
    updated[1:] += gamma * (observed[:-1] - static_prediction[:-1])
    return updated


def cold_residual_forecast(
    static_test: np.ndarray,
    last_train_residual: float,
    gamma: float = GAMMA,
) -> np.ndarray:
    """AR(1) multi-step residual forecast with no test observations."""
    horizons = np.arange(1, len(static_test) + 1, dtype=float)
    return static_test + (gamma**horizons) * last_train_residual


def run_subject(subject: str) -> dict[str, object]:
    t, values = load_rr(subject)
    split_time = float(t[-1] * 0.75)
    train_mask = t <= split_time
    test_mask = ~train_mask
    t_train, values_train = t[train_mask], values[train_mask]
    t_test, values_test = t[test_mask], values[test_mask]
    rungs = [rung for rung in range(23) if t_train[-1] / PHI**rung >= 2.0]

    started = time.time()
    ara_fit = fit_ara(t_train, values_train, rungs)
    ara_static_all = predict_ara(t, ara_fit)
    ara_online_all = online_residual_update(ara_static_all, values)
    ara_cold = cold_residual_forecast(
        ara_static_all[test_mask], values_train[-1] - ara_static_all[train_mask][-1]
    )

    subsystem_count = len(ara_fit["subsystems"])
    original_ara_parameter_count = 3 * subsystem_count + 1
    fourier_frequency_count = max(1, (original_ara_parameter_count - 1) // 2)
    fourier_fit = fit_fourier(t_train, values_train, fourier_frequency_count)
    fourier_static_all = predict_fourier(t, fourier_fit)
    fourier_online_all = online_residual_update(fourier_static_all, values)
    fourier_cold = cold_residual_forecast(
        fourier_static_all[test_mask],
        values_train[-1] - fourier_static_all[train_mask][-1],
    )

    persistence_online = values[:-1][test_mask[1:]]
    persistence_actual = values[1:][test_mask[1:]]
    centerline = np.full_like(values_test, np.mean(values_train))

    results = {
        "subject": subject,
        "n_beats": int(len(values)),
        "span_hours": float(t[-1] / 3600.0),
        "train_beats": int(np.sum(train_mask)),
        "test_beats": int(np.sum(test_mask)),
        "test_hours": float((t_test[-1] - t_test[0]) / 3600.0),
        "gamma_1_over_phi_cubed": GAMMA,
        "rungs": rungs,
        "subsystems": ara_fit["subsystems"],
        "reported_parameter_count_ara": original_ara_parameter_count,
        "reported_parameter_count_fourier": 2 * fourier_frequency_count + 1,
        "fourier_periods_seconds": [float(x) for x in fourier_fit["periods"]],
        "fit_seconds": float(time.time() - started),
        "metrics": {
            "centerline_cold": metrics(centerline, values_test),
            "ara_static_cold": metrics(ara_static_all[test_mask], values_test),
            "ara_online_one_step": metrics(ara_online_all[test_mask], values_test),
            "ara_true_cold": metrics(ara_cold, values_test),
            "fourier_static_cold": metrics(fourier_static_all[test_mask], values_test),
            "fourier_online_one_step": metrics(
                fourier_online_all[test_mask], values_test
            ),
            "fourier_true_cold": metrics(fourier_cold, values_test),
            "persistence_online_one_step": metrics(
                persistence_online, persistence_actual
            ),
        },
        "audit": {
            "online_test_observations_consumed": int(np.sum(test_mask) - 1),
            "cold_test_observations_consumed": 0,
            "model_selection_uses_train_only": True,
            "original_online_rule_is_causal": True,
            "original_online_rule_is_six_hour_cold": False,
        },
    }
    return results


def print_result(result: dict[str, object]) -> None:
    print(
        f"{result['subject']}: {result['n_beats']} beats, "
        f"{result['test_hours']:.2f} h test, "
        f"{len(result['subsystems'])} ARA subsystems"
    )
    print("method                              corr       MAE ms")
    print("----------------------------------------------------")
    for name, score in result["metrics"].items():
        print(f"{name:34s} {score['corr']:+.6f}  {score['mae_ms']:9.3f}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("subjects", nargs="*", default=["nsr050"])
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "post_leak_cardiac_replication_results.json",
    )
    args = parser.parse_args()
    results = [run_subject(subject) for subject in args.subjects]
    for result in results:
        print_result(result)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
