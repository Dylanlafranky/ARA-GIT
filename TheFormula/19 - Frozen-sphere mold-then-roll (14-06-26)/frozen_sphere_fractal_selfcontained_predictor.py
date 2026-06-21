#!/usr/bin/env python3
"""
FROZEN-SPHERE FRACTAL SELF-CONTAINED predictor  (Test 2: NINO sub-waves only)
============================================================================
Dylan's follow-on idea (13 Jun 2026): drop the external below-system. The noisy
wave already CONTAINS its sub-waves (the faster rungs). Decompose the signal
into its own octave sub-rungs, and when a fast sub-wave COMPLETES its cycle let
that handover predict the larger/slower wave. Self-contained vertical-ARA / the
"river" (fast rung's now = slow rung's near future).

VERDICT (see FROZEN_SPHERE_MOLD_THEN_ROLL_RESULT.md):
  Loses to AR at EVERY horizon, including the long end Dylan expected to win.
  The phi-handover coupling came out near-inert (coupled == uncoupled to 3 dp).
  Structural reason: long-horizon skill lives in the SLOW rungs, which persist
  -> that is exactly what AR already models. Fast sub-waves give only short
  leads. From a signal's OWN past, geometry does not beat AR on VALUE.

Strict-causal: octave decomposition is a TRAILING moving-average cascade
(telescoping, exact reconstruction, NO filtfilt / NO zero-phase leak); all
terrain molded train-only; NINO future never read. Headline = correlation.
Data: NOAA NINO3.4 anomaly 1870-2025 (full record, self-contained).
"""
import numpy as np, re, json
PHI=(1+5**0.5)/2
DATA="Claude4.8"
def load_nino():
    d={}
    for line in open(f"{DATA}/nino34_long_anom.csv"):
        m=re.match(r'\s*(\d{4})-(\d{2})-\d{2},\s*(-?\d+\.\d+)',line)
        if m and float(m.group(3))>-99: d[(int(m.group(1)),int(m.group(2)))]=float(m.group(3))
    return d
nino=load_nino(); keys=sorted(nino); N=np.array([nino[k] for k in keys]); n=len(keys)
split=int(round(n/PHI)); Nz=(N-N[:split].mean())/N[:split].std()
print(f"NINO self-contained: n={n} ({keys[0]}..{keys[-1]}) train={split} test={n-split}")

def tma(x,w):  # causal trailing moving average (expanding until window full)
    out=np.copy(x); c=np.cumsum(np.insert(x,0,0))
    for t in range(len(x)):
        a=max(0,t-w+1); out[t]=(c[t+1]-c[a])/(t+1-a)
    return out
WINS=[6,12,24,48]
def decompose(x):  # octave sub-rungs; sum(bands)=x exactly (telescoping)
    bands=[]; cur=x
    for w in WINS: s=tma(cur,w); bands.append(cur-s); cur=s
    bands.append(cur); return bands
NB=24
def cslope(x): s=np.zeros_like(x); s[1:]=x[1:]-x[:-1]; return s
def pick(x,tr): s=cslope(x); return x[:tr].std()/(s[:tr].std()+1e-9)
def mold(x,tr,sc):
    s=cslope(x); xt,st=x[:tr],s[:tr]
    th=np.arctan2(st*sc,xt); r=np.sqrt(xt**2+(st*sc)**2); dth=np.diff(np.unwrap(th))
    bv=np.full(NB,np.nan); br=np.full(NB,np.nan); idx=((th+np.pi)/(2*np.pi)*NB).astype(int)%NB
    for b in range(NB):
        if (idx[:-1]==b).sum()>=3: bv[b]=np.median(dth[idx[:-1]==b])
        if (idx==b).sum()>=3: br[b]=np.median(r[idx==b])
    for arr in (bv,br):
        gd=~np.isnan(arr)
        if gd.sum()<2: arr[:]=(np.nanmedian(arr) if gd.any() else 0.0)
        else: arr[~gd]=np.interp(np.where(~gd)[0],np.where(gd)[0],arr[gd],period=NB)
    return dict(bv=bv,br=br,sc=sc)
def step(x,s,t,push=0.0):
    sc=t['sc']; th=np.arctan2(s*sc,x); b=int(((th+np.pi)/(2*np.pi)*NB))%NB
    t2=th+t['bv'][b]; r=t['br'][b]
    return r*np.cos(t2)+push, r*np.sin(t2)/sc

bands=decompose(Nz); K=len(bands)
scs=[pick(b,split) for b in bands]; terr=[mold(bands[j],split,scs[j]) for j in range(K)]
bslopes=[cslope(b) for b in bands]
coup=[]   # phi-handover: faster band j momentum -> slower band j+1 (train corr of tendencies)
for j in range(K-1):
    a=cslope(bands[j])[:split]; b=cslope(bands[j+1])[:split]
    c=np.corrcoef(a,b)[0,1] if np.std(a)>1e-9 else 0.0
    coup.append(0.0 if not np.isfinite(c) else c)
HOR=[3,6,12,24]; HK=0.10
def roll(o,h,couple=True):
    xs=[bands[j][o] for j in range(K)]; ss=[bslopes[j][o] for j in range(K)]
    for _ in range(h):
        nxs=[];nss=[]
        for j in range(K):
            push=HK*coup[j-1]*(ss[j-1]*scs[j-1]) if (couple and j>0) else 0.0
            x2,s2=step(xs[j],ss[j],terr[j],push=push); nxs.append(x2); nss.append(s2)
        xs,ss=nxs,nss
    return sum(xs)
AR_P=6
X=np.column_stack([Nz[AR_P-1-i:split-1-i] for i in range(AR_P)]); y=Nz[AR_P:split]
arb,*_=np.linalg.lstsq(np.column_stack([np.ones(len(y)),X]),y,rcond=None)
def arf(h):
    out=[]
    for o in range(split,n-h):
        hist=list(Nz[o-AR_P+1:o+1])
        for _ in range(h): hist.append(arb[0]+sum(arb[1+i]*hist[-1-i] for i in range(AR_P)))
        out.append(hist[-1])
    return np.array(out)
def C(a,b): return np.corrcoef(a,b)[0,1] if np.std(a)>1e-9 and np.std(b)>1e-9 else 0.0
print(f"\n{'h':>4} {'frac+coup':>10} {'frac(nocp)':>11} {'AR6':>7} {'pers':>7}")
for h in HOR:
    Fc=[];Fn=[];T=[];Pe=[]
    for o in range(split,n-h):
        Fc.append(roll(o,h,True)); Fn.append(roll(o,h,False)); T.append(Nz[o+h]); Pe.append(Nz[o])
    Fc,Fn,T,Pe=map(np.array,(Fc,Fn,T,Pe)); ar=arf(h)
    print(f"{h:>4} {C(Fc,T):+10.3f} {C(Fn,T):+11.3f} {C(ar,T):+7.3f} {C(Pe,T):+7.3f}")
