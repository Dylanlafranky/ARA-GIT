import sys, numpy as np, wfdb
from wfdb import processing
r=sys.argv[1]; ci=int(sys.argv[2]); CMIN=40; fs=250
sf=ci*CMIN*60*fs; st=sf+CMIN*60*fs
h=wfdb.rdheader(r,pn_dir='slpdb'); SL=h.sig_len
if sf>=SL-fs: print(f"{r} chunk {ci}: past end"); sys.exit()
st=min(st,SL-1)
sig,f=wfdb.rdsamp(r,pn_dir='slpdb',sampfrom=sf,sampto=st)
names=f['sig_name']
def col(k):
    for i,n in enumerate(names):
        if k.lower() in n.lower(): return i
iecg=col('ECG'); ibp=col('BP'); iresp=col('Resp'); io2=col('SO2')
ecg=np.nan_to_num(sig[:,iecg])
rp=processing.gqrs_detect(sig=ecg,fs=fs); rr=np.diff(rp)/fs*1000.0; btl=rp[1:]
ok=(rr>300)&(rr<2000); rr=rr[ok]; btl=btl[ok]
bp=sig[:,ibp]; resp=sig[:,iresp]; o2=sig[:,io2] if io2 is not None else None
def bwin(x,c,half,fn):
    a=max(0,c-2*half); b=c+1; s=x[a:b]; s=s[np.isfinite(s)]
    return fn(s) if len(s) else np.nan
bpv=np.array([bwin(bp,c,fs//2,np.mean) for c in btl])
respv=np.array([bwin(resp,c,fs,np.std) for c in btl])
o2v=np.array([bwin(o2,c,fs*2,np.mean) for c in btl]) if o2 is not None else np.full(len(btl),np.nan)
bta=btl+sf  # absolute sample
np.savez(f'/tmp/CH_{r}_{ci}.npz',rr=rr,bp=bpv,resp=respv,o2=o2v,bt=bta)
print(f"{r} ch{ci}: beats={len(rr)} bp%={np.isfinite(bpv).mean():.2f} o2span={np.nanmax(o2v)-np.nanmin(o2v):.0f}")
