"""
Side-and-down: does ENSO hand off DIAGONALLY (to a neighbour) instead of straight down?
=======================================================================================
Dylan's read of the octave test: straight "down 2" should land on a clean x4 (two octaves).
We got x4.64 = 2.21 octaves -- OFF the grid. Landing between rungs is the fingerprint of a
DIAGONAL move (down a step AND sideways), same geometry as the dark-sector 3.5=7/2 diagonal.
That also explains why MJO (straight below) gripped weakly (PLV 0.24): the energy veers to the
side, not straight down.

Test: a system BESIDE ENSO -- different basin, loosely coupled, faster -- should grip MORE
cleanly than the straight-down MJO. Candidate: IOD (Indian Ocean Dipole). Different ocean,
snaps in a single autumn (faster than ENSO's 4-5yr), loosely roped to ENSO.

Compare head-to-head:
    DOWN      ENSO <-> MJO  (same-ish basin, straight below)   <- weak (0.24)
    SIDE-DOWN ENSO <-> IOD  (neighbour basin, faster)          <- does it grip tighter?

Data: NOAA NINO 3.4, NOAA PSL DMI (IOD), BoM RMM (MJO). Real. Descriptive diagnostic.
"""
import numpy as np
from numpy.fft import rfft, irfft, rfftfreq

def load_nino(p,miss=-99.99):
    d={}
    for ln in open(p):
        s=[x.strip() for x in ln.split(",")]
        if len(s)==2 and s[0][:4].isdigit():
            v=float(s[1])
            if v>miss+0.001: d[s[0][:7].replace("-","")]=v
    return d
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
def load_mjo_amp(p):
    acc={}
    for ln in open(p):
        s=ln.split()
        if len(s)<7 or not s[0].isdigit(): continue
        yr,mo=s[0],int(s[1]); amp=float(s[6])
        if amp>900: continue
        acc.setdefault(f"{yr}{mo:02d}",[]).append(amp)
    return {k:float(np.mean(v)) for k,v in acc.items()}

def bandpass_fft(x, lo, hi):
    x=x-x.mean(); n=len(x); f=rfftfreq(n,d=1.0); F=rfft(x)
    per=np.where(f>0,1.0/np.maximum(f,1e-9),np.inf)
    return irfft(np.where((per>=lo)&(per<=hi),F,0.0),n=n)
def analytic(x):
    n=len(x); Xf=np.fft.fft(x); h=np.zeros(n)
    if n%2==0: h[0]=h[n//2]=1; h[1:n//2]=2
    else: h[0]=1; h[1:(n+1)//2]=2
    return np.fft.ifft(Xf*h)
def dom_period(x, lo, hi):
    x=x-x.mean(); n=len(x); f=rfftfreq(n,d=1.0); Pw=np.abs(rfft(x))**2
    per=np.where(f>0,1.0/np.maximum(f,1e-9),np.inf)
    idx=np.where((per>=lo)&(per<=hi))[0]
    return per[idx[np.argmax(Pw[idx])]]
def xcorr_lead(a,b,maxlag=24):
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std(); n=len(a); out=[]
    for L in range(-maxlag,maxlag+1):
        if L>=0: x=a[:n-L]; y=b[L:]
        else:    x=a[-L:];  y=b[:n+L]
        out.append((L,float(np.mean(x*y))))
    return max(out,key=lambda t:abs(t[1]))

EDGE=18
def phase_pair(name, a, b, lo, hi):
    ab=bandpass_fft(a,lo,hi)[EDGE:-EDGE]; bb=bandpass_fft(b,lo,hi)[EDGE:-EDGE]
    dphi=np.angle(analytic(ab))-np.angle(analytic(bb))
    plv=np.abs(np.mean(np.exp(1j*dphi))); off=np.degrees(np.angle(np.mean(np.exp(1j*dphi))))
    L,c=xcorr_lead(ab,bb)
    kind=("in-phase" if abs(off)<45 else "COUNTERSPIN" if abs(off)>135 else "quadrature")
    print(f"   {name:22s} {lo:>3}-{hi:>3}mo : PLV {plv:.2f}  offset {off:+4.0f}deg ({kind})  corr {c:+.2f} @ lag {L:+d}")
    return plv,off,c,L

def main():
    nino=load_nino("nino34_long_anom.csv"); iod=load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
    mjo=load_mjo_amp("mjo_rmm.txt")

    print("== 1. WHERE DOES THE SIDE NEIGHBOUR SIT? (dominant periods) ==")
    ki=sorted(set(nino)&set(iod)); T=np.array([nino[k] for k in ki]); I=np.array([iod[k] for k in ki])
    pn=dom_period(T,18,200); pi_f=dom_period(I,2,18); pi_any=dom_period(I,2,200)
    print(f"   NINO/IOD overlap {len(ki)} mo  {ki[0]}..{ki[-1]}")
    print(f"   ENSO interannual {pn:5.1f} mo    IOD fast {pi_f:4.1f} mo (any {pi_any:5.1f})")
    print(f"   octave gap ENSO/IOD = {pn/pi_f:.2f}  = {np.log2(pn/pi_f):.2f} octaves")
    print(f"   (straight-down MJO was x4.64 = 2.21 octaves, OFF the grid)\n")

    print("== 2. GRIP TEST: does the SIDE neighbour (IOD) lock tighter than straight-down (MJO)? ==")
    km=sorted(set(nino)&set(mjo)); Tm=np.array([nino[k] for k in km]); M=np.array([mjo[k] for k in km])
    print("   SIDE-DOWN  ENSO <-> IOD:")
    for lo,hi in [(10,16),(18,33),(24,40)]:
        phase_pair("ENSO<->IOD (side)", T, I, lo, hi)
    print("   STRAIGHT-DOWN  ENSO <-> MJO (for comparison):")
    for lo,hi in [(10,16),(18,33),(24,40)]:
        phase_pair("ENSO<->MJO (below)", Tm, M, lo, hi)
    print()

    print("== 3. WHO LEADS the side neighbour? (envelope lead/lag) ==")
    te=np.abs(analytic(bandpass_fft(T,18,200)))[EDGE:-EDGE]
    ie=np.abs(analytic(I-I.mean()))[EDGE:-EDGE]
    L,c=xcorr_lead(ie,te,maxlag=24)
    who="IOD LEADS ENSO (feeds back up)" if L<0 else ("ENSO LEADS IOD (hands off down/side)" if L>0 else "in step")
    print(f"   IOD activity <-> ENSO envelope : corr {c:+.2f} at lag {L:+d} mo -> {who}\n")

    print("IOD is an independent neighbour basin (no self-reference). Descriptive diagnostic.")

if __name__=="__main__": main()
