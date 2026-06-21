import sys, numpy as np
from scipy.signal import butter, sosfilt, find_peaks
sys.path.insert(0,"/sessions/exciting-peaceful-archimedes/mnt/SystemFormulaFolder/GIT/ARA-GIT")

# --- load solar monthly SSN ---
vals=[]
for line in open("/sessions/exciting-peaceful-archimedes/mnt/SystemFormulaFolder/GIT/ARA-GIT/TheFormula/Claude4.8/SN_m_tot.csv"):
    p=[x.strip() for x in line.split(";")]
    if len(p)<4: continue
    try: v=float(p[3])
    except: continue
    if v>=0: vals.append(v)
data=np.array(vals); n=len(data)
TWO_PI=2*np.pi

def cbp(arr, period, bw=0.4, order=2):
    f=1.0/period; lo=max(1e-6,(1-bw)*f/0.5); hi=min(0.999,(1+bw)*f/0.5)
    if lo>=hi: return np.zeros(len(arr))
    sos=butter(order,[lo,hi],btype='bandpass',output='sos'); return sosfilt(sos,arr-arr.mean())

def rung_state(bp, period):
    p=max(2,int(period))
    if len(bp)<2*p+5: return None
    seg=bp[-p:]; amp=(seg.max()-seg.min())/2.0
    if amp<1e-9: return None
    vr,vp=bp[-1],bp[-2]; r=max(-0.99,min(0.99,vr/max(amp,1e-9)))
    theta=np.arccos(r)*(-1.0 if vr-vp>0 else 1.0)
    # f_rise from last ~2 cycles (causal)
    look=bp[-min(len(bp),3*p):]
    pk,_=find_peaks(look,distance=max(2,int(p*0.5))); tr,_=find_peaks(-look,distance=max(2,int(p*0.5)))
    f_rise=0.5
    if len(pk)>=1 and len(tr)>=2:
        # last full trough->peak->trough
        t2=tr[-1]; t1=tr[-2]; mids=pk[(pk>t1)&(pk<t2)]
        if len(mids)>=1:
            c=mids[-1]; rise=c-t1; full=t2-t1
            if full>0: f_rise=min(0.85,max(0.15,rise/full))
    return dict(amp=float(amp),theta=float(theta),f_rise=float(f_rise),ara=(1-f_rise)/f_rise,period=float(period))

def shaped(phi,f_rise):
    u=(phi/TWO_PI)%1.0; ff=1-f_rise
    return np.cos(np.pi*u/ff) if u<ff else -np.cos(np.pi*(u-ff)/f_rise)

KS=list(range(2,10))  # octave periods 4..512 (solar home ~128)
HZ=[12,24,60,132]
test_start=n-700; anchors=list(range(test_start, n-max(HZ), 4))
preds={m:{h:[] for h in HZ} for m in ["persist","cosine","varA","varB"]}; truth={h:[] for h in HZ}
for t in anchors:
    past=data[:t]; mean=past.mean(); rungs=[]
    for k in KS:
        P=2.0**k
        if 4*P>t: continue
        st=rung_state(cbp(past,P),P)
        if st: rungs.append(st)
    for h in HZ:
        truth[h].append(data[t+h]); preds["persist"][h].append(past[-1])
        c=mean; a=mean; b=mean
        for s in rungs:
            phi=s["theta"]+TWO_PI*h/s["period"]
            c+=s["amp"]*np.cos(phi)
            sh=shaped(phi,s["f_rise"])
            a+=min(s["ara"],3.0)*sh
            b+=s["amp"]*min(s["ara"],3.0)*sh
        preds["cosine"][h].append(c); preds["varA"][h].append(a); preds["varB"][h].append(b)

print("=== ARA circle predictor — SOLAR, strict-causal, correlation (n_anchors=%d) ==="%len(anchors))
print("varA=diameter=ARA only | varB=amp×ARA shaped | cosine=plain Fourier (same rungs) | V4 ref corr +0.649")
print(f"{'h(mo)':>6}{'persist':>9}{'cosine':>9}{'varA':>9}{'varB':>9}")
for h in HZ:
    tr=np.array(truth[h]); row=f"{h:>6}"
    for m in ["persist","cosine","varA","varB"]:
        pr=np.array(preds[m][h]); cr=np.corrcoef(pr,tr)[0,1] if pr.std()>1e-9 else float('nan')
        row+=f"{cr:>9.3f}"
    print(row)
