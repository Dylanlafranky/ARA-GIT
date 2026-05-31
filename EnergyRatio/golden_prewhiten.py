import warnings; warnings.filterwarnings('ignore')
import numpy as np
from astropy.timeseries import LombScargle
from scipy.optimize import curve_fit
PHI=(1+5**0.5)/2
d=np.load('/tmp/golden_kic5520878_q3.npz'); t=d['t']; f=d['f']; f=f-np.mean(f)

def best_freq(t,y,fmin,fmax,n=300000):
    fr=np.linspace(fmin,fmax,n); p=LombScargle(t,y).power(fr)
    return fr[np.argmax(p)], p.max()
def fit_sine(t,y,f0):
    g=lambda tt,a,b,c: a*np.sin(2*np.pi*f0*tt)+b*np.cos(2*np.pi*f0*tt)+c
    popt,_=curve_fit(g,t,y,p0=[np.std(y),np.std(y),0]); return g(t,*popt),popt

y=f.copy(); found=[]
# iteratively remove the strongest sinusoid + refit its frequency, 6 components
for k in range(6):
    f0,pw=best_freq(t,y,0.05,12)
    # refine locally
    f0,pw=best_freq(t,y,max(0.05,f0-0.02),f0+0.02,n=40000)
    model,popt=fit_sine(t,y,f0); amp=np.hypot(popt[0],popt[1])
    found.append((f0,amp,pw)); y=y-model
print("Iterative prewhitening (freq c/d, amplitude, LS power at extraction):\n")
for k,(f0,a,pw) in enumerate(found,1):
    print("  f%d = %.5f c/d  (P=%.4f d)  amp=%.5f"%(k,f0,1/f0,a))

f1=found[0][0]
# identify which are harmonics of f1 vs independent
print("\nClassify each vs f1 = %.5f:"%f1)
for k,(f0,a,pw) in enumerate(found,1):
    r=f0/f1
    nearest_int=round(r)
    is_harm = abs(r-nearest_int)<0.01 and nearest_int>=1
    tag = "HARMONIC %dx"%nearest_int if is_harm else "independent?"
    print("  f%d/f1 = %.4f   %s"%(k,r,tag))

# the independent (non-harmonic) modes: test their ratio vs phi & integers
indep=[f0 for (f0,a,pw) in found if abs((f0/f1)-round(f0/f1))>0.01]
print("\nIndependent (non-harmonic) frequencies:",[round(x,4) for x in indep])
if indep:
    fi=indep[0]
    for ref in [f1]+indep[1:]:
        if ref==fi: continue
    r=fi/f1
    print("\nStrongest independent / f1 = %.4f"%r)
    for name,val in [("phi",PHI),("1/phi",1/PHI),("phi^2",PHI**2),("3/2",1.5),("2",2.0),("4/3",4/3),("5/4",1.25),("0.618",0.618)]:
        print("   vs %-8s %.4f -> off %.2f%%"%(name,val,abs(r-val)/val*100))
