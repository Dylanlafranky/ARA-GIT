"""Add φ^k amplitude scaling to Universal Cascade.

Per framework_phi_k_amplitude_scaling.md: amp(rung k) = base × φ^(k - k_ref).
The residual diagnostic showed the cascade has the right shape (corr +0.37)
but mean-regression squashing (low-quartile bias -0.73, high-quartile +0.73).

Variants:
  none:     baseline (current cascade)
  global:   single scalar — rescale total prediction std to training signal std
  restore:  per-rung amplitude restoration from training stds
  phi_k:    strict φ^(k-k_ref) ratio, normalized to training signal std
  combined: restore then phi_k pattern
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


class UC:
    def __init__(self, ara, dom_P, n_rungs=5, amp_mode='none'):
        self.ara = ara; self.dom_P = dom_P
        self.offsets = list(range(-(n_rungs//2), n_rungs - n_rungs//2))
        self.rung_periods = [dom_P*(PHI**k) for k in self.offsets]
        self.tension_exp = 1.0/(1.0 + math.exp(-3.0*(ara-1.0)))
        self.amp_mode = amp_mode

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

        if self.amp_mode in ('restore', 'combined'):
            for ri, P in enumerate(self.rung_periods):
                truth_std = float(np.std(self.rungs[ri][:train_end]))
                preds = []
                for t in range(train_end - horizon):
                    f = self._feats(t)
                    preds.append(float(np.dot(self.weights[P], f)))
                pred_std = float(np.std(preds))
                if pred_std > 1e-9:
                    self.rung_scales[P] = truth_std / pred_std

        if self.amp_mode in ('phi_k', 'combined'):
            phi_pattern = np.array([PHI ** k for k in self.offsets])
            for ri, P in enumerate(self.rung_periods):
                self.rung_scales[P] *= phi_pattern[ri]
            tot_preds = []
            for t in range(train_end - horizon):
                f = self._feats(t)
                tot_preds.append(sum(float(np.dot(self.weights[P], f)) * self.rung_scales[P]
                                     for P in self.rung_periods))
            train_signal_std = float(np.std(sig[:train_end]))
            tot_std = float(np.std(tot_preds))
            if tot_std > 1e-9:
                norm = train_signal_std / tot_std
                for P in self.rung_periods:
                    self.rung_scales[P] *= norm

    def _feats(self, t):
        f = []
        for i, r in enumerate(self.rungs):
            v = float(r[t]); vt = float(self._tense(np.array([v]))[0])
            f.append(vt)
            if i > 0: f.append((2.0/PHI) * float(self.rungs[i-1][t]))
            if i < len(self.rungs)-1: f.append((1.0/(PHI**2)) * float(self.rungs[i+1][t]))
        for fc in self.fcomps: f.append(float(fc[t]))
        return f

    def predict(self, t):
        f = self._feats(t)
        out = self.tm
        for P, w in self.weights.items():
            out += float(np.dot(w, f)) * self.rung_scales[P]
        return out


def run(horizon, mode):
    uc = UC(ara=2.0, dom_P=48, n_rungs=5, amp_mode=mode)
    uc.fit(nino, [soi_a, pdo_a], train_n, horizon)
    preds, acts, pers = [], [], []
    for t in test_idx:
        if t + horizon >= len(m_df): continue
        preds.append(uc.predict(t))
        pers.append(float(nino[t]))
        acts.append(float(nino[t + horizon]))
    p = np.array(preds); a = np.array(acts); pp = np.array(pers)
    p_adj = p - p.mean() + a.mean()
    mae = float(np.abs(p_adj - a).mean())
    corr = float(np.corrcoef(p_adj, a)[0, 1]) if p.std() > 1e-9 else 0.0
    pmae = float(np.abs(pp - a).mean())
    pcorr = float(np.corrcoef(pp, a)[0, 1])
    edges = np.quantile(a, [0.0, 0.25, 0.75, 1.0])
    low_mask = a < edges[1]; high_mask = a >= edges[2]
    low_bias = float((a - p_adj)[low_mask].mean())
    high_bias = float((a - p_adj)[high_mask].mean())
    return {'mae': mae, 'corr': corr, 'pmae': pmae, 'pcorr': pcorr,
            'low_bias': low_bias, 'high_bias': high_bias,
            'std_ratio': float(p_adj.std()) / float(a.std())}


print('ENSO blind test 2001-2025 — amplitude rescaling variants')
print('=' * 90)
print(f'{"mode":>10}  {"h":>3}  {"MAE":>6}  {"corr":>7}  {"low_bias":>9}  {"high_bias":>10}  {"std/act":>8}  {"persMAE":>8}')
print('-' * 90)
for mode in ['none', 'global', 'restore', 'phi_k', 'combined']:
    for h in [1, 3, 6, 12, 22]:
        r = run(h, mode)
        gain = '  WIN' if r['mae'] < r['pmae'] and r['corr'] > r['pcorr'] else ''
        print(f'{mode:>10}  {h:>3}  {r["mae"]:>.3f}  {r["corr"]:>+.3f}  {r["low_bias"]:>+9.3f}  {r["high_bias"]:>+10.3f}  {r["std_ratio"]:>8.3f}  {r["pmae"]:>8.3f}{gain}')
    print()
