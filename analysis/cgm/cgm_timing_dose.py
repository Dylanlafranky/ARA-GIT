"""Phase vs gain: does insulin-food TIMING (pre-bolus) and/or DOSE predict the excursion?
Match each meal to its nearest fast bolus; measure offset, dose, calories, peak rise & dwell.
Within-subject standardised (removes per-person sensitivity), pooled. Spearman + partial corr.
T1D D1NAMO. Observational, confounded, not medical advice."""
import os,warnings,numpy as np,pandas as pd
from scipy import stats
warnings.filterwarnings("ignore")
T1D="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test/t1d";MG=18.0182
def grid(s):
    df=pd.read_csv(f"{T1D}/glucose_{s}.csv");c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce");c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MG
    c=c.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
    idx=pd.date_range(c.index[0].floor("5min"),c.index[-1].ceil("5min"),freq="5min")
    return c.reindex(c.index.union(idx)).sort_index().interpolate("time",limit=6).reindex(idx)
rows=[]
for s in [f"{i:03d}" for i in range(1,10)]:
    g=grid(s); gi=g.index; gv=g.values
    fd=pd.read_csv(f"{T1D}/food_{s}.csv");fd["ts"]=pd.to_datetime(fd["datetime"],format="%Y:%m:%d %H:%M:%S",errors="coerce");fd["cal"]=pd.to_numeric(fd["calories"],errors="coerce")
    ins=pd.read_csv(f"{T1D}/insulin_{s}.csv");ins["ts"]=pd.to_datetime(ins["date"]+" "+ins["time"],errors="coerce");ins["fast"]=pd.to_numeric(ins["fast_insulin"],errors="coerce").fillna(0)
    ib=ins.loc[ins["fast"]>0]
    for _,m in fd.dropna(subset=["ts","cal"]).iterrows():
        ft=m["ts"]
        dd=(ib["ts"]-ft).dt.total_seconds()/60.0
        near=dd[abs(dd)<=90]
        if len(near)==0: continue
        k=near.abs().idxmin(); offset=float(near[k]); dose=float(ib.loc[k,"fast"])
        j=gi.get_indexer([ft],method="nearest")[0]
        if j<0 or j+36>=len(gv): continue
        base=gv[j]; win=gv[j:j+37]
        if np.isnan(win).any(): continue
        peak=float(np.nanmax(win)-base)
        dwell=float(np.sum(gv[j:min(j+49,len(gv))]>180)*5)
        rows.append(dict(s=s,offset=offset,dose=dose,cal=m["cal"],base=base,peak=peak,dwell=dwell))
df=pd.DataFrame(rows)
print(f"matched meals: {len(df)} across {df['s'].nunique()} subjects")
# within-subject z-score
def zsub(col):
    return df.groupby("s")[col].transform(lambda x:(x-x.mean())/(x.std()+1e-9))
for c in ["offset","dose","cal","peak","dwell","base"]: df["z_"+c]=zsub(c)
d=df.dropna(subset=["z_offset","z_dose","z_cal","z_peak"])
def sp(a,b): r,p=stats.spearmanr(d[a],d[b]); return r,p
def partial(y,x,Z):
    import numpy as np
    Y=d[y].values; X=d[x].values; M=np.column_stack([d[z].values for z in Z]+[np.ones(len(d))])
    ry=Y-M@np.linalg.lstsq(M,Y,rcond=None)[0]; rx=X-M@np.linalg.lstsq(M,X,rcond=None)[0]
    r,p=stats.pearsonr(rx,ry); return r,p
print("\n=== PHASE (timing offset; +offset=insulin LATER) vs excursion ===")
for out in ["z_peak","z_dwell"]:
    r,p=sp("z_offset",out); print(f"  offset vs {out:8s}: Spearman r={r:+.2f} p={p:.3f}  (later insulin -> {'bigger' if r>0 else 'smaller'} excursion)")
print("  partial offset vs peak | dose,cal:", "r={:+.2f} p={:.3f}".format(*partial("z_peak","z_offset",["z_dose","z_cal"])))
print("\n=== GAIN (dose) vs excursion ===")
for out in ["z_peak","z_dwell"]:
    r,p=sp("z_dose",out); print(f"  dose   vs {out:8s}: Spearman r={r:+.2f} p={p:.3f}")
print("  partial dose vs peak | offset,cal:", "r={:+.2f} p={:.3f}".format(*partial("z_peak","z_dose",["z_offset","z_cal"])))
print("\n=== reference: meal size (calories) vs excursion ===")
r,p=sp("z_cal","z_peak"); print(f"  cal vs peak: r={r:+.2f} p={p:.3f}")
print("\noffset distribution (min): median",round(df['offset'].median(),0),"| %pre-bolus(<-5min):",round((df['offset']<-5).mean()*100),"| %together(+-5):",round((df['offset'].abs()<=5).mean()*100),"| %late(>5):",round((df['offset']>5).mean()*100))
