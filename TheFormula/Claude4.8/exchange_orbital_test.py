"""
CROSS-DOMAIN EXCHANGE-CHANNEL TEST (task #96) -- REAL JPL DE441, 7000 yr.
Endpoints = Jupiter & Saturn semi-major axis a(t) via vis-viva (carries the
perturbation structure; raw Lz is conserved/flat so it can't build rungs).
Exchange  = the anti-phase great-inequality (~883yr) mode they trade.
Predictions fixed BEFORE z: J a(t) PASS, S a(t) PASS, EXCHANGE FAIL, J<->S anti-phase.
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt, correlate, correlation_lags
PHI=(1+5**0.5)/2; rng=np.random.default_rng(11); YR=365.25
MU=0.0002959122  # GM_sun, AU^3/day^2
dt=60.0

def load(n):
    d=np.load(f"/tmp/orb/{n}.npz")
    r=np.hypot(d["X"],d["Y"]); v2=d["VX"]**2+d["VY"]**2
    a=1.0/(2.0/r - v2/MU)             # vis-viva instantaneous semi-major axis
    Lz=d["X"]*d["VY"]-d["Y"]*d["VX"]
    return d["jd"],a,r,Lz

def bp(x,P,ratio=1.3):
    ny=0.5; lo=1/(P*ratio); hi=1/(P/ratio); lo,hi=max(lo,1e-6),min(hi,ny*0.99)
    return sosfiltfilt(butter(3,[lo/ny,hi/ny],btype="band",output="sos"),x)
def phase_rand(x):
    X=np.fft.rfft(x); ph=rng.uniform(0,2*np.pi,len(X)); ph[0]=0
    if len(x)%2==0: ph[-1]=0
    return np.fft.irfft(np.abs(X)*np.exp(1j*ph),n=len(x))
def pcl(a,b,ml):
    a=(a-a.mean())/(a.std()+1e-12); b=(b-b.mean())/(b.std()+1e-12)
    c=correlate(a,b,mode="full")/len(a); lg=correlation_lags(len(a),len(b),mode="full")
    m=np.abs(lg)<=ml; c,lg=c[m],lg[m]; k=np.argmax(c); return c[k],lg[k]
def mix_test(x,P,nn=50):
    r1,r2,r3=P,P*PHI,P*PHI**2
    if len(x)<6*r3: return None
    gen=bp(bp(x,r1)*bp(x,r2),r3); ac=bp(x,r3); ml=int(r3)
    recon,lag=pcl(gen,ac,ml)
    null=[pcl(bp(bp(z:=phase_rand(x),r1)*bp(z,r2),r3),bp(z,r3),ml)[0] for _ in range(nn)]
    null=np.array(null); return dict(recon=float(recon),z=float((recon-null.mean())/(null.std()+1e-12)),lag_frac=float(lag)/r3)

jd,Ja,Jr,Jlz=load("jupiter"); _,Sa,Sr,Slz=load("saturn")
n=min(len(Ja),len(Sa)); Ja,Sa,Jr,Sr=Ja[:n],Sa[:n],Jr[:n],Sr[:n]
P_J=11.862*YR/dt; P_S=29.457*YR/dt; GI=883.0*YR/dt
print(f"N={n} span={(jd[n-1]-jd[0])/YR:.0f}yr  meanA: J={Ja.mean():.3f} S={Sa.mean():.3f}AU  GI needs {6*GI*dt/YR:.0f}yr\n")

print("=== Mix test on REAL semi-major axis a(t) ===")
print(f"{'signal':>14} {'home_yr':>8} {'recon':>7} {'z':>6} {'lag':>6}  verdict")
for nm,sig,P in [("Jupiter a",Ja,P_J),("Saturn a",Sa,P_S)]:
    r=mix_test(sig,P); v="PASS (builds tower)" if r["z"]>=2 else "fail"
    print(f"{nm:>14} {P*dt/YR:>8.2f} {r['recon']:>+7.2f} {r['z']:>+6.1f} {r['lag_frac']:>+6.2f}  {v}")

def detr(x,d=2):
    t=np.arange(len(x)); return x-np.polyval(np.polyfit(t,x,d),t)
Jgi=bp(detr(Ja),GI,1.6); Sgi=bp(detr(Sa),GI,1.6)
cc,lag=pcl(Jgi,Sgi,ml=int(GI*1.5))
print("\n=== Exchange term (great-inequality mode in semi-major axis) ===")
tag='ANTI-PHASE' if cc<-0.2 else 'in-phase' if cc>0.2 else 'weak'
print(f"corr(Jupiter_a_GI, Saturn_a_GI) = {cc:+.2f} at lag {lag*dt/YR:+.0f}yr  ({tag})")
exch=Jgi/np.std(Jgi)-Sgi/np.std(Sgi)
r=mix_test(exch,GI)
if r is None: print(f"exchange mix test: too short")
else:
    v="PASS" if r["z"]>=2 else "fail (no tower)"
    print(f"exchange home={GI*dt/YR:.0f}yr  recon={r['recon']:+.2f} z={r['z']:+.1f} lag={r['lag_frac']:+.2f}  {v}")
