"""
Tier gradient: zoom INTO one system's ladder -- energy vs information as a smooth gradient
==========================================================================================
Dylan's correction: the datum/signal/meaning tiers don't SEPARATE between two whole systems
(a whole system sits on ONE meta-rung -- at that zoom it's a single node, so clock and fuel
ride together). To see the separation you look DOWN further -- into ONE system's own rung
ladder. The tiers are a GRADIENT along the ladder, not discrete channels.

Clean physical handle inside ONE system (the warm-water battery):
   FLUX  = d(WWV)/dt = water MOVING   = energy / datum tier   (transport)
   LEVEL = WWV        = water STORED   = information / meaning  (memory carried forward)
   (level is the integral of flux: storage vs transport.)

Sweep a phi-spaced ladder of rungs. At each rung measure the fraction of FLUX power vs the
fraction of LEVEL power living there. Prediction: a SMOOTH gradient -- fast rungs flux-
dominated (energy), slow rungs level-dominated (memory), crossing at one meta-rung (the
snap / ARA~1 handover). That crossover is where energy hands the baton to information.

Data: PMEL WWV warm-water volume (one system, looked at down its own ladder). Real.
"""
import numpy as np
from numpy.fft import rfft, rfftfreq

PHI=(1+5**0.5)/2

def load_wwv(p):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==3 and s[0].isdigit() and len(s[0])==6: d[s[0]]=float(s[2])/1e14
    return d

def band_power(x, lo, hi):
    """fraction of total variance of x living in period band [lo,hi] months."""
    x=x-x.mean(); n=len(x); f=rfftfreq(n,d=1.0); P=np.abs(rfft(x))**2
    per=np.where(f>0,1.0/np.maximum(f,1e-9),np.inf)
    tot=P[1:].sum()
    m=(per>=lo)&(per<=hi)
    return float(P[m].sum()/tot) if tot>0 else 0.0

def main():
    wwv=load_wwv("wwv_west.dat")
    wk=sorted(wwv); W=np.array([wwv[wk[i]] for i in range(len(wk))])
    flux=np.gradient(W)
    print(f"WWV battery: {len(wk)} mo  {wk[0]}..{wk[-1]}")
    print("LEVEL = stored water (memory/info) ; FLUX = d/dt = moving water (energy)\n")

    # phi-spaced rung ladder of CENTER periods, half-rung-wide bands (sqrt(phi) each side)
    centers=[3.0*PHI**(k/2) for k in range(0,16)]   # ~3mo up to ~ a few years/decadal
    half=PHI**0.25
    print(f"{'rung':>4} {'period':>7}  {'FLUX%(energy)':>13} {'LEVEL%(info)':>12}   tilt")
    rows=[]
    for k,c in enumerate(centers):
        lo,hi=c/half, c*half
        e=band_power(flux,lo,hi); i=band_power(W,lo,hi)
        rows.append((c,e,i))
        bar_e=int(round(e*40));
        tilt = "ENERGY" if e>i else ("info" if i>e else "even")
        print(f"{k:>4} {c:>6.1f}mo  {e*100:>11.1f}%  {i*100:>10.1f}%   {tilt}")

    # find smooth crossover (where level overtakes flux)
    cross=None
    for a,b in zip(rows,rows[1:]):
        if (a[1]-a[2])>0 and (b[1]-b[2])<=0:
            # linear interp in log-period
            ca,ea,ia=a; cb,eb,ib=b
            da=ea-ia; db=eb-ib
            t=da/(da-db) if (da-db)!=0 else 0.5
            cross=ca*(cb/ca)**t
            break
    print()
    if cross:
        print(f"CROSSOVER (energy hands baton to information): ~{cross:.1f} months")
        print(f"   = {cross/12:.2f} years   (the snap / ARA~1 handover rung)")
    else:
        print("No single clean crossover -- gradient may be monotone across this window.")
    print("\nOne system, looked at down its own phi-ladder. Smooth tilt fast->slow = the tiers")
    print("are a GRADIENT, not separate channels. Descriptive diagnostic. PMEL WWV, real.")

if __name__=="__main__": main()
