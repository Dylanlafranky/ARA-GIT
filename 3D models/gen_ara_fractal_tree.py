"""ARA fractal tree — generated mathematically.
Geometry IS the framework: binary branching (reversible binary), golden-angle
phyllotaxis (137.5deg = the phi handover that never closes), 1/phi length scaling
per rung (octave/time-rung), recursive self-similarity (ARA has an ARA).
Emits an interactive offline Three.js viewer (inlined)."""
import numpy as np, json, os
PHI=(1+5**0.5)/2
GOLDEN=np.pi*(3-5**0.5)        # 137.50776 deg, the most-irrational angle
TILT=np.radians(34.0)          # branch opening half-angle
DEPTH=11; L0=3.2; SCALE=1/PHI; NCHILD=2
segs=[]   # (x0,y0,z0,x1,y1,z1,depth)
def frame(T):
    a=np.array([0,0,1.0]) if abs(T[2])<0.9 else np.array([1.0,0,0])
    N1=np.cross(T,a); N1/=np.linalg.norm(N1); N2=np.cross(T,N1)
    return N1,N2
az_counter=[0]
def grow(p,T,L,d):
    if d>DEPTH: return
    e=p+T*L; segs.append((*p,*e,d))
    if d==DEPTH: return
    N1,N2=frame(T)
    for k in range(NCHILD):
        az_counter[0]+=1
        az=GOLDEN*az_counter[0] + (np.pi if k else 0)   # phyllotaxis spiral + split
        side=N1*np.cos(az)+N2*np.sin(az)
        nT=T*np.cos(TILT)+side*np.sin(TILT); nT/=np.linalg.norm(nT)
        grow(e,nT,L*SCALE,d+1)
grow(np.array([0,-3.5,0.0]), np.array([0,1.0,0]), L0, 0)
segs=np.array(segs)
# colors by depth/rung: trunk warm -> tips cool-green (phi/time)
import colorsys
pos=[];col=[]
for s in segs:
    d=int(s[6]); t=d/DEPTH
    r,g,b=colorsys.hls_to_rgb(0.08+0.42*t, 0.45+0.1*t, 0.75)  # hue amber->green
    for xyz in (s[0:3],s[3:6]):
        pos+= [float(xyz[0]),float(xyz[1]),float(xyz[2])]; col+=[r,g,b]
DATA={"pos":[round(x,4) for x in pos],"col":[round(c,3) for c in col],
      "n":int(len(segs)),"depth":DEPTH,"golden_deg":round(np.degrees(GOLDEN),2),"phi":round(PHI,4)}
THREE=open('/tmp/threeinstall/node_modules/three/build/three.min.js').read()
HTML="""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARA fractal tree</title><style>
 html,body{margin:0;height:100%;background:#070b12;color:#cdd6e0;font-family:system-ui,Segoe UI,Arial,sans-serif;overflow:hidden}
 #c{position:fixed;inset:0}#info{position:fixed;top:12px;left:12px;background:rgba(10,16,26,.82);border:1px solid #2a3a52;border-radius:10px;padding:11px 14px;max-width:300px;font-size:12px;line-height:1.55;z-index:5}
 #info h1{font-size:14px;margin:0 0 6px;color:#f0c878}b{color:#9ad08a}.k{color:#7fb0ff}
 label{display:block;margin-top:8px;font-size:12px;cursor:pointer}#hint{position:fixed;bottom:10px;left:0;right:0;text-align:center;font-size:11px;opacity:.5}
</style></head><body><canvas id="c"></canvas>
<div id="info"><h1>ARA fractal tree</h1>
The geometry IS the framework: <b>binary</b> branching (reversible binary), <b>golden-angle</b> phyllotaxis (<span class="k">__GA__&deg;</span> — the most-irrational angle, the phi handover that never closes on itself), <b>1/phi</b> length per rung (the time octave), recursive (ARA has an ARA).
<label><input type="checkbox" id="spin" checked> auto-rotate</label>
<label><input type="checkbox" id="grow" checked> grow animation</label>
<div style="margin-top:8px;opacity:.7">__N__ segments &middot; depth __D__</div></div>
<div id="hint">drag to rotate &middot; scroll to zoom</div>
<script>__THREE__</script><script>
const D=__DATA__;
const scene=new THREE.Scene();const cam=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,0.1,500);cam.position.set(0,2,16);
const rnd=new THREE.WebGLRenderer({canvas:document.getElementById('c'),antialias:true});rnd.setPixelRatio(devicePixelRatio);
function fit(){cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();rnd.setSize(innerWidth,innerHeight);}fit();addEventListener('resize',fit);
const pivot=new THREE.Group();scene.add(pivot);
const g=new THREE.BufferGeometry();
g.setAttribute('position',new THREE.Float32BufferAttribute(D.pos,3));
g.setAttribute('color',new THREE.Float32BufferAttribute(D.col,3));
const mat=new THREE.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.92});
const lines=new THREE.LineSegments(g,mat);pivot.add(lines);
let drawn=0;const total=D.pos.length/3;
// drag rotate
let dr=false,px,py,ry=0.3,rx=-0.1;const cv=rnd.domElement;
cv.addEventListener('pointerdown',e=>{dr=true;px=e.clientX;py=e.clientY});
addEventListener('pointerup',()=>dr=false);
addEventListener('pointermove',e=>{if(!dr)return;ry+=(e.clientX-px)*.005;rx+=(e.clientY-py)*.005;px=e.clientX;py=e.clientY;});
cv.addEventListener('wheel',e=>{cam.position.multiplyScalar(1+Math.sign(e.deltaY)*.08);e.preventDefault();},{passive:false});
const spin=document.getElementById('spin'),grow=document.getElementById('grow');
function loop(){requestAnimationFrame(loop);
 if(spin.checked)ry+=0.0035;
 pivot.rotation.y=ry;pivot.rotation.x=rx;
 if(grow.checked){drawn=Math.min(total,drawn+24);}else{drawn=total;}
 g.setDrawRange(0,Math.floor(drawn/2)*2);
 rnd.render(scene,cam);}
loop();
document.getElementById('grow').addEventListener('change',e=>{if(e.target.checked)drawn=0;});
</script></body></html>"""
HTML=(HTML.replace('__THREE__',THREE).replace('__DATA__',json.dumps(DATA))
      .replace('__GA__',str(DATA['golden_deg'])).replace('__N__',str(DATA['n'])).replace('__D__',str(DEPTH)))
open('ARA_fractal_tree.html','w').write(HTML)
print(f"tree: {DATA['n']} segments, depth {DEPTH}, golden {DATA['golden_deg']}deg, size {round(os.path.getsize('ARA_fractal_tree.html')/1024)}KB")
