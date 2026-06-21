import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
TWO_PI=2*np.pi
df=pd.read_csv("/sessions/exciting-peaceful-archimedes/mnt/SystemFormulaFolder/GIT/ARA-GIT/TheFormula/Claude4.8/nino34_long_anom.csv",skiprows=1,names=["date","nino34"])
df["nino34"]=pd.to_numeric(df["nino34"],errors="coerce")
data=df[df["nino34"]>-90]["nino34"].astype(float).values; n=len(data)

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
    f_rise=0.5
    if len(pk)>=1 and len(tr)>=2:
        t2=tr[-1];t1=tr[-2];mids=pk[(pk>t1)&(pk<t2)]
        if len(mids)>=1:
            c=mids[-1];rise=c-t1;full=t2-t1
            if full>0: f_rise=min(0.85,max(0.15,rise/full))
    return dict(amp=float(amp),theta=float(theta),f_rise=float(f_rise),ara=(1-f_rise)/f_rise,period=float(period))
def shaped(phi,f_rise):
    u=(phi/TWO_PI)%1.0; ff=1-f_rise
    return np.cos(np.pi*u/ff) if u<ff else -np.cos(np.pi*(u-ff)/f_rise)

KS=list(range(2,8)); HZ=[3,6,12,18,24]
test_start=n-500; anchors=list(range(test_start,n-max(HZ),3))
preds={m:{h:[] for h in HZ} for m in ["persist","cosine","varA","varB","shapeonly"]}; truth={h:[] for h in HZ}
for t in anchors:
    past=data[:t]; mean=past.mean(); rungs=[]
    for k in KS:
        P=2.0**k
        if 4*P>t: continue
        st=rung_state(cbp(past,P),P)
        if st: rungs.append(st)
    for h in HZ:
        truth[h].append(data[t+h]); preds["persist"][h].append(past[-1])
        c=a=b=so=mean
        for s in rungs:
            phi=s["theta"]+TWO_PI*h/s["period"]; sh=shaped(phi,s["f_rise"]); ar=min(s["ara"],3.0)
            c+=s["amp"]*np.cos(phi); a+=ar*sh; b+=s["amp"]*ar*sh; so+=s["amp"]*sh
        preds["cosine"][h].append(c); preds["varA"][h].append(a); preds["varB"][h].append(b); preds["shapeonly"][h].append(so)
print("=== ARA circle predictor — ENSO NINO3.4, strict-causal, correlation (n_anchors=%d, N=%d) ==="%(len(anchors),n))
print("cosine=Fourier | varA=diam=ARA only | varB=amp×ARA shaped | shapeonly=amp×shaped(no ARA weight)")
print(f"{'h(mo)':>6}{'persist':>9}{'cosine':>9}{'shapeonly':>10}{'varB':>9}{'varA':>9}")
for h in HZ:
    tr=np.array(truth[h]); row=f"{h:>6}"
    for m in ["persist","cosine","shapeonly","varB","varA"]:
        pr=np.array(preds[m][h]); cr=np.corrcoef(pr,tr)[0,1] if pr.std()>1e-9 else float('nan'); row+=f"{cr:>9.3f}" if m!="shapeonly" else f"{cr:>10.3f}"
    print(row)
