"""gear_cascade_prediction.py — Dylan 2026-05-12.

Framework claim: smaller (faster) rungs aggregate UP to drive larger (slower) rungs.
This is the cascade architecture — like small gears spinning many times to power a big flywheel.

Test: use ONLY fast rungs (periods 3-13 months) at time T to predict slow rungs
(periods 21-144 months) at time T+h. If the cascade is real, accumulated fast-rung
activity should contain forecast information for slow rungs.

Strict blind protocol:
  TRAIN: 1951-2000, learn mapping (fast rungs at T) → (slow rungs at T+h)
  TEST:  2001-2025, predict slow rungs from fast rungs, compare to persistence

Benchmark: predict NINO slow-rung components from fast-rung activity in NINO+SOI+PDO.
"""
import os, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
def log(s): print(s, flush=True)

# Load NINO, SOI, PDO
nino_df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv'),
                     parse_dates=['Date'], na_values=[-99.99]).dropna()
nino_df.columns = [c.strip() for c in nino_df.columns]
nino_df['Year'] = nino_df['Date'].dt.year
nino_df['Month'] = nino_df['Date'].dt.month
nino_col = [c for c in nino_df.columns if 'NINA' in c.upper()][0]

def load_ym(path, name, skip=1):
    rows = []
    with open(path) as f:
        for i, l in enumerate(f):
            if i < skip: continue
            p = l.split()
            if len(p) == 13:
                try:
                    yr = int(p[0])
                    for m, v in enumerate([float(x) for x in p[1:]], 1):
                        if -90 < v < 90: rows.append({'Year': yr, 'Month': m, name: v})
                except: pass
    return pd.DataFrame(rows)

soi_df = load_ym(os.path.join(REPO_ROOT, 'SOI_NOAA', 'soi.data'), 'SOI', 1)
pdo_df = load_ym(os.path.join(REPO_ROOT, 'PDO_NOAA', 'ersst.v5.pdo.dat'), 'PDO', 2)

merged = nino_df[['Year','Month',nino_col]].merge(soi_df,on=['Year','Month']).merge(pdo_df,on=['Year','Month'])
merged.columns = ['Year','Month','NINO','SOI','PDO']
merged = merged.dropna().sort_values(['Year','Month']).reset_index(drop=True)
log(f'Merged: {len(merged)} months ({merged.Year.iloc[0]}-{merged.Year.iloc[-1]})')

train_mask = (merged['Year'] <= 2000).values
test_mask = (merged['Year'] > 2000).values
train_idx = np.where(train_mask)[0]
test_idx = np.where(test_mask)[0]
log(f'Train: {len(train_idx)} months, Test: {len(test_idx)} months')

def bandpass(sig, P):
    low = 1/(P*1.4); high = 1/(P*0.7); nyq = 0.5
    lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
    sos = butter(4, [lo, hi], btype='band', output='sos')
    return sosfiltfilt(sos, sig)

FAST_RUNGS = [3, 5, 8, 13]   # months — fast gears
SLOW_RUNGS = [21, 34, 55, 89, 144]  # months — slow gears

# Bandpass everything
sigs = {'NINO': merged['NINO'].values, 'SOI': merged['SOI'].values, 'PDO': merged['PDO'].values}
fast_components = {}
slow_components = {}
for name, s in sigs.items():
    for P in FAST_RUNGS: fast_components[(name, P)] = bandpass(s, P)
    for P in SLOW_RUNGS: slow_components[(name, P)] = bandpass(s, P)

# For each slow rung in NINO, train a linear model: NINO_slow[P] at T+h = f(all fast components at T)
def metrics(p, a):
    mae = float(np.abs(p-a).mean())
    corr = float(np.corrcoef(p, a)[0,1]) if p.std()>1e-9 and a.std()>1e-9 else 0.0
    return mae, corr

log(f'\n=== CASCADE TEST: fast rungs (3-13mo) predict NINO slow rungs (21-144mo) ===\n')

# Build feature matrix: at each time T, the fast-component values of all 3 systems × 4 fast rungs = 12 features
def fast_features(t):
    feats = []
    for name in ['NINO','SOI','PDO']:
        for P in FAST_RUNGS:
            feats.append(fast_components[(name, P)][t])
    return feats

# For each slow rung, predict per horizon
log(f'{"slow P":>7} | {"h":>3} | {"cascade MAE":>12} | {"cascade corr":>13} | {"pers MAE":>10} | {"pers corr":>10} | {"cascade vs pers":>16}')
log('-'*100)

for slow_P in SLOW_RUNGS:
    slow_target = slow_components[('NINO', slow_P)]
    for h in [1, 3, 6, 12]:
        # Train
        X_train, y_train = [], []
        for t in train_idx:
            if t + h < len(merged):
                X_train.append(fast_features(t))
                y_train.append(slow_target[t + h])
        X_train = np.array(X_train); y_train = np.array(y_train)
        if len(X_train) < 100: continue
        # Linear regression
        coefs, *_ = np.linalg.lstsq(X_train, y_train, rcond=None)
        # Test
        X_test, y_test, pers_test = [], [], []
        for t in test_idx:
            if t + h < len(merged):
                X_test.append(fast_features(t))
                y_test.append(slow_target[t + h])
                pers_test.append(slow_target[t])
        X_test = np.array(X_test); y_test = np.array(y_test); pers_test = np.array(pers_test)
        if len(X_test) < 30: continue
        pred = X_test @ coefs
        cmae, ccorr = metrics(pred, y_test)
        pmae, pcorr = metrics(pers_test, y_test)
        gain = (pmae - cmae)/pmae*100 if pmae > 1e-9 else 0
        log(f'{slow_P:>7d} | {h:>3d} | {cmae:>12.4f} | {ccorr:>+13.3f} | {pmae:>10.4f} | {pcorr:>+10.3f} | {gain:>+15.1f}%')

log(f'\n=== Verdict ===')
log(f'If cascade MAE beats persistence MAE on any slow rung × horizon, fast→slow framework prediction is supported.')
log(f'If cascade corr is positive at long h where persistence corr drops, that is meaningful predictive lift.')
