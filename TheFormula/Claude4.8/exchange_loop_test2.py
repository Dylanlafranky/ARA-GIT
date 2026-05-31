"""
EXCHANGE-CHANNEL CLOSURE v2 -- corrected method.
Flaw in v1: pre-isolating a narrow band removes the target rung r3=P*phi^2, so the
mix test was rigged to fail. Here the mix runs on the FULL signal with r1,r2 set to
the EMPIRICAL gold & brown centers (not phi-derived), and r3 = the rung above brown.
Tests Dylan's actual claim: GOLD x BROWN (two adjacent rungs) -> build the rung above;
and the BEAT between them = the ENSO recurrence (the 'exchange').
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt, correlate, correlation_lags
PHI = (1 + 5 ** 0.5) / 2
rng = np.random.default_rng(7)
GOLD = 29.3; BROWN = 54.5  # empirical band centers (mo)

def load_nino(path):
    vs = []
    for ln in open(path):
        ln = ln.strip()
        if not ln or ln[0].isalpha(): continue
        p = ln.replace(",", " ").split()
        try: v = float(p[-1])
        except ValueError: continue
        if v <= -99: continue
        vs.append(v)
    return np.array(vs)

def bp(x, period, ratio=1.3):
    ny = 0.5
    lo = 1.0/(period*ratio); hi = 1.0/(period/ratio)
    lo, hi = max(lo,1e-6), min(hi, ny*0.99)
    sos = butter(3,[lo/ny,hi/ny],btype="band",output="sos")
    return sosfiltfilt(sos, x)

def phase_rand(x):
    X = np.fft.rfft(x); ph = rng.uniform(0,2*np.pi,len(X)); ph[0]=0
    if len(x)%2==0: ph[-1]=0
    return np.fft.irfft(np.abs(X)*np.exp(1j*ph), n=len(x))

def pcl(a,b,maxlag):
    a=(a-a.mean())/(a.std()+1e-12); b=(b-b.mean())/(b.std()+1e-12)
    c=correlate(a,b,mode="full")/len(a); lags=correlation_lags(len(a),len(b),mode="full")
    m=np.abs(lags)<=maxlag; c,lags=c[m],lags[m]; k=np.argmax(c)
    return c[k],lags[k]

def mix_build(x, r1, r2, r3, nn=60):
    """Does x's rung at r3 get built by the product of its rungs at r1 and r2?"""
    gen = bp(bp(x,r1)*bp(x,r2), r3); ac = bp(x,r3)
    maxlag=int(r3)
    recon,lag = pcl(gen,ac,maxlag)
    null=[]
    for _ in range(nn):
        xs=phase_rand(x); g=bp(bp(xs,r1)*bp(xs,r2),r3); a=bp(xs,r3)
        null.append(pcl(g,a,maxlag)[0])
    null=np.array(null); z=(recon-null.mean())/(null.std()+1e-12)
    return recon,z,float(lag)/r3

def main():
    x = load_nino("nino34_long_anom.csv")
    print(f"NINO3.4 N={len(x)} ({len(x)/12:.0f}yr)  GOLD={GOLD}mo BROWN={BROWN}mo  ratio={BROWN/GOLD:.3f} (phi={PHI:.3f})\n")

    beat = 1/abs(1/GOLD - 1/BROWN); summ = 1/(1/GOLD + 1/BROWN)
    print(f"Gold<->Brown beat (difference tone) = {beat:.1f} mo  | sum tone = {summ:.1f} mo")
    print(f"Classic ENSO recurrence ~ 40-60 mo.  rung above Brown (xphi) = {BROWN*PHI:.1f} mo\n")

    print("=== Mix-build test on FULL NINO3.4 (r1=gold, r2=brown -> r3) ===")
    print(f"{'target r3 (mo)':>16} {'what it is':>22} {'recon':>7} {'z':>6} {'lag':>6}  verdict")
    targets = [(BROWN*PHI, "Brown x phi"), (BROWN*BROWN/GOLD, "continue ratio"),
               (beat, "Gold/Brown beat"), (GOLD*PHI**2, "Gold x phi^2")]
    for r3, lab in targets:
        recon,z,lag = mix_build(x, GOLD, BROWN, r3)
        v = "PASS" if z>=2 else "fail"
        print(f"{r3:>16.1f} {lab:>22} {recon:>+7.2f} {z:>+6.1f} {lag:>+6.2f}  {v}")

    print("\n=== Is the beat (exchange) the ENSO main band? ===")
    enso_main = bp(x, 48, ratio=1.6)        # broad 30-77mo ENSO band
    gb = bp(x,GOLD)*bp(x,BROWN)
    cc,lag = pcl(bp(gb,beat), enso_main, maxlag=int(beat))
    print(f"corr( Gold*Brown beat@{beat:.0f}mo , ENSO main band ) = {cc:+.2f} at lag {lag} mo")
    cb,_ = pcl(bp(x,BROWN), bp(x,GOLD), maxlag=int(BROWN))
    print(f"corr( Brown band , Gold band ) = {cb:+.2f}  ({'anti-phase' if cb<-0.2 else 'in-phase' if cb>0.2 else 'weak'})")

if __name__=="__main__":
    main()
