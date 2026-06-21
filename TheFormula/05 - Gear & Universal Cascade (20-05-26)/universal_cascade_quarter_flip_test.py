"""Test quarter-turn coupler flip on Universal Cascade.

Dylan 2026-05-18: 'Every 1/4 gear turn, it changes direction for the coupler
size system probably running underneath but connecting and then reverts back
to the main direction.'

Mechanic: at every dom_P/4 interval, a brief engagement window (length 1/phi^3
of each quarter) where the small coupler underneath fires a counter-current
proportional to recent momentum. Outside the window: nothing.

Sweep engagement_window x flip_strength to find what helps.
"""
import os, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1 + 5**0.5) / 2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)

# Load ENSO + feeders
nino_df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv'),
                     parse_dates=['Date'], na_values=[-99.99]).dropna()
nino_df.columns = [c.strip() for c in nino_df.columns]
nino_df['Year'] = nino_df['Date'].dt.year; nino_df['Month'] = nino_df['Date'].dt.month
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
m_df = nino_df[['Year', 'Month', nino_col, 'Date']].merge(soi_df, on=['Year', 'Month']).merge(pdo_df, on=['Year', 'Month'])
m_df.columns = ['Year', 'Month', 'NINO', 'Date', 'SOI', 'PDO']
m_df = m_df.dropna().sort_values('Date').reset_index(drop=True)
train_n = int((m_df['Year'] <= 2000).sum())
test_idx = np.where((m_df['Year'] > 2000).values)[0]
nino = np.asarray(m_df['NINO'].values, dtype=float)
soi_a = np.asarray(m_df['SOI'].values, dtype=float)
pdo_a = np.asarray(m_df['PDO'].values, dtype=float)


class UCq:
    def __init__(self, ara, dom_P, n_rungs=5, flip=False,
                 engage_window=1.0/PHI**3, flip_strength=0.5, momentum_lag=3):
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
        low = 1.0 / (P * 1.4); high = 1.0 / (P * 0.7); nyq = 0.5
        lo, hi = max(0.001, low / nyq), min(0.999, high / nyq)
        sos = butter(4, [lo, hi], btype='band', output='sos')
        return np.asarray(sosfiltfilt(sos, np.asarray(sig, dtype=float)))

    def _tense(self, x):
        sign = np.sign(x); absx = np.abs(x)
        return sign * (self.tension_exp * absx + (1 - self.tension_exp) * np.log1p(absx))

    def fit(self, sig, feeders, train_end, horizon):
        sig = np.asarray(sig, dtype=float)
        self.sig = sig
        self.tm = float(sig[:train_end].mean())
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
            if i > 0: f.append((2.0 / PHI) * float(self.rungs[i - 1][t]))
            if i < len(self.rungs) - 1: f.append((1.0 / (PHI ** 2)) * float(self.rungs[i + 1][t]))
        for fc in self.fcomps: f.append(float(fc[t]))
        return f

    def _quarter_flip(self, t):
        """Coupler engagement: brief counter-current proportional to recent momentum."""
        quarter_P = self.dom_P / 4.0
        # Phase within the current quarter (0..1)
        phase = (t % quarter_P) / quarter_P
        # Engagement only during early portion of each quarter
        if phase >= self.engage_window:
            return 0.0
        # Brief ramp: 1.0 at quarter-start, 0.0 at end of engage_window
        amp = 1.0 - (phase / self.engage_window)
        # Recent momentum: difference over momentum_lag steps
        lag = self.momentum_lag
        if t < lag: return 0.0
        mom = float(self.sig[t]) - float(self.sig[t - lag])
        # Counter-current: opposite sign × strength × ramp
        return -self.flip_strength * mom * amp

    def predict(self, t):
        f = self._feats(t)
        base = self.tm + sum(float(np.dot(w, f)) for w in self.weights.values())
        if self.flip:
            base += self._quarter_flip(t)
        return base


def run(horizon, **kw):
    uc = UCq(ara=2.0, dom_P=48, n_rungs=5, **kw)
    uc.fit(nino, [soi_a, pdo_a], train_n, horizon)
    preds, acts = [], []
    for t in test_idx:
        if t + horizon >= len(m_df): continue
        preds.append(uc.predict(t))
        acts.append(float(nino[t + horizon]))
    p = np.array(preds); a = np.array(acts)
    p_adj = p - p.mean() + a.mean()
    mae = float(np.abs(p_adj - a).mean())
    corr = float(np.corrcoef(p_adj, a)[0, 1])
    return mae, corr


print('ENSO blind test 2001-2025 — Quarter-turn coupler flip sweep')
print('=' * 78)
print('Base (no flip):')
for h in [1, 3, 6, 12, 22]:
    mb, cb = run(h, flip=False)
    print(f'  h={h:>3}  MAE {mb:.3f}  corr {cb:+.3f}')
print()

for engage in [1.0/PHI**4, 1.0/PHI**3, 1.0/PHI**2, 0.5]:
    for fstr in [0.3, 0.5, 0.8, 1.2]:
        for mlag in [1, 3, 6]:
            print(f'engage={engage:.3f}  flip_strength={fstr}  momentum_lag={mlag}:')
            for h in [3, 6, 12, 22]:
                ms, cs = run(h, flip=True, engage_window=engage,
                             flip_strength=fstr, momentum_lag=mlag)
                print(f'  h={h:>3}  MAE {ms:.3f}  corr {cs:+.3f}')
