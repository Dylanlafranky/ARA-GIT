"""
Do the two tiers actually TALK?  (energy below feeds memory above -- or just d/dt artifact?)
===========================================================================================
The flux%/level% tilt is partly guaranteed: d/dt boosts fast, integration boosts slow. So the
"gradient" could be a trivial derivative artifact. The REAL Information^3 claim is that the
two tiers COUPLE: fast ENERGY (flux, datum tier) feeds UP into slow MEMORY (level, meaning
tier). If true: their envelopes correlate AND energy leads. If they don't correlate, the
handover is just math.

Test (one system, WWV battery):
   fast-energy  = envelope of FLUX in a fast band (below the ~25mo crossover)
   slow-memory  = envelope of LEVEL in a slow band (above the crossover)
   cross-correlate, find lead/lag, and a PHASE-SCRAMBLE null (z-score) so we know it's real.

Prediction: positive corr, fast energy LEADS slow memory (charging the clock).
Data: PMEL WWV warm-water volume. Real. Descriptive diagnostic.
"""
import numpy as np
from numpy.fft import rfft, irfft, rfftfreq

def load_wwv(p):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==3 and s[0].isdigit() and len(s[0])==6: d[s[0]]=float(s[2])/1e14
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
def env(x): return np.abs(analytic(x-x.mean()))
def xcorr_lead(a,b,maxlag=36):
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std(); n=len(a); out=[]
    for L in range(-maxlag,maxlag+1):
        if L>=0: x=a[:n-L]; y=b[L:]
        else:    x=a[-L:];  y=b[:n+L]
        out.append((L,float(np.mean(x*y))))
    return max(out,key=lambda t:abs(t[1])), out
def phase_scramble(x,rng):
    n=len(x); F=rfft(x-x.mean()); mag=np.abs(F)
    ph=np.angle(F); ph[1:]=rng.uniform(-np.pi,np.pi,len(ph)-1)
    return irfft(mag*np.exp(1j*ph), n=n)

EDGE=24
def main():
    wwv=load_wwv("wwv_west.dat"); wk=sorted(wwv)
    W=np.array([wwv[k] for k in wk]); flux=np.gradient(W)
    print(f"WWV battery: {len(wk)} mo  {wk[0]}..{wk[-1]}  (crossover from tier_gradient ~25mo)\n")

    # tiers, defined cleanly either side of the 25mo handover
    fast_e = env(bandpass_fft(flux, 6, 20))[EDGE:-EDGE]    # energy below
    slow_m = env(bandpass_fft(W,    40, 70))[EDGE:-EDGE]    # memory above
    (L,c),_ = xcorr_lead(fast_e, slow_m, maxlag=36)
    who = "ENERGY leads MEMORY (charges the clock)" if L<0 else \
          ("MEMORY leads ENERGY (clock gates the fuel)" if L>0 else "in step")
    print("== CROSS-TIER COUPLING: fast energy  <->  slow memory ==")
    print(f"   peak corr {c:+.2f} at lag {L:+d} mo  ->  {who}")

    # phase-scramble null: break coupling, keep each spectrum
    rng=np.random.default_rng(7); nz=[]
    for _ in range(400):
        fe=env(bandpass_fft(phase_scramble(flux,rng),6,20))[EDGE:-EDGE]
        (Ln,cn),_=xcorr_lead(fe, slow_m, maxlag=36); nz.append(abs(cn))
    nz=np.array(nz); z=(abs(c)-nz.mean())/nz.std()
    print(f"   null |corr| {nz.mean():.2f}+/-{nz.std():.2f}   ->  z = {z:+.1f}  "
          f"({'REAL coupling' if z>2 else 'not above chance'})\n")

    # same-rung sanity: at the crossover band, flux vs level should be ~quarter cycle (derivative)
    fb=bandpass_fft(flux,18,33)[EDGE:-EDGE]; lb=bandpass_fft(W,18,33)[EDGE:-EDGE]
    dphi=np.degrees(np.angle(np.mean(np.exp(1j*(np.angle(analytic(fb))-np.angle(analytic(lb)))))))
    print(f"   sanity (same 18-33mo rung): flux vs level phase offset {dphi:+.0f} deg "
          f"(~+90 = pure derivative, recharge geometry)\n")
    print("Real PMEL WWV. If z>2 the tiers genuinely couple (not a d/dt artifact). Descriptive.")

if __name__=="__main__": main()
