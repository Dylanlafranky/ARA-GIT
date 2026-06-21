"""Universal Cascade v2 — pattern B AR memory (past code's honest method).

Pattern B (from ecg_horizon_aware_test.py and ecg_compass_refined_test.py):
  - Run a separate h=1 predictor alongside the main horizon predictor
  - At each rolling step t, observe truth at t and compute h=1 residual
    (which the h=1 prediction made at t-1 was predicting for time t)
  - Use that residual as AR feedback for the long-horizon prediction at step t

This is causal: at step t, both actual[t] and the h=1 prediction made at t-1
for target time t are known. The residual is observed past.

vs pattern A (my prior 'honest' mode): used residual at lag h, i.e.
prediction made at t-h for target t. Also honest but loses signal because
old residuals don't reflect current state.
"""
import os, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1 + 5**0.5) / 2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)

nino_df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv'),
                     parse_dates=['Date'], na_values=[-99.99]).dropna()
nino_df.columns = [c.strip() for c in nino_df.columns]
nino_df['Year'] = nino_df['Date'].dt.year; nino_df['Month'] = nino_df['Date'].dt.month
nino_col = [c for c in nino_df.columns if 'NINA' in c.upper()][0]
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
soi_df = load_ym(os.path.join(REPO_ROOT,'SOI_NOAA','soi.data'),'SOI',1)
pdo_df = load_ym(os.path.join(REPO_ROOT,'PDO_NOAA','ersst.v5.pdo.dat'),'PDO',2)
m_df = nino_df[['Year','Month',nino_col,'Date']].merge(soi_df,on=['Year','Month']).merge(pdo_df,on=['Year','Month'])
m_df.columns = ['Year','Month','NINO','Date','SOI','PDO']
m_df = m_df.dropna().sort_values('Date').reset_index(drop=True)
train_n = int((m_df['Year']<=2000).sum())
test_idx = np.where((m_df['Year']>2000).values)[0]
nino = np.asarray(m_df['NINO'].values, dtype=float)
soi_a = np.asarray(m_df['SOI'].values, dtype=float)
pdo_a = np.asarray(m_df['PDO'].values, dtype=float)


class UCv2P:
    """Universal cascade with pattern-B AR memory option."""
    def __init__(self, ara, dom_P, n_rungs=5,
                 amp_mode='none',
                 compass_gear=False,
                 ar_memory_mode='none',   # 'none' | 'lag_h_honest' | 'pattern_B_honest' | 'LEAKY_old'
                 gamma=1.0/(PHI**3),
                 ar_shortest_horizon=1):  # which horizon to use as the AR residual source
        self.ara = ara; self.dom_P = dom_P
        self.offsets = list(range(-(n_rungs//2), n_rungs - n_rungs//2))
        self.rung_periods = [dom_P*(PHI**k) for k in self.offsets]
        self.tension_exp = 1.0/(1.0 + math.exp(-3.0*(ara-1.0)))
        self.amp_mode = amp_mode
        self.compass_gear = compass_gear
        self.ar_memory_mode = ar_memory_mode
        self.gamma = gamma
        self.ar_shortest_horizon = ar_shortest_horizon

    def _bp(self, sig, P):
        if P < 3 or P > len(sig)//4: return None
        low = 1.0/(P*1.4); high = 1.0/(P*0.7); nyq = 0.5
        lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
        sos = butter(4, [lo, hi], btype='band', output='sos')
        return np.asarray(sosfiltfilt(sos, np.asarray(sig, dtype=float)))

    def _tense(self, x):
        s = np.sign(x); absx = np.abs(x)
        return s*(self.tension_exp*absx + (1-self.tension_exp)*np.log1p(absx))

    def fit(self, sig, feeders, train_end, horizon):
        sig = np.asarray(sig, dtype=float); self.tm = float(sig[:train_end].mean())
        self.signal_std = float(sig[:train_end].std())
        self.rungs = []
        for P in self.rung_periods:
            r = self._bp(sig, P)
            self.rungs.append(r if r is not None else np.zeros(len(sig)))
        self.fcomps = []
        for ff in (feeders or []):
            ff = np.asarray(ff, dtype=float)
            ff_z = (ff - ff[:train_end].mean()) / max(ff[:train_end].std(), 1e-9)
            for P in self.rung_periods:
                c = self._bp(ff_z, P)
                self.fcomps.append(c if c is not None else np.zeros(len(sig)))

        # Train weights for main horizon
        self.weights = {}
        for ri, P in enumerate(self.rung_periods):
            X, y = [], []
            for t in range(train_end - horizon):
                X.append(self._feats(t)); y.append(float(self.rungs[ri][t+horizon]))
            X = np.array(X); y = np.array(y)
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            self.weights[P] = c

        # Train weights for ar_shortest_horizon (for AR memory pattern B)
        self.ar_weights = {}
        if self.ar_memory_mode == 'pattern_B_honest':
            h_ar = self.ar_shortest_horizon
            for ri, P in enumerate(self.rung_periods):
                X, y = [], []
                for t in range(train_end - h_ar):
                    X.append(self._feats(t)); y.append(float(self.rungs[ri][t+h_ar]))
                X = np.array(X); y = np.array(y)
                c, *_ = np.linalg.lstsq(X, y, rcond=None)
                self.ar_weights[P] = c

        # Compass-gear tick weights
        self.tick_weights = {}
        if self.compass_gear:
            for ri, P in enumerate(self.rung_periods):
                X, y = [], []
                for t in range(train_end - horizon):
                    X.append(self._feats(t))
                    y.append(float(self.rungs[ri][t+horizon] - self.rungs[ri][t]))
                X = np.array(X); y = np.array(y)
                c, *_ = np.linalg.lstsq(X, y, rcond=None)
                self.tick_weights[P] = c

        self.sig = sig
        self.horizon = horizon

        self.rung_scales = {P: 1.0 for P in self.rung_periods}
        if self.amp_mode == 'global':
            tot_preds = []
            for t in range(train_end - horizon):
                f = self._feats(t)
                tot_preds.append(sum(float(np.dot(self.weights[P], f)) for P in self.rung_periods))
            train_signal_std = float(np.std(sig[:train_end]))
            tot_std = float(np.std(tot_preds))
            if tot_std > 1e-9:
                scale = train_signal_std / tot_std
                for P in self.rung_periods:
                    self.rung_scales[P] *= scale

    def _feats(self, t):
        f = []
        for i, r in enumerate(self.rungs):
            v = float(r[t]); vt = float(self._tense(np.array([v]))[0])
            f.append(vt)
            if i > 0: f.append((2.0/PHI) * float(self.rungs[i-1][t]))
            if i < len(self.rungs)-1: f.append((1.0/(PHI**2)) * float(self.rungs[i+1][t]))
        for fc in self.fcomps: f.append(float(fc[t]))
        return f

    def _base_predict(self, t):
        f = self._feats(t)
        out = self.tm
        for P, w in self.weights.items():
            out += float(np.dot(w, f)) * self.rung_scales[P]
        return out

    def _ar_predict_short_horizon(self, t):
        """Prediction at the shortest horizon (for AR memory pattern B)."""
        f = self._feats(t)
        out = self.tm
        for P, w in self.ar_weights.items():
            out += float(np.dot(w, f))  # No amp scaling for AR predictor (keep simple)
        return out

    def _compass_predict(self, t):
        f = self._feats(t)
        pers = float(self.sig[t])
        tick_total = sum(float(np.dot(self.tick_weights[P], f)) * self.rung_scales[P]
                         for P in self.rung_periods)
        return pers + tick_total

    def predict_sequence(self, test_starts, full_actual=None):
        base_preds = []
        for t in test_starts:
            if self.compass_gear:
                base_preds.append(self._compass_predict(t))
            else:
                base_preds.append(self._base_predict(t))

        if self.ar_memory_mode == 'none':
            return base_preds

        h = self.horizon
        h_ar = self.ar_shortest_horizon

        # Precompute short-horizon predictions (for pattern B)
        if self.ar_memory_mode == 'pattern_B_honest':
            ar_preds = []
            for t in test_starts:
                ar_preds.append(self._ar_predict_short_horizon(t))

        final = []
        for i, t in enumerate(test_starts):
            p = base_preds[i]
            if self.ar_memory_mode == 'lag_h_honest':
                if i >= h:
                    prior_pred_for_now = base_preds[i - h]
                    actual_now = float(full_actual[t])
                    err = actual_now - prior_pred_for_now
                    p = p + self.gamma * err
            elif self.ar_memory_mode == 'pattern_B_honest':
                # Most recent observed short-horizon residual.
                # ar_preds[j] was made at step j (time t_j) for target time t_j + h_ar.
                # We can use its residual ONCE actual[t_j + h_ar] is observed.
                # At current step i (time t), the latest such j with t_j + h_ar <= t is j = i - h_ar.
                if i >= h_ar:
                    target_time_of_ar_pred = test_starts[i - h_ar] + h_ar
                    if target_time_of_ar_pred < len(full_actual):
                        ar_pred_value = ar_preds[i - h_ar]
                        actual_at_target = float(full_actual[target_time_of_ar_pred])
                        err = actual_at_target - ar_pred_value
                        p = p + self.gamma * err
            elif self.ar_memory_mode == 'LEAKY_old':
                if i > 0:
                    prev_actual_idx = test_starts[i-1] + h
                    if prev_actual_idx < len(full_actual):
                        prev_pred = final[-1] if final else base_preds[i-1]
                        err = float(full_actual[prev_actual_idx]) - prev_pred
                        p = p + self.gamma * err
            final.append(p)
        return final


def run(horizon, **kwargs):
    uc = UCv2P(ara=2.0, dom_P=48, n_rungs=5, **kwargs)
    uc.fit(nino, [soi_a, pdo_a], train_n, horizon)
    test_starts = [t for t in test_idx if t + horizon < len(m_df)]
    preds = uc.predict_sequence(test_starts, full_actual=nino)
    acts = [float(nino[t + horizon]) for t in test_starts]
    pers = [float(nino[t]) for t in test_starts]
    p = np.array(preds); a = np.array(acts); pp = np.array(pers)
    p_adj = p - p.mean() + a.mean()
    mae = float(np.abs(p_adj - a).mean())
    corr = float(np.corrcoef(p_adj, a)[0, 1]) if p.std() > 1e-9 else 0.0
    pmae = float(np.abs(pp - a).mean())
    pcorr = float(np.corrcoef(pp, a)[0, 1])
    return {'mae': mae, 'corr': corr, 'pmae': pmae, 'pcorr': pcorr}


print('ENSO blind 2001-2025 — Pattern B (short-horizon residual cascade) vs Pattern A (lag-h)')
print('=' * 100)
print(f'{"config":>35}  {"h":>3}  {"MAE":>6}  {"corr":>7}  {"persMAE":>8}  {"persCorr":>9}  {"vsPers":>10}')
print('-' * 100)

configs = [
    ('amp+compass [NO_AR]',                dict(amp_mode='global', compass_gear=True)),
    ('amp+compass+AR_LEAKY',               dict(amp_mode='global', compass_gear=True, ar_memory_mode='LEAKY_old')),
    ('amp+compass+AR_lag_h_HONEST',        dict(amp_mode='global', compass_gear=True, ar_memory_mode='lag_h_honest')),
    ('amp+compass+AR_pattern_B (h_ar=1)',  dict(amp_mode='global', compass_gear=True, ar_memory_mode='pattern_B_honest', ar_shortest_horizon=1)),
    ('amp+compass+AR_pattern_B (h_ar=3)',  dict(amp_mode='global', compass_gear=True, ar_memory_mode='pattern_B_honest', ar_shortest_horizon=3)),
    ('amp+compass+AR_pattern_B (h_ar=6)',  dict(amp_mode='global', compass_gear=True, ar_memory_mode='pattern_B_honest', ar_shortest_horizon=6)),
]
for name, kw in configs:
    for h in [1, 3, 6, 12, 22]:
        r = run(h, **kw)
        v = 'WIN' if r['mae'] < r['pmae'] and r['corr'] > r['pcorr'] else ''
        print(f'{name:>35}  {h:>3}  {r["mae"]:>.3f}  {r["corr"]:>+.3f}  {r["pmae"]:>8.3f}  {r["pcorr"]:>+9.3f}  {v:>10}')
    print()
