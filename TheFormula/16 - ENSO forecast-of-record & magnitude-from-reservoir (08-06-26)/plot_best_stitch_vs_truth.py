import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B, enso_combined_horizon_feeder as C
W=B.load_wwv("wwv_west.dat");E=B.load_wwv("wwv_east.dat");nino=B.load_nino("nino34_long_anom.csv")
SOI=B.load_soi("soi.data");PDO=B.load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat");IOD=C.load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
bk=sorted(set(W)&set(E)&set(nino)&set(SOI)&set(PDO)&set(IOD))
T=np.array([nino[k] for k in bk]);Wv=np.array([W[k] for k in bk]);Ev=np.array([E[k] for k in bk])
Sv=np.array([SOI[k] for k in bk]);yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in bk]);mon=np.array([int(k[4:6]) for k in bk])
def build(extra):
    cols=[T,Wv,Ev,Sv];stdz=[1,2,3]
    for d in extra: cols.append(np.array([d[k] for k in bk]));stdz.append(len(cols)-1)
    return cols,stdz
# the documented stitch: +IOD for short/mid, +PDO for long
recI=B.walk_switch(*build([IOD]),yr,mon,T)
recP=B.walk_switch(*build([PDO]),yr,mon,T)
def series(rec,h):
    oy=np.array(rec[h]['oy']);pr=np.array(rec[h]['pred']);tr=np.array(rec[h]['truth']);m=oy>=2016
    return oy[m]+h/12, pr[m], tr[m]
def cc(a,b):return np.corrcoef(a,b)[0,1]
fig,(a1,a2)=plt.subplots(2,1,figsize=(14,8),sharex=True);fig.patch.set_facecolor("white")
for ax,(rec,h,lab) in zip((a1,a2),[(recI,6,"IOD stitch, 6-month lead"),(recP,24,"PDO stitch, 24-month lead")]):
    ty,pr,tr=series(rec,h)
    ax.axhline(0,color="k",lw=.6);ax.axhline(0.5,color="#d62728",lw=.7,ls=":");ax.axhline(-0.5,color="#1f77b4",lw=.7,ls=":")
    ax.plot(ty,tr,color="#111",lw=2,label="truth")
    ax.plot(ty,pr,color="#1f77b4" if h==6 else "#7a5195",lw=1.7,label=f"ARA feeder-stitch forecast")
    ax.fill_between(ty,tr,pr,color="grey",alpha=.12)
    ax.set_title(f"{lab}  —  correlation {cc(pr,tr):+.2f}",fontweight="bold",fontsize=10.5)
    ax.set_ylabel("NINO3.4 (°C)");ax.legend(fontsize=9,loc="upper right");ax.grid(alpha=.2)
a2.set_xlabel("year")
fig.suptitle("ENSO — our BEST documented method (IOD+PDO feeder stitch) vs truth (strict-causal, held-out 2016-2025)",fontsize=12,fontweight="bold",y=1.0)
fig.tight_layout(rect=[0,0,1,0.96])
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_best_stitch_vs_truth.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
print(f"6mo corr {cc(*series(recI,6)[1:]):+.3f} | 24mo corr {cc(*series(recP,24)[1:]):+.3f}")
