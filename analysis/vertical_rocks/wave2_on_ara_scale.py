"""Wave 2 (formation->erosion) redrawn ON the 0-2 ARA scale.
 A: y = ARA, ridge-anchored (build-time == destroy-time -> 1.0), phi-lines, convention band.
 B: raw log-ratio curve where the 108-degree pentagon kink actually lives."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

BODIES=[("Itokawa",0.165,"S"),("Bennu",0.268,"S"),("Ryugu",0.478,"S"),("Eros",8.07,"S"),
("Gaspra",5.93,"S"),("Ida",15.2,"S"),("Deimos",6.34,"S"),("Phobos",11.05,"S"),
("Mathilde",26.4,"S"),("Lutetia",48.8,"S"),("Epimetheus",58.2,"S"),("Janus",89.9,"S"),
("Amalthea",83.0,"S"),("Hyperion",135.,"S"),("Proteus",208.7,"T"),("Mimas",198.2,"G"),
("Vesta",261.,"T"),("Pallas",256.,"T"),("Miranda",235.7,"G"),("Enceladus",252.,"G"),
("Ceres",469.,"G"),("Tethys",531.,"G"),("Dione",561.,"G"),("Rhea",763.,"G"),
("Iapetus",734.,"G"),("Titania",788.,"G"),("Moon",1737.,"G"),("Mars",3389.,"G"),("Earth",6371.,"G")]
COL={"S":"#c98a4a","T":"#e0c060","G":"#5aa0ff"}
names=[b[0] for b in BODIES]; R=np.array([b[1] for b in BODIES]); reg=[b[2] for b in BODIES]
logR=np.log10(R*1000.)
fa_x=np.array([-2,3,5,6,6.8]); fa_y=np.array([3.0,4.5,5.5,6.5,7.7])
logTform=np.interp(logR,fa_x,fa_y)
D=2*R
logTerode=np.minimum(np.log10(0.3e9)+1.1*np.log10(D/0.8),np.log10(4.6e9))
logratio=logTerode-logTform
def ARA(W): return 1+np.tanh(logratio/W)

o=np.argsort(logR); lr=logR[o]; rt=logratio[o]; nmo=np.array(names)[o]; rego=np.array(reg)[o]
pk=int(np.argmax(rt))

fig,(axA,axB)=plt.subplots(1,2,figsize=(17,7),facecolor="#0e1116")
for ax in (axA,axB): ax.set_facecolor("#161b22"); ax.tick_params(colors="#9aa7b4"); ax.grid(False)
LAB={"S":"strength / cohesion","T":"transition","G":"gravity (rounded)"}

# ---------- Panel A : ON the ARA scale ----------
# phi / landmark lines
for yv,lab,c in [(2.0,"2.0  time singularity (pole)","#ff8a8a"),
                 (1.618,"1.618  time-φ  (handover)","#7CFC9A"),
                 (1.0,"1.0  ridge  (build = destroy)","#ffd479"),
                 (0.382,"0.382  space-φ  (empty for solids)","#7fb0ff")]:
    axA.axhline(yv,color=c,lw=1.0,ls="--",alpha=0.55)
    axA.text(logR.min()-0.15,yv,lab,color=c,fontsize=8.5,va="center",ha="right")
# convention band (W=2 upper, W=4 lower) + primary W=3 line
aU=ARA(2.0)[o]; aL=ARA(4.0)[o]; aM=ARA(3.0)[o]
axA.fill_between(lr,aL,aU,color="#5aa0ff",alpha=0.10,zorder=1,label="convention band (W=2→4)")
axA.plot(lr,aM,color="#9aa7b4",lw=1.2,alpha=0.6,zorder=2)
for i in range(len(BODIES)):
    axA.scatter(logR[i],ARA(3.0)[i],s=60,c=COL[reg[i]],edgecolors="#0e1116",lw=0.8,zorder=3)
    if names[i] in ("Itokawa","Eros","Gaspra","Hyperion","Mimas","Ceres","Moon","Mars","Earth"):
        axA.annotate(names[i],(logR[i],ARA(3.0)[i]),textcoords="offset points",
                     xytext=(0,-11 if names[i] in("Earth","Moon","Mars") else 7),
                     fontsize=8,color="#e6edf3",ha="center")
axA.set_xlim(logR.min()-2.2,logR.max()+0.3)
axA.set_ylim(0.25,2.05)
axA.set_xlabel("log₁₀ mean radius (m)",color="#cbd5e1")
axA.set_ylabel("ARA  (ridge-anchored: build-time = destroy-time → 1.0)",color="#cbd5e1")
axA.set_title("WAVE 2 on the 0–2 ARA scale\nwhole ladder rides the TIME side · asteroids→pole · planets→φ-handover",
              color="#e6edf3",fontsize=12)
import matplotlib.patches as mp
axA.legend(handles=[mp.Patch(color=COL[k],label=LAB[k]) for k in ["S","T","G"]],
           facecolor="#161b22",labelcolor="#cbd5e1",fontsize=8,loc="lower left")

# ---------- Panel B : raw log-ratio curve with the 108-degree kink ----------
for k in ["S","T","G"]:
    idx=[i for i in range(len(BODIES)) if reg[i]==k]
    axB.scatter(logR[idx],logratio[idx],s=60,c=COL[k],edgecolors="#0e1116",lw=0.8,zorder=3)
axB.plot(lr,rt,color="#9aa7b4",lw=1.0,alpha=0.4,zorder=1)
# limb fits (equal-decade convention)
sr=np.polyfit(lr[:pk+1],rt[:pk+1],1); sf=np.polyfit(lr[pk:],rt[pk:],1)
xr=np.array([lr[0],lr[pk]]); xf=np.array([lr[pk],lr[-1]])
axB.plot(xr,np.polyval(sr,xr),color="#7CFC9A",lw=2,alpha=0.9)
axB.plot(xf,np.polyval(sf,xf),color="#ff8a8a",lw=2,alpha=0.9)
ang_r=np.degrees(np.arctan(sr[0])); ang_f=np.degrees(np.arctan(sf[0])); inc=180-abs(ang_r)-abs(ang_f)
axB.scatter([lr[pk]],[rt[pk]],s=140,facecolors="none",edgecolors="#7CFC9A",lw=1.8,zorder=4)
axB.annotate(f"peak · Gaspra/Eros (R≈6 km)\nkink = {inc:.0f}°  (regular-pentagon interior angle)",
             (lr[pk],rt[pk]),textcoords="offset points",xytext=(12,-4),fontsize=9,color="#7CFC9A")
axB.text(lr[2],rt[pk]-0.55,f"rising  +{ang_r:.0f}°",color="#7CFC9A",fontsize=9)
axB.text(lr[-6],rt[-4]+0.35,f"falling  {ang_f:.0f}°",color="#ff8a8a",fontsize=9)
for nm in ("Itokawa","Eros","Gaspra","Hyperion","Mimas","Ceres","Moon","Earth"):
    i=names.index(nm)
    axB.annotate(nm,(logR[i],logratio[i]),textcoords="offset points",xytext=(0,7),fontsize=7.5,color="#cdd6e0",ha="center")
axB.set_xlabel("log₁₀ mean radius (m)   ·   1 decade",color="#cbd5e1")
axB.set_ylabel("log₁₀(T_erosion / T_formation)   ·   1 decade",color="#cbd5e1")
axB.set_title("where the angle lives (equal-decade axes)\nrising +32° · falling −40° · included 108°  — convention-dependent, flagged",
              color="#e6edf3",fontsize=12)
axB.set_aspect('equal', adjustable='box')

out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/wave2_on_ara_scale.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116"); print("saved",out)
print(f"kink included angle = {inc:.1f}deg ; rising {ang_r:.1f} ; falling {ang_f:.1f}")
