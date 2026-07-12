"""ARA circle — FLAT canonical view. Vertical axis = ARA: space(0) bottom apex,
time(2) top apex, 1.0 ridge = the horizontal diameter. phi-engines at 0.382/1.618.
Each wave-pattern potential = ARA(phase) shown as its real waveform on this axis."""
import numpy as np, json, os
N=360; ph=np.linspace(0,2*np.pi,N,endpoint=False); PHI=(1+5**0.5)/2
def golden_duty(p):
    u=(p/(2*np.pi))%1.0; rise=1/PHI
    return np.where(u<rise,u/rise,1-(u-rise)/(1-rise))
waves={
 "clock":{"label":"Clock (symmetric @ ridge)","color":"#6ca8ff","ara":1+0.72*np.sin(ph)},
 "phi_engine":{"label":"phi-engine (golden duty 0.618/0.382)","color":"#f0c878","ara":0.30+1.40*golden_duty(ph)},
 "snap":{"label":"Snap (rest -> pole reaction)","color":"#ff6b6b","ara":0.45+1.45*np.exp(-((((ph+np.pi)%(2*np.pi))-np.pi)**2)/0.06)},
 "harmonic":{"label":"Harmonic (overtones -> 2)","color":"#b197fc","ara":1+0.45*np.sin(ph)+0.28*np.sin(2*ph)+0.17*np.sin(3*ph)+0.10*np.sin(4*ph)},
 "antiphase":{"label":"Anti-phase pair (cancel @ ridge)","color":"#6fd0c8","ara":1+0.72*np.sin(ph),"ara2":1-0.72*np.sin(ph)},
}
out={"N":N,"engines":[0.382,1.618],"waves":{}}
for k,w in waves.items():
    r={"label":w["label"],"color":w["color"],"ara":[round(float(np.clip(v,0,2)),4) for v in w["ara"]]}
    if "ara2" in w: r["ara2"]=[round(float(np.clip(v,0,2)),4) for v in w["ara2"]]
    out["waves"][k]=r
HTML="""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARA circle — flat</title><style>
 html,body{margin:0;height:100%;background:#070b12;color:#cdd6e0;font-family:system-ui,Segoe UI,Arial,sans-serif;overflow:hidden}
 #c{position:fixed;inset:0}#p{position:fixed;top:12px;left:12px;background:rgba(10,16,26,.85);border:1px solid #2a3a52;border-radius:10px;padding:12px 14px;max-width:270px;font-size:12px;line-height:1.5;z-index:5}
 #p h1{font-size:14px;margin:0 0 6px;color:#f0c878}.tog{display:block;margin:5px 0;cursor:pointer}
 .sw{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:middle}
 .rng{margin-top:10px;font-size:11px}.rng input{width:100%}.leg{margin-top:9px;font-size:10.5px;opacity:.8}
</style></head><body><canvas id="c"></canvas>
<div id="p"><h1>ARA circle — flat (canonical)</h1>
<div style="opacity:.85;margin-bottom:6px">Vertical = the 0&ndash;2 axis: <b style="color:#6ca8ff">space (0)</b> bottom apex, <b style="color:#f0c878">time (2)</b> top apex, <b style="color:#3fb950">1.0 ridge</b> = the horizontal diameter. phi-engines at 0.382 / 1.618.</div>
<div id="togs"></div>
<div class="rng">speed <input type="range" id="spd" min="0" max="3" step="0.05" value="1"></div>
<div class="leg">Each wave is ARA(phase) as a real waveform on the axis &mdash; you can read the golden duty, the snap to a pole, the overtones, the anti-phase cancel.</div></div>
<script>
const D=__DATA__;const cv=document.getElementById('c'),x=cv.getContext('2d');
function fit(){cv.width=innerWidth*devicePixelRatio;cv.height=innerHeight*devicePixelRatio;x.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);}fit();addEventListener('resize',fit);
const on={};Object.keys(D.waves).forEach((k,i)=>on[k]=(i<2));
const togs=document.getElementById('togs');
for(const k in D.waves){const w=D.waves[k];const l=document.createElement('label');l.className='tog';
 l.innerHTML=`<input type="checkbox" ${on[k]?'checked':''}><span class="sw" style="background:${w.color}"></span>${w.label}`;
 l.querySelector('input').onchange=e=>on[k]=e.target.checked;togs.appendChild(l);}
let t=0;const spd=document.getElementById('spd');
function geom(){const W=innerWidth,H=innerHeight;const R=Math.min(W*0.5,H*0.42);return {cx:W/2,cy:H/2,R,W,H};}
function Y(ara,cy,R){return cy+(1-ara)*R;}        // 0->bottom(+R), 1->cy, 2->top(-R)
function loop(){requestAnimationFrame(loop);
 const {cx,cy,R,W,H}=geom();x.clearRect(0,0,W,H);
 // circle frame
 x.beginPath();x.arc(cx,cy,R,0,7);x.strokeStyle='#27384f';x.lineWidth=1.4;x.stroke();
 // ridge = horizontal diameter
 x.beginPath();x.moveTo(cx-R,cy);x.lineTo(cx+R,cy);x.strokeStyle='#3fb950';x.lineWidth=1.6;x.stroke();
 // phi engine lines (horizontal dashed)
 x.setLineDash([4,5]);x.strokeStyle='#f0c878';x.lineWidth=1;
 [D.engines[0],D.engines[1]].forEach(a=>{const hw=Math.sqrt(Math.max(0,R*R-(Y(a,cy,R)-cy)**2));x.beginPath();x.moveTo(cx-hw,Y(a,cy,R));x.lineTo(cx+hw,Y(a,cy,R));x.stroke();});
 x.setLineDash([]);
 // labels
 x.fillStyle='#9aa7b4';x.font='12px system-ui';x.textAlign='center';
 x.fillStyle='#f0c878';x.fillText('time · 2',cx,cy-R-8);
 x.fillStyle='#6ca8ff';x.fillText('space · 0',cx,cy+R+16);
 x.fillStyle='#3fb950';x.textAlign='left';x.fillText('1.0 ridge',cx+R+6,cy+4);
 x.fillStyle='#caa84e';x.fillText('1.618',cx+R+6,Y(D.engines[1],cy,R)+4);x.fillText('0.382',cx+R+6,Y(D.engines[0],cy,R)+4);
 t+=0.012*parseFloat(spd.value);
 for(const k in D.waves){if(!on[k])continue;const w=D.waves[k];
   const drawCurve=(arr)=>{x.beginPath();for(let i=0;i<=D.N;i++){const a=arr[i%D.N];const px=cx-R+(i/D.N)*2*R,py=Y(a,cy,R);i?x.lineTo(px,py):x.moveTo(px,py);}x.strokeStyle=w.color;x.lineWidth=1.7;x.globalAlpha=.55;x.stroke();x.globalAlpha=1;};
   drawCurve(w.ara); if(w.ara2)drawCurve(w.ara2);
   const idx=((t/(2*Math.PI))*D.N|0)%D.N;const mk=(arr)=>{const a=arr[idx];const px=cx-R+(idx/D.N)*2*R,py=Y(a,cy,R);
     x.beginPath();x.arc(px,py,6,0,7);x.fillStyle=w.color;x.fill();x.strokeStyle='#070b12';x.lineWidth=2;x.stroke();
     x.strokeStyle=w.color;x.globalAlpha=.25;x.beginPath();x.moveTo(px,cy);x.lineTo(px,py);x.stroke();x.globalAlpha=1;};
   mk(w.ara); if(w.ara2)mk(w.ara2);
 }
}
loop();
</script></body></html>"""
HTML=HTML.replace('__DATA__',json.dumps(out))
open('ARA_circle_flat_waves.html','w').write(HTML)
print(f"flat circle: {len(out['waves'])} archetypes, size {round(os.path.getsize('ARA_circle_flat_waves.html')/1024)}KB")
