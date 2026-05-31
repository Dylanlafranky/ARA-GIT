"""
Down-2 octave test with a GENUINELY FASTER lower rung (not ENSO's own battery)
==============================================================================
Last run's flaw: WWV had the SAME period as ENSO (it's ENSO's own subsurface), so the
counterspin I found was surface-vs-subsurface inside ENSO, not a true rung below. Here
the lower rung is MJO -- real, independent, intraseasonal, genuinely faster than ENSO.

Ladder of INDEPENDENT real systems by speed:
    PDO  (above)   ~decadal
    ENSO (us)      ~4-5 yr
    MJO  (below)   intraseasonal/seasonal  <- the faster lower rung

Dylan's rotation predicts, on the DOWN-link to the faster rung:
    * octave spacing  (ENSO period / MJO period ~ a power of 2)
    * counterspin     (anti-phase where they share a band)
    * a return path   (which one leads -> energy handed up after processing below)

Self-reference guard: MJO is a separate observing system (BoM RMM), not a filter of NINO.
Data: NOAA NINO 3.4, BoM RMM (MJO), PMEL WWV. Real. Descriptive diagnostic.
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
    lead=("ENSO leads" if (L>0)==(name.startswith("ENSO")) and L!=0 else ("lower leads" if L!=0 else "in step"))
    print(f"   {name:24s} {lo:>3}-{hi:>3}mo : PLV {plv:.2f}  offset {off:+4.0f}deg ({kind})  corr {c:+.2f} @ lag {L:+d}")
    return off,c,L

def main():
    nino=load_nino("nino34_long_anom.csv"); wwv=load_wwv("wwv_west.dat"); mjo=load_mjo_amp("mjo_rmm.txt")
    keys=sorted(set(nino)&set(mjo))
    T=np.array([nino[k] for k in keys]); M=np.array([mjo[k] for k in keys])
    print(f"NINO/MJO overlap: {len(keys)} mo  {keys[0]}..{keys[-1]}\n")

    print("== 1. WHERE DOES THE LOWER RUNG SIT?  (dominant periods) ==")
    pn_long=dom_period(T,18,200); pn_qb=dom_period(T,18,40)
    pm_fast=dom_period(M,2,18); pm_any=dom_period(M,2,200)
    print(f"   ENSO interannual {pn_long:5.1f} mo (quasi-biennial {pn_qb:4.1f})   MJO fast {pm_fast:4.1f} mo (any {pm_any:5.1f})")
    print(f"   octave check ENSO/MJOfast = {pn_long/pm_fast:.2f}   (4 = two octaves, 8 = three)")
    # express the gap in octaves (log2)
    print(f"   gap in octaves = log2(ENSO/MJOfast) = {np.log2(pn_long/pm_fast):.2f}\n")

    print("== 2. DOWN-LINK PHASE: ENSO vs the faster MJO rung ==")
    # compare where they can share a band: the seasonal/annual band both carry
    for lo,hi in [(10,16),(18,33)]:
        phase_pair("ENSO <-> MJO (below)", T, M, lo, hi)
    print()

    print("== 3. WHO LEADS? (broadband activity envelope: MJO activity vs ENSO) ==")
    me=np.abs(analytic(M-M.mean())); te=np.abs(analytic(bandpass_fft(T,18,200)))
    L,c=xcorr_lead(me[EDGE:-EDGE], te[EDGE:-EDGE], maxlag=24)
    who = "MJO activity LEADS ENSO (feeds up)" if L<0 else ("ENSO LEADS MJO (modulates down)" if L>0 else "in step")
    print(f"   MJO activity <-> ENSO envelope : corr {c:+.2f} at lag {L:+d} mo -> {who}\n")

    print("== 4. CROSS-CHECK: warm-water faster bands vs ENSO (intra-ENSO, flagged) ==")
    keys2=sorted(set(nino)&set(wwv)); T2=np.array([nino[k] for k in keys2]); W2=np.array([wwv[k] for k in keys2])
    for lo,hi in [(10,16),(18,33)]:
        phase_pair("ENSO <-> WWV", T2, W2, lo, hi)
    print("\nMJO is an independent faster system (no self-reference). WWV block is intra-ENSO")
    print("(same system, surface vs subsurface) -- shown only as a cross-check. Descriptive.")

if __name__=="__main__": main()
