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
ni=arr(nino);n=len(ni);cut=int(n/F.PHI);yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in ck]);mon=np.array([int(k[4:6]) for k in ck])
def sm(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
def envz(x,P):
    b=F.causal_bandpass(np.asarray(x,float),P,0.25);a=sm(np.abs(b),max(3,int(P/2)));return (a-a.mean())/(a.std()+1e-9)
gold=F.causal_bandpass(ni,55.,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold);L=sm(ni,48)
SOIr=arr(SOI);IODr=arr(IOD);eSOI=envz(SOI and arr(SOI) if False else arr(SOI),31);eIOD=envz(arr(IOD),19)
lags=[1,2,3,6,12,24,48];h=6;fp=th+2*np.pi*h/55
def ridge(X,y,Xt,p=0.2):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
def feat(o):return np.column_stack([np.array([[ni[t-l] for l in lags] for t in o]),Ago[o]*np.cos(fp[o]),Ago[o]*np.sin(fp[o]),SOIr[o],IODr[o]])
def cf(o):return np.column_stack([Ago[o],eSOI[o],eIOD[o],np.cos(2*np.pi*(mon[o]-1)/12),np.sin(2*np.pi*(mon[o]-1)/12)])
tr=np.arange(60,cut-h);te=np.arange(cut,n-h);d=ni[tr+h]-ni[tr];truth=ni[te+h];cur=ni[te];ty=yr[te]+h/12
hedged=ni[te]+ridge(feat(tr),d,feat(te))                       # ACCURATE central (late)
res_tr=ni[tr+h]-(ni[tr]+ridge(feat(tr),d,feat(tr)))
env=np.clip(ridge(cf(tr),np.abs(res_tr),cf(te)),0.1,None)      # CONFIDENCE (how sure)
sig=np.std(ni[tr+h]-L[tr+h]);dev=hedged-L[te];dz=(dev-dev.mean())/(np.std(dev)+1e-9)
unhedged=L[te]+dz*sig                                          # WARNING (full amplitude)
# plot
fig,ax=plt.subplots(figsize=(14,6));fig.patch.set_facecolor("white")
m=ty>=2008
ax.axhline(0,color="k",lw=.6);ax.axhline(0.5,color="#d62728",lw=.8,ls=":");ax.axhline(-0.5,color="#1f77b4",lw=.8,ls=":")
ax.text(2024.4,0.57,"El Niño",fontsize=7,color="#d62728");ax.text(2024.4,-0.62,"La Niña",fontsize=7,color="#1f77b4")
ax.fill_between(ty[m],hedged[m]-env[m],hedged[m]+env[m],color="grey",alpha=.18,label="confidence band (how sure)")
ax.plot(ty[m],truth[m],color="#111",lw=2,label="truth",zorder=5)
ax.plot(ty[m],hedged[m],color="#7a5195",lw=1.6,label="best estimate (hedged — accurate, slightly late)")
ax.plot(ty[m],unhedged[m],color="#2ca02c",lw=1.3,ls="--",alpha=.9,label="early warning (un-hedged — how big it's loading)")
ax.set_xlabel("year");ax.set_ylabel("NINO3.4 (°C)");ax.set_ylim(-2.4,3.0)
ax.set_title("ENSO 6-month forecast — combined view (strict-causal, held-out)\nWARNING (green, full amplitude) + BEST ESTIMATE (purple, accurate) + CONFIDENCE band (grey)",fontweight="bold",fontsize=11)
ax.legend(fontsize=8.5,loc="upper left");ax.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_warning_estimate_confidence.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
