"""
Flux across the grip: is a LOCK pure information (Sys3) or energy (Sys1)?
=========================================================================
Information^3 test. Dylan: the in-phase LOCKS (IOD beside, PDO above) act as a shared CLOCK
-- they agree on meaning, they don't trade fuel. The COUNTERSPIN below (MJO) is the raw
datum -- energy actually crossing the boundary.

Prediction:
   * LOCK partners (IOD, PDO): near-ZERO coupling to warm-water flux  (meaning tier, no energy)
   * COUNTERSPIN partner (MJO below): REAL coupling to warm-water flux (datum tier, energy moves)
   * ENSO itself vs its own flux: strong (reference -- it IS the battery's system)

Energy crossing the ENSO boundary = warm-water FLOW RATE = d(WWV)/dt.
For each partner band we report:
   corr(partner band, flux) and PLV, plus mean flux in partner's warm vs cool half.
Low flux coupling = the grip carries information, not energy.

Data: NOAA NINO3.4, PMEL WWV (heat battery), NOAA PSL DMI(IOD), NOAA ERSST PDO, BoM RMM(MJO).
Real, independent. Descriptive diagnostic.
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
def load_wwv(p):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==3 and s[0].isdigit() and len(s[0])==6: d[s[0]]=float(s[2])/1e14
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
def load_pdo(p,miss=99.0):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==13 and s[0].isdigit() and len(s[0])==4:
            yr=int(s[0])
            for mo in range(1,13):
                try: v=float(s[mo])
                except: continue
                if v<miss-0.001: d[f"{yr}{mo:02d}"]=v
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
def xcorr_lead(a,b,maxlag=18):
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std(); n=len(a); out=[]
    for L in range(-maxlag,maxlag+1):
        if L>=0: x=a[:n-L]; y=b[L:]
        else:    x=a[-L:];  y=b[:n+L]
        out.append((L,float(np.mean(x*y))))
    return max(out,key=lambda t:abs(t[1]))

EDGE=18
def flux_grip(name, partner, flux_full, keys_p, keys_flux, lo, hi):
    # align partner to the flux timeline
    common=[k for k in keys_flux if k in keys_p]
    pf={k:v for k,v in zip(keys_p,partner)}
    ff={k:v for k,v in zip(keys_flux,flux_full)}
    P=np.array([pf[k] for k in common]); FX=np.array([ff[k] for k in common])
    pb=bandpass_fft(P,lo,hi)[EDGE:-EDGE]; fb=bandpass_fft(FX,lo,hi)[EDGE:-EDGE]
    fx=FX[EDGE:-EDGE]
    dphi=np.angle(analytic(pb))-np.angle(analytic(fb))
    plv=np.abs(np.mean(np.exp(1j*dphi)))
    L,c=xcorr_lead(pb,fb,maxlag=18)
    warm=pb>0
    f_warm=fx[warm].mean(); f_cool=fx[~warm].mean()
    print(f"   {name:20s} {lo:>2}-{hi:>2}mo : flux-coupling PLV {plv:.2f}  corr {c:+.2f} @ lag {L:+d}   "
          f"flux warm {f_warm:+.4f} / cool {f_cool:+.4f}  (|gap| {abs(f_warm-f_cool):.4f})")
    return plv,abs(c)

def main():
    nino=load_nino("nino34_long_anom.csv"); wwv=load_wwv("wwv_west.dat")
    iod=load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
    pdo=load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")
    mjo=load_mjo_amp("mjo_rmm.txt")

    wk=sorted(wwv); W=np.array([wwv[k] for k in wk]); flux=np.gradient(W)   # energy crossing boundary
    print(f"WWV (battery) span {wk[0]}..{wk[-1]}  ({len(wk)} mo). flux = d(WWV)/dt = energy in/out\n")

    print("== FLUX ACROSS EACH GRIP  (does the lock move fuel, or just share a clock?) ==")
    print("   reference -- ENSO's OWN system vs its battery flux (should be LOUD):")
    nk=sorted(set(nino)&set(wwv)); Tn=np.array([nino[k] for k in nk])
    flux_grip("ENSO (self)", Tn, flux, nk, wk, 18,33)
    print("   LOCKS -- side/above (should be QUIET on energy if pure information):")
    ik=sorted(iod); Iv=np.array([iod[k] for k in ik])
    pk=sorted(pdo); Pv=np.array([pdo[k] for k in pk])
    flux_grip("IOD (side, lock)", Iv, flux, ik, wk, 18,33)
    flux_grip("PDO (above, lock)", Pv, flux, pk, wk, 40,70)
    print("   COUNTERSPIN -- genuine rung below (should be LOUD on energy if datum tier):")
    mk=sorted(mjo); Mv=np.array([mjo[k] for k in mk])
    flux_grip("MJO (below, spin)", Mv, flux, mk, wk, 10,16)
    flux_grip("MJO (below, spin)", Mv, flux, mk, wk, 18,33)
    print()
    print("Reading: low flux-coupling + tiny warm/cool gap = grip carries INFORMATION (Sys3).")
    print("High flux-coupling + big warm/cool gap = grip carries ENERGY (Sys1).")
    print("Real NOAA/PMEL/BoM indices. Descriptive diagnostic, not a forecast claim.")

if __name__=="__main__": main()
