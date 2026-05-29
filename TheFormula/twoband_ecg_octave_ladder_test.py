# Confirm octave reading: split the two families, test centers & 4x relation.
import numpy as np, wfdb, glob
from scipy.signal import welch, butter, sosfiltfilt, find_peaks
PHI=(1+5**0.5)/2
base="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0/"
def load(rec):
    ann=wfdb.rdann(rec,'ecg'); rr=np.diff(ann.sample)/ann.fs*1000.0
    return rr[(rr>300)&(rr<2000)]
def hp(x,Pc): return sosfiltfilt(butter(2,(1.0/Pc)/0.5,btype='high',output='sos'),x-x.mean())
def top2(x):
    f,P=welch(x,fs=1.0,nperseg=4096); per=np.divide(1.,f,out=np.full_like(f,np.inf),where=f>0)
    m=(per>=2)&(per<=50); pp=per[m][::-1]; PP=P[m][::-1]
    PPs=np.convolve(PP,np.ones(5)/5,'same')
    idx,props=find_peaks(PPs,prominence=PPs.max()*0.02)
    if len(idx)<2: return None
    order=idx[np.argsort(props['prominences'])[::-1]]; p1=pp[order[0]]
    for j in order[1:]:
        if max(pp[j]/p1,p1/pp[j])>=1.3: return sorted([p1,pp[j]])
    return None
R=[]
for fp in sorted(glob.glob(base+"nsr*.hea")):
    try:
        r=top2(hp(load(fp[:-4]),60))
        if r: R.append(r[1]/r[0])
    except: pass
R=np.array(R)
# log-domain: octaves above the fundamental.  log2(ratio): 1=octave, 2=two-octave, log2(phi)=0.69
L=np.log2(R)
low=R[R<3.0]; high=R[R>=3.0]
print(f"N={len(R)}")
print(f"log2(ratio): octave=1.000  two-octave=2.000  phi={np.log2(PHI):.3f}")
print(f"LOW family  (ratio<3): n={len(low)}  mean ratio {low.mean():.2f}  log2 {np.log2(low).mean():.3f}  -> nearest: ", end="")
print("phi" if abs(np.log2(low).mean()-np.log2(PHI))<abs(np.log2(low).mean()-1) else "octave(2.0)")
print(f"HIGH family (ratio>=3): n={len(high)}  mean ratio {high.mean():.2f}  log2 {np.log2(high).mean():.3f}")
print(f"\n  high/low ratio of centers = {high.mean()/low.mean():.2f}   (two octaves apart = 4.0)")
print(f"  median low {np.median(low):.2f}  median high {np.median(high):.2f}  -> {np.median(high)/np.median(low):.2f}x")
# tightest test: round each log2 to nearest half-octave, see where mass lands
from collections import Counter
binned=Counter(np.round(L*2)/2)
print("\n  log2(ratio) histogram (0.5=√2, 0.69=phi, 1.0=octave, 2.0=2oct, 3.0=3oct):")
for k in sorted(binned): print(f"    {k:+.1f} oct : {'#'*binned[k]} ({binned[k]})")
