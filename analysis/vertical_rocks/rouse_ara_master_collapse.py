"""THE MASTER COLLAPSE: the medium wave (ARA vs real grain size, one curve per medium, fanned)
becomes ONE universal curve when plotted vs the DIMENSIONLESS grain diameter D* = D[Rg/nu^2]^(1/3).
=> medium is fully removed by the standard sediment-transport rescaling; mode (dimension) organizes.
Replicable, deterministic. Sources as in rouse_ara_expanded.py + Ferguson&Church 2004."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import matplotlib.cm as cm
C1=18.;C2=1.
MED={'Mars air':(0.020,5.5e-4,3.71),'Earth air':(1.2,1.5e-5,9.81),'Titan air':(5.3,1.1e-6,1.35),
'Venus air':(65.,5.4e-7,8.87),'Titan liquid':(615.,8.9e-7,1.35),'Water':(1000.,1.0e-6,9.81),
'Debris slurry':(1400.,1.0e-4,9.81)}
def ws(D,rho,nu,g,rs=2650):
    R=rs/rho-1.0; return R*g*D**2/(C1*nu+np.sqrt(0.75*C2*R*g*D**3))
def ARA(s,W=2.0): return 1+np.tanh(np.log(s)/W)
Dg=np.logspace(-6,-0.5,400); rs=2650.
order=['Mars air','Earth air','Titan air','Venus air','Titan liquid','Water','Debris slurry']
pal=cm.plasma(np.linspace(0.05,0.9,len(order)))

fig,(axL,axR)=plt.subplots(1,2,figsize=(16,6.6),facecolor="#0e1116")
for ax in (axL,axR): ax.set_facecolor("#161b22"); ax.tick_params(colors="#9aa7b4"); ax.grid(False)
for md,c in zip(order,pal):
    rho,nu,g=MED[md]; R=rs/rho-1.0
    us=1.5*0.1*np.sqrt(R*g*Dg); a=ARA(ws(Dg,rho,nu,g)/us)
    Dstar=Dg*(R*g/nu**2)**(1/3.)                     # dimensionless grain diameter
    axL.plot(Dg*1e3,a,color=c,lw=2.2,label=f"{md}")
    axR.plot(Dstar,a,color=c,lw=2.2,label=f"{md}")
for ax in (axL,axR):
    ax.axhline(1.0,color="#ffd479",lw=1,ls="--",alpha=0.6)
    ax.set_ylim(-0.05,2.05); ax.set_ylabel("vertical-ARA",color="#cbd5e1")
axL.set_xscale("log"); axR.set_xscale("log")
axL.set_xlabel("real grain size D (mm)",color="#cbd5e1")
axR.set_xlabel("dimensionless grain diameter  D* = D·[Rg/ν²]^(1/3)",color="#cbd5e1")
axL.set_title("THE MEDIUM WAVE\neach medium = same curve, shifted (fans out toward suspension)",color="#e6edf3",fontsize=12)
axR.set_title("THE COLLAPSE\nvs dimensionless grain diameter → all media fall on ONE master curve",color="#e6edf3",fontsize=12)
axL.legend(facecolor="#161b22",labelcolor="#cbd5e1",fontsize=8,loc="center left")
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rouse_ara_master_collapse.png"
plt.tight_layout(); plt.savefig(out,dpi=150,facecolor="#0e1116"); print("saved",out)

# quantify collapse: spread of ARA across media at fixed D vs at fixed D*
def spread(xaxis):
    grid=np.logspace(np.log10(0.5),np.log10(50),40) if xaxis=='Dstar' else np.logspace(-2.3,0.5,40)
    sds=[]
    for xv in grid:
        vals=[]
        for md in order:
            rho,nu,g=MED[md]; R=rs/rho-1.0
            if xaxis=='Dstar': D=xv/(R*g/nu**2)**(1/3.)
            else: D=xv*1e-3
            us=1.5*0.1*np.sqrt(R*g*D); vals.append(ARA(ws(D,rho,nu,g)/us))
        sds.append(np.std(vals))
    return np.mean(sds)
print(f"mean across-media ARA spread  at fixed real grain size D : {spread('D'):.3f}")
print(f"mean across-media ARA spread  at fixed dimensionless D*   : {spread('Dstar'):.3f}")
print("=> D* rescaling removes the medium (spread collapses).")
