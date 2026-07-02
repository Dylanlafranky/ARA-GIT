import os, sys, json
import numpy as np, scipy.io as sio
from scipy.signal import find_peaks, hilbert, butter, filtfilt
HERE=os.path.dirname(os.path.abspath(__file__))
SCR=os.path.join(HERE,"..","pendulum_scripts"); sys.path.insert(0,SCR)
os.environ.setdefault("PENDULUM_DATA", os.path.join(SCR,"data"))
from pendulum_common import load_triple, rest_centered, wrap
DATA=os.path.join(SCR,"data")
def r(a,p=4): a=np.asarray(a,float); return [round(float(x),p) for x in a]

def load_driven(path,q=20):
    m=sio.loadmat(path)
    th={i:m[f'Theta{i}'].ravel()[::q] for i in (1,2,3)}
    vel={i:m[f'dTheta{i}'].ravel()[::q] for i in (1,2,3)}
    t=m['Time'].ravel()[::q]; dt=float(np.asarray(m['dt']).ravel()[0]); fs=1/(dt*q)
    return t,th,vel,fs

def spectrum(x,fs,fmax=4.0,npts=600):
    x=x-x.mean();N=len(x);f=np.fft.rfftfreq(N,1/fs);P=np.abs(np.fft.rfft(x*np.hanning(N)))**2
    f,P=f[1:],P[1:];m=f<fmax;f,P=f[m],P[m];s=max(1,len(f)//npts)
    return f[::s],np.log10(P[::s]+1e-12)

def metrics(t,th_raw,fs):
    th=rest_centered(th_raw); out={}
    # geometry
    geom={}
    for i in (1,2,3):
        x=th[i]-th[i].mean();N=len(x)
        f=np.fft.rfftfreq(N,1/fs);P=np.abs(np.fft.rfft(x*np.hanning(N)))**2;f,P=f[1:],P[1:]
        fp=f[np.argmax(P)];band=(f>0.8*fp)&(f<1.2*fp)
        geom[i]=dict(amp=round(float(x.std()*np.sqrt(2)),3),domP=round(float(1/fp),2),
                     clk=round(float(P[band].sum()/P.sum()),2))
    # spectra
    spec={}
    for i in (1,2,3):
        f,lp=spectrum(th[i]-th[i].mean(),fs); spec[i]={"f":r(f,3),"P":r(lp,2)}
    # envelopes (carrier + env), ~plot res
    bb,aa=butter(2,[0.3,1.5],btype='band',fs=fs)
    env={};carr={};decay={}
    sub=max(1,int(round(fs/50)))
    tt=t[::sub]
    for i in (1,2,3):
        c=filtfilt(bb,aa,th[i]-th[i].mean());e=np.abs(hilbert(c))
        env[i]=r(e[::sub],4);carr[i]=r(c[::sub],4)
        b6=np.array_split(e,6);decay[i]=round(float(b6[0].mean()/b6[-1].mean()),2)
    # coupling
    bb2,aa2=butter(2,[0.3,1.3],btype='band',fs=fs)
    ph={i:np.angle(hilbert(filtfilt(bb2,aa2,th[i]-th[i].mean()))) for i in (1,2,3)}
    def plv(x,y):d=wrap(ph[x]-ph[y]);return round(float(np.abs(np.mean(np.exp(1j*d)))),3)
    A=np.vstack([th[1],th[2],th[3]]);C=np.corrcoef(A)
    p13=(C[0,2]-C[0,1]*C[2,1])/np.sqrt((1-C[0,1]**2)*(1-C[2,1]**2))
    coup=dict(plv12=plv(1,2),plv23=plv(2,3),plv13=plv(1,3),
              corr13=round(float(C[0,2]),3),partial13=round(float(p13),3))
    # chain transfer adjacent rungs
    def lag_gain(a,b):
        x=(th[a]-th[a].mean());y=(th[b]-th[b].mean())
        xn=x/x.std();yn=y/y.std();ml=int(2.0*fs)
        cc=np.correlate(yn,xn,'full')/len(xn);lags=np.arange(-len(xn)+1,len(xn))
        sel=np.abs(lags)<=ml;cc=cc[sel];lags=lags[sel];k=np.argmax(np.abs(cc))
        return round(float(lags[k]/fs),3),round(float(y.std()/x.std()),3)
    l12,g12=lag_gain(1,2);l23,g23=lag_gain(2,3)
    chain=dict(gain12=g12,gain23=g23,lag12=l12,lag23=l23)
    # irreversibility deriv-skew
    irr={}
    for i in (1,2,3):
        d=np.gradient(th[i]-th[i].mean());irr[i]=round(float(np.mean(d**3)/(np.mean(d**2)**1.5)),3)
    # leadership share
    def ext_idx(x):
        prom=0.4*x.std();dist=int(0.4*fs)
        hi,_=find_peaks(x,prominence=prom,distance=dist);lo,_=find_peaks(-x,prominence=prom,distance=dist)
        return np.sort(np.concatenate([hi,lo]))
    E={i:ext_idx(th[i]-th[i].mean()) for i in (1,2,3)}
    leaders=[]
    for i1 in E[1]:
        cand={1:i1};ok=True
        for a in (2,3):
            j=E[a][np.argmin(np.abs(E[a]-i1))]
            if abs(j-i1)/fs<0.5:cand[a]=j
            else:ok=False
        if ok:leaders.append(min(cand,key=lambda a:cand[a]))
    L=np.array(leaders)
    share={i:(round(100*float(np.mean(L==i)),0) if len(L) else 0) for i in (1,2,3)}
    share["n"]=int(len(L))
    return dict(geom=geom,spec=spec,env=env,carr=carr,decay=decay,coup=coup,chain=chain,irr=irr,
                share=share,t=r(tt,3))

D={}
tu,thu,_,fsu=load_triple("run1",decimate=20); D["undriven"]=metrics(tu,thu,fsu)
td,thd,_,fsd=load_driven(os.path.join(DATA,"TripleDataWithControl_1_Dt_0_0001.mat"),q=20); D["driven"]=metrics(td,thd,fsd)

# the real drive from the single file (the one place we see the cart)
m=sio.loadmat(os.path.join(DATA,"SingleDataWithControl_1_Dt_0_0001.mat"),struct_as_record=False,squeeze_me=True)
def sig(n):return np.asarray(m[n].time,float),np.asarray(m[n].signals.values,float).ravel()
tdist,dist=sig("Distance");_,th1s=sig("Theta1");fss=1/np.median(np.diff(tdist))
sub=max(1,int(round(fss/50)))
fpk=np.fft.rfftfreq(len(dist),1/fss);Pk=np.abs(np.fft.rfft((dist-dist.mean())*np.hanning(len(dist))))**2
fpk,Pk=fpk[1:],Pk[1:];dP=1/fpk[np.argmax(Pk)]
dd=np.diff(dist);rf=np.sum(dd>0)/max(np.sum(dd<0),1)
D["drive"]=dict(t=r((tdist-tdist[0])[::sub],3),dist=r(dist[::sub],4),th1=r(th1s[::sub],4),
                period=round(float(dP),2),amp=round(float(dist.std()*np.sqrt(2)),3),
                risefall=round(float(rf),3))
open(os.path.join(HERE,"_driven_data.json"),"w").write(json.dumps(D))
print("OK. size KB:",round(len(json.dumps(D))/1024))
print("undriven domP:",[D["undriven"]["geom"][i]["domP"] for i in (1,2,3)],
      "driven domP:",[D["driven"]["geom"][i]["domP"] for i in (1,2,3)])
print("decay undriven:",D["undriven"]["decay"],"driven:",D["driven"]["decay"])
print("drive period:",D["drive"]["period"],"risefall:",D["drive"]["risefall"])
