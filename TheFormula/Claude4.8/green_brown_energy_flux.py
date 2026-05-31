"""
Green/Brown vs ENSO ENERGY FLUX  (is warm water flowing IN or OUT?)
==================================================================
Fixes the self-reference flaw: instead of comparing two filtered slices of NINO to each
other, we compare each band to an INDEPENDENT energy variable -- the warm-water battery
FLOW RATE (dWWV/dt). That flow IS energy crossing the ENSO boundary:
   flux > 0  = warm water pouring IN   (recharge / charging)
   flux < 0  = warm water draining OUT (discharge / the drain)

Dylan's model to test:
   green (our up-flow)        -> should sit on the INFLOW  (system charging)
   brown (above's down-flow)  -> should sit on the OUTFLOW (the leaf-fall draining)

For each band we report, at the band's WARM peak:
   * correlation of the band's SST rhythm with the energy flux (+ best lead/lag)
   * the phase offset (degrees) between SST band and flux
   * mean flux during the band's warm half vs cool half  (in vs out)

Data: NOAA NINO 3.4 (SST) + PMEL WWV (heat battery). Independent variables. Real.
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
def xcorr_lead(a,b,maxlag=18):
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std(); n=len(a); out=[]
    for L in range(-maxlag,maxlag+1):
        if L>=0: x=a[:n-L]; y=b[L:]
        else:    x=a[-L:];  y=b[:n+L]
        out.append((L, float(np.mean(x*y))))
    return max(out, key=lambda t:abs(t[1]))

def band_report(name, sst_band, flux, flux_band):
    # SST band warm half = band > 0 ; ask: is the system charging (flux>0) then?
    warm = sst_band > 0
    f_in_warm  = flux[warm].mean()
    f_in_cool  = flux[~warm].mean()
    L,c = xcorr_lead(sst_band, flux, maxlag=18)
    # phase offset between SST band and the flux at the same band speed
    ph_sst = np.angle(analytic(sst_band)); ph_flx = np.angle(analytic(flux_band))
    dphi = np.angle(np.exp(1j*(ph_flx - ph_sst))).mean()  # circular mean offset
    deg = np.degrees(dphi)
    print(f"-- {name} band --")
    print(f"   mean flux during WARM half : {f_in_warm:+.4f}   (>0 = charging while warm)")
    print(f"   mean flux during COOL half : {f_in_cool:+.4f}")
    print(f"   corr(SST band, flux) peak  : {c:+.3f} at lag {L:+d} mo")
    print(f"   flux leads SST by          : {deg:+.0f} deg   (+90 = classic recharge, flux precedes warming)")
    verdict = "INFLOW-led (charging drives this band)" if f_in_warm>f_in_cool else "OUTFLOW-led (draining drives this band)"
    print(f"   -> {verdict}\n")
    return f_in_warm, f_in_cool, deg

def main():
    nino=load_nino("nino34_long_anom.csv"); wwv=load_wwv("wwv_west.dat")
    nk=sorted(nino); T=np.array([nino[k] for k in nk]); nidx={k:i for i,k in enumerate(nk)}
    green=bandpass_fft(T,24,33); brown=bandpass_fft(T,40,70)

    keys=[k for k in sorted(wwv) if k in nidx]; keys=keys[6:len(keys)-6]
    W=np.array([wwv[k] for k in keys])
    flux=np.gradient(W)                      # warm-water FLOW RATE = energy crossing boundary
    gb=np.array([green[nidx[k]] for k in keys]); bb=np.array([brown[nidx[k]] for k in keys])
    flux_g=bandpass_fft(flux,24,33); flux_b=bandpass_fft(flux,40,70)
    print(f"WWV overlap: {len(keys)} mo  {keys[0]}..{keys[-1]}")
    print("flux = monthly change in warm-water volume (>0 IN / charging, <0 OUT / draining)\n")

    gw,gc,gdeg = band_report("GREEN (our up-flow?)",   gb, flux, flux_g)
    bw,bc,bdeg = band_report("BROWN (above down-flow?)", bb, flux, flux_b)

    print("== READING ==")
    if gw>gc and bw<bc:
        print("Green rides the INFLOW, brown rides the OUTFLOW -> the up/down split is REAL")
        print("as actual energy crossing the ENSO boundary.")
    elif gw>gc and bw>bc:
        print("BOTH bands ride the inflow -> both charge with the system; no clean up/down split.")
    elif gw<gc and bw<bc:
        print("BOTH bands ride the outflow -> both drain; no clean up/down split.")
    else:
        print("Green rides OUTFLOW and brown rides INFLOW -> OPPOSITE of the model.")
    print("\nSST bands vs an INDEPENDENT heat-flux variable. Descriptive diagnostic.")

if __name__=="__main__": main()
