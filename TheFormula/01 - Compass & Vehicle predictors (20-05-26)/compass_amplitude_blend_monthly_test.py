"""
Compass + amplitude blend at mid-horizons (h=6 to h=12).

At short lead, compass dominates (anchored prediction with bounded drift).
At long lead, amplitude dominates (structural per-rung prediction).
Mid-horizon (h=6-12) is where neither alone is strong.

Test: blend = α × compass + (1-α) × amplitude. Sweep α from 0.0 to 1.0.
Find optimal α per horizon and check if the blend exceeds either alone.

Hypothesis: if the two vehicles make different errors, a blend should reduce
variance and improve correlation/MAE. If they make the same errors (same
underlying signal), blend won't help.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter

PHI = 1.6180339887498949
INV_PHI = 1.0 / PHI
INV_PHI3 = 1.0 / (PHI**3)
INV_PHI4 = 1.0 / (PHI**4)

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\compass_amplitude_blend_monthly_data.js")

def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)
def load_soi():
    rows=[]
    with open(SOI_PATH) as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts)<13: continue
            try: year=int(parts[0])
            except: continue
            if year<1900 or year>2100: continue
            for m in range(12):
                try: v=float(parts[1+m])
                except: continue
                if v<-90: continue
                rows.append((pd.Timestamp(year=year,month=m+1,day=1),v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino = load_nino(); soi = load_soi()
def to_m(s):
    s=s.copy(); s.index=pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino,soi = to_m(nino),to_m(soi)
common = nino.index.intersection(soi.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
SOI = soi.reindex(common).values.astype(float)
DATES = common; N = len(NINO)

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
    return lfilter(b, a, arr - np.mean(arr))

def read_amp_theta(bp_to_t):
    if len(bp_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]; rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

def amp_predict(refit_t, h, last_residual_internal, state, soi_scale, nino_scale, mean_train):
    nino_rung_future = []; soi_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, _ = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        nino_rung_future.append(a_n * np.cos(new_th_n))
        a_f, th_f, _ = state[('SOI', ri)]
        soi_rung_future.append(a_f * np.cos(th_f + 2*np.pi*h/p))
    nino_rung_future = np.array(nino_rung_future)
    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))
    soi_norm = np.array(soi_rung_future) / soi_scale * nino_scale
    walker = -1.0 * 1.0 * soi_norm[K_REF_IDX] * RUNG_WEIGHTS[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * RUNG_WEIGHTS[ri]
    return mean_train + own_pred + walker + INV_PHI3 * last_residual_internal

def run_compass(refit_t, horizon, last_residual_internal, state, soi_scale, nino_scale, mean_train, step_mean):
    cur_pos = NINO[refit_t - 1]
    prev_amp = NINO[refit_t - 1]
    for tau in range(1, horizon + 1):
        amp = amp_predict(refit_t, tau, last_residual_internal, state, soi_scale, nino_scale, mean_train)
        delta = amp - prev_amp
        direction = 1 if delta > 0 else -1
        cur_pos += direction * min(abs(delta), step_mean * PHI)
        prev_amp = amp
    return cur_pos

# ===== Rolling test =====
HORIZONS = [3, 6, 8, 10, 12, 18, 24]
MIN_TRAIN = 30 * 12
STEP = 1
ALPHAS = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]  # 0 = pure amp, 1 = pure compass

print(f"\n  Sweeping α ∈ {ALPHAS} at h ∈ {HORIZONS}")

records = {h: dict(amp=[], compass=[], blends={a: [] for a in ALPHAS}) for h in HORIZONS}
prev_res_compass = {h: 0.0 for h in HORIZONS}  # for compass γ=1/φ corrector
last_residual_internal = 0.0

t_start = time.time()
for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    nino_scale = float(np.std(arr_train)) + 1e-9
    soi_scale = float(np.std(SOI[:refit_t])) + 1e-9
    step_mean = float(np.mean(np.abs(np.diff(arr_train))))

    bp = {nm: [causal_bandpass({'NINO':NINO,'SOI':SOI}[nm][:refit_t], p) for k,p in RUNGS] for nm in ['NINO','SOI']}
    state = {}
    for nm in ['NINO','SOI']:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            state[(nm, ri)] = (a, th, 1.0)

    for h in HORIZONS:
        if refit_t + h - 1 >= N: continue
        truth = NINO[refit_t + h - 1]
        # Amplitude prediction
        amp_p = amp_predict(refit_t, h, last_residual_internal, state, soi_scale, nino_scale, mean_train)
        # Compass + γ=1/φ corrector (best for mid-lead)
        compass_p = run_compass(refit_t, h, last_residual_internal, state, soi_scale, nino_scale, mean_train, step_mean)
        compass_corrected = compass_p - INV_PHI * prev_res_compass[h]
        # Record
        records[h]['amp'].append((refit_t, amp_p, truth))
        records[h]['compass'].append((refit_t, compass_corrected, truth))
        for a in ALPHAS:
            blend = a * compass_corrected + (1.0 - a) * amp_p
            records[h]['blends'][a].append((refit_t, blend, truth))
        # Update prev residual for compass corrector (using BASE compass to avoid feedback)
        prev_res_compass[h] = float(truth - compass_p)

    if records[1 if 1 in HORIZONS else HORIZONS[0]]['amp']:
        last = records[HORIZONS[0]]['amp'][-1]
        last_residual_internal = float(last[2] - last[1])

print(f"  {time.time()-t_start:.1f}s")

# ===== Metrics =====
print(f"\n========= COMPASS + AMPLITUDE BLEND RESULTS =========")
clim_pred = float(np.mean(NINO))

def metrics(recs):
    if not recs: return None
    preds = np.array([r[1] for r in recs])
    truths = np.array([r[2] for r in recs])
    pers_preds = np.array([NINO[r[0]-1] for r in recs])
    corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
    mae = float(np.mean(np.abs(preds - truths)))
    ss_res = np.sum((truths - preds)**2)
    ss_pers = np.sum((truths - pers_preds)**2)
    r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
    dir_acc = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
    return dict(corr=corr, mae=mae, r2_pers=r2_pers, dir=dir_acc)

results_out = {}
print(f"\n  {'h':>4}  {'metric':>10}", end='')
for a in ALPHAS:
    print(f"   α={a}", end='')
print(f"   compass-only   amp-only")

for h in HORIZONS:
    m_amp = metrics(records[h]['amp'])
    m_comp = metrics(records[h]['compass'])
    m_blends = {a: metrics(records[h]['blends'][a]) for a in ALPHAS}
    if m_amp is None or m_comp is None: continue
    results_out[h] = dict(amp=m_amp, compass=m_comp, blends={str(a):m_blends[a] for a in ALPHAS})

    # Find best α by MAE
    best_alpha_mae = min(ALPHAS, key=lambda a: m_blends[a]['mae'])
    best_alpha_corr = max(ALPHAS, key=lambda a: m_blends[a]['corr'])

    print(f"\n  h={h:>2}  {'corr':>10}", end='')
    for a in ALPHAS:
        c = m_blends[a]['corr']
        marker = '*' if a == best_alpha_corr else ' '
        print(f"  {marker}{c:+.2f}", end='')
    print(f"   {m_comp['corr']:+.2f}        {m_amp['corr']:+.2f}")

    print(f"  h={h:>2}  {'MAE':>10}", end='')
    for a in ALPHAS:
        m = m_blends[a]['mae']
        marker = '*' if a == best_alpha_mae else ' '
        print(f"  {marker}{m:.2f}", end='')
    print(f"   {m_comp['mae']:.2f}        {m_amp['mae']:.2f}")

    print(f"  h={h:>2}  {'R²(pers)':>10}", end='')
    for a in ALPHAS:
        r = m_blends[a]['r2_pers']
        print(f"   {r:+.2f}", end='')
    print(f"   {m_comp['r2_pers']:+.2f}        {m_amp['r2_pers']:+.2f}")

    print(f"  h={h:>2}  {'dir':>10}", end='')
    for a in ALPHAS:
        d = m_blends[a]['dir']*100
        print(f"   {d:.0f}%", end='')
    print(f"   {m_comp['dir']*100:.0f}%        {m_amp['dir']*100:.0f}%")

    # Headline: best blend vs best of either alone
    best_blend_mae = m_blends[best_alpha_mae]['mae']
    best_solo_mae = min(m_amp['mae'], m_comp['mae'])
    if best_blend_mae < best_solo_mae - 0.005:
        print(f"  → BLEND WINS at h={h}: best α={best_alpha_mae} → MAE {best_blend_mae:.3f} (solo best {best_solo_mae:.3f})")

out = dict(method="Compass + amplitude blend test across horizons",
           horizons=HORIZONS, alphas=ALPHAS,
           results=results_out)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.COMPASS_AMP_BLEND = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
