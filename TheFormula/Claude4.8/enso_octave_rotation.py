"""
Octave rotation: leaf falls DOWN-2, counterspins below, returns UP
==================================================================
Dylan's mechanism: energy from the system ABOVE (PDO) doesn't drop one rung into ENSO.
It drops TWO (the octave), passing through ENSO down to the warm-water layer BELOW as
COUNTERSPIN (anti-phase), gets processed there, then rotates back UP into ENSO. That
round trip is what makes the ladder space by x2 (octaves).

Three phase predictions (the mechanism's fingerprint):
  UP-link    ENSO <-> PDO (above)      : IN-PHASE / locked      (energy sits with the clock)
  DOWN-link  ENSO <-> WWV (below/warm) : COUNTERSPIN / anti-phase
  RETURN     WWV should LEAD ENSO      : charged below, comes back up

Plus the spacing test: dominant interannual periods of WWV / NINO / PDO -- do they sit on
a x2 (octave) ladder?

Data: NOAA NINO 3.4, PMEL WWV (warm water), NOAA ERSST v5 PDO. Real. Descriptive.
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

def bandpass_fft(x, lo, hi):
    x=x-x.mean(); n=len(x); f=rfftfreq(n,d=1.0); F=rfft(x)
    per=np.where(f>0,1.0/np.maximum(f,1e-9),np.inf)
    return irfft(np.where((per>=lo)&(per<=hi),F,0.0),n=n)
def analytic(x):
    n=len(x); Xf=np.fft.fft(x); h=np.zeros(n)
    if n%2==0: h[0]=h[n//2]=1; h[1:n//2]=2
    else: h[0]=1; h[1:(n+1)//2]=2
    return np.fft.ifft(Xf*h)
def dom_period(x, lo=18, hi=200):
    x=x-x.mean(); n=len(x); f=rfftfreq(n,d=1.0); P=np.abs(rfft(x))**2
    per=np.where(f>0,1.0/np.maximum(f,1e-9),np.inf)
    m=(per>=lo)&(per<=hi); idx=np.where(m)[0]
    return per[idx[np.argmax(P[idx])]]
def xcorr_lead(a,b,maxlag=24):
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std(); n=len(a); out=[]
    for L in range(-maxlag,maxlag+1):
        if L>=0: x=a[:n-L]; y=b[L:]
        else:    x=a[-L:];  y=b[:n+L]
        out.append((L,float(np.mean(x*y))))
    return max(out,key=lambda t:abs(t[1]))

EDGE=24
def phase_pair(name, a, b, lo, hi):
    ab=bandpass_fft(a,lo,hi)[EDGE:-EDGE]; bb=bandpass_fft(b,lo,hi)[EDGE:-EDGE]
    dphi=np.angle(analytic(ab))-np.angle(analytic(bb))
    plv=np.abs(np.mean(np.exp(1j*dphi)))
    off=np.degrees(np.angle(np.mean(np.exp(1j*dphi))))
    L,c=xcorr_lead(ab,bb)
    kind=("in-phase/locked" if abs(off)<45 else "COUNTERSPIN/anti-phase" if abs(off)>135 else "quadrature")
    print(f"   {name:26s} band {lo}-{hi}mo : PLV {plv:.2f}  offset {off:+4.0f}deg  ({kind})  peak corr {c:+.2f} @ lag {L:+d}")
    return off,c,L

def main():
    nino=load_nino("nino34_long_anom.csv"); wwv=load_wwv("wwv_west.dat")
    pdo=load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")
    keys=sorted(set(nino)&set(wwv)&set(pdo))
    T=np.array([nino[k] for k in keys]); W=np.array([wwv[k] for k in keys]); P=np.array([pdo[k] for k in keys])
    print(f"WWV/NINO/PDO overlap: {len(keys)} mo  {keys[0]}..{keys[-1]}\n")

    print("== 1. OCTAVE LADDER  (dominant interannual periods) ==")
    pw=dom_period(W); pn=dom_period(T); pp=dom_period(P)
    print(f"   WWV (below) {pw:5.1f} mo   NINO (us) {pn:5.1f} mo   PDO (above) {pp:5.1f} mo")
    print(f"   ratios: NINO/WWV {pn/pw:.2f}   PDO/NINO {pp/pn:.2f}   PDO/WWV {pp/pw:.2f}   (x2 = octave)\n")

    print("== 2. PHASE GEOMETRY  (the rotation's fingerprint) ==")
    print("   UP-link (should be in-phase/locked):")
    phase_pair("ENSO <-> PDO (above)", T, P, 40, 70)
    print("   DOWN-link (should be counterspin):")
    phase_pair("ENSO <-> WWV (below)", T, W, 40, 70)
    phase_pair("ENSO <-> WWV (below)", T, W, 24, 33)
    print()

    print("== 3. RETURN  (warm water charged below should LEAD ENSO back up) ==")
    for lo,hi,nm in [(40,70,'brown'),(24,33,'green')]:
        wb=bandpass_fft(W,lo,hi)[EDGE:-EDGE]; tb=bandpass_fft(T,lo,hi)[EDGE:-EDGE]
        L,c=xcorr_lead(wb,tb)
        lead = "WWV LEADS ENSO" if L<0 else ("ENSO leads WWV" if L>0 else "in step")
        print(f"   {nm} band: peak corr {c:+.2f} at lag {L:+d} mo  -> {lead}")
    print("\nReal NOAA/PMEL indices. Descriptive diagnostic (zero-phase bands). Not a forecast claim.")

if __name__=="__main__": main()
