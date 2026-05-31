"""
Green/Brown <-> WWV battery coupling test
=========================================
Dylan's model: green and brown are each their OWN system (ARA self-similar). What we
measure here is not ownership but how strongly OUR battery (WWV warm-water charge)
TOUCHES each band -- from our system's perspective.

  * GREEN band (24-33 mo) = our system's UP-flow. Should be COUPLED to our WWV battery.
  * BROWN band (40-70 mo) = the above system's DOWN-flow (leaf-fall). Should be LOOSE /
    aloof from our WWV battery -- it falls in from outside.

Test: envelope of each NINO band vs envelope of WWV. Bands built on full NINO record
(good freq resolution), then sliced to the WWV overlap window. Diagnostic only.
Data: NOAA NINO 3.4 + PMEL WWV. Real.
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

def envelope(x):
    n=len(x); Xf=np.fft.fft(x); h=np.zeros(n)
    if n%2==0: h[0]=h[n//2]=1; h[1:n//2]=2
    else: h[0]=1; h[1:(n+1)//2]=2
    return np.abs(np.fft.ifft(Xf*h))

def xcorr_lead(a,b,maxlag=18):
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std(); n=len(a); out=[]
    for L in range(-maxlag,maxlag+1):
        if L>=0: x=a[:n-L]; y=b[L:]
        else:    x=a[-L:];  y=b[:n+L]
        out.append((L, float(np.mean(x*y))))
    best=max(out, key=lambda t:abs(t[1]))
    return best, out

def main():
    nino=load_nino("nino34_long_anom.csv")
    wwv =load_wwv("wwv_west.dat")
    nk=sorted(nino); T=np.array([nino[k] for k in nk])

    # bands on full NINO record for resolution
    green=bandpass_fft(T,24,33); brown=bandpass_fft(T,40,70)
    ge=envelope(green); be=envelope(brown)
    nidx={k:i for i,k in enumerate(nk)}

    # align to WWV window
    keys=[k for k in sorted(wwv) if k in nidx]
    keys=keys[6:len(keys)-6]            # small edge trim on the overlap window
    ig=np.array([ge[nidx[k]] for k in keys])
    ib=np.array([be[nidx[k]] for k in keys])
    W =np.array([wwv[k] for k in keys])
    we=envelope(W - W.mean())           # battery activity envelope
    print(f"WWV overlap: {len(keys)} mo  {keys[0]}..{keys[-1]}\n")

    (Lg,cg),cvg=xcorr_lead(ig,we,maxlag=18)
    (Lb,cb),cvb=xcorr_lead(ib,we,maxlag=18)
    z0g=dict(cvg)[0]; z0b=dict(cvb)[0]
    print("== HOW STRONGLY DOES OUR WWV BATTERY TOUCH EACH BAND? ==")
    print(f"   GREEN env <-> WWV env : peak {cg:+.3f} at lag {Lg:+d} mo   (lag0 {z0g:+.3f})")
    print(f"   BROWN env <-> WWV env : peak {cb:+.3f} at lag {Lb:+d} mo   (lag0 {z0b:+.3f})\n")

    # also: raw band signal vs WWV bandpassed to the same band (does the battery itself
    # carry the green rhythm but not the brown?)
    Wg=bandpass_fft(W,24,33); Wb=bandpass_fft(W,40,70)
    g_raw=np.array([green[nidx[k]] for k in keys]); b_raw=np.array([brown[nidx[k]] for k in keys])
    def c(a,b): a=a-a.mean(); b=b-b.mean(); return float((a*b).sum()/np.sqrt((a*a).sum()*(b*b).sum()))
    print("== DOES THE BATTERY ITSELF CARRY EACH RHYTHM? (band signal corr) ==")
    print(f"   NINO green  <-> WWV green  : {c(g_raw,Wg):+.3f}")
    print(f"   NINO brown  <-> WWV brown  : {c(b_raw,Wb):+.3f}\n")

    g_touch=abs(cg); b_touch=abs(cb)
    if g_touch > b_touch + 0.08:
        print(f"-> GREEN touches our battery MORE ({g_touch:.2f} vs {b_touch:.2f}).")
        print("   Consistent with: green = OUR up-flow, brown = the above system falling in.")
    elif b_touch > g_touch + 0.08:
        print(f"-> BROWN touches our battery more ({b_touch:.2f} vs {g_touch:.2f}). Against the model.")
    else:
        print(f"-> Both touch our battery about equally ({g_touch:.2f} vs {b_touch:.2f}). No clean split.")
    print("\nGreen/brown are each their own system; this is only how OUR battery touches them.")

if __name__=="__main__": main()
