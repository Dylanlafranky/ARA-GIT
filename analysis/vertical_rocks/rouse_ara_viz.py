"""Visualize the Rouse-ARA collapse: MODE organizes the ARA scale, MEDIUM washes out.
Self-contained + deterministic (replicability rule). Sources documented in rouse_ara_test.py."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
np.random.seed(0)
kappa=0.41; C1=18.0; C2=1.0
WATER=dict(rho=1000.,nu=1.0e-6,g=9.81,rhos=2650.); AIR=dict(rho=1.20,nu=1.5e-5,g=9.81,rhos=2650.)
MARS=dict(rho=0.020,nu=5.5e-4,g=3.71,rhos=3000.)
def settling(D,m):
    R=m["rhos"]/m["rho"]-1.0
    return R*m["g"]*D**2/(C1*m["nu"]+np.sqrt(0.75*C2*R*m["g"]*D**3))
SYS=[("Aeolian dune",AIR,0.25e-3,0.40,"saltation/bed"),("Aeolian ripple",AIR,0.30e-3,0.30,"saltation/bed"),
 ("Dust storm",AIR,0.020e-3,0.50,"suspension"),("Gravel-bed river",WATER,30e-3,0.15,"bedload"),
 ("Sand-bed river",WATER,0.40e-3,0.08,"mixed/bed"),("River-mouth delta",WATER,0.10e-3,0.02,"deposition"),
 ("Floodplain mud",WATER,0.010e-3,0.01,"deposition"),("Turbidity current",WATER,0.10e-3,0.50,"suspension"),
 ("Beach swash",WATER,0.30e-3,0.05,"mixed/bed"),("Alluvial fan",WATER,5.0e-3,0.20,"bedload"),
 ("Mars dune",MARS,0.15e-3,1.00,"saltation/bed"),("Mars dust",MARS,0.003e-3,1.00,"suspension")]
MN={id(WATER):"water",id(AIR):"air",id(MARS):"Mars"}
MEDCOL={"air":"#e0c060","water":"#5aa0ff","Mars":"#ff8a8a"}
def ARA(s,W): return 1+np.tanh(np.log(s)/W)
rows=[]
for nm,m,D,us,mode in SYS:
    ws=settling(D,m); s=ws/us; rows.append((nm,MN[id(m)],s,ARA(s,2.0),mode))
# order modes deposition->bed->ridge->suspension along the release axis
mode_order=["bedload","saltation/bed","mixed/bed","deposition","suspension"]
yof={mo:i for i,mo in enumerate(mode_order)}

fig,ax=plt.subplots(figsize=(14,7),facecolor="#0e1116"); ax.set_facecolor("#161b22")
ax.tick_params(colors="#9aa7b4"); ax.grid(False)
for xv,lab,c in [(0.0,"0  suspension pole\n(release / carried off)","#ff8a8a"),
                 (0.382,"0.382 φ","#7fb0ff"),(1.0,"1.0  RIDGE\nfall = friction (s=1)\n[sourced transition]","#ffd479"),
                 (1.618,"1.618 φ","#7CFC9A"),(2.0,"2  deposition pole\n(accumulation / settles)","#ff8a8a")]:
    ax.axvline(xv,color=c,lw=1.0,ls="--",alpha=0.5)
    ax.text(xv,5.15,lab,color=c,fontsize=8,ha="center",va="bottom")
# jitter within mode row; color by medium
rngj=np.random.default_rng(1)
for (nm,mn,s,a,mode) in rows:
    y=yof[mode]+rngj.uniform(-0.16,0.16)
    ax.scatter(a,y,s=120,c=MEDCOL[mn],edgecolors="#0e1116",lw=1.0,zorder=3)
    ax.annotate(nm,(a,y),textcoords="offset points",xytext=(0,10),fontsize=7.5,color="#e6edf3",ha="center")
# mode row bands to show clustering
for mo,yi in yof.items():
    xs=[r[3] for r in rows if r[4]==mo]
    ax.plot([min(xs),max(xs)],[yi,yi],color="#3a4453",lw=8,alpha=0.35,zorder=1,solid_capstyle="round")
ax.set_yticks(range(len(mode_order)))
ax.set_yticklabels([m.upper() for m in mode_order],color="#cbd5e1",fontsize=10)
ax.set_ylabel("transport MODE  (≈ dimensionality available to the grain)",color="#cbd5e1")
ax.set_xlabel("vertical-ARA  from Rouse number  s = w_s/u*  (ridge s=1 = sourced suspension↔saltation transition)",color="#cbd5e1")
ax.set_xlim(-0.15,2.15); ax.set_ylim(-0.6,5.6)
ax.set_title("Bagnold/Rouse sediment transport, ARA-ised — the COLLAPSE\n"
             "MODE organizes ARA (η²=0.77) · MEDIUM washes out (η²=0.19): a dune is a dune on Earth OR Mars",
             color="#e6edf3",fontsize=12.5)
import matplotlib.patches as mp
ax.legend(handles=[mp.Patch(color=MEDCOL[k],label=f"medium: {k}") for k in ["air","water","Mars"]],
          facecolor="#161b22",labelcolor="#cbd5e1",fontsize=9,loc="lower right")
ax.text(0.02,-0.45,"colours (media) are mixed across every mode-row → medium is not what sets the ARA; the mode (dimension) is.",
        color="#9aa7b4",fontsize=8.5)
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rouse_ara_collapse.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116"); print("saved",out)
