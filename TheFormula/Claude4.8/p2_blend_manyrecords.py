#!/usr/bin/env python3
"""P2 next-rung=mix on RAW, many records (cache-only). Brain/heart from slpdb cache;
ENSO/Sun windowed. Each record = a dot (snap_ARA, recon, |lag|, z). Pooled friction-lag."""
from __future__ import annotations
import json, warnings
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfiltfilt, correlate, correlation_lags, find_peaks
import phi_rung_entropy_decay_test as E
import rent_vs_ara_test as R
warnings.filterwarnings("ignore")
PHI = E.PHI
HERE = Path("/tmp/p2")
CACHE = HERE / "slpdb_cache"
rng = np.random.default_rng(7)

def norm(a):
    a=np.asarray(a,float); a=a-a.mean(); s=a.std(); return a/s if s>0 else a
def bp(x,period,ratio=1.3):
    lo=1.0/(period*ratio); hi=min(1.0/(period/ratio),0.49)
    sos=butter(3,[lo,hi],btype="band",fs=1.0,output="sos"); return sosfiltfilt(sos,x)
def phase_rand(x):
    X=np.fft.rfft(x); mag=np.abs(X); ph=np.angle(X)
    rp=rng.uniform(-np.pi,np.pi,len(ph)); rp[0]=ph[0]
    if len(x)%2==0: rp[-1]=ph[-1]
    return np.fft.irfft(mag*np.exp(1j*rp),n=len(x))
def gen_slow(s,r1,r2,r3): return bp(bp(s,r1)*bp(s,r2),r3)
def pcl(a,b,maxlag):
    a=norm(a); b=norm(b); c=correlate(b,a,mode="full")/len(a)
    lg=correlation_lags(len(b),len(a),mode="full"); m=np.abs(lg)<=maxlag
    cc=c[m]; ll=lg[m]; i=int(np.argmax(cc)); return float(cc[i]),int(ll[i])
def snap_ara(x,P,pf=0.3):
    x=np.asarray(x,float); d=max(3,int(P*0.55)); pr=pf*np.std(x)
    pks,_=find_peaks(x,distance=d,prominence=pr)
    if len(pks)<8: return None
    b=[]; r=[]
    for i in range(1,len(pks)-1):
        a,p,c=pks[i-1],pks[i],pks[i+1]
        tb=a+int(np.argmin(x[a:p+1])); ta=p+int(np.argmin(x[p:c+1]))
        bu=p-tb; re=ta-p
        if bu>0 and re>0: b.append(bu); r.append(re)
    if len(b)<5: return None
    return float(np.median(np.array(r,float)/np.array(b,float)))
def dot(x,P,nn=15):
    x=norm(x); r1,r2,r3=P,P*PHI,P*PHI**2
    if len(x)<6*r3 or r1<4: return None
    g=gen_slow(x,r1,r2,r3); ac=bp(x,r3); ml=int(round(r3))
    co,lag=pcl(g,ac,ml)
    nl=[pcl(gen_slow(phase_rand(x),r1,r2,r3),bp(phase_rand(x),r3),ml)[0] for _ in range(nn)]
    nl=np.array(nl); z=float((co-nl.mean())/(nl.std()+1e-9))
    return {"recon":co,"lag_frac":float(lag/r3),"z":z}

def main():
    fs=250.0
    print("="*72); print("P2 NEXT RUNG = MIX  RAW many-records (cache-only)"); print("="*72)
    recs=sorted(p.stem for p in CACHE.glob("*.npz"))
    print(f"cached records: {len(recs)} -> {recs}")
    S={"EEG (brain)":[], "ECG (heart)":[], "ENSO":[], "Solar":[]}
    for rec in recs:
        d=np.load(CACHE/f"{rec}.npz",allow_pickle=True); d={k:d[k] for k in d.files}
        for sysn,ch,lo,hi in [("EEG (brain)","EEG",int(fs/12),int(fs/4)),
                              ("ECG (heart)","ECG",int(0.4*fs),int(1.5*fs))]:
            if ch not in d: continue
            v=np.asarray(d[ch],float); v=v[np.isfinite(v)][:120000]
            if len(v)<6000: continue
            P=R.dominant_period(v,lo,hi); a=snap_ara(v,P); dd=dot(v,P)
            if a is None or dd is None: continue
            dd["snap_ara"]=a; dd["rec"]=rec; S[sysn].append(dd)
        print(f"  {rec} done",flush=True)
    def win(name,x,lo,hi,nw=8):
        x=np.asarray(x,float); x=x[np.isfinite(x)]; w=len(x)//nw
        for k in range(nw):
            seg=x[k*w:(k+1)*w]
            if len(seg)<200: continue
            P=R.dominant_period(seg,lo,hi); a=snap_ara(seg,P); dd=dot(seg,P,15)
            if a is None or dd is None: continue
            dd["snap_ara"]=a; dd["rec"]=f"{name}_w{k}"; S[name].append(dd)
    xe,_,_=E.load_enso(); win("ENSO",xe,24,96,2)
    xs,_,_=E.load_solar(); win("Solar",xs,90,160,1)
    print("\n"+"="*72); print("PER-SYSTEM DISTRIBUTIONS (raw)"); print("="*72)
    summ={}
    for s,ds in S.items():
        if not ds: print(f"  {s:14s} no dots"); continue
        ara=np.array([d["snap_ara"] for d in ds]); rec=np.array([d["recon"] for d in ds])
        z=np.array([d["z"] for d in ds]); lag=np.array([abs(d["lag_frac"]) for d in ds])
        fa=float(np.mean(z>=2.0))
        summ[s]={"n":len(ds),"ara_med":float(np.median(ara)),
                 "ara_iqr":[float(np.percentile(ara,25)),float(np.percentile(ara,75))],
                 "recon_med":float(np.median(rec)),"z_med":float(np.median(z)),
                 "frac_above_null":fa,"lag_med":float(np.median(lag)),
                 "dots":[{k:d[k] for k in ("snap_ara","recon","lag_frac","z","rec")} for d in ds]}
        print(f"  {s:14s} n={len(ds):2d} snapARA={np.median(ara):.3f}"
              f"[{np.percentile(ara,25):.2f},{np.percentile(ara,75):.2f}] "
              f"recon={np.median(rec):+.3f} z_med={np.median(z):+.1f} "
              f"above-null={fa*100:.0f}% |lag|={np.median(lag):.3f}")
    pool=[d for ds in S.values() for d in ds if d["z"]>=2.0]
    print("\n"+"="*72); print("P4 FRICTION-LAG vs snap-ARA (pooled above-null)"); print("="*72)
    out={"systems":summ,"phi":PHI}
    if len(pool)>=8:
        a=np.array([d["snap_ara"] for d in pool]); lg=np.array([abs(d["lag_frac"]) for d in pool])
        cphi=float(np.corrcoef(np.abs(a-PHI),lg)[0,1]); cbal=float(np.corrcoef(np.abs(a-1.0),lg)[0,1])
        print(f"  pooled N(above-null)={len(pool)}")
        print(f"  corr(|snapARA-phi|,|lag|)={cphi:+.3f}  (predict POSITIVE)")
        print(f"  corr(|snapARA-1.0|,|lag|)={cbal:+.3f}  (predict NEGATIVE)")
        out.update(pooled_N=len(pool),corr_distphi_lag=cphi,corr_dist1_lag=cbal)
    else:
        print(f"  pooled N={len(pool)} too few"); out["pooled_N"]=len(pool)
    (HERE/"p2_result.json").write_text(json.dumps(out,indent=2))
    print("\nSaved p2_result.json")

if __name__=="__main__": main()
