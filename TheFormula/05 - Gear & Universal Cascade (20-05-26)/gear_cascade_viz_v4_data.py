"""V4 viz data: actual + persistence + UC base + UC+Snapback + UC+GlobalAmp (winning variant)."""
import os, json, math
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
    def __init__(self, ara, dom_P, n_rungs=5, amp_mode='none', snapback=False,
                 snap_fraction=0.5, wall_threshold=0.5):
        self.ara = ara; self.dom_P = dom_P
        self.offsets = list(range(-(n_rungs//2), n_rungs - n_rungs//2))
        self.rung_periods = [dom_P*(PHI**k) for k in self.offsets]
        self.tension_exp = 1.0/(1.0 + math.exp(-3.0*(ara-1.0)))
        self.amp_mode = amp_mode
        self.snapback = snapback
        self.snap_fraction = snap_fraction
        self.wall_threshold = wall_threshold

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
        self.floor = float(sig[:train_end].min())
        self.ceiling = float(sig[:train_end].max())
        self.midpoint = (self.floor + self.ceiling) / 2.0
        self.range_half = (self.ceiling - self.floor) / 2.0
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

    def _snapback_force(self, current_x):
        dist = current_x - self.midpoint
        abs_dist = abs(dist)
        thresh = self.wall_threshold * self.range_half
        if abs_dist <= thresh: return 0.0
        ramp = min((abs_dist - thresh) / max(self.range_half - thresh, 1e-9), 1.5)
        return -np.sign(dist) * self.snap_fraction * self.signal_std * ramp

    def predict(self, t, current_value=None):
        f = self._feats(t)
        out = self.tm
        for P, w in self.weights.items():
            out += float(np.dot(w, f)) * self.rung_scales[P]
        if self.snapback:
            out += self._snapback_force(current_value if current_value is not None else 0.0)
        return out


HORIZONS = [1, 3, 6, 12, 22]
predictions = {}
for h in HORIZONS:
    uc = UC(ara=2.0, dom_P=48, n_rungs=5, amp_mode='none', snapback=False)
    uc.fit(nino, [soi_a, pdo_a], train_n, h)
    ucs = UC(ara=2.0, dom_P=48, n_rungs=5, amp_mode='none', snapback=True)
    ucs.fit(nino, [soi_a, pdo_a], train_n, h)
    uca = UC(ara=2.0, dom_P=48, n_rungs=5, amp_mode='global', snapback=False)
    uca.fit(nino, [soi_a, pdo_a], train_n, h)
    uc_p, ucs_p, uca_p, pers_p, act, dates = [], [], [], [], [], []
    for t in test_idx:
        if t + h >= len(m_df): continue
        uc_p.append(uc.predict(t))
        ucs_p.append(ucs.predict(t, current_value=float(nino[t])))
        uca_p.append(uca.predict(t))
        pers_p.append(float(nino[t]))
        act.append(float(nino[t + h]))
        dates.append(pd.Timestamp(m_df.loc[t + h, 'Date']).strftime('%Y-%m-%d'))
    up = np.array(uc_p); usp = np.array(ucs_p); uap = np.array(uca_p); pp = np.array(pers_p); aa = np.array(act)
    up_adj = up - up.mean() + aa.mean()
    usp_adj = usp - usp.mean() + aa.mean()
    uap_adj = uap - uap.mean() + aa.mean()
    def met(p, a):
        mae = float(np.abs(p - a).mean())
        corr = float(np.corrcoef(p, a)[0, 1]) if p.std() > 1e-9 else 0.0
        return mae, corr
    um, uc_corr = met(up_adj, aa)
    um_s, ucs_corr = met(usp_adj, aa)
    um_a, uca_corr = met(uap_adj, aa)
    pm, pc = met(pp, aa)
    predictions[str(h)] = {
        'dates': dates,
        'actual': [float(x) for x in act],
        'universal_cascade': up_adj.tolist(),
        'universal_cascade_snap': usp_adj.tolist(),
        'universal_cascade_amp': uap_adj.tolist(),
        'persistence': pers_p,
        'uc_mae': um, 'uc_corr': uc_corr,
        'ucs_mae': um_s, 'ucs_corr': ucs_corr,
        'uca_mae': um_a, 'uca_corr': uca_corr,
        'pers_mae': pm, 'pers_corr': pc,
    }
    print(f'h={h:3d}: UC {um:.3f}/{uc_corr:+.3f} | +Snap {um_s:.3f}/{ucs_corr:+.3f} | +AmpFix {um_a:.3f}/{uca_corr:+.3f} | pers {pm:.3f}/{pc:+.3f}')

out = {'horizons': HORIZONS, 'predictions': predictions,
       'system': 'ENSO (NINO 3.4)', 'ara': 2.0, 'period': '48 months'}
with open(os.path.join(_HERE, 'gear_cascade_viz_v4_data.js'), 'w') as f:
    f.write('window.cascadeVizData = '); json.dump(out, f); f.write(';')
print('Saved v4 viz data')
