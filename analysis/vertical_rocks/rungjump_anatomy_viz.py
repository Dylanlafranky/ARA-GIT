"""Anatomy of a RUNG JUMP, drawn on the real potato data — the stuck→cross→taper story."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
B=[("Itokawa",(0.268,0.147,0.104)),("Eros",(17.2,5.6,5.6)),("Gaspra",(9.1,5.2,4.4)),("Ida",(29.9,12.7,9.3)),
("Bennu",(0.283,0.272,0.249)),("Ryugu",(0.502,0.495,0.440)),("Mathilde",(33.,24.,23.)),("Lutetia",(60.5,50.5,37.5)),
("Phobos",(13.,11.4,9.1)),("Deimos",(7.5,6.1,5.5)),("Amalthea",(125.,73.,64.)),("Janus",(101.7,93.,76.3)),
("Epimetheus",(64.9,57.3,53.)),("Hyperion",(180.1,133.,102.7)),("Vesta",(286.3,278.6,223.2)),("Pallas",(275.,258.,238.)),
("Proteus",(218.,208.,201.)),("Mimas",(207.8,196.7,190.6)),("Miranda",(240.,234.2,232.9)),("Enceladus",(256.6,251.4,248.3)),
("Ceres",(482.1,482.1,445.9)),("Tethys",(538.4,528.3,526.3)),("Dione",(563.4,561.3,559.6)),("Rhea",(765.,763.1,762.4)),
("Iapetus",(745.7,745.7,712.1)),("Titania",(788.4,788.4,788.4)),("Moon",(1738.1,1738.1,1736.)),("Mars",(3396.2,3396.2,3376.2)),
("Earth",(6378.1,6378.1,6356.8)),("Saturn",(60268.,60268.,54364.)),("Jupiter",(71492.,71492.,66854.))]
names=[b[0] for b in B]
Rm=np.array([(b[1][0]*b[1][1]*b[1][2])**(1/3.) for b in B]); ca=np.array([b[1][2]/b[1][0] for b in B])
x=np.log10(Rm*1000.); m=np.array([n not in("Saturn","Jupiter") for n in names])
def log150(x,lo,hi,x0,k): return lo+(hi-lo)/(1+np.exp(-k*(x-x0)))
p,_=curve_fit(log150,x[m],ca[m],p0=[0.6,0.98,5.2,6],maxfev=40000); x0=p[2]

fig,ax=plt.subplots(figsize=(14.5,7.6),facecolor="#0e1116"); ax.set_facecolor("#12161c")
ax.tick_params(colors="#9aa7b4"); ax.grid(False)
# three zones
ax.axvspan(x.min()-0.3,x0-0.25,color="#c98a4a",alpha=0.10)
ax.axvspan(x0-0.25,x0+0.35,color="#7CFC9A",alpha=0.12)
ax.axvspan(x0+0.35,x.max()+0.4,color="#5aa0ff",alpha=0.09)
# gravity>strength crossover band (42-338 km)
ax.axvspan(np.log10(42e3),np.log10(338e3),color="#7CFC9A",alpha=0.10)
xs=np.linspace(x.min()-0.3,x.max()+0.4,400)
ax.plot(xs,log150(xs,*p),color="#eaeff5",lw=2.6,zorder=4)
for i in range(len(B)):
    if names[i] in("Saturn","Jupiter"):
        ax.scatter(x[i],ca[i],s=80,marker="v",c="#b197fc",edgecolors="#0e1116",lw=0.8,zorder=5)
    else:
        col="#c98a4a" if x[i]<x0 else "#5aa0ff"
        ax.scatter(x[i],ca[i],s=70,c=col,edgecolors="#0e1116",lw=0.8,zorder=5)
for nm,dy in [("Itokawa",8),("Eros",-14),("Ida",-14),("Bennu",8),("Hyperion",-14),("Mimas",9),("Ceres",8),("Earth",9),("Saturn",-15)]:
    i=names.index(nm); ax.annotate(nm,(x[i],ca[i]),textcoords="offset points",xytext=(0,dy),fontsize=7.5,color="#cdd6e0",ha="center")
# zone headline labels
ax.text((x.min()-0.3+x0-0.25)/2,0.40,"① STUCK AT THE SINGULARITY",color="#e0a45a",fontsize=11,ha="center",fontweight="bold")
ax.text((x.min()-0.3+x0-0.25)/2,0.36,"base units (grain strength) can't cross\nsize↔roundness ρ=−0.03 (p=0.91): flat & scattered",color="#c98a4a",fontsize=8.5,ha="center")
ax.text(x0+0.05,0.47,"② THE CROSSING",color="#7CFC9A",fontsize=11,ha="center",fontweight="bold")
ax.text(x0+0.05,0.435,"self-gravity overtakes\nstrength (~10 MPa)\nat ~166 km → sharp jump",color="#7CFC9A",fontsize=8.5,ha="center")
ax.text((x0+0.35+x.max()+0.4)/2,0.55,"③ TAPER TO THE MAX",color="#7fb0ff",fontsize=11,ha="center",fontweight="bold")
ax.text((x0+0.35+x.max()+0.4)/2,0.51,"higher component (gravity) drives the climb\nρ=+0.78 (p<0.001) → saturates at a sphere",color="#5aa0ff",fontsize=8.5,ha="center")
# rinse & repeat arrow to gas giants
ig=names.index("Saturn")
ax.annotate("④ RINSE & REPEAT →\nnext rung: rotational flattening\n(new higher component = spin)",
            (x[ig],ca[ig]),textcoords="offset points",xytext=(-4,-58),fontsize=8.5,color="#b197fc",ha="center",
            arrowprops=dict(arrowstyle="->",color="#b197fc",lw=1.3))
ax.axvline(x0,color="#ffd479",lw=1,ls="--",alpha=0.6)
ax.text(x0,1.005,"potato radius ≈166 km",color="#ffd479",fontsize=8,ha="center")
ax.set_xlabel("log₁₀ mean radius (m)  —  climbing the size ladder →",color="#cbd5e1",fontsize=10)
ax.set_ylabel("roundness  c/a  (1 = perfect sphere)",color="#cbd5e1",fontsize=10)
ax.set_ylim(0.30,1.04); ax.set_xlim(x.min()-0.35,x.max()+0.45)
ax.set_title("Anatomy of a rung jump — the S-curve is one 0→2 ARA crossing\n"
             "base units stall at the pole · an emergent HIGHER component crosses the octave · it tapers at its max · repeat",
             color="#e6edf3",fontsize=12.5)
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rungjump_anatomy.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116"); print("saved",out)
