"""
ara_nasal_to_enso_prediction_test.py

Vertical ARA transfer prediction test:
  Use the smaller coupled nasal-cycle geometry as an external template to
  forecast the larger ENSO coupled index.

Target:
  ENSO coupled index LI = (zNINO - zSOI) / (abs(zNINO) + abs(zSOI)).

Models:
  - nasal_template: signed coupled-cycle template from 33-subject nasal data.
  - enso_own_template: signed coupled-cycle template from ENSO train only.
  - nino_only_template: one-sided NINO geometry, train only.
  - soi_only_template: one-sided inverted-SOI geometry, train only.
  - ar_current: train-fitted current-state baseline.
  - persistence: current ENSO LI.

No-leakage guard:
  - ENSO scaling is fitted on the chronological train split only.
  - Templates that use ENSO are built from train data only.
  - Phase period estimates are built from train data only.
  - The linear decoder is fitted on train origins only, per horizon.
  - Held-out origins are strictly after the split.
  - The nasal template is external data; it never sees ENSO heldout values.
"""

from __future__ import annotations

import json
import math
from bisect import bisect_right
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter1d

from ara_nasal_enso_coupled_geometry_test import (
    EPS,
    N_PHASE,
    PHI,
    enso_base,
    load_all_nasal,
    mean_signed_template,
    signed_coupled_cycle_templates,
)


HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "ara_nasal_to_enso_prediction_result.json"
OUT_JS = HERE / "ara_nasal_to_enso_prediction_result.js"

HORIZONS = [1, 3, 6, 12, 18, 24]
MIN_ORIGIN = 120
RIDGE_ALPHA = 1e-5


def causal_smooth(x, window=5):
    """Trailing moving average. Uses no samples later than the current index."""
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x, dtype=float)
    csum = np.cumsum(np.r_[0.0, x])
    for i in range(len(x)):
        a = max(0, i - window + 1)
        out[i] = (csum[i + 1] - csum[a]) / float(i - a + 1)
    return out


def corr(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    good = np.isfinite(a) & np.isfinite(b)
    a = a[good]
    b = b[good]
    if len(a) < 5 or np.std(a) < EPS or np.std(b) < EPS:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def mae(pred, actual):
    pred = np.asarray(pred, dtype=float)
    actual = np.asarray(actual, dtype=float)
    good = np.isfinite(pred) & np.isfinite(actual)
    if not np.any(good):
        return float("nan")
    return float(np.mean(np.abs(pred[good] - actual[good])))


def ridge_fit(x, y, alpha=RIDGE_ALPHA):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    good = np.isfinite(y) & np.all(np.isfinite(x), axis=1)
    x = x[good]
    y = y[good]
    if len(y) == 0:
        return np.zeros(x.shape[1] + 1, dtype=float)
    x1 = np.column_stack([np.ones(len(x)), x])
    reg = np.eye(x1.shape[1]) * alpha
    reg[0, 0] = 0.0
    try:
        return np.linalg.solve(x1.T @ x1 + reg, x1.T @ y)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(x1.T @ x1 + reg, x1.T @ y, rcond=None)
        return beta


def ridge_predict(beta, x):
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    x1 = np.column_stack([np.ones(len(x)), x])
    return x1 @ beta


def sign_nonzero(value, fallback=1.0):
    if not math.isfinite(float(value)) or abs(float(value)) < 1e-12:
        return fallback
    return 1.0 if value > 0 else -1.0


def zero_crossings(signal):
    signal = np.asarray(signal, dtype=float)
    crossings = []
    for i in range(1, len(signal)):
        prev = sign_nonzero(signal[i - 1], 0.0)
        cur = sign_nonzero(signal[i], prev)
        if prev != 0.0 and cur != prev:
            crossings.append(i)
    return crossings


def median_period_from_train(signal, split, min_half_len=5):
    crossings = [c for c in zero_crossings(signal[:split]) if c >= 1]
    half_lengths = [b - a for a, b in zip(crossings[:-1], crossings[1:]) if b - a >= min_half_len]
    full_lengths = [c - a for a, c in zip(crossings[:-2], crossings[2:]) if c - a >= 2 * min_half_len]
    if not full_lengths:
        full = 2.0 * (float(np.median(half_lengths)) if half_lengths else 36.0)
    else:
        full = float(np.median(full_lengths))
    return {
        "crossings": crossings,
        "median_half": float(np.median(half_lengths)) if half_lengths else full / 2.0,
        "median_full": full,
        "n_half_lengths": int(len(half_lengths)),
        "n_full_lengths": int(len(full_lengths)),
    }


def sample_template(template, phase):
    template = np.asarray(template, dtype=float)
    p = float(phase % 1.0) * len(template)
    i0 = int(math.floor(p)) % len(template)
    i1 = (i0 + 1) % len(template)
    frac = p - math.floor(p)
    return float((1.0 - frac) * template[i0] + frac * template[i1])


def template_raw_prediction(template, phase_signal, period_info, origin, horizon):
    crossings = period_info["crossings"]
    pos = bisect_right(crossings, origin) - 1
    if pos < 0:
        return None
    last_cross = crossings[pos]
    elapsed = max(0.0, float(origin - last_cross))
    full_period = max(2.0, float(period_info["median_full"]))
    current_sign = sign_nonzero(phase_signal[origin], 1.0)
    phase_future = (elapsed + float(horizon)) / full_period
    return current_sign * sample_template(template, phase_future)


def build_source_library(nasal_subjects):
    library = []
    for item in nasal_subjects:
        file_name = Path(item["path"]).name
        for template, desc in zip(item["cycles"], item["cycle_descriptors"]):
            half1 = float(desc["mid_minute"] - desc["start_minute"])
            half2 = float(desc["end_minute"] - desc["mid_minute"])
            if half1 <= 0 or half2 <= 0:
                continue
            period = half1 + half2
            library.append(
                {
                    "file": file_name,
                    "template": np.asarray(template, dtype=float),
                    "ara": float(half2 / half1),
                    "midpoint_fraction": float(half1 / period),
                    "period": period,
                }
            )
    return library


def last_completed_cycle_info(crossings, origin):
    triples = [(a, b, c) for a, b, c in zip(crossings[:-2], crossings[1:-1], crossings[2:]) if c <= origin]
    if not triples:
        return None
    a, b, c = triples[-1]
    half1 = float(b - a)
    half2 = float(c - b)
    if half1 <= 0 or half2 <= 0:
        return None
    return {
        "start": int(a),
        "mid": int(b),
        "end": int(c),
        "ara": float(half2 / half1),
        "period": float(c - a),
        "midpoint_fraction": float(half1 / (half1 + half2)),
    }


def ara_matched_raw_prediction(source_library, target_signal, crossings, origin, horizon, bandwidth=0.35):
    info = last_completed_cycle_info(crossings, origin)
    if info is None:
        return None
    prev_crossings = [c for c in crossings if c <= origin]
    if not prev_crossings:
        return None
    last_cross = prev_crossings[-1]
    elapsed = float(origin - last_cross)
    period = max(2.0, info["period"])
    current_sign = sign_nonzero(target_signal[origin], 1.0)
    target_ara = max(0.05, info["ara"])
    target_phase = elapsed / period

    values = []
    weights = []
    for item in source_library:
        source_ara = max(0.05, item["ara"])
        ara_weight = math.exp(-abs(math.log(source_ara / target_ara)) / bandwidth)
        midpoint_delta = abs(item["midpoint_fraction"] - info["midpoint_fraction"])
        midpoint_weight = math.exp(-midpoint_delta / 0.20)
        consistency_weight = 1.0
        if target_phase > item["midpoint_fraction"]:
            consistency_weight = 0.35
        weight = ara_weight * midpoint_weight * consistency_weight
        if weight <= 1e-9:
            continue
        phase_future = (elapsed + float(horizon)) / period
        values.append(current_sign * sample_template(item["template"], phase_future))
        weights.append(weight)
    if not weights:
        return None
    return float(np.average(values, weights=weights))


def build_rows(template, phase_signal, target_signal, period_info, origins, horizon):
    rows = []
    y = []
    kept_origins = []
    for origin in origins:
        target_idx = origin + horizon
        if target_idx >= len(target_signal):
            continue
        raw = template_raw_prediction(template, phase_signal, period_info, origin, horizon)
        if raw is None:
            continue
        rows.append([raw, float(target_signal[origin])])
        y.append(float(target_signal[target_idx]))
        kept_origins.append(origin)
    return np.asarray(rows, dtype=float), np.asarray(y, dtype=float), kept_origins


def build_ara_matched_rows(source_library, target_signal, crossings, origins, horizon):
    rows = []
    y = []
    kept_origins = []
    for origin in origins:
        target_idx = origin + horizon
        if target_idx >= len(target_signal):
            continue
        raw = ara_matched_raw_prediction(source_library, target_signal, crossings, origin, horizon)
        info = last_completed_cycle_info(crossings, origin)
        if raw is None or info is None:
            continue
        rows.append([raw, float(target_signal[origin]), float(info["ara"]), float(info["midpoint_fraction"])])
        y.append(float(target_signal[target_idx]))
        kept_origins.append(origin)
    return np.asarray(rows, dtype=float), np.asarray(y, dtype=float), kept_origins


def score_prediction(pred, actual, current):
    pred = np.asarray(pred, dtype=float)
    actual = np.asarray(actual, dtype=float)
    current = np.asarray(current, dtype=float)
    persistence = current.copy()
    out = {
        "n": int(len(actual)),
        "mae": mae(pred, actual),
        "persistence_mae": mae(persistence, actual),
        "mae_lift_vs_persistence": mae(persistence, actual) - mae(pred, actual),
        "corr": corr(pred, actual),
        "persistence_corr": corr(persistence, actual),
    }
    if len(actual):
        out["dominance_sign_accuracy"] = float(np.mean(np.sign(pred) == np.sign(actual)))
        actual_delta = actual - current
        pred_delta = pred - current
        good = np.abs(actual_delta) > 1e-9
        out["delta_direction_accuracy"] = float(np.mean(np.sign(pred_delta[good]) == np.sign(actual_delta[good]))) if np.any(good) else 0.0
        actual_turn = np.sign(actual) != np.sign(current)
        pred_turn = np.sign(pred) != np.sign(current)
        out["turn_event_accuracy"] = float(np.mean(actual_turn == pred_turn))
        out["actual_turn_rate"] = float(np.mean(actual_turn))
        out["pred_turn_rate"] = float(np.mean(pred_turn))
    return out


def load_templates_and_signals():
    # External nasal template: all cached nasal subjects. This is source-domain
    # information and never uses target-domain heldout ENSO values.
    _, _, nasal_cycle_train, nasal_cycle_test, nasal_summary, nasal_subjects = load_all_nasal()
    nasal_template = mean_signed_template(nasal_cycle_train + nasal_cycle_test)
    source_library = build_source_library(nasal_subjects)

    dates, zn, zs, split = enso_base()
    target_li = (zn - zs) / (np.abs(zn) + np.abs(zs) + EPS)
    target_li = causal_smooth(target_li, window=5)
    nino_signal = causal_smooth(zn, window=5)
    soi_signal = causal_smooth(-zs, window=5)

    enso_train_cycles, _ = signed_coupled_cycle_templates(target_li[:split], min_half_len=5, center=0.0)
    enso_template = mean_signed_template(enso_train_cycles)

    nino_train_cycles, _ = signed_coupled_cycle_templates(nino_signal[:split], min_half_len=5, center=0.0)
    soi_train_cycles, _ = signed_coupled_cycle_templates(soi_signal[:split], min_half_len=5, center=0.0)
    nino_template = mean_signed_template(nino_train_cycles)
    soi_template = mean_signed_template(soi_train_cycles)

    signals = {
        "coupled": target_li,
        "nino_only": nino_signal,
        "soi_only": soi_signal,
    }
    templates = {
        "nasal_template": {
            "label": "External nasal coupled template",
            "template": nasal_template,
            "phase_signal": "coupled",
        },
        "enso_own_template": {
            "label": "ENSO train coupled template",
            "template": enso_template,
            "phase_signal": "coupled",
        },
        "nino_only_template": {
            "label": "NINO-only train template",
            "template": nino_template,
            "phase_signal": "nino_only",
        },
        "soi_only_template": {
            "label": "SOI-only inverted train template",
            "template": soi_template,
            "phase_signal": "soi_only",
        },
        "nasal_ara_matched_template": {
            "label": "External nasal template matched by completed ENSO ARA",
            "template": nasal_template,
            "phase_signal": "coupled",
            "ara_matched": True,
        },
    }
    period_info = {
        name: median_period_from_train(signal, split, min_half_len=5)
        for name, signal in signals.items()
    }
    return {
        "dates": [str(d.date()) for d in dates],
        "split": split,
        "target": target_li,
        "signals": signals,
        "templates": templates,
        "period_info": period_info,
        "target_crossings": zero_crossings(target_li),
        "source_library": source_library,
        "nasal_subjects": nasal_summary,
        "n_nasal_signed_cycles": int(len(nasal_cycle_train) + len(nasal_cycle_test)),
        "n_nasal_source_library": int(len(source_library)),
        "n_enso_train_cycles": int(len(enso_train_cycles)),
        "n_nino_train_cycles": int(len(nino_train_cycles)),
        "n_soi_train_cycles": int(len(soi_train_cycles)),
    }


def evaluate_horizon(state, horizon):
    split = state["split"]
    target = state["target"]
    train_origins = list(range(MIN_ORIGIN, split - horizon))
    test_origins = list(range(split, len(target) - horizon))

    current_test = np.asarray([target[o] for o in test_origins], dtype=float)
    actual_test = np.asarray([target[o + horizon] for o in test_origins], dtype=float)

    results = {
        "horizon_months": horizon,
        "n_train_origins_available": len(train_origins),
        "n_test_origins_available": len(test_origins),
        "baselines": {},
        "models": {},
    }

    # Persistence and train-fitted current-state baseline.
    persistence_pred = current_test.copy()
    results["baselines"]["persistence"] = score_prediction(persistence_pred, actual_test, current_test)

    x_train = np.asarray([[target[o]] for o in train_origins], dtype=float)
    y_train = np.asarray([target[o + horizon] for o in train_origins], dtype=float)
    beta_current = ridge_fit(x_train, y_train)
    ar_pred = ridge_predict(beta_current, np.asarray([[target[o]] for o in test_origins], dtype=float))
    results["baselines"]["ar_current"] = {
        **score_prediction(ar_pred, actual_test, current_test),
        "beta": [float(x) for x in beta_current],
    }

    for model_name, spec in state["templates"].items():
        if spec.get("ara_matched"):
            xtr, ytr, _ = build_ara_matched_rows(state["source_library"], target, state["target_crossings"], train_origins, horizon)
            xte, yte, kept = build_ara_matched_rows(state["source_library"], target, state["target_crossings"], test_origins, horizon)
        else:
            phase_signal = state["signals"][spec["phase_signal"]]
            pinfo = state["period_info"][spec["phase_signal"]]
            xtr, ytr, _ = build_rows(spec["template"], phase_signal, target, pinfo, train_origins, horizon)
            xte, yte, kept = build_rows(spec["template"], phase_signal, target, pinfo, test_origins, horizon)
        if len(ytr) < 10 or len(yte) < 5:
            continue
        beta = ridge_fit(xtr, ytr)
        pred = ridge_predict(beta, xte)
        current = np.asarray([target[o] for o in kept], dtype=float)
        raw_pred = xte[:, 0]
        raw_score = score_prediction(raw_pred, yte, current)
        decoded_score = score_prediction(pred, yte, current)
        results["models"][model_name] = {
            "label": spec["label"],
            "phase_signal": spec["phase_signal"],
            "ara_matched": bool(spec.get("ara_matched", False)),
            "n_train": int(len(ytr)),
            "n_test": int(len(yte)),
            "beta": [float(x) for x in beta],
            "raw_template_score": raw_score,
            "decoded_score": decoded_score,
        }
    return results


def best_by_metric(horizon_result, metric="mae"):
    rows = []
    for name, score in horizon_result["baselines"].items():
        rows.append((name, score.get(metric, float("inf"))))
    for name, payload in horizon_result["models"].items():
        rows.append((name, payload["decoded_score"].get(metric, float("inf"))))
    if metric == "mae":
        return min(rows, key=lambda x: x[1])
    return max(rows, key=lambda x: x[1])


def main():
    print("Loading nasal template and ENSO signals...")
    state = load_templates_and_signals()
    print(f"ENSO months: {len(state['target'])}; split={state['split']} ({state['dates'][state['split']]})")
    print(f"Nasal signed cycles: {state['n_nasal_signed_cycles']}")
    print(f"ENSO train cycles: {state['n_enso_train_cycles']}")

    horizon_results = []
    for horizon in HORIZONS:
        print(f"Running horizon {horizon} months...")
        horizon_results.append(evaluate_horizon(state, horizon))

    summary = []
    for result in horizon_results:
        h = result["horizon_months"]
        best_mae_name, best_mae = best_by_metric(result, "mae")
        best_corr_name, best_corr = best_by_metric(result, "corr")
        nasal = result["models"]["nasal_template"]["decoded_score"]
        persistence = result["baselines"]["persistence"]
        enso_own = result["models"]["enso_own_template"]["decoded_score"]
        summary.append(
            {
                "horizon_months": h,
                "best_mae_model": best_mae_name,
                "best_mae": float(best_mae),
                "best_corr_model": best_corr_name,
                "best_corr": float(best_corr),
                "nasal_mae": nasal["mae"],
                "nasal_corr": nasal["corr"],
                "nasal_lift_vs_persistence": nasal["mae_lift_vs_persistence"],
                "persistence_mae": persistence["mae"],
                "persistence_corr": persistence["corr"],
                "enso_own_mae": enso_own["mae"],
                "enso_own_corr": enso_own["corr"],
            }
        )

    payload = {
        "date": "2026-05-23",
        "method": "External nasal signed coupled-cycle template predicts heldout ENSO coupled LI. Per-horizon linear decoder uses train origins only with features [template_future, current_LI].",
        "leakage_guard": [
            "NINO/SOI scaling fitted on chronological train split only.",
            "ENSO-own, NINO-only, and SOI-only templates built from train data only.",
            "Period estimates and zero-crossing phase clocks built from train data only.",
            "Linear decoders fitted on train origins only.",
            "Test origins are strictly after the split.",
            "Nasal template is external source-domain data.",
        ],
        "split": {
            "index": int(state["split"]),
            "date": state["dates"][state["split"]],
            "n_months": int(len(state["target"])),
            "train_start": state["dates"][0],
            "test_end": state["dates"][-1],
        },
        "counts": {
            "nasal_subjects": int(len(state["nasal_subjects"])),
            "nasal_signed_cycles": state["n_nasal_signed_cycles"],
            "nasal_source_library_cycles": state["n_nasal_source_library"],
            "enso_train_cycles": state["n_enso_train_cycles"],
            "nino_train_cycles": state["n_nino_train_cycles"],
            "soi_train_cycles": state["n_soi_train_cycles"],
        },
        "period_info": state["period_info"],
        "summary": summary,
        "horizons": horizon_results,
        "phi": PHI,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_JS.write_text("window.NASAL_TO_ENSO_PREDICTION = " + json.dumps(payload) + ";\n", encoding="utf-8")

    print("\n=== SUMMARY ===")
    for row in summary:
        print(
            f"h={row['horizon_months']:>2}m "
            f"nasal MAE={row['nasal_mae']:.3f} corr={row['nasal_corr']:+.3f} "
            f"lift={row['nasal_lift_vs_persistence']:+.3f} "
            f"best_MAE={row['best_mae_model']}({row['best_mae']:.3f})"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    main()
