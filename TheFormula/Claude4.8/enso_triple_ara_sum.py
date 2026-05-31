"""
Linkage test: do the three systems' ARAs sum to ~1.5?  (1.75 - 0.25 = span between walls)
=========================================================================================
Dylan's diagnostic: three systems are LINKED into one self-propelling stack when their ARAs
add to ~1.5 -- the usable span between the two singularity cut-offs (0.25 space-wall and
1.75 time-wall). Self-propelling at this level needs component systems that SEMI-maintain
(ARA partway between singularity and full shock-absorber 1.0), so three of them total ~1.5.

ARA per system = T_release / T_accumulation, measured from waveform asymmetry:
   accumulation = trough -> peak (slow charge) ; release = peak -> trough (discharge).
   symmetric wave -> ARA 1.0 ; fast-snap relaxation oscillator -> ARA < 1.

Triple (independent, sign-changing ocean oscillators):
   PDO (above)  +  NINO (us)  +  IOD (side)
Prediction: sum ~ 1.5 if the three are one linked stack.

Data: NOAA ERSST PDO, NOAA NINO3.4, NOAA PSL DMI(IOD). Real. Descriptive diagnostic.
"""
import numpy as np
from numpy.fft import rfft, rfftfreq

def load_nino(p,miss=-99.99):
    d={}
    for ln in open(p):
        s=[x.strip() for x in ln.split(",")]
        if len(s)==2 and s[0][:4].isdigit():
            v=float(s[1])
            if v>miss+0.001: d[s[0][:7].replace("-","")]=v
    return d
def load_pdo(p,miss=99.0):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==13 and s[0].isdigit() and len(s[0])==4:
            yr=int(s[0])
            for mo in range(1,13):
                try: v=float(s[mo])
                except: continue
                if v<miss-0.001: d[f"{yr}{mo:02d}"]=v
    return d
def load_dmi(p,miss=-9990.0):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==13 and s[0].isdigit() and len(s[0])==4:
            yr=int(s[0])
            if yr<1800 or yr>2100: continue
            for mo in range(1,13):
                try: v=float(s[mo])
                except: continue
                if v>miss: d[f"{yr}{mo:02d}"]=v
    return d

def smooth(x,w):
    if w<2: return x
    k=np.ones(w)/w; return np.convolve(x,k,mode="same")
def dom_period(x,lo=12,hi=240):
    x=x-x.mean(); n=len(x); f=rfftfreq(n,d=1.0); P=np.abs(rfft(x))**2
    per=np.where(f>0,1.0/np.maximum(f,1e-9),np.inf); m=(per>=lo)&(per<=hi); idx=np.where(m)[0]
    return per[idx[np.argmax(P[idx])]]
def extrema(x,sep):
    mx=[]; mn=[]
    for i in range(len(x)):
        a=max(0,i-sep); b=min(len(x),i+sep+1); seg=x[a:b]
        if x[i]==seg.max() and x[i]>x[a] : mx.append(i)
        if x[i]==seg.min() and x[i]<x[a] : mn.append(i)
    # dedupe near-equal plateaus
    def thin(idx):
        out=[]
        for j in idx:
            if not out or j-out[-1]>=sep: out.append(j)
        return out
    return thin(mx),thin(mn)
def ara(x):
    p=dom_period(x); sep=max(2,int(round(p/3)))
    xs=smooth(x,max(3,sep//2))
    mx,mn=extrema(xs,sep)
    ev=sorted([(i,'M') for i in mx]+[(i,'m') for i in mn])
    acc=[]; rel=[]   # accumulation = trough->peak ; release = peak->trough
    for (i0,t0),(i1,t1) in zip(ev,ev[1:]):
        if t0=='m' and t1=='M': acc.append(i1-i0)
        if t0=='M' and t1=='m': rel.append(i1-i0)
    if not acc or not rel: return np.nan,p,len(mx),len(mn)
    return float(np.mean(rel)/np.mean(acc)), p, len(mx), len(mn)

def main():
    nino=load_nino("nino34_long_anom.csv")
    pdo =load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")
    iod =load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
    # common span so all three see the same epoch
    keys=sorted(set(nino)&set(pdo)&set(iod))
    T=np.array([nino[k] for k in keys]); P=np.array([pdo[k] for k in keys]); I=np.array([iod[k] for k in keys])
    print(f"common span: {len(keys)} mo  {keys[0]}..{keys[-1]}\n")
    print(f"{'system':>16} {'ARA=rel/acc':>12} {'dom period':>11}  (peaks/troughs)")
    rows=[]
    for nm,x in [("PDO (above)",P),("NINO (us)",T),("IOD (side)",I)]:
        a,p,nx,nn=ara(x); rows.append((nm,a))
        print(f"{nm:>16} {a:>12.3f} {p:>9.1f}mo  ({nx}/{nn})")
    s=sum(a for _,a in rows if not np.isnan(a))
    print(f"\n   SUM of three ARAs = {s:.3f}   (target ~1.50 = 1.75 - 0.25, span between walls)")
    print(f"   each averages {s/3:.3f}  (0.50 = a clean 'semi-maintainer')")
    verdict = "LINKED stack (sum near 1.5)" if abs(s-1.5)<0.25 else "sum off 1.5 -- linkage not shown this way"
    print(f"   -> {verdict}")
    print("\nReal NOAA indices, same epoch. ARA from waveform charge/discharge asymmetry. Descriptive.")

if __name__=="__main__": main()
