"""
JUMP 2 of the rung staircase: ROTATIONAL FLATTENING, with SPIN as the higher component.
Once a body is gravity-rounded (past jump 1), the next reshaping is centrifugal.
Higher-component ratio: m = omega^2 a^3 / (G M) = centrifugal accel / gravity at the equator
 (exact analog of jump 1's self-gravity/strength). Base state = hydrostatic SPHERE held by gravity;
 spin overtakes -> oblateness rises -> taper/limit at m~1 (equatorial breakup / mass-shedding).

Predictions tested (Dylan's 'rinse and repeat'):
 - low spin: stuck at the sphere pole (f~0), regardless of size/mass.
 - flattening tracks SPIN (m), not size or mass alone (the higher component does the crossing).
 - taper/max at the rotational stability limit; Haumea sits at it (Jacobi, ring+moons shed).

REPLICABLE: equatorial/polar radii, rotation, mass = NASA Planetary Fact Sheet; Haumea a,c,P from
 stellar-occultation (Ortiz+ 2017 / Dunham+ 2019). Deterministic. G=6.674e-11.
"""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
G=6.674e-11
# name, a_eq(km), c_pol(km), P_rot(h), M(kg)
BODY=[
 ("Venus",   6051.8, 6051.8, 5832.5, 4.867e24),
 ("Mercury", 2440.5, 2438.3, 1407.6, 3.301e23),
 ("Pluto",   1188.0, 1188.0,  153.3, 1.303e22),
 ("Moon",    1738.1, 1736.0,  655.7, 7.346e22),
 ("Mars",    3396.2, 3376.2,   24.62,6.417e23),
 ("Earth",   6378.1, 6356.8,   23.93,5.972e24),
 ("Uranus", 25559.0,24973.0,   17.24,8.681e25),
 ("Neptune",24764.0,24341.0,   16.11,1.024e26),
 ("Ceres",    482.0,  446.0,    9.07,9.380e20),
 ("Jupiter",71492.0,66854.0,    9.925,1.898e27),
 ("Saturn", 60268.0,54364.0,   10.656,5.683e26),
 ("Haumea",  1161.0,  513.0,    3.915,4.006e21),   # Jacobi, at breakup
]
name=[b[0] for b in BODY]
a=np.array([b[1] for b in BODY])*1e3; c=np.array([b[2] for b in BODY])*1e3
P=np.array([b[3] for b in BODY])*3600.; M=np.array([b[4] for b in BODY])
f=(a-c)/a                                   # flattening / oblateness
om=2*np.pi/P
mspin=om**2*a**3/(G*M)                       # centrifugal/gravity ratio at equator

print("=== JUMP 2: rotational flattening (real, sourced) ===")
print(f"{'body':9s} {'m=cent/grav':>11s} {'flatten f':>9s}")
for i in np.argsort(mspin):
    print(f"{name[i]:9s} {mspin[i]:11.4f} {f[i]:9.4f}")

# flattening driven by SPIN (m), not size/mass alone?
print("\ncorrelations (does the HIGHER component = spin do the crossing?):")
print(f"  Spearman(f, m spin)        = {spearmanr(f,mspin)[0]:+.2f}")
print(f"  Spearman(f, equatorial R)  = {spearmanr(f,a)[0]:+.2f}")
print(f"  Spearman(f, mass M)        = {spearmanr(f,M)[0]:+.2f}")
# stuck plateau: slow rotators (m<0.01) all near sphere regardless
slow=mspin<0.01
print(f"\nstuck-at-sphere (m<0.01, n={slow.sum()}): flattening mean={f[slow].mean():.4f} max={f[slow].max():.4f}  (pole, base gravity holds sphere)")
print(f"breakup limit m=1 (centrifugal=gravity): Haumea m={mspin[name.index('Haumea')]:.2f} -> at/over the limit (Jacobi ellipsoid, sheds ring+moons)")

# ---------------- FIGURE: jump 2 alone ----------------
fig,ax=plt.subplots(figsize=(13,7),facecolor="#0e1116"); ax.set_facecolor("#161b22")
ax.tick_params(colors="#9aa7b4"); ax.grid(False)
# zones
ax.axvspan(1e-5,1e-2,color="#5aa0ff",alpha=0.10)     # stuck sphere
ax.axvspan(1e-2,3e-1,color="#7CFC9A",alpha=0.12)     # crossing
ax.axvspan(3e-1,3e0,color="#b197fc",alpha=0.12)      # taper/breakup
# uniform-fluid small-m Maclaurin reference f=1.25 m
mm=np.logspace(-5,0.2,200); ax.plot(mm,1.25*mm,color="#5b6b7a",lw=1.4,ls=":",label="uniform-fluid Maclaurin  f=1.25m")
ax.axvline(1.0,color="#ff8a8a",lw=1.3,ls="--"); ax.text(1.02,0.02,"m=1\ncentrifugal = gravity\n(equatorial breakup)",color="#ff8a8a",fontsize=8.5,va="bottom")
ax.scatter(mspin,f,s=90,c="#eaeff5",edgecolors="#0e1116",lw=0.9,zorder=4)
for i in range(len(BODY)):
    dy=8 if name[i] not in("Neptune","Ceres") else -14
    ax.annotate(name[i],(mspin[i],f[i]),textcoords="offset points",xytext=(0,dy),fontsize=8,color="#cdd6e0",ha="center")
ax.text(3e-4,0.45,"① STUCK AT THE SPHERE POLE\nlow spin: gravity holds the sphere\nf≈0 regardless of size/mass",color="#5aa0ff",fontsize=9,ha="left")
ax.text(3.3e-2,0.50,"② CROSSING\nspin overtakes,\nflattening rises",color="#7CFC9A",fontsize=9,ha="left")
ax.text(4e-1,0.30,"③ TAPER / MAX\nrotational breakup;\nHaumea = Jacobi,\nsheds ring + moons",color="#b197fc",fontsize=9,ha="left")
ax.set_xscale("log"); ax.set_xlabel("spin parameter  m = ω²a³/GM  (centrifugal ÷ gravity — the higher component)",color="#cbd5e1")
ax.set_ylabel("flattening  f = (a−c)/a",color="#cbd5e1")
ax.set_xlim(8e-6,3); ax.set_ylim(-0.02,0.60)
ax.set_title("JUMP 2 · rotational-flattening rung — spin is the new higher component\n"
             f"f tracks spin (ρ={spearmanr(f,mspin)[0]:+.2f}), not size (ρ={spearmanr(f,a)[0]:+.2f}) or mass (ρ={spearmanr(f,M)[0]:+.2f}); breakup at m~1",
             color="#e6edf3",fontsize=12)
ax.legend(facecolor="#161b22",labelcolor="#cbd5e1",fontsize=9,loc="upper left")
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/jump2_rotation.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116"); print("\nsaved",out)
