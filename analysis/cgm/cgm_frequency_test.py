"""Distinguish 'same event, less often/delayed' (Dylan) vs 'same event, bigger swings'.
Per subject: corrections/day, overshoot dwell above 180, excursion amplitude/peak. Real data."""
import os, json, warnings, numpy as np, pandas as pd
from scipy.signal import find_peaks
from scipy import stats
warnings.filterwarnings("ignore")
DATA="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test"
BI=os.path.join(DATA,"healthy_bigideas"); T1D=os.path.join(DATA,"t1d")
MG=18.0182; PROM=10.0; AMP=15.0; DIST=24; HI=180.0; LO=70.0; DT_MIN=5

def load_bi(s):
    df=pd.read_csv(os.path.join(BI,f"Dexcom_{s}.csv"),low_memory=False); e=df[df["Event Type"]=="EGV"].copy()
    e["ts"]=pd.to_datetime(e["Timestamp (YYYY-MM-DDThh:mm:ss)"],errors="coerce"); e["g"]=pd.to_numeric(e["Glucose Value (mg/dL)"],errors="coerce")
    return e.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
def load_t1d(s):
    df=pd.read_csv(os.path.join(T1D,f"glucose_{s}.csv")); c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce"); c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MG
    return c.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
def prep(s):
    f=f"{DT_MIN}min"; idx=pd.date_range(s.index[0].floor(f),s.index[-1].ceil(f),freq=f)
    x=s.reindex(s.index.union(idx)).sort_index().interpolate(method="time",limit=6).reindex(idx)
    return x.rolling(3,center=True,min_periods=2).mean().values

def metrics(sig):
    s=sig[~np.isnan(sig)]
    if len(s)<50: return None
    days=len(s)*DT_MIN/1440.0
    pk,_=find_peaks(s,distance=DIST,prominence=PROM); tr,_=find_peaks(-s,distance=DIST,prominence=PROM)
    amps=[]; peaks=[]; pabove=[]; n=0
    for p in pk:
        pv=tr[tr<p]; nx=tr[tr>p]
        if not len(pv) or not len(nx): continue
        a,b=pv[-1],nx[0]
        if p-a<3 or b-p<3: continue
        amp=s[p]-min(s[a],s[b])
        if amp<AMP: continue
        n+=1; amps.append(amp); peaks.append(s[p]); pabove.append(max(0.0,s[p]-HI))
    # overshoot dwell: contiguous runs above HI, durations (min)
    above=s>HI; dwell=[]; run=0
    for v in above:
        if v: run+=1
        elif run: dwell.append(run*DT_MIN); run=0
    if run: dwell.append(run*DT_MIN)
    return dict(days=round(days,1), corr_per_day=round(n/days,2) if days>0 else 0,
                n=n, med_amp=round(float(np.median(amps)),1) if amps else np.nan,
                med_peak=round(float(np.median(peaks)),1) if peaks else np.nan,
                med_peak_above180=round(float(np.median(pabove)),1) if pabove else 0.0,
                pct_above180=round(float(np.mean(above)*100),1),
                pct_below70=round(float(np.mean(s<LO)*100),1),
                med_dwell_above_min=round(float(np.median(dwell)),0) if dwell else 0.0)

def cohort(loader,ids):
    out={}
    for s in ids:
        try: m=metrics(prep(loader(s)))
        except Exception as e: print("ERR",s,e); continue
        if m and m["n"]>=3: out[s]=m
    return out
H=cohort(load_bi,[f"{i:03d}" for i in range(1,17)])
D=cohort(load_t1d,[f"{i:03d}" for i in range(1,10)])
def cliffs(a,b):
    a,b=np.array(a),np.array(b); gt=sum((x>b).sum() for x in a); lt=sum((x<b).sum() for x in a)
    return round((gt-lt)/(len(a)*len(b)),2)
def comp(key):
    h=[v[key] for v in H.values() if not np.isnan(v[key])]; d=[v[key] for v in D.values() if not np.isnan(v[key])]
    p=stats.mannwhitneyu(h,d,alternative="two-sided").pvalue
    return round(float(np.median(h)),1),round(float(np.median(d)),1),round(float(p),4),cliffs(h,d)
print(f"subjects: healthy {len(H)}, T1D {len(D)}")
print(f"{'metric':<22}{'healthy':>9}{'T1D':>9}{'MW p':>9}{'cliffδ':>8}   reading")
rows=[("corr_per_day","corrections/day","Dylan: less often → H>T1D"),
      ("med_dwell_above_min","dwell >180 (min)","delayed → T1D longer"),
      ("med_amp","excursion amp (mg/dL)","bigger swings → T1D higher"),
      ("med_peak_above180","peak above 180","bigger swings → T1D higher"),
      ("pct_above180","% time >180","T1D higher"),
      ("pct_below70","% time <70","T1D higher")]
for k,lab,rd in rows:
    hh,dd,p,cd=comp(k); print(f"{lab:<22}{hh:>9}{dd:>9}{p:>9}{cd:>8}   {rd}")
