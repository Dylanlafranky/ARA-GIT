import numpy as np
phi=(1+5**0.5)/2; ceiling=2-phi

def prep(x):
    idx=np.arange(len(x)); g=np.isfinite(x); x=np.interp(idx,idx[g],x[g])
    return x-np.polyval(np.polyfit(idx,x,1),idx)
def load_nino():
    v=[float(l.split(',')[1]) if l.split(',')[1:] and l[:4].isdigit() else np.nan for l in open('GIT/ARA-GIT/TheFormula/Claude4.8/nino34_long_anom.csv')]
    v=[np.nan if (x!=x or x<=-99) else x for x in v if isinstance(x,float)]
    return np.array(v)
def load_sun():
    v=[]
    for l in open('GIT/ARA-GIT/TheFormula/Claude4.8/SN_m_tot.csv'):
        p=l.split(';'); 
        if len(p)>=4:
            x=float(p[3]); v.append(np.nan if x<0 else x)
    return np.array(v)
def load_ecg():
    v=[]
    for l in open('TheFormula/nsr001_rr.csv'):
        p=l.split(',')
        if len(p)==2 and p[1].strip()[0:1].isdigit():
            try: v.append(float(p[1]))
            except: pass
    return np.array(v[:40000])
def dom_period(x):
    n=len(x); p=np.abs(np.fft.rfft(x*np.hanning(n)))**2; fr=np.fft.rfftfreq(n); p[0]=0
    # restrict to periods between 6 and n/4 samples
    per=1/np.where(fr>0,fr,1e9); m=(per>6)&(per<n/4)
    k=np.where(m)[0][np.argmax(p[m])]; return 1/fr[k]
def acf(x,lag):
    lag=int(round(lag))
    if lag<=0 or lag>=len(x)-2: return np.nan
    a=x[:-lag]-x[:-lag].mean(); b=x[lag:]-x[lag:].mean()
    return np.sum(a*b)/np.sqrt(np.sum(a*a)*np.sum(b*b))
def ara(x,P):
    # asymmetry of dominant cycle: bandpass-ish via rolling mean removal, peaks vs troughs
    from numpy import diff,sign
    w=max(3,int(P/6)); 
    sm=np.convolve(x,np.ones(w)/w,'same')
    s=x-sm
    zc=np.where(diff(sign(s)))[0]
    if len(zc)<4: return np.nan
    halves=np.diff(zc)
    rise=halves[0::2].mean(); fall=halves[1::2].mean()
    return max(rise,fall)/min(rise,fall)   # >=1 asymmetry magnitude

print('%-16s %8s %8s %8s %8s %8s'%('system','P(smp)','floor1P','floor2P','perCyc loss','ARA-asym'))
for name,load in [('ENSO',load_nino),('ECG/heart',load_ecg),('Solar',load_sun)]:
    x=prep(load()); P=dom_period(x)
    f1=abs(acf(x,P)); f2=abs(acf(x,2*P))
    loss=1-min(f2/f1,1.0) if f1>0.05 else 1.0   # if floor at noise, ~total loss
    A=ara(x,P)
    print('%-16s %8.1f %8.3f %8.3f %8.3f %8.2f'%(name,P,f1,f2,loss,A))
print('\n2-phi ceiling = %.3f'%ceiling)
print('Predicted chain: higher recycling floor -> lower per-cycle loss; leaky sits at/above ceiling.')
