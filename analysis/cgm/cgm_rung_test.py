"""Test Dylan's 'lost coupled pair -> held by the rung above (octave/log slower)' model.
Per excursion: absolute T_rise/T_fall (min), mean rise/fall RATE (mg/dL/min), and the
STEEPEST slope (the 'snap'). Distinguishes: rung-above(=x2 slower+lower rate) vs
bigger-swing-same-rate vs event-faster(steeper snap). Real data."""
import os, warnings, numpy as np, pandas as pd
from scipy.signal import find_peaks
from scipy import stats
warnings.filterwarnings("ignore")
DATA="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test"
BI=os.path.join(DATA,"healthy_bigideas"); T1D=os.path.join(DATA,"t1d")
MG=18.0182; PROM=10.0; AMP=15.0; DIST=24; DT=5  # min/sample
def load_bi(s):
    df=pd.read_csv(os.path.join(BI,f"Dexcom_{s}.csv"),low_memory=False);e=df[df["Event Type"]=="EGV"].copy()
    e["ts"]=pd.to_datetime(e["Timestamp (YYYY-MM-DDThh:mm:ss)"],errors="coerce");e["g"]=pd.to_numeric(e["Glucose Value (mg/dL)"],errors="coerce")
    return e.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
def load_t1d(s):
    df=pd.read_csv(os.path.join(T1D,f"glucose_{s}.csv"));c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce");c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MG
    return c.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
def prep(s):
    f=f"{DT}min";idx=pd.date_range(s.index[0].floor(f),s.index[-1].ceil(f),freq=f)
    x=s.reindex(s.index.union(idx)).sort_index().interpolate(method="time",limit=6).reindex(idx)
    return x.rolling(3,center=True,min_periods=2).mean().values
def subj(sig):
    s=sig[~np.isnan(sig)]
    if len(s)<50: return None
    pk,_=find_peaks(s,distance=DIST,prominence=PROM); tr,_=find_peaks(-s,distance=DIST,prominence=PROM)
    Tr=[];Tf=[];rr=[];fr=[];snap=[]
    for p in pk:
        pv=tr[tr<p];nx=tr[tr>p]
        if not len(pv) or not len(nx): continue
        a,b=pv[-1],nx[0]
        if p-a<3 or b-p<3: continue
        if s[p]-min(s[a],s[b])<AMP: continue
        tr_=(p-a)*DT; tf=(b-p)*DT
        Tr.append(tr_);Tf.append(tf)
        rr.append((s[p]-s[a])/tr_); fr.append((s[p]-s[b])/tf)
        fall=np.diff(s[p:b+1])/DT   # mg/dL per min over the fall
        if len(fall): snap.append(-fall.min())  # steepest drop magnitude
    if len(Tf)<3: return None
    return dict(Tr=np.median(Tr),Tf=np.median(Tf),rr=np.median(rr),fr=np.median(fr),snap=np.median(snap))
def cohort(loader,ids):
    o=[]
    for s in ids:
        try: m=subj(prep(loader(s)))
        except: m=None
        if m: o.append(m)
    return o
H=cohort(load_bi,[f"{i:03d}" for i in range(1,17)]); D=cohort(load_t1d,[f"{i:03d}" for i in range(1,10)])
def cd(a,b):
    a,b=np.array(a),np.array(b);gt=sum((x>b).sum() for x in a);lt=sum((x<b).sum() for x in a);return round((gt-lt)/(len(a)*len(b)),2)
def comp(k):
    h=[x[k] for x in H];d=[x[k] for x in D]
    return float(np.median(h)),float(np.median(d)),float(stats.mannwhitneyu(h,d,alternative="two-sided").pvalue),cd(h,d)
print(f"healthy n={len(H)} T1D n={len(D)}")
print(f"{'metric':<26}{'healthy':>9}{'T1D':>9}{'T1D/H':>7}{'MW p':>9}{'δ':>7}")
for k,lab in [("Tr","T_rise (min)"),("Tf","T_fall (min)"),("rr","rise rate mg/dL/min"),
              ("fr","fall rate mg/dL/min"),("snap","steepest fall mg/dL/min")]:
    h,d,p,delta=comp(k); fold=d/h if h else float('nan')
    print(f"{lab:<26}{h:>9.2f}{d:>9.2f}{fold:>7.2f}{p:>9.4f}{delta:>7.2f}")
print(f"\noctave check: log2(T_fall fold) = {np.log2(comp('Tf')[1]/comp('Tf')[0]):.2f}  (1.0 = exactly one rung up)")
