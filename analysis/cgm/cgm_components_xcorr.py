import os,warnings,numpy as np,pandas as pd
warnings.filterwarnings("ignore")
T1D="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test/t1d";MG=18.0182
def grid(s):
    df=pd.read_csv(f"{T1D}/glucose_{s}.csv");c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce");c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MG
    c=c.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
    idx=pd.date_range(c.index[0].floor("5min"),c.index[-1].ceil("5min"),freq="5min")
    return c.reindex(c.index.union(idx)).sort_index().interpolate("time",limit=6).reindex(idx)
def impulses(s,idx,kind):
    z=pd.Series(0.0,index=idx)
    if kind=="food":
        df=pd.read_csv(f"{T1D}/food_{s}.csv");df["ts"]=pd.to_datetime(df["datetime"],format="%Y:%m:%d %H:%M:%S",errors="coerce")
        for ts,cal in zip(df["ts"],pd.to_numeric(df["calories"],errors="coerce")):
            if pd.notna(ts) and pd.notna(cal):
                j=idx.get_indexer([ts],method="nearest")[0];
                if 0<=j<len(z): z.iloc[j]+=cal
    else:
        df=pd.read_csv(f"{T1D}/insulin_{s}.csv");df["ts"]=pd.to_datetime(df["date"]+" "+df["time"],errors="coerce")
        fast=pd.to_numeric(df["fast_insulin"],errors="coerce").fillna(0)
        for ts,u in zip(df["ts"],fast):
            if pd.notna(ts) and u>0:
                j=idx.get_indexer([ts],method="nearest")[0]
                if 0<=j<len(z): z.iloc[j]+=u
    return z.values
LAGS=np.arange(0,61) # 0..5h in 5-min
def xcorr(imp,dgdt):
    imp=(imp-imp.mean()); out=[]
    for L in LAGS:
        a=imp[:len(imp)-L]; b=dgdt[L:]
        m=~np.isnan(b)
        out.append(np.corrcoef(a[m],b[m])[0,1] if m.sum()>50 and a.std()>0 else np.nan)
    return np.array(out)
FX=[];IX=[]
for s in [f"{i:03d}" for i in range(1,10)]:
    g=grid(s); idx=g.index; dg=np.diff(g.values,prepend=g.values[0])
    FX.append(xcorr(impulses(s,idx,"food"),dg)); IX.append(xcorr(impulses(s,idx,"ins"),dg))
fx=np.nanmean(FX,0); ix=np.nanmean(IX,0); t=LAGS*5
fp=np.nanargmax(fx); ip=np.nanargmin(ix)
print(f"FOOD -> dG/dt: peak +corr {fx[fp]:+.3f} at lag {t[fp]} min ({t[fp]/60:.1f} h)  = appearance drives RISE")
print(f"INSULIN(fast) -> dG/dt: trough {ix[ip]:+.3f} at lag {t[ip]} min ({t[ip]/60:.1f} h) = disposal drives FALL")
print(f"meal rung 4h: log2(4h / appearance {t[fp]/60:.2f}h) = {np.log2(4/(t[fp]/60+1e-9)):.2f} octaves down")
print(f"             log2(4h / disposal   {t[ip]/60:.2f}h) = {np.log2(4/(t[ip]/60+1e-9)):.2f} octaves down")
import json
d=json.load(open("_cgm_results.json"))
d["components_xcorr"]={"t":[int(x) for x in t],"food":[round(float(x),3) for x in fx],
  "insulin":[round(float(x),3) for x in ix],"food_lag":int(t[fp]),"ins_lag":int(t[ip])}
json.dump(d,open("_cgm_results.json","w"))
