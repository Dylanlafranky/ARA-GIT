"""
Green up-flow / Brown E-event (leaf-fall) diagnostic
====================================================
Dylan's two-flows picture for ENSO, made measurable:

  * GREEN band (quasi-biennial ~24-33 mo) = energy from OUR system going UP a rung
    (promotion / up-flow). If true, green energy should LEAD the brown band -- the
    faster rung pumping the slower one above it.
  * BROWN band (low-freq ~40-70 mo) = the reservoir above. It occasionally SHEDS a
    "leaf" back DOWN -- a sharp discharge = an E-event (disruption). Those sheds should
    land on the green band as a spike (the leaf hitting the forest floor).

DIAGNOSTIC of structure (zero-phase bandpass to isolate bands -- description, NOT a
forecast claim). Data: NOAA NINO 3.4. Real.
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
    """Zero-phase band isolation in period-months [lo,hi]. Diagnostic only."""
    x=x-x.mean(); n=len(x)
    f=rfftfreq(n, d=1.0)
    F=rfft(x)
    per=np.where(f>0, 1.0/np.maximum(f,1e-9), np.inf)
    keep=(per>=lo_mo)&(per<=hi_mo)
    F2=np.where(keep, F, 0.0)
    return irfft(F2, n=n)

def envelope(x):
    """Analytic-signal amplitude envelope via FFT Hilbert."""
    n=len(x); Xf=np.fft.fft(x)
    h=np.zeros(n)
    if n%2==0:
        h[0]=h[n//2]=1; h[1:n//2]=2
    else:
        h[0]=1; h[1:(n+1)//2]=2
    z=np.fft.ifft(Xf*h)
    return np.abs(z)

def xcorr_lead(a,b,maxlag=18):
    """corr(a, b shifted) over lags; positive lag = a leads b."""
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std(); n=len(a)
    out=[]
    for L in range(-maxlag,maxlag+1):
        if L>=0: x=a[:n-L]; y=b[L:]
        else:    x=a[-L:];  y=b[:n+L]
        out.append((L, float(np.mean(x*y))))
    best=max(out, key=lambda t:t[1])
    return best, out

EDGE=60   # drop FFT bandpass edge artifacts (months) at each end

def find_sheds(be, keys, min_sep=24, topn=12):
    """Big brown leaf-falls = most negative d(envelope)/dt, well separated."""
    dbe=np.gradient(be)
    order=np.argsort(dbe)
    picked=[]
    for k in order:
        if dbe[k]>=0: break
        if all(abs(k-p)>=min_sep for p in picked):
            picked.append(k)
        if len(picked)>=topn: break
    return sorted(picked), dbe

def main():
    nino=load_nino("nino34_long_anom.csv")
    keys=sorted(nino); T=np.array([nino[k] for k in keys])
    print(f"NINO 3.4: {len(keys)} mo  {keys[0]}..{keys[-1]}  (trimming {EDGE}mo edges)\n")

    green=bandpass_fft(T,24,33); brown=bandpass_fft(T,40,70)
    ge=envelope(green); be=envelope(brown)
    sl=slice(EDGE,len(T)-EDGE)
    keys=keys[EDGE:len(T)-EDGE]; T=T[sl]; green=green[sl]; brown=brown[sl]; ge=ge[sl]; be=be[sl]

    # 1. green <-> brown lead/lag
    (Lg,cg),curve=xcorr_lead(ge,be,maxlag=24)
    print("== 1. GREEN <-> BROWN envelope lead/lag  (+lag = GREEN leads = up-flow) ==")
    print("   lag(mo): " + " ".join(f"{L:>5d}" for L,_ in curve[::6]))
    print("   corr   : " + " ".join(f"{c:>+5.2f}" for _,c in curve[::6]))
    direction = ("GREEN leads BROWN -> energy going UP a rung (up-flow)" if Lg>0
                 else "BROWN leads GREEN -> reservoir sheds DOWN (down-flow)")
    print(f"   peak {cg:+.3f} at lag {Lg:+d} mo  ->  {direction}\n")

    # 2. big brown E-events (leaf-falls)
    events,dbe=find_sheds(be, keys, min_sep=24, topn=12)
    big_enso={1877,1888,1896,1902,1905,1911,1918,1925,1932,1940,1941,1957,1965,1972,
              1982,1983,1987,1991,1997,1998,2009,2015,2016,2023}
    print("== 2. BIG BROWN E-EVENTS  (the reservoir discharging fastest = leaf-falls) ==")
    for k in events:
        yr=int(keys[k][:4]); near=min(abs(yr-e) for e in big_enso)
        tag=f"near big ENSO ({yr if near==0 else f'+/-{near}yr'})" if near<=1 else ""
        print(f"   {keys[k][:4]}-{keys[k][4:6]}   shed {dbe[k]:+.3f}/mo   brown {brown[k]:+.2f}   {tag}")
    print()

    # 3. does a brown shed land as a green spike?
    print("== 3. DOES A BROWN SHED LAND AS A GREEN SPIKE?  (leaf hits the forest floor) ==")
    win=12
    resp=[]
    for k in events:
        if k-6>=0 and k+win<len(ge):
            before=ge[k-6:k+1].mean(); after=ge[k+1:k+1+win].max()
            resp.append(after-before)
    if resp:
        rng=np.random.default_rng(7); nullresp=[]
        cand=[i for i in range(6,len(ge)-win) if all(abs(i-k)>24 for k in events)]
        for i in rng.choice(cand, size=min(2000,len(cand)), replace=False):
            nullresp.append(ge[i+1:i+1+win].max() - ge[i-6:i+1].mean())
        m=np.mean(resp); mn=np.mean(nullresp); sd=np.std(nullresp)
        z=(m-mn)/(sd/np.sqrt(len(resp))) if sd>0 else 0
        print(f"   mean GREEN rise in 12mo after a brown shed : {m:+.3f}")
        print(f"   mean GREEN rise after a random month       : {mn:+.3f}")
        verdict = ('green spikes after the leaf-fall -> down-flow lands on green' if z>2
                   else 'no clear green spike after the shed')
        print(f"   z = {z:+.2f}  ({verdict})")
    print("\nGreen vs Brown are the two flows. Diagnostic bandpass (zero-phase), structure only.")

if __name__=="__main__": main()
