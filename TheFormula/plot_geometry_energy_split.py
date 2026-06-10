import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
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
ni=arr(nino);n=len(ni);mon=np.array([int(k[4:6]) for k in ck]);yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in ck])
def smooth(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
def envz(x,P):
    b=F.causal_bandpass(np.asarray(x,float),P,0.25);a=smooth(np.abs(b),max(3,int(P/2)));return (a-a.mean())/(a.std()+1e-9)
def ridge(X,y,Xt,p=0.1):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold);cut=int(n/PHI)
eSOI=envz(arr(SOI),31);eIOD=envz(arr(IOD),19);lags=[1,2,3,6,12,24,48];SOIr=arr(SOI);IODr=arr(IOD)
h=18
def geomfeat(o):  # GEOMETRY = phase clock + AR + raw feeders
    fp=th[o]+2*np.pi*h/55.0
    return np.column_stack([np.array([[ni[t-l] for l in lags] for t in o]),Ago[o]*np.cos(fp),Ago[o]*np.sin(fp),SOIr[o],IODr[o]])
def cfeat(o):return np.column_stack([Ago[o],eSOI[o],eIOD[o],np.cos(2*np.pi*(mon[o]-1)/12),np.sin(2*np.pi*(mon[o]-1)/12)])
o=np.arange(60,n-h);tr=o[o+h<cut];te=o[o>=cut];d=ni[tr+h]-ni[tr]
beta=np.linalg.lstsq(np.column_stack([np.ones(len(tr)),geomfeat(tr)]),d,rcond=None)[0]
dev_tr=np.column_stack([np.ones(len(tr)),geomfeat(tr)])@beta
dev_te=np.column_stack([np.ones(len(te)),geomfeat(te)])@beta
geom_te=ni[te]+dev_te                       # GEOMETRY prediction
rtr=d-dev_tr
env_tr=ridge(cfeat(tr),np.abs(rtr),cfeat(tr));env_te=ridge(cfeat(tr),np.abs(rtr),cfeat(te))
ez_te=(env_te-env_tr.mean())/(env_tr.std()+1e-9);ez_tr=(env_tr-env_tr.mean())/(env_tr.std()+1e-9)
ab=np.linalg.lstsq(np.column_stack([dev_tr,dev_tr*ez_tr]),d,rcond=None)[0]
energy_term=ab[1]*dev_te*ez_te              # ENERGY amplitude addition
full_te=ni[te]+ab[0]*dev_te+energy_term     # GEOMETRY + ENERGY
truth=ni[te+h];ty=yr[te]+h/12
def cc(a,b):return np.corrcoef(a,b)[0,1]
# ---- PLOT ----
fig,(ax,ax2)=plt.subplots(2,1,figsize=(14,8.5),height_ratios=[2,1]);fig.patch.set_facecolor("white")
ax.axhline(0,color="k",lw=.6)
ax.plot(ty,truth,color="#111",lw=2,label="truth",zorder=5)
ax.plot(ty,geom_te,color="#1f77b4",lw=1.7,label=f"GEOMETRY (phase/clock+feeders)  corr {cc(geom_te,truth):+.2f}")
ax.plot(ty,full_te,color="#d62728",lw=1.7,ls="-",label=f"GEOMETRY + ENERGY (amplitude)  corr {cc(full_te,truth):+.2f}")
# energy contribution shaded between geometry and full
ax.fill_between(ty,geom_te,full_te,color="#d62728",alpha=.18,label="energy's amplitude contribution")
# confidence band from envelope (±predicted randomness)
ax.fill_between(ty,full_te-env_te,full_te+env_te,color="grey",alpha=.12,label="randomness envelope (±predicted |resid|)")
ax.set_title("ENSO 18-month forecast vs truth — prediction split into GEOMETRY (phase) + ENERGY (amplitude)",fontweight="bold")
ax.set_xlabel("year");ax.set_ylabel("NINO3.4 (°C)");ax.legend(fontsize=8.5,loc="upper right");ax.grid(alpha=.2)
# bottom: the two channels' roles
ax2.axhline(0,color="k",lw=.6)
ax2.plot(ty,ab[0]*dev_te,color="#1f77b4",lw=1.4,label="geometry channel → sets the SHAPE/phase")
ax2.plot(ty,energy_term,color="#d62728",lw=1.4,label="energy channel → adds AMPLITUDE where envelope is high")
ax2.plot(ty,env_te,color="#777",lw=1,ls=":",label="randomness envelope (confidence)")
ax2.set_title("the two channels: geometry = WHEN it turns · energy = HOW BIG + how trustworthy",fontweight="bold",fontsize=10)
ax2.set_xlabel("year");ax2.set_ylabel("contribution (°C)");ax2.legend(fontsize=8,loc="upper right");ax2.grid(alpha=.2)
fig.suptitle("ARA prediction decomposed: PHASE→value (geometry) + ENERGY→amplitude/confidence  (ENSO, strict-causal, test 2016–2025)",fontsize=12.5,fontweight="bold",y=.99)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_prediction_geometry_energy_split.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
