"""ECG visualizer data: UC base vs UC+QuarterFlip vs Persistence on nsr001."""
import os, json, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1 + 5**0.5) / 2
_HERE = os.path.dirname(os.path.abspath(__file__))

rr = pd.read_csv(os.path.join(_HERE, 'nsr001_rr.csv'))
sig_full = np.asarray(rr['rr_ms'].values, dtype=float)
time_full = np.asarray(rr['time_s'].values, dtype=float)

WINDOW_START = 2000
WINDOW_LEN = 1500
sig = sig_full[WINDOW_START:WINDOW_START + WINDOW_LEN]
times = time_full[WINDOW_START:WINDOW_START + WINDOW_LEN]
train_n = int(len(sig) * 0.6)


class UCq:
    def __init__(self, ara, dom_P, n_rungs=5, flip=False,
                 engage_window=1.0/PHI**3, flip_strength=0.8, momentum_lag=1):
        self.ara = ara; self.dom_P = dom_P
        offsets = list(range(-(n_rungs // 2), n_rungs - n_rungs // 2))
        self.rung_periods = [dom_P * (PHI ** k) for k in offsets]
        self.tension_exp = 1.0 / (1.0 + math.exp(-3.0 * (ara - 1.0)))
        self.flip = flip
        self.engage_window = engage_window
        self.flip_strength = flip_strength
        self.momentum_lag = momentum_lag

    def _bp(self, sig, P):
        if P < 3 or P > len(sig) // 4: return None
        low = 1.0/(P*1.4); high = 1.0/(P*0.7); nyq = 0.5
        lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
        try:
            sos = butter(4, [lo, hi], btype='band', output='sos')
            return np.asarray(sosfiltfilt(sos, np.asarray(sig, dtype=float)))
        except Exception:
            return None

    def _tense(self, x):
        s = np.sign(x); absx = np.abs(x)
        return s * (self.tension_exp * absx + (1 - self.tension_exp) * np.log1p(absx))

    def fit(self, sig, train_end, horizon):
        sig = np.asarray(sig, dtype=float); self.sig = sig
        self.tm = float(sig[:train_end].mean())
        self.rungs = []
        for P in self.rung_periods:
            r = self._bp(sig, P)
            self.rungs.append(r if r is not None else np.zeros(len(sig)))
        self.weights = {}
        for ri, P in enumerate(self.rung_periods):
            X, y = [], []
            for t in range(train_end - horizon):
                X.append(self._feats(t)); y.append(float(self.rungs[ri][t + horizon]))
            X = np.array(X); y = np.array(y)
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            self.weights[P] = c
        self.horizon = horizon

    def _feats(self, t):
        f = []
        for i, r in enumerate(self.rungs):
            v = float(r[t]); vt = float(self._tense(np.array([v]))[0])
            f.append(vt)
            if i > 0: f.append((2.0/PHI) * float(self.rungs[i-1][t]))
            if i < len(self.rungs)-1: f.append((1.0/(PHI**2)) * float(self.rungs[i+1][t]))
        return f

    def _quarter_flip(self, t):
        quarter_P = self.dom_P / 4.0
        phase = (t % quarter_P) / quarter_P
        if phase >= self.engage_window: return 0.0
        amp = 1.0 - (phase / self.engage_window)
        lag = self.momentum_lag
        if t < lag: return 0.0
        mom = float(self.sig[t]) - float(self.sig[t - lag])
        return -self.flip_strength * mom * amp

    def predict(self, t):
        f = self._feats(t)
        base = self.tm + sum(float(np.dot(w, f)) for w in self.weights.values())
        if self.flip: base += self._quarter_flip(t)
        return base


HORIZONS = [1, 3, 5, 10]
predictions = {}
for h in HORIZONS:
    uc = UCq(ara=PHI, dom_P=5, n_rungs=5, flip=False)
    uc.fit(sig, train_n, h)
    ucf = UCq(ara=PHI, dom_P=5, n_rungs=5, flip=True,
              engage_window=1.0/PHI**3, flip_strength=0.8, momentum_lag=1)
    ucf.fit(sig, train_n, h)
    uc_p, ucf_p, pers_p, act, beat_idx = [], [], [], [], []
    for t in range(train_n, len(sig) - h):
        uc_p.append(uc.predict(t))
        ucf_p.append(ucf.predict(t))
        pers_p.append(float(sig[t]))
        act.append(float(sig[t + h]))
        beat_idx.append(int(WINDOW_START + t + h))
    up = np.array(uc_p); usp = np.array(ucf_p); pp = np.array(pers_p); aa = np.array(act)
    up_adj = up - up.mean() + aa.mean()
    usp_adj = usp - usp.mean() + aa.mean()
    def met(p, a):
        mae = float(np.abs(p-a).mean())
        corr = float(np.corrcoef(p, a)[0, 1]) if p.std() > 1e-9 else 0.0
        return mae, corr
    um, uc_corr = met(up_adj, aa)
    um_s, ucf_corr = met(usp_adj, aa)
    pm, pc = met(pp, aa)
    predictions[str(h)] = {
        'beat_idx': beat_idx,
        'actual': [float(x) for x in act],
        'universal_cascade': up_adj.tolist(),
        'universal_cascade_flip': usp_adj.tolist(),
        'persistence': pers_p,
        'uc_mae': um, 'uc_corr': uc_corr,
        'ucf_mae': um_s, 'ucf_corr': ucf_corr,
        'pers_mae': pm, 'pers_corr': pc,
    }
    print(f'h={h:>3}: UC MAE {um:.2f} corr {uc_corr:+.3f} | UC+flip MAE {um_s:.2f} corr {ucf_corr:+.3f} | pers MAE {pm:.2f} corr {pc:+.3f}')

out = {'horizons': HORIZONS, 'predictions': predictions,
       'system': 'ECG nsr001 RR intervals (beats '+str(WINDOW_START)+'-'+str(WINDOW_START+WINDOW_LEN)+')',
       'ara': float(PHI), 'period': '5 beats',
       'flip_params': {'engage_window': 1.0/PHI**3, 'flip_strength': 0.8, 'momentum_lag': 1}}
with open(os.path.join(_HERE, 'ecg_quarter_flip_viz_data.js'), 'w') as f:
    f.write('window.ecgVizData = '); json.dump(out, f); f.write(';')
print('Saved ECG viz data')
