"""
ROUSE-NUMBER ARA across sediment-transport systems (Bagnold/Rouse, ARA-ised).
Accumulation = settling/deposition ; Release = turbulent suspension/erosion.
Variable: s = w_s / u*  (fall velocity / shear velocity) = kappa * Rouse.
Ridge (s=1) is EMPIRICALLY the suspension<->saltation transition (fall~friction ~ unity) [M1,M3].

Dylan's prediction: adjusting for MEDIUM (air/water/Mars) and DIMENSION (bed vs volume),
the systems collapse to a SIMILAR ARA structure (self-similar, like the caves<->sinuses test 152).

REPLICABILITY (standing rule): settling from Ferguson & Church (2004) closed form; every grain
size / shear velocity / fluid property is a cited public value (sources below). Deterministic.

SOURCES
[F] Ferguson & Church 2004, Water Resour Res / J.Sed.Res: w=R g D^2/(C1 nu + sqrt(0.75 C2 R g D^3)), C1=18,C2=1.
[M1] Aeolian sand transport active at u*~0.5 m/s, threshold ~0.25; sand ~0.25-0.27 mm.
     leovanrijn-sediment.com Aeoliansandtransport2018 ; USGS Lees Ferry threshold dataset.
[M2] Fluvial shear velocities: gravel-bed u*~0.1-0.3, sand-bed ~0.05-0.1 m/s (open-channel texts, Julien).
[M3] Mars: impact-threshold u*t ~1.0 m/s; suspension<->saltation grain 52 um (Earth) vs 210 um (Mars);
     transition when fall/friction ~ unity. pnas.org/doi/10.1073/pnas.0800202105 ; Sullivan 2017 JGR.
[M4] Turbidity currents: u* ~0.3-1 m/s, fine sand/silt suspended (deep-sea sedimentology).
[M5] Delta / floodplain deposition: decelerating flow u*~0.01-0.03, fines settle (deltaic sedimentation).
"""
import numpy as np
np.random.seed(0)
kappa=0.41; C1=18.0; C2=1.0

# fluids: rho_f (kg/m3), nu (m2/s), g (m/s2), grain rho_s
WATER=dict(rho=1000., nu=1.0e-6, g=9.81, rhos=2650.)   # quartz in water
AIR  =dict(rho=1.20,  nu=1.5e-5, g=9.81, rhos=2650.)   # quartz in Earth air
MARS =dict(rho=0.020, nu=5.5e-4, g=3.71, rhos=3000.)   # basalt in Mars CO2 (~600 Pa)

def settling(D, med):
    R=med["rhos"]/med["rho"]-1.0
    return R*med["g"]*D**2 / (C1*med["nu"] + np.sqrt(0.75*C2*R*med["g"]*D**3))

# name, medium, grain D (m), u* (m/s), transport MODE, source
SYS=[
 ("Aeolian dune",       AIR,  0.25e-3, 0.40, "saltation/bed", "M1"),
 ("Aeolian ripple",     AIR,  0.30e-3, 0.30, "saltation/bed", "M1"),
 ("Dust storm (silt)",  AIR,  0.020e-3,0.50, "suspension",    "M1"),
 ("Gravel-bed river",   WATER,30.0e-3, 0.15, "bedload",       "M2"),
 ("Sand-bed river",     WATER,0.40e-3, 0.08, "mixed/bed",     "M2"),
 ("River-mouth delta",  WATER,0.10e-3, 0.02, "deposition",    "M5"),
 ("Floodplain mud",     WATER,0.010e-3,0.01, "deposition",    "M5"),
 ("Turbidity current",  WATER,0.10e-3, 0.50, "suspension",    "M4"),
 ("Beach swash",        WATER,0.30e-3, 0.05, "mixed/bed",     "M2"),
 ("Alluvial fan",       WATER,5.0e-3,  0.20, "bedload",       "M2"),
 ("Mars dune",          MARS, 0.15e-3, 1.00, "saltation/bed", "M3"),
 ("Mars dust",          MARS, 0.003e-3,1.00, "suspension",    "M3"),
]
MEDNAME={id(WATER):"water",id(AIR):"air",id(MARS):"Mars"}

rows=[]
for nm,med,D,us,mode,src in SYS:
    ws=settling(D,med); s=ws/us; P=s/kappa
    rows.append((nm,MEDNAME[id(med)],D,us,ws,s,P,mode,src))

# ---- ARA map: ridge at s=1 (sourced transition). deposition(s>1)->pole 2 ; suspension(s<1)->pole 0 ----
def ARA(s,W): return 1+np.tanh(np.log(s)/W)

print("=== ROUSE-ARA PROVENANCE (every value sourced) ===")
print(f"{'system':18s} {'medium':6s} {'D(mm)':>7s} {'u*(m/s)':>7s} {'w_s(m/s)':>9s} {'s=ws/u*':>8s} {'Rouse P':>8s} {'ARA(W2)':>7s}  mode [src]")
for (nm,mn,D,us,ws,s,P,mode,src) in rows:
    print(f"{nm:18s} {mn:6s} {D*1e3:7.3f} {us:7.2f} {ws:9.4f} {s:8.3f} {P:8.2f} {ARA(s,2.0):7.3f}  {mode} [{src}]")

# ---- COLLAPSE TEST: does medium wash out, mode organize? ----
import numpy as np
s_all=np.array([r[5] for r in rows]); mode_all=[r[7] for r in rows]; med_all=[r[1] for r in rows]
def grp(keys,vals):
    out={}
    for k,v in zip(keys,vals): out.setdefault(k,[]).append(v)
    return {k:(np.mean(np.log10(v)),np.std(np.log10(v)),len(v)) for k,v in out.items()}
print("\n=== COLLAPSE TEST (log10 s = log10 fall/friction) ===")
print("by MEDIUM (Dylan: medium should wash OUT -> big within-group spread):")
for k,(m,sd,n) in grp(med_all,s_all).items(): print(f"  {k:6s} n={n} mean log10 s={m:+.2f}  sd={sd:.2f}")
print("by MODE (should ORGANIZE -> tight within-group spread):")
for k,(m,sd,n) in grp(mode_all,s_all).items(): print(f"  {k:16s} n={n} mean log10 s={m:+.2f}  sd={sd:.2f}")
# variance explained by medium vs by mode
def eta2(keys,vals):
    v=np.log10(vals); grand=v.mean(); ss_tot=((v-grand)**2).sum()
    ss_between=0.0
    for k in set(keys):
        gi=np.array([vv for kk,vv in zip(keys,v) if kk==k]); ss_between+=len(gi)*(gi.mean()-grand)**2
    return ss_between/ss_tot
print(f"\nvariance in log10 s explained by MEDIUM: eta^2 = {eta2(med_all,s_all):.2f}")
print(f"variance in log10 s explained by MODE  : eta^2 = {eta2(mode_all,s_all):.2f}")
print("Dylan's prediction holds if MODE eta^2 >> MEDIUM eta^2 (medium washes out, mode/dimension organizes).")
