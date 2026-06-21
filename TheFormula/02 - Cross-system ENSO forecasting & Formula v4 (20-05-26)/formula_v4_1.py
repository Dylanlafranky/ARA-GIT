#!/usr/bin/env python3
"""formula_v4_1.py — Framework-faithful coupling channel projection.

Same wave_shape as v4. New: channel_projection() smoothly interpolates between
bidirectional (rung distance = 0) and half-rectified (large rung distance) using
the framework's 1/phi^|dk| coupler scaling.

NO hard Type 1 / Type 2 categories. The half-rectification emerges geometrically
from how far a subsystem sits from the pump rung.
"""

import math
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1.0 / PHI
INV_PHI3 = 1.0 / (PHI ** 3)
INV_PHI4 = 1.0 / (PHI ** 4)


def wave_shape(phase, ARA):
    """Normalized wave shape in [-1, 1] at phase [0, 1) of cycle.
    Same as v4. Pure geometry from ARA."""
    a = max(0.05, float(ARA))
    T_acc_frac = a / (1.0 + a)
    T_rel_frac = 1.0 / (1.0 + a)
    phase_arr = np.atleast_1d(np.asarray(phase, dtype=float))
    f = np.mod(phase_arr, 1.0)
    out = np.zeros_like(f)
    in_acc = f < T_acc_frac
    in_rel = ~in_acc
    f_acc = f[in_acc] / T_acc_frac
    out[in_acc] = -1.0 + 2.0 * np.power(f_acc, 1.0 / a)
    f_rel = (f[in_rel] - T_acc_frac) / T_rel_frac
    out[in_rel] = 1.0 - 2.0 * np.power(f_rel, a)
    return out if out.shape != (1,) else float(out[0])


def channel_projection(source_wave, rung_distance):
    """Project a subsystem's wave to the pump's R-R sequence.

    Framework Rule 9: coupling channels have their own ARA. The further a
    subsystem sits from the pump rung, the more "overflow-like" the channel
    becomes. Overflow channels mostly transmit the source's accumulation phase
    and reject the release phase (which goes back to the source's own pump).

    Smooth interpolation:
      weight_bi = 1/phi^|Δk|  (full bidirectional weight)
      weight_rect = 1 - weight_bi  (half-rectified weight)

    For Δk = 0: weight_bi = 1.0 → fully bidirectional (direct coupling)
    For Δk = 1: weight_bi = 0.618 → mostly bidirectional (Type 1 handoff)
    For Δk = 2: weight_bi = 0.382 → starting to half-rectify (overflow emerging)
    For Δk = 3: weight_bi = 0.236 → mostly half-rectified
    For Δk → ∞: weight_bi → 0 → fully half-rectified (pure overflow)

    No hard categories — single smooth rule from the framework's coupler scaling.
    """
    abs_dk = abs(int(rung_distance))
    if abs_dk == 0:
        return source_wave
    weight_bi = PHI ** (-abs_dk)
    weight_rect = 1.0 - weight_bi
    half_rectified = np.maximum(source_wave, 0.0)
    return weight_bi * source_wave + weight_rect * half_rectified


def fit_subsystem_at_rung(t_array, v_array, period, rung_distance,
                          ara_grid=None, tref_grid_n=12):
    """Fit a single subsystem at a given rung (with rung distance from pump).

    Returns dict with: ARA, amplitude, t_ref, corr, rung_distance.
    """
    if ara_grid is None:
        ara_grid = np.linspace(0.1, 2.0, 30)
    tref_grid = np.linspace(0, period, tref_grid_n, endpoint=False)
    best = {"corr": 0.0, "ARA": 1.0, "amplitude": 0.0, "centerline": 0.0,
            "t_ref": 0.0, "rung_distance": rung_distance,
            "mae": float("inf")}
    for ara in ara_grid:
        for tref in tref_grid:
            phase = ((t_array - tref) % period) / period
            raw_shape = wave_shape(phase, ara)
            projected = channel_projection(raw_shape, rung_distance)
            X = np.column_stack([np.ones_like(t_array), projected])
            coefs, *_ = np.linalg.lstsq(X, v_array, rcond=None)
            c, A = float(coefs[0]), float(coefs[1])
            pred = c + A * projected
            if pred.std() < 1e-9:
                continue
            corr = float(np.corrcoef(pred, v_array)[0, 1])
            if not np.isfinite(corr):
                continue
            if abs(corr) > abs(best["corr"]):
                best = {"corr": corr, "ARA": float(ara), "amplitude": A,
                        "centerline": c, "t_ref": float(tref),
                        "rung_distance": int(rung_distance),
                        "mae": float(np.mean(np.abs(pred - v_array)))}
    return best


def project_subsystem_signal(t_eval, sub):
    """Compute the projected wave for a fitted subsystem at evaluation times."""
    period = sub['period']
    phase = ((t_eval - sub['t_ref']) % period) / period
    raw = wave_shape(phase, sub['ARA'])
    return channel_projection(raw, sub['rung_distance'])


def fit_hierarchical(t_array, v_array, candidate_rungs, pump_rung,
                     max_subsystems=8):
    """Greedy + joint LSQ fit using v4.1 channel projection."""
    centerline = float(np.mean(v_array))
    residuals = v_array - centerline

    # First pass: best fit per rung
    candidates = []
    for k in candidate_rungs:
        period = PHI ** k
        rung_distance = k - pump_rung
        fit = fit_subsystem_at_rung(t_array, residuals, period, rung_distance)
        fit['rung'] = int(k)
        fit['period'] = float(period)
        candidates.append(fit)

    # Sort by absolute correlation
    candidates.sort(key=lambda c: abs(c['corr']), reverse=True)

    # Sequentially extract top subsystems
    chosen = []
    current_residuals = residuals.copy()
    for c in candidates[:max_subsystems]:
        rung_distance = c['rung'] - pump_rung
        period = c['period']
        refit = fit_subsystem_at_rung(t_array, current_residuals, period,
                                       rung_distance)
        if abs(refit['corr']) < 0.03:
            continue
        refit['rung'] = c['rung']
        refit['period'] = period
        sub_signal = project_subsystem_signal(t_array, refit) * refit['amplitude']
        current_residuals = current_residuals - sub_signal
        chosen.append(refit)

    # Joint LSQ refit
    if chosen:
        N = len(chosen)
        X = np.zeros((len(t_array), N + 1))
        X[:, 0] = 1.0
        for i, s in enumerate(chosen):
            X[:, i + 1] = project_subsystem_signal(t_array, s)
        coefs, *_ = np.linalg.lstsq(X, v_array, rcond=None)
        centerline = float(coefs[0])
        for i, s in enumerate(chosen):
            s['amplitude'] = float(coefs[i + 1])

    pred = np.full_like(v_array, centerline)
    for s in chosen:
        pred += s['amplitude'] * project_subsystem_signal(t_array, s)

    return {
        'centerline': centerline,
        'subsystems': chosen,
        'pred': pred,
        'corr': float(np.corrcoef(pred, v_array)[0, 1]) if pred.std() > 0 else 0,
        'mae': float(np.mean(np.abs(pred - v_array))),
    }


def predict(t_eval, fit_result):
    """Apply a fit to new evaluation times."""
    p = np.full_like(t_eval, fit_result['centerline'], dtype=float)
    for s in fit_result['subsystems']:
        p = p + s['amplitude'] * project_subsystem_signal(t_eval, s)
    return p


def ar_feedback(pred_static, v_obs, gamma=INV_PHI3):
    """1/phi^3 AR feedback (causal — uses observed previous beat)."""
    out = pred_static.copy()
    for i in range(1, len(out)):
        out[i] = pred_static[i] + gamma * (v_obs[i - 1] - pred_static[i - 1])
    return out


if __name__ == "__main__":
    print("formula_v4_1.py — channel projection from coupler scaling")
    print(f"PHI = {PHI:.6f}")
    print()
    print("Channel projection weights by rung distance:")
    print(f"{'Δk':>4} {'weight_bi':>12} {'weight_rect':>14}  interpretation")
    for dk in range(0, 7):
        w_bi = PHI ** (-dk) if dk > 0 else 1.0
        w_rect = 1 - w_bi
        if dk == 0:
            interp = "direct (Type 1, full)"
        elif dk == 1:
            interp = "Type 1 handoff"
        elif dk == 2:
            interp = "transitioning"
        else:
            interp = "Type 2 overflow"
        print(f"{dk:>4} {w_bi:>12.4f} {w_rect:>14.4f}  {interp}")

    # Sanity: projecting a perfect cosine
    print("\nSanity check: project cos wave through different Δk:")
    t = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    test_wave = np.cos(t)
    for dk in [0, 1, 2, 5]:
        proj = channel_projection(test_wave, dk)
        print(f"  Δk={dk}: input range [{test_wave.min():.2f}, {test_wave.max():.2f}],"
              f" projected range [{proj.min():.3f}, {proj.max():.3f}]")
