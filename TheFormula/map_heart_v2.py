#!/usr/bin/env python3
"""
map_heart_v2.py — Hierarchical heart mapping (subsystems FEED INTO the pump).

REFRAMING FROM v1:
  v1: RR(t) = centerline + Σ subsystem_k(t)                 (parallel, additive)
  v2: pump = ground cycle; subsystems modulate pump via coupling channels
      with their own ARA (Rule 9 in ARA_decomposition_rules.md).

FRAMEWORK STRUCTURE
-------------------
  • Ground cycle = ventricular pump at φ¹ rung (~1.618s), ARA ≈ φ (engine zone).
    This is what the R-R interval IS — every sample t_n is one beat of the pump.
  • Every other oscillator is a subsystem on its own φ-rung with its own ARA.
  • Each subsystem couples to the pump via either:
        Type 1 (handoff)    — adjacent rungs, ARA_coupler ≈ φ
        Type 2 (overflow)   — distant rungs, ARA_coupler ≈ 5
  • Coupler scaling: contribution weight = 1/φ^|k_sub − k_pump|
    (the "log^xPhi" rule — far rungs talk weakly, near rungs talk strongly)

THE HIERARCHICAL FORMULA
------------------------
  RR(t_n) = pump_base_RR
          + pump_amp × wave(ARA_pump, period_pump, t_n)             # the pump itself
          + Σ peer-Type-1: κ₁ × amp × wave(ARA_sub, period_sub, t_n)   # bidirectional
          + Σ slow-Type-2: κ₂ × amp × envelope_overflow(t_n)            # rectified accumulation
          + Σ fast-Type-2: κ₂ × amp × envelope_pulse_train(t_n)         # rectified release

  κ₁ = 1/φ^|Δk|     (Type 1 falls off slowly — strong pair coupling)
  κ₂ = 1/φ^(2|Δk|)  (Type 2 falls off faster — overflow is more diffuse)

The Type-2 envelope is the subsystem's RECTIFIED accumulation phase only — overflow
means the buildup spills into the pump's filling, which is one-directional, not the
full bidirectional wave.
"""

import csv
import math
import os
import sys
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
ECG_CSV = os.path.join(PROJECT_ROOT, "computations", "real_ecg_rr.csv")

PUMP_RUNG = 1                    # φ¹ ≈ 1.618 s — the ventricular pump
PUMP_PERIOD = PHI ** PUMP_RUNG
PUMP_ARA_TARGET = PHI            # engine-zone, sustained-pump default


# =====================================================================
# FORMULA — value_at_times (vectorised, unchanged from v1)
# =====================================================================

def ara_to_T(ara, period):
    T_acc = period / (2 * (1 + ara))
    T_rel = ara * period / (2 * (1 + ara))
    return T_acc, T_rel


def polarity(ara):
    return max(0.0, 1 - abs(ara - 1) / (PHI - 1))


def value_at_times(t, ara, amp, period, t_ref=0.0):
    a = max(0.05, ara)
    pol = polarity(ara)
    T_acc, T_rel = ara_to_T(a, period)
    out = np.zeros_like(t, dtype=float)
    eff = t - t_ref
    x = np.mod(eff, period)
    m1 = x < T_rel
    m2 = (x >= T_rel) & (x < T_rel + T_acc)
    m3 = (x >= T_rel + T_acc) & (x < 2 * T_rel + T_acc)
    m4 = x >= 2 * T_rel + T_acc
    f1 = np.clip(x[m1] / T_rel, 0, 1)
    out[m1] = amp * (1 - np.power(f1, a))
    f2 = np.clip((x[m2] - T_rel) / T_acc, 0, 1)
    out[m2] = -amp * pol * np.power(f2, 1.0 / a)
    f3 = np.clip((x[m3] - T_rel - T_acc) / T_rel, 0, 1)
    out[m3] = -amp * pol * (1 - np.power(f3, a))
    f4 = np.clip((x[m4] - 2 * T_rel - T_acc) / T_acc, 0, 1)
    out[m4] = amp * np.power(f4, 1.0 / a)
    return out


# =====================================================================
# COUPLING CHANNEL RECTIFICATION (Rule 8 + Rule 9)
# =====================================================================

def overflow_envelope(t, ara, amp, period, t_ref=0.0):
    """Type 2 overflow signal. Only the ACCUMULATION phase contributes — overflow
    means the buildup spills sideways into the receiving system; release goes
    elsewhere (back into the source's own ground cycle). So we rectify: keep the
    positive-going accumulation portions, zero out the rest."""
    full = value_at_times(t, ara, amp, period, t_ref=t_ref)
    return np.maximum(full, 0.0)        # keep only positive-going contribution


def coupling_strength(rung_sub, rung_pump=PUMP_RUNG, ctype=1):
    """1/φ^|Δk|·power. Type 1 talks across one rung gracefully (power=1).
    Type 2 falls off twice as fast — overflow is leakier, less directional."""
    dk = abs(rung_sub - rung_pump)
    power = 1 if ctype == 1 else 2
    return PHI ** (-dk * power)


def classify_coupling(rung_sub, rung_pump=PUMP_RUNG):
    """Adjacent rungs (Δk ≤ 1) handoff (Type 1); distant rungs overflow (Type 2)."""
    return 1 if abs(rung_sub - rung_pump) <= 1 else 2


# =====================================================================
# DATA
# =====================================================================

def load_ecg():
    rows = []
    with open(ECG_CSV) as f:
        for r in csv.DictReader(f):
            rows.append((float(r["time_s"]), float(r["rr_ms"])))
    rows.sort(key=lambda x: x[0])
    t = np.array([r[0] for r in rows])
    v = np.array([r[1] for r in rows])
    t = t - t[0]
    return t, v


# =====================================================================
# HIERARCHICAL FIT
# =====================================================================

def search_subsystem_signal(t, residuals, period, ctype, ara_grid=None, tref_grid=None):
    """Search ARA × t_ref for best fit at this period, given coupling type
    (which determines whether we use full wave or rectified envelope)."""
    if ara_grid is None:
        ara_grid = np.linspace(0.1, 2.0, 20)
    if tref_grid is None:
        tref_grid = np.linspace(0, period, 16, endpoint=False)
    best = {"corr": -2.0}
    for ara in ara_grid:
        for tref in tref_grid:
            if ctype == 1:
                pred_unit = value_at_times(t, ara, 1.0, period, t_ref=tref)
            else:
                pred_unit = overflow_envelope(t, ara, 1.0, period, t_ref=tref)
            denom = float(np.sum(pred_unit * pred_unit))
            if denom < 1e-9:
                continue
            amp = float(np.sum(pred_unit * residuals) / denom)
            pred = amp * pred_unit
            if np.std(pred) < 1e-9:
                continue
            corr = float(np.corrcoef(pred, residuals)[0, 1])
            if not np.isfinite(corr):
                continue
            if corr > best["corr"]:
                mae = float(np.mean(np.abs(pred - residuals)))
                best = {"ara": float(ara), "amp": amp,
                        "period": float(period), "t_ref": float(tref),
                        "corr": corr, "mae": mae}
    return best


def map_heart_hierarchical(t, v, candidate_rungs=None, max_subsystems=4, verbose=True):
    centerline = float(np.mean(v))
    residuals = v - centerline

    if candidate_rungs is None:
        # All cardiac-relevant rungs except pump itself (= φ¹).
        candidate_rungs = [-1, 0, 2, 3, 4, 5, 6, 7, 8]

    if verbose:
        print(f"\nGround cycle (pump): rung φ^{PUMP_RUNG} = {PUMP_PERIOD:.3f}s, "
              f"ARA target = {PUMP_ARA_TARGET:.3f}")
        print(f"\nScreening {len(candidate_rungs)} candidate subsystem rungs:")
        print(f"{'rung':>5} {'period(s)':>10} {'type':>5} {'ARA_sub':>9} "
              f"{'amp':>9} {'κ':>7} {'corr':>7}")

    candidates = []
    for k in candidate_rungs:
        period = PHI ** k
        ctype = classify_coupling(k)
        kappa = coupling_strength(k, ctype=ctype)
        # Search the residuals for this subsystem's footprint
        best = search_subsystem_signal(t, residuals, period, ctype)
        best["rung"] = k
        best["ctype"] = ctype
        best["kappa"] = kappa
        candidates.append(best)
        if verbose:
            label = "T1" if ctype == 1 else "T2"
            print(f"{k:>5} {period:>10.4f} {label:>5} {best['ara']:>9.3f} "
                  f"{best['amp']:>9.2f} {kappa:>7.3f} {best['corr']:>+7.3f}")

    # Pick the strongest, separated by rung
    candidates.sort(key=lambda c: abs(c["corr"]), reverse=True)
    chosen = []
    used_rungs = set()
    current_residuals = residuals.copy()
    if verbose:
        print(f"\nSequentially extracting up to {max_subsystems} subsystems:")
    for c in candidates:
        if len(chosen) >= max_subsystems:
            break
        if any(abs(c["rung"] - uk) < 1 for uk in used_rungs):
            continue
        # Re-fit to current residuals
        refit = search_subsystem_signal(t, current_residuals, c["period"], c["ctype"])
        if abs(refit["corr"]) < 0.10:
            continue
        refit["rung"] = c["rung"]
        refit["ctype"] = c["ctype"]
        refit["kappa"] = c["kappa"]
        # Subtract this subsystem's contribution from residuals
        if c["ctype"] == 1:
            pred = value_at_times(t, refit["ara"], refit["amp"], refit["period"],
                                  t_ref=refit["t_ref"])
        else:
            pred = overflow_envelope(t, refit["ara"], refit["amp"], refit["period"],
                                     t_ref=refit["t_ref"])
        current_residuals = current_residuals - pred
        chosen.append(refit)
        used_rungs.add(c["rung"])
        if verbose:
            label = "T1 handoff" if c["ctype"] == 1 else "T2 overflow"
            print(f"  Sub {len(chosen)}: rung φ^{c['rung']:+d} P={refit['period']:.3f}s "
                  f"{label} ARA={refit['ara']:.3f} amp={refit['amp']:.2f} "
                  f"κ={c['kappa']:.3f} corr={refit['corr']:+.3f}")

    # Joint LSQ refit. Each subsystem contributes its own column at strength κ.
    if chosen:
        N = len(chosen)
        X = np.zeros((len(t), N + 1))
        X[:, 0] = 1.0
        for i, s in enumerate(chosen):
            if s["ctype"] == 1:
                col = value_at_times(t, s["ara"], 1.0, s["period"], t_ref=s["t_ref"])
            else:
                col = overflow_envelope(t, s["ara"], 1.0, s["period"], t_ref=s["t_ref"])
            X[:, i + 1] = s["kappa"] * col
        coefs, *_ = np.linalg.lstsq(X, v, rcond=None)
        centerline = float(coefs[0])
        for i, s in enumerate(chosen):
            s["amp_raw"] = float(coefs[i + 1])             # amplitude WITHOUT κ
            s["amp"] = float(coefs[i + 1] * s["kappa"])    # effective contribution
        if verbose:
            print(f"\nJoint LSQ refit: centerline = {centerline:.2f} ms")
            for i, s in enumerate(chosen):
                print(f"  Sub {i+1} (rung φ^{s['rung']:+d}, T{s['ctype']}): "
                      f"amp_raw={s['amp_raw']:.2f}, κ={s['kappa']:.3f} → "
                      f"effective={s['amp']:.2f}")

    # Reconstruct
    full_pred = np.full_like(v, centerline)
    for s in chosen:
        if s["ctype"] == 1:
            sig = value_at_times(t, s["ara"], 1.0, s["period"], t_ref=s["t_ref"])
        else:
            sig = overflow_envelope(t, s["ara"], 1.0, s["period"], t_ref=s["t_ref"])
        full_pred += s["amp_raw"] * s["kappa"] * sig

    final_corr = float(np.corrcoef(full_pred, v)[0, 1]) if np.std(full_pred) > 0 else 0.0
    final_mae = float(np.mean(np.abs(full_pred - v)))

    return {
        "centerline": centerline,
        "subsystems": chosen,
        "full_pred": full_pred,
        "corr": final_corr,
        "mae": final_mae,
    }


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 78)
    print("map_heart_v2.py — Hierarchical heart mapping (subsystems FEED INTO pump)")
    print("=" * 78)

    if not os.path.exists(ECG_CSV):
        print(f"ERROR: {ECG_CSV} not found.")
        sys.exit(1)

    t, v = load_ecg()
    print(f"\nLoaded {len(t)} R-R intervals.")
    print(f"  Time span:  {t[-1]:.2f} sec")
    print(f"  R-R range:  {v.min():.1f} to {v.max():.1f} ms")
    print(f"  R-R mean:   {v.mean():.1f} ms (= {60000/v.mean():.1f} bpm)")
    print(f"  R-R std:    {v.std():.1f} ms")

    result = map_heart_hierarchical(t, v, max_subsystems=4, verbose=True)

    print("\n" + "=" * 78)
    print("THE HEART, MAPPED HIERARCHICALLY")
    print("=" * 78)
    print(f"\nGround cycle (pump): rung φ^{PUMP_RUNG} = {PUMP_PERIOD:.3f}s")
    print(f"Pump baseline R-R: {result['centerline']:.2f} ms ({60000/result['centerline']:.1f} bpm)")

    print(f"\nSubsystems coupling into the pump: {len(result['subsystems'])}")
    for i, s in enumerate(result['subsystems'], 1):
        f = 1.0 / s["period"]
        if f >= 0.15:
            band = "HF (respiratory)"
        elif f >= 0.04:
            band = "LF (sympathovagal)"
        elif f >= 0.0033:
            band = "VLF (slow autonomic)"
        else:
            band = "ULF"
        coupling_label = ("Type 1 handoff (peer-scale, ARA_coupler ≈ φ)"
                          if s["ctype"] == 1
                          else "Type 2 overflow (rung-distant, ARA_coupler ≈ 5)")
        zone = ("near clock" if abs(s["ara"] - 1) < 0.2 else
                "engine zone" if s["ara"] >= PHI - 0.1 else
                "warm engine" if s["ara"] >= 1 else
                "consumer zone")
        print(f"\nSubsystem {i}: rung φ^{s['rung']:+d}  ({band})")
        print(f"  Period:           {s['period']:.3f} s ({f:.4f} Hz)")
        print(f"  Subsystem ARA:    {s['ara']:.3f} ({zone})")
        print(f"  Coupling:         {coupling_label}")
        dk = abs(s['rung'] - PUMP_RUNG)
        power = dk if s['ctype'] == 1 else 2 * dk
        print(f"  Coupler κ:        {s['kappa']:.3f}  (= 1/φ^{power})")
        print(f"  Amp (raw):        {s['amp_raw']:.2f} ms")
        print(f"  Amp × κ:          {s['amp']:.2f} ms peak contribution to pump R-R")
        print(f"  Phase t_ref:      {s['t_ref']:+.3f} s")
        print(f"  Independent corr: {s['corr']:+.4f}")

    print(f"\nCombined fit:")
    print(f"  Correlation:       {result['corr']:+.4f}")
    print(f"  MAE:               {result['mae']:.3f} ms")
    print(f"  Baseline MAE:      {float(np.mean(np.abs(v - v.mean()))):.3f} ms")
    var_explained = 100 * (1 - float(np.var(v - result['full_pred'])) / float(np.var(v)))
    print(f"  Variance explained: {var_explained:.1f}%")

    # Save result
    import json
    out = {
        "version": "v2_hierarchical",
        "pump": {"rung": PUMP_RUNG, "period_s": PUMP_PERIOD,
                 "ARA_target": PUMP_ARA_TARGET,
                 "baseline_RR_ms": result["centerline"],
                 "baseline_bpm": 60000.0 / result["centerline"]},
        "subsystems": result["subsystems"],
        "metrics": {"corr": result["corr"], "mae": result["mae"],
                    "var_explained": var_explained},
        "data_t": [float(x) for x in t],
        "data_v": [float(x) for x in v],
        "pred_v": [float(x) for x in result["full_pred"]],
    }
    out_path = os.path.join(HERE, "heart_map_v2.json")
    with open(out_path, "w") as f:
        json.dump(out, f)
    print(f"\nSaved hierarchical mapping to {out_path}")


if __name__ == "__main__":
    main()
