import sys, numpy as np, json
recs=['041','230','417','476']; HS=[5,10,20,40,80]; W=15
def feat(rr,drv,i):
    f=[1.0, rr[i], rr[i]-rr[i-W]]
    for d in drv:
        seg=d[max(0,i-W):i+1]; seg=seg[np.isfinite(seg)]
        v=seg[-1] if len(seg) else 0.0
        sl=(seg[-1]-seg[0]) if len(seg)>1 else 0.0
        f += [v, sl]
    return f
def run(rr,drivers,h):
    n=len(rr); 
    # fill nan in drivers by ffill
    drv=[]
    for d in drivers:
        d=d.copy()
        for k in range(1,len(d)):
            if not np.isfinite(d[k]): d[k]=d[k-1]
        d[~np.isfinite(d)]=np.nanmean(d[np.isfinite(d)])
        drv.append(d)
    idx=range(W,n-h)
    X=np.array([feat(rr,drv,i) for i in idx]); y=np.array([rr[i+h] for i in idx])
    m=len(idx); tr=slice(0,m//2); te=slice(m//2,m)
    mu=X[tr].mean(0); sd=X[tr].std(0); sd[sd==0]=1
    Xs=(X-mu)/sd
    beta,*_=np.linalg.lstsq(Xs[tr],y[tr],rcond=None)
    pred=Xs[te]@beta; act=y[te]
    if pred.std()<1e-6: return np.nan
    return np.corrcoef(pred,act)[0,1]
out={}
for r in recs:
    rr=np.load(f'/tmp/m_rr_{r}.npy'); spo2=np.load(f'/tmp/m_spo2_{r}.npy'); bp=np.load(f'/tmp/m_bp_{r}.npy')
    rec={}
    for h in HS:
        base=run(rr,[],h); o=run(rr,[spo2],h); b=run(rr,[bp],h); ob=run(rr,[spo2,bp],h)
        rec[h]={'heart':base,'+O2':o,'+BP':b,'+both':ob}
    out[r]=rec
# means
print("h    heart   +O2     +BP    +both   (corr; lift vs heart)")
for h in HS:
    hs=np.nanmean([out[r][h]['heart'] for r in recs])
    o =np.nanmean([out[r][h]['+O2'] for r in recs])
    b =np.nanmean([out[r][h]['+BP'] for r in recs])
    ob=np.nanmean([out[r][h]['+both'] for r in recs])
    print(f"{h:>3}  {hs:+.3f}  {o:+.3f}({o-hs:+.3f}) {b:+.3f}({b-hs:+.3f}) {ob:+.3f}({ob-hs:+.3f})")
json.dump(out,open('/tmp/mimic_lock.json','w'),indent=1)
print("\nper-record +both lift vs heart:")
for r in recs:
    print(r, {h: round(out[r][h]['+both']-out[r][h]['heart'],3) for h in HS})
