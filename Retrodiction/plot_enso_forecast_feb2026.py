import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
PHI=F.PHI
d=B.load_nino("nino34_long_anom.csv");keys=sorted(d)
ni=np.array([d[k] for k in keys]+[-0.37,-0.16])
yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys]+[2026.0,2026+1/12])
n=len(ni)
W=B.load_wwv("wwv_west.dat");E=B.load_wwv("wwv_east.dat");ckw=sorted(set(W)&set(E))
chg=np.array([W[k]+E[k] for k in ckw]);chz=(chg-chg.mean())/chg.std()
wyr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in ckw])
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold);th0=th[-1];A0=Ago[-1]
now=2026+1/12;last=ni[-1]   # anchor here (-0.16)
H=np.arange(0,31);fyr=now+H/12
shape=A0*np.cos(th0+2*np.pi*H/55.0)
fproj=last+(shape-shape[0])                     # engine shape, anchored to last obs
wwv_now=chz[-1]
warm_lean=np.clip(wwv_now*0.30*np.sin(np.pi*np.clip(H,0,18)/18),0,None)
fproj_e=fproj+warm_lean
band=0.2+0.4*(H/30.0)
fig,(ax,ax2)=plt.subplots(2,1,figsize=(14,8),height_ratios=[2.3,1],sharex=True);fig.patch.set_facecolor("white")
m=yr>=2018
ax.axhline(0,color="k",lw=.7);ax.axhspan(0.5,3,color="#d62728",alpha=.05);ax.axhspan(-3,-0.5,color="#1f77b4",alpha=.05)
ax.text(2018.2,0.62,"El Niño",fontsize=8,color="#d62728");ax.text(2018.2,-0.72,"La Niña",fontsize=8,color="#1f77b4")
ax.plot(yr[m],ni[m],color="#111",lw=2,label="observed NINO3.4 (truth, to Feb 2026)")
ax.axvline(now,color="green",lw=1.5,ls="--");ax.text(now+0.05,2.0,"NOW\n(Feb 2026)",fontsize=8,color="green")
ax.plot(fyr,fproj,color="#7a5195",lw=1.6,ls=":",label="engine-clock shape (geometry, anchored to now)")
ax.plot(fyr,fproj_e,color="#d62728",lw=2.2,label="forecast: engine + WWV recharge")
ax.fill_between(fyr,fproj_e-band,fproj_e+band,color="#d62728",alpha=.13,label="uncertainty (grows w/ horizon)")
ax.scatter([now],[last],color="green",zorder=6,s=30)
ax.set_ylabel("NINO3.4 anomaly (°C)");ax.set_ylim(-1.6,2.4)
ax.set_title("ENSO forecast from Feb 2026 — observed → cutoff → projection (line now connects at NOW)\nDIRECTION only; magnitude = ARA-1.0 barrier, NOT a 'super' call",fontweight="bold",fontsize=10.5)
ax.legend(fontsize=8.5,loc="upper left");ax.grid(alpha=.2)
wm=wyr>=2018
ax2.axhline(0,color="k",lw=.6)
ax2.fill_between(wyr[wm],0,chz[wm],where=chz[wm]>=0,color="#d62728",alpha=.35)
ax2.fill_between(wyr[wm],0,chz[wm],where=chz[wm]<0,color="#1f77b4",alpha=.35)
ax2.plot(wyr[wm],chz[wm],color="#222",lw=1.5);ax2.axvline(now,color="green",lw=1.5,ls="--")
ax2.annotate(f"charging +{wwv_now:.1f}σ (Apr 2026)\n= warm event LOADING",(wyr[-1],chz[-1]),(2021.3,1.3),fontsize=8.5,color="#d62728",arrowprops=dict(arrowstyle="->",color="#d62728"))
ax2.set_ylabel("WWV charge (z)");ax2.set_xlabel("year");ax2.set_title("Subsurface warm-water volume — the energy reservoir (leads SST)",fontweight="bold",fontsize=9.5)
ax2.set_xlim(2018,2029);ax2.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_forecast_feb2026.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved (anchored)",out)
