"""Does ENERGY determine ENSO direction? Energy-only (WWV charge + recharge rate + stored engine
energy, NO phase) vs phase clock, direction hit-rate by horizon. Strict-causal, feeder-era ENSO.
RESULT: energy 0.75@3mo, beats phase clock to ~12mo (recharge oscillator); phase carries 18-24mo.
Run from TheFormula/Claude4.8/ (needs enso_pdo_feeder_test + ara_framework on path)."""
import sys, numpy as np
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"../../..")  # to ara_framework (adjust if needed: GIT/ARA-GIT)
import ara_framework as F
PHI=F.PHI
W=B.load_wwv("wwv_west.dat");E=B.load_wwv("wwv_east.dat");nino=B.load_nino("nino34_long_anom.csv")
ck=sorted(set(W)&set(E)&set(nino));arr=lambda d:np.array([d[k] for k in ck])
ni=arr(nino);n=len(ni);cut=int(n/PHI)
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold)
charge=arr(W)+arr(E);chz=(charge-charge[:cut].mean())/charge[:cut].std()
chtr=chz-np.concatenate([[chz[0]],chz[:-1]]);storedE=Ago**2
def ridge(X,y,Xt,p=0.1):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
def hit(ps,ts):
    m=(ps!=0)&(ts!=0);return float(np.mean(ps[m]==ts[m]))
def dirtest(h):
    o=np.arange(60,n-h);tr=o[o+h<cut];te=o[o>=cut];d=ni[tr+h]-ni[tr];tdir=np.sign(ni[te+h]-ni[te])
    fp=th+2*np.pi*h/55.0
    geo=lambda i:np.column_stack([Ago[i]*np.cos(fp[i]),Ago[i]*np.sin(fp[i])])
    en =lambda i:np.column_stack([chz[i],chtr[i],storedE[i]])
    pred=lambda fn:ni[te]+ridge(fn(tr),d,fn(te))
    pg=np.sign(pred(geo)-ni[te]);pe=np.sign(pred(en)-ni[te])
    pc=np.sign(pred(lambda i:np.column_stack([geo(i),en(i)]))-ni[te])
    return hit(pg,tdir),hit(pe,tdir),hit(pc,tdir)
if __name__=="__main__":
    print(f"{'h':>4}{'phase/geom':>12}{'ENERGY only':>13}{'combined':>10}")
    for h in (3,6,9,12,18,24):
        g,e,c=dirtest(h);print(f"{h:>4}{g:>12.3f}{e:>13.3f}{c:>10.3f}")
