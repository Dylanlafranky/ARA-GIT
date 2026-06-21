import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
PHI=F.PHI
def load_dmi(p,miss=-9990.0):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==13 and s[0].isdigit() and len(s[0])==4:
            for mo in range(1,13):
                try:v=float(s[mo])
                except:continue
                if v>miss:d[f"{int(s[0])}{mo:02d}"]=v
    return d
W=B.load_wwv("wwv_west.dat");Ee=B.load_wwv("wwv_east.dat");nino=B.load_nino("nino34_long_anom.csv")
SOI=B.load_soi("soi.data");PDO=B.load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat");IOD=load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
rungs=[12*PHI**k for k in range(7)]
def arr(d,k): return np.array([d[x] for x in k])
def rung_energy(x):
    x=np.asarray(x,float)-np.nanmean(x); return np.array([np.nanvar(F.causal_bandpass(x,P,0.20)) for P in rungs])
systems={"NINO (surface engine)":(nino,"#c47f00"),"SOI (atmosphere)":(SOI,"#8a6d3b"),
         "WWV (subsurface reservoir)":(W,"#1f77b4"),"IOD (fast donor)":(IOD,"#2ca02c"),
         "PDO (slow clock)":(PDO,"#d62728")}
ck=sorted(set.intersection(set(nino),set(SOI),set(W),set(PDO),set(IOD)))
fig,(ax,ax2)=plt.subplots(1,2,figsize=(15,6.2),gridspec_kw={'width_ratios':[1.7,1]}); fig.patch.set_facecolor("white")
x=np.arange(len(rungs)); wid=0.16
for i,(nm,(d,c)) in enumerate(systems.items()):
    f=rung_energy(arr(d,ck)); f=f/f.sum()
    ax.bar(x+(i-2)*wid,f*100,wid,color=c,label=nm)
ax.set_xticks(x); ax.set_xticklabels([f"{r:.0f}mo" for r in rungs])
ax.set_xlabel("φ-rung (period) — the pipe ladder"); ax.set_ylabel("% of system energy in this rung")
ax.set_title("Wave breakdown: where each ENSO subsystem stores its energy",fontweight="bold")
ax.axhline(80.9,color="k",ls="--",lw=1); ax.text(5.7,82,"pipe saturation φ/2 = 80.9%",fontsize=8,ha="right")
ax.legend(fontsize=8.5); ax.grid(alpha=.2,axis="y")
ax.annotate("IOD peaks FAST\n→ lifts short horizons",(1,31),(1.4,52),fontsize=8,color="#2ca02c",arrowprops=dict(arrowstyle="->",color="#2ca02c"))
ax.annotate("PDO peaks SLOW\n→ holds long horizons",(5,26),(3.5,44),fontsize=8,color="#d62728",arrowprops=dict(arrowstyle="->",color="#d62728"))
ax.annotate("WWV + NINO peak at\nthe 51mo ENGINE rung",(3,42),(3.0,62),fontsize=8,color="#1f77b4",arrowprops=dict(arrowstyle="->",color="#1f77b4"))
# right panel: NINO cascade vs framework constants
en=rung_energy(arr(nino,ck)); en=en/en.max()
ax2.plot(x,en,"o-",color="#c47f00",lw=2,label="NINO rung energy")
ax2.axvline(3,color="#1f77b4",ls=":",alpha=.6); ax2.text(3.05,0.5,"engine\n51mo",fontsize=8,color="#1f77b4")
ax2.set_xticks(x); ax2.set_xticklabels([f"{r:.0f}" for r in rungs],fontsize=8)
ax2.set_xlabel("φ-rung (mo)"); ax2.set_ylabel("energy (norm to peak)")
ax2.set_title("ENSO fills the engine rung,\nthen sheds ~1/φ³ above it",fontweight="bold",fontsize=10)
ax2.grid(alpha=.2)
post=en[4]/en[3]
ax2.annotate(f"drop after engine\n= {post:.2f} ≈ 1/φ³ ({1/PHI**3:.2f})",(4,en[4]),(2.2,0.72),fontsize=8,arrowprops=dict(arrowstyle="->"))
fig.suptitle("ENSO energy through the pipe: no single wave fills it (max 42% < 81% saturation) → spread energy = framework has headroom",
             fontsize=12.5,fontweight="bold",y=1.0)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/TheFormula/ARA_enso_energy_pipe_breakdown.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white"); print("saved",out)
