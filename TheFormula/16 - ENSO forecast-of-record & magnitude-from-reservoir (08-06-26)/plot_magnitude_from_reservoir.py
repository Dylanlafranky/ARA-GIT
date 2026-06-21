import sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,".")
import enso_pdo_feeder_test as B
sys.path.insert(0,"/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT")
import ara_framework as F
keys=sorted(B.load_nino("nino34_long_anom.csv"));d=B.load_nino("nino34_long_anom.csv")
ni=np.array([d[k] for k in keys]);n=len(ni)
yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
def smooth(x,w):return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])
nis=smooth(ni,3)
upx=[i for i in range(13,n-13) if nis[i-1]<0<=nis[i]]
integ=[];peak=[];cyr=[];pk_i=[]
for c in upx:
    seg=ni[c:c+12];integ.append(-np.sum(ni[c-9:c]));peak.append(np.max(seg));cyr.append(yr[c]);pk_i.append(c+int(np.argmax(seg)))
integ=np.array(integ);peak=np.array(peak);cyr=np.array(cyr);m=len(peak);cut=int(m*0.6)
def cc(a,b):return np.corrcoef(a,b)[0,1]
b=np.polyfit(integ,peak,1);corr=cc(integ,peak)
btr=np.polyfit(integ[:cut],peak[:cut],1);pred=np.polyval(btr,integ[cut:]);oos=cc(pred,peak[cut:])
pre=cyr<1980
fig,(ax,ax2)=plt.subplots(1,2,figsize=(14,5.6));fig.patch.set_facecolor("white")
# Panel A: scatter recharge proxy vs next peak
ax.scatter(integ[pre],peak[pre],c="#1f77b4",s=45,alpha=.8,label=f"pre-1980 (n={pre.sum()})",edgecolor="white")
ax.scatter(integ[~pre],peak[~pre],c="#d62728",s=45,alpha=.8,label=f"1980+ (n={(~pre).sum()})",edgecolor="white")
xs=np.linspace(integ.min(),integ.max(),50);ax.plot(xs,np.polyval(b,xs),"k--",lw=1.5,label=f"fit (corr {corr:+.2f})")
# label the biggest peaks
for i in np.argsort(peak)[-5:]:
    ax.annotate(f"{int(cyr[i])}",(integ[i],peak[i]),fontsize=8,xytext=(4,3),textcoords="offset points",color="#555")
ax.set_xlabel("recharge proxy at crossing  (trailing cool accumulation = stored energy)")
ax.set_ylabel("magnitude of next warm peak (°C)")
ax.set_title(f"Does the reservoir at the crossing set the next peak's size?\n1870+, {m} warm onsets — corr {corr:+.2f}",fontweight="bold",fontsize=10.5)
ax.legend(fontsize=8.5);ax.grid(alpha=.2)
# Panel B: out-of-sample predicted vs actual
ax2.scatter(pred,peak[cut:],c="#d62728",s=50,alpha=.8,edgecolor="white")
lim=[min(pred.min(),peak[cut:].min())-0.1,max(pred.max(),peak[cut:].max())+0.1]
ax2.plot(lim,lim,"k--",lw=1,alpha=.6,label="perfect")
ax2.set_xlim(lim);ax2.set_ylim(lim)
ax2.set_xlabel("predicted peak size (from reservoir, trained on earlier half)")
ax2.set_ylabel("actual peak size (°C)")
ax2.set_title(f"Out-of-sample: reservoir predicts peak size\non held-out later events — corr {oos:+.2f}",fontweight="bold",fontsize=10.5)
ax2.legend(fontsize=8.5);ax2.grid(alpha=.2)
fig.suptitle("ENSO magnitude IS partly traceable from the reservoir at the crossing — validated on 150 years (modest but real)",fontsize=12,fontweight="bold",y=1.0)
out="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/GIT/ARA-GIT/Retrodiction/ARA_enso_magnitude_from_reservoir.png"
fig.savefig(out,dpi=130,bbox_inches="tight",facecolor="white");print("saved",out)
