# STRICT-CAUSAL camshaft predictor: use the SLOW (gold) band to predict the
# FAST (green) band's ENERGY (envelope) h beats ahead.
# Benchmark vs persistence (green energy now) so we know gold adds value.
import numpy as np, wfdb, glob
from scipy.signal import welch, butter, sosfiltfilt, hilbert
PHI=(1+5**0.5)/2
base="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0/"
def load(rec):
    ann=wfdb.rdann(rec,'ecg'); rr=np.diff(ann.sample)/ann.fs*1000.0
    return rr[(rr>300)&(rr<2000)]
def hp(x,Pc): return sosfiltfilt(butter(2,(1.0/Pc)/0.5,btype='high',output='sos'),x-x.mean())
def loud(x,b):
    f,P=welch(x,fs=1.0,nperseg=4096); per=np.divide(1.,f,out=np.full_like(f,np.inf),where=f>0)
    m=(per>=b[0])&(per<=b[1]); return per[m][np.argmax(P[m])]
def bf(x,P,frac=0.4):
    lo=(1/P)*(1-frac)/0.5; hi=min((1/P)*(1+frac)/0.5,0.99)
    return sosfiltfilt(butter(4,[lo,hi],btype='band',output='sos'),x)
def corr(a,b):
    a=np.asarray(a);b=np.asarray(b)
    return float(np.corrcoef(a,b)[0,1]) if a.std() and b.std() else 0.0
H=[3,6,12,20,30]
recs=sorted(glob.glob(base+"nsr*.hea"))[:25]
cam={h:{'p':[],'t':[],'per':[]} for h in H}
for fp in recs:
    try:
        rr=load(fp[:-4]); spb=np.median(rr)/1000.0; x=hp(rr,60)
        g=loud(x,(1/0.40/spb,1/0.15/spb)); b=loud(x,(1/0.15/spb,1/0.04/spb))
        G=bf(x,g); B=bf(x,b)
        genv=np.abs(hilbert(G)); benv=np.abs(hilbert(B)); bph=np.angle(hilbert(B))
        n=len(x); cut=n//2  # train first half, test second half (causal)
        # fit cam: green energy ~ gold energy + cos/sin(gold phase), TRAIN ONLY
        def feats(j): return np.column_stack([np.ones_like(j,dtype=float),benv[j],np.cos(bph[j]),np.sin(bph[j])])
        tr=np.arange(2*int(b),cut)
        co,*_=np.linalg.lstsq(feats(tr),genv[tr],rcond=None)
        for h in H:
            te=np.arange(cut, n-h)
            # predicted gold phase h ahead from its known period (causal, period from train)
            ph_ahead=bph[te]+2*np.pi*h/b
            F=np.column_stack([np.ones(len(te)),benv[te],np.cos(ph_ahead),np.sin(ph_ahead)])
            pred=F@co
            truth=genv[te+h]
            cam[h]['p'].append(corr(pred,truth))
            cam[h]['per'].append(corr(genv[te],truth))  # persistence baseline
    except Exception as e: print("skip",e)
print(f"N={len(cam[H[0]]['p'])} hearts | green-ENERGY forecast, pooled mean corr")
print(f"{'h(beats)':>8} {'camshaft':>9} {'persist':>9} {'gold adds':>10}")
for h in H:
    cm=np.mean(cam[h]['p']); pr=np.mean(cam[h]['per'])
    print(f"{h:>8} {cm:>+9.3f} {pr:>+9.3f} {cm-pr:>+10.3f}")
