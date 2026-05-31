"""
ENSO <-> Above-ENSO (PDO): green = up-pipe, brown = shared clock
================================================================
Dylan's refined model:
  * GREEN band = ENSO's OUTPUT going UP to the system above it.   -> ENSO should LEAD PDO.
  * BROWN/GOLD band = the SHARED CLOCK / snap between ENSO and the system above.
        -> a shared gear ticks in BOTH at once: high phase-lock, ~ZERO lag (synchronous).

Discriminator:
  - If brown is the shared clock, NINO-brown and PDO-brown are phase-LOCKED near zero lag.
  - If green is ENSO passing energy UP, NINO-green LEADS PDO-green (ENSO first, PDO answers).
  - If brown were just another energy band (old framing) it would behave like green, not lock.

PLV = phase-locking value |<exp i(phase_NINO - phase_PDO)>| in [0,1]; 1 = perfectly locked.
mean phase offset (deg): >0 = NINO leads PDO.

Data: NOAA NINO 3.4 + NOAA ERSST v5 PDO. Real, independent indices. Descriptive diagnostic.
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

def bandpass_fft(x, lo_mo, hi_mo):
    x=x-x.mean(); n=len(x)
    f=rfftfreq(n, d=1.0); F=rfft(x)
    per=np.where(f>0, 1.0/np.maximum(f,1e-9), np.inf)
    keep=(per>=lo_mo)&(per<=hi_mo)
    return irfft(np.where(keep,F,0.0), n=n)
def analytic(x):
    n=len(x); Xf=np.fft.fft(x); h=np.zeros(n)
    if n%2==0: h[0]=h[n//2]=1; h[1:n//2]=2
    else: h[0]=1; h[1:(n+1)//2]=2
    return np.fft.ifft(Xf*h)
def xcorr_lead(a,b,maxlag=24):
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std(); n=len(a); out=[]
    for L in range(-maxlag,maxlag+1):
        if L>=0: x=a[:n-L]; y=b[L:]
        else:    x=a[-L:];  y=b[:n+L]
        out.append((L, float(np.mean(x*y))))
    return max(out, key=lambda t:abs(t[1])), out

EDGE=60
def band_pair(name, ni, pd, lo, hi):
    nb=bandpass_fft(ni,lo,hi); pb=bandpass_fft(pd,lo,hi)
    nb=nb[EDGE:len(nb)-EDGE]; pb=pb[EDGE:len(pb)-EDGE]
    phn=np.angle(analytic(nb)); php=np.angle(analytic(pb))
    dphi=phn-php
    plv=np.abs(np.mean(np.exp(1j*dphi)))
    offset=np.degrees(np.angle(np.mean(np.exp(1j*dphi))))   # >0 NINO leads
    (L,c),_=xcorr_lead(nb,pb,maxlag=24)
    print(f"-- {name} band ({lo}-{hi} mo) --")
    print(f"   phase-lock PLV (NINO vs PDO) : {plv:.3f}   (1=locked together)")
    print(f"   mean phase offset            : {offset:+.0f} deg   (>0 = NINO leads PDO)")
    print(f"   peak band corr               : {c:+.3f} at lag {L:+d} mo")
    return plv, offset, L, c

def main():
    nino=load_nino("nino34_long_anom.csv")
    pdo =load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")
    keys=sorted(set(nino)&set(pdo))
    ni=np.array([nino[k] for k in keys]); pd=np.array([pdo[k] for k in keys])
    print(f"NINO & PDO overlap: {len(keys)} mo  {keys[0]}..{keys[-1]}  (edges trimmed {EDGE})\n")

    gP,gO,gL,gC = band_pair("GREEN (ENSO up-pipe?)", ni, pd, 24, 33)
    print()
    bP,bO,bL,bC = band_pair("BROWN (shared clock?)", ni, pd, 40, 70)
    print()

    print("== READING ==")
    clock_like  = (bP > gP + 0.05) and (abs(bL) <= abs(gL))
    green_leads = gL > 1
    if clock_like:
        print(f"BROWN locks tighter ({bP:.2f} vs green {gP:.2f}) and near its lag -> behaves like a SHARED CLOCK.")
    else:
        print(f"BROWN does NOT lock tighter than green ({bP:.2f} vs {gP:.2f}) -> not obviously a shared clock.")
    if green_leads:
        print(f"GREEN: NINO leads PDO by {gL:+d} mo, offset {gO:+.0f} deg -> ENSO feeding UP into PDO.")
    else:
        print(f"GREEN: NINO does not clearly lead PDO (lag {gL:+d} mo) -> up-feed not seen.")
    print("\nTwo independent NOAA indices. Descriptive diagnostic, not a forecast claim.")

if __name__=="__main__": main()
