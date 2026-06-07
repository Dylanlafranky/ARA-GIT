import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
PHI=F.PHI
W=B.load_wwv("wwv_west.dat");E=B.load_wwv("wwv_east.dat");nino=B.load_nino("nino34_long_anom.csv")
SOI=B.load_soi("soi.data");PDO=B.load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")
# extend NINO with CPC ONI 2026 so the anchor is current
nino=dict(nino); nino["202601"]=-0.37; nino["202602"]=-0.16
ck=sorted(set(W)&set(E)&set(nino)&set(SOI)&set(PDO))
ni=np.array([nino[k] for k in ck]);SOIr=np.array([SOI[k] for k in ck]);PDOr=np.array([PDO[k] for k in ck])
charge=np.array([W[k]+E[k] for k in ck]);n=len(ni);cut=int(n/PHI)
yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in ck])
print(f"aligned to {ck[-1]} n={n} last NINO {ni[-1]:+.2f}")
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold)
zc=(charge-charge[:cut].mean())/charge[:cut].std();dch=charge-np.concatenate([[charge[0]],charge[:-1]]);zd=(dch-dch[:cut].mean())/dch[:cut].std()
einp_c=2-(1+np.tanh(zc/2));einp_d=2-(1+np.tanh(zd/2))
zS=(SOIr-SOIr[:cut].mean())/SOIr[:cut].std();zP=(PDOr-PDOr[:cut].mean())/PDOr[:cut].std()
lags=[1,2,3,6,12,24,48]
def ridge(X,y,Xt,p=0.2):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
def feat(idx,h):
    fp=th+2*np.pi*h/55.0
    return np.column_stack([np.array([[ni[t-l] for l in lags] for t in idx]),
        Ago[idx]*np.cos(fp[idx]),Ago[idx]*np.sin(fp[idx]),zS[idx],zP[idx],einp_c[idx],einp_d[idx]])
# HINDCAST reference: causal 6-mo ARA forecast, train pre-cut, applied across the record (target = origin+6)
h=6;tr=np.arange(60,cut-h);d=ni[tr+h]-ni[tr]
allo=np.arange(60,n-h)
hind_pred=ni[allo]+ridge(feat(tr,h),d,feat(allo,h))   # predicts NINO at allo+h
hind_tyr=yr[allo]+h/12
hcorr=np.corrcoef(hind_pred[allo>=cut],ni[allo+h][allo>=cut])[0,1]
# FORWARD: multi-horizon trajectory from last origin
o0=n-1;H=np.arange(1,29);fc=[]
for hh in H:
    trh=np.arange(60,n-hh);dh=ni[trh+hh]-ni[trh]
    fc.append(ni[o0]+ridge(feat(trh,hh),dh,feat(np.array([o0]),hh))[0])
fc=np.array(fc);fyr=yr[o0]+H/12
# PLOT
fig,ax=plt.subplots(figsize=(14,6));fig.patch.set_facecolor("white")
m=yr>=2010
ax.axhline(0,color="k",lw=.7);ax.axhspan(0.5,3,color="#d62728",alpha=.04);ax.axhspan(-3,-0.5,color="#1f77b4",alpha=.04)
ax.plot(yr[m],ni[m],color="#111",lw=1.8,label="observed NINO3.4 (truth)")
hm=hind_tyr>=2010
ax.plot(hind_tyr[hm],hind_pred[hm],color="#1f77b4",lw=1.5,alpha=.85,label=f"ARA framework — 6-mo causal hindcast (reference, corr {hcorr:+.2f})")
ax.axvline(yr[o0],color="green",lw=1.5,ls="--");ax.text(yr[o0]+0.05,1.9,f"NOW\n({ck[-1][:4]}-{ck[-1][4:]})",fontsize=8,color="green")
ax.plot(fyr,fc,color="#d62728",lw=2.2,marker="o",ms=3,label="ARA framework — forward forecast")
ax.scatter([yr[o0]],[ni[o0]],color="green",zorder=6,s=30)
ax.set_ylabel("NINO3.4 anomaly (°C)");ax.set_xlabel("year");ax.set_ylim(-1.7,2.3);ax.set_xlim(2010,2029)
ax.set_title("ENSO — ARA framework (engine clock + AR + SOI/PDO feeders + 2−ARA energy)\nblue = ARA tracking truth over history (reference) · red = ARA forward forecast · DIRECTION not magnitude",fontweight="bold",fontsize=10.5)
ax.legend(fontsize=8.5,loc="upper left");ax.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_forecast_with_hindcast_reference.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
print(f"hindcast test corr@6mo={hcorr:.3f}; fwd(6,12,24mo)={[round(fc[i],2) for i in [5,11,23]]}")
