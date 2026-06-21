"""Generate JSON data for cascade vs persistence visualizer."""
import os, json
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

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
merged = nino_df[['Year','Month',nino_col,'Date']].merge(soi_df,on=['Year','Month']).merge(pdo_df,on=['Year','Month'])
merged.columns = ['Year','Month','NINO','Date','SOI','PDO']
merged = merged.dropna().sort_values('Date').reset_index(drop=True)

train_idx = np.where((merged['Year']<=2000).values)[0]
test_idx = np.where((merged['Year']>2000).values)[0]

def bp(sig, P):
    low=1.0/(P*1.4); high=1.0/(P*0.7); nyq=0.5
    lo,hi=max(0.001,low/nyq),min(0.999,high/nyq)
    sos=butter(4,[lo,hi],btype='band',output='sos')
    return np.asarray(sosfiltfilt(sos, np.asarray(sig, dtype=float)))

nino = np.asarray(merged['NINO'].values, dtype=float)
soi_arr = np.asarray(merged['SOI'].values, dtype=float)
pdo_arr = np.asarray(merged['PDO'].values, dtype=float)

TIERS = {'T1':[3,5],'T2':[8,13],'T3':[21,34],'T4':[55,89],'T5':[144]}
TIER_ORDER = ['T1','T2','T3','T4','T5']
TIER_H = {'T1':1,'T2':3,'T3':6,'T4':12}

all_periods = sum(TIERS.values(), [])
N_comp = {P: bp(nino, P) for P in all_periods}
S_comp = {P: bp(soi_arr, P) for P in TIERS['T1']+TIERS['T2']}
P_comp = {P: bp(pdo_arr, P) for P in TIERS['T1']+TIERS['T2']}

def feats(tier, t):
    out = []
    for P in TIERS[tier]:
        out.append(float(N_comp[P][t]))
    if tier in ('T1','T2'):
        for P in TIERS[tier]:
            out.append(float(S_comp[P][t]))
            out.append(float(P_comp[P][t]))
    return out

# Train
chain = {}
for i, tier in enumerate(TIER_ORDER[:-1]):
    nt = TIER_ORDER[i+1]
    h = TIER_H[tier]
    chain[tier] = {}
    for Pn in TIERS[nt]:
        X,y = [], []
        for t in train_idx:
            if t + h < len(merged):
                X.append(feats(tier, t))
                y.append(float(N_comp[Pn][t+h]))
        X = np.array(X); y = np.array(y)
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        chain[tier][Pn] = c.tolist()

print(f'Chain trained, {sum(len(v) for v in chain.values())} models')

HORIZONS = [1, 3, 6, 12, 22]
test_dates = [pd.Timestamp(d).strftime('%Y-%m-%d') for d in merged.loc[test_idx, 'Date'].values]
predictions = {}

for h in HORIZONS:
    chain_p, pers_p, act, dates_h = [], [], [], []
    for ti, t in enumerate(test_idx):
        if t+h >= len(merged): continue
        full = 0.0
        for P in TIERS['T1']: full += float(N_comp[P][t])
        for P in TIERS['T2']:
            full += float(np.dot(chain['T1'][P], feats('T1',t)))
        for P in TIERS['T3']:
            full += float(np.dot(chain['T2'][P], feats('T2',t)))
        for P in TIERS['T4']:
            full += float(np.dot(chain['T3'][P], feats('T3',t)))
        for P in TIERS['T5']:
            full += float(np.dot(chain['T4'][P], feats('T4',t)))
        chain_p.append(full)
        pers_p.append(float(nino[t]))
        act.append(float(nino[t+h]))
        if t+h < len(test_idx) + test_idx[0]:
            dates_h.append(pd.Timestamp(merged.loc[t+h, 'Date']).strftime('%Y-%m-%d'))
        else:
            dates_h.append('')
    
    cp = np.array(chain_p); pp = np.array(pers_p); aa = np.array(act)
    cp_adj = cp - cp.mean() + aa.mean()
    
    cm = float(np.abs(cp_adj - aa).mean())
    pm = float(np.abs(pp - aa).mean())
    cc = float(np.corrcoef(cp_adj, aa)[0,1]) if cp_adj.std()>1e-9 and aa.std()>1e-9 else 0.0
    pc = float(np.corrcoef(pp, aa)[0,1]) if pp.std()>1e-9 and aa.std()>1e-9 else 0.0
    
    predictions[str(h)] = {
        'dates': dates_h,
        'actual': act,
        'chained_cascade': cp_adj.tolist(),
        'persistence': pers_p,
        'chain_mae': cm, 'chain_corr': cc,
        'pers_mae': pm, 'pers_corr': pc,
    }
    print(f'h={h:3d}: chain MAE {cm:.3f} corr {cc:+.3f} | pers MAE {pm:.3f} corr {pc:+.3f}')

out = {'horizons': HORIZONS, 'predictions': predictions}
with open(os.path.join(_HERE, 'gear_cascade_viz_data.js'), 'w') as f:
    f.write('window.cascadeVizData = ')
    json.dump(out, f)
    f.write(';')
print(f'\nSaved gear_cascade_viz_data.js ({os.path.getsize(os.path.join(_HERE, "gear_cascade_viz_data.js"))//1024} KB)')
