import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,"/tmp"); sys.path.insert(0,".")
import apf as A
import enso_pdo_feeder_test as B
ni=np.array(list(B.load_nino("nino34_long_anom.csv").values()))
H=list(range(1,73))
chg=[];val=[]
for h in H:
    r=A.ara_forecast(ni,period=55,horizon=h)
    if "error" in r: chg.append(np.nan);val.append(np.nan);continue
    chg.append(r["skill_on_change"]);val.append(r["value_corr"])
chg=np.array(chg);val=np.array(val)
print("Does coherence RETURN at one engine cycle (~55mo)?  change-skill by horizon:")
for h in [6,12,18,24,30,36,42,48,55,60,66,72]:
    if h<=len(chg): print(f"  {h:>3}mo: change-skill {chg[h-1]:+.2f}  value-corr {val[h-1]:+.2f}")
fig,ax=plt.subplots(figsize=(13,5.5));fig.patch.set_facecolor("white")
ax.axhline(0,color="k",lw=.6)
ax.axvspan(20,36,color="grey",alpha=.10);ax.text(28,0.05,"decoherence\nwall",ha="center",fontsize=8,color="#555")
ax.axvline(55,color="#c47f00",lw=1.2,ls="--");ax.text(55.5,0.7,"one engine\ncycle (55mo)",fontsize=8,color="#c47f00")
ax.plot(H,chg,"o-",color="#1f77b4",lw=2,ms=3,label="shape/direction skill (change-corr)")
ax.plot(H,val,"s-",color="#888",lw=1.2,ms=2,alpha=.7,label="value correlation")
ax.set_xlabel("forecast horizon (months)");ax.set_ylabel("skill");ax.grid(alpha=.2);ax.legend(fontsize=9)
ax.set_title("ENSO forecast skill past the wall — does the prediction window REOPEN at one engine cycle?\n(strict-causal, universal ARA formula, horizons 1-72 months)",fontweight="bold",fontsize=10.5)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_second_window.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
