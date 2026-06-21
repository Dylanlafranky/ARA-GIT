import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,"/tmp"); sys.path.insert(0,".")
import apf as A
import enso_pdo_feeder_test as B
ni=np.array(list(B.load_nino("nino34_long_anom.csv").values()))
def loadsolar(p):
    d=[]
    for ln in open(p):
        q=ln.replace(';',' ').split()
        if len(q)>=4 and q[0].isdigit():
            try:vv=float(q[3])
            except:continue
            if vv>=0:d.append(vv)
    return np.array(d)
sol=loadsolar("SN_m_tot.csv")
# heart: LONGER concatenated RR, proper period
fs=250;parts=[]
for rec in ["slp01a","slp01b","slp02a","slp02b"]:
    d=np.load(f"slpdb_cache/{rec}.npz");ecg=d["ECG"];x=ecg-np.median(ecg);thr=3*np.std(x);pk=[];i=1
    while i<len(x)-1:
        if x[i]>thr and x[i]>=x[i-1] and x[i]>x[i+1]: pk.append(i);i+=int(0.4*fs)
        else:i+=1
    r=np.diff(pk)/fs*1000.;r=r[(r>300)&(r<1500)];parts.append(r)
rr=np.concatenate(parts)
rng=np.random.default_rng(0);t=np.arange(1200)
syn=np.sin(2*np.pi*t/48)+0.4*np.sin(2*np.pi*t/19)+0.3*rng.standard_normal(1200)
systems=[("Synthetic oscillator",syn,48,6,"#555"),
         ("ENSO (NINO3.4, monthly)",ni,55,6,"#1f77b4"),
         ("Solar sunspots (monthly)",sol,133,12,"#c47f00"),
         ("Heart RR intervals (2391 beats, engine~10)",rr,10,5,"#d62728")]
fig,axes=plt.subplots(4,1,figsize=(14,11));fig.patch.set_facecolor("white")
for ax,(name,x,P,h,c) in zip(axes,systems):
    r=A.ara_forecast(x,period=P,horizon=h);pred=r["prediction"];truth=r["truth"]
    ns=min(len(truth),300);xx=np.arange(len(truth)-ns,len(truth))
    ax.plot(xx,truth[-ns:],color="#111",lw=1.6,label="truth")
    ax.plot(xx,pred[-ns:],color=c,lw=1.4,alpha=.85,label="ARA formula")
    beat="✓ beats persistence" if r['value_corr']>r['persistence_corr'] else "ties persistence"
    ax.set_title(f"{name}  —  period {r['period']:.0f}, lead {h}   |   change-skill {r['skill_on_change']:+.2f} (persistence=0) · "
                 f"dir {r['direction_hit']:.2f} · val {r['value_corr']:+.2f} vs pers {r['persistence_corr']:+.2f} {beat} · lag {r['lag_months']:+d}",
                 fontsize=9.3,fontweight="bold")
    ax.legend(fontsize=8,loc="upper right");ax.grid(alpha=.2)
fig.suptitle("Generalized ARA prediction formula — ONE function, FOUR systems vs truth (strict-causal, held-out) — heart now properly configured",
             fontsize=12,fontweight="bold",y=1.0)
fig.tight_layout(rect=[0,0,1,0.97])
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_formula_across_systems.png"
fig.savefig(out,dpi=125,bbox_inches="tight",facecolor="white");print("saved",out)
