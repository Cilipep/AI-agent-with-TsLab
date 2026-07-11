---
name: threejs-nn-3d-visualization
description: Create interactive 3D neural network architecture visualizations using Three.js with WebGL. Use when user asks for 3D visualization of neural networks, model architecture diagrams, or ML pipeline visualizations. Covers SphereGeometry neurons, BoxGeometry processing blocks, BufferGeometry edge connections, CanvasTexture labels, Raycaster tooltips, FogExp2 depth, MeshPhongMaterial emissive pulsing, PointsMaterial particles, OrbitControls, and sidebar UI.
---

# Three.js Neural Network 3D Visualization

Create interactive, rotating 3D visualizations of neural network architectures using Three.js WebGL.

## When to use
- User asks for "3D визуализация нейросети", "3D neural network", "model architecture visualization"
- Need to show layers, connections, and data flow in a neural network
- Want interactive tooltips on hover showing layer details

## Tech Stack (all CDN, no build tools)
- Three.js r128: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- OrbitControls: `https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js`

## File Structure (~350-500 lines)
```
- CSS: sidebar, tooltip, stats bar, button styles
- HTML: canvas + sidebar with model cards + stats bar
- JS: scene → lights → materials → factory → layers → edges → particles → labels → tooltip → animation
```

## Core Components

### 1. Scene Setup
```javascript
var renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.setClearColor(0x080818);
var scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x080818, 0.012);
var camera = new THREE.PerspectiveCamera(50, w/h, 0.1, 200);
camera.position.set(0, 15, 35);
var controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.5;
```

### 2. Lighting (3 lights)
```javascript
scene.add(new THREE.AmbientLight(0x334466, 0.5));
var dl = new THREE.DirectionalLight(0xffffff, 0.7); dl.position.set(10, 20, 15);
var pl = new THREE.PointLight(0x0088ff, 0.6, 60);  // moves in animate()
var pl2 = new THREE.PointLight(0xff4400, 0.3, 50);  // moves in animate()
```

### 3. Materials
```javascript
function makeMat(color) {
  return new THREE.MeshPhongMaterial({
    color: color, emissive: color, emissiveIntensity: 0.3,
    shininess: 80, transparent: true, opacity: 0.9,
  });
}
```

### 4. Factory: Neurons (SphereGeometry)
```javascript
function createNeuron(x, y, z, color, size) {
  var geo = new THREE.SphereGeometry(size || 0.25, 12, 8);
  var mesh = new THREE.Mesh(geo, makeMat(color));
  mesh.position.set(x, y, z);
  mesh.userData = {pulsPhase: Math.random() * Math.PI * 2};
  return mesh;
}
```

### 5. Factory: Processing Blocks (BoxGeometry)
```javascript
function createBlock(x, y, z, color, sx, sy, sz) {
  var geo = new THREE.BoxGeometry(sx||0.6, sy||0.5, sz||0.5);
  var mesh = new THREE.Mesh(geo, makeMat(color));
  mesh.position.set(x, y, z);
  mesh.userData = {pulsPhase: Math.random() * Math.PI * 2};
  return mesh;
}
```

### 6. Factory: Labels (CanvasTexture + Sprite)
```javascript
function createLabel(text, x, y, z) {
  var c = document.createElement('canvas');
  c.width = 512; c.height = 64;
  var ctx = c.getContext('2d');
  ctx.fillStyle = '#88ccff';
  ctx.font = 'bold 20px Arial';
  ctx.textAlign = 'center';
  ctx.fillText(text, 256, 44);
  var tex = new THREE.CanvasTexture(c);
  var mat = new THREE.SpriteMaterial({map: tex, transparent: true});
  var sprite = new THREE.Sprite(mat);
  sprite.position.set(x, y, z);
  sprite.scale.set(4, 0.5, 1);
  return sprite;
}
```

### 7. Edges (BufferGeometry Lines)
```javascript
function createEdge(x1,y1,z1, x2,y2,z2, color) {
  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(
    new Float32Array([x1,y1,z1, x2,y2,z2]), 3));
  return new THREE.Line(geo, new THREE.LineBasicMaterial({
    color: color||0x223355, transparent:true, opacity:0.15}));
}
```

### 8. Background Particles (PointsMaterial + AdditiveBlending)
```javascript
var pGeo = new THREE.BufferGeometry();
var pPos = new Float32Array(500 * 3);
for (var i=0; i<500; i++) {
  pPos[i*3] = (Math.random()-0.5)*80;
  pPos[i*3+1] = (Math.random()-0.5)*40;
  pPos[i*3+2] = (Math.random()-0.5)*80;
}
pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
var particles = new THREE.Points(pGeo, new THREE.PointsMaterial({
  color: 0x2244aa, size: 0.08, transparent: true, opacity: 0.6,
  blending: THREE.AdditiveBlending, depthWrite: false}));
scene.add(particles);
```

### 9. Tooltip (Raycaster)
```javascript
var raycaster = new THREE.Raycaster();
var mouse = new THREE.Vector2();
document.addEventListener('mousemove', function(e) {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  var hits = raycaster.intersectObjects(allMeshes);
  if (hits.length > 0) {
    // show tooltip with layer info
  }
});
```

### 10. Animation Loop
```javascript
function animate() {
  requestAnimationFrame(animate);
  var t = clock.getElapsedTime();
  controls.update();
  // Pulse neurons: emissiveIntensity = 0.3 + 0.15 * sin(t*2 + phase)
  // Animate particles: move Y up, wrap at boundary
  // Move lights: pl.position.x = sin(t*0.3) * 15
  renderer.render(scene, camera);
}
```

## Layer Definition Pattern
```javascript
var LAYERS = [
  {id:'input',  n:10, x:-20, y:0,  color:0x336699, type:'sphere'},
  {id:'lstm',   n:8,  x:-14, y:3,  color:0x00ccff, type:'sphere'},
  {id:'xgb',    n:5,  x:-2,  y:4,  color:0x00ff88, type:'box'},
  {id:'meta',   n:5,  x:10,  y:0,  color:0xffffff, type:'box'},
  {id:'output', n:3,  x:16,  y:0,  color:0x00ffcc, type:'sphere'},
];
```

## Key Gotchas
- All JS curly braces must be `{{` `}}` if inside Python f-string
- WebGL context may fail → add fallback message
- CanvasTexture needs `minFilter = THREE.LinearFilter` for crisp text
- OrbitControls from CDN uses `THREE.OrbitControls` (not module import)
- Particles with `AdditiveBlending` look best on dark backgrounds
- Label canvas width=512 for quality, height=64 is enough for one line
