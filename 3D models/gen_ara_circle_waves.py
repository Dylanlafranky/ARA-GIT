"""ARA circle with wave-pattern potentials — math generated in Python, animated in Canvas.
The 0-2 ARA axis is the RADIUS: center=0 (space singularity), the 1.0 ridge = a circle,
outer edge=2 (time singularity); phi-engines at 0.382/1.618. Each wave archetype = ARA(phase),
sampled here and overlaid as a polar loop with an orbiting marker. Toggle which to show."""
import numpy as np, json, os
N=360
ph=np.linspace(0,2*np.pi,N,endpoint=False)
PHI=(1+5**0.5)/2
def golden_duty(p):  # rise over 0.618 of cycle, fall over 0.382 (asymmetric engine)
    u=(p/(2*np.pi))%1.0; rise=1/PHI  # 0.618
    return np.where(u<rise, u/rise, 1-(u-rise)/(1-rise))  # 0..1..0 skewed
waves={
 "clock":      {"label":"Clock (sine, symmetric @ ridge)","color":"#6ca8ff",
                "ara":(1+0.72*np.sin(ph))},
 "phi_engine": {"label":"phi-engine (golden duty 0.618/0.382)","color":"#f0c878",
                "ara":(0.30+1.40*golden_duty(ph))},
 "snap":       {"label":"Snap (rest, then pole reaction)","color":"#ff6b6b",
                "ara":(0.55+1.40*np.exp(-((((ph-0.0+np.pi)%(2*np.pi))-np.pi)**2)/0.07))},
 "harmonic":   {"label":"Harmonic / resonance (overtones -> 2)","color":"#b197fc",
                "ara":(1+0.45*np.sin(ph)+0.28*np.sin(2*ph)+0.17*np.sin(3*ph)+0.10*np.sin(4*ph))},
 "antiphase":  {"label":"Anti-phase pair (cancel @ ridge)","color":"#6fd0c8",
                "ara":(1+0.72*np.sin(ph)), "ara2":(1-0.72*np.sin(ph))},
}
out={"N":N,"phi":round(PHI,4),"engines":[round(2-PHI,3),round(PHI-1+0.0,3)],"waves":{}}
out["engines"]=[0.382,1.618]
for k,w in waves.items():
    rec={"label":w["label"],"color":w["color"],"ara":[round(float(np.clip(x,0,2)),4) for x in w["ara"]]}
    if "ara2" in w: rec["ara2"]=[round(float(np.clip(x,0,2)),4) for x in w["ara2"]]
    out["waves"][k]=rec
HTML="""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARA circle — wave potentials</title><style>
 html,body{margin:0;height:100%;background:#070b12;color:#cdd6e0;font-family:system-ui,Segoe UI,Arial,sans-serif;overflow:hidden}
 #c{position:fixed;inset:0}#p{position:fixed;top:12px;left:12px;background:rgba(10,16,26,.85);border:1px solid #2a3a52;border-radius:10px;padding:12px 14px;max-width:280px;font-size:12px;line-height:1.5;z-index:5}
 #p h1{font-size:14px;margin:0 0 6px;color:#f0c878}.tog{display:block;margin:5px 0;cursor:pointer}
 .sw{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:middle}
 .rng{margin-top:10px;font-size:11px}.rng input{width:100%}
 .leg{margin-top:9px;font-size:10.5px;opacity:.8;line-height:1.5}.k{color:#7fb0ff}.t{color:#f0c878}
</style></head><body><canvas id="c"></canvas>
<div id="p"><h1>ARA circle — wave potentials</h1>
<div style="opacity:.85;margin-bottom:6px">Radius = the 0&ndash;2 axis: <span class="k">center = 0 (space pole)</span>, <span style="color:#3fb950">1.0 ridge</span> circle, <span class="t">outer = 2 (time pole)</span>; phi-engines at 0.382 / 1.618.</div>
<div id="togs"></div>
<div class="rng">speed <input type="range" id="spd" min="0" max="3" step="0.05" value="1"></div>
<div class="leg">Each wave is ARA(phase) traced as a polar loop; the marker is the system moving through its cycle. See where it dwells, how it crosses the ridge, where it snaps to a pole.</div></div>
<script>
const D=__DATA__;const cv=document.getElementById('c'),x=cv.getContext('2d');
function fit(){cv.width=innerWidth*devicePixelRatio;cv.height=innerHeight*devicePixelRatio;x.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);}fit();addEventListener('resize',fit);
const on={};Object.keys(D.waves).forEach((k,i)=>on[k]=(i<2));
const togs=document.getElementById('togs');
for(const k in D.waves){const w=D.waves[k];const l=document.createElement('label');l.className='tog';
 l.innerHTML=`<input type="checkbox" ${on[k]?'checked':''}><span class="sw" style="background:${w.color}"></span>${w.label}`;
 l.querySelector('input').onchange=e=>on[k]=e.target.checked;togs.appendChild(l);}
let t=0;const spd=document.getElementById('spd');
function R(){return Math.min(innerWidth,innerHeight)*0.36;}
function pt(ara,phase,cx,cy,rmax){const r=ara/2*rmax;return [cx+r*Math.cos(phase-Math.PI/2),cy+r*Math.sin(phase-Math.PI/2)];}
function ring(cx,cy,r,col,w,dash){x.beginPath();x.arc(cx,cy,r,0,7);x.strokeStyle=col;x.lineWidth=w||1;x.setLineDash(dash||[]);x.stroke();x.setLineDash([]);}
function loop(){requestAnimationFrame(loop);
 const W=innerWidth,H=innerHeight,cx=W/2,cy=H/2,rmax=R();
 x.clearRect(0,0,W,H);
 // guide rings: poles, ridge, phi engines
 ring(cx,cy,rmax,'#3a4a62',1.2);                 // ARA=2 time pole (outer)
 ring(cx,cy,rmax*0.5,'#3fb950',1.4);             // ARA=1 ridge
 ring(cx,cy,rmax*D.engines[0]/2,'#f0c878',1,[3,4]); // 0.382
 ring(cx,cy,rmax*D.engines[1]/2,'#f0c878',1,[3,4]); // 1.618
 x.fillStyle='#5a6b80';x.font='11px system-ui';x.textAlign='center';
 x.fillText('2 · time pole',cx,cy-rmax-6);x.fillText('0 · space pole',cx,cy+4);
 x.fillStyle='#3fb950';x.fillText('1.0 ridge',cx,cy-rmax*0.5-5);
 t+=0.012*parseFloat(spd.value);
 for(const k in D.waves){if(!on[k])continue;const w=D.waves[k];
   // trace the loop
   const draw=(arr)=>{x.beginPath();for(let i=0;i<=D.N;i++){const a=arr[i%D.N];const[px,py]=pt(a,i/D.N*2*Math.PI,cx,cy,rmax);i?x.lineTo(px,py):x.moveTo(px,py);}x.strokeStyle=w.color;x.lineWidth=1.6;x.globalAlpha=.5;x.stroke();x.globalAlpha=1;};
   draw(w.ara); if(w.ara2)draw(w.ara2);
   // marker(s)
   const idx=((t/(2*Math.PI))*D.N|0);const mk=(arr,ofs)=>{const a=arr[(idx+ofs)%D.N];const[px,py]=pt(a,t,cx,cy,rmax);
     x.beginPath();x.arc(px,py,6,0,7);x.fillStyle=w.color;x.fill();x.strokeStyle='#070b12';x.lineWidth=2;x.stroke();};
   mk(w.ara,0); if(w.ara2)mk(w.ara2,0);
 }
}
loop();
</script></body></html>"""
HTML=HTML.replace('__DATA__',json.dumps(out))
open('ARA_circle_waves.html','w').write(HTML)
print(f"circle waves: {len(out['waves'])} archetypes, N={N}, size {round(os.path.getsize('ARA_circle_waves.html')/1024)}KB")
