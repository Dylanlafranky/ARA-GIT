"""
Rolling vehicle test — runs the framework's actual mechanics forward.

NOT regression on bandpass features. The vehicle:
  At each refit time t, compute each rung's CURRENT amplitude and phase
  from causal bandpass on training data only. Then forward-step each rung
  as a deterministic oscillator. Sum across rungs to predict NINO[t+h].

V0: equal-weight rung sum (each rung extrapolated as A·cos(ωt+θ))
V1: V0 + per-rung weights learned from training data (causal)
V2: V1 + ARA-driven amplitude decay

DATA: NOAA Niño 3.4.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_data.js")

print("Loading NINO 3.4...")
df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df['date'] = pd.to_datetime(df['date'].str.strip())
df = df[df['val'] > -90].copy()
df['date'] = df['date'].dt.to_period('M').dt.to_timestamp()
df = df.groupby('date').first().reset_index().sort_values('date')
NINO = df['val'].values.astype(float)
DATES = df['date'].values
N = len(NINO)
print(f"  N={N} months, {pd.Timestamp(DATES[0]).date()} to {pd.Timestamp(DATES[-1]).date()}")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr)
    f_c = 1.0/period_units
    nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq)
    Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
        return lfilter(b, a, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)

def read_rung_state(bp_train_to_t):
    """Read amplitude and phase at end of bp_train_to_t."""
    if len(bp_train_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_train_to_t))
    recent = bp_train_to_t[-n_recent:]
    amp = float(np.std(recent) * np.sqrt(2)) + 1e-9
    last = bp_train_to_t[-1]
    rate = bp_train_to_t[-1] - bp_train_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    theta = np.arccos(ratio) * (-1 if rate > 0 else 1)
    return amp, theta

def vehicle_forward_value(amp, theta, period, dt_months, decay_rate=0.0):
    """Project forward dt_months: A·cos(θ + 2π·dt/period) × decay."""
    new_theta = theta + 2*np.pi*dt_months/period
    new_amp = amp * np.exp(-decay_rate * dt_months)
    return new_amp * np.cos(new_theta)

# ===== Rolling loop =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12  # 30 years
STEP = 12  # refit yearly

print(f"\n  Rolling: refit every {STEP} months, min_train={MIN_TRAIN}, horizons={HORIZONS}")

results_by_variant = {}
forecasts_by_variant = {}

for variant in ['V0', 'V1', 'V2']:
    decay_rate = 0.005 if variant == 'V2' else 0.0
    print(f"\n--- Vehicle {variant} (decay={decay_rate}) ---")
    results = {h: [] for h in HORIZONS}
    t_start = time.time()

    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        arr_train = NINO[:refit_t]
        mean_train = float(np.mean(arr_train))

        # Compute causal bandpass for each rung over the training data ONCE
        bp_per_rung = []
        for k, p in RUNGS:
            bp_per_rung.append(causal_bandpass(arr_train, p))

        # Read state at end of training data
        rung_amps = []; rung_thetas = []
        for i, bp in enumerate(bp_per_rung):
            a, th = read_rung_state(bp)
            rung_amps.append(a); rung_thetas.append(th)

        # V1/V2: fit per-rung weights using bandpass values themselves as features
        # X[t] = [bp_rung_0(t), bp_rung_1(t), ...] for t in training window
        # y[t] = NINO[t] - mean_train
        if variant in ('V1', 'V2'):
            # Skip first ~max period to avoid filter warm-up
            warm = max(50, int(2*RUNGS[-1][1]))  # ~2× longest period? too long; keep modest
            warm = min(warm, refit_t - 100)
            if warm < refit_t:
                rows = []; ys = []
                for t in range(warm, refit_t):
                    rows.append([bp_per_rung[i][t] for i in range(N_RUNGS)])
                    ys.append(NINO[t] - mean_train)
                X = np.array(rows); y = np.array(ys)
                ridge = 5.0
                A = X.T @ X + ridge*np.eye(N_RUNGS)
                weights = np.linalg.solve(A, X.T @ y)
            else:
                weights = np.ones(N_RUNGS) / N_RUNGS
        else:
            weights = np.ones(N_RUNGS) / N_RUNGS  # equal weight

        # Forward predict at each horizon
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            future_vals = np.array([
                vehicle_forward_value(rung_amps[i], rung_thetas[i], RUNGS[i][1], h, decay_rate)
                for i in range(N_RUNGS)
            ])
            pred = mean_train + float(np.dot(weights, future_vals))
            truth = NINO[refit_t + h - 1]
            results[h].append((refit_t, pred, truth))

    print(f"  {time.time()-t_start:.1f}s, {len(results[HORIZONS[0]])} forecasts/horizon")

    print(f"  {'horizon':>8}  {'corr':>7}  {'MAE':>7}  {'pers MAE':>9}  {'clim MAE':>9}  {'R²(clim)':>9}  {'dir':>6}")
    h_metrics = {}
    for h in HORIZONS:
        if not results[h]: continue
        preds = np.array([r[1] for r in results[h]])
        truths = np.array([r[2] for r in results[h]])
        clim_pred = float(np.mean(NINO))
        pers_preds = np.array([NINO[r[0]-1] for r in results[h]])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds - truths)))
        pers_mae = float(np.mean(np.abs(pers_preds - truths)))
        clim_mae = float(np.mean(np.abs(clim_pred - truths)))
        ss_res = np.sum((truths - preds)**2); ss_tot = np.sum((truths - clim_pred)**2)
        r2_clim = float(1 - ss_res/ss_tot) if ss_tot > 0 else 0.0
        dir_acc = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
        print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {pers_mae:.3f}      {clim_mae:.3f}  {r2_clim:+.3f}  {dir_acc*100:5.1f}%")
        h_metrics[h] = dict(corr=corr, mae=mae, pers_mae=pers_mae, clim_mae=clim_mae,
                            r2_clim=r2_clim, dir_acc=dir_acc, n=len(results[h]))
    results_by_variant[variant] = h_metrics

    # Save forecast arrays (V1 only to save space)
    if variant == 'V1':
        forecasts_by_variant[variant] = {
            h: dict(refit_t=[r[0] for r in results[h]],
                    preds=[r[1] for r in results[h]],
                    truths=[r[2] for r in results[h]])
            for h in HORIZONS
        }

out = dict(method="Rolling vehicle: forward-simulate each φ-rung as oscillator from causal training state",
           variants={'V0': 'equal weights', 'V1': 'V0 + training-fit weights', 'V2': 'V1 + amplitude decay'},
           results_by_variant=results_by_variant,
           forecasts=forecasts_by_variant)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
