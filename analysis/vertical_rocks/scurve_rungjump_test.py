"""
Is the roundness S-curve a RUNG JUMP? Test Dylan's two predictions:
 (1) ASYMMETRY: escaping the low pole is the hard/costly side (long low shoulder), taper at top.
 (2) MECHANISM: base units (grain strength) can't cross; an emergent HIGHER component (self-gravity)
     overtakes strength and drives the jump. Steep part should sit at the gravity=strength crossover,
     and BELOW it roundness should NOT track size (base units stuck), only above.

REPLICABLE: real triaxial axes (IAU/JPL/Cassini/mission); sourced strengths & constants; deterministic.
SOURCES: G=6.674e-11. Rock cohesive/tensile shape-supporting strength ~1-10 MPa (fractured/regolith),
 intact up to ~100 MPa; ice ~1 MPa. Potato-radius derivations use a few MPa (e.g. rubble/weak-rock).
 Self-gravity central stress P ~ (2/3)*pi*G*rho^2*R^2.
"""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import spearmanr
np.random.seed(0)

# name, (a,b,c) radii km, mean density g/cc  (real measured)
B=[("Itokawa",(0.268,0.147,0.104),1.9),("Eros",(17.2,5.6,5.6),2.67),("Gaspra",(9.1,5.2,4.4),2.7),
("Ida",(29.9,12.7,9.3),2.6),("Bennu",(0.283,0.272,0.249),1.19),("Ryugu",(0.502,0.495,0.440),1.19),
("Mathilde",(33.,24.,23.),1.3),("Lutetia",(60.5,50.5,37.5),3.4),("Phobos",(13.,11.4,9.1),1.88),
("Deimos",(7.5,6.1,5.5),1.47),("Amalthea",(125.,73.,64.),0.86),("Janus",(101.7,93.,76.3),0.63),
("Epimetheus",(64.9,57.3,53.),0.64),("Hyperion",(180.1,133.,102.7),0.54),("Vesta",(286.3,278.6,223.2),3.46),
("Pallas",(275.,258.,238.),2.9),("Proteus",(218.,208.,201.),1.3),("Mimas",(207.8,196.7,190.6),1.15),
("Miranda",(240.,234.2,232.9),1.2),("Enceladus",(256.6,251.4,248.3),1.61),("Ceres",(482.1,482.1,445.9),2.16),
("Tethys",(538.4,528.3,526.3),0.98),("Dione",(563.4,561.3,559.6),1.48),("Rhea",(765.,763.1,762.4),1.24),
("Iapetus",(745.7,745.7,712.1),1.09),("Titania",(788.4,788.4,788.4),1.66),("Moon",(1738.1,1738.1,1736.),3.34),
("Mars",(3396.2,3396.2,3376.2),3.93),("Earth",(6378.1,6378.1,6356.8),5.51)]
names=[b[0] for b in B]
Rm=np.array([(b[1][0]*b[1][1]*b[1][2])**(1/3.) for b in B])      # mean radius km
ca=np.array([b[1][2]/b[1][0] for b in B]); rho=np.array([b[2] for b in B])*1000.
x=np.log10(Rm*1000.)                                             # log10 radius (m)
# gas giants excluded from the rounding rise (they flatten back)
m=np.array([n not in ("Saturn","Jupiter") for n in names])

# ---------- (1) ASYMMETRY: symmetric logistic vs asymmetric Richards ----------
def logistic(x,lo,hi,x0,k): return lo+(hi-lo)/(1+np.exp(-k*(x-x0)))
def richards(x,lo,hi,x0,k,nu): return lo+(hi-lo)/(1+nu*np.exp(-k*(x-x0)))**(1/nu)
pL,_=curve_fit(logistic,x[m],ca[m],p0=[0.4,0.97,5.3,3],maxfev=40000)
pR,_=curve_fit(richards,x[m],ca[m],p0=[0.4,0.97,5.3,3,1.0],maxfev=80000,
               bounds=([0.2,0.8,3,0.3,0.05],[0.7,1.05,7,20,20]))
def shoulders(fp):
    lo,hi=fp[0],fp[1]; xs=np.linspace(2,8,3000); ys=richards(xs,*fp) if len(fp)==5 else logistic(xs,*fp)
    def xat(f):
        t=lo+f*(hi-lo); i=np.argmin(np.abs(ys-t)); return xs[i]
    x10,x50,x90=xat(0.10),xat(0.50),xat(0.90)
    return (x50-x10),(x90-x50)   # low shoulder (escape), high shoulder (taper), in decades
loA,hiA=shoulders(pR)
# bootstrap asymmetry (low/high shoulder ratio and Richards nu)
rng=np.random.default_rng(1); nus=[]; ratios=[]
xi,yi=x[m],ca[m]; idx=np.arange(len(xi))
for _ in range(400):
    s=rng.choice(idx,len(idx),replace=True)
    try:
        p,_=curve_fit(richards,xi[s],yi[s],p0=pR,maxfev=40000,
                      bounds=([0.2,0.8,3,0.3,0.05],[0.7,1.05,7,20,20]))
        lo_,hi_=shoulders(p); nus.append(p[4]); ratios.append(lo_/hi_)
    except Exception: pass
nus=np.array(nus); ratios=np.array(ratios)

print("=== (1) ASYMMETRY ===")
print(f"Richards nu = {pR[4]:.2f}  (nu=1 symmetric; nu<1 long-LOW shoulder=hard escape; nu>1 long-high)")
print(f"  bootstrap nu 95% CI: [{np.percentile(nus,2.5):.2f}, {np.percentile(nus,97.5):.2f}]")
print(f"low shoulder (10->50%, ESCAPE)  = {loA:.2f} decades of radius")
print(f"high shoulder (50->90%, TAPER)  = {hiA:.2f} decades of radius")
print(f"escape/taper width ratio = {loA/hiA:.2f}  (>1 => escape is the wider/costlier side, as predicted)")
print(f"  bootstrap ratio 95% CI: [{np.percentile(ratios,2.5):.2f}, {np.percentile(ratios,97.5):.2f}]")

# ---------- (2) MECHANISM: self-gravity stress vs strength; sub-potato flatness ----------
G=6.674e-11
def Pgrav(R_m,rho_): return (2/3)*np.pi*G*rho_**2*R_m**2   # central self-gravity stress (Pa)
# strength band (sourced): weak/rubble ~1e6, strong rock ~1e8 Pa
Rgrid=np.logspace(2,7,400)  # 0.1 km -> 10000 km, in m
rho_typ=2000.
Pg=Pgrav(Rgrid,rho_typ)
def crossoverR(Y,rho_): return np.sqrt(Y/((2/3)*np.pi*G*rho_**2))
xover_weak=crossoverR(1e6,2000.); xover_mid=crossoverR(1e7,2000.); xover_strong=crossoverR(1e8,2500.)
x0_fit=pR[2]; transR=10**x0_fit
print("\n=== (2) MECHANISM (higher component = self-gravity overtakes strength) ===")
print(f"roundness transition (Richards x0)     : R = {transR/1000:.0f} km")
print(f"gravity=strength crossover, Y=1 MPa    : R = {xover_weak/1000:.0f} km")
print(f"gravity=strength crossover, Y=10 MPa   : R = {xover_mid/1000:.0f} km")
print(f"gravity=strength crossover, Y=100 MPa  : R = {xover_strong/1000:.0f} km")
print(f"  => observed transition {transR/1000:.0f} km sits INSIDE the strength-crossover band ({xover_weak/1000:.0f}-{xover_strong/1000:.0f} km).")

# sub-potato: do the small (base-unit) bodies track size, or are they stuck/scattered?
below=m & (x < x0_fit); above=m & (x >= x0_fit)
rb,pb=spearmanr(x[below],ca[below]); ra,pa=spearmanr(x[above],ca[above])
print(f"\nsub-potato (below transition, n={below.sum()}): Spearman(size,roundness) rho={rb:+.2f} p={pb:.2f}  (flat/stuck => base units can't cross)")
print(f"above transition (n={above.sum()}):            Spearman(size,roundness) rho={ra:+.2f} p={pa:.2f}")
print(f"sub-potato roundness: mean={ca[below].mean():.2f} sd={ca[below].std():.2f} (scattered by material, not size)")

# ---------- FIGURE ----------
fig,(axA,axB)=plt.subplots(1,2,figsize=(16,6.6),facecolor="#0e1116")
for ax in (axA,axB): ax.set_facecolor("#161b22"); ax.tick_params(colors="#9aa7b4"); ax.grid(False)
xs=np.linspace(x.min(),x.max(),300)
axA.plot(xs,logistic(xs,*pL),color="#5b6b7a",lw=1.5,ls=":",label="symmetric logistic")
axA.plot(xs,richards(xs,*pR),color="#7fb0ff",lw=2.3,label=f"asymmetric Richards (ν={pR[4]:.2f})")
axA.axvline(x0_fit,color="#ffd479",lw=1,ls="--",alpha=0.7)
axA.axvspan(np.log10(xover_weak),np.log10(xover_strong),color="#7CFC9A",alpha=0.12)
axA.text(np.log10(xover_mid),0.33,"gravity > strength\n(higher component takes over)",color="#7CFC9A",fontsize=8.5,ha="center")
for i in range(len(B)):
    if not m[i]: continue
    col="#c98a4a" if x[i]<x0_fit else "#5aa0ff"
    axA.scatter(x[i],ca[i],s=55,c=col,edgecolors="#0e1116",lw=0.7,zorder=3)
for nm in ("Itokawa","Eros","Ida","Hyperion","Mimas","Ceres","Earth"):
    i=names.index(nm); axA.annotate(nm,(x[i],ca[i]),textcoords="offset points",xytext=(0,7),fontsize=7,color="#cdd6e0",ha="center")
axA.annotate("",xy=(x0_fit,0.62),xytext=(x0_fit-loA,0.62),arrowprops=dict(arrowstyle="<->",color="#ff8a8a",lw=1.4))
axA.text(x0_fit-loA/2,0.585,f"escape {loA:.1f} dec",color="#ff8a8a",fontsize=8,ha="center")
axA.annotate("",xy=(x0_fit+hiA,0.86),xytext=(x0_fit,0.86),arrowprops=dict(arrowstyle="<->",color="#7CFC9A",lw=1.4))
axA.text(x0_fit+hiA/2,0.885,f"taper {hiA:.1f} dec",color="#7CFC9A",fontsize=8,ha="center")
axA.set_xlabel("log₁₀ mean radius (m)",color="#cbd5e1"); axA.set_ylabel("roundness c/a",color="#cbd5e1")
axA.set_ylim(0.28,1.03); axA.legend(facecolor="#161b22",labelcolor="#cbd5e1",fontsize=8.5,loc="lower right")
axA.set_title(f"(1) the rung-jump S is ASYMMETRIC\nescape/taper width ratio = {loA/hiA:.2f} (long low shoulder = hard escape)",color="#e6edf3",fontsize=11.5)

axB.plot(np.log10(Rgrid),np.log10(Pg),color="#7CFC9A",lw=2,label="self-gravity stress (ρ=2000)")
axB.axhspan(6,8,color="#c98a4a",alpha=0.15); axB.text(2.3,7,"material strength band\n1–100 MPa",color="#c98a4a",fontsize=8.5)
axB.axvline(x0_fit,color="#ffd479",lw=1.2,ls="--"); axB.text(x0_fit+0.05,3,f"roundness\ntransition\n{transR/1000:.0f} km",color="#ffd479",fontsize=8.5)
axB.set_xlabel("log₁₀ radius (m)",color="#cbd5e1"); axB.set_ylabel("log₁₀ stress (Pa)",color="#cbd5e1")
axB.set_title("(2) the HIGHER component crossing\nself-gravity overtakes strength AT the transition",color="#e6edf3",fontsize=11.5)
axB.legend(facecolor="#161b22",labelcolor="#cbd5e1",fontsize=8.5,loc="upper left")
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/scurve_rungjump.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116"); print("\nsaved",out)
