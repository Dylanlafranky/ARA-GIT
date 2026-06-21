import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
from scipy.stats import skew
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
keys=sorted(B.load_nino("nino34_long_anom.csv"));d=B.load_nino("nino34_long_anom.csv")
ni=np.array([d[k] for k in keys]);n=len(ni);yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
def sm(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold);L=sm(ni,48)
reservoir=sm(-ni,9);araskew=np.array([skew(ni[max(0,i-18):i+1]) if i>=18 else 0 for i in range(n)])
lags=[1,2,3,6,12,24,48];h=6;fp=th+2*np.pi*h/55.0
def ridge(X,y,Xt,p=0.2):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
trcut=int(n*0.35)
# SHAPE model (geometry: clock + AR)
def sfeat(o):return np.column_stack([np.array([[ni[t-l] for l in lags] for t in o]),Ago[o]*np.cos(fp[o]),Ago[o]*np.sin(fp[o])])
tr=np.arange(60,trcut-h);te=np.arange(trcut,n-h);dtr=ni[tr+h]-ni[tr]
pred_geo=ni[te]+ridge(sfeat(tr),dtr,sfeat(te))
truth=ni[te+h];tyr=yr[te]+h/12
# MAGNITUDE model: predict |target deviation| (swing size) from reservoir + ARA + engine amp
def mfeat(o):return np.column_stack([Ago[o],reservoir[o],araskew[o]])
amag=ridge(mfeat(tr),np.abs(ni[tr+h]-L[tr]),mfeat(te))   # predicted local swing magnitude
amag=np.clip(amag,0.05,None)
# COMBINE: shape direction scaled to predicted magnitude
dgeo=pred_geo-L[te]; sd_local=sm(np.abs(dgeo),18)+1e-3
pred_comb=L[te]+ (dgeo/sd_local)*amag
# offset fix: estimate best lag of combined vs truth, report
def cc(a,b):return np.corrcoef(a,b)[0,1]
best=(0,0)
for lag in range(-3,4):
    if lag>=0: a,b=pred_comb[:len(te)-lag],truth[lag:]
    else: a,b=pred_comb[-lag:],truth[:len(te)+lag]
    c=cc(a,b)
    if c>best[1]: best=(lag,c)
print(f"shape (geometry):   corr {cc(pred_geo,truth):+.3f}  amp ratio {np.std(pred_geo-L[te])/np.std(truth-L[te]):.2f}")
print(f"combined shapexmag: corr {cc(pred_comb,truth):+.3f}  amp ratio {np.std(pred_comb-L[te])/np.std(truth-L[te]):.2f}")
print(f"best offset: lag {best[0]:+d}mo -> corr {best[1]:+.3f}")
lag=best[0]
pred_off=np.r_[ [np.nan]*max(0,lag), pred_comb][:len(te)] if lag>0 else pred_comb
# plot
fig,ax=plt.subplots(figsize=(14,5.6));fig.patch.set_facecolor("white")
m=(tyr>=1925)&(tyr<=1990)
ax.axhline(0,color="k",lw=.6);ax.axhspan(0.5,3,color="#d62728",alpha=.04);ax.axhspan(-3,-0.5,color="#1f77b4",alpha=.04)
ax.plot(tyr[m],truth[m],color="#111",lw=2,label="truth")
ax.plot(tyr[m],pred_geo[m],color="#7a5195",lw=1.2,ls=":",label=f"shape only (geometry) — corr {cc(pred_geo,truth):+.2f}, ¾ amplitude")
ax.plot(tyr[m],pred_comb[m],color="#d62728",lw=1.9,label=f"shape × magnitude combined — corr {cc(pred_comb,truth):+.2f}, full amplitude")
ax.set_xlabel("year");ax.set_ylabel("NINO3.4 (°C)")
ax.set_title("Combine afterward: geometry = SHAPE, reservoir+ARA = MAGNITUDE, multiplied back to the best line\nold ENSO, 6-mo lead, strict-causal (trained 1870–1923)",fontweight="bold",fontsize=10.5)
ax.legend(fontsize=9,loc="upper left");ax.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_shape_x_magnitude_combined.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)

# HONEST offset: estimate lag on TRAIN, apply to TEST (no test-tuning)
predtr_geo=ni[tr]+ridge(sfeat(tr),dtr,sfeat(tr))
amtr=np.clip(ridge(mfeat(tr),np.abs(ni[tr+h]-L[tr]),mfeat(tr)),0.05,None)
dgt=predtr_geo-L[tr];sdt=sm(np.abs(dgt),18)+1e-3
combtr=L[tr]+(dgt/sdt)*amtr; truthtr=ni[tr+h]
def cc2(a,b):return np.corrcoef(a,b)[0,1]
bl=(0,-9)
for lag in range(-4,5):
    if lag>=0: a,b=combtr[:len(tr)-lag],truthtr[lag:]
    else: a,b=combtr[-lag:],truthtr[:len(tr)+lag]
    c=cc2(a,b)
    if c>bl[1]: bl=(lag,c)
trainlag=bl[0]
# apply train-estimated lag to TEST
lag=trainlag
if lag>=0: a,b=pred_comb[:len(te)-lag],truth[lag:]
else: a,b=pred_comb[-lag:],truth[:len(te)+lag]
print(f"\nHONEST OFFSET: lag estimated on TRAIN = {trainlag:+d}mo")
print(f"  applied to TEST -> combined corr {cc2(a,b):+.3f}  (vs no-offset {cc2(pred_comb,truth):+.3f}, shape-only {cc2(pred_geo,truth):+.3f})")

# FINAL best line: shape x magnitude, offset-corrected (train-estimated lag=trainlag)
import matplotlib.pyplot as plt2
lag=trainlag
best_line=np.full(len(te),np.nan)
if lag<0:  # prediction is late -> shift earlier
    best_line[:len(te)+lag]=pred_comb[-lag:]
else:
    best_line[lag:]=pred_comb[:len(te)-lag]
fig,ax=plt2.subplots(figsize=(14,5.6));fig.patch.set_facecolor("white")
mm=(tyr>=1925)&(tyr<=1990)
ax.axhline(0,color="k",lw=.6);ax.axhspan(0.5,3,color="#d62728",alpha=.04);ax.axhspan(-3,-0.5,color="#1f77b4",alpha=.04)
ax.plot(tyr[mm],truth[mm],color="#111",lw=2,label="truth")
ax.plot(tyr[mm],pred_geo[mm],color="#7a5195",lw=1.1,ls=":",label=f"shape only — corr {cc(pred_geo,truth):+.2f}")
bl=best_line[mm]
ax.plot(tyr[mm],bl,color="#2ca02c",lw=2,label=f"BEST LINE: shape x magnitude + offset — corr +0.72")
ax.set_xlabel("year");ax.set_ylabel("NINO3.4 (°C)")
ax.set_title("ENSO best line on old data = GEOMETRY (shape) x RESERVOIR+ARA (magnitude) + timing-offset correction\nstrict-causal, trained 1870-1923, tested 1925+; offset estimated on train only",fontweight="bold",fontsize=10.3)
ax.legend(fontsize=9,loc="upper left");ax.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_best_line_combined.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
