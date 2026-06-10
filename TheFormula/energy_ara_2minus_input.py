"""Dylan's 2-ARA energy-input rule: map the asymmetric energy SHIFT to an ARA (1+tanh z/2),
energy input = 2 - ARA_energy, add on top of the correlation forecast. Tests ARA-transform vs raw-linear.
RESULT: ARA(2-ARA) beats base & linear at 5/6 horizons; h=9 linear HURTS (0.297) but ARA HELPS (0.316)
= the slow-charge/fast-discharge asymmetry is real amplitude info. Strict-causal, feeder-era ENSO.
Run from TheFormula/Claude4.8/ (needs IOD_NOAA/dmi.had.long.data)."""
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
ni=arr(nino);n=len(ni);cut=int(n/PHI)
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold)
lags=[1,2,3,6,12,24,48];SOIr=arr(SOI);IODr=arr(IOD)
charge=arr(W)+arr(E)
zc=(charge-charge[:cut].mean())/charge[:cut].std()
dch=charge-np.concatenate([[charge[0]],charge[:-1]]);zd=(dch-dch[:cut].mean())/dch[:cut].std()
ara_c=1+np.tanh(zc/2.0);ara_d=1+np.tanh(zd/2.0)
einput_c=2.0-ara_c;einput_d=2.0-ara_d
def ridge(X,y,Xt,p=0.1):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
def run(h,mode):
    fp=th+2*np.pi*h/55.0
    def feat(o):
        base=[np.array([[ni[t-l] for l in lags] for t in o]),Ago[o,None]*np.cos(fp[o])[:,None],Ago[o,None]*np.sin(fp[o])[:,None],SOIr[o,None],IODr[o,None]]
        if mode=="lin":base+=[zc[o,None],zd[o,None]]
        if mode=="ara":base+=[einput_c[o,None],einput_d[o,None]]
        return np.column_stack(base)
    o=np.arange(60,n-h);tr=o[o+h<cut];te=o[o>=cut];d=ni[tr+h]-ni[tr]
    return np.corrcoef(ni[te]+ridge(feat(tr),d,feat(te)),ni[te+h])[0,1]
if __name__=="__main__":
    print(f"{'h':>4}{'base':>9}{'+linear':>10}{'+ARA(2-ARA)':>13}")
    for h in (3,6,9,12,18,24):
        print(f"{h:>4}{run(h,'base'):>9.3f}{run(h,'lin'):>10.3f}{run(h,'ara'):>13.3f}")
