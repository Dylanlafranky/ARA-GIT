# Strict-causal horizon sweep: self-forecast vs persistence vs cycle-ago. Find flywheel wall.
import numpy as np
z=np.load('solar_silso_monthly.npz'); x=z['ssn'].astype(float); N=len(x); phi=1.6180339887
lags=[1,2,3,6,9,12,18,24,36,48,72,96,120,132]; Lmax=max(lags)
HS=[12,24,48,96,132,180,264,300,396,528]
def feats(i): return [1.0]+[x[i-l] for l in lags]
print(" horizon(yr)  self  persist  cycle-ago")
for h in HS:
    idx=[i for i in range(Lmax,N-h)]; X=np.array([feats(i) for i in idx]); y=x[np.array(idx)+h]
    m=len(idx); tr=slice(0,m//2); te=slice(m//2,m)
    mu=X[tr].mean(0); sd=X[tr].std(0); sd[sd==0]=1; mu[0]=0; sd[0]=1; Xs=(X-mu)/sd
    b,*_=np.linalg.lstsq(Xs[tr],y[tr],rcond=None); p=Xs[te]@b; a=y[te]
    now=np.array([x[i] for i in idx])[te]
    ca=np.array([x[i+h-132] if (i+h-132)>=0 else np.nan for i in idx])[te]; g=np.isfinite(ca)
    print(f" {h:4d}({h/12:5.1f})  {np.corrcoef(p,a)[0,1]:+.3f}  {np.corrcoef(now,a)[0,1]:+.3f}  {np.corrcoef(ca[g],a[g])[0,1]:+.3f}")
