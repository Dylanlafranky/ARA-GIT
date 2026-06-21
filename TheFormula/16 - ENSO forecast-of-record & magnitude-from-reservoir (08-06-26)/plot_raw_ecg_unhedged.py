import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,"/tmp"); sys.path.insert(0,".")
import apf as A
d=np.load("slpdb_cache/slp01a.npz");ecg=d["ECG"].astype(float)
ds=5;e=ecg[::ds];fs=250/ds;n=len(e)
x=e-e.mean();X=np.abs(np.fft.rfft(x*np.hanning(n)))**2;f=np.fft.rfftfreq(n,1.0)
per=np.where(f>0,1/f,np.inf);bb=(per>=20)&(per<=80);P=per[bb][np.argmax(X[bb])]
h=5  # 100 ms lead
r=A.ara_forecast(e,period=P,horizon=h)
pred=r["prediction"];warn=r["warning"];truth=r["truth"]
def cc(a,b):return np.corrcoef(a,b)[0,1]
def amp(p):
    L=A._trail_mean(e,int(P))[r["test_index"]];return np.std(p-L)/np.std(truth-L)
print(f"RAW ECG {h*1000/fs:.0f}ms lead — change-skill {r['skill_on_change']:+.3f}  hedged-amp {r['amp_ratio']:.2f}  warning-amp {r['warning_amp_ratio']:.2f}")
fig,(a1,a2)=plt.subplots(2,1,figsize=(14,7.5),sharex=True);fig.patch.set_facecolor("white")
w0=600;ns=int(10*fs);t=np.arange(ns)/fs
for ax,(nm,p,c) in zip((a1,a2),[("HEDGED (best estimate — damps the QRS spikes)",pred,"#7a5195"),
                                ("UN-HEDGED (full amplitude — reaches the real spike heights)",warn,"#2ca02c")]):
    ax.plot(t,truth[w0:w0+ns],color="#111",lw=1.6,label="raw ECG (truth)")
    ax.plot(t,p[w0:w0+ns],color=c,lw=1.3,alpha=.85,label="ARA forecast")
    ax.set_title(f"{nm}",fontweight="bold",fontsize=10.5)
    ax.set_ylabel("ECG (raw units)");ax.legend(fontsize=9,loc="upper right");ax.grid(alpha=.2)
a2.set_xlabel("seconds (held-out test window)")
fig.suptitle(f"RAW ECG waveform, {h*1000/fs:.0f} ms ahead — universal ARA formula, HEDGED vs UN-HEDGED (strict-causal, held-out)\n"
             f"change-skill {r['skill_on_change']:+.2f} · hedged amp {r['amp_ratio']:.2f} vs un-hedged amp {r['warning_amp_ratio']:.2f}",
             fontsize=11.5,fontweight="bold",y=1.0)
fig.tight_layout(rect=[0,0,1,0.94])
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_raw_ecg_unhedged.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
