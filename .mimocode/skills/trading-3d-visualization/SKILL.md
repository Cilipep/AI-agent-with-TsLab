---
name: trading-3d-visualization
description: Interactive 3D trading visualizations using Three.js — candlestick charts, order books, depth maps, portfolio heatmaps, and real-time streaming. Use when the user asks for 3D visualization of trading data, financial charts in 3D, interactive market data visualization, or any request involving Three.js + trading/finance. Covers candlestick rendering, order book depth, portfolio correlation, equity curves, and WebSocket real-time updates.
---

# 3D Trading Visualization Skill

Create stunning, interactive 3D visualizations for trading data using Three.js. This skill covers everything from candlestick charts to order book depth to portfolio heatmaps — all rendered in real-time 3D with orbit controls, tooltips, and responsive layouts.

## Prerequisites

```bash
npm install three
npm install @types/three  # if TypeScript
# Optional but recommended:
npm install dat.gui       # debug UI
npm install lil-gui       # modern alternative to dat.gui
```

For quick prototyping, use CDN:
```html
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>
```

## Architecture: Single-File Trading Dashboard

The canonical pattern is a single HTML file with inline JS/CSS — no build step, works in any browser, easy to iterate:

```
trading-3d/
├── index.html          # Single-file dashboard (canonical)
├── js/
│   ├── main.js         # Scene setup, renderer, camera, controls
│   ├── CandlestickChart.js   # 3D candlestick rendering
│   ├── OrderBook3D.js        # Order book depth visualization
│   ├── EquityCurve3D.js      # 3D equity curve with drawdown
│   ├── PortfolioHeatmap.js   # Correlation heatmap in 3D
│   └── utils.js              # Color scales, formatters, helpers
└── css/
    └── styles.css      # Dark theme, overlays, HUD
```

## Scene Setup (Canonical Pattern)

```javascript
// main.js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function createScene(container) {
  // Renderer
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  container.appendChild(renderer.domElement);

  // Scene
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a1a);
  scene.fog = new THREE.FogExp2(0x0a0a1a, 0.015);

  // Camera
  const camera = new THREE.PerspectiveCamera(
    60,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
  );
  camera.position.set(0, 15, 30);

  // Controls
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 5;
  controls.maxDistance = 100;
  controls.maxPolarAngle = Math.PI / 2.1;

  // Lights
  const ambientLight = new THREE.AmbientLight(0x404060, 0.5);
  scene.add(ambientLight);
  const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
  directionalLight.position.set(10, 20, 10);
  scene.add(directionalLight);
  const pointLight = new THREE.PointLight(0x00ff88, 0.5, 50);
  pointLight.position.set(-5, 10, -5);
  scene.add(pointLight);

  // Grid helper
  const grid = new THREE.GridHelper(50, 50, 0x1a1a3a, 0x0d0d2a);
  grid.position.y = -0.01;
  scene.add(grid);

  // Resize handler
  window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });

  // Animation loop
  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  return { scene, camera, renderer, controls };
}
```

## 3D Candlestick Chart

The core visualization. Each candle is a box (body) + two cylinders (wicks):

```javascript
// CandlestickChart.js
import * as THREE from 'three';

const BULL_COLOR = 0x00e676;
const BEAR_COLOR = 0xff1744;
const WICK_COLOR = 0x666688;

export class CandlestickChart {
  constructor(scene, options = {}) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'candlesticks';
    scene.add(this.group);

    this.candleWidth = options.candleWidth || 0.8;
    this.gap = options.gap || 0.2;
    this.wickWidth = options.wickWidth || 0.08;
    this.bodyGeometry = new THREE.BoxGeometry(1, 1, 1);
    this.wickGeometry = new THREE.CylinderGeometry(1, 1, 1, 8);
  }

  /**
   * @param {Array<{time, open, high, low, close, volume}>} data
   */
  update(data) {
    // Clear previous
    while (this.group.children.length > 0) {
      const child = this.group.children[0];
      child.geometry?.dispose();
      child.material?.dispose();
      this.group.remove(child);
    }

    const step = this.candleWidth + this.gap;

    data.forEach((candle, i) => {
      const x = i * step;
      const isBull = candle.close >= candle.open;
      const color = isBull ? BULL_COLOR : BEAR_COLOR;

      const bodyBottom = Math.min(candle.open, candle.close);
      const bodyTop = Math.max(candle.open, candle.close);
      const bodyHeight = Math.max(bodyTop - bodyBottom, 0.001);

      // Body
      const bodyMat = new THREE.MeshPhongMaterial({
        color,
        transparent: true,
        opacity: 0.9,
        shininess: 80,
      });
      const body = new THREE.Mesh(this.bodyGeometry, bodyMat);
      body.scale.set(this.candleWidth, bodyHeight, this.candleWidth * 0.6);
      body.position.set(x, bodyBottom + bodyHeight / 2, 0);
      this.group.add(body);

      // Upper wick
      const upperWickLen = candle.high - bodyTop;
      if (upperWickLen > 0) {
        const wickMat = new THREE.MeshBasicMaterial({ color: WICK_COLOR });
        const upperWick = new THREE.Mesh(this.wickGeometry, wickMat);
        upperWick.scale.set(this.wickWidth, upperWickLen, this.wickWidth);
        upperWick.position.set(x, bodyTop + upperWickLen / 2, 0);
        this.group.add(upperWick);
      }

      // Lower wick
      const lowerWickLen = bodyBottom - candle.low;
      if (lowerWickLen > 0) {
        const wickMat = new THREE.MeshBasicMaterial({ color: WICK_COLOR });
        const lowerWick = new THREE.Mesh(this.wickGeometry, wickMat);
        lowerWick.scale.set(this.wickWidth, lowerWickLen, this.wickWidth);
        lowerWick.position.set(x, bodyBottom - lowerWickLen / 2, 0);
        this.group.add(lowerWick);
      }
    });

    // Center the chart
    const totalWidth = data.length * step;
    this.group.position.x = -totalWidth / 2;
  }

  dispose() {
    this.group.children.forEach(child => {
      child.geometry?.dispose();
      child.material?.dispose();
    });
    this.scene.remove(this.group);
  }
}
```

## Volume Bars (Below Candlesticks)

Volume bars are semi-transparent boxes below the price chart:

```javascript
export class VolumeBars {
  constructor(scene, options = {}) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'volume';
    scene.add(this.group);
    this.maxBarHeight = options.maxBarHeight || 3;
    this.candleWidth = options.candleWidth || 0.8;
    this.gap = options.gap || 0.2;
  }

  update(data) {
    while (this.group.children.length > 0) {
      const child = this.group.children[0];
      child.geometry?.dispose();
      child.material?.dispose();
      this.group.remove(child);
    }

    const maxVol = Math.max(...data.map(d => d.volume));
    const step = this.candleWidth + this.gap;
    const geometry = new THREE.BoxGeometry(1, 1, 1);

    data.forEach((candle, i) => {
      const x = i * step;
      const height = (candle.volume / maxVol) * this.maxBarHeight;
      const isBull = candle.close >= candle.open;

      const mat = new THREE.MeshPhongMaterial({
        color: isBull ? 0x00e676 : 0xff1744,
        transparent: true,
        opacity: 0.3,
      });
      const bar = new THREE.Mesh(geometry, mat);
      bar.scale.set(this.candleWidth * 0.9, height, this.candleWidth * 0.4);
      bar.position.set(x, -height / 2 - 0.5, 0);
      this.group.add(bar);
    });

    const totalWidth = data.length * step;
    this.group.position.x = -totalWidth / 2;
  }
}
```

## 3D Order Book Depth

Visualize bid/ask depth as a terrain or stacked bars:

```javascript
// OrderBook3D.js
import * as THREE from 'three';

export class OrderBook3D {
  constructor(scene, options = {}) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'orderbook';
    scene.add(this.group);
    this.barDepth = options.barDepth || 10; // Z-axis layers
  }

  /**
   * @param {Array<{price, bidSize, askSize}>} levels
   */
  update(levels) {
    while (this.group.children.length > 0) {
      const child = this.group.children[0];
      child.geometry?.dispose();
      child.material?.dispose();
      this.group.remove(child);
    }

    const maxQuantity = Math.max(
      ...levels.map(l => Math.max(l.bidSize, l.askSize))
    );

    const geometry = new THREE.BoxGeometry(1, 1, 1);

    levels.forEach((level, i) => {
      const x = (i - levels.length / 2) * 1.2;

      // Bid (green, front)
      const bidHeight = (level.bidSize / maxQuantity) * 5;
      const bidMat = new THREE.MeshPhongMaterial({
        color: 0x00e676,
        transparent: true,
        opacity: 0.8,
      });
      const bidBar = new THREE.Mesh(geometry, bidMat);
      bidBar.scale.set(0.8, bidHeight, 0.8);
      bidBar.position.set(x, bidHeight / 2, -1);
      this.group.add(bidBar);

      // Ask (red, back)
      const askHeight = (level.askSize / maxQuantity) * 5;
      const askMat = new THREE.MeshPhongMaterial({
        color: 0xff1744,
        transparent: true,
        opacity: 0.8,
      });
      const askBar = new THREE.Mesh(geometry, askMat);
      askBar.scale.set(0.8, askHeight, 0.8);
      askBar.position.set(x, askHeight / 2, 1);
      this.group.add(askBar);
    });
  }
}
```

## 3D Portfolio Correlation Heatmap

A grid of colored cubes where color = correlation coefficient:

```javascript
// PortfolioHeatmap.js
import * as THREE from 'three';

export class PortfolioHeatmap {
  constructor(scene, options = {}) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'heatmap';
    scene.add(this.group);
    this.spacing = options.spacing || 1.2;
  }

  /**
   * @param {string[]} symbols
   * @param {number[][]} correlationMatrix  NxN, values in [-1, 1]
   */
  update(symbols, correlationMatrix) {
    while (this.group.children.length > 0) {
      const child = this.group.children[0];
      child.geometry?.dispose();
      child.material?.dispose();
      this.group.remove(child);
    }

    const n = symbols.length;
    const geometry = new THREE.BoxGeometry(1, 1, 1);

    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const corr = correlationMatrix[i][j];
        const color = this.corrToColor(corr);

        const height = Math.abs(corr) * 2 + 0.1;
        const mat = new THREE.MeshPhongMaterial({
          color,
          transparent: true,
          opacity: 0.85,
        });
        const cube = new THREE.Mesh(geometry, mat);
        cube.scale.set(
          this.spacing * 0.9,
          height,
          this.spacing * 0.9
        );
        cube.position.set(
          (i - n / 2) * this.spacing,
          height / 2,
          (j - n / 2) * this.spacing
        );
        this.group.add(cube);
      }
    }
  }

  corrToColor(corr) {
    // -1 = deep red, 0 = white, +1 = deep green
    if (corr >= 0) {
      const t = corr;
      return new THREE.Color(
        1 - t * 0.8,
        1 - t * 0.2,
        1 - t * 0.8
      );
    } else {
      const t = -corr;
      return new THREE.Color(
        1 - t * 0.2,
        1 - t * 0.8,
        1 - t * 0.8
      );
    }
  }
}
```

## 3D Equity Curve with Drawdown

Render equity as a ribbon/line in 3D with drawdown regions highlighted:

```javascript
// EquityCurve3D.js
import * as THREE from 'three';

export class EquityCurve3D {
  constructor(scene, options = {}) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'equity';
    scene.add(this.group);
    this.ribbonWidth = options.ribbonWidth || 0.3;
  }

  /**
   * @param {number[]} equity - array of portfolio values
   * @param {number[]} drawdown - array of drawdown percentages (0 to -1)
   */
  update(equity, drawdown) {
    while (this.group.children.length > 0) {
      const child = this.group.children[0];
      child.geometry?.dispose();
      child.material?.dispose();
      this.group.remove(child);
    }

    const points = equity.map((val, i) =>
      new THREE.Vector3(i * 0.3, val, 0)
    );

    // Equity line
    const curve = new THREE.CatmullRomCurve3(points);
    const tubeGeometry = new THREE.TubeGeometry(curve, 200, 0.05, 8, false);
    const tubeMat = new THREE.MeshPhongMaterial({ color: 0x00bfff });
    const tube = new THREE.Mesh(tubeGeometry, tubeMat);
    this.group.add(tube);

    // Drawdown fill (red area below)
    if (drawdown && drawdown.length > 0) {
      const ddPoints = [];
      equity.forEach((val, i) => {
        ddPoints.push(new THREE.Vector3(i * 0.3, val, 0));
        ddPoints.push(new THREE.Vector3(i * 0.3, val * (1 + drawdown[i]), 0));
      });

      // Simple plane for drawdown visualization
      const shape = new THREE.Shape();
      equity.forEach((val, i) => {
        const x = i * 0.3;
        const y = val * (1 + (drawdown[i] || 0));
        if (i === 0) shape.moveTo(x, y);
        else shape.lineTo(x, y);
      });
      // Close back to equity line
      for (let i = equity.length - 1; i >= 0; i--) {
        shape.lineTo(i * 0.3, equity[i]);
      }
      shape.closePath();

      const ddGeometry = new THREE.ShapeGeometry(shape);
      const ddMat = new THREE.MeshBasicMaterial({
        color: 0xff1744,
        transparent: true,
        opacity: 0.3,
        side: THREE.DoubleSide,
      });
      const ddMesh = new THREE.Mesh(ddGeometry, ddMat);
      ddMesh.position.z = -0.01;
      this.group.add(ddMesh);
    }
  }
}
```

## Real-Time WebSocket Streaming

Connect to live data and update visuals in real-time:

```javascript
// RealTimeStream.js
export class RealTimeStream {
  constructor(url, onUpdate) {
    this.ws = new WebSocket(url);
    this.buffer = [];
    this.maxCandles = 200;

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.buffer.push(data);
      if (this.buffer.length > this.maxCandles) {
        this.buffer.shift();
      }
      onUpdate(this.buffer);
    };

    this.ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  }

  close() {
    this.ws.close();
  }
}

// Usage:
// const stream = new RealTimeStream('wss://exchange/ws/trades', (candles) => {
//   chart.update(candles);
//   volume.update(candles);
// });
```

## HUD Overlay (HTML/CSS)

Dark-themed overlay with metrics:

```html
<!-- index.html -->
<div id="hud">
  <div class="hud-panel">
    <h3>BTC/USDT</h3>
    <div class="metric">
      <span class="label">Price</span>
      <span class="value" id="price">$67,432.10</span>
    </div>
    <div class="metric">
      <span class="label">24h Change</span>
      <span class="value positive" id="change">+2.34%</span>
    </div>
    <div class="metric">
      <span class="label">Volume</span>
      <span class="value" id="volume">$1.2B</span>
    </div>
  </div>
</div>

<style>
  #hud {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 100;
    pointer-events: none;
  }
  .hud-panel {
    background: rgba(10, 10, 26, 0.9);
    border: 1px solid rgba(0, 191, 255, 0.3);
    border-radius: 8px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #e0e0e0;
    backdrop-filter: blur(10px);
  }
  .hud-panel h3 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: #00bfff;
    text-transform: uppercase;
    letter-spacing: 2px;
  }
  .metric {
    display: flex;
    justify-content: space-between;
    margin: 6px 0;
    font-size: 13px;
  }
  .metric .label { color: #888; }
  .metric .value { font-weight: 600; }
  .metric .value.positive { color: #00e676; }
  .metric .value.negative { color: #ff1744; }
</style>
```

## Tooltip on Hover

Raycasting for mouse-over info:

```javascript
function addTooltip(scene, camera, renderer, objects) {
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  const tooltip = document.getElementById('tooltip');

  renderer.domElement.addEventListener('mousemove', (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(objects);

    if (intersects.length > 0) {
      const obj = intersects[0].object;
      const data = obj.userData;
      tooltip.style.display = 'block';
      tooltip.style.left = event.clientX + 15 + 'px';
      tooltip.style.top = event.clientY - 10 + 'px';
      tooltip.innerHTML = `
        <div>O: ${data.open?.toFixed(2)}</div>
        <div>H: ${data.high?.toFixed(2)}</div>
        <div>L: ${data.low?.toFixed(2)}</div>
        <div>C: ${data.close?.toFixed(2)}</div>
      `;
    } else {
      tooltip.style.display = 'none';
    }
  });
}
```

## Color Palette (Trading Theme)

```javascript
// utils.js
export const COLORS = {
  bg:           0x0a0a1a,
  grid:         0x1a1a3a,
  bull:         0x00e676,
  bear:         0xff1744,
  neutral:      0x666688,
  accent:       0x00bfff,
  accentDim:    0x005f8c,
  volume:       0x4488ff,
  drawdown:     0xff1744,
  text:         '#e0e0e0',
  textDim:      '#888888',
  positive:     '#00e676',
  negative:     '#ff1744',
};

export function priceToY(price, minPrice, maxPrice, height = 10) {
  return ((price - minPrice) / (maxPrice - minPrice)) * height;
}

export function formatPrice(p) {
  return p >= 1000
    ? '$' + p.toLocaleString('en-US', { minimumFractionDigits: 2 })
    : '$' + p.toFixed(4);
}
```

## Common Gotchas

1. **Dispose geometries/materials** when updating — memory leaks kill performance
2. **Use BufferGeometry** (not Geometry) — deprecated in Three.js r125+
3. **Limit draw calls** — merge static geometries with `BufferGeometryUtils.mergeGeometries()`
4. **Pixel ratio cap** — `Math.min(devicePixelRatio, 2)` prevents retina overload
5. **Fog hides distant objects** — set fog far enough to not clip your chart
6. **OrbitControls + scroll** — disable page scroll when mouse is over canvas
7. **Wick rendering order** — render wicks after bodies to avoid z-fighting
8. **WebSocket reconnect** — always handle disconnects in production

## Performance Checklist

- [ ] Disposed old geometries before creating new ones
- [ ] Capped pixel ratio at 2
- [ ] Used `MeshPhongMaterial` (not `MeshStandardMaterial`) for speed
- [ ] Merged static geometries where possible
- [ ] Throttled WebSocket updates to 60fps max
- [ ] Used `requestAnimationFrame` (not `setInterval`)
- [ ] Tested with 1000+ candles without frame drops

## File Structure Summary

```
trading-3d/
├── index.html              ← Single-file entry point
├── js/
│   ├── main.js             ← Scene, renderer, camera, controls, lights
│   ├── CandlestickChart.js ← 3D candle bodies + wicks
│   ├── VolumeBars.js       ← Semi-transparent volume underneath
│   ├── OrderBook3D.js      ← Bid/ask depth as 3D bars
│   ├── EquityCurve3D.js    ← Portfolio line + drawdown fill
│   ├── PortfolioHeatmap.js ← NxN correlation grid
│   ├── RealTimeStream.js   ← WebSocket data feed
│   └── utils.js            ← Colors, formatters, helpers
├── css/
│   └── styles.css          ← Dark theme, HUD panels
└── README.md
```
