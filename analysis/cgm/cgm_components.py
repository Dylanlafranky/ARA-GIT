"""Component bore-in (T1D, D1NAMO): the PARTS of the glucose change.
Appearance = food(calories)->glucose rise ; Disposal = fast insulin->glucose fall.
Event-triggered averages + impulse->dG/dt cross-correlation -> lags & timescales.
Test Dylan's prediction: the disposal coupling sits a 'log down' (smaller/faster) than
the ~4h meal excursion. Real data."""
import os,glob,warnings,numpy as np,pandas as pd
warnings.filterwarnings("ignore")
T1D="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test/t1d"
MG=18.0182;DT=5
def gl(s):
    df=pd.read_csv(f"{T1D}/glucose_{s}.csv");c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce");c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MG
    c=c.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
    idx=pd.date_range(c.index[0].floor("5min"),c.index[-1].ceil("5min"),freq="5min")
    return c.reindex(c.index.union(idx)).sort_index().interpolate("time",limit=6).reindex(idx)
def food(s):
    df=pd.read_csv(f"{T1D}/food_{s}.csv");df["ts"]=pd.to_datetime(df["datetime"],format="%Y:%m:%d %H:%M:%S",errors="coerce")
    df["cal"]=pd.to_numeric(df["calories"],errors="coerce");return df.dropna(subset=["ts","cal"])[["ts","cal"]]
def ins(s):
    df=pd.read_csv(f"{T1D}/insulin_{s}.csv");df["ts"]=pd.to_datetime(df["date"]+" "+df["time"],errors="coerce")
    df["fast"]=pd.to_numeric(df["fast_insulin"],errors="coerce").fillna(0)
    df["slow"]=pd.to_numeric(df["slow_insulin"],errors="coerce").fillna(0)
    return df.dropna(subset=["ts"])[["ts","fast","slow"]]

def eta(g, events, pre=6, post=48):
    """baseline-subtracted glucose around each event (5-min samples)."""
    out=[]
    gi=g.index
    for ts in events:
        j=gi.get_indexer([ts],method="nearest")[0]
        if j-pre<0 or j+post>=len(g): continue
        w=g.values[j-pre:j+post+1].astype(float)
        if np.isnan(w).any(): continue
        out.append(w-np.nanmean(w[:pre+1]))   # baseline = pre-event mean
    return np.array(out)

FA=[];FAi=[]   # food ETA, insulin(fast) ETA
for s in [f"{i:03d}" for i in range(1,10)]:
    try: g=gl(s)
    except Exception as e: print("gl err",s,e); continue
    f=food(s); i=ins(s)
    fa=eta(g, f["ts"].values)
    ia=eta(g, i.loc[i["fast"]>0,"ts"].values)
    if len(fa): FA.append(fa)
    if len(ia): FAi.append(ia)
FA=np.vstack(FA); FAi=np.vstack(FAi)
t=np.arange(-6,49)*DT  # minutes
fa=np.nanmean(FA,0); ia=np.nanmean(FAi,0)
print(f"food events pooled={len(FA)}  fast-insulin events pooled={len(FAi)}")
# appearance: time to peak rise after food
pk=np.argmax(fa[6:])+6; print(f"\nAPPEARANCE (food->glucose): peak +{fa[pk]:.0f} mg/dL at lag {t[pk]:.0f} min")
# disposal: time to nadir after insulin
nd=np.argmin(ia[6:])+6; print(f"DISPOSAL (fast insulin->glucose): nadir {ia[nd]:.0f} mg/dL at lag {t[nd]:.0f} min")
# half-times (timescale)
def half_rise(curve,base_i,ext_i,frac=0.5):
    a=curve[base_i]; b=curve[ext_i]; target=a+frac*(b-a)
    for k in range(base_i,ext_i+1):
        if (b>a and curve[k]>=target) or (b<a and curve[k]<=target): return t[k]
    return t[ext_i]
print(f"  food half-rise time ~ {half_rise(fa,6,pk):.0f} min ; insulin half-fall time ~ {half_rise(ia,6,nd):.0f} min")
meal_h=4.0
print(f"\nmeal rung ~ {meal_h} h. disposal lag-to-nadir {t[nd]/60:.1f} h -> log2(meal/disposal)={np.log2(meal_h/(t[nd]/60)):.2f} (>0 = a log DOWN / faster)")
print(f" appearance lag-to-peak {t[pk]/60:.1f} h -> log2(meal/appearance)={np.log2(meal_h/(t[pk]/60)):.2f}")
np.save("/tmp/fa.npy",fa); np.save("/tmp/ia.npy",ia); np.save("/tmp/t.npy",t)
# dump for dashboard
import json
d=json.load(open("_cgm_results.json"))
d["components"]={"t":[int(x) for x in t],"food":[round(float(x),1) for x in fa],
  "insulin":[round(float(x),1) for x in ia],"n_food":int(len(FA)),"n_ins":int(len(FAi)),
  "appearance_lag_min":int(t[pk]),"disposal_lag_min":int(t[nd]),"meal_h":meal_h}
json.dump(d,open("_cgm_results.json","w"))
