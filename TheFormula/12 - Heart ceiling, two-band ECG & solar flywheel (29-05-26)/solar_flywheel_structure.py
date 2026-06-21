# Octave-rung test (edge-free 3 strongest distinct peaks) + between-band golden duty.
import numpy as np
from scipy.signal import welch, hilbert, butter, sosfiltfilt
z=np.load('solar_silso_monthly.npz'); ssn=z['ssn']; fsm=12.0; phi=1.6180339887
x=ssn-ssn.mean()
f,P=welch(x,fs=fsm,nperseg=min(2048,len(x))); per=1/f[1:]; Pp=P[1:]
m=(per>=2)&(per<=200); per,Pp=per[m],Pp[m]; order=np.argsort(Pp)[::-1]
peaks=[]
for i in order:
    if all(abs(np.log2(per[i]/q))>0.4 for q in peaks): peaks.append(per[i])
    if len(peaks)>=3: break
peaks=sorted(peaks); print("bands(yr):",[round(p,2) for p in peaks])
for p in peaks[1:]: print(f"  {p:.1f}/{peaks[0]:.1f}={p/peaks[0]:.2f} log2={np.log2(p/peaks[0]):.2f}")
