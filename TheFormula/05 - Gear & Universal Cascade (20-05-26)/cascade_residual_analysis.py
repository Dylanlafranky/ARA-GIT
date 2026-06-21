"""Residual analysis: what is the Universal Cascade actually missing on ENSO?

Compute residual = actual - prediction at h=12 (headline horizon) and h=22.
Output four diagnostics for the visualizer:
  1. Residual time series (aligned with actual signal)
  2. FFT power spectrum of residual (where in frequency does error live?)
  3. Residual vs actual scatter (does error track magnitude/sign?)
  4. Autocorrelation function (does residual have memory?)
Plus per-quartile mean residual (is error worse when actual is at walls?).
"""
import os, json, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1 + 5**0.5) / 2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)

# Load ENSO + feeders (same protocol as v3 viz)
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
    def __init__(self, ara, dom_P, n_rungs=5):
        self.ara=ara; self.dom_P=dom_P
        offsets=list(range(-(n_rungs//2), n_rungs - n_rungs//2))
        self.rung_periods=[dom_P*(PHI**k) for k in offsets]
        self.tension_exp=1.0/(1.0+math.exp(-3.0*(ara-1.0)))
    def _bp(self,sig,P):
        if P<3 or P>len(sig)//4: return None
        low=1.0/(P*1.4); high=1.0/(P*0.7); nyq=0.5
        lo,hi=max(0.001,low/nyq),min(0.999,high/nyq)
        sos=butter(4,[lo,hi],btype='band',output='sos')
        return np.asarray(sosfiltfilt(sos,np.asarray(sig,dtype=float)))
    def _tense(self,x):
        s=np.sign(x); absx=np.abs(x)
        return s*(self.tension_exp*absx + (1-self.tension_exp)*np.log1p(absx))
    def fit(self,sig,feeders,train_end,horizon):
        sig=np.asarray(sig,dtype=float); self.tm=float(sig[:train_end].mean())
        self.rungs=[]
        for P in self.rung_periods:
            r=self._bp(sig,P)
            self.rungs.append(r if r is not None else np.zeros(len(sig)))
        self.fcomps=[]
        for ff in (feeders or []):
            ff=np.asarray(ff,dtype=float)
            ff_z=(ff-ff[:train_end].mean())/max(ff[:train_end].std(),1e-9)
            for P in self.rung_periods:
                c=self._bp(ff_z,P)
                self.fcomps.append(c if c is not None else np.zeros(len(sig)))
        self.weights={}
        for ri,P in enumerate(self.rung_periods):
            X,y=[],[]
            for t in range(train_end-horizon):
                X.append(self._feats(t)); y.append(float(self.rungs[ri][t+horizon]))
            X=np.array(X); y=np.array(y)
            c,*_=np.linalg.lstsq(X,y,rcond=None)
            self.weights[P]=c
        self.horizon=horizon
    def _feats(self,t):
        f=[]
        for i,r in enumerate(self.rungs):
            v=float(r[t]); vt=float(self._tense(np.array([v]))[0])
            f.append(vt)
            if i>0: f.append((2.0/PHI)*float(self.rungs[i-1][t]))
            if i<len(self.rungs)-1: f.append((1.0/(PHI**2))*float(self.rungs[i+1][t]))
        for fc in self.fcomps: f.append(float(fc[t]))
        return f
    def predict(self,t):
        f=self._feats(t)
        return self.tm + sum(float(np.dot(w,f)) for w in self.weights.values())


def analyze(horizon):
    uc = UC(ara=2.0, dom_P=48, n_rungs=5)
    uc.fit(nino, [soi_a, pdo_a], train_n, horizon)
    pred, act, dates = [], [], []
    for t in test_idx:
        if t+horizon>=len(m_df): continue
        pred.append(uc.predict(t))
        act.append(float(nino[t+horizon]))
        dates.append(pd.Timestamp(m_df.loc[t+horizon,'Date']).strftime('%Y-%m-%d'))
    p = np.array(pred); a = np.array(act)
    p_adj = p - p.mean() + a.mean()
    resid = a - p_adj  # actual minus prediction
    n = len(resid)

    # FFT of residual (one-sided)
    fft = np.fft.rfft(resid - resid.mean())
    freqs = np.fft.rfftfreq(n, d=1.0)  # cycles per month
    periods = np.array([1.0/f if f>0 else 0.0 for f in freqs])  # in months
    power = np.abs(fft)**2

    # Autocorrelation up to lag 60 months
    ac = []
    rmean = resid.mean(); rstd = resid.std()
    for lag in range(1, 61):
        v = np.corrcoef(resid[:-lag], resid[lag:])[0,1]
        ac.append(float(v))

    # Quartile bins of actual
    edges = np.quantile(a, [0, 0.25, 0.5, 0.75, 1.0])
    bins = []
    for i in range(4):
        if i < 3:
            mask = (a >= edges[i]) & (a < edges[i+1])
        else:
            mask = (a >= edges[i]) & (a <= edges[i+1])
        if mask.sum() > 0:
            bins.append({
                'range': f'{edges[i]:.2f} to {edges[i+1]:.2f}',
                'mean_resid': float(resid[mask].mean()),
                'mean_abs_resid': float(np.abs(resid[mask]).mean()),
                'n': int(mask.sum())
            })

    # Wall-distance vs |residual|: do errors grow at the walls?
    floor = float(nino[:train_n].min()); ceiling = float(nino[:train_n].max())
    midpoint = (floor + ceiling) / 2.0; range_half = (ceiling - floor) / 2.0
    wall_distance = 1.0 - np.abs(a - midpoint) / range_half  # 1 = at wall, 0 = at center
    wall_distance = np.clip(wall_distance, -0.2, 1.0)
    # Bin by wall_distance
    wbins = [(0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]
    wall_buckets = []
    for lo, hi in wbins:
        mask = (wall_distance >= lo) & (wall_distance < hi)
        if mask.sum() > 0:
            wall_buckets.append({
                'distance_to_wall': f'{lo:.2f}-{hi:.2f} (0=center, 1=wall)',
                'mean_resid': float(resid[mask].mean()),
                'mean_abs_resid': float(np.abs(resid[mask]).mean()),
                'n': int(mask.sum())
            })

    # Top 8 spectral peaks
    idx_sorted = np.argsort(power)[::-1]
    top_peaks = []
    for i in idx_sorted[:8]:
        if freqs[i] > 0:
            top_peaks.append({'period_months': float(periods[i]), 'power': float(power[i])})

    return {
        'horizon': horizon,
        'dates': dates,
        'actual': a.tolist(),
        'prediction': p_adj.tolist(),
        'residual': resid.tolist(),
        'fft_periods': periods[1:].tolist(),  # skip f=0
        'fft_power': power[1:].tolist(),
        'autocorr_lags': list(range(1, 61)),
        'autocorr_values': ac,
        'quartile_bins': bins,
        'wall_buckets': wall_buckets,
        'top_spectral_peaks': top_peaks,
        'stats': {
            'mae': float(np.abs(resid).mean()),
            'rmse': float(np.sqrt((resid**2).mean())),
            'corr': float(np.corrcoef(p_adj, a)[0,1]),
            'residual_mean': float(resid.mean()),
            'residual_std': float(resid.std()),
            'residual_skew': float(((resid-rmean)**3).mean() / (rstd**3)),
            'residual_kurt': float(((resid-rmean)**4).mean() / (rstd**4) - 3.0),
        }
    }

H12 = analyze(12)
H22 = analyze(22)

out = {'h12': H12, 'h22': H22, 'system': 'ENSO NINO 3.4', 'ara': 2.0, 'dom_period': 48,
       'phi_rungs': [48/(PHI**2), 48/PHI, 48, 48*PHI, 48*PHI**2]}

with open(os.path.join(_HERE, 'cascade_residual_data.js'), 'w') as f:
    f.write('window.residualData = '); json.dump(out, f); f.write(';')

# Console summary
print('ENSO Universal Cascade — Residual Analysis')
print('=' * 70)
for label, d in [('h=12', H12), ('h=22', H22)]:
    s = d['stats']
    print(f'\n{label}: MAE {s["mae"]:.3f}  RMSE {s["rmse"]:.3f}  corr {s["corr"]:+.3f}')
    print(f'      residual: mean {s["residual_mean"]:+.3f}  std {s["residual_std"]:.3f}  skew {s["residual_skew"]:+.3f}  kurt {s["residual_kurt"]:+.3f}')
    print(f'      Top spectral peaks in residual (period in months):')
    for p in d['top_spectral_peaks'][:5]:
        print(f'         period {p["period_months"]:.1f}mo   power {p["power"]:.2f}')
    print(f'      Residual by actual quartile:')
    for b in d['quartile_bins']:
        print(f'         {b["range"]:>14}  mean_resid {b["mean_resid"]:+.3f}  |resid| {b["mean_abs_resid"]:.3f}  (n={b["n"]})')
    print(f'      Residual by wall distance:')
    for w in d['wall_buckets']:
        print(f'         {w["distance_to_wall"]:>30}  mean_resid {w["mean_resid"]:+.3f}  |resid| {w["mean_abs_resid"]:.3f}  (n={w["n"]})')
    print(f'      Autocorr lag-1: {d["autocorr_values"][0]:+.3f}  lag-6: {d["autocorr_values"][5]:+.3f}  lag-12: {d["autocorr_values"][11]:+.3f}  lag-24: {d["autocorr_values"][23]:+.3f}')

print('\nSaved residual diagnostic data')
