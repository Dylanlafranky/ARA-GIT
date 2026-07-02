"""Scale-free angle readout on the rock ladder.
Mapping (declared): ARA = 2*sphericity (form<->deform; 0=irregular,2=sphere);
phase_deg = ARA*180 (Dylan's rule: ARA 0-2 = 0-360deg) -> phase = 360*sphericity.
x = octave = log2(diameter). Slope d(phase)/d(octave) = degrees per octave = the 'twist'.
Test the rise (strength->gravity) & the drop (gravity->rotation) vs 36 / 30/45/60/72 + a shuffled null.
HONEST: mapping has freedom + the potato-radius transition is fuzzy; report slope, R2, null, sensitivity."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng=np.random.default_rng(0)
BODIES=[("silt",5e-5,0.65),("sand",5e-4,0.70),("granule",3e-3,0.68),("pebble",2e-2,0.72),
 ("cobble",1.5e-1,0.70),("boulder",1.0,0.60),("block",8.0,0.55),("Itokawa",5.4e2,0.48),
 ("Eros",1.7e4,0.42),("Phobos",2.2e4,0.70),("Hyperion",2.7e5,0.50),("Vesta",5.25e5,0.78),
 ("Mimas",3.96e5,0.95),("Ceres",9.4e5,0.97),("Enceladus",5.0e5,0.99),("Tethys",1.06e6,0.98),
 ("Moon",3.47e6,0.998),("Mars",6.78e6,0.994),("Earth",1.27e7,0.9966),("Saturn",1.16e8,0.902),("Jupiter",1.4e8,0.935)]
name=[b[0] for b in BODIES]; d=np.array([b[1] for b in BODIES]); s=np.array([b[2] for b in BODIES])
oct_=np.log2(d); phase=360.0*s          # declared mapping
def fit(mask):
    o=oct_[mask]; p=phase[mask]; A=np.vstack([o,np.ones_like(o)]).T
    sl,ic=np.linalg.lstsq(A,p,rcond=None)[0]; pred=A@[sl,ic]
    r2=1-np.sum((p-pred)**2)/np.sum((p-p.mean())**2) if len(p)>2 else np.nan
    return sl,ic,r2
rise=(oct_>=np.log2(1e4))&(oct_<=np.log2(1.1e6))   # transition window
drop=(oct_>=np.log2(3e6))                            # plateau -> gas giants
slr,icr,r2r=fit(rise); sld,icd,r2d=fit(drop)
def nearest(v): 
    cands=[30,36,45,60,72]; return min(cands,key=lambda c:abs(abs(v)-c))
print(f"RISE (strength->gravity): {slr:+.1f} deg/octave  R2={r2r:.2f}  nearest of[30,36,45,60,72]={nearest(slr)}")
print(f"DROP (gravity->rotation): {sld:+.1f} deg/octave  R2={r2d:.2f}  nearest={nearest(sld)}")
# NULL: shuffle sphericity across bodies, refit rise slope
null=[]
for _ in range(3000):
    sp=rng.permutation(s); ph=360*sp; o=oct_[rise]; p=ph[rise]
    A=np.vstack([o,np.ones_like(o)]).T; sl=np.linalg.lstsq(A,p,rcond=None)[0][0]; null.append(sl)
null=np.array(null); p_struct=np.mean(np.abs(null)>=abs(slr))
print(f"NULL rise slope: mean {null.mean():.1f}, 95% |slope|<= {np.percentile(np.abs(null),95):.1f} deg/oct ; p(|null|>=real)={p_struct:.3f}")
# sensitivity: alt mapping ARA centered (ridge at s=0.75 round/irregular balance?) and angle=ARA*90
phase2=90.0*(2*s); A=np.vstack([oct_[rise],np.ones(rise.sum())]).T
sl2=np.linalg.lstsq(A,phase2[rise],rcond=None)[0][0]
print(f"SENSITIVITY: angle=ARA*90 mapping -> rise {sl2:+.1f} deg/oct (half of the ARA*180 reading)")
print(f"VERDICT seed: rise ~{abs(slr):.0f} deg/oct under the declared map; 36 is {'plausible' if abs(abs(slr)-36)<12 else 'not the clean answer'}; transition R2={r2r:.2f} (fuzzy if low).")

# ---- visualise ----
fig,(a1,a2)=plt.subplots(1,2,figsize=(15,6.2),facecolor="#0e1116")
for ax in (a1,a2): ax.set_facecolor("#161b22"); ax.tick_params(colors="#9aa7b4")
COL=np.where(s<0.85,"#c98a4a",np.where(d>3e7,"#b197fc","#5aa0ff"))
# panel 1: sphericity vs log10 size (the raw curve)
x10=np.log10(d); o1=np.argsort(x10)
a1.plot(x10[o1],s[o1],color="#9aa7b4",lw=0.8,alpha=0.5)
a1.scatter(x10,s,s=60,c=COL,edgecolors="#0e1116",lw=0.7,zorder=3)
a1.axvspan(np.log10(2e5),np.log10(4e5),color="#5aa0ff",alpha=0.10)
for i,n in enumerate(name): a1.annotate(n,(x10[i],s[i]),xytext=(0,6),textcoords="offset points",fontsize=6.8,color="#cdd6e0",ha="center")
a1.set_xlabel("log₁₀ diameter (m)",color="#cbd5e1"); a1.set_ylabel("sphericity (form↔deform)",color="#cbd5e1")
a1.set_title("the curve (real bodies)",color="#e6edf3"); a1.set_ylim(0.3,1.05)
# panel 2: phase (deg) vs octave  — the 'side view'; angle readout
o2=np.argsort(oct_)
a2.scatter(oct_,phase,s=60,c=COL,edgecolors="#0e1116",lw=0.7,zorder=3)
# rise fit line + reference angles anchored at rise start
xs=np.array([oct_[rise].min(),oct_[rise].max()]); x0,y0=oct_[rise].min(),(360*s)[rise][np.argmin(oct_[rise])]
a2.plot(xs,icr+slr*xs,color="#ffd43b",lw=2,label=f"rise fit {slr:+.0f}°/oct (R²={r2r:.2f})")
for ang,c in [(36,"#5ad17e"),(45,"#888"),(60,"#888"),(72,"#888"),(30,"#888")]:
    a2.plot(xs, y0+ang*(xs-x0), color=c, ls="--", lw=1 if ang!=36 else 1.6, alpha=.9 if ang==36 else .5)
    a2.text(xs[1], y0+ang*(xs[1]-x0), f" {ang}°/oct", color=c, fontsize=8, va="center")
# null band around rise start
a2.fill_between(xs, y0+np.percentile(np.abs(null),5)*(xs-x0), y0+np.percentile(np.abs(null),95)*(xs-x0), color="#3a4a62", alpha=.25, label="shuffled-null slope band")
a2.set_xlabel("octave rung = log₂ diameter",color="#cbd5e1"); a2.set_ylabel("ARA phase (deg) = 360·sphericity",color="#cbd5e1")
a2.set_title("seen from the side: phase vs octave (the 'twist')",color="#e6edf3")
a2.legend(facecolor="#161b22",labelcolor="#cbd5e1",fontsize=8,loc="lower right")
plt.tight_layout(); out="rock_vertical_ARA_angle.png"; plt.savefig(out,dpi=150,facecolor="#0e1116"); print("saved",out)
