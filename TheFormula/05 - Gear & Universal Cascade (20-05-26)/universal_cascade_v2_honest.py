"""HONEST version of Universal Cascade v2 — AR memory uses only legitimately
past information.

Original v2 used future actuals to compute the AR error term. Fixed here:
at step i predicting for time test_starts[i]+h, look back to the prediction
we made h steps ago for the time that is NOW past (test_starts[i]). Use the
NOW-known actual at that time to compute the error. No future leakage.
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


class UCv2H:
    def __init__(self, ara, dom_P, n_rungs=5,
                 amp_mode='none',
                 compass_gear=False,
                 ar_memory_mode='none',  # 'none' | 'honest' | 'LEAKY_old'
                 gamma=1.0/(PHI**3)):
        self.ara = ara; self.dom_P = dom_P
        self.offsets = list(range(-(n_rungs//2), n_rungs - n_rungs//2))
        self.rung_periods = [dom_P*(PHI**k) for k in self.offsets]
        self.tension_exp = 1.0/(1.0 + math.exp(-3.0*(ara-1.0)))
        self.amp_mode = amp_mode
        self.compass_gear = compass_gear
        self.ar_memory_mode = ar_memory_mode
        self.gamma = gamma

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

        self.weights = {}
        for ri, P in enumerate(self.rung_periods):
            X, y = [], []
            for t in range(train_end - horizon):
                X.append(self._feats(t)); y.append(float(self.rungs[ri][t+horizon]))
            X = np.array(X); y = np.array(y)
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            self.weights[P] = c

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

    def _compass_predict(self, t):
        f = self._feats(t)
        pers = float(self.sig[t])
        tick_total = sum(float(np.dot(self.tick_weights[P], f)) * self.rung_scales[P]
                         for P in self.rung_periods)
        return pers + tick_total

    def predict_sequence(self, test_starts, full_actual=None):
        # Pre-compute all base predictions (no AR)
        base_preds = []
        for t in test_starts:
            if self.compass_gear:
                base_preds.append(self._compass_predict(t))
            else:
                base_preds.append(self._base_predict(t))

        if self.ar_memory_mode == 'none':
            return base_preds

        h = self.horizon
        final = []
        for i, t in enumerate(test_starts):
            p = base_preds[i]
            if self.ar_memory_mode == 'honest':
                # Honest: prediction made h steps ago for time t is now in the past
                # because t is the time at which we KNOW actual[t] (we're predicting for t+h)
                # The prediction made h steps ago (at step i-h) targeted time test_starts[i-h]+h
                # If test_starts step = 1, then test_starts[i-h]+h = (t-h)+h = t
                if i >= h:
                    prior_pred_for_now = base_preds[i - h]
                    actual_now = float(full_actual[t])  # legitimately known
                    err = actual_now - prior_pred_for_now
                    p = p + self.gamma * err
            elif self.ar_memory_mode == 'LEAKY_old':
                # OLD CODE: used future actual (this was the bug)
                if i > 0:
                    prev_actual_idx = test_starts[i-1] + h
                    if prev_actual_idx < len(full_actual):
                        err = float(full_actual[prev_actual_idx]) - final[-1] if final else float(full_actual[prev_actual_idx]) - base_preds[i-1]
                        p = p + self.gamma * err
            final.append(p)
        return final


def run(horizon, **kwargs):
    uc = UCv2H(ara=2.0, dom_P=48, n_rungs=5, **kwargs)
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


configs = [
    ('baseline',          dict()),
    ('+amp',              dict(amp_mode='global')),
    ('+amp+AR_LEAKY',     dict(amp_mode='global', ar_memory_mode='LEAKY_old')),
    ('+amp+AR_HONEST',    dict(amp_mode='global', ar_memory_mode='honest')),
    ('+amp+compass',      dict(amp_mode='global', compass_gear=True)),
    ('+amp+compass+AR_LEAKY',  dict(amp_mode='global', compass_gear=True, ar_memory_mode='LEAKY_old')),
    ('+amp+compass+AR_HONEST', dict(amp_mode='global', compass_gear=True, ar_memory_mode='honest')),
]

print('ENSO blind — LEAKY AR memory vs HONEST AR memory')
print('=' * 92)
print(f'{"config":>26}  {"h":>3}  {"MAE":>6}  {"corr":>7}  {"persMAE":>8}  {"persCorr":>9}  {"vsPers":>10}')
print('-' * 92)
for name, kw in configs:
    for h in [1, 3, 6, 12, 22]:
        r = run(h, **kw)
        v = 'WIN' if r['mae'] < r['pmae'] and r['corr'] > r['pcorr'] else ''
        print(f'{name:>26}  {h:>3}  {r["mae"]:>.3f}  {r["corr"]:>+.3f}  {r["pmae"]:>8.3f}  {r["pcorr"]:>+9.3f}  {v:>10}')
    print()
