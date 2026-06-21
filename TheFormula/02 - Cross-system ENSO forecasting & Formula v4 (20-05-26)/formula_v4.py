#!/usr/bin/env python3
"""formula_v4.py — The mature framework formulation.

CORE CLAIM:
    A wave is energy moving through time-geometry.
    ARA + framework geometry give the SHAPE.
    Energy is a separate LOG-SCALE SLIDER for amplitude.
    Multi-scale = same wave at φ-scaled time-rulers.

API:
    wave_shape(phase, ARA)   -> normalized [-1, 1] shape (pure geometry)
    energy_at_scale(...)     -> amplitude scaling on log-measurement axis
    wave_value(...)          -> wave_shape × energy_at_scale, evaluated at time t
    generate_wave(...)       -> generate full wave over a time span at one scale

TEST USAGE: see __main__ at bottom.
"""

import math
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1.0 / PHI
INV_PHI3 = 1.0 / (PHI ** 3)
INV_PHI4 = 1.0 / (PHI ** 4)


# ============================================================
# 1. WAVE SHAPE — derived from ARA + framework geometry alone
# ============================================================

def wave_shape(phase, ARA):
    """Normalized wave shape in [-1, 1] at given phase [0, 1) of cycle.

    The wave is what energy looks like as it traverses ARA-shaped time.

    For ARA = T_acc / T_rel:
    - Accumulation phase (T_acc/T_total fraction): smooth ascent from -1 to +1
    - Release phase (T_rel/T_total fraction): rapid descent from +1 to -1
    - As ARA increases: ascent smoother, descent sharper (engine-like)
    - As ARA decreases below 1: ascent sharper, descent smoother (snap-like)

    Power-law shape parameters derived from ARA itself:
    - Accumulation curvature: f_acc^(1/ARA)  — concave up as ARA grows
    - Release curvature:      f_rel^(ARA)    — convex down as ARA grows
    """
    a = max(0.05, float(ARA))
    T_acc_frac = a / (1.0 + a)
    T_rel_frac = 1.0 / (1.0 + a)

    # Vectorize: handle both scalar and array inputs
    phase_arr = np.atleast_1d(np.asarray(phase, dtype=float))
    f = np.mod(phase_arr, 1.0)

    out = np.zeros_like(f)
    in_acc = f < T_acc_frac
    in_rel = ~in_acc

    # Accumulation: smooth power-law ascent
    f_acc = f[in_acc] / T_acc_frac
    out[in_acc] = -1.0 + 2.0 * np.power(f_acc, 1.0 / a)

    # Release: power-law descent (sharper for higher ARA)
    f_rel = (f[in_rel] - T_acc_frac) / T_rel_frac
    out[in_rel] = 1.0 - 2.0 * np.power(f_rel, a)

    return out if out.shape != (1,) else float(out[0])


# ============================================================
# 2. ENERGY LOG SLIDER — amplitude scaling
# ============================================================

def energy_at_scale(base_amplitude, scale_factor=1.0, ARA=PHI):
    """Energy/amplitude at a chosen measurement scale.

    base_amplitude: the energy magnitude at the reference scale (e.g., from one
                    observation of the data, or from physics of the system).
    scale_factor:   ratio of THIS scale to the reference scale.
                    1.0 = same scale. φ = one rung coarser. 1/φ = one rung finer.
    ARA:            the system's ARA (energy scaling can depend on ARA, since
                    higher-ARA systems pack more energy per cycle).

    Default: amplitude scales linearly with scale_factor (each coarser ruler
    sees proportionally larger amplitude). For ARA-modulated scaling, can be
    extended.
    """
    # Linear scaling: amplitude = base × scale_factor
    # (This is the "log slider" — log_φ(scale_factor) gives the rung shift)
    return base_amplitude * scale_factor


def scale_to_phi_rungs(scale_factor):
    """Convert a multiplicative scale_factor to its φ-rung position.

    scale_factor = φ^k  →  returns k.
    """
    return math.log(max(scale_factor, 1e-9)) / math.log(PHI)


def phi_rungs_to_scale(rung_offset):
    """Inverse: convert φ-rung offset to multiplicative scale factor."""
    return PHI ** rung_offset


# ============================================================
# 3. WAVE VALUE — composition of shape × energy
# ============================================================

def wave_value(t, ARA, base_amplitude, period, t_ref=0.0, scale_factor=1.0):
    """Wave value at time t.

    t:               time(s) at which to evaluate (scalar or array)
    ARA:             system's ARA value
    base_amplitude:  amplitude at the reference scale (from data or physics)
    period:          wave period in time units of t
    t_ref:           phase offset (default 0)
    scale_factor:    multiplicative scale for the energy slider (default 1)

    Returns:         wave value(s) at t, scaled to data units
    """
    t_arr = np.atleast_1d(np.asarray(t, dtype=float))
    phase = ((t_arr - t_ref) % period) / period
    shape = wave_shape(phase, ARA)
    amp = energy_at_scale(base_amplitude, scale_factor, ARA)
    val = amp * shape
    return val if val.shape != (1,) else float(val[0])


def generate_wave(t_array, ARA, base_amplitude, period, t_ref=0.0,
                  centerline=0.0, scale_factor=1.0):
    """Generate the wave at all times in t_array, with optional centerline shift."""
    return centerline + wave_value(t_array, ARA, base_amplitude, period, t_ref, scale_factor)


# ============================================================
# 4. MULTI-SCALE — same wave at φ-rung shifted rulers
# ============================================================

def wave_at_rung_offset(t_array, ARA, base_amplitude, base_period, rung_offset,
                        centerline=0.0, t_ref=0.0):
    """Generate the same wave at a different φ-rung scale.

    rung_offset = +1  →  ruler 1 rung coarser (period × φ, amp × φ)
    rung_offset = -1  →  ruler 1 rung finer (period / φ, amp / φ)
    rung_offset = 0   →  reference scale

    The framework's claim: same ARA, scaled period AND amplitude by φ^rung_offset.
    """
    scale = phi_rungs_to_scale(rung_offset)
    period_at_rung = base_period * scale
    return generate_wave(t_array, ARA, base_amplitude, period_at_rung,
                         t_ref, centerline, scale_factor=scale)


# ============================================================
# 5. SHAPE-FIT — find ARA that best matches a normalized signal
# ============================================================

def fit_shape_to_data(t_array, v_array, period, t_ref=0.0,
                      ara_grid=None):
    """Given (t, v) data and a known period, find the ARA that best matches
    the SHAPE of the wave (assuming amplitude is set separately).

    Returns the best ARA and the corresponding amplitude and centerline.

    This uses the new formulation: shape and amplitude are fit SEPARATELY.
    1. For each candidate ARA, compute normalized shape at data t
    2. Fit linear scaling: v = centerline + amplitude × shape
    3. Pick ARA that maximizes |corr(pred, v)|
    """
    if ara_grid is None:
        ara_grid = np.linspace(0.1, 2.0, 40)

    best = {"corr": 0.0, "ARA": 1.0, "amplitude": 0.0, "centerline": 0.0,
            "mae": float("inf")}
    for ara in ara_grid:
        phase = ((t_array - t_ref) % period) / period
        shape = wave_shape(phase, ara)
        # Linear least squares: v = c + A * shape
        # Solve [1, shape] @ [c, A]^T = v
        X = np.column_stack([np.ones_like(t_array), shape])
        coefs, *_ = np.linalg.lstsq(X, v_array, rcond=None)
        c, A = float(coefs[0]), float(coefs[1])
        pred = c + A * shape
        if pred.std() < 1e-9:
            continue
        corr = float(np.corrcoef(pred, v_array)[0, 1])
        if not np.isfinite(corr):
            continue
        if abs(corr) > abs(best["corr"]):
            best = {
                "corr": corr,
                "ARA": float(ara),
                "amplitude": A,
                "centerline": c,
                "mae": float(np.mean(np.abs(pred - v_array))),
            }
    return best


def fit_shape_amplitude_phase(t_array, v_array, period,
                              ara_grid=None, tref_grid_n=24):
    """Like fit_shape_to_data but ALSO searches over t_ref (phase offset)."""
    if ara_grid is None:
        ara_grid = np.linspace(0.1, 2.0, 40)
    tref_grid = np.linspace(0, period, tref_grid_n, endpoint=False)
    best = {"corr": 0.0, "ARA": 1.0, "amplitude": 0.0, "centerline": 0.0,
            "t_ref": 0.0, "mae": float("inf")}
    for ara in ara_grid:
        for tref in tref_grid:
            phase = ((t_array - tref) % period) / period
            shape = wave_shape(phase, ara)
            X = np.column_stack([np.ones_like(t_array), shape])
            coefs, *_ = np.linalg.lstsq(X, v_array, rcond=None)
            c, A = float(coefs[0]), float(coefs[1])
            pred = c + A * shape
            if pred.std() < 1e-9:
                continue
            corr = float(np.corrcoef(pred, v_array)[0, 1])
            if not np.isfinite(corr):
                continue
            if abs(corr) > abs(best["corr"]):
                best = {
                    "corr": corr, "ARA": float(ara), "amplitude": A,
                    "centerline": c, "t_ref": float(tref),
                    "mae": float(np.mean(np.abs(pred - v_array))),
                }
    return best


# ============================================================
# 6. SIMPLE DEMO
# ============================================================

if __name__ == "__main__":
    print("formula_v4.py — mature framework formulation")
    print(f"PHI = {PHI:.6f}")
    print()

    # Generate one cycle at three different ARAs
    phases = np.linspace(0, 1, 100, endpoint=False)
    print("Example wave_shape values at phase=0.0 (cycle start):")
    for ara_test in [0.5, 1.0, PHI, 2.0]:
        sample = wave_shape(np.array([0.0, 0.25, 0.5, 0.75]), ara_test)
        print(f"  ARA={ara_test:.3f}: {sample}")

    # Multi-scale test: same wave at three rung offsets
    print("\nMulti-scale test (same wave, ruler shifted by φ):")
    t_demo = np.linspace(0, 10, 50)
    for k in [-1, 0, 1, 2]:
        v = wave_at_rung_offset(t_demo, ARA=PHI, base_amplitude=1.0,
                                 base_period=2.0, rung_offset=k)
        print(f"  rung offset {k:+d}: range [{v.min():.3f}, {v.max():.3f}] "
              f"(period at this rung = {2.0 * PHI**k:.3f})")
