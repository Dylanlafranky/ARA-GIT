"""Strict-causal test: do the HEART's own sub-beat subsystems lift the h=3-8 dip?

We reuse the SAME layered operator (ara_unified_layered_framework_test) and the SAME
slp01a record. Baseline = external feeders only (BP/Resp/EEG means). Then we add
INTERNAL sub-beat morphology features extracted from the raw ECG and BP waveform of
EACH beat (so feature at beat i uses only beat i's waveform = causal). We compare
out-of-sample correlation vs persistence at every horizon, focusing on h=3,5,8.
"""
import json, numpy as np
from numpy import nan
from scipy.signal import find_peaks
import ara_unified_layered_framework_test as U
from ara_unified_layered_framework_test import System, Contact, evaluate

FS = 250.0

def load_beats():
    sig = np.load("slp01a_sig.npy").astype(float)
    names = json.loads(open("slp01a_names.json").read())
    ch = {n:i for i,n in enumerate(names)}
    ecg = sig[:, ch["ECG"]]; bp = sig[:, ch["BP"]]
    eeg = sig[:, ch["EEG (C4-A1)"]]; resp = sig[:, ch["Resp (sum)"]]
    dist = int(0.4*FS); prom = 0.4*np.std(ecg)
    pks,_ = find_peaks(ecg, distance=dist, prominence=prom)
    pks = pks[(pks>1)&(pks<len(ecg)-1)]
    rr = np.diff(pks)/FS*1000.0
    nb = len(pks)-1
    # external feeders (means over each beat) -- the current model
    bp_mean   = np.array([bp[pks[i]:pks[i+1]].mean()  for i in range(nb)])
    resp_mean = np.array([resp[pks[i]:pks[i+1]].mean() for i in range(nb)])
    eeg_mean  = np.array([eeg[pks[i]:pks[i+1]].mean() for i in range(nb)])
    # INTERNAL sub-beat morphology (heart's own subsystems), per beat, causal
    ecg_qt=np.full(nb,nan); ecg_cen=np.full(nb,nan); ecg_amp=np.full(nb,nan)
    bp_sys=np.full(nb,nan); bp_pp=np.full(nb,nan)
    for i in range(nb):
        w = ecg[pks[i]:pks[i+1]]; L=len(w)
        if L<10: continue
        # electrical systole proxy: T-wave location as fraction of RR (after QRS, before next P)
        a,b=int(0.10*L),max(int(0.55*L),int(0.10*L)+2)
        seg=w[a:b]
        if len(seg)>1:
            ecg_qt[i]=(a+int(np.argmax(np.abs(seg-np.median(w)))))/L
        # within-beat energy centroid (where the electrical energy sits = within-beat ARA)
        e=(w-np.mean(w))**2; s=e.sum()
        if s>0: ecg_cen[i]=float(np.dot(np.arange(L),e)/s)/L
        ecg_amp[i]=float(w.max()-w.min())
        wb=bp[pks[i]:pks[i+1]]
        if len(wb)>2:
            bp_sys[i]=float(np.argmax(wb))/len(wb)   # mechanical systole upstroke timing
            bp_pp[i]=float(wb.max()-wb.min())        # pulse pressure
    # clean RR (ectopics/misses); apply SAME mask to all
    med=np.median(rr); good=(rr>0.4*med)&(rr<1.8*med)
    def m(x): return x[good]
    return dict(rr=m(rr), bp_mean=m(bp_mean), resp_mean=m(resp_mean), eeg_mean=m(eeg_mean),
                ecg_qt=m(ecg_qt), ecg_cen=m(ecg_cen), ecg_amp=m(ecg_amp),
                bp_sys=m(bp_sys), bp_pp=m(bp_pp))

def fill(x):
    x=np.asarray(x,float)
    # causal-safe fill of rare NaNs by forward fill then median (does not use future beyond ffill)
    med=np.nanmedian(x)
    out=x.copy(); last=med
    for i in range(len(out)):
        if np.isfinite(out[i]): last=out[i]
        else: out[i]=last
    return out

def make_system(name, d, lower, upper):
    return System(name=name, unit="beat", home=d["rr"], home_period=8.0,
                  horizons=(1,3,5,8,13), home_lags=(0,1,2,3,4,5,8,13),
                  lower=tuple(lower), upper=tuple(upper))

def main():
    d=load_beats()
    for k in ["bp_mean","resp_mean","eeg_mean","ecg_qt","ecg_cen","ecg_amp","bp_sys","bp_pp"]:
        d[k]=fill(d[k])
    print(f"[beats after clean] {len(d['rr'])}  median RR {np.median(d['rr']):.0f} ms")
    ext_lower=[Contact("BP fast", d["bp_mean"],1.0,8,1), Contact("Resp", d["resp_mean"],4.0,8,1)]
    ext_upper=[Contact("EEG slow", d["eeg_mean"],13.0,13,1)]
    int_lower=[Contact("ECG QT systole", d["ecg_qt"],1.0,8,1),
               Contact("ECG energy centroid", d["ecg_cen"],1.0,8,2),
               Contact("BP systole upstroke", d["bp_sys"],1.0,8,1),
               Contact("ECG amplitude", d["ecg_amp"],2.0,8,2),
               Contact("BP pulse pressure", d["bp_pp"],2.0,8,2)]
    systems={
      "EXTERNAL only (current model)": make_system("ext", d, ext_lower, ext_upper),
      "INTERNAL sub-beat only":        make_system("int", d, int_lower, ext_upper),
      "BOTH (external + internal)":     make_system("both", d, ext_lower+int_lower, ext_upper),
    }
    print(f"\n{'horizon':>22} | {'persist':>8} {'roll_readout':>13} {'home+ara':>10}")
    store={}
    for label,sysm in systems.items():
        res=evaluate(sysm); store[label]=res
        print(f"\n-- {label} --")
        for h,sc in res["horizons"].items():
            p=sc["persistence"]["corr"]; rr=sc["ara_roll_readout"]["corr"]; ha=sc["home_plus_ara"]["corr"]
            star=" <== DIP" if h in("3","5","8") else ""
            print(f"{('h='+h+' beats'):>22} | {p:+.3f}   {rr:+.3f}        {ha:+.3f}{star}")
    # focused dip summary
    print("\n=== DIP (h=3,5,8): best framework model corr minus persistence ===")
    for h in ("3","5","8"):
        line=f"h={h}: "
        pers=store["EXTERNAL only (current model)"]["horizons"][h]["persistence"]["corr"]
        line+=f"persist {pers:+.3f} | "
        for label in systems:
            best=max(store[label]["horizons"][h][m]["corr"] for m in
                     ("ara_fixed_roll","ara_roll_readout","home_ar","home_plus_ara"))
            line+=f"{label.split()[0]} {best:+.3f}(Δ{best-pers:+.3f})  "
        print(line)
    json.dump({l:r for l,r in store.items()}, open("heart_subsystem_dip_result.json","w"), indent=2, default=float)
    print("\nwrote heart_subsystem_dip_result.json")

if __name__=="__main__":
    main()
