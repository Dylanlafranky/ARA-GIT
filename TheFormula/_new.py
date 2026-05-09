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


def add_e_event_layer(t, base_pred, v, with_rebound=True, min_run=1, sigma_threshold=1.0):
    residuals = v - base_pred
    events = detect_e_events(t, residuals, min_run=min_run, sigma_threshold=sigma_threshold)
    if not events:
        return {"events": [], "pulses": np.zeros_like(t).tolist(), "pred": base_pred,
                "corr": float(np.corrcoef(base_pred, v)[0, 1]),
                "mae": float(np.mean(np.abs(base_pred - v)))}

    n_events = len(events)
    n_cols = n_events * (2 if with_rebound else 1)
    X = np.zeros((len(t), n_cols))
    INV_PHI3 = 1.0 / (PHI ** 3)
    for j, ev in enumerate(events):
        X[:, j] = event_bell_unit(t, ev) * ev["sign"]
    if with_rebound:
        for j, ev in enumerate(events):
            # Rebound column: AA-boundary 1/φ³ momentum, opposite sign of primary
            X[:, n_events + j] = event_rebound_unit(t, ev) * ev["sign"] * INV_PHI3

    coefs, *_ = np.linalg.lstsq(X, residuals, rcond=None)
    pulses = X @ coefs
    for j, ev in enumerate(events):
        ev["fitted_amp"] = float(coefs[j] * ev["sign"])
        if with_rebound:
            ev["rebound_amp"] = float(coefs[n_events + j] * ev["sign"] * INV_PHI3)
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
    ev_res = add_e_event_layer(t, fit_full['pred'], v, with_rebound=True, min_run=1, sigma_threshold=1.0)
    print("\nfit_with_events_v3 (min_run=1, +1/φ³ rebound):  corr=%+.4f  MAE=%.2f  N=%d" % (ev_res['corr'], ev_res['mae'], len(ev_res['events'])))
    for ev in ev_res['events']:
        rb = ev.get('rebound_amp', 0.0)
        print("  event t=[%6.2f, %6.2f]  n=%2d  resid_peak=%+6.1f  fitted=%+6.1f  rebound=%+6.1f" % (ev['t_start'], ev['t_end'], ev['n_beats'], ev['peak_amp'], ev.get('fitted_amp', 0.0), rb))

    bu_res = add_burst_rhythm(t, fit_full['pred'], v)
    print("\nfit_with_burst   (+ burst rhythm):  corr=%+.4f  MAE=%.2f" % (bu_res['corr'], bu_res['mae']))
    bp = bu_res.get('burst_period')
    if bp:
        log_phi = math.log(bp)/math.log(PHI)
        print("  burst period: %.2fs (~ phi^%.2f)" % (bp, log_phi))
        if bu_res.get('subsystem'):
            s = bu_res['subsystem']
            print("  burst subsystem: ARA=%.2f  amp=%+.1f  t_ref=%.2fs" % (s['ara'], s['amp'], s['t_ref']))

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
    print("\nSaved heart_map_v3.json and heart_map_v3_data.js")


if __name__ == "__main__":
    main()
