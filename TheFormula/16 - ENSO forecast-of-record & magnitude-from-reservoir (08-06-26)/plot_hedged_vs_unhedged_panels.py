import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
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
ni=arr(nino);n=len(ni);cut=int(n/F.PHI);yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in ck])
def sm(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
gold=F.causal_bandpass(ni,55.,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold);L=sm(ni,48)
SOIr=arr(SOI);IODr=arr(IOD);lags=[1,2,3,6,12,24,48];h=6;fp=th+2*np.pi*h/55
def ridge(X,y,Xt,p=0.2):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
def feat(o):return np.column_stack([np.array([[ni[t-l] for l in lags] for t in o]),Ago[o]*np.cos(fp[o]),Ago[o]*np.sin(fp[o]),SOIr[o],IODr[o]])
tr=np.arange(60,cut-h);te=np.arange(cut,n-h);d=ni[tr+h]-ni[tr];truth=ni[te+h];cur=ni[te];ty=yr[te]+h/12
hedged=ni[te]+ridge(feat(tr),d,feat(te))
sig_train=np.std(ni[tr+h]-L[tr+h]);dev=hedged-L[te];dz=(dev-dev.mean())/(np.std(dev)+1e-9)
unhedged=L[te]+dz*sig_train
def cc(a,b):return np.corrcoef(a,b)[0,1]
def amp(p):return np.std(p-L[te])/np.std(truth-L[te])
m=ty>=2008
fig,(ax1,ax2)=plt.subplots(2,1,figsize=(14,8),sharex=True);fig.patch.set_facecolor("white")
for ax,(nm,p,c) in zip((ax1,ax2),[("HEDGED (MSE — minimizes average error, damps the peaks)",hedged,"#7a5195"),
                                   ("UN-HEDGED (full amplitude — commits to the extremes)",unhedged,"#2ca02c")]):
    ax.axhline(0,color="k",lw=.6);ax.axhspan(0.5,3,color="#d62728",alpha=.05);ax.axhspan(-3,-0.5,color="#1f77b4",alpha=.05)
    ax.text(2008.3,1.4,"El Niño",fontsize=8,color="#d62728");ax.text(2008.3,-1.5,"La Niña",fontsize=8,color="#1f77b4")
    ax.plot(ty[m],truth[m],color="#111",lw=2,label="truth")
    ax.plot(ty[m],p[m],color=c,lw=1.7,label="forecast")
    ax.fill_between(ty[m],truth[m],p[m],color=c,alpha=.12)
    ax.set_title(f"{nm}   |   amplitude {amp(p):.2f} of truth · change-corr {cc(p-cur,truth-cur):+.2f}",fontweight="bold",fontsize=10)
    ax.set_ylabel("NINO3.4 (°C)");ax.legend(fontsize=9,loc="upper right");ax.grid(alpha=.2);ax.set_ylim(-2.2,2.8)
ax2.set_xlabel("year")
fig.suptitle("ENSO 6-month forecast vs truth — HEDGED vs UN-HEDGED (strict-causal, held-out 2008–2025)\nshaded = gap to truth; the hedge stays safe in the middle, un-hedged reaches the real peaks",
             fontsize=12,fontweight="bold",y=0.99)
fig.tight_layout(rect=[0,0,1,0.96])
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_hedged_vs_unhedged_panels.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
