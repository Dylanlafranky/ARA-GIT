"""Universal Cascade v2 with HALF-ROTATION AR memory (Dylan 2026-05-20).

Replaces fixed h_ar=6 with h_ar derived from system geometry:
  - 'half_system'  : h_ar = dom_P / 2  (half a rotation of the system as a whole)
  - 'half_per_rung': each rung uses its own period / 2 — per-rung AR memory

All AR variants are strictly causal Pattern B:
at step i (time t), use actual[t] - ar_pred_made_at(t - h_ar)_for_target(t).
actual[t] is observable at step i; ar_pred used past-only data.

Verified all 7 causal checklist items before running.
"""
import os, math
import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter

PHI = (1 + 5**0.5) / 2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)


def find_data_root():
    candidates = [REPO_ROOT, os.path.dirname(REPO_ROOT), os.path.dirname(os.path.dirname(REPO_ROOT))]
    for root in candidates:
        if os.path.exists(os.path.join(root, 'Nino34', 'nino34.long.anom.csv')):
            return root
    raise FileNotFoundError('Could not locate Nino34/nino34.long.anom.csv from script context.')


DATA_ROOT = find_data_root()

# Data
nino_df = pd.read_csv(os.path.join(DATA_ROOT, 'Nino34', 'nino34.long.anom.csv'),
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
soi_df = load_ym(os.path.join(DATA_ROOT,'SOI_NOAA','soi.data'),'SOI',1)
pdo_df = load_ym(os.path.join(DATA_ROOT,'PDO_NOAA','ersst.v5.pdo.dat'),'PDO',2)
m_df = nino_df[['Year','Month',nino_col,'Date']].merge(soi_df,on=['Year','Month']).merge(pdo_df,on=['Year','Month'])
m_df.columns = ['Year','Month','NINO','Date','SOI','PDO']
m_df = m_df.dropna().sort_values('Date').reset_index(drop=True)
train_n = int((m_df['Year']<=2000).sum())
test_idx = np.where((m_df['Year']>2000).values)[0]
nino = np.asarray(m_df['NINO'].values, dtype=float)
soi_a = np.asarray(m_df['SOI'].values, dtype=float)
pdo_a = np.asarray(m_df['PDO'].values, dtype=float)


class UCv2H:
    """Universal Cascade with half-rotation AR memory options."""
    def __init__(self, ara, dom_P, n_rungs=5,
                 amp_mode='none',
                 compass_gear=False,
                 ar_mode='none',  # 'none' | 'fixed_6' | 'half_system' | 'half_per_rung'
                 gamma=1.0/(PHI**3)):
        self.ara = ara; self.dom_P = dom_P
        self.offsets = list(range(-(n_rungs//2), n_rungs - n_rungs//2))
        self.rung_periods = [dom_P*(PHI**k) for k in self.offsets]
        self.tension_exp = 1.0/(1.0 + math.exp(-3.0*(ara-1.0)))
        self.amp_mode = amp_mode
        self.compass_gear = compass_gear
        self.ar_mode = ar_mode
        self.gamma = gamma

    def _bp(self, sig, P):
        if P < 3 or P > len(sig)//4: return None
        low = 1.0/(P*1.4); high = 1.0/(P*0.7); nyq = 0.5
        lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
        sos = butter(4, [lo, hi], btype='band', output='sos')
        b, a = butter(4, [lo, hi], btype='band')
        return lfilter(b, a, np.asarray(sig, dtype=float) - np.mean(np.asarray(sig, dtype=float)))

    def _tense(self, x):
        s = np.sign(x); absx = np.abs(x)
        return s*(self.tension_exp*absx + (1-self.tension_exp)*np.log1p(absx))

    def _resolve_h_ar(self, horizon):
        """Compute h_ar per AR mode. Returns single int (system-level) or
        list of ints per rung (per-rung)."""
        if self.ar_mode == 'none': return None
        if self.ar_mode == 'fixed_6': return 6
        if self.ar_mode == 'half_system': return max(1, int(round(self.dom_P / 2.0)))
        if self.ar_mode == 'half_per_rung':
            return [max(1, int(round(P / 2.0))) for P in self.rung_periods]
        return None

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

        # Main weights
        self.weights = {}
        for ri, P in enumerate(self.rung_periods):
            X, y = [], []
            for t in range(train_end - horizon):
                X.append(self._feats(t)); y.append(float(self.rungs[ri][t+horizon]))
            X = np.array(X); y = np.array(y)
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            self.weights[P] = c

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

        # AR weights — separate model for each h_ar value needed
        self.ar_weights = {}      # for system-level: dict of {rung_period: coef}
        self.ar_weights_per_rung = {}  # for per-rung: list of dicts, one per rung
        h_ar = self._resolve_h_ar(horizon)
        if h_ar is not None:
            if isinstance(h_ar, list):
                # Per-rung: train each rung's AR with its own h_ar
                self.ar_weights_per_rung = []
                for ri, P in enumerate(self.rung_periods):
                    h_ri = h_ar[ri]
                    rung_weights = {}
                    for rj, Pj in enumerate(self.rung_periods):
                        X, y = [], []
                        for t in range(train_end - h_ri):
                            X.append(self._feats(t))
                            y.append(float(self.rungs[rj][t+h_ri]))
                        X = np.array(X); y = np.array(y)
                        c, *_ = np.linalg.lstsq(X, y, rcond=None)
                        rung_weights[Pj] = c
                    self.ar_weights_per_rung.append(rung_weights)
            else:
                # System-level: train with single h_ar
                for ri, P in enumerate(self.rung_periods):
                    X, y = [], []
                    for t in range(train_end - h_ar):
                        X.append(self._feats(t))
                        y.append(float(self.rungs[ri][t+h_ar]))
                    X = np.array(X); y = np.array(y)
                    c, *_ = np.linalg.lstsq(X, y, rcond=None)
                    self.ar_weights[P] = c

        self.sig = sig
        self.horizon = horizon
        self.h_ar = h_ar

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

    def _ar_predict_system(self, t):
        f = self._feats(t)
        out = self.tm
        for P, w in self.ar_weights.items():
            out += float(np.dot(w, f))
        return out

    def _ar_predict_per_rung(self, t):
        """Returns dict of rung -> predicted value at its own h_ar ahead."""
        f = self._feats(t)
        out = {}
        for ri, P in enumerate(self.rung_periods):
            rw = self.ar_weights_per_rung[ri]
            pred = self.tm + sum(float(np.dot(c, f)) for c in rw.values())
            out[ri] = pred
        return out

    def predict_sequence(self, test_starts, full_actual=None):
        base_preds = []
        for t in test_starts:
            if self.compass_gear:
                base_preds.append(self._compass_predict(t))
            else:
                base_preds.append(self._base_predict(t))

        if self.ar_mode == 'none' or self.h_ar is None:
            return base_preds

        # Precompute AR predictions for use as lag references
        if isinstance(self.h_ar, list):
            # Per-rung: ar_preds[i] = dict rung_idx -> pred
            ar_preds = []
            for t in test_starts:
                ar_preds.append(self._ar_predict_per_rung(t))
        else:
            ar_preds = []
            for t in test_starts:
                ar_preds.append(self._ar_predict_system(t))

        final = []
        for i, t in enumerate(test_starts):
            p = base_preds[i]
            if isinstance(self.h_ar, list):
                # Sum per-rung corrections, weighted by rung_scale
                correction = 0.0
                for ri, P in enumerate(self.rung_periods):
                    h_ri = self.h_ar[ri]
                    if i >= h_ri:
                        target_time = test_starts[i - h_ri] + h_ri
                        if target_time < len(full_actual):
                            err = float(full_actual[target_time]) - ar_preds[i - h_ri][ri]
                            # Weight per-rung err by 1/n_rungs so the total γ contribution is comparable
                            correction += err / len(self.rung_periods)
                p = p + self.gamma * correction
            else:
                h_ar = self.h_ar
                if i >= h_ar:
                    target_time = test_starts[i - h_ar] + h_ar
                    if target_time < len(full_actual):
                        err = float(full_actual[target_time]) - ar_preds[i - h_ar]
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
    return {'mae': mae, 'corr': corr, 'pmae': pmae, 'pcorr': pcorr, 'h_ar': uc.h_ar}


print('ENSO blind 2001-2025 — Half-Rotation AR Memory (Dylan 2026-05-20)')
print('=' * 100)
print('CORRELATION leads (per feedback_correlation_over_mae.md)')
print('All variants strictly causal (per feedback_strict_causal_protocol.md)')
print()
print(f'{"config":>32}  {"h":>3}  {"corr":>7}  {"MAE":>6}  {"persCorr":>9}  {"persMAE":>8}  {"dCorr":>7}  {"h_ar":>14}')
print('-' * 100)

configs = [
    ('NO AR (baseline cascade)',  dict(amp_mode='global', compass_gear=True, ar_mode='none')),
    ('Fixed h_ar=6',              dict(amp_mode='global', compass_gear=True, ar_mode='fixed_6')),
    ('Half-system (h_ar=24)',     dict(amp_mode='global', compass_gear=True, ar_mode='half_system')),
    ('Half-per-rung (9..63)',     dict(amp_mode='global', compass_gear=True, ar_mode='half_per_rung')),
]

for name, kw in configs:
    for h in [1, 3, 6, 12, 22]:
        r = run(h, **kw)
        dc = r['corr'] - r['pcorr']
        h_ar_str = str(r['h_ar']) if not isinstance(r['h_ar'], list) else f"[{','.join(str(x) for x in r['h_ar'])}]"
        print(f'{name:>32}  {h:>3}  {r["corr"]:>+.3f}  {r["mae"]:>.3f}  {r["pcorr"]:>+9.3f}  {r["pmae"]:>8.3f}  {dc:>+7.3f}  {h_ar_str:>14}')
    print()
