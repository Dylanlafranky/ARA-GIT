import warnings; warnings.filterwarnings('ignore')
import numpy as np, glob, os
from astropy.timeseries import LombScargle
from scipy.optimize import curve_fit
PHI=(1+5**0.5)/2
def bestf(t,y,a,b,n=120000):
    fr=np.linspace(a,b,n); p=LombScargle(t,y).power(fr); return fr[np.argmax(p)]
def fitsine(t,y,f0):
    g=lambda tt,a,b,c:a*np.sin(2*np.pi*f0*tt)+b*np.cos(2*np.pi*f0*tt)+c
    popt,_=curve_fit(g,t,y,p0=[np.std(y),np.std(y),0]); return g(t,*popt),np.hypot(popt[0],popt[1])
def analyze(fn):
    d=np.load(fn); t=d['t']; f=d['f']-np.mean(d['f'])
    y=f.copy(); comps=[]
    for k in range(6):
        f0=bestf(y if False else t,y,0.05,12) if k==0 else bestf(t,y,0.05,12)
        f0=bestf(t,y,max(0.05,f0-0.02),f0+0.02,40000)
        m,a=fitsine(t,y,f0); comps.append((f0,a)); y=y-m
    f1,A1=comps[0]
    # second harmonic amplitude (nearest comp to 2*f1)
    A2h=next((a for (fc,a) in comps if abs(fc/f1-2)<0.01), np.nan)
    R21=A2h/A1 if A2h==A2h else np.nan
    # independent secondary mode = strongest non-harmonic
    indep=[(fc,a) for (fc,a) in comps[1:] if abs(fc/f1-round(fc/f1))>0.02]
    sec=indep[0] if indep else (np.nan,np.nan)
    return f1,A1,R21,sec[0]/f1 if sec[0]==sec[0] else np.nan
print("NEAR-PHI CLUB — leanness (R21 harmonic spray) measured from raw Kepler light curves\n")
print("%-14s %10s %8s %10s %12s"%("star","f1(c/d)","R21","2nd/f1","vs phi"))
files={'KIC5520878':'/tmp/golden_kic5520878_q3.npz','KIC4064484':'/tmp/club_4064484.npz',
       'KIC8832417':'/tmp/club_8832417.npz','KIC9453114':'/tmp/club_9453114.npz'}
r21s=[]
for nm,fn in files.items():
    f1,A1,R21,sr=analyze(fn)
    off=(sr-PHI)/PHI*100 if sr==sr else float('nan')
    r21s.append(R21)
    print("%-14s %10.4f %8.3f %10.4f %+11.1f%%"%(nm,f1,R21,sr,off))
print("\nCLUB mean R21 = %.3f   (n=%d)"%(np.nanmean(r21s),len(r21s)))
print("CROWD mean R21:  RRd 0.162 , Cep 0.191  (ordinary double-mode, off-phi)")
print("Control classical Cepheid V1154 Cyg R21 (from earlier): A2/A1=0.0384/0.137=%.3f"%(0.0384/0.1369))
