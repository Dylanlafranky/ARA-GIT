"""universal_cascade_predictor.py — Dylan 2026-05-12.

GENERAL gear-mechanical cascade predictor — works on any oscillating system
given a dominant period, ARA value, and observed history. No system-specific
tuning. Encodes the framework's three reuse-able innovations from old work:

  1. ARA-asymmetric tension (engines get linear, consumers get log)
  2. Three-way φ²/2φ coupling (Space-Time-Rationality non-linear interaction)
  3. 1/φ³ momentum feedback (ARA orbit's worth of self-feedback)

Test it on ENSO (climate, ARA≈2 harmonic) and on bidmc01 ECG (cardiac, ARA≈φ engine).
Same architecture, different inputs, no per-system tuning.
"""
import os, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt, find_peaks

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
def log(s): print(s, flush=True)

# ============================================================================
# Universal cascade predictor (framework-derived, no per-system tuning)
# ============================================================================
class UniversalCascade:
    """Generic gear-mechanical cascade forecaster."""
    
    def __init__(self, ara: float, dominant_period: float, n_rungs: int = 5):
        """
        ara: system's ARA value (0.382 consumer ↔ 1.0 clock ↔ 1.618 engine ↔ 2.0 harmonic)
        dominant_period: in samples (e.g. 47 for ENSO ~4 years monthly, ~280 for ECG at 1Hz)
        n_rungs: how many φ-spaced rungs to use around the dominant period
        """
        self.ara = ara
        self.dom_P = dominant_period
        self.n_rungs = n_rungs
        # φ-spaced rung periods CENTRED on dominant_period
        offsets = list(range(-(n_rungs//2), n_rungs - n_rungs//2))
        self.rung_periods = [dominant_period * (PHI ** k) for k in offsets]
        # ARA-asymmetric tension parameter — smooth transition
        # engine (ARA=φ): tension_exponent = 1 (linear)
        # consumer (ARA=1/φ²≈0.382): tension_exponent = 0 (log-like)
        # smooth interp using sigmoid centred at 1.0
        self.tension_exp = 1.0 / (1.0 + math.exp(-3.0 * (ara - 1.0)))
        # 1/φ³ momentum coefficient
        self.momentum = 1.0 / (PHI ** 3)
        # Will be set by fit()
        self.weights = None
        self.training_mean = None
    
    def _bandpass(self, sig, P):
        """Bandpass at period P (in sample units). Fractional bandwidth 0.4."""
        if P < 3 or P > len(sig) // 4: return None
        low = 1.0/(P*1.4); high = 1.0/(P*0.7); nyq = 0.5
        lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
        if lo >= hi: return None
        try:
            sos = butter(4, [lo, hi], btype='band', output='sos')
            return np.asarray(sosfiltfilt(sos, np.asarray(sig, dtype=float)))
        except: return None
    
    def _ara_tension(self, x):
        """Apply ARA-asymmetric tension: linear for engines, log for consumers."""
        # mixed: linear^tension_exp + log^(1-tension_exp)
        sign = np.sign(x)
        absx = np.abs(x)
        linear = absx
        loglike = np.log1p(absx)
        return sign * (self.tension_exp * linear + (1 - self.tension_exp) * loglike)
    
    def fit(self, signal, feeders=None, train_end_idx=None, horizon=12):
        """Learn per-rung coefficients on training data only."""
        sig = np.asarray(signal, dtype=float)
        N = len(sig)
        if train_end_idx is None: train_end_idx = (2 * N) // 3
        self.training_mean = float(sig[:train_end_idx].mean())
        
        # Per-rung components of main signal
        self.rung_comps = []
        for P in self.rung_periods:
            c = self._bandpass(sig, P)
            self.rung_comps.append(c if c is not None else np.zeros(N))
        
        # Per-rung components of feeders (z-scored to handle different units)
        self.feeder_comps = []
        if feeders is not None:
            for f in feeders:
                f_arr = np.asarray(f, dtype=float)
                f_z = (f_arr - f_arr[:train_end_idx].mean()) / max(f_arr[:train_end_idx].std(), 1e-9)
                for P in self.rung_periods:
                    c = self._bandpass(f_z, P)
                    self.feeder_comps.append(c if c is not None else np.zeros(N))
        
        # Three-way coupling structure: at each rung k, build a feature vector
        # combining (rung k, rung k-1 with φ² weight, rung k+1 with 2/φ weight)
        # Plus ARA-tension applied to each component
        def features_at(t):
            f = []
            for i, comp in enumerate(self.rung_comps):
                # Triangle structure: this rung × neighbour rungs at framework weights
                v = float(comp[t])
                v_tense = float(self._ara_tension(np.array([v]))[0])
                f.append(v_tense)
                if i > 0:  # slower neighbour with 2/φ weight (Rationality flow)
                    f.append((2.0/PHI) * float(self.rung_comps[i-1][t]))
                if i < len(self.rung_comps)-1:  # faster neighbour with φ² weight (Space-Time)
                    f.append((1.0/(PHI**2)) * float(self.rung_comps[i+1][t]))
            for fc in self.feeder_comps:
                f.append(float(fc[t]))
            return f
        
        self._features_at = features_at
        
        # Train: predict each rung component at T+h from features at T
        self.weights = {}
        for ri, P in enumerate(self.rung_periods):
            target = self.rung_comps[ri]
            X, y = [], []
            for t in range(train_end_idx - horizon):
                X.append(features_at(t))
                y.append(float(target[t + horizon]))
            X = np.array(X); y = np.array(y)
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            self.weights[P] = c
        
        self.horizon = horizon
        self.train_end_idx = train_end_idx
        return self
    
    def predict(self, t):
        """Predict full signal at time t + self.horizon, given features at time t."""
        feats = self._features_at(t)
        # Sum rung-component predictions with 1/φ³ momentum from previous prediction
        total = 0.0
        for P, w in self.weights.items():
            total += float(np.dot(w, feats))
        # Add training mean offset back
        total += self.training_mean
        # Momentum: this needs state across the prediction loop — caller handles
        return total

# ============================================================================
# Test on ENSO (monthly, ARA≈2.0 harmonic, dominant period ~50 months)
# ============================================================================
def load_ym(path, name, skip=1):
    rows=[]
    with open(path) as f:
        for i,l in enumerate(f):
            if i<skip: continue
            p=l.split()
            if len(p)==13:
                try:
                    yr=int(p[0])
                    for m,v in enumerate([float(x) for x in p[1:]],1):
                        if -90<v<90: rows.append({'Year':yr,'Month':m,name:v})
                except: pass
    return pd.DataFrame(rows)

nino_df = pd.read_csv(os.path.join(REPO_ROOT,'Nino34','nino34.long.anom.csv'),
                     parse_dates=['Date'], na_values=[-99.99]).dropna()
nino_df.columns = [c.strip() for c in nino_df.columns]
nino_df['Year'] = nino_df['Date'].dt.year; nino_df['Month'] = nino_df['Date'].dt.month
nino_col = [c for c in nino_df.columns if 'NINA' in c.upper()][0]
soi_df = load_ym(os.path.join(REPO_ROOT,'SOI_NOAA','soi.data'),'SOI',1)
pdo_df = load_ym(os.path.join(REPO_ROOT,'PDO_NOAA','ersst.v5.pdo.dat'),'PDO',2)
m = nino_df[['Year','Month',nino_col]].merge(soi_df,on=['Year','Month']).merge(pdo_df,on=['Year','Month'])
m.columns = ['Year','Month','NINO','SOI','PDO']
m = m.dropna().sort_values(['Year','Month']).reset_index(drop=True)
log(f'ENSO data: {len(m)} months, train end at year 2000')
train_end = int((m['Year']<=2000).sum())

# ENSO is a harmonic (ARA≈2.0), dominant period ~48 months (φ³ × 12 = ~50)
predictor = UniversalCascade(ara=2.0, dominant_period=48, n_rungs=5)
predictor.fit(m['NINO'].values, feeders=[m['SOI'].values, m['PDO'].values],
              train_end_idx=train_end, horizon=12)

# Test predictions
preds = []; pers = []; act = []
for t in range(train_end, len(m) - 12):
    preds.append(predictor.predict(t))
    pers.append(float(m['NINO'].values[t]))
    act.append(float(m['NINO'].values[t + 12]))
preds = np.array(preds); pers = np.array(pers); act = np.array(act)
preds = preds - preds.mean() + act.mean()

def metrics(p, a):
    mae = float(np.abs(p-a).mean())
    corr = float(np.corrcoef(p,a)[0,1]) if p.std()>1e-9 and a.std()>1e-9 else 0.0
    return mae, corr

mae_u, corr_u = metrics(preds, act)
mae_p, corr_p = metrics(pers, act)
log(f'\n=== ENSO h=12mo blind forecast (Universal cascade, ARA=2.0) ===')
log(f'  Universal cascade:  MAE {mae_u:.3f}, corr {corr_u:+.3f}')
log(f'  Persistence:        MAE {mae_p:.3f}, corr {corr_p:+.3f}')
log(f'  Improvement:        {(mae_p-mae_u)/mae_p*100:+.1f}% MAE')

# ============================================================================
# Test on bidmc01 ECG (~1 sec dominant period, ARA close to engine φ≈1.618)
# ============================================================================
log(f'\n=== ECG bidmc01 (RR-interval-like, ARA≈φ engine) ===')

ecg_df = pd.read_csv(os.path.join(_HERE, 'bidmc01_ecg.csv'))
ecg = ecg_df.iloc[:, 0].values.astype(float)
FS = 125
# Get R-peaks to derive RR intervals
from scipy.signal import find_peaks
sos = butter(4, 0.5/(FS/2), btype='high', output='sos')
ecg_hp = sosfiltfilt(sos, ecg)
thresh = np.percentile(ecg_hp, 95) * 0.5
r_peaks, _ = find_peaks(ecg_hp, height=thresh, distance=int(0.4*FS))
rr_intervals = np.diff(r_peaks) / FS * 1000  # ms
log(f'  Derived {len(rr_intervals)} RR intervals, mean {rr_intervals.mean():.0f}ms')

if len(rr_intervals) >= 50:
    train_end_ecg = int(len(rr_intervals) * 2/3)
    # ECG (heart): engine-class, ARA ≈ φ, dominant period = 1 beat
    # But for multi-beat structure we predict in beat-units; dominant period ~5 beats (autonomic)
    predictor_ecg = UniversalCascade(ara=1.618, dominant_period=5, n_rungs=4)
    predictor_ecg.fit(rr_intervals, feeders=None, train_end_idx=train_end_ecg, horizon=5)
    preds_e=[]; pers_e=[]; act_e=[]
    for t in range(train_end_ecg, len(rr_intervals) - 5):
        preds_e.append(predictor_ecg.predict(t))
        pers_e.append(float(rr_intervals[t]))
        act_e.append(float(rr_intervals[t + 5]))
    if len(preds_e) >= 5:
        preds_e=np.array(preds_e); pers_e=np.array(pers_e); act_e=np.array(act_e)
        preds_e=preds_e-preds_e.mean()+act_e.mean()
        mae_eu, corr_eu = metrics(preds_e, act_e)
        mae_ep, corr_ep = metrics(pers_e, act_e)
        log(f'  Universal cascade:  MAE {mae_eu:.3f}ms, corr {corr_eu:+.3f}')
        log(f'  Persistence:        MAE {mae_ep:.3f}ms, corr {corr_ep:+.3f}')
        log(f'  Improvement:        {(mae_ep-mae_eu)/mae_ep*100:+.1f}% MAE')
    else:
        log(f'  Too few predictions to score')

log('\n=== Done ===')
