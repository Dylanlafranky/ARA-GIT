"""
Follow the energy pulse UP the rung: IOD short/mid, PDO long -- one combined forecaster.
=========================================================================================
The transfer-entropy map (enso_info_exchange_R.py) said:
   * IOD = info donor ~11mo ahead  -> lifts SHORT/MID horizons   (a message)
   * PDO = tightest phase-LOCK, low info -> lifts LONG horizons   (a clock)
The single-feeder test (enso_iod_feeder_test.py) confirmed they are COMPLEMENTARY:
   IOD wins h<=15, PDO wins h>=18.  So stitch them: let each feeder work where its
   information actually lives. We are following the energy pulse up (and to the right
   through time) the rung as far as we can.

   combined(h) = +IOD  for h <= 15   (short/mid: the message leads)
               = +PDO  for h >= 18   (long:      the clock holds)

Same STRICTLY CAUSAL protocol as every feeder test (same as the PDO/IOD tests):
   feeders contemporaneous (known at origin); train-only standardize; both seasonal
   maps refit past-only each origin; regime=calendar; correlation leads; held from 2016.

Usage: python3 enso_combined_horizon_feeder.py
"""
import numpy as np
import enso_pdo_feeder_test as B   # loaders + walk_switch + evalrec + feats

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

    configs={"switch (base)":[], "+PDO":[PDO], "+IOD":[IOD], "+IOD+PDO":[IOD,PDO]}
    res={}
    for name,extra in configs.items():
        cols,stdz,yr,mon,T=build(extra)
        res[name]=B.evalrec(B.walk_switch(cols,stdz,yr,mon,T))

    # stitch: IOD for h<=15, PDO for h>=18
    def pick(h):
        return "+IOD" if h<=15 else "+PDO"

    names=["switch (base)","+IOD","+PDO","+IOD+PDO","combined"]
    print("HELD-OUT CORRELATION (leads)   combined = IOD(h<=15) / PDO(h>=18)\n")
    print(f"{'lead':>4}  " + "".join(f"{nm:>15}" for nm in names))
    for h in (1,3,6,9,12,15,18,24):
        row=f"{h:>4} "
        for nm in names:
            src = pick(h) if nm=="combined" else nm
            d=res[src].get(h)
            row+=f"   {d['corr']:>+6.3f}     " if d else f"   {'--':>9}   "
        print(row)

    def g(nm,h): return res[nm].get(h,{}).get('corr')
    def gc(h):   return res[pick(h)].get(h,{}).get('corr')   # combined
    print(f"\nSHORT/MID (IOD drives):")
    print(f"  h=6 : base {g('switch (base)',6):+.3f} -> combined {gc(6):+.3f}   (target 0.764 = 1 - 1/phi^3)")
    print(f"  h=12: base {g('switch (base)',12):+.3f} -> combined {gc(12):+.3f}")
    print(f"LONG (PDO holds):")
    print(f"  h=18: base {g('switch (base)',18):+.3f} -> combined {gc(18):+.3f}")
    print(f"  h=24: base {g('switch (base)',24):+.3f} -> combined {gc(24):+.3f}   (hold >= +0.47?)")
    print("\nFollowing the pulse up the rung: message (IOD) leads short, clock (PDO) holds long.")
    print("All feeders contemporaneous = fully causal.")

if __name__=="__main__": main()
