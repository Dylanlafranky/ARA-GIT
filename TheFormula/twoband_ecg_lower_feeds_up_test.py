# LONG horizons by targeting the SLOW band, and testing LOWER rungs feeding UP.
# Target = TIDE value (slow, ~356-beat period) h beats ahead, h up to ~4 min.
# Does green+gold recent ENERGY (the small accumulating) help predict the tide,
# on top of the tide's own slow persistence?  Strict-causal (train 1st half).
import numpy as np, wfdb, glob
from scipy.signal import welch, butter, sosfiltfilt, hilbert
base="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0/"
def load(rec):
    ann=wfdb.rdann(rec,'ecg'); rr=np.diff(ann.sample)/ann.fs*1000.0
    return rr[(rr>300)&(rr<2000)]
def bp(x,lo,hi):
    sos=butter(4,[(1/hi)/0.5,min((1/lo)/0.5,0.99)],btype='band',output='sos'); return sosfiltfilt(sos,x-x.mean())
def env(s): return np.abs(hilbert(s))
def corr(a,b):
    a=np.asarray(a);b=np.asarray(b)
    return float(np.corrcoef(a,b)[0,1]) if a.std() and b.std() else 0.0
def fp(Xtr,ytr,Xte):
    co,*_=np.linalg.lstsq(Xtr,ytr,rcond=None); return Xte@co
H=[30,60,120,240]   # ~0.4, 0.8, 1.6, 3.2 minutes
recs=sorted(glob.glob(base+"nsr*.hea"))[:25]
TP={h:[] for h in H}; TPL={h:[] for h in H}
for fpn in recs:
    try:
        rr=load(fpn[:-4]); spb=np.median(rr)/1000.0
        green=bp(rr,1/0.40/spb,1/0.15/spb); gold=bp(rr,1/0.15/spb,1/0.04/spb)
        tide=bp(rr,1/0.04/spb,1/0.0033/spb)
        ge=env(green); bo=env(gold); tv=tide; tph=np.angle(hilbert(tide)); tper=356
        n=len(rr); cut=n//2
        for h in H:
            tr=np.arange(800,cut-h); ts=np.arange(cut,n-h)
            ytr=tv[tr+h]; yts=tv[ts+h]
            # tide self-projection: its phase carried forward by its period
            cph_tr=np.cos(tph[tr]+2*np.pi*h/tper); sph_tr=np.sin(tph[tr]+2*np.pi*h/tper)
            cph_ts=np.cos(tph[ts]+2*np.pi*h/tper); sph_ts=np.sin(tph[ts]+2*np.pi*h/tper)
            Xp_tr=np.column_stack([np.ones(len(tr)),tv[tr],cph_tr,sph_tr])
            Xp_ts=np.column_stack([np.ones(len(ts)),tv[ts],cph_ts,sph_ts])
            # add LOWER rungs feeding up: green & gold recent energy
            Xl_tr=np.column_stack([Xp_tr,ge[tr],bo[tr]])
            Xl_ts=np.column_stack([Xp_ts,ge[ts],bo[ts]])
            TP[h].append(corr(fp(Xp_tr,ytr,Xp_ts),yts))
            TPL[h].append(corr(fp(Xl_tr,ytr,Xl_ts),yts))
    except Exception as e: print("skip",e)
print(f"N={len(TP[H[0]])} hearts | forecasting the SLOW TIDE value (period ~356 beats ~5min)")
print(f"{'h(beats)':>8} {'~min':>5} {'tide self':>10} {'+low rungs':>11} {'low adds':>9}")
for h in H:
    mins=h*0.8/60; p=np.mean(TP[h]); pl=np.mean(TPL[h])
    print(f"{h:>8} {mins:>5.1f} {p:>+10.3f} {pl:>+11.3f} {pl-p:>+9.3f}")
