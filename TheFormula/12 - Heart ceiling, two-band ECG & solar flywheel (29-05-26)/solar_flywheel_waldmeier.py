# Within-cycle golden-duty: rise(fast charge) vs fall(slow discharge) fraction across cycles.
import numpy as np
from scipy.signal import savgol_filter, find_peaks
z=np.load('solar_silso_monthly.npz'); yr=z['yr']; ssn=z['ssn']; phi=1.6180339887
s=savgol_filter(ssn,25,3)
mx,_=find_peaks(s,distance=12*7,prominence=20); mn,_=find_peaks(-s,distance=12*7,prominence=10)
rf=[]
for xm in mx:
    prev=mn[mn<xm]; nxt=mn[mn>xm]
    if len(prev) and len(nxt):
        r=yr[xm]-yr[prev[-1]]; f=yr[nxt[0]]-yr[xm]
        if 1<r<9 and 1<f<11: rf.append(r/(r+f))
rf=np.array(rf)
print(f"cycles {len(rf)}; rise(fast) {rf.mean():.3f}+/-{rf.std():.3f}; fall(slow) {1-rf.mean():.3f}")
print(f"target 1/phi^2={1/phi**2:.3f} / 1/phi={1/phi:.3f}")
