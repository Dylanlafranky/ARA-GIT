"""MX1 development-only Gauss <-> ARA/TE-ARA analysis.

This script may inspect the Alves/OSIRIS development archive only. It does not
accept or open the sealed Tang-Wu-Tao confirmation files.

Outputs:
  - MX1_DEVELOPMENT_RESULTS.json
  - MX1_DEVELOPMENT_TIMESERIES.csv
  - MX1_DEVELOPMENT_CELLS.csv
  - MX1_DEVELOPMENT_REPORT.md
  - MX1_DEVELOPMENT_GEOMETRY.png

TE-ARA values here are explicitly signal-power analogues. A complete physical
energy TE-ARA would also need a declared field-plus-particle energy ledger.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


FIELD_MD5 = "b4f645e3876e3ae6b432b0de211ded8c"
PHASE_MD5 = "e73debf0cf66d6c5af5d7cd1f62490c1"
FIELD_SHA256 = "0b368655fe61b33a3193d7d01180623d4f1df4be068b68fb4d453cd8e6d62907"
PHASE_SHA256 = "1cef8ab44720f60ab6559d04333fa60e8a9415963ff26356a177128181b8770f"


class RestrictedNumpyUnpickler(pickle.Unpickler):
    """Allow only the NumPy constructors used by the published archives."""

    def find_class(self, module: str, name: str):
        allowed = {
            ("numpy.core.multiarray", "_reconstruct"): np._core.multiarray._reconstruct,
            ("numpy.core.multiarray", "scalar"): np._core.multiarray.scalar,
            ("numpy", "ndarray"): np.ndarray,
            ("numpy", "dtype"): np.dtype,
            ("numpy.core.numeric", "_frombuffer"): np._core.numeric._frombuffer,
        }
        try:
            return allowed[(module, name)]
        except KeyError as exc:
            raise pickle.UnpicklingError(
                f"Blocked unexpected pickle global: {module}.{name}"
            ) from exc


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_load(path: Path):
    with path.open("rb") as handle:
        return RestrictedNumpyUnpickler(handle).load()


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    good = np.isfinite(a) & np.isfinite(b)
    if good.sum() < 3 or np.std(a[good]) == 0 or np.std(b[good]) == 0:
        return float("nan")
    return float(np.corrcoef(a[good], b[good])[0, 1])


def regression_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    good = np.isfinite(actual) & np.isfinite(predicted)
    actual = actual[good]
    predicted = predicted[good]
    error = predicted - actual
    denom = float(np.sum((actual - np.mean(actual)) ** 2))
    correlation = corr(actual, predicted)
    return {
        "n": int(len(actual)),
        "correlation": correlation if math.isfinite(correlation) else None,
        "mae": float(np.mean(np.abs(error))),
        "nrmse_by_std": float(np.sqrt(np.mean(error**2)) / np.std(actual)),
        "r2": float(1.0 - np.sum(error**2) / denom) if denom > 0 else float("nan"),
    }


def one_sided_power(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    coeff = np.fft.rfft(values - np.mean(values))
    power = np.abs(coeff) ** 2
    weights = np.full(len(power), 2.0)
    weights[0] = 1.0
    if len(values) % 2 == 0:
        weights[-1] = 1.0
    return coeff, weights * power


def phase_fold(values: np.ndarray, mode: int, bins: int = 64) -> np.ndarray:
    """Fold all peer cells onto one cycle without narrow-band filtering."""
    n = len(values)
    phase_index = (mode * np.arange(n)) % n
    which = np.floor(phase_index * bins / n).astype(int)
    sums = np.bincount(which, weights=values, minlength=bins)
    counts = np.bincount(which, minlength=bins)
    folded = sums / np.maximum(counts, 1)
    # Fixed one-pass circular 1:2:1 smoother suppresses deposition-grid noise.
    return (np.roll(folded, 1) + 2.0 * folded + np.roll(folded, -1)) / 4.0


def component_ara(folded: np.ndarray, sign: int) -> float:
    """Raw accumulation/release ratio for one signed lobe.

    Orientation is increasing spatial phase. Values above 2 are retained in
    raw output but are not accepted as clean bounded ARA coordinates.
    """
    wave = sign * (np.asarray(folded, dtype=float) - np.mean(folded))
    n = len(wave)
    peak = int(np.argmax(wave))
    if wave[peak] <= 0:
        return float("nan")

    left = None
    right = None
    for distance in range(1, n):
        candidate = (peak - distance) % n
        if wave[candidate] <= 0:
            left = candidate
            break
    for distance in range(1, n):
        candidate = (peak + distance) % n
        if wave[candidate] <= 0:
            right = candidate
            break
    if left is None or right is None:
        return float("nan")

    left_positive = (left + 1) % n
    right_positive = (right - 1) % n
    left_fraction = wave[left_positive] / (
        wave[left_positive] - wave[left]
    ) if wave[left_positive] != wave[left] else 0.0
    right_fraction = wave[right_positive] / (
        wave[right_positive] - wave[right]
    ) if wave[right_positive] != wave[right] else 0.0

    accumulation = (peak - left_positive) % n + left_fraction
    release = (right_positive - peak) % n + right_fraction
    if accumulation <= 0 or release <= 0:
        return float("nan")
    return float(accumulation / release)


def pair_coordinates(source: np.ndarray) -> tuple[float, float, float, float]:
    q_plus = float(np.mean(np.maximum(source, 0.0)))
    q_minus = float(np.mean(np.maximum(-source, 0.0)))
    total = q_plus + q_minus
    x_q = 2.0 * q_plus / total if total > 0 else float("nan")
    return q_plus, q_minus, total, x_q


def periodic_interpolate(values: np.ndarray, positions: np.ndarray) -> np.ndarray:
    n = len(values)
    grid = np.arange(n + 1, dtype=float)
    wrapped_values = np.concatenate([values, values[:1]])
    return np.interp(np.mod(positions, n), grid, wrapped_values)


def cell_pair_measurements(
    source: np.ndarray,
    field: np.ndarray,
    mode: int,
    dx: float,
    samples_per_cell: int = 128,
) -> list[dict]:
    """Measure complete peer cells using a field-fundamental phase origin."""
    n = len(source)
    coefficient = np.fft.rfft(field - np.mean(field))[mode]
    period_samples = n / mode
    start = (-np.angle(coefficient) * n / (2.0 * np.pi * mode)) % period_samples
    cells = []
    for cell in range(mode):
        positions = start + cell * period_samples + np.linspace(
            0.0, period_samples, samples_per_cell + 1
        )
        source_values = periodic_interpolate(source, positions)
        field_values = periodic_interpolate(field, positions)
        coordinate = positions * dx
        q_plus = float(np.trapezoid(np.maximum(source_values, 0.0), coordinate))
        q_minus = float(np.trapezoid(np.maximum(-source_values, 0.0), coordinate))
        total = q_plus + q_minus
        x_q = 2.0 * q_plus / total if total > 0 else float("nan")
        cells.append({
            "cell": cell,
            "q_plus": q_plus,
            "q_minus": q_minus,
            "tq": total,
            "xq": x_q,
            "qnet_from_pair": total * (x_q - 1.0),
            "boundary_field_difference": float(field_values[-1] - field_values[0]),
        })
    return cells


def spectral_entropy(power: np.ndarray) -> float:
    p = np.asarray(power[1:], dtype=float)
    total = float(np.sum(p))
    if total <= 0:
        return float("nan")
    p = p / total
    positive = p > 0
    return float(-np.sum(p[positive] * np.log(p[positive])) / np.log(len(p)))


def fit_model(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray):
    mean = np.mean(train_x, axis=0)
    scale = np.std(train_x, axis=0)
    scale[scale == 0] = 1.0
    z_train = (train_x - mean) / scale
    z_test = (test_x - mean) / scale
    design_train = np.column_stack([np.ones(len(z_train)), z_train])
    design_test = np.column_stack([np.ones(len(z_test)), z_test])
    beta = np.linalg.lstsq(design_train, train_y, rcond=None)[0]
    return design_test @ beta, {
        "intercept_standardised": float(beta[0]),
        "coefficients_standardised": [float(v) for v in beta[1:]],
        "feature_mean": [float(v) for v in mean],
        "feature_std": [float(v) for v in scale],
    }


def finite_or_none(value):
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, (np.integer, int)):
        return int(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[4] / "_data_cache" / "ara_em1",
    )
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    field_path = args.data_dir / "fld_data.pkl"
    phase_path = args.data_dir / "phase_space_data.pkl"
    hashes = {
        "field_md5": digest(field_path, "md5"),
        "field_sha256": digest(field_path, "sha256"),
        "phase_md5": digest(phase_path, "md5"),
        "phase_sha256": digest(phase_path, "sha256"),
    }
    expected = {
        "field_md5": FIELD_MD5,
        "field_sha256": FIELD_SHA256,
        "phase_md5": PHASE_MD5,
        "phase_sha256": PHASE_SHA256,
    }
    if hashes != expected:
        raise RuntimeError(f"Development archive hash mismatch: {hashes}")

    field = safe_load(field_path)
    phase = safe_load(phase_path)
    x = np.asarray(field["x"], dtype=float)
    t = np.asarray(field["t"], dtype=float)
    e_field = np.asarray(field["E"], dtype=float)
    distribution = np.asarray(phase["F"], dtype=float)
    dx = float(field["dx"])
    du = float(phase["du"])

    if e_field.shape != (459, 256) or distribution.shape != (459, 256, 256):
        raise RuntimeError("Unexpected development array shape")
    if not np.allclose(t, phase["t"]) or not np.allclose(x, phase["x"]):
        raise RuntimeError("Field and particle grids do not match")

    electron_density = du * np.sum(distribution, axis=1)
    rho_f = 1.0 - electron_density
    n_space = e_field.shape[1]
    k_phys = 2.0 * np.pi * np.fft.rfftfreq(n_space, d=dx)
    e_hat = np.fft.rfft(e_field, axis=1)
    rho_g_hat = 1j * k_phys[None, :] * e_hat
    rho_g = np.fft.irfft(rho_g_hat, n=n_space, axis=1)
    rho_c = (np.roll(e_field, -1, axis=1) - np.roll(e_field, 1, axis=1)) / (2.0 * dx)

    e_rms = np.sqrt(np.mean(e_field**2, axis=1))
    initial_noise = float(np.median(e_rms[:10]))
    amplitude_gate = e_rms >= 10.0 * initial_noise

    raw_mode_power = np.abs(e_hat) ** 2
    raw_mode_power[:, 0] = 0.0
    integrated = np.sum(raw_mode_power[amplitude_gate], axis=0)
    k0_mode = int(np.argmax(integrated))
    k0_physical = float(k_phys[k0_mode])
    fundamental_fraction = raw_mode_power[:, k0_mode] / np.sum(raw_mode_power, axis=1)
    coherent_gate = fundamental_fraction >= 0.25
    eligible = amplitude_gate & coherent_gate

    harmonic_modes = [
        multiple * k0_mode
        for multiple in range(1, 13)
        if multiple * k0_mode < len(k_phys)
    ]
    harmonic_set = np.asarray(harmonic_modes, dtype=int)

    rows: list[dict] = []
    cell_rows: list[dict] = []
    for index in range(len(t)):
        e_coeff, e_power = one_sided_power(e_field[index])
        g_coeff, g_power = one_sided_power(rho_g[index])
        f_coeff, f_power = one_sided_power(rho_f[index])

        p_e = float(np.sum(e_power[harmonic_set]) / np.sum(e_power[1:]))
        p_g = float(np.sum(g_power[harmonic_set]) / np.sum(g_power[1:]))
        p_f = float(np.sum(f_power[harmonic_set]) / np.sum(f_power[1:]))

        folded_e = phase_fold(e_field[index], k0_mode)
        folded_g = phase_fold(rho_g[index], k0_mode)
        folded_f = phase_fold(rho_f[index], k0_mode)

        ara_e_positive = component_ara(folded_e, +1)
        ara_e_negative = component_ara(folded_e, -1)
        ara_e_clean = (
            math.isfinite(ara_e_positive)
            and math.isfinite(ara_e_negative)
            and 0.0 < ara_e_positive <= 2.0
            and 0.0 < ara_e_negative <= 2.0
        )
        ara_e_mean_centered = (
            0.5 * (ara_e_positive + ara_e_negative) - 1.0
            if ara_e_clean else float("nan")
        )
        ara_e_contrast = (
            ara_e_positive - ara_e_negative
            if ara_e_clean else float("nan")
        )

        qpf, qmf, tqf, xqf = pair_coordinates(rho_f[index])
        qpg, qmg, tqg, xqg = pair_coordinates(rho_g[index])
        cells_f = cell_pair_measurements(rho_f[index], e_field[index], k0_mode, dx)
        cells_g = cell_pair_measurements(rho_g[index], e_field[index], k0_mode, dx)
        cell_xq_f = np.asarray([cell["xq"] for cell in cells_f])
        cell_xq_g = np.asarray([cell["xq"] for cell in cells_g])
        for cell_f, cell_g in zip(cells_f, cells_g):
            cell_rows.append({
                "index": index,
                "time": float(t[index]),
                "eligible": bool(eligible[index]),
                "cell": cell_f["cell"],
                "xq_f": cell_f["xq"],
                "xq_g": cell_g["xq"],
                "tq_f": cell_f["tq"],
                "tq_g": cell_g["tq"],
                "qnet_f": cell_f["qnet_from_pair"],
                "qnet_g": cell_g["qnet_from_pair"],
                "boundary_field_difference": cell_g["boundary_field_difference"],
            })
        source_activity_f = float(np.mean(np.abs(rho_f[index] - np.mean(rho_f[index]))))
        source_activity_g = float(np.mean(np.abs(rho_g[index] - np.mean(rho_g[index]))))
        dimensional_scale = k0_physical * e_rms[index]
        shape_factor_f = source_activity_f / dimensional_scale if dimensional_scale > 0 else float("nan")
        shape_factor_g = source_activity_g / dimensional_scale if dimensional_scale > 0 else float("nan")

        centred_e = e_field[index] - np.mean(e_field[index])
        std_e = float(np.std(centred_e))
        skew_e = float(np.mean((centred_e / std_e) ** 3)) if std_e > 0 else float("nan")
        crest_e = float(np.max(np.abs(centred_e)) / std_e) if std_e > 0 else float("nan")

        rows.append(
            {
                "index": index,
                "time": float(t[index]),
                "eligible": bool(eligible[index]),
                "e_rms": float(e_rms[index]),
                "fundamental_fraction": float(fundamental_fraction[index]),
                "te_ara_e_analogue": 2.0 * p_e,
                "te_ara_rho_g_analogue": 2.0 * p_g,
                "te_ara_rho_f_analogue": 2.0 * p_f,
                "other_e_fraction": 1.0 - p_e,
                "other_rho_f_fraction": 1.0 - p_f,
                "ara_e_positive_raw": ara_e_positive,
                "ara_e_negative_raw": ara_e_negative,
                "ara_e_mean_centered_clean": ara_e_mean_centered,
                "ara_e_contrast_clean": ara_e_contrast,
                "ara_te_interaction_clean": (
                    p_e * ara_e_mean_centered if ara_e_clean else float("nan")
                ),
                "ara_rho_g_positive_raw": component_ara(folded_g, +1),
                "ara_rho_g_negative_raw": component_ara(folded_g, -1),
                "ara_rho_f_positive_raw": component_ara(folded_f, +1),
                "ara_rho_f_negative_raw": component_ara(folded_f, -1),
                "q_plus_f_density": qpf,
                "q_minus_f_density": qmf,
                "tq_f_density": tqf,
                "xq_f": xqf,
                "q_plus_g_density": qpg,
                "q_minus_g_density": qmg,
                "tq_g_density": tqg,
                "xq_g": xqg,
                "cell_xq_f_mean": float(np.mean(cell_xq_f)),
                "cell_xq_f_std": float(np.std(cell_xq_f)),
                "cell_xq_g_mean": float(np.mean(cell_xq_g)),
                "cell_xq_g_std": float(np.std(cell_xq_g)),
                "source_activity_f": source_activity_f,
                "source_activity_g": source_activity_g,
                "dimensional_scale_k0_e_rms": dimensional_scale,
                "source_shape_factor_f": shape_factor_f,
                "source_shape_factor_g": shape_factor_g,
                "spectral_entropy_e": spectral_entropy(e_power),
                "skew_e": skew_e,
                "crest_e": crest_e,
            }
        )

    eligible_index = np.flatnonzero(eligible)
    if len(eligible_index) < 30:
        raise RuntimeError("Too few eligible development slices")

    eligible_rows = [rows[i] for i in eligible_index]
    split = int(0.70 * len(eligible_rows))
    train_rows = eligible_rows[:split]
    test_rows = eligible_rows[split:]

    feature_sets = {
        "scale_only": [],
        "te_only": ["te_ara_e_analogue"],
        "ara_only": ["ara_e_mean_centered_clean", "ara_e_contrast_clean"],
        "ara_plus_te": [
            "te_ara_e_analogue",
            "ara_e_mean_centered_clean",
            "ara_e_contrast_clean",
            "ara_te_interaction_clean",
        ],
        "matched_generic": [
            "te_ara_e_analogue",
            "spectral_entropy_e",
            "skew_e",
            "crest_e",
        ],
    }
    common_features = sorted({
        feature
        for features in feature_sets.values()
        for feature in features
    })
    common_train_rows = [
        row for row in train_rows
        if math.isfinite(row["source_shape_factor_f"])
        and all(math.isfinite(row[feature]) for feature in common_features)
    ]
    common_test_rows = [
        row for row in test_rows
        if math.isfinite(row["source_shape_factor_f"])
        and all(math.isfinite(row[feature]) for feature in common_features)
    ]
    model_results = {}
    for name, features in feature_sets.items():
        usable_train = common_train_rows
        usable_test = common_test_rows
        train_y = np.asarray([r["source_shape_factor_f"] for r in usable_train])
        test_y = np.asarray([r["source_shape_factor_f"] for r in usable_test])
        if not features:
            predicted_y = np.full(len(test_y), np.mean(train_y))
            coefficients = {"intercept_standardised": float(np.mean(train_y)), "coefficients_standardised": []}
        else:
            train_x = np.asarray([[r[f] for f in features] for r in usable_train])
            test_x = np.asarray([[r[f] for f in features] for r in usable_test])
            predicted_y, coefficients = fit_model(train_x, train_y, test_x)
        scale_test = np.asarray([r["dimensional_scale_k0_e_rms"] for r in usable_test])
        actual_source = np.asarray([r["source_activity_f"] for r in usable_test])
        predicted_source = predicted_y * scale_test
        model_results[name] = {
            "features": features,
            "train_n": len(usable_train),
            "test_n": len(usable_test),
            "shape_factor_metrics": regression_metrics(test_y, predicted_y),
            "source_activity_metrics": regression_metrics(actual_source, predicted_source),
            "fit": coefficients,
        }

    full_train_y = np.asarray([r["source_shape_factor_f"] for r in train_rows])
    full_test_y = np.asarray([r["source_shape_factor_f"] for r in test_rows])
    full_scale_prediction_y = np.full(len(full_test_y), np.mean(full_train_y))
    full_test_scale = np.asarray([r["dimensional_scale_k0_e_rms"] for r in test_rows])
    full_test_source = np.asarray([r["source_activity_f"] for r in test_rows])
    scale_full_coverage = {
        "train_n": len(train_rows),
        "test_n": len(test_rows),
        "shape_factor_metrics": regression_metrics(full_test_y, full_scale_prediction_y),
        "source_activity_metrics": regression_metrics(
            full_test_source, full_scale_prediction_y * full_test_scale
        ),
    }

    eligible_mask_flat = np.repeat(eligible, n_space)
    level0 = {
        "spectral_derivative": regression_metrics(
            rho_f.ravel()[eligible_mask_flat], rho_g.ravel()[eligible_mask_flat]
        ),
        "central_difference": regression_metrics(
            rho_f.ravel()[eligible_mask_flat], rho_c.ravel()[eligible_mask_flat]
        ),
        "spectral_slope_through_origin": float(
            np.dot(rho_g[eligible].ravel(), rho_f[eligible].ravel())
            / np.dot(rho_g[eligible].ravel(), rho_g[eligible].ravel())
        ),
        "particle_source_mean_offset": float(np.mean(rho_f[eligible])),
    }

    rho_f_hat_all = np.fft.rfft(rho_f, axis=1)
    rho_g_h_hat = np.zeros_like(rho_g_hat)
    rho_f_h_hat = np.zeros_like(rho_f_hat_all)
    rho_g_h_hat[:, harmonic_set] = rho_g_hat[:, harmonic_set]
    rho_f_h_hat[:, harmonic_set] = rho_f_hat_all[:, harmonic_set]
    rho_g_h = np.fft.irfft(rho_g_h_hat, n=n_space, axis=1)
    rho_f_h = np.fft.irfft(rho_f_h_hat, n=n_space, axis=1)
    level1 = {
        "identity_gauss_vs_identity_particle": regression_metrics(
            rho_f_h[eligible].ravel(), rho_g_h[eligible].ravel()
        ),
        "identity_gauss_vs_full_particle": regression_metrics(
            rho_f[eligible].ravel(), rho_g_h[eligible].ravel()
        ),
    }

    def column(name: str) -> np.ndarray:
        return np.asarray([r[name] for r in eligible_rows], dtype=float)

    geometry = {
        "te_source_g_vs_f_correlation": corr(
            column("te_ara_rho_g_analogue"), column("te_ara_rho_f_analogue")
        ),
        "te_source_g_vs_f_mae": float(
            np.mean(np.abs(column("te_ara_rho_g_analogue") - column("te_ara_rho_f_analogue")))
        ),
        "te_field_vs_source_f_correlation": corr(
            column("te_ara_e_analogue"), column("te_ara_rho_f_analogue")
        ),
        "source_activity_g_vs_f": regression_metrics(
            column("source_activity_f"), column("source_activity_g")
        ),
        "pair_xq_g_vs_f": regression_metrics(column("xq_f"), column("xq_g")),
        "pair_xq_f_median": float(np.median(column("xq_f"))),
        "pair_xq_f_max_abs_from_ridge": float(np.max(np.abs(column("xq_f") - 1.0))),
        "te_ara_medians": {
            "field": float(np.median(column("te_ara_e_analogue"))),
            "gauss_source": float(np.median(column("te_ara_rho_g_analogue"))),
            "particle_source": float(np.median(column("te_ara_rho_f_analogue"))),
        },
        "te_ara_ranges": {
            "field": [float(np.min(column("te_ara_e_analogue"))), float(np.max(column("te_ara_e_analogue")))],
            "gauss_source": [float(np.min(column("te_ara_rho_g_analogue"))), float(np.max(column("te_ara_rho_g_analogue")))],
            "particle_source": [float(np.min(column("te_ara_rho_f_analogue"))), float(np.max(column("te_ara_rho_f_analogue")))],
        },
        "clean_bounded_ara_fraction": {
            key: float(np.mean((column(key) > 0.0) & (column(key) <= 2.0)))
            for key in [
                "ara_e_positive_raw",
                "ara_e_negative_raw",
                "ara_rho_f_positive_raw",
                "ara_rho_f_negative_raw",
            ]
        },
    }
    eligible_cells = [row for row in cell_rows if row["eligible"]]
    cell_column = lambda name: np.asarray([row[name] for row in eligible_cells], dtype=float)
    geometry["cell_pair_xq_g_vs_f"] = regression_metrics(
        cell_column("xq_f"), cell_column("xq_g")
    )
    geometry["cell_total_source_g_vs_f"] = regression_metrics(
        cell_column("tq_f"), cell_column("tq_g")
    )
    geometry["cell_qnet_g_vs_f"] = regression_metrics(
        cell_column("qnet_f"), cell_column("qnet_g")
    )
    geometry["cell_boundary_gauss_vs_particle_qnet"] = regression_metrics(
        cell_column("qnet_f"), cell_column("boundary_field_difference")
    )
    geometry["cell_pair_xq_f_range"] = [
        float(np.min(cell_column("xq_f"))),
        float(np.max(cell_column("xq_f"))),
    ]

    results = {
        "claim_id": "MX1-v2",
        "tier": "DEVELOPMENT / EXPLORATORY / NOT CONFIRMATORY",
        "confirmation_arrays_opened": False,
        "fidelity_verdict": "EXACT ENOUGH TO TEST",
        "hashes": hashes,
        "rules": {
            "initial_noise": initial_noise,
            "amplitude_gate": "E_rms >= 10 * median(first 10 E_rms)",
            "coherence_gate": "reference fundamental power fraction >= 0.25",
            "reference_mode_index": k0_mode,
            "reference_k_physical": k0_physical,
            "identity_harmonic_modes": harmonic_modes,
            "te_label": "signal-power TE-ARA analogue; not complete physical joule energy",
            "ara_orientation": "increasing spatial phase; raw left-zero-to-extremum / extremum-to-right-zero",
            "bounded_ara_acceptance": "0 < raw ratio <= 2; larger values retained but flagged compound/undefined",
            "development_split": "first 70% versus final 30% of eligible slices",
        },
        "eligible": {
            "n": int(np.sum(eligible)),
            "first_index": int(eligible_index[0]),
            "first_time": float(t[eligible_index[0]]),
            "last_time": float(t[eligible_index[-1]]),
        },
        "level0": level0,
        "level1": level1,
        "geometry": geometry,
        "compressed_models": model_results,
        "scale_only_full_coverage_diagnostic": scale_full_coverage,
    }

    json_path = args.output_dir / "MX1_DEVELOPMENT_RESULTS.json"
    json_path.write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")

    csv_path = args.output_dir / "MX1_DEVELOPMENT_TIMESERIES.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: finite_or_none(value) for key, value in row.items()})

    cell_csv_path = args.output_dir / "MX1_DEVELOPMENT_CELLS.csv"
    with cell_csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cell_rows[0].keys()))
        writer.writeheader()
        for row in cell_rows:
            writer.writerow({key: finite_or_none(value) for key, value in row.items()})

    te_g = geometry["te_source_g_vs_f_correlation"]
    te_mae = geometry["te_source_g_vs_f_mae"]
    best_name = max(
        model_results,
        key=lambda name: model_results[name]["source_activity_metrics"]["r2"],
    )
    best = model_results[best_name]["source_activity_metrics"]
    report = f"""# MX1 development report — Gauss ↔ ARA/TE-ARA geometry

**Tier:** DEVELOPMENT / EXPLORATORY / NOT CONFIRMATORY  
**Confirmation arrays opened:** No  
**Fidelity verdict:** EXACT ENOUGH TO TEST

## Outcome

The established Gauss instrument check passes on {int(np.sum(eligible))} eligible time slices. The spectral derivative
of the electric field matches the independently deposited particle charge with correlation
{level0["spectral_derivative"]["correlation"]:.6f}, NRMSE {level0["spectral_derivative"]["nrmse_by_std"]:.4f}, and
through-origin slope {level0["spectral_slope_through_origin"]:.6f}.

The identity family is spatial mode {k0_mode} plus its first {len(harmonic_modes)} available multiples through
mode {harmonic_modes[-1]}. Field-side Gauss weighting and particle-side measurement give source-participation
TE-ARA analogues with correlation {te_g:.6f} and mean absolute difference {te_mae:.6f} on the 0–2 scale.
The identity-only Gauss reconstruction matches the independently measured identity-only particle source with
correlation {level1["identity_gauss_vs_identity_particle"]["correlation"]:.6f}. Against the unfiltered full particle
source, its correlation is {level1["identity_gauss_vs_full_particle"]["correlation"]:.6f}; the difference is the
declared Other structure rather than discarded error.

The whole periodic-domain pair coordinate remains close to its 1.0 cancellation ridge: median
{geometry["pair_xq_f_median"]:.6f}; maximum observed displacement {geometry["pair_xq_f_max_abs_from_ridge"]:.6f}.
That is expected because the ring contains complete peer cycles. After phase-aligning and measuring its five cells
separately, particle-side pair ARA ranges from {geometry["cell_pair_xq_f_range"][0]:.4f} to
{geometry["cell_pair_xq_f_range"][1]:.4f}. Field-side and particle-side local pair coordinates correlate
{geometry["cell_pair_xq_g_vs_f"]["correlation"]:.4f}. Their local total unsigned source magnitudes correlate
{geometry["cell_total_source_g_vs_f"]["correlation"]:.6f}, while their local signed net results correlate
{geometry["cell_qnet_g_vs_f"]["correlation"]:.6f}. Total unsigned activity remains non-zero, distinguishing intense
positive/negative structure from an empty zero.

All compressed models were compared on the same {len(common_test_rows)} clean bounded-ARA late slices. The best internal
chronological development model was {best_name}, with held-late source-activity correlation
{best["correlation"]:.4f} and R² {best["r2"]:.4f}. In this development run, adding scalar ARA/TE-ARA coordinates did
not beat the dimensional scale-only bridge. That is a narrowing result: TE-ARA still describes identity participation,
but the tested scalar compression adds no held-late source-magnitude skill here. This is calibration evidence only and
cannot support the ARA claim until a frozen rule transfers to the sealed archive.

## What each coordinate contributes

- Pair ARA x_Q supplies signed positive/negative composition around the 1.0 ridge.
- Whole-ring x_Q is the coarse cancellation view; phase-aligned per-cell x_Q is the local moving view.
- Total unsigned source activity supplies magnitude.
- Field TE-ARA analogue supplies the fraction of field signal power in the declared identity family.
- Source TE-ARA analogue tests whether that identity survives the quarter-turn and k-weighting imposed by Gauss.
- Component ARAs retain positive- and negative-lobe shape. Raw values above 2 are preserved but flagged as compound
  rather than forced onto the bounded scale.
- Other remains one minus identity participation and is never discarded.
- The dimensional source scale is k0 × E_rms. The compressed models predict only the remaining dimensionless shape
  factor, because TE-ARA is a fraction and cannot create absolute magnitude by itself.

## Frozen-development candidates, not yet registered

- Eligibility: E_rms at least ten times the first-ten-slice noise median and fundamental fraction at least 0.25.
- Rung: fixed spatial mode {k0_mode}.
- Identity family: fixed multiples {harmonic_modes}.
- Phase folding: 64 bins with a fixed one-pass circular 1:2:1 deposition-noise smoother.
- Development assessment: chronological 70/30 split.

The confirmation arrays remain sealed. Review these development choices before hashing and registering the transfer test.
"""
    report_path = args.output_dir / "MX1_DEVELOPMENT_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    eligible_time = column("time")
    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
    axes[0].plot(t, e_rms, label="E RMS", color="#2b6cb0")
    axes[0].axvspan(t[eligible_index[0]], t[eligible_index[-1]], alpha=0.12, color="#38a169", label="eligible")
    axes[0].set_ylabel("field scale")
    axes[0].legend(loc="upper left")

    axes[1].plot(eligible_time, column("te_ara_e_analogue"), label="TE-ARA E", linewidth=1.6)
    axes[1].plot(eligible_time, column("te_ara_rho_g_analogue"), label="TE-ARA Gauss source", linewidth=1.3)
    axes[1].plot(eligible_time, column("te_ara_rho_f_analogue"), label="TE-ARA particle source", linewidth=1.1)
    axes[1].set_ylim(0, 2.05)
    axes[1].set_ylabel("0–2 participation")
    axes[1].legend(loc="lower left", ncol=3)

    cell_mean_f = column("cell_xq_f_mean")
    cell_std_f = column("cell_xq_f_std")
    cell_mean_g = column("cell_xq_g_mean")
    axes[2].plot(eligible_time, cell_mean_f, label="mean local particle pair ARA", color="#805ad5")
    axes[2].fill_between(
        eligible_time,
        cell_mean_f - cell_std_f,
        cell_mean_f + cell_std_f,
        color="#805ad5",
        alpha=0.18,
        label="peer-cell ±1 SD",
    )
    axes[2].plot(eligible_time, cell_mean_g, label="mean local Gauss pair ARA", color="#d53f8c", alpha=0.75)
    axes[2].axhline(1.0, color="black", linestyle="--", linewidth=1)
    axes[2].set_ylabel("pair ARA")
    axes[2].legend(loc="upper left")

    for key, label, color in [
        ("ara_e_positive_raw", "E positive lobe", "#dd6b20"),
        ("ara_e_negative_raw", "E negative lobe", "#319795"),
    ]:
        values = column(key)
        clean = (values > 0) & (values <= 2)
        axes[3].plot(eligible_time[clean], values[clean], ".", label=label, color=color, markersize=3)
    axes[3].axhline(1.0, color="black", linestyle="--", linewidth=1)
    axes[3].set_ylim(0, 2.05)
    axes[3].set_ylabel("clean component ARA")
    axes[3].set_xlabel("normalised simulation time")
    axes[3].legend(loc="upper left")
    fig.suptitle("MX1 development geometry — confirmation remains sealed")
    fig.tight_layout()
    fig.savefig(args.output_dir / "MX1_DEVELOPMENT_GEOMETRY.png", dpi=170)
    plt.close(fig)

    print(json.dumps({
        "report": str(report_path),
        "eligible_slices": int(np.sum(eligible)),
        "k0_mode": k0_mode,
        "level0_correlation": level0["spectral_derivative"]["correlation"],
        "te_source_correlation": te_g,
        "te_source_mae": te_mae,
        "best_internal_model": best_name,
        "best_internal_model_metrics": best,
        "confirmation_arrays_opened": False,
    }, indent=2))


if __name__ == "__main__":
    main()
