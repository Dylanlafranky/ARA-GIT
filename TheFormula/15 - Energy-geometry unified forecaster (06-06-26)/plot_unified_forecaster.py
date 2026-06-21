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
ni=arr(nino);n=len(ni);cut=int(n/PHI);mon=np.array([int(k[4:6]) for k in ck]);yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in ck])
def smooth(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
def envz(x,P):
    b=F.causal_bandpass(np.asarray(x,float),P,0.25);a=smooth(np.abs(b),max(3,int(P/2)));return (a-a.mean())/(a.std()+1e-9)
def ridge(X,y,Xt,p=0.1):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold)
lags=[1,2,3,6,12,24,48];SOIr=arr(SOI);IODr=arr(IOD)
charge=arr(W)+arr(E);chz=(charge-charge[:cut].mean())/charge[:cut].std();chtr=chz-np.concatenate([[chz[0]],chz[:-1]]);storedE=Ago**2
eSOI=envz(arr(SOI),31);eIOD=envz(arr(IOD),19)
def cc(a,b):return np.corrcoef(a,b)[0,1]
HZ=[3,6,9,12,18,24,36]
VAL={};DIRg={};DIRe={};DIRc={};CONF={}
for h in HZ:
    fp=th+2*np.pi*h/55.0
    o=np.arange(60,n-h);tr=o[o+h<cut];te=o[o>=cut];d=ni[tr+h]-ni[tr];tdir=np.sign(ni[te+h]-ni[te])
    def vfeat(idx):return np.column_stack([np.array([[ni[t-l] for l in lags] for t in idx]),Ago[idx]*np.cos(fp[idx]),Ago[idx]*np.sin(fp[idx]),SOIr[idx],IODr[idx],chz[idx],chtr[idx],storedE[idx]])
    pv=ni[te]+ridge(vfeat(tr),d,vfeat(te));VAL[h]=cc(pv,ni[te+h])
    geo=lambda i:np.column_stack([Ago[i]*np.cos(fp[i]),Ago[i]*np.sin(fp[i])])
    en =lambda i:np.column_stack([chz[i],chtr[i],storedE[i]])
    hit=lambda ps:np.mean((np.sign(ps-ni[te])==tdir)[tdir!=0])
    DIRg[h]=hit(ni[te]+ridge(geo(tr),d,geo(te)));DIRe[h]=hit(ni[te]+ridge(en(tr),d,en(te)))
    DIRc[h]=hit(ni[te]+ridge(np.column_stack([geo(tr),en(tr)]),d,np.column_stack([geo(te),en(te)])))
    # confidence: predicted |residual| envelope corr
    rtr=d-(ridge(vfeat(tr),d,vfeat(tr)));cf=lambda i:np.column_stack([Ago[i],eSOI[i],eIOD[i]])
    env=ridge(cf(tr),np.abs(rtr),cf(te));CONF[h]=cc(env,np.abs(ni[te+h]-pv))

fig,ax=plt.subplots(1,3,figsize=(16,5.2));fig.patch.set_facecolor("white")
# Panel 1: VALUE correlation
ax[0].plot(HZ,[VAL[h] for h in HZ],"o-",color="#1f77b4",lw=2.2)
ax[0].axhspan(0.6,0.7,color="grey",alpha=.12);ax[0].text(35,0.66,"operational ~0.6–0.7",fontsize=8,ha="right")
ax[0].set_title("VALUE — correlation vs truth\n(geometry reads the energy)",fontweight="bold",fontsize=10.5)
ax[0].set_xlabel("horizon (months)");ax[0].set_ylabel("correlation");ax[0].grid(alpha=.2);ax[0].set_ylim(0,1)
# Panel 2: DIRECTION — energy vs geometry handoff
ax[1].plot(HZ,[DIRe[h] for h in HZ],"o-",color="#d62728",lw=2,label="energy (reservoir)")
ax[1].plot(HZ,[DIRg[h] for h in HZ],"s-",color="#7a5195",lw=2,label="geometry (phase clock)")
ax[1].plot(HZ,[DIRc[h] for h in HZ],"--",color="#222",lw=1.6,label="combined")
ax[1].axhline(0.5,color="k",lw=1);ax[1].text(35,0.515,"chance",fontsize=8,ha="right")
ax[1].axvspan(3,12,color="#d62728",alpha=.06);ax[1].axvspan(18,36,color="#7a5195",alpha=.06)
ax[1].text(7,0.78,"clear energy\nreading",fontsize=8,color="#d62728",ha="center")
ax[1].text(27,0.78,"geometry\nskeleton only",fontsize=8,color="#7a5195",ha="center")
ax[1].set_title("DIRECTION — energy leads short, geometry carries long\n(the SAME read, decohering with horizon)",fontweight="bold",fontsize=10.5)
ax[1].set_xlabel("horizon (months)");ax[1].set_ylabel("turns called right");ax[1].legend(fontsize=8);ax[1].grid(alpha=.2);ax[1].set_ylim(.45,.85)
# Panel 3: CONFIDENCE — energy predicts the randomness envelope
ax[2].plot(HZ,[CONF[h] for h in HZ],"o-",color="#2ca02c",lw=2.2)
ax[2].axhline(0,color="k",lw=.7)
ax[2].set_title("CONFIDENCE — energy predicts the\nrandomness envelope (when to trust)",fontweight="bold",fontsize=10.5)
ax[2].set_xlabel("horizon (months)");ax[2].set_ylabel("corr(predicted |resid|, actual)");ax[2].grid(alpha=.2);ax[2].set_ylim(-.05,.4)
fig.suptitle("ARA unified ENSO forecaster — ONE energy reading through the geometry, three outputs  (strict-causal, test 2016–2025)",fontsize=12.5,fontweight="bold",y=1.0)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_unified_three_output_forecaster.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
print("VALUE:",{h:round(VAL[h],2) for h in HZ});print("DIR energy:",{h:round(DIRe[h],2) for h in HZ});print("DIR geom:",{h:round(DIRg[h],2) for h in HZ})
