#!/usr/bin/env python3
"""Endpoint (A-node) vs Exchange-channel mix test on REAL slpdb EEG.
A-node   = raw EEG anchored at theta scale -> should BUILD its phi^2-up rung (pass, z>=2).
Exchange = gamma amplitude envelope (theta<->gamma shuttle); slow rhythm INHERITED from
           theta phase -> should FAIL (high recon possible, low z: phase-scramble costs little).
RAW-data rule: minimal causal-equivalent bandpass; mix test anchored where r3 stays in-band.
"""
import json, warnings
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfiltfilt, correlate, correlation_lags, hilbert
warnings.filterwarnings("ignore")
PHI=(1+5**0.5)/2; FS=250.0
HERE=Path("/tmp/p2"); CACHE=HERE/"slpdb_cache"; rng=np.random.default_rng(7)

def norm(a):
    a=np.asarray(a,float); a=a-a.mean(); s=a.std(); return a/s if s>0 else a
def bp(x,period,ratio=1.3):
    lo=1.0/(period*ratio); hi=min(1.0/(period/ratio),0.49)
    sos=butter(3,[lo,hi],btype="band",fs=1.0,output="sos"); return sosfiltfilt(sos,x)
def bp_hz(x,f1,f2,fs=FS):
    sos=butter(3,[f1/(fs/2),f2/(fs/2)],btype="band",output="sos"); return sosfiltfilt(sos,x)
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
def dot(x,P,nn=15):
    x=norm(x); r1,r2,r3=P,P*PHI,P*PHI**2
    if len(x)<6*r3 or r1<4: return None
    g=gen_slow(x,r1,r2,r3); ac=bp(x,r3); ml=int(round(r3))
    co,lag=pcl(g,ac,ml)
    nl=[pcl(gen_slow(phase_rand(x),r1,r2,r3),bp(phase_rand(x),r3),ml)[0] for _ in range(nn)]
    nl=np.array(nl); z=float((co-nl.mean())/(nl.std()+1e-9))
    return {"recon":co,"lag_frac":float(lag/r3),"z":z}

# theta scale anchor: P_theta in samples. theta~6 Hz -> ~41.7 samples. Use 6 Hz.
P_THETA=FS/6.0
def main():
    recs=sorted(p.stem for p in CACHE.glob("*.npz"))
    print("="*72); print("ENDPOINT (A-node) vs EXCHANGE-channel mix test  REAL EEG"); print("="*72)
    print(f"records={len(recs)}  fs={FS}  P_theta={P_THETA:.1f} samp (~6 Hz)")
    A=[]; X=[]
    for rec in recs:
        d=np.load(CACHE/f"{rec}.npz",allow_pickle=True)
        if "EEG" not in d.files: continue
        v=np.asarray(d["EEG"],float); v=v[np.isfinite(v)][:120000]
        if len(v)<6000: continue
        # A-node: raw EEG at theta scale
        da=dot(v,P_THETA)
        # Exchange: gamma (30-50 Hz) amplitude envelope -> its slow fluctuation
        gam=bp_hz(v,30,50); env=np.abs(hilbert(gam))
        dx=dot(env,P_THETA)
        if da is None or dx is None: continue
        da["rec"]=rec; dx["rec"]=rec; A.append(da); X.append(dx)
        print(f"  {rec}: A-node z={da['z']:+5.1f} recon={da['recon']:+.3f} | "
              f"exch z={dx['z']:+5.1f} recon={dx['recon']:+.3f}",flush=True)
    def summ(name,L):
        z=np.array([d["z"] for d in L]); rc=np.array([d["recon"] for d in L])
        fa=float(np.mean(z>=2.0))
        print(f"  {name:16s} n={len(L):2d}  z_med={np.median(z):+5.1f}  "
              f"recon_med={np.median(rc):+.3f}  pass(z>=2)={fa*100:.0f}%")
        return {"n":len(L),"z_med":float(np.median(z)),"recon_med":float(np.median(rc)),
                "pass_frac":fa,"z":[float(x) for x in z],"recon":[float(x) for x in rc]}
    print("\n"+"="*72); print("SUMMARY"); print("="*72)
    sa=summ("A-node (raw EEG)",A); sx=summ("Exchange (gamma env)",X)
    # paired: per-record does A pass while exchange fails?
    pair=[(a["z"],x["z"]) for a,x in zip(A,X)]
    both=sum(1 for az,xz in pair if az>=2.0 and xz<2.0)
    print(f"\n  records where A-node PASSES and exchange FAILS: {both}/{len(pair)}")
    print(f"  median recon: A={sa['recon_med']:+.3f} vs exch={sx['recon_med']:+.3f} "
          f"(exchange can have HIGH recon = inherited, but LOW z)")
    out={"phi":PHI,"P_theta":P_THETA,"A_node":sa,"exchange":sx,
         "both_split":both,"n_pairs":len(pair)}
    (HERE/"endpoint_exchange_result.json").write_text(json.dumps(out,indent=2))
    print("\nSaved endpoint_exchange_result.json")
if __name__=="__main__": main()
