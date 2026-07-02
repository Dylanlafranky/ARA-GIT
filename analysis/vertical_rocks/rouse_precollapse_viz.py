"""Rouse-ARA BEFORE the D* collapse: real systems in (grain size, ARA) space, colored by medium,
with faint per-medium guide curves. This is the 'medium wave' state — each medium on its own line."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
C1=18.;C2=1.
MED={'Mars air':(0.020,5.5e-4,3.71),'Earth air':(1.2,1.5e-5,9.81),'Titan air':(5.3,1.1e-6,1.35),
'Venus air':(65.,5.4e-7,8.87),'Titan liquid':(615.,8.9e-7,1.35),'Water':(1000.,1.0e-6,9.81),
'Debris slurry':(1400.,1.0e-4,9.81),'Pyroclastic':(0.5,5.0e-5,9.81)}
MCOL={'Mars air':'#ff6b6b','Earth air':'#e0c060','Titan air':'#8b5cf6','Venus air':'#f59e0b',
'Titan liquid':'#22d3ee','Water':'#5aa0ff','Debris slurry':'#a3e635','Pyroclastic':'#fb923c'}
def ws(D,m,rs):
    rho,nu,g=m; R=rs/rho-1.0
    if R<=0: return np.nan
    return R*g*D**2/(C1*nu+np.sqrt(0.75*C2*R*g*D**3))
def ARA(s,W=2.0): return 1+np.tanh(np.log(s)/W)
SYS=[("Aeolian dune","Earth air",0.25e-3,2650,0.40),("Aeolian ripple","Earth air",0.30e-3,2650,0.30),
("Blowing snow","Earth air",0.20e-3,250,0.35),("Dust storm","Earth air",0.020e-3,2650,0.50),
("Loess fallout","Earth air",0.030e-3,2650,0.05),("Gravel-bed river","Water",30e-3,2650,0.15),
("Sand-bed river","Water",0.40e-3,2650,0.08),("River-mouth delta","Water",0.10e-3,2650,0.02),
("Floodplain mud","Water",0.010e-3,2650,0.01),("Turbidity current","Water",0.10e-3,2650,0.50),
("Beach swash","Water",0.30e-3,2650,0.05),("Alluvial fan","Water",5.0e-3,2650,0.20),
("Subglacial stream","Water",10e-3,2650,0.25),("Debris flow","Debris slurry",50e-3,2650,0.50),
("Lahar","Debris slurry",5.0e-3,2650,0.40),("Pyroclastic flow","Pyroclastic",0.10e-3,2650,1.00),
("Mars dune","Mars air",0.15e-3,3000,1.00),("Mars dust","Mars air",0.003e-3,3000,1.00),
("Venus dune","Venus air",0.15e-3,2900,0.04),("Titan river","Titan liquid",5.0e-3,950,0.05),
("Titan dune","Titan air",0.25e-3,950,0.04),("Titan delta","Titan liquid",0.10e-3,950,0.01)]

fig,ax=plt.subplots(figsize=(14.5,7.6),facecolor="#0e1116"); ax.set_facecolor("#161b22")
ax.tick_params(colors="#9aa7b4"); ax.grid(False)
# faint guide curves per medium (reference grain 2650, u*=1.5x threshold)
Dg=np.logspace(np.log10(2e-6),np.log10(0.1),300)
for md,(rho,nu,g) in MED.items():
    R=2650/rho-1.0
    if R<=0: continue
    us=1.5*0.1*np.sqrt(R*g*Dg); a=ARA(ws(Dg,MED[md],2650)/us)
    ax.plot(Dg*1e3,a,color=MCOL[md],lw=1.3,alpha=0.35,zorder=1)
# real systems as points
for nm,md,D,rs,us in SYS:
    a=ARA(ws(D,MED[md],rs)/us)
    ax.scatter(D*1e3,a,s=120,c=MCOL[md],edgecolors="#0e1116",lw=1,zorder=3)
    ax.annotate(nm,(D*1e3,a),textcoords="offset points",xytext=(0,9),fontsize=7,color="#e6edf3",ha="center")
ax.axhline(1.0,color="#ffd479",lw=1,ls="--",alpha=0.6); ax.text(1.3e-3,1.03,"ridge s=1",color="#ffd479",fontsize=8)
ax.text(1.3e-3,1.9,"deposition pole",color="#ff8a8a",fontsize=8); ax.text(1.3e-3,0.06,"suspension pole",color="#ff8a8a",fontsize=8)
ax.set_xscale("log"); ax.set_xlabel("real grain size D (mm)",color="#cbd5e1")
ax.set_ylabel("vertical-ARA  (from Rouse s = w_s/u*)",color="#cbd5e1")
ax.set_ylim(-0.05,2.05)
ax.set_title("Rouse-ARA BEFORE the collapse — each medium on its own curve (the medium wave)\n"
             "real systems (points) fanned by medium; faint lines = per-medium guides. Same shape, shifted by fluid.",
             color="#e6edf3",fontsize=12.5)
import matplotlib.patches as mp
ax.legend(handles=[mp.Patch(color=MCOL[k],label=k) for k in MED],facecolor="#161b22",labelcolor="#cbd5e1",fontsize=8,ncol=2,loc="center right")
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rouse_precollapse.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116"); print("saved",out)
