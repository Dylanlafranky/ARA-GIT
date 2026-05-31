# Recycling floor + per-cycle loss for Kepler pulsator light curves (run fetch_data.py first).
import numpy as np, os, warnings; warnings.filterwarnings('ignore')
from astropy.timeseries import LombScargle
def acf(x,lag):
    lag=int(round(lag))
    if lag<=0 or lag>=len(x)-2: return np.nan
    a=x[:-lag]-x[:-lag].mean(); b=x[lag:]-x[lag:].mean()
    return np.sum(a*b)/np.sqrt(np.sum(a*a)*np.sum(b*b))
def domP(t,f):
    fr=np.linspace(0.05,12,60000); p=LombScargle(t,f).power(fr); return 1/fr[np.argmax(p)]
files={'KIC5520878':'/tmp/golden_kic5520878_q3.npz','KIC4064484':'/tmp/club_4064484.npz',
       'KIC8832417':'/tmp/club_8832417.npz','KIC9453114':'/tmp/club_9453114.npz','V1154Cyg':'/tmp/cep_v1154.npz'}
print('%-12s %8s %8s %8s'%('star','floor1P','floor2P','loss'))
for nm,fn in files.items():
    if not os.path.exists(fn): print(nm,'MISSING'); continue
    d=np.load(fn); t=d['t']; f=d['f']-np.mean(d['f'])
    P=domP(t,f); Ps=P/np.median(np.diff(t))
    f1=abs(acf(f,Ps)); f2=abs(acf(f,2*Ps))
    print('%-12s %8.3f %8.3f %8.3f'%(nm,f1,f2,1-min(f2/f1,1.0) if f1>0.05 else 1.0))
