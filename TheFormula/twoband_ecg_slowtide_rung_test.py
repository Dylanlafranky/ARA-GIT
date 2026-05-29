# THREE-RUNG ladder, all from ONE RR series (auto-aligned, same body/clock):
#   tide (very-slow, <~0.04Hz)  ->  gold (LF)  ->  green (HF)
# Test A: does the slow TIDE gate GOLD's energy the way gold gates green?
# Test B: does adding the tide lift the strict-causal forecast of gold energy?
import numpy as np, wfdb, glob
from scipy.signal import welch, butter, sosfiltfilt, hilbert
base="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0/"
def load(rec):
    ann=wfdb.rdann(rec,'ecg'); rr=np.diff(ann.sample)/ann.fs*1000.0
    return rr[(rr>300)&(rr<2000)]
def bp(x,lo,hi):  # bandpass in beats (period), causal-safe filtfilt for descriptive
    nyq=0.5; sos=butter(4,[ (1/hi)/nyq, min((1/lo)/nyq,0.99) ],btype='band',output='sos')
    return sosfiltfilt(sos,x-x.mean())
def loud(x,b):
    f,P=welch(x,fs=1.0,nperseg=8192); per=np.divide(1.,f,out=np.full_like(f,np.inf),where=f>0)
    m=(per>=b[0])&(per<=b[1]); return per[m][np.argmax(P[m])]
def env(s): return np.abs(hilbert(s))
def corr(a,b):
    a=np.asarray(a);b=np.asarray(b)
    return float(np.corrcoef(a,b)[0,1]) if a.std() and b.std() else 0.0
def fitpred(Xtr,ytr,Xte):
    co,*_=np.linalg.lstsq(Xtr,ytr,rcond=None); return Xte@co
H=[6,12,20,30]; recs=sorted(glob.glob(base+"nsr*.hea"))[:25]
ccA=[]; G={h:[] for h in H}; GT={h:[] for h in H}; tideP=[]
for fp in recs:
    try:
        rr=load(fp[:-4]); spb=np.median(rr)/1000.0
        # bands in beats from Hz: HF .15-.40, LF .04-.15, VLF tide .0033-.04
        green=bp(rr,1/0.40/spb,1/0.15/spb)
        gold =bp(rr,1/0.15/spb,1/0.04/spb)
        tide =bp(rr,1/0.04/spb,1/0.0033/spb)
        ge=env(gold); te=env(tide); tph=np.angle(hilbert(tide))
        tper=loud(rr,(1/0.04/spb,1/0.0033/spb))
        tideP.append(tper)
        ccA.append(corr(ge,te))                       # tide loudness vs gold loudness
        n=len(rr); cut=n//2
        for h in H:
            tr=np.arange(2*int(tper),cut-h); ts=np.arange(cut,n-h)
            ytr=ge[tr+h]; yts=ge[ts+h]
            ph_tr=tph[tr]+2*np.pi*h/tper; ph_ts=tph[ts]+2*np.pi*h/tper
            Xp_tr=np.column_stack([np.ones(len(tr)),ge[tr]])
            Xp_ts=np.column_stack([np.ones(len(ts)),ge[ts]])
            Xg_tr=np.column_stack([np.ones(len(tr)),ge[tr],te[tr],np.cos(ph_tr),np.sin(ph_tr)])
            Xg_ts=np.column_stack([np.ones(len(ts)),ge[ts],te[ts],np.cos(ph_ts),np.sin(ph_ts)])
            G[h].append(corr(fitpred(Xp_tr,ytr,Xp_ts),yts))
            GT[h].append(corr(fitpred(Xg_tr,ytr,Xg_ts),yts))
    except Exception as e: print("skip",e)
print(f"N={len(ccA)} hearts | median tide period {np.median(tideP):.0f} beats")
print(f"\nTest A  corr(gold loudness, tide loudness) = {np.mean(ccA):+.3f} ± {np.std(ccA):.3f}")
print(f"        (compare: gold-gates-green was +0.33)")
print(f"\nTest B  strict-causal forecast of GOLD energy:")
print(f"{'h':>4} {'gold-only':>10} {'gold+tide':>10} {'tide adds':>10}")
for h in H:
    p=np.mean(G[h]); pg=np.mean(GT[h]); print(f"{h:>4} {p:>+10.3f} {pg:>+10.3f} {pg-p:>+10.3f}")
