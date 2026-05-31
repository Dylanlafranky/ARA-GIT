"""
ENSO + PDO (the above-system / brown shared clock) -> does it move the wall?
============================================================================
The PDO clock test (enso_above_pdo_clock.py) showed: ENSO's BROWN band phase-locks to
the PDO (the system ABOVE ENSO) at 0.71, green only 0.24, and ENSO leads. So PDO is the
real "system above". Dylan: importing it into the forecast should push the SHORT horizon
(h=6) toward the 0.764 cutoff and lift the long horizon (h=24) a bit.

Test it by adding PDO as a feeder to the spring regime-switch model. STRICTLY CAUSAL:
  * PDO at origin i is contemporaneous (known) -- no future leakage.
  * standardized train-only each origin; both seasonal maps refit past-only each origin;
  * regime label = calendar; correlation leads; held out from 2016. N set by overlap.

Configs:
  switch (base)   = T, zWWV, zWWVe, zSOI                  [prior champion, ~0.725 @ h6]
  +PDO            = base + zPDO                            [add the system above]
  +PDO matched    = base + zPDO + zPDO_brown(40-70mo)     [feed PDO at the shared-clock speed]

Usage: python3 enso_pdo_feeder_test.py
"""
import re
import numpy as np
from numpy.fft import rfft, irfft, rfftfreq

WALK_START=2005.0; MIN_TRAIN=270; CAL_SPLIT_YEAR=2016.0; HMAX=30
SPRING={3,4,5}

# ---------- loaders ----------
def load_wwv(p):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==3 and s[0].isdigit() and len(s[0])==6: d[s[0]]=float(s[2])/1e14
    return d
def load_nino(p,miss=-99.99):
    d={}
    for ln in open(p):
        s=[x.strip() for x in ln.split(",")]
        if len(s)==2 and s[0][:4].isdigit():
            v=float(s[1])
            if v>miss+0.001: d[s[0][:7].replace("-","")]=v
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

def bandpass_fft(x, lo_mo, hi_mo):
    """Zero-phase band isolation. NOTE: applied to the FULL PDO series ONCE up front.
       This is non-causal (uses whole record) -- used only as a slow background channel,
       same role as a climatological filter. Flagged honestly; the head-to-head base
       comparison does NOT use it, so any lift from +PDO (plain) is fully causal."""
    x=x-x.mean(); n=len(x)
    f=rfftfreq(n, d=1.0); F=rfft(x)
    per=np.where(f>0, 1.0/np.maximum(f,1e-9), np.inf)
    keep=(per>=lo_mo)&(per<=hi_mo)
    return irfft(np.where(keep,F,0.0), n=n)

# ---------- model ----------
def base_feats(X,m):
    th=2*np.pi*(m-1)/12; c,s=np.cos(th),np.sin(th)
    return np.column_stack([X, X*c[:,None], X*s[:,None], c, s, np.ones(len(X))])
def spring_feats(X,m):
    F=base_feats(X,m); mix=(X[:,1]*X[:,3])[:,None]
    return np.column_stack([F, mix])

def walk_switch(cols_raw, stdz, yr, mon, T):
    rec={h:{"pred":[],"truth":[],"clim":[],"oy":[]} for h in range(1,HMAX+1)}
    A=np.column_stack(cols_raw)
    for i in range(len(T)):
        if yr[i]<WALK_START: continue
        idx=np.arange(0,i)
        if len(idx)<MIN_TRAIN: continue
        X=A.copy().astype(float)
        for j in stdz:
            mu=A[idx,j].mean(); sd=A[idx,j].std()
            X[:,j]=(A[:,j]-mu)/(sd if sd>0 else 1.0)
        clim=T[idx].mean()
        mtr=mon[idx][:-1]; Xa=X[idx][:-1]; Xb=X[idx][1:]
        sp=np.array([int(v) in SPRING for v in mtr])
        if sp.sum()<12 or (~sp).sum()<12: continue
        Bs=np.linalg.lstsq(spring_feats(Xa[sp],mtr[sp]), Xb[sp], rcond=None)[0]
        Br=np.linalg.lstsq(base_feats(Xa[~sp],mtr[~sp]), Xb[~sp], rcond=None)[0]
        for h in range(1,HMAX+1):
            if i+h>=len(T): break
            x=X[i].copy()
            for kk in range(h):
                mm=((mon[i]-1+kk)%12)+1
                x=(spring_feats(x[None,:],np.array([mm]))[0]@Bs) if mm in SPRING \
                  else (base_feats(x[None,:],np.array([mm]))[0]@Br)
            rec[h]["pred"].append(x[0]); rec[h]["truth"].append(T[i+h])
            rec[h]["clim"].append(clim); rec[h]["oy"].append(yr[i])
    return rec

def corr(pred,truth):
    pred=np.asarray(pred); truth=np.asarray(truth); m=~np.isnan(pred)
    a=pred[m]-pred[m].mean(); b=truth[m]-truth[m].mean()
    d=np.sqrt((a*a).sum()*(b*b).sum()); return float((a*b).sum()/d) if d>0 else 0.0
def evalrec(rec):
    out={}
    for h in range(1,HMAX+1):
        oy=np.array(rec[h]["oy"]); pr=np.array(rec[h]["pred"]); tr=np.array(rec[h]["truth"])
        if len(oy)==0: continue
        tst=oy>=CAL_SPLIT_YEAR
        if tst.sum()<20: continue
        out[h]=dict(corr=corr(pr[tst],tr[tst]), n=int(tst.sum()))
    return out

def main():
    W=load_wwv("wwv_west.dat"); E=load_wwv("wwv_east.dat")
    nino=load_nino("nino34_long_anom.csv"); SOI=load_soi("soi.data")
    PDO=load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")

    base_keys=sorted(set(W)&set(E)&set(nino)&set(SOI)&set(PDO))
    print(f"aligned (T,WWV,SOI,PDO): {len(base_keys)}  {base_keys[0]}..{base_keys[-1]}\n")

    # PDO brown band built on the full PDO record (flagged non-causal background channel)
    pk=sorted(PDO); pser=np.array([PDO[k] for k in pk])
    pbrown={k:v for k,v in zip(pk, bandpass_fft(pser,40,70))}

    def build(extra_plain, with_brown):
        keys=[k for k in base_keys]
        T=np.array([nino[k] for k in keys]); Wv=np.array([W[k] for k in keys])
        Ev=np.array([E[k] for k in keys]); Sv=np.array([SOI[k] for k in keys])
        yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
        mon=np.array([int(k[4:6]) for k in keys])
        cols=[T,Wv,Ev,Sv]; stdz=[1,2,3]
        for d in extra_plain:
            cols.append(np.array([d[k] for k in keys])); stdz.append(len(cols)-1)
        if with_brown:
            cols.append(np.array([pbrown[k] for k in keys])); stdz.append(len(cols)-1)
        return cols,stdz,yr,mon,T

    configs={
        "switch (base)": (lambda: build([], False)),
        "+PDO":          (lambda: build([PDO], False)),
        "+PDO matched":  (lambda: build([PDO], True)),
    }
    res={}
    for name,fn in configs.items():
        cols,stdz,yr,mon,T=fn()
        res[name]=evalrec(walk_switch(cols,stdz,yr,mon,T))

    names=list(configs)
    print("HELD-OUT CORRELATION (leads)\n")
    print(f"{'lead':>4}  " + "".join(f"{nm:>16}" for nm in names))
    for h in (1,3,6,9,12,15,18,24):
        row=f"{h:>4} "
        for nm in names:
            d=res[nm].get(h)
            row+=f"   {d['corr']:>+6.3f}      " if d else f"   {'--':>10}   "
        print(row)
    b6=res['switch (base)'].get(6,{}).get('corr'); p6=res['+PDO'].get(6,{}).get('corr')
    b24=res['switch (base)'].get(24,{}).get('corr'); p24=res['+PDO'].get(24,{}).get('corr')
    print(f"\nh=6 : base {b6:+.3f} -> +PDO {p6:+.3f}   (target 0.764 = 1 - 1/phi^3)")
    print(f"h=24: base {b24:+.3f} -> +PDO {p24:+.3f}")
    print("\n+PDO (plain) is fully causal. '+PDO matched' adds a non-causal slow background")
    print("band (flagged) -- treat its lift as an upper bound, not an operational number.")

if __name__=="__main__": main()
