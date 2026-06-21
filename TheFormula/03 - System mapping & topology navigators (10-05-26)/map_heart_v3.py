#!/usr/bin/env python3
"""map_heart_v3.py — Run four heart-mapping configurations and compare them."""

import csv, json, math, os
import numpy as np

PHI = (1+math.sqrt(5))/2
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
ECG_CSV = os.path.join(PROJECT_ROOT, "computations", "real_ecg_rr.csv")

PUMP_RUNG = 1
PUMP_PERIOD = PHI ** PUMP_RUNG


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


def load_ecg():
    rows = []
    with open(ECG_CSV) as f:
        for r in csv.DictReader(f):
            rows.append((float(r["time_s"]), float(r["rr_ms"])))
    rows.sort(key=lambda x: x[0])
    t = np.array([r[0] for r in rows]); v = np.array([r[1] for r in rows])
    return t - t[0], v


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


def detect_e_events(t, residuals, min_run=1, sigma_threshold=1.0):
    """Detect runs of consecutive same-sign deviations exceeding threshold.
    min_run=1 catches single-beat spikes; runs link only when next beat exceeds
    half-threshold AND has same sign."""
    sigma = float(np.std(residuals))
    threshold = sigma_threshold * sigma
    events = []
    n = len(residuals); i = 0
    while i < n:
        if abs(residuals[i]) < threshold:
            i += 1; continue
        sign = np.sign(residuals[i]); j = i
        while j < n and np.sign(residuals[j]) == sign and abs(residuals[j]) >= threshold * 0.5:
            j += 1
        if j - i >= min_run:
            run_t = t[i:j]; run_v = residuals[i:j]
            duration = float(run_t[-1] - run_t[0]) if j-i > 1 else 0.0
            events.append({
                "t_start": float(run_t[0]), "t_end": float(run_t[-1]),
                "t_peak": float(run_t[np.argmax(np.abs(run_v))]),
                "peak_amp": float(run_v[np.argmax(np.abs(run_v))]),
                "sign": int(sign), "n_beats": int(j - i),
                "duration_s": duration,
            })
        i = j
    return events


def event_bell_unit(t, event, sharpness=PHI):
    """Unit-amplitude bell. For single-beat events use a narrow pulse centred
    on t_peak with width = mean dt; otherwise width = duration/2."""
    if event["n_beats"] <= 1:
        # Narrow pulse — width is the local beat spacing (~ 0.7s)
        half = 0.7
    else:
        half = max(1.0, event["duration_s"]) * 0.5
    delta = (t - event["t_peak"]) / half
    return np.maximum(0.0, np.cos(np.pi * delta / 2.0)) ** sharpness


def event_rebound_unit(t, event, sharpness=PHI):
    """1/φ³ rebound term — AA-boundary momentum: cycle following the event
    inherits a 1/φ³ deviation in the OPPOSITE direction. Centred one beat
    after t_end, width similar to event but opposite sign baked in."""
    half = 0.7 if event["n_beats"] <= 1 else max(1.0, event["duration_s"]) * 0.5
    rebound_centre = event["t_end"] + half  # one event-width after the end
    delta = (t - rebound_centre) / half
    bell = np.maximum(0.0, np.cos(np.pi * delta / 2.0)) ** sharpness
    return -bell  # opposite sign by construction


def event_peak_booster_unit(t, event, sharpness=PHI**3):
    """Narrow peak-booster bell — captures continuous feedback compounding
    within sustained events. φ³-sharp narrows the bell to ~1/3 the width of
    the primary, so LSQ can boost peak height independently of run duration."""
    half = 0.7 if event["n_beats"] <= 1 else max(1.0, event["duration_s"]) * 0.5
    delta = (t - event["t_peak"]) / half
    return np.maximum(0.0, np.cos(np.pi * delta / 2.0)) ** sharpness


def event_compound_unit(t, event, growth=PHI):
    """Per-beat exponential compounding within an event run.
    Each beat k from t_start has weight growth^k during the BUILD phase
    (k=0 at start, k=n_peak at the peak), and growth^(2·n_peak - k) during
    DECAY (geometric ramp, peaking at the actual peak position).
    Then convolved with a narrow Gaussian per beat to produce a smooth field.
    For single-beat events, falls back to a sharp peak bell."""
    n = event["n_beats"]
    if n <= 1:
        # Same as peak booster — single-beat events have nothing to compound
        half = 0.7
        delta = (t - event["t_peak"]) / half
        return np.maximum(0.0, np.cos(np.pi * delta / 2.0)) ** (PHI ** 3)

    # Estimate beat positions: evenly spaced from t_start to t_end
    beat_times = np.linspace(event["t_start"], event["t_end"], n)
    # Identify which beat is closest to the recorded peak
    k_peak = int(np.argmin(np.abs(beat_times - event["t_peak"])))

    # Per-beat geometric weight, peaking at k_peak
    weights = np.zeros(n, dtype=float)
    for k in range(n):
        if k <= k_peak:
            weights[k] = growth ** k                  # build: 1, φ, φ², ...
        else:
            weights[k] = growth ** (2 * k_peak - k)   # decay: same envelope mirrored

    # Per-beat Gaussian width — narrow enough that beats don't overlap excessively
    if n > 1:
        beat_dt = (event["t_end"] - event["t_start"]) / max(1, n - 1)
    else:
        beat_dt = 0.7
    sigma = max(0.25, beat_dt * 0.5)

    # Sum of weighted Gaussians at each beat position
    out = np.zeros_like(t, dtype=float)
    for k in range(n):
        out += weights[k] * np.exp(-((t - beat_times[k]) / sigma) ** 2)

    # Normalise so peak is 1 — LSQ controls absolute amplitude
    peak = float(out.max())
    if peak > 1e-9:
        out = out / peak
    return out


def add_e_event_layer(t, base_pred, v, with_rebound=True, with_peak_boost=False,
                       with_compound=False, min_run=1, sigma_threshold=1.0):
    residuals = v - base_pred
    events = detect_e_events(t, residuals, min_run=min_run, sigma_threshold=sigma_threshold)
    if not events:
        return {"events": [], "pulses": np.zeros_like(t).tolist(), "pred": base_pred,
                "corr": float(np.corrcoef(base_pred, v)[0, 1]),
                "mae": float(np.mean(np.abs(base_pred - v)))}

    n_events = len(events)
    n_terms = 1 + (1 if with_rebound else 0) + (1 if with_peak_boost else 0) + (1 if with_compound else 0)
    n_cols = n_events * n_terms
    X = np.zeros((len(t), n_cols))
    INV_PHI3 = 1.0 / (PHI ** 3)
    col = 0
    # Primary bell
    for j, ev in enumerate(events):
        X[:, col] = event_bell_unit(t, ev) * ev["sign"]
        col += 1
    if with_rebound:
        for j, ev in enumerate(events):
            X[:, col] = event_rebound_unit(t, ev) * ev["sign"] * INV_PHI3
            col += 1
    if with_peak_boost:
        for j, ev in enumerate(events):
            X[:, col] = event_peak_booster_unit(t, ev) * ev["sign"]
            col += 1
    if with_compound:
        for j, ev in enumerate(events):
            X[:, col] = event_compound_unit(t, ev) * ev["sign"]
            col += 1

    coefs, *_ = np.linalg.lstsq(X, residuals, rcond=None)
    pulses = X @ coefs
    offset = 0
    for j, ev in enumerate(events):
        ev["fitted_amp"] = float(coefs[offset + j] * ev["sign"])
    offset += n_events
    if with_rebound:
        for j, ev in enumerate(events):
            ev["rebound_amp"] = float(coefs[offset + j] * ev["sign"] * INV_PHI3)
        offset += n_events
    if with_peak_boost:
        for j, ev in enumerate(events):
            ev["peak_boost_amp"] = float(coefs[offset + j] * ev["sign"])
        offset += n_events
    if with_compound:
        for j, ev in enumerate(events):
            ev["compound_amp"] = float(coefs[offset + j] * ev["sign"])

    pred = base_pred + pulses
    return {"events": events, "pulses": pulses.tolist(), "pred": pred,
            "corr": float(np.corrcoef(pred, v)[0, 1]) if pred.std() > 0 else 0.0,
            "mae": float(np.mean(np.abs(pred - v)))}


def add_burst_rhythm(t, base_pred, v):
    residuals = v - base_pred
    envelope = np.abs(residuals)
    dt = float(np.mean(np.diff(t))); n = len(envelope)
    fft_vals = np.fft.rfft(envelope - envelope.mean())
    fft_freqs = np.fft.rfftfreq(n, d=dt)
    mask = (fft_freqs >= 1.0/60.0) & (fft_freqs <= 1.0/10.0)
    if not mask.any():
        return {"burst_period": None, "pred": base_pred, "subsystem": None,
                "pulses": [0.0]*len(t),
                "corr": float(np.corrcoef(base_pred, v)[0, 1]),
                "mae": float(np.mean(np.abs(base_pred - v)))}
    fft_amp = np.abs(fft_vals)
    fft_amp_masked = np.where(mask, fft_amp, 0)
    idx = np.argmax(fft_amp_masked)
    burst_freq = float(fft_freqs[idx])
    burst_period = 1.0 / burst_freq if burst_freq > 0 else None
    if burst_period is None:
        return {"burst_period": None, "pred": base_pred, "subsystem": None,
                "pulses": [0.0]*len(t),
                "corr": float(np.corrcoef(base_pred, v)[0, 1]),
                "mae": float(np.mean(np.abs(base_pred - v)))}
    best = search_subsystem(t, residuals, burst_period, ctype=2)
    sig = overflow_envelope(t, best["ara"], best["amp"], burst_period, best["t_ref"])
    pred = base_pred + sig
    return {"burst_period": burst_period, "burst_freq": burst_freq,
            "subsystem": {**best, "period": burst_period},
            "pulses": sig.tolist(), "pred": pred,
            "corr": float(np.corrcoef(pred, v)[0, 1]) if pred.std() > 0 else 0.0,
            "mae": float(np.mean(np.abs(pred - v)))}


def main():
    t, v = load_ecg()
    print("Loaded %d R-R intervals; range %.0f-%.0f ms, std %.1f ms" % (len(t), v.min(), v.max(), v.std()))

    rungs = [-1, 0, 2, 3, 4, 5, 6, 7, 8]

    fit_default = fit_subsystems(t, v, rungs, max_subsystems=4, allow_neighbours=False)
    print("\nfit_default      (no-neighbour, <=4 sub):  corr=%+.4f  MAE=%.2f" % (fit_default['corr'], fit_default['mae']))
    for s in fit_default['subsystems']:
        print("  rung phi^%+d  T%d  P=%6.2fs  ARA=%.2f  amp=%+6.1f" % (s['rung'], s['ctype'], s['period'], s['ara'], s['amp']))

    fit_full = fit_subsystems(t, v, rungs, max_subsystems=6, allow_neighbours=True)
    print("\nfit_full_ladder  (neighbours allowed, <=6 sub):  corr=%+.4f  MAE=%.2f" % (fit_full['corr'], fit_full['mae']))
    for s in fit_full['subsystems']:
        print("  rung phi^%+d  T%d  P=%6.2fs  ARA=%.2f  amp=%+6.1f" % (s['rung'], s['ctype'], s['period'], s['ara'], s['amp']))

    # Original (min_run=3) for comparison
    ev_res_old = add_e_event_layer(t, fit_full['pred'], v, with_rebound=False, min_run=3, sigma_threshold=0.8)
    print("\nfit_with_events_v1 (min_run=3, no rebound):  corr=%+.4f  MAE=%.2f  N=%d" % (ev_res_old['corr'], ev_res_old['mae'], len(ev_res_old['events'])))

    # Wider (min_run=1) — catches all spikes
    ev_res_wide = add_e_event_layer(t, fit_full['pred'], v, with_rebound=False, min_run=1, sigma_threshold=1.0)
    print("\nfit_with_events_v2 (min_run=1, no rebound):  corr=%+.4f  MAE=%.2f  N=%d" % (ev_res_wide['corr'], ev_res_wide['mae'], len(ev_res_wide['events'])))

    # Wider + 1/φ³ rebound
    ev_res = add_e_event_layer(t, fit_full['pred'], v, with_rebound=True,
                                with_peak_boost=False, min_run=1, sigma_threshold=1.0)
    print("\nfit_with_events_v3 (min_run=1, +1/φ³ rebound):  corr=%+.4f  MAE=%.2f  N=%d" % (ev_res['corr'], ev_res['mae'], len(ev_res['events'])))

    # v4: rebound + peak booster (continuous feedback)
    ev_res_v4 = add_e_event_layer(t, fit_full['pred'], v, with_rebound=True,
                                   with_peak_boost=True, with_compound=False,
                                   min_run=1, sigma_threshold=1.0)
    print("\nfit_with_events_v4 (+ peak booster φ³-sharp):  corr=%+.4f  MAE=%.2f  N=%d" % (ev_res_v4['corr'], ev_res_v4['mae'], len(ev_res_v4['events'])))

    # v5: + per-beat exponential compounding (geometric ramp within run)
    ev_res_v5 = add_e_event_layer(t, fit_full['pred'], v, with_rebound=True,
                                   with_peak_boost=True, with_compound=True,
                                   min_run=1, sigma_threshold=1.0)
    print("\nfit_with_events_v5 (+ φ-compound per beat):  corr=%+.4f  MAE=%.2f  N=%d" % (ev_res_v5['corr'], ev_res_v5['mae'], len(ev_res_v5['events'])))
    print("\nfit_with_events_v5 (+ phi-compound per beat):  corr=%+.4f  MAE=%.2f  N=%d" % (ev_res_v5['corr'], ev_res_v5['mae'], len(ev_res_v5['events'])))

    bu_res = add_burst_rhythm(t, fit_full['pred'], v)
    print("\nfit_with_burst   (+ burst rhythm):  corr=%+.4f  MAE=%.2f" % (bu_res['corr'], bu_res['mae']))
    bp = bu_res.get('burst_period')
    if bp:
        log_phi = math.log(bp)/math.log(PHI)
        print("  burst period: %.2fs (~ phi^%.2f)" % (bp, log_phi))

    out = {
        "data_t": t.tolist(),
        "data_v": v.tolist(),
        "centerline": fit_default['centerline'],
        "fits": {
            "default": {"pred": fit_default['pred'].tolist(), "corr": fit_default['corr'],
                        "mae": fit_default['mae'], "subsystems": fit_default['subsystems']},
            "full_ladder": {"pred": fit_full['pred'].tolist(), "corr": fit_full['corr'],
                            "mae": fit_full['mae'], "subsystems": fit_full['subsystems']},
            "events_v1": {"pred": ev_res_old['pred'].tolist(), "corr": ev_res_old['corr'],
                          "mae": ev_res_old['mae'], "events": ev_res_old['events'],
                          "pulses": ev_res_old['pulses']},
            "events_v2": {"pred": ev_res_wide['pred'].tolist(), "corr": ev_res_wide['corr'],
                          "mae": ev_res_wide['mae'], "events": ev_res_wide['events'],
                          "pulses": ev_res_wide['pulses']},
            "events_v3": {"pred": ev_res['pred'].tolist(), "corr": ev_res['corr'],
                          "mae": ev_res['mae'], "events": ev_res['events'],
                          "pulses": ev_res['pulses']},
            "events_v4": {"pred": ev_res_v4['pred'].tolist(), "corr": ev_res_v4['corr'],
                          "mae": ev_res_v4['mae'], "events": ev_res_v4['events'],
                          "pulses": ev_res_v4['pulses']},
            "events_v5": {"pred": ev_res_v5['pred'].tolist(), "corr": ev_res_v5['corr'],
                          "mae": ev_res_v5['mae'], "events": ev_res_v5['events'],
                          "pulses": ev_res_v5['pulses']},
            "with_burst": {"pred": bu_res['pred'].tolist(), "corr": bu_res['corr'],
                           "mae": bu_res['mae'],
                           "burst_period_s": bu_res.get('burst_period'),
                           "burst_subsystem": bu_res.get('subsystem'),
                           "pulses": bu_res.get('pulses', [0.0]*len(t))},
        },
    }
    with open(os.path.join(HERE, "heart_map_v3.json"), "w") as f:
        json.dump(out, f)
    with open(os.path.join(HERE, "heart_map_v3_data.js"), "w") as f:
        f.write("window.HEART_DATA_V3 = ")
        json.dump(out, f)
        f.write(";")
    print("\nSaved heart_map_v3.json and heart_map_v3_data.js")


if __name__ == "__main__":
    main()
