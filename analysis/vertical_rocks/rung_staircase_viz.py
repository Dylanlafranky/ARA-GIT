"""The rung STAIRCASE — two fully-worked jumps, same stuck->cross->taper shape, new higher component each time."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
G=6.674e-11
# ---- jump 1 data (roundness vs size) ----
B1=[("Itokawa",(0.268,0.147,0.104)),("Eros",(17.2,5.6,5.6)),("Gaspra",(9.1,5.2,4.4)),("Ida",(29.9,12.7,9.3)),
("Bennu",(0.283,0.272,0.249)),("Ryugu",(0.502,0.495,0.440)),("Mathilde",(33.,24.,23.)),("Lutetia",(60.5,50.5,37.5)),
("Phobos",(13.,11.4,9.1)),("Deimos",(7.5,6.1,5.5)),("Amalthea",(125.,73.,64.)),("Janus",(101.7,93.,76.3)),
("Epimetheus",(64.9,57.3,53.)),("Hyperion",(180.1,133.,102.7)),("Vesta",(286.3,278.6,223.2)),("Pallas",(275.,258.,238.)),
("Proteus",(218.,208.,201.)),("Mimas",(207.8,196.7,190.6)),("Miranda",(240.,234.2,232.9)),("Enceladus",(256.6,251.4,248.3)),
("Ceres",(482.1,482.1,445.9)),("Tethys",(538.4,528.3,526.3)),("Dione",(563.4,561.3,559.6)),("Rhea",(765.,763.1,762.4)),
("Iapetus",(745.7,745.7,712.1)),("Moon",(1738.1,1738.1,1736.)),("Mars",(3396.2,3396.2,3376.2)),("Earth",(6378.1,6378.1,6356.8))]
n1=[b[0] for b in B1]; Rm=np.array([(b[1][0]*b[1][1]*b[1][2])**(1/3.) for b in B1]); ca=np.array([b[1][2]/b[1][0] for b in B1])
x1=np.log10(Rm*1000.)
def logi(x,lo,hi,x0,k): return lo+(hi-lo)/(1+np.exp(-k*(x-x0)))
p1,_=curve_fit(logi,x1,ca,p0=[0.6,0.98,5.2,6],maxfev=40000); x0_1=p1[2]
# ---- jump 2 data (flattening vs spin) ----
B2=[("Venus",6051.8,6051.8,5832.5,4.867e24),("Mercury",2440.5,2438.3,1407.6,3.301e23),("Pluto",1188,1188,153.3,1.303e22),
("Moon",1738.1,1736.,655.7,7.346e22),("Mars",3396.2,3376.2,24.62,6.417e23),("Earth",6378.1,6356.8,23.93,5.972e24),
("Uranus",25559,24973,17.24,8.681e25),("Neptune",24764,24341,16.11,1.024e26),("Ceres",482,446,9.07,9.38e20),
("Jupiter",71492,66854,9.925,1.898e27),("Saturn",60268,54364,10.656,5.683e26),("Haumea",1161,513,3.915,4.006e21)]
n2=[b[0] for b in B2]; a=np.array([b[1] for b in B2])*1e3; c=np.array([b[2] for b in B2])*1e3
P=np.array([b[3] for b in B2])*3600.; M=np.array([b[4] for b in B2])
f=(a-c)/a; mspin=(2*np.pi/P)**2*a**3/(G*M)

fig=plt.figure(figsize=(16,8.4),facecolor="#0e1116")
gs=fig.add_gridspec(2,2,height_ratios=[0.9,3.4],hspace=0.32,wspace=0.16)
# ---- top: conceptual staircase strip ----
axT=fig.add_subplot(gs[0,:]); axT.set_facecolor("#0e1116"); axT.axis("off")
steps=[(0.03,"RUNG 0\nirregular\n(strength-locked)","#c98a4a"),
       (0.255,"— jump 1 →\nhigher component:\nSELF-GRAVITY","#7CFC9A"),
       (0.46,"RUNG 1\nSPHERE\n(gravity-held)","#5aa0ff"),
       (0.685,"— jump 2 →\nhigher component:\nSPIN","#7CFC9A"),
       (0.86,"RUNG 2\nflattened → breakup\n(Jacobi/shedding)","#b197fc")]
for xx,txt,col in steps:
    axT.text(xx,0.5,txt,color=col,fontsize=10,ha="center",va="center",fontweight="bold",transform=axT.transAxes)
for xx in (0.145,0.35,0.575,0.775):
    axT.annotate("",xy=(xx+0.05,0.5),xytext=(xx,0.5),xycoords="axes fraction",
                 arrowprops=dict(arrowstyle="->",color="#9aa7b4",lw=1.4))
axT.text(0.5,1.02,"THE RUNG STAIRCASE — base units stall at a pole; an emergent HIGHER component crosses the octave; it maxes out; repeat",
         color="#e6edf3",fontsize=12.5,ha="center",va="bottom",transform=axT.transAxes,fontweight="bold")
# ---- jump 1 panel ----
ax1=fig.add_subplot(gs[1,0]); ax1.set_facecolor("#161b22"); ax1.tick_params(colors="#9aa7b4"); ax1.grid(False)
ax1.axvspan(x1.min()-0.3,x0_1-0.25,color="#c98a4a",alpha=0.10); ax1.axvspan(x0_1-0.25,x0_1+0.35,color="#7CFC9A",alpha=0.12); ax1.axvspan(x0_1+0.35,x1.max()+0.4,color="#5aa0ff",alpha=0.09)
xs=np.linspace(x1.min()-0.3,x1.max()+0.4,300); ax1.plot(xs,logi(xs,*p1),color="#eaeff5",lw=2.4,zorder=4)
for i in range(len(B1)):
    ax1.scatter(x1[i],ca[i],s=48,c=("#c98a4a" if x1[i]<x0_1 else "#5aa0ff"),edgecolors="#0e1116",lw=0.6,zorder=3)
for nm in("Itokawa","Eros","Mimas","Earth"):
    i=n1.index(nm); ax1.annotate(nm,(x1[i],ca[i]),textcoords="offset points",xytext=(0,7),fontsize=7,color="#cdd6e0",ha="center")
ax1.axvline(x0_1,color="#ffd479",lw=1,ls="--",alpha=0.6)
ax1.text(0.5,0.94,"stuck: strength ρ=−0.03 → gravity crosses (166 km) → sphere ρ=+0.78",transform=ax1.transAxes,color="#9aa7b4",fontsize=8,ha="center")
ax1.set_xlabel("log₁₀ radius (m)",color="#cbd5e1"); ax1.set_ylabel("roundness c/a",color="#cbd5e1"); ax1.set_ylim(0.3,1.03)
ax1.set_title("JUMP 1 · strength → gravity",color="#e6edf3",fontsize=11.5)
# ---- jump 2 panel ----
ax2=fig.add_subplot(gs[1,1]); ax2.set_facecolor("#161b22"); ax2.tick_params(colors="#9aa7b4"); ax2.grid(False)
ax2.axvspan(1e-5,1e-2,color="#5aa0ff",alpha=0.10); ax2.axvspan(1e-2,3e-1,color="#7CFC9A",alpha=0.12); ax2.axvspan(3e-1,3,color="#b197fc",alpha=0.12)
mm=np.logspace(-5,0.2,200); ax2.plot(mm,1.25*mm,color="#eaeff5",lw=1.8,ls=":")
ax2.axvline(1.0,color="#ff8a8a",lw=1.2,ls="--"); ax2.text(1.03,0.5,"m=1 breakup",color="#ff8a8a",fontsize=8,rotation=90,va="center")
ax2.scatter(mspin,f,s=70,c="#eaeff5",edgecolors="#0e1116",lw=0.8,zorder=4)
for nm in("Venus","Earth","Saturn","Jupiter","Haumea","Ceres"):
    i=n2.index(nm); ax2.annotate(nm,(mspin[i],f[i]),textcoords="offset points",xytext=(0,8),fontsize=7.5,color="#cdd6e0",ha="center")
ax2.text(0.5,0.94,"stuck: sphere → spin crosses (m~1) → breakup;  f∼spin ρ=+0.96, not size/mass",transform=ax2.transAxes,color="#9aa7b4",fontsize=8,ha="center")
ax2.set_xscale("log"); ax2.set_xlabel("spin parameter m = ω²a³/GM",color="#cbd5e1"); ax2.set_ylabel("flattening f=(a−c)/a",color="#cbd5e1")
ax2.set_xlim(8e-6,3); ax2.set_ylim(-0.02,0.60)
ax2.set_title("JUMP 2 · gravity → spin",color="#e6edf3",fontsize=11.5)
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rung_staircase.png"
plt.savefig(out,dpi=150,facecolor="#0e1116",bbox_inches="tight"); print("saved",out)
