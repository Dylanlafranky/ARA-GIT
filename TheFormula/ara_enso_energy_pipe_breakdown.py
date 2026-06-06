import sys, numpy as np
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
PHI=F.PHI
def load_dmi(p,miss=-9990.0):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==13 and s[0].isdigit() and len(s[0])==4:
            for mo in range(1,13):
                try:v=float(s[mo])
                except:continue
                if v>miss:d[f"{int(s[0])}{mo:02d}"]=v
    return d
W=B.load_wwv("wwv_west.dat");E=B.load_wwv("wwv_east.dat");nino=B.load_nino("nino34_long_anom.csv")
SOI=B.load_soi("soi.data");PDO=B.load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat");IOD=load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
def arr(d,keys): return np.array([d[k] for k in keys])
# energy per rung = variance of causal bandpass at period P
def rung_energy(x, periods):
    x=np.asarray(x,float); x=x-np.nanmean(x)
    out=[]
    for P in periods:
        b=F.causal_bandpass(x,P,0.20); out.append(np.nanvar(b))
    return np.array(out)
# phi-rung ladder anchored at annual (12mo): 12, 12*phi, 12*phi^2 ...
rungs=[12*PHI**k for k in range(0,7)]
print("phi-rung ladder (months):", [f"{r:.0f}" for r in rungs])
systems={"NINO(surface)":nino,"SOI(atmos)":SOI,"WWVw(subsurf)":W,"WWVe(subsurf)":E,"IOD":IOD,"PDO":PDO}
# common keys
ck=sorted(set.intersection(*[set(d) for d in systems.values()]))
print(f"common span {ck[0]}..{ck[-1]} n={len(ck)}\n")
print(f"{'system':>16} | "+ " ".join(f"{r:>5.0f}mo" for r in rungs)+" | conc  pipe%")
for nm,d in systems.items():
    en=rung_energy(arr(d,ck),rungs); frac=en/en.sum()
    conc=frac.max()                         # concentration = fullest single pipe
    print(f"{nm:>16} | "+" ".join(f"{f*100:>5.0f}%" for f in frac)+f" | {conc:.3f} {conc*100:>4.0f}")
# rung-to-rung cascade ratio for NINO (does energy fall ~1/phi per rung as framework claims?)
en=rung_energy(arr(nino,ck),rungs); en=en/en.max()
print(f"\nNINO rung-energy cascade (normalized to peak): "+" ".join(f"{e:.2f}" for e in en))
ratios=[en[i+1]/en[i] for i in range(len(en)-1) if en[i]>1e-9]
print(f"adjacent-rung ratios: "+" ".join(f"{r:.2f}" for r in ratios))
print(f"framework constants: 1/phi={1/PHI:.3f}  1/phi^2={1/PHI**2:.3f}  phi/2={PHI/2:.3f}  (time-pipe direct share)")
# theoretical pipe capacity: space pipe=2 hands to time pipe=phi; direct share phi/2, shed 1-phi/2
print(f"\nPIPE CAPACITY (framework): Space-pipe width 2 -> Time-pipe width phi")
print(f"  direct through-share  phi/2 = {PHI/2:.3f}  (max fraction that passes head-on at once)")
print(f"  shed/recycled         1-phi/2 = {1-PHI/2:.3f}")
print(f"  => a pipe whose dominant rung holds < {PHI/2:.3f} of energy has HEADROOM (energy spread);")
print(f"     one above {PHI/2:.3f} is saturated (one wave dominates -> framework ties a clock).")
