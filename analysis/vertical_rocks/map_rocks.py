"""Vertical ARA — rock to planet ladder. Real representative values.
Map sphericity (form<->deform: irregular vs gravity-equilibrium round) vs log-size
(octave rungs). The substrate SWAP shows as regime transitions:
 cohesion/strength -> gravity-rounding (potato radius ~300km) -> rotational flattening.
Let the curve emerge; mark where it re-anchors; defer the 36-deg readout."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
# (name, diameter_m, sphericity 0-1 [1=perfect sphere], regime)
BODIES=[
 ("silt",5e-5,0.65,"S"),("sand",5e-4,0.70,"S"),("granule",3e-3,0.68,"S"),
 ("pebble",2e-2,0.72,"S"),("cobble",1.5e-1,0.70,"S"),("boulder",1.0,0.60,"S"),
 ("block",8.0,0.55,"S"),("Itokawa",5.4e2,0.48,"S"),("Eros",1.7e4,0.42,"S"),
 ("Phobos",2.2e4,0.70,"S"),("Hyperion",2.7e5,0.50,"S"),("Vesta",5.25e5,0.78,"T"),
 ("Mimas",3.96e5,0.95,"G"),("Ceres",9.4e5,0.97,"G"),("Enceladus",5.0e5,0.99,"G"),
 ("Tethys",1.06e6,0.98,"G"),("Moon",3.47e6,0.998,"G"),("Mars",6.78e6,0.994,"G"),
 ("Earth",1.27e7,0.9966,"G"),("Saturn",1.16e8,0.902,"R"),("Jupiter",1.4e8,0.935,"R")]
COL={"S":"#c98a4a","T":"#e0c060","G":"#5aa0ff","R":"#b197fc"}
LAB={"S":"strength / cohesion","T":"transition","G":"gravity (rounded)","R":"rotational flattening"}
d=np.array([b[1] for b in BODIES]); s=np.array([b[2] for b in BODIES]); reg=[b[3] for b in BODIES]
x=np.log10(d)
fig,ax=plt.subplots(figsize=(12,6.5),facecolor="#0e1116"); ax.set_facecolor("#161b22")
# octave rungs (x2) light gridlines on a log2 sense
for xv in np.arange(-5,9):
    ax.axvline(xv,color="#222a33",lw=0.5)
# potato radius band ~200-400 km
ax.axvspan(np.log10(2e5),np.log10(4e5),color="#5aa0ff",alpha=0.10)
ax.text(np.log10(3e5),0.40,"potato radius\n(strength→gravity)",color="#7fb0ff",fontsize=9,ha="center")
# the curve (sorted by size)
o=np.argsort(x)
ax.plot(x[o],s[o],color="#9aa7b4",lw=1.0,alpha=0.5,zorder=1)
for b in BODIES:
    xv=np.log10(b[1]); ax.scatter(xv,b[2],s=70,c=COL[b[3]],edgecolors="#0e1116",lw=0.8,zorder=3)
    ax.annotate(b[0],(xv,b[2]),textcoords="offset points",xytext=(0,7),fontsize=7.5,color="#cdd6e0",ha="center")
ax.set_xlabel("log₁₀ diameter (m)   ·   each gridline ≈ one decade; octave rungs ×2",color="#cbd5e1")
ax.set_ylabel("sphericity  (form ↔ deform : irregular → gravity-round)",color="#cbd5e1")
ax.set_title("Vertical ARA — the rock→planet ladder (real bodies)\nthe rule re-anchors at each substrate swap",color="#e6edf3",fontsize=13)
ax.set_ylim(0.3,1.04); ax.tick_params(colors="#9aa7b4")
import matplotlib.patches as mp
ax.legend(handles=[mp.Patch(color=COL[k],label=LAB[k]) for k in ["S","T","G","R"]],
          facecolor="#161b22",labelcolor="#cbd5e1",fontsize=9,loc="lower right")
ax.grid(False)
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rock_ladder_curve.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116")
print("saved",out)
# quick characterisation of the gravity-rounding rise (scale-free-ish)
strength=[b for b in BODIES if b[3] in("S","T")]; grav=[b for b in BODIES if b[3]=="G"]
print(f"strength-regime mean sphericity {np.mean([b[2] for b in strength]):.2f} (n={len(strength)})")
print(f"gravity-regime mean sphericity {np.mean([b[2] for b in grav]):.2f} (n={len(grav)})")
print(f"rotational (gas giants) {np.mean([b[2] for b in BODIES if b[3]=='R']):.2f}")
print("Two substrate swaps visible: strength→gravity (~potato radius) rise, gravity→rotational drop.")
