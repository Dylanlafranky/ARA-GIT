"""Interactive OFFLINE html of the two vertical-ARA waves (real measured shape data)."""
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import spearmanr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import get_plotlyjs

BODIES = [
 ("Itokawa",(0.268,0.147,0.104),"S",1.9),("Eros",(17.2,5.6,5.6),"S",2.67),
 ("Gaspra",(9.1,5.2,4.4),"S",2.7),("Ida",(29.9,12.7,9.3),"S",2.6),
 ("Bennu",(0.283,0.272,0.249),"S",1.19),("Ryugu",(0.502,0.495,0.440),"S",1.19),
 ("Mathilde",(33.0,24.0,23.0),"S",1.3),("Lutetia",(60.5,50.5,37.5),"S",3.4),
 ("Phobos",(13.0,11.4,9.1),"S",1.88),("Deimos",(7.5,6.1,5.5),"S",1.47),
 ("Amalthea",(125.,73.0,64.0),"S",0.86),("Janus",(101.7,93.0,76.3),"S",0.63),
 ("Epimetheus",(64.9,57.3,53.0),"S",0.64),("Hyperion",(180.1,133.0,102.7),"S",0.54),
 ("Vesta",(286.3,278.6,223.2),"T",3.46),("Pallas",(275.,258.,238.),"T",2.9),
 ("Proteus",(218.,208.,201.),"T",1.3),("Mimas",(207.8,196.7,190.6),"G",1.15),
 ("Miranda",(240.,234.2,232.9),"G",1.2),("Enceladus",(256.6,251.4,248.3),"G",1.61),
 ("Ceres",(482.1,482.1,445.9),"G",2.16),("Tethys",(538.4,528.3,526.3),"G",0.98),
 ("Dione",(563.4,561.3,559.6),"G",1.48),("Rhea",(765.0,763.1,762.4),"G",1.24),
 ("Iapetus",(745.7,745.7,712.1),"G",1.09),("Titania",(788.4,788.4,788.4),"G",1.66),
 ("Moon",(1738.1,1738.1,1736.0),"G",3.34),("Mars",(3396.2,3396.2,3376.2),"G",3.93),
 ("Earth",(6378.1,6378.1,6356.8),"G",5.51),("Saturn",(60268.,60268.,54364.),"R",0.69),
 ("Jupiter",(71492.,71492.,66854.),"R",1.33),
]
COL={"S":"#c98a4a","T":"#e0c060","G":"#5aa0ff","R":"#b197fc"}
LAB={"S":"strength / cohesion","T":"transition","G":"gravity (rounded)","R":"rotational flattening"}
names=[b[0] for b in BODIES]; reg=[b[2] for b in BODIES]; dens=[b[3] for b in BODIES]
Rmean=np.array([(b[1][0]*b[1][1]*b[1][2])**(1/3.) for b in BODIES])
ca=np.array([b[1][2]/b[1][0] for b in BODIES])
x=np.log10(Rmean*1000.0)

def logistic(xx,lo,hi,x0,k): return lo+(hi-lo)/(1+np.exp(-k*(xx-x0)))
m=np.array([r!="R" for r in reg])
popt,_=curve_fit(logistic,x[m],ca[m],p0=[0.4,0.97,5.3,3.0],maxfev=20000)
x0_fit=popt[2]; potatoR=10**x0_fit
rho,_=spearmanr(x[m],ca[m])
rng=np.random.default_rng(0)
null=[spearmanr(x[m],rng.permutation(ca[m]))[0] for _ in range(5000)]
p_null=(np.sum(np.array(null)>=rho)+1)/(len(null)+1)
fitted=logistic(x,*popt); resid=ca-fitted

# wave 2
logR=x.copy()
fa_x=np.array([-2,3,5,6,6.8]); fa_y=np.array([3.0,4.5,5.5,6.5,7.7])
logTform=np.interp(logR,fa_x,fa_y)
D=2*Rmean
logTerode=np.minimum(np.log10(0.3e9)+1.1*np.log10(D/0.8),np.log10(4.6e9))
ratio=logTerode-logTform
mr=m.copy()

fig=make_subplots(rows=1,cols=2,horizontal_spacing=0.08,
   subplot_titles=(f"WAVE 1 · size → roundness (real triaxial axes)<br>"
                   f"<span style='font-size:12px;color:#9aa7b4'>Spearman ρ={rho:.2f} · shuffle-null p={p_null:.4f} · transition R≈{potatoR/1000:.0f} km</span>",
                   "WAVE 2 · formation → erosion (order-of-magnitude, fenced)<br>"
                   "<span style='font-size:12px;color:#9aa7b4'>persistence per build-cost · peak ≈ small-asteroid scale</span>"))
# fit curve + transition
xs=np.linspace(x.min(),x.max(),300)
fig.add_trace(go.Scatter(x=xs,y=logistic(xs,*popt),mode="lines",line=dict(color="#7fb0ff",width=2),
   name="logistic fit",hoverinfo="skip"),row=1,col=1)
fig.add_vline(x=x0_fit,line=dict(color="#ffd479",width=1,dash="dash"),row=1,col=1)
# points by regime
for k in ["S","T","G","R"]:
    idx=[i for i in range(len(BODIES)) if reg[i]==k]
    fig.add_trace(go.Scatter(x=[x[i] for i in idx],y=[ca[i] for i in idx],mode="markers",
       marker=dict(size=11,color=COL[k],line=dict(color="#0e1116",width=1)),name=LAB[k],
       text=[f"<b>{names[i]}</b><br>mean R = {Rmean[i]:.1f} km<br>c/a = {ca[i]:.3f}"
             f"<br>density = {dens[i]} g/cc<br>off-curve resid = {resid[i]:+.3f}" for i in idx],
       hovertemplate="%{text}<extra></extra>"),row=1,col=1)
# wave 2 points
fig.add_trace(go.Scatter(x=logR[mr],y=ratio[mr],mode="lines",line=dict(color="#9aa7b4",width=1),
   opacity=0.4,hoverinfo="skip",showlegend=False),row=1,col=2)
for k in ["S","T","G"]:
    idx=[i for i in range(len(BODIES)) if reg[i]==k and m[i]]
    fig.add_trace(go.Scatter(x=[logR[i] for i in idx],y=[ratio[i] for i in idx],mode="markers",
       marker=dict(size=11,color=COL[k],line=dict(color="#0e1116",width=1)),showlegend=False,
       text=[f"<b>{names[i]}</b><br>mean R = {Rmean[i]:.1f} km<br>"
             f"log T_form ≈ {logTform[i]:.1f} yr<br>log T_erode ≈ {logTerode[i]:.1f} yr<br>"
             f"log(erode/form) = {ratio[i]:.2f}" for i in idx],
       hovertemplate="%{text}<extra></extra>"),row=1,col=2)
peak_i=int(np.argmax(np.where(mr,ratio,-1e9)))
fig.add_vline(x=logR[peak_i],line=dict(color="#7CFC9A",width=1.2,dash="dash"),row=1,col=2)
fig.add_annotation(x=logR[peak_i],y=ratio[mr].min()+0.2,text=f"peak ≈ {names[peak_i]}<br>R≈{Rmean[peak_i]:.0f} km",
   showarrow=False,font=dict(color="#7CFC9A",size=11),row=1,col=2)

fig.update_xaxes(title_text="log₁₀ mean radius (m)",gridcolor="#222a33",zeroline=False,
   title_font_color="#cbd5e1",tickfont_color="#9aa7b4",row=1,col=1)
fig.update_xaxes(title_text="log₁₀ mean radius (m)",gridcolor="#222a33",zeroline=False,
   title_font_color="#cbd5e1",tickfont_color="#9aa7b4",row=1,col=2)
fig.update_yaxes(title_text="roundness c/a (1=sphere)",gridcolor="#222a33",zeroline=False,
   title_font_color="#cbd5e1",tickfont_color="#9aa7b4",row=1,col=1)
fig.update_yaxes(title_text="log₁₀(T_erosion / T_formation)",gridcolor="#222a33",zeroline=False,
   title_font_color="#cbd5e1",tickfont_color="#9aa7b4",row=1,col=2)
fig.update_layout(paper_bgcolor="#0e1116",plot_bgcolor="#161b22",font_color="#cbd5e1",
   legend=dict(bgcolor="#161b22",bordercolor="#222a33",borderwidth=1,x=0.30,y=0.18,font_size=11),
   margin=dict(l=60,r=30,t=70,b=60),height=640)

body=fig.to_html(full_html=False,include_plotlyjs=False,div_id="plot")
html=f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Vertical ARA — two waves (real data)</title>
<style>body{{background:#0e1116;color:#cbd5e1;font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:16px}}
h2{{font-weight:600;margin:0 0 4px}} .note{{color:#9aa7b4;font-size:13px;max-width:1100px;line-height:1.5;margin:6px 0 14px}}
b.k{{color:#e6edf3}}</style>
<script>{get_plotlyjs()}</script></head><body>
<h2>Vertical ARA — the rock→planet ladder on real measured shapes</h2>
<div class="note">31 bodies, grain→gas-giant. Roundness <b class="k">c/a</b> computed from published triaxial axes (not eyeballed). 
<b class="k">Wave 1</b> (real): roundness tracks size, ρ=0.82, p=0.0002, transition ≈180 km (the potato radius). Hover any point. 
Note the two outlier classes: <b class="k">Eros / Ida / Itokawa</b> sit below (monolithic shards), <b class="k">Bennu / Ryugu</b> sit above (rubble-pile spinning tops). <b class="k">Hyperion</b> (density 0.54) vs <b class="k">Mimas</b> (1.15) = same shelf, opposite form. 
<b class="k">Wave 2</b> (fenced, order-of-magnitude): persistence-per-build-cost peaks at the small-asteroid scale — the "optimal size", but built on scaling laws, not per-body measurement.</div>
{body}
</body></html>"""
out="/sessions/inspiring-wizardly-hypatia/mnt/SystemFormulaFolder/GIT/ARA-GIT/analysis/vertical_rocks/rock_two_waves.html"
open(out,"w",encoding="utf-8").write(html)
print("saved",out,len(html),"bytes")
