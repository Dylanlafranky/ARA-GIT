"""Separate the overlapping appearance(food) & disposal(insulin) waves by deconvolution.
Events coincide but the kernels differ (fast rise vs slower fall), so ridge FIR regression
recovers each impulse-response wave. glucose(t) = conv(food,h_food)+conv(insulin,h_insulin).
Real T1D data (D1NAMO)."""
import os,warnings,numpy as np,pandas as pd
from scipy.signal import detrend
warnings.filterwarnings("ignore")
T1D="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test/t1d";MG=18.0182
L=48  # 4h FIR
def grid(s):
    df=pd.read_csv(f"{T1D}/glucose_{s}.csv");c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce");c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MG
    c=c.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
    idx=pd.date_range(c.index[0].floor("5min"),c.index[-1].ceil("5min"),freq="5min")
    return c.reindex(c.index.union(idx)).sort_index().interpolate("time",limit=6).reindex(idx)
def imp(s,idx,kind):
    z=np.zeros(len(idx))
    if kind=="food":
        df=pd.read_csv(f"{T1D}/food_{s}.csv");df["ts"]=pd.to_datetime(df["datetime"],format="%Y:%m:%d %H:%M:%S",errors="coerce")
        vals=pd.to_numeric(df["calories"],errors="coerce")/100.0  # per 100 kcal
    else:
        df=pd.read_csv(f"{T1D}/insulin_{s}.csv");df["ts"]=pd.to_datetime(df["date"]+" "+df["time"],errors="coerce")
        vals=pd.to_numeric(df["fast_insulin"],errors="coerce").fillna(0)  # per unit
    for ts,v in zip(df["ts"],vals):
        if pd.notna(ts) and pd.notna(v) and v>0:
            j=idx.get_indexer([ts],method="nearest")[0]
            if 0<=j<len(z): z[j]+=v
    return z
def lagmat(x):
    return np.column_stack([np.concatenate([np.zeros(l),x[:len(x)-l]]) for l in range(L+1)])
X=[];Y=[]
for s in [f"{i:03d}" for i in range(1,10)]:
    g=grid(s); m=~np.isnan(g.values)
    gg=np.full(len(g),np.nan); gg[m]=detrend(g.values[m])
    f=imp(s,g.index,"food"); i=imp(s,g.index,"ins")
    Xs=np.column_stack([lagmat(f),lagmat(i)])
    ok=m & ~np.isnan(gg)
    X.append(Xs[ok]); Y.append(gg[ok])
X=np.vstack(X); Y=np.concatenate(Y)
alpha=20.0
w=np.linalg.solve(X.T@X+alpha*np.eye(X.shape[1]), X.T@Y)
hf=w[:L+1]; hi=w[L+1:]
pred=X@w; r2=1-np.sum((Y-pred)**2)/np.sum((Y-Y.mean())**2)
t=np.arange(L+1)*5
print(f"deconvolution fit R^2={r2:.3f}  (n={len(Y)} samples, {len(X[0])} predictors)")
print(f"APPEARANCE kernel (food, per100kcal): peak +{hf.max():.1f} mg/dL at {t[np.argmax(hf)]} min")
print(f"DISPOSAL  kernel (insulin, per unit): trough {hi.min():.1f} mg/dL at {t[np.argmin(hi)]} min")
fa=t[np.argmax(hf)]/60; di=t[np.argmin(hi)]/60
print(f"timescales: appearance peak {fa:.2f}h, disposal trough {di:.2f}h")
print(f"separation: disposal is {di/ (fa+1e-9):.2f}x the appearance time; log2(disposal/appearance)={np.log2(di/(fa+1e-9)):.2f} octaves")
import json
d=json.load(open("_cgm_results.json"))
d["separated"]={"t":[int(x) for x in t],"appearance":[round(float(x),2) for x in hf],
  "disposal":[round(float(x),2) for x in hi],"r2":round(float(r2),3),
  "app_peak_min":int(t[np.argmax(hf)]),"disp_trough_min":int(t[np.argmin(hi)])}
json.dump(d,open("_cgm_results.json","w"))
