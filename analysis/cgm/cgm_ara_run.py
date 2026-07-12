"""
Glucose CGM — framework-faithful ARA run (replaces analyze_cgm_phi.py's phi-hunt).

MAPPING (declared before measuring):
  Boundary   : blood-glucose regulation in one person over the CGM record.
  Observable : interstitial glucose (CGM), resampled to 5 min.
  Opposed    : APPEARANCE/absorption (rise, accumulation) vs DISPOSAL/clearance (fall, release).
  1.0 ridge  : fasting homeostasis — appearance ~ disposal, level held near setpoint.
  Handover   : the rise->fall switch at each meal peak (appearance-led -> disposal-led).
  phi (on probation): T_fall/T_rise is a TIME-handover ratio, so phi is *allowed* to fall
               out here. We do NOT hunt it: declared first, tested with competing constants,
               a pairing-null, and the between-group prediction. Reason it might appear in
               healthy & not T1D: healthy has an intact internal insulin handover; T1D's is
               broken/external, so the self-organising time-handover should DEGRADE.
  Ridge read : healthy = tight ridge w/ active hidden throughput; T1D = ridge failing.

Honest stats: per-SUBJECT is the unit (16 vs 9); matched absolute detection across cohorts
(T1D mmol/L -> mg/dL); effect sizes + bootstrap CIs; NO affirming-the-null vs phi.
Real data only.
"""
import os, json, warnings
import numpy as np, pandas as pd
from scipy.signal import find_peaks
from scipy import stats
warnings.filterwarnings("ignore")
rng = np.random.default_rng(0)

PHI = (1+np.sqrt(5))/2
DATA = os.environ.get("CGM_DATA", "/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test")
BI = os.path.join(DATA, "healthy_bigideas"); T1D = os.path.join(DATA, "t1d")
MMOL_TO_MGDL = 18.0182
PROM_MGDL = 10.0      # matched absolute prominence
AMP_MGDL  = 15.0      # matched min excursion amplitude
DIST = 24             # 2 h at 5 min
TIR_LO, TIR_HI = 70.0, 180.0
BI_HBA1C = {"001":5.5,"002":5.6,"003":5.9,"004":6.4,"005":5.7,"006":5.8,"007":5.3,"008":5.6,
            "009":6.1,"010":6.0,"011":6.0,"012":5.6,"013":5.7,"014":5.5,"015":5.5,"016":5.5}

def load_bi(sid):
    df = pd.read_csv(os.path.join(BI,f"Dexcom_{sid}.csv"), low_memory=False)
    e = df[df["Event Type"]=="EGV"].copy()
    e["ts"]=pd.to_datetime(e["Timestamp (YYYY-MM-DDThh:mm:ss)"],errors="coerce")
    e["g"]=pd.to_numeric(e["Glucose Value (mg/dL)"],errors="coerce")
    e=e.dropna(subset=["ts","g"]).set_index("ts").sort_index()
    return e["g"]

def load_t1d(sid):
    df=pd.read_csv(os.path.join(T1D,f"glucose_{sid}.csv"))
    c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce")
    c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MMOL_TO_MGDL   # -> mg/dL
    c=c.dropna(subset=["ts","g"]).set_index("ts").sort_index()
    return c["g"]

def preprocess(s, fm=5, gap=30):
    f=f"{fm}min"
    idx=pd.date_range(s.index[0].floor(f), s.index[-1].ceil(f), freq=f)
    x=s.reindex(s.index.union(idx)).sort_index().interpolate(method="time",limit=gap//fm).reindex(idx)
    return x.rolling(3,center=True,min_periods=2).mean().values

def cycles(sig):
    s=sig[~np.isnan(sig)]
    if len(s)<50: return [],[]
    pk,_=find_peaks(s,distance=DIST,prominence=PROM_MGDL)
    tr,_=find_peaks(-s,distance=DIST,prominence=PROM_MGDL)
    rises,falls=[],[]
    for p in pk:
        pv=tr[tr<p]; nx=tr[tr>p]
        if not len(pv) or not len(nx): continue
        a,b=pv[-1],nx[0]; tr_=p-a; tf=b-p
        if tr_<3 or tf<3: continue
        if s[p]-min(s[a],s[b])<AMP_MGDL: continue
        if 0.2< tf/tr_ <8.0:
            rises.append(tr_); falls.append(tf)
    return rises,falls

def ridge(sig):
    s=sig[~np.isnan(sig)]
    if len(s)<50: return {}
    mean=float(np.mean(s)); cv=float(np.std(s)/mean)
    tir=float(np.mean((s>=TIR_LO)&(s<=TIR_HI))*100)
    flux=float(np.mean(np.abs(np.diff(s)))/mean)   # throughput proxy: normalised |dG/dt|
    return dict(mean=round(mean,1),cv=round(cv,3),tir=round(tir,1),throughput=round(flux,5))

def cohort(loader, ids, hba=None):
    out=[]
    for sid in ids:
        try: sig=preprocess(loader(sid))
        except Exception as ex: print("  ERR",sid,ex); continue
        ri,fa=cycles(sig)
        if len(ri)<3: 
            print(f"  {sid}: too few cycles ({len(ri)})"); 
            continue
        ratios=np.array(fa)/np.array(ri)
        rec=dict(sid=sid,n=len(ratios),median_ratio=round(float(np.median(ratios)),3),
                 rises=[int(x) for x in ri],falls=[int(x) for x in fa],**ridge(sig))
        if hba: rec["hba1c"]=hba.get(sid)
        out.append(rec); print(f"  {sid}: n={rec['n']} med={rec['median_ratio']} cv={rec['cv']} tir={rec['tir']} thru={rec['throughput']}")
    return out

def boot_median(vals,n=4000):
    vals=np.array(vals); bs=[np.median(rng.choice(vals,len(vals),replace=True)) for _ in range(n)]
    return round(float(np.median(vals)),3), round(float(np.percentile(bs,2.5)),3), round(float(np.percentile(bs,97.5)),3)

def cliffs(a,b):
    a,b=np.array(a),np.array(b); gt=sum((x>b).sum() for x in a); lt=sum((x<b).sum() for x in a)
    return round((gt-lt)/(len(a)*len(b)),3)

print("=== HEALTHY (Big Ideas) ==="); H=cohort(load_bi,[f"{i:03d}" for i in range(1,17)],BI_HBA1C)
print("=== T1D (D1NAMO) ===");      D=cohort(load_t1d,[f"{i:03d}" for i in range(1,10)])

hr=[s["median_ratio"] for s in H]; dr=[s["median_ratio"] for s in D]
res={"phi":round(PHI,4),"per_subject":{"healthy":H,"t1d":D}}

# --- phi on probation: competing constants on healthy median-of-medians ---
hmed,hlo,hhi=boot_median(hr); dmed,dlo,dhi=boot_median(dr)
consts={"1.5":1.5,"phi=1.618":PHI,"1.75":1.75,"2.0":2.0}
dist={k:round(abs(hmed-v),3) for k,v in consts.items()}
nearest=min(dist,key=dist.get)
# pairing null: within subject, random re-pair rises<->falls, recompute median-of-medians, dist to phi
def pairing_null(subjects,reps=2000):
    real=np.median([s["median_ratio"] for s in subjects]); ds=[]
    for _ in range(reps):
        meds=[]
        for s in subjects:
            fa=np.array(s["falls"]); ri=np.array(s["rises"])
            meds.append(np.median(fa/rng.permutation(ri)))
        ds.append(abs(np.median(meds)-PHI))
    real_d=abs(real-PHI); p=float(np.mean(np.array(ds)<=real_d))
    return round(real_d,3),round(float(np.median(ds)),3),round(p,3)
real_d,surr_d,pval=pairing_null(H)

res["phi_test"]={
 "healthy_median_ratio":hmed,"healthy_ci":[hlo,hhi],
 "t1d_median_ratio":dmed,"t1d_ci":[dlo,dhi],
 "dist_to_constants":dist,"nearest_constant":nearest,
 "pairing_null":{"real_dist_to_phi":real_d,"surrogate_median_dist":surr_d,
   "p_real_nearer_or_equal":pval},
}
# between-group (the real test)
mw=stats.mannwhitneyu(hr,dr,alternative="two-sided")
res["between_group"]={
 "ratio":{"mw_p":round(float(mw.pvalue),4),"cliffs_delta":cliffs(hr,dr),
          "healthy":hmed,"t1d":dmed},
}
for key in ("cv","tir","throughput"):
    h=[s[key] for s in H]; d=[s[key] for s in D]
    res["between_group"][key]={"healthy_med":round(float(np.median(h)),4),
        "t1d_med":round(float(np.median(d)),4),
        "mw_p":round(float(stats.mannwhitneyu(h,d,alternative='two-sided').pvalue),4),
        "cliffs_delta":cliffs(h,d)}

# representative healthy trace (subject 001, first ~14h) for the dashboard
sig=preprocess(load_bi("001")); s=sig[~np.isnan(sig)][:170]
res["trace"]={"g":[round(float(x),1) for x in s],"tir_lo":TIR_LO,"tir_hi":TIR_HI,
              "mean":round(float(np.nanmean(s)),1)}

json.dump(res,open(os.path.join(os.path.dirname(__file__),"_cgm_results.json"),"w"))
print("\n--- phi on probation (healthy) ---")
print(" healthy median ratio",hmed,hlo,hhi," | nearest constant:",nearest,dist)
print(" pairing-null: real dist-to-phi",real_d,"surrogate median",surr_d,"p(real<=surr)",pval)
print("--- between-group (healthy vs T1D) ---")
print(" ratio: H",hmed,"T1D",dmed,"MW p",res["between_group"]["ratio"]["mw_p"],"delta",res["between_group"]["ratio"]["cliffs_delta"])
for k in ("cv","tir","throughput"):
    b=res["between_group"][k]; print(f" {k}: H {b['healthy_med']} T1D {b['t1d_med']} MW p {b['mw_p']} delta {b['cliffs_delta']}")
