import numpy as np, glob, re, json
def merge(r):
    fs=sorted(glob.glob(f'/tmp/FA_{r}_*.npz'), key=lambda p:int(re.search(r'_(\d+)\.npz',p).group(1)))
    rr=[];resp=[];bt=[]
    for f in fs:
        d=np.load(f); rr.append(d['rr']);resp.append(d['resp']);bt.append(d['bt'])
    return np.concatenate(rr),np.concatenate(resp),np.concatenate(bt)

HS=[10,30,60,120,300,600,1200]; W=15
def ffill(x):
    x=x.copy(); last=np.nan
    for i in range(len(x)):
        if np.isfinite(x[i]): last=x[i]
        elif np.isfinite(last): x[i]=last
    m=np.nanmean(x[np.isfinite(x)]) if np.isfinite(x).any() else 0.0
    x[~np.isfinite(x)]=m; return x

def sweep(rr,resp):
    resp=ffill(resp)
    N=len(rr); res={}
    for h in HS:
        # build features
        X=[];Xb=[];Y=[]
        for i in range(W,N-h):
            base=[1.0,rr[i],rr[i]-rr[i-W]]
            bf=base+[resp[i],resp[i]-resp[i-W]]
            X.append(base);Xb.append(bf);Y.append(rr[i+h])
        X=np.array(X);Xb=np.array(Xb);Y=np.array(Y)
        n=len(Y);tr=n//2
        def run(M):
            Mtr=M[:tr];Mte=M[tr:];ytr=Y[:tr];yte=Y[tr:]
            mu=Mtr.mean(0);sd=Mtr.std(0);sd[sd==0]=1
            mu[0]=0;sd[0]=1
            Ms=(Mtr-mu)/sd;Me=(Mte-mu)/sd
            b,_,_,_=np.linalg.lstsq(Ms,ytr,rcond=None)
            pred=Me@b
            return np.corrcoef(pred,yte)[0,1]
        # persistence: predict rr[i+h] = rr[i]
        idx=np.arange(W,N-h);yte=Y[tr:]
        rrnow=rr[idx][tr:]
        pc=np.corrcoef(rrnow,yte)[0,1]
        res[h]={'heart':run(X),'breath':run(Xb),'pers':pc}
    return res

out={}
for r in ['f1y01','f1o01']:
    rr,resp,bt=merge(r)
    out[r]=sweep(rr,resp)
    print(r, len(rr),'beats')
# mean
mean={}
for h in HS:
    mean[h]={k:np.mean([out[r][h][k] for r in out]) for k in ['heart','breath','pers']}
secpb=0.75  # ~0.75s per beat awake (~80bpm)
print("\nh(beats) approx-time  heart  breath  pers")
for h in HS:
    t=h*secpb
    tt=f"{t:.0f}s" if t<90 else f"{t/60:.1f}m"
    m=mean[h]
    print(f"{h:5d} {tt:>6}  {m['heart']:+.3f} {m['breath']:+.3f} {m['pers']:+.3f}")
json.dump({'per':out,'mean':mean,'secpb':secpb},open('/tmp/fa_result.json','w'),indent=1)
