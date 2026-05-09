"""
ecg_horizon_aware_test.py

Port the horizon-aware γ_eff + lag-h corrector findings from ENSO to ECG
(single-subject nsr001 RR intervals).

ECG is single-channel — no partner pool — so dynamic per-rung assignment
isn't applicable here. But the two framework-constant interventions are:
  (1) γ_eff(h) = (1/φ^3) × (1/φ)^((h-1)/scale)   — decays at long lead
  (2) horizon-conditional lag-h corrector on the prediction residuals

If the lift pattern matches what we saw on ENSO, that's strong cross-domain
confirmation that the corrections come from framework geometry, not from
ENSO-specific physics.

Strict-causal as before:
  - bandpass per rung from training-only data
  - phase advance deterministic from training state
  - lag-h corrector uses residual from origin t-h (truth fully closed at t)
"""
import json, os, time, sys
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter

PHI = 1.6180339887498949
INV_PHI  = 1/PHI
INV_PHI2 = 1/PHI**2
INV_PHI3 = 1/PHI**3

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\ecg_horizon_aware_data.js")

print("Loading ECG nsr001 RR-interval data...")
df = pd.read_csv(ECG_PATH)
ecg_t = df['time_s'].values
ecg_rr = df['rr_ms'].values
print(f"  {len(df)} beats, {ecg_t[-1]/3600:.2f}h total")

DT = 10.0
t_uniform = np.arange(0, int(ecg_t[-1]) - 1, int(DT))
ecg_signal = np.interp(t_uniform, ecg_t, ecg_rr)
mean_full = float(np.mean(ecg_signal))
ecg_signal = ecg_signal - mean_full
N = len(ecg_signal)
print(f"  Resampled to {DT}s: {N} samples = {N*DT/3600:.2f}h")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
        return lfilter(b, a, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

def read_amp_theta(bp_to_t):
    if len(bp_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]; rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

# ECG rungs in 10s units
RUNGS_K = [k for k in range(8, 21) if PHI**k >= 5*DT and PHI**k < N*DT/3]
RUNGS = [(k, PHI**k / DT) for k in RUNGS_K]
N_RUNGS = len(RUNGS)
K_REF = 19
K_REF_IDX = next((i for i,(k,_) in enumerate(RUNGS) if k == K_REF), N_RUNGS//2)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)
print(f"  Using rungs k={[r[0] for r in RUNGS]} (periods {[f'{r[1]*DT:.0f}s' for r in RUNGS]})")
print(f"  Home rung k={RUNGS[K_REF_IDX][0]} (period {RUNGS[K_REF_IDX][1]*DT:.0f}s ≈ BRAC envelope)")

# Horizons in 10s samples: 6=1min, 30=5min, 180=30min, 360=1h, 720=2h
HORIZONS = [6, 30, 180, 360, 720]
HORIZON_LABELS = {6:'1min', 30:'5min', 180:'30min', 360:'1h', 720:'2h'}

# γ_eff(h) — same φ-decay as ENSO but in ECG time units.
# In ENSO h=1 month was the "tick"; in ECG h=1 sample is 10s.
# To match the ENSO schedule's effective decay shape, use a horizon-in-rungs proxy.
# Choose scale such that h=1 (1 sample, 10s) gives γ near INV_PHI3, h=720 (2h) decays away.
def gamma_phi_h(h_samples):
    # Treat h relative to home rung period (φ^19/DT samples)
    home_period_samples = PHI**K_REF / DT
    # h=home_period -> decay by 1/φ each "home" multiple
    return INV_PHI3 * (INV_PHI ** (h_samples / home_period_samples))

# Horizon-conditional lag-h corrector (mirrors ENSO finding):
# Short lead (h <= ~home/4): +1/φ
# Mid lead (h ~ home/2): +1/φ^2
# Long lead (h ~ home): 0 or small
# Past home: -1/φ^2
home_p = PHI**K_REF / DT
def gamma_corr_h(h_samples):
    if h_samples <= home_p / 8: return +INV_PHI
    if h_samples <= home_p / 2: return +INV_PHI2
    if h_samples <= home_p * 1.5: return 0.0
    return -INV_PHI2

# ===== Vehicle =====
def amp_predict(state, h_samples, last_residual, gamma_fn):
    rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a, th = state[ri]
        new_th = th + 2*np.pi*h_samples/p
        rung_future.append(a * np.cos(new_th))
    own_pred = float(np.dot(RUNG_WEIGHTS, np.array(rung_future)))
    return own_pred + gamma_fn(h_samples) * last_residual

# ===== Rolling test =====
MIN_TRAIN = 3000  # ~8.3h
STEP = 6  # 1-minute refit (10s × 6 = 60s) — gives ~729 origins per horizon

def run(gamma_fn, label):
    print(f"\n--- {label} ---")
    print(f"  γ at h=6 (1min): {gamma_fn(6):.4f}, h=180 (30min): {gamma_fn(180):.4f}, h=720 (2h): {gamma_fn(720):.4f}")
    results = {h: [] for h in HORIZONS}
    last_residual = 0.0
    t0 = time.time()
    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        bp = [causal_bandpass(ecg_signal[:refit_t], p) for k,p in RUNGS]
        state = [read_amp_theta(bp[ri]) for ri in range(N_RUNGS)]
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            pred = amp_predict(state, h, last_residual, gamma_fn)
            truth = ecg_signal[refit_t + h - 1]
            results[h].append((refit_t, pred + mean_full, truth + mean_full))
        if results[6]:
            last_residual = float(results[6][-1][2] - mean_full - (results[6][-1][1] - mean_full))
    print(f"  ran in {time.time()-t0:.1f}s, {len(results[HORIZONS[0]])} origins")
    return results

def metrics(results, label, apply_corrector=False):
    print(f"\n=== {label}{' + horizon-conditional corrector' if apply_corrector else ''} ===")
    print(f"  {'horizon':>9}  {'corr':>7}  {'MAE_ms':>8}  {'R²pers':>8}  {'dir':>7}  n")
    out = {}
    for h in HORIZONS:
        if not results[h]: continue
        rec = np.array(results[h])
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        if apply_corrector:
            g = gamma_corr_h(h)
            o2i = {ot:i for i,ot in enumerate(origins)}
            corr_p = preds.copy()
            if abs(g) > 1e-9:
                for i, t in enumerate(origins):
                    tb = t - h
                    if tb in o2i:
                        corr_p[i] = preds[i] + g * (truths[o2i[tb]] - preds[o2i[tb]])
        else:
            corr_p = preds
        # persistence: last observation at refit_t-1
        pers = ecg_signal[origins-1] + mean_full
        c = float(np.corrcoef(corr_p, truths)[0,1]) if np.std(corr_p)>1e-9 else 0
        mae = float(np.mean(np.abs(corr_p - truths)))
        r2p = float(1 - np.sum((truths-corr_p)**2)/np.sum((truths-pers)**2))
        d = float(np.mean(np.sign(corr_p-pers) == np.sign(truths-pers)))
        print(f"  {HORIZON_LABELS[h]:>9}  {c:+.3f}    {mae:7.2f}    {r2p:+.3f}    {d*100:5.1f}%   {len(rec)}")
        out[HORIZON_LABELS[h]] = dict(corr=c, mae=mae, r2p=r2p, dir=d, n=int(len(rec)),
                                       gamma_corr=gamma_corr_h(h) if apply_corrector else 0)
    return out

# Two runs: BASE (constant γ) and GAMMA_PHI (horizon-aware)
const_results = run(lambda h: INV_PHI3, "BASE — γ=1/φ^3 constant")
phi_results   = run(gamma_phi_h, "GAMMA_PHI — γ_eff(h) decays per φ")

base_metrics = metrics(const_results, "BASE")
base_corr    = metrics(const_results, "BASE", apply_corrector=True)
phi_metrics  = metrics(phi_results,   "GAMMA_PHI")
phi_corr     = metrics(phi_results,   "GAMMA_PHI", apply_corrector=True)

out = dict(method="ECG horizon-aware γ + corrector port from ENSO",
           subject="nsr001 (PhysioNet NSRDB)",
           base=base_metrics, base_with_corrector=base_corr,
           gamma_phi=phi_metrics, gamma_phi_with_corrector=phi_corr)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ECG_HORIZON = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
