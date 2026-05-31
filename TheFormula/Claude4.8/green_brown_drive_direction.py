"""
Green/Brown drive-direction test  (gravity-from-above vs matched-rung hum)
==========================================================================
Dylan's model: brown = the heavier system OVERHEAD. If brown truly pulls energy DOWN,
it should leave a ONE-WAY fingerprint: brown's past should forecast green's future
better than green's past forecasts brown's future. A real pull is asymmetric.
If green/brown are just two bands humming at matched speeds, the drive is SYMMETRIC.

Measure (Granger-style, on the band ENERGY = envelopes):
  drive(brown->green) = how much knowing brown's recent past shrinks the error in
                        predicting green's next step, beyond green's own past.
  drive(green->brown) = the mirror.
Asymmetry = brown->green minus green->brown.  Positive => energy drives DOWN (gravity).

Honesty: descriptive diagnostic on the full record (not a forecast claim). Bands built
zero-phase. Phase-scramble null included so we know what "no real drive" looks like.
Data: NOAA NINO 3.4. Real.
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

def granger_reduction(target, source, L=12):
    """Fraction of target's 1-step error variance removed by adding source's past
       (lags 1..L), beyond target's own past. Returns reduction in [0,1)."""
    t=(target-target.mean())/target.std(); s=(source-source.mean())/source.std()
    n=len(t)
    rows_y=[]; X_self=[]; X_full=[]
    for i in range(L, n):
        y=t[i]
        self_lags=[t[i-k] for k in range(1,L+1)]
        src_lags =[s[i-k] for k in range(1,L+1)]
        rows_y.append(y); X_self.append(self_lags); X_full.append(self_lags+src_lags)
    y=np.array(rows_y); Xs=np.array(X_self); Xf=np.array(X_full)
    Xs=np.column_stack([Xs,np.ones(len(y))]); Xf=np.column_stack([Xf,np.ones(len(y))])
    bs=np.linalg.lstsq(Xs,y,rcond=None)[0]; bf=np.linalg.lstsq(Xf,y,rcond=None)[0]
    rss_self=np.sum((y-Xs@bs)**2); rss_full=np.sum((y-Xf@bf)**2)
    return 1.0 - rss_full/rss_self

def phase_scramble(x, rng):
    n=len(x); F=np.fft.rfft(x-x.mean())
    ph=rng.uniform(0,2*np.pi,len(F)); ph[0]=0
    if n%2==0: ph[-1]=0
    return np.fft.irfft(np.abs(F)*np.exp(1j*ph), n=n)

EDGE=60
def main():
    nino=load_nino("nino34_long_anom.csv")
    keys=sorted(nino); T=np.array([nino[k] for k in keys])
    green=bandpass_fft(T,24,33); brown=bandpass_fft(T,40,70)
    ge=envelope(green); be=envelope(brown)
    sl=slice(EDGE,len(T)-EDGE)
    ge=ge[sl]; be=be[sl]
    print(f"NINO 3.4 record, {len(ge)} mo used (edges trimmed {EDGE}).\n")

    L=12
    bg=granger_reduction(ge, be, L)   # brown -> green  (downward drive)
    gb=granger_reduction(be, ge, L)   # green -> brown  (upward drive)
    asym=bg-gb
    print("== DRIVE DIRECTION  (energy = band envelope, lags 1..12 mo) ==")
    print(f"   brown -> green  (DOWN-drive) : {bg:+.3f}")
    print(f"   green -> brown  (UP-drive)   : {gb:+.3f}")
    print(f"   asymmetry (down - up)        : {asym:+.3f}\n")

    # null: what asymmetry do we see when there is NO real cross-drive?
    rng=np.random.default_rng(11); nulls=[]
    for _ in range(300):
        gs=envelope(phase_scramble(green,rng))[ :len(ge)] if False else None
        gn=phase_scramble(ge,rng); bn=phase_scramble(be,rng)
        nulls.append(granger_reduction(gn,bn,L)-granger_reduction(bn,gn,L))
    nulls=np.array(nulls); mu=nulls.mean(); sd=nulls.std()
    z=(asym-mu)/sd if sd>0 else 0
    print("== NULL (phase-scrambled, no real coupling) ==")
    print(f"   null asymmetry mean {mu:+.3f}  sd {sd:.3f}")
    print(f"   observed asymmetry z = {z:+.2f}")
    if z>2 and asym>0:
        print("   -> brown DRIVES green one-way: energy pulled DOWN from above (gravity).")
    elif z<-2 and asym<0:
        print("   -> green drives brown one-way: energy pushed UP from our system.")
    else:
        print("   -> no clean one-way drive: looks like matched-rung hum, not a pull.")
    print("\nDescriptive diagnostic; bands zero-phase. Not a forecast claim.")

if __name__=="__main__": main()
