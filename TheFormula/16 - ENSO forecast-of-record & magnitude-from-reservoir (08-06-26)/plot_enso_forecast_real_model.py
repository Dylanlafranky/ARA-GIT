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
SOI=B.load_soi("soi.data");PDO=B.load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat");IOD=load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
# align on NINO+SOI+WWV+PDO (drop IOD - missing late); extend NINO to Feb2026
ck=sorted(set(W)&set(E)&set(nino)&set(SOI)&set(PDO))
ni=np.array([nino[k] for k in ck]);SOIr=np.array([SOI[k] for k in ck]);PDOr=np.array([PDO[k] for k in ck])
charge=np.array([W[k]+E[k] for k in ck]);n=len(ni);cut=n
yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in ck])
print(f"aligned to {ck[-1]} n={n}; NINO last {ni[-1]:+.2f}")
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold)
zc=(charge-charge.mean())/charge.std();dch=charge-np.concatenate([[charge[0]],charge[:-1]]);zd=(dch-dch.mean())/dch.std()
einp_c=2.0-(1+np.tanh(zc/2));einp_d=2.0-(1+np.tanh(zd/2))   # 2 - energy ARA
zS=(SOIr-SOIr.mean())/SOIr.std();zP=(PDOr-PDOr.mean())/PDOr.std()
lags=[1,2,3,6,12,24,48]
def ridge(X,y,Xt,p=0.2):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
# REAL ARA model: clock(phase) + AR lags + feeders(SOI,PDO) + 2-ARA energy(charge,shift). Forecast h=1..28 from last origin.
o0=n-1
H=np.arange(1,29);fc=[]
for h in H:
    fp=th+2*np.pi*h/55.0
    def feat(idx):
        return np.column_stack([np.array([[ni[t-l] for l in lags] for t in idx]),
            Ago[idx]*np.cos(fp[idx]),Ago[idx]*np.sin(fp[idx]),zS[idx],zP[idx],einp_c[idx],einp_d[idx]])
    tr=np.arange(60,n-h);d=ni[tr+h]-ni[tr]
    pred=ni[o0]+ridge(feat(tr),d,feat(np.array([o0])))[0]
    fc.append(pred)
fc=np.array(fc);fyr=yr[o0]+H/12
# plot
fig,ax=plt.subplots(figsize=(13,5.5));fig.patch.set_facecolor("white")
m=yr>=2018
ax.axhline(0,color="k",lw=.7);ax.axhspan(0.5,3,color="#d62728",alpha=.05);ax.axhspan(-3,-0.5,color="#1f77b4",alpha=.05)
ax.plot(yr[m],ni[m],color="#111",lw=1.8,label="observed NINO3.4 (truth)")
ax.axvline(yr[o0],color="green",lw=1.5,ls="--");ax.text(yr[o0]+0.04,1.8,f"NOW\n({ck[-1][:4]}-{ck[-1][4:]})",fontsize=8,color="green")
ax.plot(fyr,fc,color="#d62728",lw=2,marker="o",ms=3,label="ACTUAL ARA model forecast\n(clock + AR + SOI/PDO feeders + 2−ARA energy)")
ax.scatter([yr[o0]],[ni[o0]],color="green",zorder=6,s=30)
ax.set_ylabel("NINO3.4 anomaly (°C)");ax.set_xlabel("year");ax.set_ylim(-1.6,2.2)
ax.set_title("ENSO forecast — the ACTUAL ARA framework run forward (not a single sine)\nstill smoother than truth past ~1yr = the unpredictable ARA-1.0 residual; DIRECTION not magnitude",fontweight="bold",fontsize=10.5)
ax.legend(fontsize=8.5,loc="upper left");ax.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_forecast_REAL_model.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
print("forecast (3,6,9,12,18,24mo):",[round(fc[i],2) for i in [2,5,8,11,17,23]])
