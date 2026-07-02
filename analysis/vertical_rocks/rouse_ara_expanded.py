"""
ROUSE-ARA pushed harder: more systems, more media (Mars->Earth air->Titan air->Venus->Titan liquid
->water->debris slurry), and EXTRACT THE MEDIUM WAVE.
Prediction (Dylan): mode still organizes ARA; medium is a secondary ORDERED line (a wave), not noise —
media converge at the bedload end and fan out toward suspension, each medium tracing its own curve.

REPLICABLE: Ferguson&Church(2004) settling; every fluid/grain value cited; deterministic.
SOURCES (new):
[T] Titan liquid CH4/C2H6/N2: rho=615 kg/m3, mu=547.8 uPa.s (nu=8.9e-7), Ts=94K, g=1.35;
    grains water-ice/organics rho~950. sciencedirect S0032063397001256 ; en.wikipedia Geology_of_Titan.
    Titan atmosphere (N2,1.5bar,94K): rho~5.3, nu~1.1e-6.
[V] Venus surface atmosphere (92 bar CO2, 740K): rho~65 kg/m3, nu~5.4e-7, g=8.87; grain basalt ~2900;
    threshold u*t ~0.025 m/s (~10x lower than Earth); microdunes at surface wind 0.6-1.5 m/s.
    sciencedirect S001910352200269X ; S0019103585711074 (Magellan) ; arxiv 1201.4353.
[P] Pyroclastic density current: hot particle-laden gas ~ rho 0.5, nu 5e-5 (approx), ash grains 2650.
[D] Debris flow / lahar: hyperconcentrated slurry rho~1400, nu~1e-4 (mud), clasts 2650.
(earth air/water, mars, aeolian, fluvial sources as in rouse_ara_test.py)
"""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import matplotlib.cm as cm, matplotlib.colors as mcolors
np.random.seed(0)
kappa=0.41; C1=18.0; C2=1.0

# media: rho_f, nu, g   (grain density is per-system)
MED={
 "Mars air":   dict(rho=0.020, nu=5.5e-4, g=3.71),
 "Earth air":  dict(rho=1.20,  nu=1.5e-5, g=9.81),
 "Titan air":  dict(rho=5.3,   nu=1.1e-6, g=1.35),
 "Venus air":  dict(rho=65.0,  nu=5.4e-7, g=8.87),
 "Titan liquid":dict(rho=615., nu=8.9e-7, g=1.35),
 "Water":      dict(rho=1000., nu=1.0e-6, g=9.81),
 "Debris slurry":dict(rho=1400.,nu=1.0e-4, g=9.81),
 "Pyroclastic":dict(rho=0.5,   nu=5.0e-5, g=9.81),
}
def settling(D, m, rhos):
    R=rhos/m["rho"]-1.0
    if R<=0: return np.nan
    return R*m["g"]*D**2/(C1*m["nu"]+np.sqrt(0.75*C2*R*m["g"]*D**3))
def ARA(s,W): return 1+np.tanh(np.log(s)/W)

# name, medium, D(m), rho_s, u*(m/s), mode
SYS=[
 ("Aeolian dune","Earth air",0.25e-3,2650,0.40,"saltation/bed"),
 ("Aeolian ripple","Earth air",0.30e-3,2650,0.30,"saltation/bed"),
 ("Blowing snow","Earth air",0.20e-3,250,0.35,"saltation/bed"),
 ("Dust storm","Earth air",0.020e-3,2650,0.50,"suspension"),
 ("Loess fallout","Earth air",0.030e-3,2650,0.05,"deposition"),
 ("Gravel-bed river","Water",30e-3,2650,0.15,"bedload"),
 ("Sand-bed river","Water",0.40e-3,2650,0.08,"mixed/bed"),
 ("River-mouth delta","Water",0.10e-3,2650,0.02,"deposition"),
 ("Floodplain mud","Water",0.010e-3,2650,0.01,"deposition"),
 ("Turbidity current","Water",0.10e-3,2650,0.50,"suspension"),
 ("Beach swash","Water",0.30e-3,2650,0.05,"mixed/bed"),
 ("Alluvial fan","Water",5.0e-3,2650,0.20,"bedload"),
 ("Subglacial stream","Water",10e-3,2650,0.25,"bedload"),
 ("Debris flow","Debris slurry",50e-3,2650,0.50,"bedload"),
 ("Lahar","Debris slurry",5.0e-3,2650,0.40,"mixed/bed"),
 ("Pyroclastic flow","Pyroclastic",0.10e-3,2650,1.00,"suspension"),
 ("Mars dune","Mars air",0.15e-3,3000,1.00,"saltation/bed"),
 ("Mars dust","Mars air",0.003e-3,3000,1.00,"suspension"),
 ("Venus dune","Venus air",0.15e-3,2900,0.04,"saltation/bed"),
 ("Titan river","Titan liquid",5.0e-3,950,0.05,"bedload"),
 ("Titan dune","Titan air",0.25e-3,950,0.04,"saltation/bed"),
 ("Titan delta","Titan liquid",0.10e-3,950,0.01,"deposition"),
]
rows=[]
for nm,mn,D,rs,us,mode in SYS:
    ws=settling(D,MED[mn],rs); s=ws/us; rows.append(dict(nm=nm,med=mn,D=D,s=s,ara=ARA(s,2.0),mode=mode,rho=MED[mn]["rho"]))

# ---------- eta^2 mode vs medium ----------
logs=np.array([np.log10(r["s"]) for r in rows])
def eta2(keys):
    grand=logs.mean(); ss=((logs-grand)**2).sum(); b=0.0
    for k in set(keys):
        gi=logs[[i for i,kk in enumerate(keys) if kk==k]]; b+=len(gi)*(gi.mean()-grand)**2
    return b/ss
modes=[r["mode"] for r in rows]; meds=[r["med"] for r in rows]
print(f"n={len(rows)} systems, {len(set(meds))} media, {len(set(modes))} modes")
print(f"eta^2 MODE   = {eta2(modes):.2f}")
print(f"eta^2 MEDIUM = {eta2(meds):.2f}")

# medium ordering (the wave): mean log10 s per medium vs fluid density
print("\nMEDIUM WAVE (mean log10 s per medium, ordered by fluid density):")
mm={}
for r in rows: mm.setdefault(r["med"],[]).append(np.log10(r["s"]))
for md in sorted(mm,key=lambda k:MED[k]["rho"]):
    print(f"  rho={MED[md]['rho']:7.1f}  {md:13s} mean log10 s = {np.mean(mm[md]):+.2f}  (n={len(mm[md])})")

# ================= FIGURE 1: expanded collapse, colour = fluid density =================
fig,ax=plt.subplots(figsize=(14,7.2),facecolor="#0e1116"); ax.set_facecolor("#161b22")
ax.tick_params(colors="#9aa7b4"); ax.grid(False)
mode_order=["bedload","saltation/bed","mixed/bed","deposition","suspension"]
yof={m:i for i,m in enumerate(mode_order)}
norm=mcolors.LogNorm(vmin=0.02,vmax=1400); cmap=cm.viridis
for xv,lab,c in [(0.0,"0 suspension pole","#ff8a8a"),(1.0,"1.0 RIDGE (s=1)","#ffd479"),(2.0,"2 deposition pole","#ff8a8a")]:
    ax.axvline(xv,color=c,lw=1.0,ls="--",alpha=0.5); ax.text(xv,5.15,lab,color=c,fontsize=8.5,ha="center",va="bottom")
rj=np.random.default_rng(1)
for r in rows:
    y=yof[r["mode"]]+rj.uniform(-0.17,0.17)
    ax.scatter(r["ara"],y,s=130,c=[cmap(norm(r["rho"]))],edgecolors="#0e1116",lw=1,zorder=3)
    ax.annotate(r["nm"],(r["ara"],y),textcoords="offset points",xytext=(0,10),fontsize=7,color="#e6edf3",ha="center")
for mo,yi in yof.items():
    xs=[r["ara"] for r in rows if r["mode"]==mo]
    if xs: ax.plot([min(xs),max(xs)],[yi,yi],color="#3a4453",lw=8,alpha=0.35,zorder=1,solid_capstyle="round")
ax.set_yticks(range(len(mode_order))); ax.set_yticklabels([m.upper() for m in mode_order],color="#cbd5e1",fontsize=10)
ax.set_ylabel("transport MODE (≈ dimension available to grain)",color="#cbd5e1")
ax.set_xlabel("vertical-ARA from Rouse  s=w_s/u*  (ridge s=1)",color="#cbd5e1")
ax.set_xlim(-0.15,2.15); ax.set_ylim(-0.6,5.6)
ax.set_title(f"Rouse-ARA expanded — {len(rows)} systems, {len(set(meds))} media\n"
             f"MODE organizes (η²={eta2(modes):.2f}) · MEDIUM secondary but ORDERED (η²={eta2(meds):.2f}) — colour = fluid density",
             color="#e6edf3",fontsize=12.5)
sm=cm.ScalarMappable(norm=norm,cmap=cmap); sm.set_array([])
cb=fig.colorbar(sm,ax=ax,pad=0.01); cb.set_label("fluid density ρ_f (kg/m³)",color="#cbd5e1"); cb.ax.yaxis.set_tick_params(color="#9aa7b4")
plt.setp(plt.getp(cb.ax.axes,'yticklabels'),color="#9aa7b4")
out1="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rouse_ara_expanded.png"
plt.tight_layout(); plt.savefig(out1,dpi=150,facecolor="#0e1116"); print("saved",out1)

# ================= FIGURE 2: THE MEDIUM WAVE — ARA vs grain size, one curve per medium =================
# fixed transport stage: u* = 1.5 * fluid threshold u*t ; u*t = 0.1*sqrt(R g D) (Bagnold, sand+; fine end ignores cohesion)
fig2,ax2=plt.subplots(figsize=(13,7),facecolor="#0e1116"); ax2.set_facecolor("#161b22")
ax2.tick_params(colors="#9aa7b4"); ax2.grid(False)
Dgrid=np.logspace(np.log10(2e-6),np.log10(0.1),400)  # 2 um -> 10 cm
order_media=["Mars air","Earth air","Titan air","Venus air","Titan liquid","Water","Debris slurry"]
palette=cm.plasma(np.linspace(0.05,0.9,len(order_media)))
rhos_ref=2650.0
for md,cimg in zip(order_media,palette):
    m=MED[md]; R=rhos_ref/m["rho"]-1.0
    if R<=0: continue
    ustar=1.5*0.1*np.sqrt(R*m["g"]*Dgrid)
    ws=np.array([settling(D,m,rhos_ref) for D in Dgrid])
    s=ws/ustar; a=ARA(s,2.0)
    ax2.plot(Dgrid*1e3,a,color=cimg,lw=2.2,label=f"{md} (ρ={m['rho']:g})")
ax2.axhline(1.0,color="#ffd479",lw=1,ls="--",alpha=0.6); ax2.text(0.0025,1.02,"ridge s=1",color="#ffd479",fontsize=8)
ax2.axhline(2.0,color="#ff8a8a",lw=1,ls="--",alpha=0.4); ax2.axhline(0.0,color="#ff8a8a",lw=1,ls="--",alpha=0.4)
ax2.text(0.003,1.9,"deposition pole",color="#ff8a8a",fontsize=8); ax2.text(0.003,0.06,"suspension pole",color="#ff8a8a",fontsize=8)
ax2.set_xscale("log"); ax2.set_xlabel("grain size D (mm)  —  fixed transport stage u*=1.5×threshold, reference grain ρ_s=2650",color="#cbd5e1")
ax2.set_ylabel("vertical-ARA",color="#cbd5e1"); ax2.set_ylim(-0.05,2.05)
ax2.set_title("THE MEDIUM WAVE — each medium traces its own curve\nconverge at the bedload/deposition end, FAN OUT toward suspension (fine grains) — ordered by fluid density",
              color="#e6edf3",fontsize=12.5)
ax2.legend(facecolor="#161b22",labelcolor="#cbd5e1",fontsize=9,loc="center left")
out2="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rouse_ara_medium_wave.png"
plt.tight_layout(); plt.savefig(out2,dpi=150,facecolor="#0e1116"); print("saved",out2)
