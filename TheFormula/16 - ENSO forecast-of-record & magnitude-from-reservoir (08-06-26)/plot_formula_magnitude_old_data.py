import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
keys=sorted(B.load_nino("nino34_long_anom.csv"));d=B.load_nino("nino34_long_anom.csv")
ni=np.array([d[k] for k in keys]);n=len(ni)
yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
def smooth(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
def ctrail(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold);L=ctrail(ni,48)
# recharge reservoir PROXY (causal): trailing 9-mo cool accumulation = stored energy
recharge=ctrail(-ni,9)   # high when recently cool (charging)
rz=(recharge-np.nanmean(recharge))/np.nanstd(recharge)
lags=[1,2,3,6,12,24,48]
def ridge(X,y,Xt,p=0.2):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
h=6
fp=th+2*np.pi*h/55.0
def feat(o,reservoir):
    cols=[np.array([[ni[t-l] for l in lags] for t in o]),Ago[o]*np.cos(fp[o]),Ago[o]*np.sin(fp[o])]
    if reservoir: cols+=[rz[o],rz[o]*np.cos(fp[o]),rz[o]*Ago[o]]   # reservoir sets/modulates amplitude
    return np.column_stack(cols)
trcut=int(n*0.35)   # train on earliest ~35% (1870-1923), hindcast the rest
tr=np.arange(60,trcut-h);te=np.arange(trcut,n-h);dtr=ni[tr+h]-ni[tr]
pred_geo=ni[te]+ridge(feat(tr,False),dtr,feat(te,False))
pred_res=ni[te]+ridge(feat(tr,True),dtr,feat(te,True))
truth=ni[te+h];tyr=yr[te]+h/12
def cc(a,b):return np.corrcoef(a,b)[0,1]
print(f"hindcast {tyr[0]:.0f}-{tyr[-1]:.0f} (h=6mo, trained on 1870-{yr[trcut]:.0f})")
print(f"  geometry only:        corr {cc(pred_geo,truth):+.3f}  MAE {np.mean(np.abs(pred_geo-truth)):.3f}")
print(f"  geometry + reservoir: corr {cc(pred_res,truth):+.3f}  MAE {np.mean(np.abs(pred_res-truth)):.3f}")
# plot an OLD window
fig,ax=plt.subplots(figsize=(14,5.5));fig.patch.set_facecolor("white")
m=(tyr>=1925)&(tyr<=1990)
ax.axhline(0,color="k",lw=.6);ax.axhspan(0.5,3,color="#d62728",alpha=.04);ax.axhspan(-3,-0.5,color="#1f77b4",alpha=.04)
ax.plot(tyr[m],truth[m],color="#111",lw=2,label="truth (NINO3.4)")
ax.plot(tyr[m],pred_geo[m],color="#7a5195",lw=1.4,ls=":",label=f"formula: geometry only (corr {cc(pred_geo,truth):+.2f})")
ax.plot(tyr[m],pred_res[m],color="#d62728",lw=1.8,label=f"formula: geometry + reservoir magnitude (corr {cc(pred_res,truth):+.2f})")
ax.set_xlabel("year");ax.set_ylabel("NINO3.4 anomaly (°C)")
ax.set_title("Prediction formula on OLD ENSO vs truth (6-month lead, strict-causal, trained only on 1870–1923)\nreservoir-magnitude term scales the swings to match the big vs small events",fontweight="bold",fontsize=10.5)
ax.legend(fontsize=9,loc="upper left");ax.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_formula_with_magnitude_old_data.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
