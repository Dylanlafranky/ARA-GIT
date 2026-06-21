#!/usr/bin/env python3
"""
map_heart_v3.py — Run four heart-mapping configurations and compare them.

  fit_default      : current 4-subsystem fit with no-neighbour guard (= v2)
  fit_full_ladder  : same engine but allows ALL φ-rungs including neighbours,
                     up to 6 subsystems
  fit_with_events  : full-ladder + E-event layer (discrete displacement-correction
                     pulses on consecutive same-sign deviation runs)
  fit_with_burst   : full-ladder + burst-rhythm component derived from the
                     dominant period of |residual| envelope
"""

import csv, json, math, os, sys
import numpy as np

PHI = (1+math.sqrt(5))/2
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
ECG_CSV = os.path.join(PROJECT_ROOT, "computations", "real_ecg_rr.csv")

PUMP_RUNG = 1
PUMP_PERIOD = PHI ** PUMP_RUNG


# ============================================================
# Formula
# ============================================================

def ara_to_T(ara, period):
    return period/(2*(1+ara)), ara*period/(2*(1+ara))

def polarity(ara):
    return max(0.0, 1 - abs(ara - 1)/(PHI - 1))

def value_at_times(t, ara, amp, period, t_ref=0.0):
    a = max(0.05, ara); pol = polarity(ara)
    T_acc, T_rel = ara_to_T(a, period)
    out = np.zeros_like(t, dtype=float)
    x = np.mod(t - t_ref, period)
    m1 = x < T_rel
    m2 = (x >= T_rel) & (x < T_rel + T_acc)
    m3 = (x >= T_rel + T_acc) & (x < 2*T_rel + T_acc)
    m4 = x >= 2*T_rel + T_acc
    out[m1] = amp * (1 - np.power(np.clip(x[m1]/T_rel, 0, 1), a))
    out[m2] = -amp * pol * np.power(np.clip((x[m2]-T_rel)/T_acc, 0, 1), 1.0/a)
    out[m3] = -amp * pol * (1 - np.power(np.clip((x[m3]-T_rel-T_acc)/T_rel, 0, 1), a))
    out[m4] = amp * np.power(np.clip((x[m4]-2*T_rel-T_acc)/T_acc, 0, 1), 1.0/a)
    return out

def overflow_envelope(t, ara, amp, period, t_ref=0.0):
    return np.maximum(value_at_times(t, ara, amp, period, t_ref), 0.0)

def coupling_strength(rung_sub, ctype=1):
    dk = abs(rung_sub - PUMP_RUNG)
    return PHI ** (-dk * (1 if ctype == 1 else 2))

def classify_coupling(rung_sub):
    return 1 if abs(rung_sub - PUMP_RUNG) <= 1 else 2


# ============================================================
# Data
# ============================================================

def load_ecg():
    rows = []
    with open(ECG_CSV) as f:
        for r in csv.DictReader(f):
            rows.append((float(r["time_s"]), float(r["rr_ms"])))
    rows.sort(key=lambda x: x[0])
    t = np.array([r[0] for r in rows]); v = np.array([r[1] for r in rows])
    return t - t[0], v


# ============================================================
# Subsystem fitting
# ============================================================

def search_subsystem(t, residuals, period, ctype, ara_grid=None, tref_grid=None):
    if ara_grid is None: ara_grid = np.linspace(0.1, 2.0, 20)
    if tref_grid is None: tref_grid = np.linspace(0, period, 16, endpoint=False)
    best = {"corr": -2.0}
    for ara in ara_grid:
        for tref in tref_grid:
            sig = (value_at_times(t, ara, 1.0, period, tref) if ctype == 1
                   else overflow_envelope(t, ara, 1.0, period, tref))
            denom = float(np.sum(sig*sig))
            if denom < 1e-9: continue
            amp = float(np.sum(sig*residuals)/denom)
            pred = amp*sig
            if pred.std() < 1e-9: continue
            corr = float(np.corrcoef(pred, residuals)[0, 1])
            if not np.isfinite(corr): continue
            if corr > best["corr"]:
                best = {"ara": float(ara), "amp": amp, "period": float(period),
                        "t_ref": float(tref), "corr": corr,
                        "mae": float(np.mean(np.abs(pred-residuals)))}
    return best


def fit_subsystems(t, v, candidate_rungs, max_subsystems, allow_neighbours=False):
    """Greedy + joint-LSQ refit. allow_neighbours skips the rung-spacing guard."""
    centerline = float(np.mean(v))
    residuals = v - centerline
    candidates = []
    for k in candidate_rungs:
        period = PHI**k; ctype = classify_coupling(k); kappa = coupling_strength(k, ctype)
        best = search_subsystem(t, residuals, period, ctype)
        best["rung"] = k; best["ctype"] = ctype; best["kappa"] = kappa
        candidates.append(best)
    candidates.sort(key=lambda c: abs(c["corr"]), reverse=True)

    chosen, used_rungs, current_residuals = [], set(), residuals.copy()
    for c in candidates:
        if len(chosen) >= max_subsystems: break
        if not allow_neighbours and any(abs(c["rung"] - uk) < 1 for uk in used_rungs):
            continue
        refit = search_subsystem(t, current_residuals, c["period"], c["ctype"])
        if abs(refit["corr"]) < 0.10: continue
        refit["rung"] = c["rung"]; refit["ctype"] = c["ctype"]; refit["kappa"] = c["kappa"]
        sig_fn = value_at_times if c["ctype"] == 1 else overflow_envelope
        current_residuals -= sig_fn(t, refit["ara"], refit["amp"], refit["period"], refit["t_ref"])
        chosen.append(refit); used_rungs.add(c["rung"])

    if chosen:
        N = len(chosen); X = np.zeros((len(t), N+1))
        X[:, 0] = 1.0
        for i, s in enumerate(chosen):
            sig_fn = value_at_times if s["ctype"] == 1 else overflow_envelope
            X[:, i+1] = s["kappa"] * sig_fn(t, s["ara"], 1.0, s["period"], s["t_ref"])
        coefs, *_ = np.linalg.lstsq(X, v, rcond=None)
        centerline = float(coefs[0])
        for i, s in enumerate(chosen):
            s["amp_raw"] = float(coefs[i+1])
            s["amp"] = float(coefs[i+1] * s["kappa"])

    pred = np.full_like(v, centerline)
    for s in chosen:
        sig_fn = value_at_times if s["ctype"] == 1 else overflow_envelope
        pred += s["amp_raw"] * s["kappa"] * sig_fn(t, s["ara"], 1.0, s["period"], s["t_ref"])

    return {"centerline": centerline, "subsystems": chosen, "pred": pred,
            "corr": float(np.corrcoef(pred, v)[0, 1]) if pred.std() > 0 else 0.0,
            "mae": float(np.mean(np.abs(pred - v)))}


# ============================================================
# E-event layer
# ============================================================

def detect_e_events(t, residuals, min_run=4, sigma_threshold=1.0):
    """Find runs of >= min_run consecutive same-sign deviations exceeding
    sigma_threshold × σ_residual. Each run becomes one E-event."""
    sigma = float(np.std(residuals))
    threshold = sigma_threshold * sigma
    events = []
    n = len(residuals)
    i = 0
    while i < n:
        if abs(residuals[i]) < threshold:
            i += 1
            continue
        sign = np.sign(residuals[i])
        j = i
        while j < n and np.sign(residuals[j]) == sign and abs(residuals[j]) >= threshold * 0.5:
            j += 1
        if j - i >= min_run:
            run_t = t[i:j]
            run_v = residuals[i:j]
            events.append({
                "t_start": float(run_t[0]),
                "t_end": float(run_t[-1]),
                "t_peak": float(run_t[np.argmax(np.abs(run_v))]),
                "peak_amp": float(run_v[np.argmax(np.abs(run_v))]),
                "sign": int(sign),
                "n_beats": int(j - i),
                "duration_s": float(run_t[-1] - run_t[0]),
            })
        i = j
    return events


def event_bell_unit(t, event, sharpness=PHI):
    """Unit-amplitude (peak=1) framework-shaped pulse centred on event peak."""
    half = max(1.0, event["duration_s"]) * 0.5
    delta = (t - event["t_peak"]) / half
    return np.maximum(0.0, np.cos(np.pi * delta / 2.0)) ** sharpness


def add_e_event_layer(t, base_pred, v):
    """Detect E-events on residuals, LSQ-fit each event's amplitude jointly."""
    residuals = v - base_pred
    events = detect_e_events(t, residuals, min_run=3, sigma_threshold=0.8)
    if not events:
        return {"events": [], "pulses": np.zeros_like(t), "pred": base_pred,
                "corr": float(np.corrcoef(base_pred, v)[0, 1]),
                "mae": float(np.mean(np.abs(base_pred - v)))}
    # Build basis matrix: one column per event (sign-aware unit bell).
    # Joint LSQ on residuals → fits all event amplitudes simultaneously.
    X = np.zeros((len(t), len(events)))
    for j, ev in enumerate(events):
        X[:, j] = event_bell_unit(t, ev) * ev["sign"]
    coefs, *_ = np.linalg.lstsq(X, residuals, rcond=None)
    pulses = X @ coefs
    for j, ev in enumerate(events):
        ev["fitted_amp"] = float(coefs[j] * ev["sign"])
    pred = base_pred + pulses
    return {"events": events, "pulses": pulses, "pred": pred,
            "corr": float(np.corrcoef(pred, v)[0, 1]) if pred.std() > 0 else 0.0,
            "mae": float(np.mean(np.abs(pred - v)))}


# ============================================================
# Burst rhythm — dominant envelope frequency
# ============================================================

def add_burst_rhythm(t, base_pred, v):
    """Find the dominant frequency in |residual| envelope and add a
    matched subsystem at that period."""
    residuals = v - base_pred
    envelope = np.abs(residuals)

    # Estimate dominant period via FFT (assumes uniform-ish sampling, which beat
    # series isn't perfectly — but t is monotonically increasing, average dt ≈ 0.72s)
    dt = float(np.mean(np.diff(t)))
    n = len(envelope)
    fft_vals = np.fft.rfft(envelope - envelope.mean())
    fft_freqs = np.fft.rfftfreq(n, d=dt)

    # Restrict to physically plausible burst-spacings (10s to 60s)
    mask = (fft_freqs >= 1.0/60.0) & (fft_freqs <= 1.0/10.0)
    if not mask.any():
        return {"burst_period": None, "pred": base_pred, "subsystem": None,
                "corr": float(np.corrcoef(base_pred, v)[0, 1]),
                "mae": float(np.mean(np.abs(base_pred - v)))}

    fft_amp = np.abs(fft_vals)
    fft_amp_masked = np.where(mask, fft_amp, 0)
    idx = np.argmax(fft_amp_masked)
    burst_freq = float(fft_freqs[idx])
    burst_period = 1.0 / burst_freq if burst_freq > 0 else None

    if burst_period is None:
        return {"burst_period": None, "pred": base_pred, "subsystem": None,
                "corr": float(np.corrcoef(base_pred, v)[0, 1]),
                "mae": float(np.mean(np.abs(base_pred - v)))}

    # Fit a Type-2 overflow subsystem at this exact period
    best = search_subsystem(t, residuals, burst_period, ctype=2)
    sig = overflow_envelope(t, best["ara"], best["amp"], burst_period, best["t_ref"])
    pred = base_pred + sig
    return {"burst_period": burst_period, "burst_freq": burst_freq,
            "subsystem": {**best, "period": burst_period},
            "pulses": sig, "pred": pred,
            "corr": float(np.corrcoef(pred, v)[0, 1]) if pred.std() > 0 else 0.0,
            "mae": float(np.mean(np.abs(pred - v)))}


# ============================================================
# Driver
# ============================================================

def main():
    t, v = load_ecg()
    print(f"Loaded {len(t)} R-R intervals; range {v.min():.0f}-{v.max():.0f} ms, std {v.std():.1f} ms\n")

    rungs = [-1, 0, 2, 3, 4, 5, 6, 7, 8]

    # 1) fit_default — current v2 (no neighbours)
    fit_default = fit_subsystems(t, v, rungs, max_subsystems=4, allow_neighbours=False)
    print("=" * 70)
    print(f"fit_default         (no-neighbour guard, ≤4 sub):  corr={fit_default['corr']:+.4f}  MAE={fit_default['mae']:.2f}")
    for s in fit_default['subsystems']:
        print(f"  rung φ^{s['rung']:+d}  T{s['ctype']}  P={s['period']:6.2f}s  ARA={s['ara']:.2f}  amp={s['amp']:+6.1f}")

    # 2) fit_full_ladder — neighbours allowed, more subsystems
    fit_full = fit_subsystems(t, v, rungs, max_subsystems=6, allow_neighbours=True)
    print(f"\nfit_full_ladder     (neighbours allowed, ≤6 sub):  corr={fit_full['corr']:+.4f}  MAE={fit_full['mae']:.2f}")
    for s in fit_full['subsystems']:
        print(f"  rung φ^{s['rung']:+d}  T{s['ctype']}  P={s['period']:6.2f}s  ARA={s['ara']:.2f}  amp={s['amp']:+6.1f}")

    # 3) fit_with_events — full ladder + E-events
    ev_res = add_e_event_layer(t, fit_full['pred'], v)
    print(f"\nfit_with_events     (+ {len(ev_res['events'])} E-events):  corr={ev_res['corr']:+.4f}  MAE={ev_res['mae']:.2f}")
    for ev in ev_res['events']:
        fitted = ev.get('fitted_amp', 0.0)
        print(f"  event  t∈[{ev['t_start']:6.2f}, {ev['t_end']:6.2f}]  n={ev['n_beats']:2d}  resid_peak={ev['peak_amp']:+6.1f}  fitted_amp={fitted:+6.1f}")

    # 4) fit_with_burst — full ladder + dominant envelope freq
    bu_res = add_burst_rhythm(t, fit_full['pred'], v)
    bp = bu_res.get('burst_period')
    print(f"\nfit_with_burst      (+ burst rhythm):  corr={bu_res['corr']:+.4f}  MAE={bu_res['mae']:.2f}")
    if bp:
        # Closest φ-rung to the discovered burst period
        log_phi = math.log(bp)/math.log(PHI)
        print(f"  burst period: {bp:.2f}s (≈ φ^{log_phi:.2f})")
        if bu_res.get('subsystem'):
            s = bu_res['subsystem']
            print(f"  burst subsystem: ARA={s['ara']:.2f}  amp={s['amp']:+.1f}  t_ref={s['t_ref']:.2f}s")

    # ===== Save all four for the viewer =====
    out = {
        "data_t": t.tolist(), "data_v": v.tolist(),
        "centerline": fit_default['centerline'],
        "fits": {
            "default":     {"pred": fit_default['pred'].tolist(), "corr": fit_default['corr'],
                            "mae": fit_default['mae'], "subsystems": fit_default['subsystems']},
            "full_ladder": {"pred": fit_full['pred'].tolist(),    "corr": fit_full['corr'],
                            "mae": fit_full['mae'], "subsystems": fit_full['subsystems']},
            "with_events": {"pred": ev_res['pred'].tolist(),      "corr": ev_res['corr'],
                            "mae": ev_res['mae'], "events": ev_res['events']},
            "full_ladder": {"pred": fit_full['pred'].tolist(),    "corr": fit_full['corr'],
                            "mae": fit_full['mae'], "subsystems": fit_full['subsystems']},
            "with_events": {"pred": ev_res['pred'].tolist(),      "corr": ev_res['corr'],
                            "mae": ev_res['mae'], "events": ev_res['events']},
            "with_burst":  {"pred": bu_res['pred'].tolist(),      "corr": bu_res['corr'],
                            "mae": bu_res['mae'],
                            "burst_period_s": bu_res.get('burst_period'),
                            "burst_subsystem": bu_res.get('subsystem')},
        },
    }
    with open(os.path.join(HERE, "heart_map_v3.json"), "w") as f:
        json.dump(out, f)
    with open(os.path.join(HERE, "heart_map_v3_data.js"), "w") as f:
        f.write("window.HEART_DATA_V3 = "); json.dump(out, f); f.write(";")
    print("\nSaved heart_map_v3.json and heart_map_v3_data.js")


if __name__ == "__main__":
    main()
