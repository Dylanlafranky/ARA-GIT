"""Randomness as a variable constant: forecast residual = ARA 1.0 (lotto barrier), but its MAGNITUDE
(randomness envelope) is predictable from ENERGY+season (+0.25) -> a usable trust score.
RESULT: residual ARA=1.00; |residual|<-energy corr +0.25; high-confidence half forecasts +0.37 vs
low-confidence +0.16 (>2x). Strict-causal, feeder-era ENSO. Run from TheFormula/Claude4.8/."""
import sys, numpy as np
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"../../..")
import ara_framework as F
PHI=F.PHI
def load_dmi(p,miss=-9990.0):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==13 and s[0].isdigit() and len(s[0])==4:
            for mo in range(1,13):
                try:v=float(s[mo])
                except:continue
                if v>miss:d[f"{int(s[0])}{mo:02d}"]=v
    return d
W=B.load_wwv("wwv_west.dat");E=B.load_wwv("wwv_east.dat");nino=B.load_nino("nino34_long_anom.csv")
SOI=B.load_soi("soi.data");IOD=load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
ck=sorted(set(W)&set(E)&set(nino)&set(SOI)&set(IOD));arr=lambda d:np.array([d[k] for k in ck])
ni=arr(nino);n=len(ni);mon=np.array([int(k[4:6]) for k in ck])
def smooth(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
def envz(x,P):
    b=F.causal_bandpass(np.asarray(x,float),P,0.25);a=smooth(np.abs(b),max(3,int(P/2)));return (a-a.mean())/(a.std()+1e-9)
def ctrail(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
def ridge(X,y,Xt,p=0.1):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold);cut=int(n/PHI)
eSOI=envz(arr(SOI),31);eIOD=envz(arr(IOD),19);lags=[1,2,3,6,12,24,48];SOIr=arr(SOI);IODr=arr(IOD)
def feat(o,h):
    fp=th[o]+2*np.pi*h/55.0
    return np.column_stack([np.array([[ni[t-l] for l in lags] for t in o]),Ago[o]*np.cos(fp),Ago[o]*np.sin(fp),SOIr[o],IODr[o]])
def cfeat(o):return np.column_stack([Ago[o],eSOI[o],eIOD[o],np.cos(2*np.pi*(mon[o]-1)/12),np.sin(2*np.pi*(mon[o]-1)/12)])
if __name__=="__main__":
    h=12
    o=np.arange(60,n-h);tr=o[o+h<cut];te=o[o>=cut];d=ni[tr+h]-ni[tr]
    pred_tr=ni[tr]+ridge(feat(tr,h),d,feat(tr,h));pred_te=ni[te]+ridge(feat(tr,h),d,feat(te,h))
    res_tr=ni[tr+h]-pred_tr;res_te=ni[te+h]-pred_te
    zr=(res_te-res_te.mean())/res_te.std();print(f"residual ARA = {(1+np.tanh(zr/2)).mean():.2f}")
    conf=ridge(cfeat(tr),np.abs(res_tr),cfeat(te))
    print(f"|residual| <- energy+season corr = {np.corrcoef(conf,np.abs(res_te))[0,1]:+.3f}")
    order=np.argsort(conf);half=len(te)//2;hi=order[:half];lo=order[half:]
    cr=lambda a,b:np.corrcoef(a,b)[0,1]
    print(f"overall {cr(pred_te,ni[te+h]):+.3f} | HIGH-conf {cr(pred_te[hi],ni[te+h][hi]):+.3f} | LOW-conf {cr(pred_te[lo],ni[te+h][lo]):+.3f}")
