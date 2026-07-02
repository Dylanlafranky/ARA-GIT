"""Vertical ARA on REAL measured shape data.
Two waves, both built on the disciplined tanh mapping (no dialed 0/2):
  (1) SIZE -> ROUNDNESS  (the shape wave; confirm form, locate potato radius)
  (2) FORMATION -> EROSION time-ARA (the genuine release/accumulation wave; hunt the peak)

Roundness metric = c/a  (min axis / max axis of the published triaxial ellipsoid;
1.0 = sphere). This is DERIVED from measured axis lengths, not eyeballed.
Triaxial radii (km) are canonical IAU / JPL / Cassini / mission-derived values.
"""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

# name, (a,b,c) radii km  [a>=b>=c],  regime tag, density g/cc (for note)
BODIES = [
 # ---- strength / cohesion regime (irregular, shape held by material strength) ----
 ("Itokawa",   (0.268,0.147,0.104), "S", 1.9),
 ("Eros",      (17.2, 5.6,  5.6),   "S", 2.67),
 ("Gaspra",    (9.1,  5.2,  4.4),   "S", 2.7),
 ("Ida",       (29.9, 12.7, 9.3),   "S", 2.6),
 ("Bennu",     (0.283,0.272,0.249), "S", 1.19),
 ("Ryugu",     (0.502,0.495,0.440), "S", 1.19),
 ("Mathilde",  (33.0, 24.0, 23.0),  "S", 1.3),
 ("Lutetia",   (60.5, 50.5, 37.5),  "S", 3.4),
 ("Phobos",    (13.0, 11.4, 9.1),   "S", 1.88),
 ("Deimos",    (7.5,  6.1,  5.5),   "S", 1.47),
 ("Amalthea",  (125., 73.0, 64.0),  "S", 0.86),
 ("Janus",     (101.7,93.0, 76.3),  "S", 0.63),
 ("Epimetheus",(64.9, 57.3, 53.0),  "S", 0.64),
 ("Hyperion",  (180.1,133.0,102.7), "S", 0.54),   # porous low-density -> stays irregular
 # ---- transition zone (the "potato radius") ----
 ("Vesta",     (286.3,278.6,223.2), "T", 3.46),
 ("Pallas",    (275.,258., 238.),   "T", 2.9),
 ("Proteus",   (218.,208., 201.),   "T", 1.3),    # largest clearly-irregular body
 # ---- gravity regime (hydrostatic, rounded) ----
 ("Mimas",     (207.8,196.7,190.6), "G", 1.15),   # smallest round body
 ("Miranda",   (240.,234.2,232.9),  "G", 1.2),
 ("Enceladus", (256.6,251.4,248.3), "G", 1.61),
 ("Ceres",     (482.1,482.1,445.9), "G", 2.16),
 ("Tethys",    (538.4,528.3,526.3), "G", 0.98),
 ("Dione",     (563.4,561.3,559.6), "G", 1.48),
 ("Rhea",      (765.0,763.1,762.4), "G", 1.24),
 ("Iapetus",   (745.7,745.7,712.1), "G", 1.09),
 ("Titania",   (788.4,788.4,788.4), "G", 1.66),
 ("Moon",      (1738.1,1738.1,1736.0),"G",3.34),
 ("Mars",      (3396.2,3396.2,3376.2),"G",3.93),
 ("Earth",     (6378.1,6378.1,6356.8),"G",5.51),
 # ---- rotational flattening (fast spinners) ----
 ("Saturn",    (60268.,60268.,54364.),"R",0.69),
 ("Jupiter",   (71492.,71492.,66854.),"R",1.33),
]

names=[b[0] for b in BODIES]
ax_a=np.array([b[1][0] for b in BODIES]); ax_c=np.array([b[1][2] for b in BODIES])
reg=[b[2] for b in BODIES]
Rmean=np.array([ (b[1][0]*b[1][1]*b[1][2])**(1/3.) for b in BODIES ])  # geometric-mean radius km
round_ca = ax_c/ax_a                       # roundness 0-1 (1=sphere)
x = np.log10(Rmean*1000.0)                 # log10 mean radius in METRES

COL={"S":"#c98a4a","T":"#e0c060","G":"#5aa0ff","R":"#b197fc"}
LAB={"S":"strength / cohesion","T":"transition","G":"gravity (rounded)","R":"rotational flattening"}

# ---------- tanh mapping method (the disciplined map; no dialed 0/2) ----------
def th(v, ridge, width):
    """map a value to ARA 0-2 via tanh; ridge->1.0, asymptotes toward (not onto) 0/2."""
    return 1.0 + np.tanh((v-ridge)/width)

# ================= WAVE 1 : SIZE -> ROUNDNESS =================
# logistic fit roundness ~ size to locate the transition (potato radius)
from scipy.optimize import curve_fit
def logistic(xx, lo, hi, x0, k): return lo + (hi-lo)/(1+np.exp(-k*(xx-x0)))
# fit on non-rotational bodies (gas giants flatten back down -> exclude from rise)
m = np.array([r!="R" for r in reg])
p0=[0.4,0.97, 5.3, 3.0]
try:
    popt,_=curve_fit(logistic,x[m],round_ca[m],p0=p0,maxfev=20000)
    x0_fit=popt[2]; k_fit=popt[3]
except Exception as e:
    popt=p0; x0_fit=5.3; k_fit=3.0
potato_R_m = 10**x0_fit
# spearman + shuffle null (does roundness really track size?)
from scipy.stats import spearmanr
rho,pval = spearmanr(x[m], round_ca[m])
rng=np.random.default_rng(0)
null=[spearmanr(x[m], rng.permutation(round_ca[m]))[0] for _ in range(5000)]
p_null=(np.sum(np.array(null)>=rho)+1)/(len(null)+1)

# ================= WAVE 2 : FORMATION -> EROSION (time-ARA) =================
# ORDER-OF-MAGNITUDE published scaling relations (NOT per-body measured):
#   T_form  : accretion time. pebbles ~1e3 yr ; km planetesimal ~3e4 ; 100km ~3e5 ;
#             1000km ~3e6 ; terrestrial planet ~5e7 (tens of Myr).  (rocky track only)
#   T_erode : collisional/destruction lifetime. Bottke: D=0.8km ~0.3 Gyr ; D=10km ~5 Gyr.
#             power law T~D^1.1 ; capped at solar-system age 4.6 Gyr for big stable bodies.
logR = np.log10(Rmean*1000.0)             # log metres
# formation time (log10 yr), smooth rocky-track anchors:
fa_x=np.array([-2, 3, 5, 6, 6.8]); fa_y=np.array([3.0,4.5,5.5,6.5,7.7])
logTform=np.interp(logR, fa_x, fa_y)
# erosion/collisional lifetime (log10 yr):
#  anchor on Bottke at small-body diameters, cap at system age
D_km=2*Rmean
logTerode_raw = np.log10(0.3e9) + 1.1*np.log10(D_km/0.8)   # Bottke power law
logTerode=np.minimum(logTerode_raw, np.log10(4.6e9))       # cap at system age
ratio = logTerode - logTform                               # log10(T_erode/T_form) = persistence-per-cost
ara_time = th(ratio, ridge=np.median(ratio), width=(ratio.max()-ratio.min())/3.0)

# locate peak of the ratio across size (rocky bodies, exclude gas giants)
mr = np.array([r!="R" for r in reg])
order=np.argsort(logR[mr])
lr=logR[mr][order]; rr=ratio[mr][order]; nm=np.array(names)[mr][order]
peak_i=int(np.argmax(rr)); peak_name=nm[peak_i]; peak_R=10**lr[peak_i]

# ---------------- PLOT ----------------
fig,(axA,axB)=plt.subplots(1,2,figsize=(17,6.6),facecolor="#0e1116")
for ax in (axA,axB): ax.set_facecolor("#161b22"); ax.tick_params(colors="#9aa7b4"); ax.grid(False)

# --- Panel A: size -> roundness ---
xs=np.linspace(x.min(),x.max(),300)
axA.axvspan(np.log10(1.5e5),np.log10(3e5),color="#5aa0ff",alpha=0.10)
axA.plot(xs,logistic(xs,*popt),color="#7fb0ff",lw=2,alpha=0.8,zorder=2,label="logistic fit")
axA.axvline(x0_fit,color="#ffd479",lw=1.2,ls="--",alpha=0.8)
axA.text(x0_fit,0.34,f" transition R≈{potato_R_m/1000:.0f} km",color="#ffd479",fontsize=9)
for i,b in enumerate(BODIES):
    axA.scatter(x[i],round_ca[i],s=70,c=COL[reg[i]],edgecolors="#0e1116",lw=0.8,zorder=3)
    if names[i] in ("Phobos","Hyperion","Mimas","Eros","Vesta","Proteus","Bennu","Earth","Saturn","Itokawa"):
        axA.annotate(names[i],(x[i],round_ca[i]),textcoords="offset points",xytext=(0,7),
                     fontsize=7.5,color="#cdd6e0",ha="center")
axA.set_xlabel("log₁₀ mean radius (m)",color="#cbd5e1")
axA.set_ylabel("roundness  c/a  (min/max axis; 1=sphere)",color="#cbd5e1")
axA.set_title(f"WAVE 1 · size → roundness (real triaxial axes)\nSpearman ρ={rho:.2f}, shuffle-null p={p_null:.4f}",
              color="#e6edf3",fontsize=12)
axA.set_ylim(0.28,1.03)
import matplotlib.patches as mp
axA.legend(handles=[mp.Patch(color=COL[k],label=LAB[k]) for k in ["S","T","G","R"]],
           facecolor="#161b22",labelcolor="#cbd5e1",fontsize=8,loc="lower right")

# --- Panel B: formation -> erosion ratio (the time wave) ---
axB.plot(lr,rr,color="#9aa7b4",lw=1.0,alpha=0.5,zorder=1)
sc=axB.scatter(logR[mr],ratio[mr],s=70,c=[COL[r] for r in np.array(reg)[mr]],
               edgecolors="#0e1116",lw=0.8,zorder=3)
axB.axvline(lr[peak_i],color="#7CFC9A",lw=1.4,ls="--",alpha=0.85)
axB.text(lr[peak_i],rr.min()+0.2,f" peak ≈ {peak_name}\n R≈{peak_R/1000:.0f} km",color="#7CFC9A",fontsize=9)
for nmx,lrx,rrx in zip(nm,lr,rr):
    if nmx in ("Itokawa","Eros","Phobos","Hyperion","Mimas","Vesta","Ceres","Moon","Earth","Ida"):
        axB.annotate(nmx,(lrx,rrx),textcoords="offset points",xytext=(0,7),fontsize=7.5,color="#cdd6e0",ha="center")
axB.set_xlabel("log₁₀ mean radius (m)",color="#cbd5e1")
axB.set_ylabel("log₁₀ ( T_erosion / T_formation )  =  persistence per build-cost",color="#cbd5e1")
axB.set_title("WAVE 2 · formation → erosion  (ORDER-OF-MAGNITUDE scaling, fenced)\n"
              "Bottke collisional lifetime ÷ accretion time · survival capped at system age",
              color="#e6edf3",fontsize=12)

out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rock_real_two_waves.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116"); print("saved",out)

# ---------------- REPORT NUMBERS ----------------
print("\n=== WAVE 1 : size -> roundness (REAL measured axes) ===")
print(f"Spearman rho = {rho:.3f}, shuffle-null p = {p_null:.4f}  (n={m.sum()} non-rotational bodies)")
print(f"logistic transition radius = {potato_R_m/1000:.0f} km  (potato radius; literature ~200-300 km)")
print("\nOutlier check (roundness vs the fitted curve):")
fitted=logistic(x,*popt)
resid=round_ca-fitted
oi=np.argsort(-np.abs(resid))
for i in oi[:6]:
    print(f"  {names[i]:10s} R={Rmean[i]:7.1f}km  c/a={round_ca[i]:.3f}  fit={fitted[i]:.3f}  resid={resid[i]:+.3f}")
print("\nHyperion vs Mimas (same size shelf, opposite form):")
for nm_ in ("Hyperion","Mimas"):
    i=names.index(nm_); print(f"  {nm_:9s} R={Rmean[i]:.0f}km  c/a={round_ca[i]:.3f}  density={BODIES[i][3]} g/cc")

print("\n=== WAVE 2 : formation -> erosion (FENCED order-of-magnitude) ===")
print(f"ratio peaks at {peak_name}  (R≈{peak_R/1000:.0f} km, log-ratio {rr[peak_i]:.2f})")
print("interpretation: small bodies fragile (cheap but short-lived); planets expensive to build")
print("and survival saturates at system age -> persistence-per-cost peaks at intermediate size.")
print("FENCE: timescales are model/scaling-derived, processes heterogeneous, peak sensitive to the age cap.")
