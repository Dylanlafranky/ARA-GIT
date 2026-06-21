import numpy as np, json, pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
TWO_PI=2*np.pi
def cbp(arr,period,bw=0.4,order=2):
    f=1.0/period; lo=max(1e-6,(1-bw)*f/0.5); hi=min(0.999,(1+bw)*f/0.5)
    if lo>=hi: return np.zeros(len(arr))
    sos=butter(order,[lo,hi],btype='bandpass',output='sos'); return sosfilt(sos,arr-arr.mean())
def rung_state(bp,period):
    p=max(2,int(period))
    if len(bp)<2*p+5: return None
    seg=bp[-p:]; amp=(seg.max()-seg.min())/2.0
    if amp<1e-9: return None
    vr,vp=bp[-1],bp[-2]; r=max(-0.99,min(0.99,vr/max(amp,1e-9)))
    theta=np.arccos(r)*(-1.0 if vr-vp>0 else 1.0)
    look=bp[-min(len(bp),3*p):]; pk,_=find_peaks(look,distance=max(2,int(p*0.5))); tr,_=find_peaks(-look,distance=max(2,int(p*0.5)))
    fr=0.5
    if len(pk)>=1 and len(tr)>=2:
        t2=tr[-1];t1=tr[-2];m=pk[(pk>t1)&(pk<t2)]
        if len(m)>=1 and t2-t1>0: fr=min(0.85,max(0.15,(m[-1]-t1)/(t2-t1)))
    return dict(amp=float(amp),theta=float(theta),fr=float(fr),period=float(period))
def shaped(phi,fr):
    u=(phi/TWO_PI)%1.0; ff=1-fr
    return np.cos(np.pi*u/ff) if u<ff else -np.cos(np.pi*(u-ff)/fr)

def run(name,data,KS):
    n=len(data); tf=int(0.63*n); train=data[:tf]; mean=train.mean()
    rungs=[]
    for k in KS:
        P=2.0**k
        if 4*P>tf: continue
        st=rung_state(cbp(train,P),P)
        if st: rungs.append(st)
    fc_shape=np.full(n,np.nan); fc_cos=np.full(n,np.nan)
    for t in range(tf,n):
        h=t-(tf-1); s=mean; c=mean
        for r in rungs:
            phi=r["theta"]+TWO_PI*h/r["period"]
            s+=r["amp"]*shaped(phi,r["fr"]); c+=r["amp"]*np.cos(phi)
        fc_shape[t]=s; fc_cos[t]=c
    act=data[tf:]
    def cc(f): f=f[tf:]; return float(np.corrcoef(f,act)[0,1])
    # persistence-from-freeze (flat) has 0 variance -> skip; climatology mean corr=0
    print(f"{name}: N={n}, freeze at {tf} ({n-tf} pts held out, blind-generative)")
    print(f"   frozen-shape corr over WHOLE held-out = {cc(fc_shape):+.3f}   frozen-cosine = {cc(fc_cos):+.3f}")
    # also corr in first 1/3 vs last 1/3 of held-out (does it hold up long?)
    hostart=tf; hN=n-tf; q=hN//3
    for lab,(a,b) in [("near (1st third)",(0,q)),("far (last third)",(2*q,hN))]:
        fa=fc_shape[hostart+a:hostart+b]; aa=act[a:b]
        print(f"   {lab}: frozen-shape corr = {np.corrcoef(fa,aa)[0,1]:+.3f}")
    return dict(name=name,tf=tf,data=data.tolist(),fc_shape=fc_shape.tolist(),fc_cos=fc_cos.tolist())

# SOLAR
vals=[]
for line in open("TheFormula/Claude4.8/SN_m_tot.csv"):
    p=[x.strip() for x in line.split(";")]
    if len(p)>=4:
        try:
            v=float(p[3])
            if v>=0: vals.append(v)
        except: pass
solar=np.array(vals)
res_solar=run("SOLAR", solar, list(range(2,10)))
# ENSO
df=pd.read_csv("TheFormula/Claude4.8/nino34_long_anom.csv",skiprows=1,names=["date","nino34"])
df["nino34"]=pd.to_numeric(df["nino34"],errors="coerce"); enso=df[df["nino34"]>-90]["nino34"].astype(float).values
res_enso=run("ENSO", enso, list(range(2,8)))
json.dump({"solar":res_solar,"enso":res_enso}, open("/sessions/exciting-peaceful-archimedes/mnt/outputs/frozen_viz.json","w"))
print("saved frozen_viz.json")
