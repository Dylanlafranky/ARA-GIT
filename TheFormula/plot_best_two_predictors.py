import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B, enso_combined_horizon_feeder as C
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
PHI=F.PHI
W=B.load_wwv("wwv_west.dat");E=B.load_wwv("wwv_east.dat");nino=B.load_nino("nino34_long_anom.csv")
SOI=B.load_soi("soi.data");PDO=B.load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat");IOD=C.load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
bk=sorted(set(W)&set(E)&set(nino)&set(SOI)&set(PDO)&set(IOD))
yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in bk])
T=np.array([nino[k] for k in bk]);Wv=np.array([W[k] for k in bk]);Ev=np.array([E[k] for k in bk])
Sv=np.array([SOI[k] for k in bk]);mon=np.array([int(k[4:6]) for k in bk])
# ===== Version 1: best CORRELATION (feeder stitch). Capture +IOD predictions @h6 =====
cols=[T,Wv,Ev,Sv,np.array([IOD[k] for k in bk])];stdz=[1,2,3,4]
rec=B.walk_switch(cols,stdz,yr,mon,T)
def series(h):
    oy=np.array(rec[h]['oy']);pr=np.array(rec[h]['pred']);tr=np.array(rec[h]['truth'])
    # build target year for each origin
    # origins are sequential from WALK_START; approximate target yr by oy + h/12
    m=oy>=2016
    return oy[m]+h/12, pr[m], tr[m]
ty6,pr6,tr6=series(6)
c6=np.corrcoef(pr6,tr6)[0,1]
# corr by horizon (stitch)
HZ=[1,3,6,9,12,15,18,24]
def evalrec(rec):
    o={}
    for h in HZ:
        oy=np.array(rec[h]['oy']);pr=np.array(rec[h]['pred']);tr=np.array(rec[h]['truth']);m=oy>=2016
        o[h]=np.corrcoef(pr[m],tr[m])[0,1] if m.sum()>5 else np.nan
    return o
stitch_corr=evalrec(rec)
# ===== Version 2: best DIRECTION (topology+clock). Build on same keyed data =====
ni=T;n=len(ni);cut=int(n*0.60)
gold=F.causal_bandpass(ni,55.0,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);om=2*np.pi/55.0
Ago=np.sqrt(gold*gold+(v/om)**2);th=np.arctan2(-v/om,gold)
def ctrail(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
L=ctrail(ni,48)
def ridge(X,y,Xt,p=0.1):
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-9]=1;A=(X-mu)/sd;Bm=(Xt-mu)/sd
    A=np.column_stack([np.ones(len(A)),A]);Bm=np.column_stack([np.ones(len(Bm)),Bm])
    R=np.eye(A.shape[1])*p;R[0,0]=0;return Bm@np.linalg.solve(A.T@A+R,A.T@y)
lags=[1,2,3,6,12,24,48]
feeds=[ni,Sv,Wv,Ev,np.array([IOD[k] for k in bk]),np.array([PDO[k] for k in bk])]
def lm(o):return np.array([[f[t-l] for f in feeds for l in lags] for t in o])
def clk(o,h):fp=th[o]+2*np.pi*h/55.0;return np.column_stack([Ago[o]*np.cos(fp),Ago[o]*np.sin(fp),np.cos(fp),np.sin(fp)])
def dirhit(h):
    o=np.arange(60,n-h);tr=o[o+h<cut];te=o[o>=cut];d=ni[tr+h]-ni[tr]
    comb=ni[te]+ridge(np.column_stack([lm(tr),clk(tr,h)]),d,np.column_stack([lm(te),clk(te,h)]))
    fe=ni[te]+ridge(lm(tr),d,lm(te))
    tdir=np.sign(ni[te+h]-ni[te])
    hp=lambda p:np.mean(np.sign(p-ni[te])[tdir!=0]==tdir[tdir!=0])
    return hp(comb),hp(fe),np.mean(np.sign(ni[te]-ni[te-3])[tdir!=0]==tdir[tdir!=0]),te,comb,ni[te+h],ni[te]
HD=[6,12,18,24,36]
dres={h:dirhit(h) for h in HD}
# value-vs-truth overlay for the combined @h18
_,_,_,te,comb18,fut18,cur18=dirhit(18)
ty18=yr[te]+18/12

# ============ PLOT ============
fig=plt.figure(figsize=(15,9));fig.patch.set_facecolor("white")
gs=fig.add_gridspec(2,2,hspace=0.32,wspace=0.2)
# V1 top: pred vs truth @h6
a=fig.add_subplot(gs[0,0]);a.axhline(0,color="k",lw=.7)
a.plot(ty6,tr6,color="#222",lw=1.6,label="truth")
a.plot(ty6,pr6,color="#1f77b4",lw=1.6,alpha=.85,label="prediction")
a.set_title(f"VERSION 1 — best CORRELATION (IOD+PDO feeder stitch)\n6-month forecast vs truth · corr = {c6:+.2f}",fontweight="bold",fontsize=11)
a.set_xlabel("year");a.set_ylabel("NINO3.4 (°C)");a.legend(fontsize=9);a.grid(alpha=.2)
# V1 bottom: corr by horizon vs industry
b=fig.add_subplot(gs[1,0])
hs=[h for h in HZ];cs=[stitch_corr[h] for h in HZ]
b.plot(hs,cs,"o-",color="#1f77b4",lw=2,label="ARA feeder stitch")
b.axhspan(0.6,0.7,color="grey",alpha=.15);b.text(20,0.66,"operational models ~0.6–0.7",fontsize=8,ha="right")
b.axhline(0.5,color="orange",ls="--",lw=1);b.text(20,0.515,"deep-learning SOTA >0.5 @16–20mo",fontsize=8,ha="right",color="#b06000")
b.set_title("Correlation vs horizon (value skill)",fontweight="bold",fontsize=10)
b.set_xlabel("forecast horizon (months)");b.set_ylabel("correlation");b.legend(fontsize=8);b.grid(alpha=.2);b.set_ylim(0,1)
# V2 top: combined value pred vs truth @h18 with sign-match shading
c=fig.add_subplot(gs[0,1]);c.axhline(0,color="k",lw=.7)
c.plot(ty18,fut18,color="#222",lw=1.6,label="truth")
c.plot(ty18,comb18,color="#d62728",lw=1.6,alpha=.85,label="prediction (18-mo)")
match=np.sign(comb18-cur18)==np.sign(fut18-cur18)
c.fill_between(ty18,fut18,comb18,where=match,color="#2ca02c",alpha=.12)
c.set_title("VERSION 2 — best DIRECTION (multi-feeder topology + engine clock)\n18-mo forecast vs truth · green = turn called right",fontweight="bold",fontsize=11)
c.set_xlabel("year");c.set_ylabel("NINO3.4 (°C)");c.legend(fontsize=9);c.grid(alpha=.2)
# V2 bottom: direction hit-rate by horizon
d=fig.add_subplot(gs[1,1])
d.plot(HD,[dres[h][0] for h in HD],"o-",color="#d62728",lw=2,label="topology + clock")
d.plot(HD,[dres[h][1] for h in HD],"s--",color="#888",lw=1.5,label="feeders only")
d.plot(HD,[dres[h][2] for h in HD],"^:",color="#aaa",lw=1.3,label="persistence")
d.axhline(0.5,color="k",lw=1);d.text(35,0.51,"chance",fontsize=8,ha="right")
d.set_title("Direction hit-rate vs horizon",fontweight="bold",fontsize=10)
d.set_xlabel("forecast horizon (months)");d.set_ylabel("fraction of turns called right");d.legend(fontsize=8);d.grid(alpha=.2);d.set_ylim(.4,.9)
fig.suptitle("ARA — our two best ENSO predictors vs truth  (strict-causal, NOAA NINO3.4 + feeders, test 2016–2025)",fontsize=13,fontweight="bold",y=0.99)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/TheFormula/ARA_best_two_predictors.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
print(f"V1 corr@6={c6:.3f}; V2 dir@24={dres[24][0]:.3f} vs feeders {dres[24][1]:.3f}")
