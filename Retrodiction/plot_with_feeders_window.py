import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,"/tmp"); sys.path.insert(0,".")
import apf as A
import enso_pdo_feeder_test as B
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
ck=sorted(set(W)&set(E)&set(nino)&set(SOI)&set(PDO)&set(IOD));arr=lambda d:np.array([d[k] for k in ck])
ni=arr(nino);n=len(ni);P=55.;om=2*np.pi/P;cut=int(n/A.PHI)
print(f"feeder-era aligned {n} months {ck[0]}..{ck[-1]}")
gold=A._causal_bandpass(ni,P,0.25);v=gold-np.concatenate([[gold[0]],gold[:-1]]);Ago=np.sqrt(gold**2+(v/om)**2);th=np.arctan2(-v/om,gold)
rz=(A._trail_mean(-ni,max(3,int(P/6)))-0);rz=(rz-rz.mean())/(rz.std()+1e-9);ask=A._trail_skew(ni,max(8,int(P/3)))
WWV=arr(W)+arr(E);SOIr=arr(SOI);IODr=arr(IOD);PDOr=arr(PDO)
home_lags=[l for l in [1,2,3,6,12,int(round(P/4)),int(round(P/2)),int(round(P))] if 0<l<n//3];start=max(home_lags)+2
def feat(o,h,feed):
    fp=th+2*np.pi*h/P
    c=[np.array([[ni[t-l] for l in home_lags] for t in o]),Ago[o]*np.cos(fp[o]),Ago[o]*np.sin(fp[o]),rz[o],ask[o],rz[o]*Ago[o]]
    if feed: c+=[WWV[o],SOIr[o],IODr[o],PDOr[o]]   # the documented feeder set
    return np.column_stack(c)
def run(h,feed):
    o=np.arange(start,n-h);tr=o[o+h<cut];te=o[o>=cut];d=ni[tr+h]-ni[tr]
    p=ni[te]+A._ridge(feat(tr,h,feed),d,feat(te,h,feed))
    return np.corrcoef(p,ni[te+h])[0,1], np.corrcoef(p-ni[te],ni[te+h]-ni[te])[0,1]
H=[1,3,6,9,12,18,24,30,36,48,55]
vb=[];vf=[];cf=[]
print(f"{'h':>4}{'no-feeder val':>15}{'+FEEDER val':>13}{'+feeder change':>16}")
for h in H:
    a,_=run(h,False);b,bc=run(h,True);vb.append(a);vf.append(b);cf.append(bc)
    print(f"{h:>4}{a:>15.3f}{b:>13.3f}{bc:>16.3f}")
fig,ax=plt.subplots(figsize=(13,5.5));fig.patch.set_facecolor("white")
ax.axhline(0,color="k",lw=.6);ax.axhspan(.6,.7,color="grey",alpha=.12);ax.text(50,.66,"operational ~0.6-0.7",fontsize=8,ha="right")
ax.plot(H,vf,"o-",color="#1f77b4",lw=2.2,label="value corr — WITH feeders (our best)")
ax.plot(H,vb,"s--",color="#aaa",lw=1.5,label="value corr — engine only (the stripped ~0.3 runs)")
ax.plot(H,cf,"^-",color="#2ca02c",lw=1.6,alpha=.8,label="change/direction skill — with feeders")
ax.set_xlabel("forecast horizon (months)");ax.set_ylabel("skill / correlation");ax.grid(alpha=.2);ax.legend(fontsize=9);ax.set_ylim(-.2,1)
ax.set_title("ENSO — universal ARA formula WITH feeders (apples-to-apples best) vs the stripped engine\nstrict-causal, feeder-era held-out · feeders ~double the value skill",fontweight="bold",fontsize=10.5)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_with_feeders_window.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
