"""Retrodiction = the forward engine-clock + home-AR predictor run on REVERSED time.
Reverse the series, run the same forward predictor; its forecasts on the flipped series = retrodictions.
RESULT: reverse dir ~0.71-0.75 @1-2yr, nearly mirrors forward (~0.77-0.81); small forward-reverse gap =
arrow of time (ENSO onset skew); same ~2yr decoherence wall both ways. Strict-causal, real NINO3.4 1870+.
Run from TheFormula/Claude4.8/."""
import sys, numpy as np
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"../../..")
import ara_framework as F
PHI=F.PHI
ni_full=np.array(list(B.load_nino("nino34_long_anom.csv").values()))
def ctrail(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
def ridge(X,y,Xt,p=0.1):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
def predictor(ni,h):
    n=len(ni);cut=int(n/PHI)
    gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
    Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold);L=ctrail(ni,48)
    lags=[1,2,3,6,12,24,48]
    o=np.arange(50,n-h);tr=o[o+h<cut];te=o[o>=cut]
    if len(te)<30:return np.nan,np.nan
    d=ni[tr+h]-ni[tr]
    def feat(idx,fp):
        lm=np.array([[ni[t-l] for l in lags] for t in idx])
        return np.column_stack([lm,Ago[idx]*np.cos(fp),Ago[idx]*np.sin(fp)])
    pred=ni[te]+ridge(feat(tr,th[tr]+2*np.pi*h/55.0),d,feat(te,th[te]+2*np.pi*h/55.0))
    cur=ni[te];fut=ni[te+h];cval=np.corrcoef(pred,fut)[0,1]
    tdir=np.sign(fut-cur);pd=np.sign(pred-cur);m=tdir!=0
    return cval,float(np.mean(pd[m]==tdir[m]))
if __name__=="__main__":
    print(f"{'h':>6}{'fwd corr':>10}{'rev corr':>10}{'fwd dir':>9}{'rev dir':>9}")
    for h in (6,12,18,24,36):
        fc,fd=predictor(ni_full,h);rc,rd=predictor(ni_full[::-1],h)
        print(f"{h:>6}{fc:>+10.3f}{rc:>+10.3f}{fd:>9.3f}{rd:>9.3f}")
