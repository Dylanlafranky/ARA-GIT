"""Diagnostics: check sign and test 3-way combining."""
import os, json
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
def log(s): print(s, flush=True)

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
merged = nino_df[['Year','Month',nino_col]].merge(soi_df,on=['Year','Month']).merge(pdo_df,on=['Year','Month'])
merged.columns = ['Year','Month','NINO','SOI','PDO']
merged = merged.dropna().sort_values(['Year','Month']).reset_index(drop=True)
nino = np.asarray(merged['NINO'].values, dtype=float)
soi_a = np.asarray(merged['SOI'].values, dtype=float)
pdo_a = np.asarray(merged['PDO'].values, dtype=float)
train_idx = np.where((merged['Year']<=2000).values)[0]
test_idx = np.where((merged['Year']>2000).values)[0]

def bp(sig, P):
    low=1.0/(P*1.4); high=1.0/(P*0.7); nyq=0.5
    lo,hi=max(0.001,low/nyq),min(0.999,high/nyq)
    sos=butter(4,[lo,hi],btype='band',output='sos')
    return np.asarray(sosfiltfilt(sos, sig))

TIERS={'T1':[3,5],'T2':[8,13],'T3':[21,34],'T4':[55,89],'T5':[144]}
TIER_ORDER=['T1','T2','T3','T4','T5']
TIER_H={'T1':1,'T2':3,'T3':6,'T4':12}
all_P=sum(TIERS.values(),[])
nc={P:bp(nino,P) for P in all_P}
sc={P:bp(soi_a,P) for P in TIERS['T1']+TIERS['T2']}
pc={P:bp(pdo_a,P) for P in TIERS['T1']+TIERS['T2']}

def feats(tier,t):
    f=[float(nc[P][t]) for P in TIERS[tier]]
    if tier in ('T1','T2'):
        for P in TIERS[tier]:
            f.append(float(sc[P][t])); f.append(float(pc[P][t]))
    return f

# === DIAGNOSTIC 1: per-tier correlation check ===
log('=== Per-tier prediction quality (chain links) ===')
log('Each tier-N model predicts tier-(N+1) components from tier-N features at h_stage.')
log('Negative correlation = chain is "upside down" at that link.\n')

for i,tier in enumerate(TIER_ORDER[:-1]):
    nt=TIER_ORDER[i+1]
    h=TIER_H[tier]
    for Pn in TIERS[nt]:
        X,y=[],[]
        for t in train_idx:
            if t+h<len(merged):
                X.append(feats(tier,t)); y.append(float(nc[Pn][t+h]))
        X=np.array(X); y=np.array(y)
        c,*_=np.linalg.lstsq(X,y,rcond=None)
        # Test on test set
        Xt,yt=[],[]
        for t in test_idx:
            if t+h<len(merged):
                Xt.append(feats(tier,t)); yt.append(float(nc[Pn][t+h]))
        Xt=np.array(Xt); yt=np.array(yt)
        pred=Xt@c
        corr=float(np.corrcoef(pred,yt)[0,1]) if pred.std()>1e-9 and yt.std()>1e-9 else 0.0
        flag=' ← FLIPPED' if corr<-0.1 else (' ← weak' if abs(corr)<0.1 else '')
        log(f'  {tier}→{nt} P={Pn:3d}mo at h={h}mo:  corr {corr:+.3f}{flag}')

log('\n=== DIAGNOSTIC 2: at h=12, check whether negating the full chain prediction improves correlation ===')

# Train full chain at fixed h_total stages
chain={}
for i,tier in enumerate(TIER_ORDER[:-1]):
    nt=TIER_ORDER[i+1]
    h=TIER_H[tier]
    chain[tier]={}
    for Pn in TIERS[nt]:
        X,y=[],[]
        for t in train_idx:
            if t+h<len(merged):
                X.append(feats(tier,t)); y.append(float(nc[Pn][t+h]))
        c,*_=np.linalg.lstsq(np.array(X),np.array(y),rcond=None)
        chain[tier][Pn]=c.tolist()

def chain_predict_full(t):
    full = 0.0
    for P in TIERS['T1']: full += float(nc[P][t])
    for P in TIERS['T2']:
        full += float(np.dot(chain['T1'][P], feats('T1',t)))
    for P in TIERS['T3']:
        full += float(np.dot(chain['T2'][P], feats('T2',t)))
    for P in TIERS['T4']:
        full += float(np.dot(chain['T3'][P], feats('T3',t)))
    for P in TIERS['T5']:
        full += float(np.dot(chain['T4'][P], feats('T4',t)))
    return full

for h in [6, 12, 22]:
    chain_p, pers_p, act = [], [], []
    for t in test_idx:
        if t+h>=len(merged): continue
        chain_p.append(chain_predict_full(t))
        pers_p.append(float(nino[t]))
        act.append(float(nino[t+h]))
    cp=np.array(chain_p); pp=np.array(pers_p); aa=np.array(act)
    cp_adj=cp-cp.mean()+aa.mean()
    cp_flip=-(cp-cp.mean())+aa.mean()
    
    def met(p,a):
        mae=float(np.abs(p-a).mean()); corr=float(np.corrcoef(p,a)[0,1]) if p.std()>1e-9 and a.std()>1e-9 else 0.0
        return mae,corr
    cm,cc=met(cp_adj,aa); fm,fc=met(cp_flip,aa); pm,pc=met(pp,aa)
    log(f'  h={h:3d}: chain MAE {cm:.3f} corr {cc:+.3f} | flipped MAE {fm:.3f} corr {fc:+.3f} | pers MAE {pm:.3f} corr {pc:+.3f}')

# === DIAGNOSTIC 3: 3-way (triangular) combination at one tier ===
log('\n=== DIAGNOSTIC 3: try 3-component triangular combination ===')
log('Framework claim: actual NINO might require 3 components combined (not just summed).')
log('Test: combine NINO_lowfreq × NINO_midfreq × NINO_highfreq via products and check predictive power.')

# Build slow + medium + fast components of NINO
slow = nc[55] + nc[89] + nc[144]  # slow envelope
medium = nc[21] + nc[34]
fast = nc[3] + nc[5] + nc[8] + nc[13]

# Test if NINO ≈ slow + medium + fast (sum) vs slow * medium * fast (product) vs other 3-way
# h=12 forecast
h=12
for t_label, model in [('sum', slow + medium + fast),
                        ('slow only', slow + slow.mean()),
                        ('medium only', medium + medium.mean()),
                        ('slow + 0.5*medium', slow + 0.5*medium),
                        ('3-way: slow×sign(medium)×abs(fast)', slow * np.sign(medium+1e-9) * np.abs(fast))]:
    pred=[]; act=[]
    for t in test_idx:
        if t+h>=len(merged): continue
        pred.append(float(model[t])); act.append(float(nino[t+h]))
    pp=np.array(pred); aa=np.array(act)
    pp=pp-pp.mean()+aa.mean()
    mae=float(np.abs(pp-aa).mean())
    corr=float(np.corrcoef(pp,aa)[0,1]) if pp.std()>1e-9 and aa.std()>1e-9 else 0.0
    log(f'  {t_label:35s}: MAE {mae:.3f}, corr {corr:+.3f}')

log('\n=== Done diagnostics ===')
