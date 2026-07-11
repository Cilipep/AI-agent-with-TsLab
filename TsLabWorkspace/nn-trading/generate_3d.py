"""Generate 3D visualization HTML with backtest results."""
from pathlib import Path
import json


def generate():
    # Load results
    for fname in ["results/full_backtest_3yr.json", "results/portfolio_allocation.json", "results/instruments_walkforward.json"]:
        try:
            with open(fname) as f:
                pass
        except:
            pass

    bt_data = {}
    alloc_data = {}
    inst_data = {}

    try:
        with open("results/full_backtest_3yr.json") as f:
            bt_data = json.load(f)
    except: pass
    try:
        with open("results/portfolio_allocation.json") as f:
            alloc_data = json.load(f)
    except: pass
    try:
        with open("results/instruments_walkforward.json") as f:
            inst_data = json.load(f)
    except: pass

    instruments = inst_data.get("instruments", bt_data.get("instruments", []))
    alloc = alloc_data.get("allocation", {})
    portfolio = bt_data.get("portfolio", {})

    port_ret = portfolio.get("total_return", 0)
    port_dd = portfolio.get("max_drawdown", 0)
    port_sh = portfolio.get("sharpe", 0)

    # Build instrument HTML rows
    inst_rows = []
    for inst in sorted(instruments, key=lambda x: -x.get("total_return", 0)):
        name = inst.get("instrument", "?")
        ret = inst.get("total_return", 0)
        dd = inst.get("max_drawdown", 0)
        sh = inst.get("sharpe", 0)
        alloc_pct = alloc.get(name, 0)
        color = "#00ff88" if ret > 0 else "#ff4444"
        inst_rows.append(f'<tr><td style="color:{color};font-weight:bold">{name}</td><td style="color:{color}">{ret:+.2f}%</td><td>{dd:.2f}%</td><td>{sh:+.2f}</td><td>{alloc_pct:.1f}%</td></tr>')

    inst_table = "\n".join(inst_rows)
    alloc_json = json.dumps(alloc)

    # Portfolio stat class
    port_ret_cls = "neg" if port_ret < 0 else ""
    port_sh_cls = "neg" if port_sh < 0 else ""

    html = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>NN Trading — 3D Архитектура + Результаты</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a1a;font-family:'Segoe UI',Arial,sans-serif;color:#fff;overflow-x:hidden}
#canvas3d{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0}
#overlay{position:relative;z-index:10;padding:20px}
.panel{background:rgba(0,10,30,0.85);border:1px solid rgba(0,150,255,0.3);border-radius:12px;padding:20px;margin:15px;backdrop-filter:blur(10px)}
.panel h2{color:#00ccff;margin-bottom:12px;font-size:18px;border-bottom:1px solid rgba(0,150,255,0.3);padding-bottom:8px}
.panel h3{color:#00aaff;margin:10px 0 6px;font-size:14px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:rgba(0,100,200,0.3);color:#88ccff;padding:8px 10px;text-align:left}
td{padding:6px 10px;border-bottom:1px solid rgba(255,255,255,0.05)}
.stat{display:inline-block;margin:8px 15px 8px 0}
.stat .val{font-size:24px;font-weight:bold;color:#00ff88}
.stat .lbl{font-size:11px;color:#888}
.stat.neg .val{color:#ff4444}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}
.legend{display:flex;gap:12px;flex-wrap:wrap;margin:10px 0}
.legend-item{display:flex;align-items:center;gap:5px;font-size:11px;color:#aaa}
.dot{width:10px;height:10px;border-radius:50%}
</style>
</head>
<body>
<canvas id="canvas3d"></canvas>
<div id="overlay">

<div class="panel" style="max-width:900px">
  <h2>3D Архитектура: HybridEnsemble + DQN RL</h2>
  <p style="color:#aaa;font-size:13px;margin-bottom:10px">
    Гибридная торговая система — комбинация нейросетей (LSTM, Transformer, Attention) с классическими ML (XGBoost, CatBoost, LightGBM, RandomForest)
  </p>
  <div class="legend">
    <div class="legend-item"><div class="dot" style="background:#336699"></div>Input (40-50 фичей)</div>
    <div class="legend-item"><div class="dot" style="background:#00ccff"></div>LSTM</div>
    <div class="legend-item"><div class="dot" style="background:#ff6600"></div>Attention</div>
    <div class="legend-item"><div class="dot" style="background:#00ff88"></div>XGBoost</div>
    <div class="legend-item"><div class="dot" style="background:#ff0066"></div>CatBoost</div>
    <div class="legend-item"><div class="dot" style="background:#ffff00"></div>LightGBM</div>
    <div class="legend-item"><div class="dot" style="background:#aa00ff"></div>RandomForest</div>
    <div class="legend-item"><div class="dot" style="background:#ffffff"></div>Meta-Learner</div>
    <div class="legend-item"><div class="dot" style="background:#00ffcc"></div>Output (Buy/Hold/Sell)</div>
  </div>
</div>

<div class="grid" style="max-width:900px">

<div class="panel">
  <h2>Результаты бэктеста (3 года)</h2>
  <div class="stat PORT_RET_CLS">
    <div class="val">PORT_RET</div>
    <div class="lbl">Portfolio Return</div>
  </div>
  <div class="stat">
    <div class="val">PORT_DD</div>
    <div class="lbl">Max Drawdown</div>
  </div>
  <div class="stat PORT_SH_CLS">
    <div class="val">PORT_SH</div>
    <div class="lbl">Sharpe Ratio</div>
  </div>

  <h3>По инструментам</h3>
  <table>
    <tr><th>Инструмент</th><th>Return</th><th>DD</th><th>Sharpe</th><th>Доля</th></tr>
    INST_TABLE
  </table>
</div>

<div class="panel">
  <h2>Portfolio Allocation</h2>
  <div style="height:250px;display:flex;align-items:center;justify-content:center;">
    <canvas id="pieCanvas" width="250" height="250"></canvas>
  </div>
  <div id="pieLegend"></div>
</div>

</div>

<div class="panel" style="max-width:900px">
  <h2>Описание архитектуры</h2>
  <div class="grid">
    <div>
      <h3>1. Входной слой</h3>
      <p style="color:#aaa;font-size:12px">40-50 мультитаймфреймовых фичей (1d + 1w + 1M): EMA, RSI, MACD, Bollinger Bands, ATR, ADX, Stochastic, Williams %R, CCI, ROC, Momentum, OBV, MFI</p>
      <h3>2. LSTM слой</h3>
      <p style="color:#aaa;font-size:12px">Hidden: 64, Layers: 2, Dropout: 0.35. Запоминает последовательности и временные зависимости</p>
      <h3>3. Attention слой</h3>
      <p style="color:#aaa;font-size:12px">Multi-head attention с 8 heads. Находит важные паттерны и корреляции</p>
    </div>
    <div>
      <h3>4. ML Models</h3>
      <p style="color:#aaa;font-size:12px">XGBoost, CatBoost, LightGBM, RandomForest — градиентный бустинг для табличных данных</p>
      <h3>5. Meta-Learner</h3>
      <p style="color:#aaa;font-size:12px">Комбинирует предсказания 7 базовых моделей через взвешенное усреднение</p>
      <h3>6. Output</h3>
      <p style="color:#aaa;font-size:12px">3 действия: Buy / Hold / Sell. Confidence threshold: 0.5+. Trailing stop + dynamic sizing</p>
    </div>
  </div>
</div>

</div>

<script>
// === 3D Neural Network ===
var canvas = document.getElementById('canvas3d');
var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
if (!gl) { document.body.innerHTML = '<h1 style="color:#fff;padding:50px">WebGL not supported</h1>'; }

function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; gl.viewport(0, 0, canvas.width, canvas.height); }
resize();
window.addEventListener('resize', resize);

var vsSource = 'attribute vec3 aPos; attribute vec3 aColor; uniform mat4 uMVP; varying vec3 vColor; void main() { gl_Position = uMVP * vec4(aPos, 1.0); vColor = aColor; gl_PointSize = 6.0; }';
var fsSource = 'precision mediump float; varying vec3 vColor; void main() { gl_FragColor = vec4(vColor, 0.8); }';

function createShader(type, src) { var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; }
var prog = gl.createProgram();
gl.attachShader(prog, createShader(gl.VERTEX_SHADER, vsSource));
gl.attachShader(prog, createShader(gl.FRAGMENT_SHADER, fsSource));
gl.linkProgram(prog);
gl.useProgram(prog);

var aPos = gl.getAttribLocation(prog, 'aPos');
var aColor = gl.getAttribLocation(prog, 'aColor');
var uMVP = gl.getUniformLocation(prog, 'uMVP');

var nodes = [];
var colors = [];
var layers = [
  { name: 'Input', count: 8, x: -12, color: [0.2, 0.4, 0.6] },
  { name: 'LSTM', count: 6, x: -6, color: [0, 0.8, 1] },
  { name: 'Attention', count: 6, x: 0, color: [1, 0.4, 0] },
  { name: 'XGBoost', count: 4, x: 4, color: [0, 1, 0.5] },
  { name: 'CatBoost', count: 3, x: 6, color: [1, 0, 0.4] },
  { name: 'LightGBM', count: 3, x: 8, color: [1, 1, 0] },
  { name: 'RF', count: 3, x: 10, color: [0.67, 0, 1] },
  { name: 'Meta', count: 2, x: 12, color: [1, 1, 1] },
  { name: 'Output', count: 3, x: 14, color: [0, 1, 0.8] },
];

layers.forEach(function(l) {
  for (var i = 0; i < l.count; i++) {
    var y = (i - (l.count-1)/2) * 1.2;
    nodes.push(l.x, y, 0);
    colors.push(l.color[0], l.color[1], l.color[2]);
  }
});

var edges = [];
var edgeColors = [];
var nodeIdx = 0;
for (var l = 0; l < layers.length - 1; l++) {
  var start = nodeIdx;
  var end = start + layers[l].count;
  var nextStart = end;
  var nextEnd = nextStart + layers[l+1].count;
  for (var i = start; i < end; i++) {
    for (var j = nextStart; j < nextEnd; j++) {
      edges.push(nodes[i*3], nodes[i*3+1], nodes[i*3+2], nodes[j*3], nodes[j*3+1], nodes[j*3+2]);
      edgeColors.push(0.15, 0.2, 0.3, 0.15, 0.2, 0.3);
    }
  }
  nodeIdx = end;
}

function makeBuf(data) { var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.STATIC_DRAW); return b; }
var nodeBuf = makeBuf(nodes);
var nodeColBuf = makeBuf(colors);
var edgeBuf = makeBuf(edges);
var edgeColBuf = makeBuf(edgeColors);

function perspective(fov, aspect, near, far) {
  var f = 1/Math.tan(fov/2), nf = 1/(near-far);
  return [f/aspect,0,0,0, 0,f,0,0, 0,0,(far+near)*nf,-1, 0,0,2*far*near*nf,0];
}
function lookAt(eye, center, up) {
  var zx=eye[0]-center[0], zy=eye[1]-center[1], zz=eye[2]-center[2];
  var len=1/Math.sqrt(zx*zx+zy*zy+zz*zz); var z=[zx*len,zy*len,zz*len];
  var xx=up[1]*z[2]-up[2]*z[1], xy=up[2]*z[0]-up[0]*z[2], xz=up[0]*z[1]-up[1]*z[0];
  len=1/Math.sqrt(xx*xx+xy*xy+xz*xz); var x=[xx*len,xy*len,xz*len];
  var y=[z[1]*x[2]-z[2]*x[1], z[2]*x[0]-z[0]*x[2], z[0]*x[1]-z[1]*x[0]];
  return [x[0],y[0],z[0],0, x[1],y[1],z[1],0, x[2],y[2],z[2],0,
    -(x[0]*eye[0]+x[1]*eye[1]+x[2]*eye[2]), -(y[0]*eye[0]+y[1]*eye[1]+y[2]*eye[2]), -(z[0]*eye[0]+z[1]*eye[1]+z[2]*eye[2]), 1];
}
function mulMat4(a, b) {
  var r=new Float32Array(16);
  for(var i=0;i<4;i++) for(var j=0;j<4;j++) { var s=0; for(var k=0;k<4;k++) s+=a[i+k*4]*b[k+j*4]; r[i+j*4]=s; }
  return r;
}

gl.enable(gl.BLEND);
gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
gl.clearColor(0.04, 0.04, 0.1, 1);

var angle = 0;
function render() {
  requestAnimationFrame(render);
  angle += 0.004;
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  var aspect = canvas.width / canvas.height;
  var proj = perspective(Math.PI/4, aspect, 0.1, 100);
  var eye = [Math.sin(angle)*22, 8, Math.cos(angle)*22];
  var view = lookAt(eye, [1, 0, 0], [0, 1, 0]);
  var mvp = mulMat4(proj, view);

  gl.uniformMatrix4fv(uMVP, false, mvp);

  gl.bindBuffer(gl.ARRAY_BUFFER, edgeBuf);
  gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, 0, 0);
  gl.enableVertexAttribArray(aPos);
  gl.bindBuffer(gl.ARRAY_BUFFER, edgeColBuf);
  gl.vertexAttribPointer(aColor, 3, gl.FLOAT, false, 0, 0);
  gl.enableVertexAttribArray(aColor);
  gl.drawArrays(gl.LINES, 0, edges.length / 3);

  gl.bindBuffer(gl.ARRAY_BUFFER, nodeBuf);
  gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, 0, 0);
  gl.enableVertexAttribArray(aPos);
  gl.bindBuffer(gl.ARRAY_BUFFER, nodeColBuf);
  gl.vertexAttribPointer(aColor, 3, gl.FLOAT, false, 0, 0);
  gl.enableVertexAttribArray(aColor);
  gl.drawArrays(gl.POINTS, 0, nodes.length / 3);
}
render();

// === Pie Chart ===
var pieCanvas = document.getElementById('pieCanvas');
var ctx = pieCanvas.getContext('2d');
var allocData = ALLOC_JSON;
var total = Object.values(allocData).reduce(function(a,b){return a+b}, 0);
var pieColors = ['#00ccff','#ff6600','#00ff88','#ff0066','#ffff00','#aa00ff','#00ffcc','#ff8800','#88ff00','#ff00aa'];
var startAngle = -Math.PI/2;
var colorIdx = 0;
var legend = document.getElementById('pieLegend');
var legendHtml = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px">';

var entries = Object.entries(allocData).sort(function(a,b){return b[1]-a[1]});
for (var e = 0; e < entries.length; e++) {
  var name = entries[e][0];
  var pct = entries[e][1];
  var slice = (pct/total) * Math.PI * 2;
  ctx.beginPath();
  ctx.moveTo(125, 125);
  ctx.arc(125, 125, 100, startAngle, startAngle + slice);
  ctx.fillStyle = pieColors[colorIdx % pieColors.length];
  ctx.fill();
  ctx.strokeStyle = '#0a0a1a';
  ctx.lineWidth = 2;
  ctx.stroke();
  legendHtml += '<div class="legend-item"><div class="dot" style="background:' + pieColors[colorIdx % pieColors.length] + '"></div>' + name + ': ' + pct.toFixed(1) + '%</div>';
  startAngle += slice;
  colorIdx++;
}
legendHtml += '</div>';
legend.innerHTML = legendHtml;
</script>
</body>
</html>"""

    # Replace placeholders
    html = html.replace("INST_TABLE", inst_table)
    html = html.replace("ALLOC_JSON", alloc_json)
    html = html.replace("PORT_RET", f"{port_ret:+.2f}%")
    html = html.replace("PORT_DD", f"{abs(port_dd):.2f}%")
    html = html.replace("PORT_SH", f"{port_sh:+.2f}")
    html = html.replace("PORT_RET_CLS", f"{'neg' if port_ret < 0 else ''}")
    html = html.replace("PORT_SH_CLS", f"{'neg' if port_sh < 0 else ''}")

    out = Path("nn_3d_visualization.html")
    out.write_text(html, encoding="utf-8")
    print(f"Saved to {out}")
    print(f"Open: file:///{out.resolve().as_posix()}")


if __name__ == "__main__":
    generate()
