import os,json,warnings,numpy as np,pandas as pd
from scipy.signal import butter,filtfilt,hilbert,detrend,find_peaks
from scipy import stats
warnings.filterwarnings("ignore")
DATA="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/cgm_test"
BI=os.path.join(DATA,"healthy_bigideas");T1D=os.path.join(DATA,"t1d")
MG=18.0182;DT=5.0;FS=1.0/DT;PROM=10.0;AMP=15.0;DIST=24;HI=180.0
RUNGS=[("0.5h",0.5),("1h",1.0),("2h",2.0),("4h",4.0),("8h",8.0)]
def load_bi(s):
    df=pd.read_csv(os.path.join(BI,f"Dexcom_{s}.csv"),low_memory=False);e=df[df["Event Type"]=="EGV"].copy()
    e["ts"]=pd.to_datetime(e["Timestamp (YYYY-MM-DDThh:mm:ss)"],errors="coerce");e["g"]=pd.to_numeric(e["Glucose Value (mg/dL)"],errors="coerce")
    return e.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
def load_t1d(s):
    df=pd.read_csv(os.path.join(T1D,f"glucose_{s}.csv"));c=df[df["type"]=="cgm"].copy()
    c["ts"]=pd.to_datetime(c["date"]+" "+c["time"],errors="coerce");c["g"]=pd.to_numeric(c["glucose"],errors="coerce")*MG
    return c.dropna(subset=["ts","g"]).set_index("ts").sort_index()["g"]
def prep(s):
    f="5min";idx=pd.date_range(s.index[0].floor(f),s.index[-1].ceil(f),freq=f)
    x=s.reindex(s.index.union(idx)).sort_index().interpolate(method="time",limit=6).reindex(idx);return x.rolling(3,center=True,min_periods=2).mean().values
def band(x,ph):
    lo=1.0/(ph*np.sqrt(2)*60);hi=1.0/(ph/np.sqrt(2)*60);b,a=butter(2,[lo/(FS/2),hi/(FS/2)],btype="band");return filtfilt(b,a,x)
def rung_coup(sig):
    s=sig[~np.isnan(sig)]
    if len(s)<int(8*60/DT*3):return None
    s=detrend(s);bands=[band(s,ph) for _,ph in RUNGS];pw=np.array([np.var(b) for b in bands]);pw=pw/pw.sum()
    env=[np.abs(hilbert(b)) for b in bands];n=len(bands);cm=np.zeros((n,n))
    for i in range(n):
        for j in range(n):cm[i,j]=np.corrcoef(env[i],env[j])[0,1]
    return pw,cm
def freq(sig):
    s=sig[~np.isnan(sig)]
    if len(s)<50:return None
    days=len(s)*DT/1440.0;pk,_=find_peaks(s,distance=DIST,prominence=PROM);tr,_=find_peaks(-s,distance=DIST,prominence=PROM)
    amps=[];fr=[];snap=[];n=0
    for p in pk:
        pv=tr[tr<p];nx=tr[tr>p]
        if not len(pv) or not len(nx):continue
        a,b=pv[-1],nx[0]
        if p-a<3 or b-p<3:continue
        amp=s[p]-min(s[a],s[b])
        if amp<AMP:continue
        n+=1;amps.append(amp);fr.append((s[p]-s[b])/((b-p)*DT))
        fall=np.diff(s[p:b+1])/DT
        if len(fall):snap.append(-fall.min())
    above=s>HI;dw=[];run=0
    for v in above:
        if v:run+=1
        elif run:dw.append(run*DT);run=0
    if run:dw.append(run*DT)
    if n<3:return None
    return dict(cpd=n/days,amp=float(np.median(amps)),fr=float(np.median(fr)),
                snap=float(np.median(snap)),dwell=float(np.median(dw)) if dw else 0.0)
def coh(loader,ids):
    P=[];C=[];F=[]
    for s in ids:
        try:r=rung_coup(prep(loader(s)));f=freq(prep(loader(s)))
        except:r=None;f=None
        if r:P.append(r[0]);C.append(r[1])
        if f:F.append(f)
    return np.array(P),np.array(C),F
HP,HC,HF=coh(load_bi,[f"{i:03d}" for i in range(1,17)])
DP,DC,DF=coh(load_t1d,[f"{i:03d}" for i in range(1,10)])
names=[r[0] for r in RUNGS]
def cd(a,b):
    a,b=np.array(a),np.array(b);return round((sum((x>b).sum() for x in a)-sum((x<b).sum() for x in a))/(len(a)*len(b)),2)
rf={}
for k in ("cpd","amp","fr","snap","dwell"):
    h=[x[k] for x in HF];d=[x[k] for x in DF]
    rf[k]={"h":round(float(np.median(h)),2),"d":round(float(np.median(d)),2),"delta":cd(h,d)}
res=json.load(open("_cgm_results.json"))
res["rung_power"]={"names":names,
    "h":[round(float(x),3) for x in np.median(HP,axis=0)],
    "d":[round(float(x),3) for x in np.median(DP,axis=0)],
    "h_all":[[round(float(v),3) for v in HP[:,i]] for i in range(len(names))],
    "d_all":[[round(float(v),3) for v in DP[:,i]] for i in range(len(names))]}
res["coupling"]={"names":names,
    "h":[[round(float(v),2) for v in row] for row in np.median(HC,axis=0)],
    "d":[[round(float(v),2) for v in row] for row in np.median(DC,axis=0)]}
res["ridge_failure"]=rf
json.dump(res,open("_cgm_results.json","w"))
print("rung power H:",res["rung_power"]["h"],"T1D:",res["rung_power"]["d"])
print("ridge_failure:",rf)
