# Edge-free: no HF/LF windows. Highpass out slow drift, then let each heart's
# spectrum reveal its two strongest distinct peaks. Pool ratio over 54 records.
import numpy as np, wfdb, glob
from scipy.signal import welch, butter, sosfiltfilt, find_peaks
PHI=(1+5**0.5)/2
base="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0/"
def load(rec):
    ann=wfdb.rdann(rec,'ecg'); rr=np.diff(ann.sample)/ann.fs*1000.0
    return rr[(rr>300)&(rr<2000)]
def hp(x,Pc): return sosfiltfilt(butter(2,(1.0/Pc)/0.5,btype='high',output='sos'),x-x.mean())
def top2(x):
    # smoothed periodogram over physiological band 2..50 beats, no sub-windows
    f,P=welch(x,fs=1.0,nperseg=4096)
    per=np.divide(1.,f,out=np.full_like(f,np.inf),where=f>0)
    m=(per>=2)&(per<=50)
    pp=per[m][::-1]; PP=P[m][::-1]   # ascending period
    # log-smooth
    k=np.ones(5)/5; PPs=np.convolve(PP,k,'same')
    idx,props=find_peaks(PPs,prominence=PPs.max()*0.02)
    if len(idx)<2: return None
    order=idx[np.argsort(props['prominences'])[::-1]]
    # take strongest, then strongest that is >=1.3x away in period (distinct band)
    p1=pp[order[0]]
    for j in order[1:]:
        if max(pp[j]/p1,p1/pp[j])>=1.3:
            p2=pp[j]; return sorted([p1,p2])
    return None
recs=sorted(glob.glob(base+"nsr*.hea")); R=[]
for fp in recs:
    try:
        x=hp(load(fp[:-4]),60); r=top2(x)
        if r: R.append(r[1]/r[0])
    except: pass
R=np.array(R)
print(f"N usable = {len(R)}")
print(f"  mean {R.mean():.3f}  median {np.median(R):.3f}  trimmed10% {np.mean(np.sort(R)[len(R)//10:-len(R)//10 or None]):.3f}  geomean {np.exp(np.mean(np.log(R))):.3f}")
print(f"\n  3*phi = {3*PHI:.3f}   pi*phi = {np.pi*PHI:.3f}   2*phi^2 = {2*PHI**2:.3f}   5 = 5.000")
# how many records fall nearer 3phi vs piphi
d3=np.abs(R-3*PHI); dp=np.abs(R-np.pi*PHI)
print(f"  records closer to 3*phi: {(d3<dp).sum()} ; closer to pi*phi: {(dp<d3).sum()}")

print("\nsorted ratios:")
print(np.round(np.sort(R),2))
import numpy as np
print(f"\nfraction near octave (1.7-2.3): {((R>1.7)&(R<2.3)).mean():.2f}")
print(f"fraction near pi*phi (4.5-5.5): {((R>4.5)&(R<5.5)).mean():.2f}")
print(f"fraction in between (2.3-4.5):   {((R>2.3)&(R<4.5)).mean():.2f}")
