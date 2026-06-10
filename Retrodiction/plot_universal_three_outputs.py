import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,"/tmp"); sys.path.insert(0,".")
import apf as A
import enso_pdo_feeder_test as B
keys=sorted(B.load_nino("nino34_long_anom.csv"));d=B.load_nino("nino34_long_anom.csv")
ni=np.array([d[k] for k in keys]);yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
# THE UNIVERSAL FORMULA — one call, nothing bolted on
r=A.ara_forecast(ni, period=55, horizon=6)
pred=r["prediction"];warn=r["warning"];conf=r["confidence"];truth=r["truth"];te=r["test_index"]
ty=yr[te]+6/12
print(f"universal ara_forecast on ENSO: change-skill {r['skill_on_change']:+.3f}  val {r['value_corr']:+.3f}  "
      f"pers {r['persistence_corr']:+.3f}  amp {r['amp_ratio']:.2f}  warn-amp {r['warning_amp_ratio']:.2f}  lag {r['lag_months']:+d}")
fig,ax=plt.subplots(figsize=(14,6));fig.patch.set_facecolor("white")
m=ty>=2000
ax.axhline(0,color="k",lw=.6);ax.axhline(0.5,color="#d62728",lw=.8,ls=":");ax.axhline(-0.5,color="#1f77b4",lw=.8,ls=":")
ax.text(2000.3,0.57,"El Nino",fontsize=7,color="#d62728");ax.text(2000.3,-0.66,"La Nina",fontsize=7,color="#1f77b4")
ax.fill_between(ty[m],pred[m]-conf[m],pred[m]+conf[m],color="grey",alpha=.18,label="confidence band (how sure)")
ax.plot(ty[m],truth[m],color="#111",lw=2,label="truth",zorder=5)
ax.plot(ty[m],pred[m],color="#7a5195",lw=1.6,label="best estimate (accurate, slightly late)")
ax.plot(ty[m],warn[m],color="#2ca02c",lw=1.2,ls="--",alpha=.9,label="early warning (full amplitude / how big)")
ax.set_xlabel("year");ax.set_ylabel("NINO3.4 (deg C)");ax.set_ylim(-2.6,3.2)
ax.set_title("ENSO 6-mo forecast — the SAME universal ara_forecast() formula, three outputs it returns itself\n(prediction / warning / confidence) · strict-causal, held-out · nothing bolted on",fontweight="bold",fontsize=10.5)
ax.legend(fontsize=8.5,loc="upper left");ax.grid(alpha=.2)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_universal_formula_three_outputs.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
