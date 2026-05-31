"""
The R: information exchange between ENSO and its systems (transfer entropy)
==========================================================================
A1 (map) -> R (info geometry) -> A2 (predict).  We have A1 (ARA maps) and keep guessing A2
(forecasts). The missing piece is R: HOW information moves between the systems. Energy
correlation read this near zero (z=-0.1). Information is different: transfer entropy asks how
much knowing X's PAST reduces our SURPRISE about ENSO's FUTURE, beyond ENSO's own past.

TE(X->Y) at lag L = I(Y_{t+1} ; X_{t-L} | Y_t), binned (quantile), bits.
For each feeder we report TE both directions, the best lead-lag, and a phase-scramble null
z-score (preserves each spectrum, breaks the coupling). Net = TE(feeder->NINO) - TE(NINO->feeder).

Data: NOAA NINO3.4, PMEL WWV, NOAA SOI, NOAA ERSST PDO, NOAA PSL DMI(IOD). Real. Descriptive.
"""
import re
import numpy as np
from numpy.fft import rfft, irfft

def load_nino(p,miss=-99.99):
    d={}
    for ln in open(p):
        s=[x.strip() for x in ln.split(",")]
        if len(s)==2 and s[0][:4].isdigit():
            v=float(s[1])
            if v>miss+0.001: d[s[0][:7].replace("-","")]=v
    return d
def load_wwv(p):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==3 and s[0].isdigit() and len(s[0])==6: d[s[0]]=float(s[2])/1e14
    return d
def load_soi(p,miss=-99.99):
    d={}
    for ln in open(p):
        m=re.match(r"\s*(\d{4})\s+(.*)",ln)
        if not m: continue
        yr=int(m.group(1))
        if yr<1900 or yr>2100: continue
        for mo,val in enumerate(ln.split()[1:13],1):
            try: v=float(val)
            except: continue
            if v>miss+0.001: d[f"{yr}{mo:02d}"]=v
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

def qbin(x,q):
    edges=np.quantile(x,np.linspace(0,1,q+1)); edges[0]-=1e-9; edges[-1]+=1e-9
    return np.clip(np.digitize(x,edges[1:-1]),0,q-1)

def te(X,Y,L,q=5):
    """TE(X->Y) at lag L (X leads), bits. Y_{t+1} from Y_t and X_{t-L}."""
    n=len(Y)
    y1=Y[L+1:n]; y0=Y[L:n-1]; xx=X[0:n-1-L]
    a=qbin(y1,q); b=qbin(y0,q); c=qbin(xx,q)
    N=len(a)
    H=np.zeros((q,q,q))
    for i in range(N): H[a[i],b[i],c[i]]+=1
    p=H/N
    p_y0=p.sum(axis=(0,2)); p_y1y0=p.sum(axis=2); p_y0x=p.sum(axis=0)
    s=0.0
    for i in range(q):
        for j in range(q):
            for k in range(q):
                pijk=p[i,j,k]
                if pijk<=0: continue
                num=pijk*p_y0[j]; den=p_y0x[j,k]*p_y1y0[i,j]
                if den<=0: continue
                s+=pijk*np.log2(num/den)
    return max(s,0.0)

def phase_scramble(x,rng):
    F=rfft(x-x.mean()); mag=np.abs(F); ph=np.angle(F)
    ph[1:]=rng.uniform(-np.pi,np.pi,len(ph)-1)
    return irfft(mag*np.exp(1j*ph),n=len(x))

def best_te(X,Y,lags,q=5):
    vals=[(L,te(X,Y,L,q)) for L in lags]
    return max(vals,key=lambda t:t[1])

def directed(name,F,T,rng,lags=range(0,13),q=5,nnull=200):
    Lf,tf=best_te(F,T,lags,q)   # feeder -> NINO
    Lr,tr=best_te(T,F,lags,q)   # NINO -> feeder
    null=np.array([te(phase_scramble(F,rng),T,Lf,q) for _ in range(nnull)])
    z=(tf-null.mean())/(null.std()+1e-12)
    arrow = "feeder->ENSO" if tf>tr else "ENSO->feeder"
    print(f"   {name:12s}: TE(feeder->ENSO) {tf:.3f} bits @lag {Lf:+d}mo | "
          f"TE(ENSO->feeder) {tr:.3f} @lag {Lr:+d} | net {tf-tr:+.3f} -> {arrow}  (z {z:+.1f})")
    return name,tf,Lf,tr,Lr,z

def main():
    nino=load_nino("nino34_long_anom.csv")
    feeders={
        "WWV":  load_wwv("wwv_west.dat"),
        "SOI":  load_soi("soi.data"),
        "PDO":  load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat"),
        "IOD":  load_dmi("../../../../IOD_NOAA/dmi.had.long.data"),
    }
    rng=np.random.default_rng(11)
    print("== R: INFORMATION EXCHANGE (transfer entropy, bits) -- who informs ENSO's future? ==")
    print("   (lag>0 = feeder's past informs ENSO's next step; z>2 = real, not chance)\n")
    rows=[]
    for nm,d in feeders.items():
        keys=sorted(set(nino)&set(d))
        T=np.array([nino[k] for k in keys]); F=np.array([d[k] for k in keys])
        print(f"   [{nm}] overlap {len(keys)} mo {keys[0]}..{keys[-1]}")
        rows.append(directed(nm,F,T,rng))
    print()
    real=[r for r in rows if r[5]>2]
    if real:
        best=max(real,key=lambda r:r[1])
        print(f"Strongest real information donor to ENSO: {best[0]} "
              f"({best[1]:.3f} bits @ lag {best[2]:+d}mo, z {best[5]:+.1f}).")
    else:
        print("No feeder exceeds chance on transfer entropy.")
    print("\nTransfer entropy = directed information flow. Descriptive diagnostic, real indices.")

if __name__=="__main__": main()
