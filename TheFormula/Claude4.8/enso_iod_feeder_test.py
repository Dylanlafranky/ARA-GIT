"""
Fold the INFO-DONOR (IOD) into the ENSO forecast -- the R says it leads ~11mo.
=============================================================================
The transfer-entropy map (enso_info_exchange_R.py) found:
   * IOD  = real NET information donor to ENSO, ~11mo ahead (z +3.2)   <- never used before
   * WWV  = info donor ~8mo (already in base)
   * PDO  = tightest phase-LOCK but lowest info transfer (z +1.0)      <- a clock, not a message
   * SOI  = simultaneous (lag 0), no predictive lead (already in base)

So the lever is IOD. Head-to-head, STRICTLY CAUSAL (same protocol as the PDO test):
   switch (base) = T, zWWV, zWWVe, zSOI         [prior champion]
   +PDO          = base + zPDO                  [the lock -- expected weak]
   +IOD          = base + zIOD                  [the info-donor -- expected to lift long horizons]

Causal: feeder at origin i is contemporaneous (known); train-only standardize; both seasonal
maps refit past-only each origin; regime=calendar; correlation leads; held out from 2016.

Usage: python3 enso_iod_feeder_test.py
"""
import numpy as np
import enso_pdo_feeder_test as B   # reuse loaders + walk_switch + evalrec + feats

def load_dmi(p,miss=-9990.0):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==13 and s[0].isdigit() and len(s[0])==4:
            yr=int(s[0])
            if yr<1800 or yr>2100: continue
            for mo in range(1,13):
                try: v=float(s[mo])
                except: continue
                if v>miss: d[f"{yr}{mo:02d}"]=v
    return d

def main():
    W=B.load_wwv("wwv_west.dat"); E=B.load_wwv("wwv_east.dat")
    nino=B.load_nino("nino34_long_anom.csv"); SOI=B.load_soi("soi.data")
    PDO=B.load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")
    IOD=load_dmi("../../../../IOD_NOAA/dmi.had.long.data")

    base_keys=sorted(set(W)&set(E)&set(nino)&set(SOI)&set(PDO)&set(IOD))
    print(f"aligned (T,WWV,SOI,PDO,IOD): {len(base_keys)}  {base_keys[0]}..{base_keys[-1]}\n")

    def build(extra):
        keys=list(base_keys)
        T=np.array([nino[k] for k in keys]); Wv=np.array([W[k] for k in keys])
        Ev=np.array([E[k] for k in keys]); Sv=np.array([SOI[k] for k in keys])
        yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
        mon=np.array([int(k[4:6]) for k in keys])
        cols=[T,Wv,Ev,Sv]; stdz=[1,2,3]
        for d in extra:
            cols.append(np.array([d[k] for k in keys])); stdz.append(len(cols)-1)
        return cols,stdz,yr,mon,T

    configs={"switch (base)":[], "+PDO":[PDO], "+IOD":[IOD]}
    res={}
    for name,extra in configs.items():
        cols,stdz,yr,mon,T=build(extra)
        res[name]=B.evalrec(B.walk_switch(cols,stdz,yr,mon,T))

    names=list(configs)
    print("HELD-OUT CORRELATION (leads)\n")
    print(f"{'lead':>4}  " + "".join(f"{nm:>15}" for nm in names))
    for h in (1,3,6,9,12,15,18,24):
        row=f"{h:>4} "
        for nm in names:
            d=res[nm].get(h)
            row+=f"   {d['corr']:>+6.3f}     " if d else f"   {'--':>9}   "
        print(row)
    def g(nm,h): return res[nm].get(h,{}).get('corr')
    print(f"\nh=6 : base {g('switch (base)',6):+.3f} -> +IOD {g('+IOD',6):+.3f}   (target 0.764 = 1 - 1/phi^3)")
    print(f"h=12: base {g('switch (base)',12):+.3f} -> +IOD {g('+IOD',12):+.3f}")
    print(f"h=24: base {g('switch (base)',24):+.3f} -> +IOD {g('+IOD',24):+.3f}")
    print("\nAll feeders contemporaneous = fully causal. IOD is the transfer-entropy donor (~11mo lead).")

if __name__=="__main__": main()
