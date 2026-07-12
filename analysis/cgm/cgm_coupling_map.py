"""Map the area + find couplings (H vs T1D), then bore in.
Octave-rung decomposition of glucose; per-rung normalised power (shape, not amplitude);
cross-rung amplitude-envelope coupling matrix. Find which rung/coupling collapses in T1D.
Real data; descriptive (filtfilt OK)."""
import os, warnings, numpy as np, pandas as pd
from scipy.signal import butter, filtfilt, hilbert, detrend
from scipy import stats
warnings.filterwarnings("ignore")
DATA="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test"
BI=os.path.join(DATA,"healthy_bigideas"); T1D=os.path.join(DATA,"t1d")
MG=18.0182; DT=5.0; FS=1.0/DT  # cycles per minute
RUNGS=[("0.5h",0.5),("1h",1.0),("2h",2.0),("4h(meal)",4.0),("8h",8.0)]  # octave centres (hours)
def load_bi(s):
    df=pd.read_csv(os.path.join(BI,f"Dexcom_{s}.csv"),low_memory=False);e=df[df["Event Type"]=="EGV"].copy()
    e["ts"]=pd.to_datetime(e["Timestamp (YYYY-MM-DDThh:mm:ss)"],errors="coerce");e["g"]=pd.to_numeric(e["Glucose Value (mg/dL)"],errors="coerce")
    return e.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
def load_t1d(s):
    df=pd.read_csv(os.path.join(T1D,f"glucose_{s}.csv"));c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce");c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MG
    return c.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
def prep(s):
    f="5min";idx=pd.date_range(s.index[0].floor(f),s.index[-1].ceil(f),freq=f)
    x=s.reindex(s.index.union(idx)).sort_index().interpolate(method="time",limit=6).reindex(idx)
    return x.rolling(3,center=True,min_periods=2).mean().values
def band(x,ph):  # bandpass around centre period ph (hours), octave width
    lo=1.0/(ph*np.sqrt(2)*60); hi=1.0/(ph/np.sqrt(2)*60)  # freq cyc/min
    b,a=butter(2,[lo/(FS/2),hi/(FS/2)],btype="band"); return filtfilt(b,a,x)
def subj(sig):
    s=sig[~np.isnan(sig)]
    if len(s)< int(8*60/DT*3): return None  # need >=3x the slowest period
    s=detrend(s)
    bands=[band(s,ph) for _,ph in RUNGS]
    pw=np.array([np.var(b) for b in bands]); pw=pw/pw.sum()        # normalised rung power
    env=[np.abs(hilbert(b)) for b in bands]
    n=len(bands); cm=np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            cm[i,j]=np.corrcoef(env[i],env[j])[0,1]
    return pw,cm
def cohort(loader,ids):
    P=[];C=[]
    for s in ids:
        try: r=subj(prep(loader(s)))
        except Exception as e: r=None
        if r: P.append(r[0]);C.append(r[1])
    return np.array(P),np.array(C)
HP,HC=cohort(load_bi,[f"{i:03d}" for i in range(1,17)])
DP,DC=cohort(load_t1d,[f"{i:03d}" for i in range(1,10)])
names=[r[0] for r in RUNGS]
print(f"healthy n={len(HP)}  T1D n={len(DP)}")
print("\n=== STAGE 1: rung power map (normalised; where the variance lives) ===")
print(f"{'rung':<10}{'healthy':>9}{'T1D':>9}{'H-T1D':>8}{'MW p':>8}")
for i,nm in enumerate(names):
    h=HP[:,i];d=DP[:,i];p=stats.mannwhitneyu(h,d,alternative='two-sided').pvalue
    print(f"{nm:<10}{np.median(h):>9.3f}{np.median(d):>9.3f}{np.median(h)-np.median(d):>8.3f}{p:>8.4f}")
print("\n=== STAGE 2: cross-rung coupling (env-corr); H, T1D, and H-T1D ===")
HCm=np.median(HC,axis=0);DCm=np.median(DC,axis=0);diff=HCm-DCm
print("pairs with largest healthy-minus-T1D coupling difference (collapsed couplings):")
pairs=[]
for i in range(len(names)):
    for j in range(i+1,len(names)):
        pairs.append((abs(diff[i,j]),diff[i,j],names[i],names[j],HCm[i,j],DCm[i,j]))
for ad,d,a,b,hc,dc in sorted(pairs,reverse=True)[:6]:
    print(f"  {a:<9}<->{b:<9}  H={hc:+.2f}  T1D={dc:+.2f}  (H-T1D={d:+.2f})")
