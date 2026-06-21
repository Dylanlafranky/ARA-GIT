import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,"/tmp"); sys.path.insert(0,".")
import apf as A
import enso_pdo_feeder_test as B
d=dict(B.load_nino("nino34_long_anom.csv")); d["202601"]=-0.37; d["202602"]=-0.16  # extend to current (CPC ONI)
keys=sorted(d); ni=np.array([d[k] for k in keys]); n=len(ni)
yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
P=55.0; PHI=A.PHI
# ---- universal-formula parts (same as ara_forecast), fit on ALL history, projected FORWARD ----
gold=A._causal_bandpass(ni,P,0.25); v=gold-np.concatenate([[gold[0]],gold[:-1]]); om=2*np.pi/P
Ago=np.sqrt(gold**2+(v/om)**2); th=np.arctan2(-v/om,gold); L=A._trail_mean(ni,int(P))
reservoir=A._trail_mean(-ni,max(3,int(P/6))); rz=(reservoir-reservoir.mean())/(reservoir.std()+1e-9)
araskew=A._trail_skew(ni,max(8,int(P/3)))
home_lags=[l for l in [1,2,3,6,12,int(round(P/4)),int(round(P/2)),int(round(P))] if 0<l<n//3]
start=max(home_lags)+2; o0=n-1
def feat(o,h):
    fp=th+2*np.pi*h/P
    return np.column_stack([np.array([[ni[t-l] for l in home_lags] for t in o]),
        Ago[o]*np.cos(fp[o]),Ago[o]*np.sin(fp[o]),rz[o],araskew[o],rz[o]*Ago[o]])
H=np.arange(1,19); best=[];warn=[];conf=[]
sig_all=np.std(ni-L)   # full real swing scale (for un-hedging)
for h in H:
    tr=np.arange(start,n-h); dd=ni[tr+h]-ni[tr]
    p=ni[o0]+A._ridge(feat(tr,h),dd,feat(np.array([o0]),h))[0]   # best estimate (hedged)
    best.append(p)
    # confidence: energy predicts residual size
    res=ni[tr+h]-(ni[tr]+A._ridge(feat(tr,h),dd,feat(tr,h)))
    cf=lambda idx:np.column_stack([Ago[idx],rz[idx],araskew[idx]])
    conf.append(float(np.clip(A._ridge(cf(tr),np.abs(res),cf(np.array([o0])))[0],0.1,None)))
best=np.array(best);conf=np.array(conf)
# UN-HEDGE the forward trajectory: rescale deviations from level to full amplitude
dev=best-L[o0]; 
if np.std(dev)>1e-6: warn=L[o0]+(dev-dev.mean())/np.std(dev)*sig_all*(np.std(dev)/np.std(dev))  # keep shape
# simpler robust un-hedge: scale dev so trajectory std ~ historical swing, but keep sign/shape
scale = sig_all/ (np.std(dev)+1e-9)
warn = L[o0] + dev*min(scale, 3.0)   # cap scaling to avoid blow-up
fyr=yr[o0]+H/12
print(f"anchor {keys[-1]} NINO={ni[-1]:+.2f}; WWV charging (+1.96 sigma to Apr2026, leading)")
print("forward (best / WARNING un-hedged):")
for i in [2,5,8,11,17]:
    print(f"  +{H[i]:>2}mo ({fyr[i]:.1f}): best {best[i]:+.2f}  warning {warn[i]:+.2f}  +/-{conf[i]:.2f}")
# plot
fig,ax=plt.subplots(figsize=(14,6));fig.patch.set_facecolor("white")
m=yr>=2012
ax.axhline(0,color="k",lw=.6);ax.axhline(0.5,color="#d62728",lw=.9,ls=":");ax.axhline(-0.5,color="#1f77b4",lw=.9,ls=":")
ax.axhline(1.5,color="#d62728",lw=.7,ls=":",alpha=.5);ax.text(2012.3,1.55,"strong El Nino",fontsize=7,color="#d62728")
ax.text(2012.3,0.57,"El Nino",fontsize=7,color="#d62728");ax.text(2012.3,-0.66,"La Nina",fontsize=7,color="#1f77b4")
ax.plot(yr[m],ni[m],color="#111",lw=2,label="observed NINO3.4")
ax.axvline(fyr[0]-1/12,color="green",lw=1.4,ls="--");ax.text(fyr[0]+0.05,2.4,"NOW\n(Feb 2026)",fontsize=8,color="green")
ax.fill_between(fyr,warn-conf,warn+conf,color="#2ca02c",alpha=.15,label="confidence band")
ax.plot(fyr,warn,color="#2ca02c",lw=2.2,marker="o",ms=3,label="UN-HEDGED forecast (full amplitude / how big it's loading)")
ax.plot(fyr,best,color="#7a5195",lw=1.3,ls=":",label="hedged best estimate (for reference)")
ax.scatter([fyr[0]-1/12],[ni[-1]],color="green",zorder=6,s=30)
ax.set_xlabel("year");ax.set_ylabel("NINO3.4 (deg C)");ax.set_ylim(-2.2,3.0);ax.set_xlim(2012,2028)
ax.set_title("ENSO 2026 forward forecast — UN-HEDGED, universal ARA framework formula\nanchored Feb 2026 (neutral, warming; WWV reservoir charging). DIRECTION call; magnitude = a lean, not exact",fontweight="bold",fontsize=10.5)
ax.legend(fontsize=8.5,loc="upper left");ax.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_2026_forward_unhedged.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
