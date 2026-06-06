import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
PHI=F.PHI

# ---------- logged session numbers (correlation vs horizon) ----------
H_short=[3,6,9,12,15,18,24,36,48,60,72]
val={  # corr vs h ; None where not run at that h
 "home_ar (AR memory)":   [.816,.543,.272,.133,.083,.087,-.006,-.019,-.005,.057,-.066],
 "lag-harmonic-ridge":    [.812,.535,.266,.134,.082,.084,-.001,-.021,-.001,.056,-.067],
 "stable ARA":            [.807,.538,.339,.298,.237,.160,-.019,.087,-.078,-.011,-.000],
 "G3-A geometry-native":  [.807,.573,.385,.319,.235,.146,-.047,.033,-.078,-.040,-.035],
 "G3-A + PDO above":      [.806,.571,.384,.319,.235,.146,-.048,None,None,None,None],
 "G3-A + PDO 5:1":        [.798,.543,.362,.319,.237,.159,.025,None,None,None,None],
 "G3-A + solar above":    [.802,.550,.349,.279,None,.156,-.004,.056,-.041,.029,.037],
}
# spin-lock feeders: logged h=3 best of all = +0.834 (only short-horizon point we have)
spinlock={3:.834}

# direction result
Hd=[6,12,18,24,36,48,60]
pump_dir=[.614,.666,.727,.736,.662,.620,.641]
goldproj_dir=[.606,.692,.732,.749,.662,.645,.636]
persist_dir=[.500,.453,.445,.409,.450,.412,.475]

# ---------- recompute the gold-engine-phase prediction vs truth for the overlay ----------
def load_nino(p,miss=-99.99):
    d={}
    for ln in open(p):
        s=[x.strip() for x in ln.split(",")]
        if len(s)==2 and s[0][:4].isdigit():
            v=float(s[1])
            if v>miss+1e-3: d[s[0][:7].replace("-","")]=(v,s[0][:7])
    return d
raw=load_nino("/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/TheFormula/Claude4.8/nino34_long_anom.csv")
keys=list(raw.keys()); ni=np.array([raw[k][0] for k in keys]); n=len(ni)
yrs=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
Pgold=55.0; gold=F.causal_bandpass(ni,Pgold,0.25)
v=gold-np.concatenate([[gold[0]],gold[:-1]]); om=2*np.pi/Pgold
Ago=np.sqrt(gold*gold+(v/om)**2); thgo=np.arctan2(-v/om,gold)
def ctrail(x,w):
    o=np.full(len(x),np.nan)
    for i in range(len(x)):
        a=x[max(0,i-w+1):i+1]
        if len(a)>=6: o[i]=np.mean(a)
    return o
L=ctrail(ni,48); cut=int(n/PHI)
hh=18; te=np.arange(cut,n-hh)
pred=L[te]+Ago[te]*np.cos(thgo[te]+2*np.pi*hh/Pgold)
truth=ni[te+hh]; tgt_yr=yrs[te+hh]

# =================== PLOT ===================
fig=plt.figure(figsize=(15,11)); fig.patch.set_facecolor("white")
gs=fig.add_gridspec(2,2,height_ratios=[1,1],hspace=0.33,wspace=0.22)

# Panel A: value skill vs horizon
axA=fig.add_subplot(gs[0,0])
styles={"home_ar (AR memory)":("#888","--"),"lag-harmonic-ridge":("#bbab00",":"),
 "stable ARA":("#1f77b4","-"),"G3-A geometry-native":("#d62728","-"),
 "G3-A + PDO above":("#2ca02c","-."),"G3-A + PDO 5:1":("#17becf","-."),
 "G3-A + solar above":("#9467bd","-.")}
for name,ys in val.items():
    c,ls=styles[name]; xs=[h for h,y in zip(H_short,ys) if y is not None]; yy=[y for y in ys if y is not None]
    axA.plot(xs,yy,ls,color=c,lw=2 if name in("stable ARA","G3-A geometry-native") else 1.4,
             marker="o",ms=3,label=name)
axA.scatter([3],[spinlock[3]],color="k",zorder=6,s=45,marker="*")
axA.annotate("spin-lock feeders\n(best @h=3, +0.834)",(3,.834),(6,.86),fontsize=8,color="k",
             arrowprops=dict(arrowstyle="->",color="k"))
axA.axhline(0,color="k",lw=.8); axA.axvspan(36,72,color="grey",alpha=.10)
axA.text(54,.45,"predictability\nfloor (~0)\nbeyond ~36mo",ha="center",fontsize=8,color="#555")
axA.set_title("A. Point-VALUE skill vs horizon (ENSO)",fontweight="bold")
axA.set_xlabel("forecast horizon (months)"); axA.set_ylabel("correlation vs truth")
axA.legend(fontsize=7.2,loc="upper right",framealpha=.9); axA.grid(alpha=.25); axA.set_ylim(-.2,.95)

# Panel B: direction hit-rate vs horizon
axB=fig.add_subplot(gs[0,1])
axB.plot(Hd,pump_dir,"-o",color="#d62728",lw=2,label="crossing-pump (direction)")
axB.plot(Hd,goldproj_dir,"--s",color="#1f77b4",lw=2,label="gold-engine phase (control)")
axB.plot(Hd,persist_dir,":^",color="#888",lw=1.6,label="persistence direction")
axB.axhline(0.5,color="k",lw=1,ls="-"); axB.text(60,.51,"chance 0.50",fontsize=8,ha="right")
axB.axvspan(18,24,color="#d62728",alpha=.08)
axB.annotate("~0.73–0.74 @18–24mo\nwhile VALUE is floored",(24,.736),(30,.80),fontsize=8.5,
             color="#d62728",arrowprops=dict(arrowstyle="->",color="#d62728"))
axB.set_title("B. DIRECTION hit-rate vs horizon — the key win",fontweight="bold")
axB.set_xlabel("forecast horizon (months)"); axB.set_ylabel("fraction of swings called correctly")
axB.legend(fontsize=8,loc="lower left"); axB.grid(alpha=.25); axB.set_ylim(.38,.85)

# Panel C: predicted vs truth overlay (gold-engine phase, h=18) — last ~40yr
axC=fig.add_subplot(gs[1,:])
mask=tgt_yr>=1985
axC.plot(tgt_yr[mask],truth[mask],color="#222",lw=1.6,label="truth (NINO3.4 anomaly)")
axC.plot(tgt_yr[mask],pred[mask],color="#d62728",lw=1.6,alpha=.85,label="gold-engine phase prediction (18-mo lead)")
axC.axhline(0,color="k",lw=.7)
# shade where direction agrees
agree=np.sign(pred[mask]-truth[mask]*0 ) # placeholder
axC.fill_between(tgt_yr[mask],truth[mask],pred[mask],
                 where=(np.sign(np.diff(np.concatenate([[truth[mask][0]],truth[mask]])))==
                        np.sign(np.diff(np.concatenate([[pred[mask][0]],pred[mask]])))),
                 color="#d62728",alpha=.06)
axC.set_title("C. Predicted vs truth — gold-engine-phase call at 18-month lead (literal 'vs truth'; value corr~0 but turns/direction track)",
              fontweight="bold",fontsize=10.5)
axC.set_xlabel("year"); axC.set_ylabel("NINO3.4 anomaly (°C)")
axC.legend(fontsize=9,loc="upper right"); axC.grid(alpha=.25)

fig.suptitle("ARA session arc on ENSO: every method vs truth — value collapses past ~36mo, but DIRECTION stays ~0.73 at 18–24mo",
             fontsize=13,fontweight="bold",y=0.985)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/TheFormula/ARA_session_methods_vs_truth.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white")
print("saved",out)
