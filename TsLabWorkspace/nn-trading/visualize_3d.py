"""Интерактивная 3D-визуализация архитектуры LSTM торговой нейросети."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgba(c, a=0.85):
    r, g, b = _hex_to_rgb(c)
    return f'rgba({r},{g},{b},{a})'


def _make_cylinder(x, y, z, r=0.3, h=0.6, color='#00b4d8', opacity=0.8, n=16):
    theta = np.linspace(0, 2 * np.pi, n)
    xs = x + r * np.cos(theta)
    zs = z + r * np.sin(theta)
    y_top = y + h / 2
    y_bot = y - h / 2
    verts = []
    faces = []
    colors = []
    base = 0
    for i in range(n):
        nxt = (i + 1) % n
        verts.append([xs[i], y_bot, zs[i]])
        verts.append([xs[i], y_top, zs[i]])
    for i in range(n):
        nxt = (i + 1) % n
        i0, i1 = 2 * i, 2 * i + 1
        i2, i3 = 2 * nxt, 2 * nxt + 1
        faces.append([i0, i1, i3, i2])
        colors.append(color)
    bot_center = [x, y_bot, z]
    top_center = [x, y_top, z]
    bot_idx = len(verts)
    top_idx = bot_idx + 1
    verts.append(bot_center)
    verts.append(top_center)
    for i in range(n):
        nxt = (i + 1) % n
        faces.append([bot_idx, 2 * nxt, 2 * i, bot_idx])
        colors.append(color)
        faces.append([top_idx, 2 * i + 1, 2 * nxt + 1, top_idx])
        colors.append(color)
    return np.array(verts), faces, colors


def build_network_3d():
    """Build vertices and faces for the full LSTM trading network."""
    all_verts = []
    all_faces = []
    all_colors = []

    # ─── LAYOUT ──────────────────────────────────────────────
    feature_names = [
        "returns", "rsi", "stoch_k", "williams_r",
        "macd", "macd_sig", "macd_hist",
        "ema_12", "ema_26", "adx",
        "bb_up", "bb_low", "bb_w", "atr", "vol_ratio",
    ]
    n_features = len(feature_names)      # 15
    window = 60
    hidden_size = 64
    n_lstm_layers = 2
    dense1_size = 32
    n_lstm_cells = 8  # representative cells for visualization

    x_gap = 2.2
    y_gap = 0.6
    z_gap = 0.6
    layer_x = 0

    colors_input = '#0077b6'
    colors_lstm = ['#e76f51', '#f4a261']
    colors_dense = ['#2a9d8f', '#264653']
    colors_output = '#e63946'

    vo = 0  # vertex offset

    # ─── 1. INPUT LAYER ─────────────────────────────────────
    n_input_nodes = n_features
    x_in = layer_x
    for i in range(n_input_nodes):
        y = (i - n_input_nodes / 2) * y_gap
        z = 0
        v, f, c = _make_cylinder(x_in, y, z, r=0.2, h=0.35, color=colors_input)
        all_verts.append(v + [0, 0, 0])
        all_faces.extend([[x + vo for x in poly] for poly in f])
        all_colors.extend(c)
        vo += len(v)
    layer_x += x_gap

    # ─── 2. LSTM LAYER 1 ────────────────────────────────────
    n_lstm1 = n_lstm_cells
    x_lstm1 = layer_x
    for i in range(n_lstm1):
        y = (i - n_lstm1 / 2) * y_gap * 1.5
        z = 0
        v, f, c = _make_cylinder(x_lstm1, y, z, r=0.35, h=0.5, color=colors_lstm[0])
        all_verts.append(v + [0, 0, 0])
        all_faces.extend([[x + vo for x in poly] for poly in f])
        all_colors.extend(c)
        vo += len(v)
    # recurrent connections within layer 1
    for i in range(n_lstm1 - 1):
        y1 = (i - n_lstm1 / 2) * y_gap * 1.5
        y2 = (i + 1 - n_lstm1 / 2) * y_gap * 1.5
        for side in [-1, 1]:
            all_verts.append(np.array([[x_lstm1 + 0.8, y1 + side * 0.15, 0.3],
                                       [x_lstm1 + 0.8, y2 + side * 0.15, 0.3]]))
            all_faces.append([vo, vo + 1])
            all_colors.append('#8d99ae')
            vo += 2
    layer_x += x_gap

    # ─── 3. LSTM LAYER 2 ────────────────────────────────────
    n_lstm2 = n_lstm_cells
    x_lstm2 = layer_x
    for i in range(n_lstm2):
        y = (i - n_lstm2 / 2) * y_gap * 1.5
        z = 0
        v, f, c = _make_cylinder(x_lstm2, y, z, r=0.35, h=0.5, color=colors_lstm[1])
        all_verts.append(v + [0, 0, 0])
        all_faces.extend([[x + vo for x in poly] for poly in f])
        all_colors.extend(c)
        vo += len(v)
    # recurrent connections within layer 2
    for i in range(n_lstm2 - 1):
        y1 = (i - n_lstm2 / 2) * y_gap * 1.5
        y2 = (i + 1 - n_lstm2 / 2) * y_gap * 1.5
        for side in [-1, 1]:
            all_verts.append(np.array([[x_lstm2 + 0.8, y1 + side * 0.15, 0.3],
                                       [x_lstm2 + 0.8, y2 + side * 0.15, 0.3]]))
            all_faces.append([vo, vo + 1])
            all_colors.append('#8d99ae')
            vo += 2
    layer_x += x_gap

    # ─── 4. DENSE 64→32 ─────────────────────────────────────
    n_d1 = min(dense1_size, 10)
    x_d1 = layer_x
    for i in range(n_d1):
        y = (i - n_d1 / 2) * y_gap * 0.9
        z = 0
        v, f, c = _make_cylinder(x_d1, y, z, r=0.18, h=0.28, color=colors_dense[0])
        all_verts.append(v + [0, 0, 0])
        all_faces.extend([[x + vo for x in poly] for poly in f])
        all_colors.extend(c)
        vo += len(v)
    layer_x += x_gap

    # ─── 5. DENSE 32→1 (OUTPUT) ─────────────────────────────
    x_out = layer_x
    v, f, c = _make_cylinder(x_out, 0, 0, r=0.5, h=0.7, color=colors_output)
    all_verts.append(v + [0, 0, 0])
    all_faces.extend([[x + vo for x in poly] for poly in f])
    all_colors.extend(c)
    vo += len(v)

    # ─── 6. CONNECTIONS (input → lstm1 → lstm2 → dense → output) ───
    conn_color = '#6c757d'
    # input → lstm1
    for fi in range(min(n_input_nodes, 8)):
        for li in range(n_lstm1):
            if (fi + li) % 3 == 0:
                y1 = (fi - n_input_nodes / 2) * y_gap
                y2 = (li - n_lstm1 / 2) * y_gap * 1.5
                all_verts.append(np.array([[x_in + 0.3, y1, 0],
                                           [x_lstm1 - 0.3, y2, 0]]))
                all_faces.append([vo, vo + 1])
                all_colors.append(conn_color)
                vo += 2
    # lstm1 → lstm2
    for l1 in range(n_lstm1):
        for l2 in range(n_lstm2):
            if l1 == l2 or abs(l1 - l2) == 1:
                y1 = (l1 - n_lstm1 / 2) * y_gap * 1.5
                y2 = (l2 - n_lstm2 / 2) * y_gap * 1.5
                all_verts.append(np.array([[x_lstm1 + 0.4, y1, 0],
                                           [x_lstm2 - 0.4, y2, 0]]))
                all_faces.append([vo, vo + 1])
                all_colors.append(conn_color)
                vo += 2
    # lstm2 → dense
    for l2 in range(n_lstm2):
        for d in range(n_d1):
            if l2 % 2 == d % 2:
                y1 = (l2 - n_lstm2 / 2) * y_gap * 1.5
                y2 = (d - n_d1 / 2) * y_gap * 0.9
                all_verts.append(np.array([[x_lstm2 + 0.4, y1, 0],
                                           [x_d1 - 0.2, y2, 0]]))
                all_faces.append([vo, vo + 1])
                all_colors.append(conn_color)
                vo += 2
    # dense → output
    for d in range(n_d1):
        y1 = (d - n_d1 / 2) * y_gap * 0.9
        all_verts.append(np.array([[x_d1 + 0.2, y1, 0],
                                   [x_out - 0.5, 0, 0]]))
        all_faces.append([vo, vo + 1])
        all_colors.append(conn_color)
        vo += 2

    return np.concatenate(all_verts, axis=0), all_faces, all_colors


def create_3d_figure():
    verts, faces, colors = build_network_3d()

    # separate lines (2 vertices) and mesh (4+ vertices)
    line_traces = []
    mesh_verts = []
    mesh_faces = []
    mesh_colors = []
    mesh_idx_offset = 0

    for face, c in zip(faces, colors):
        if len(face) == 2:
            p1, p2 = verts[face[0]], verts[face[1]]
            line_traces.append(go.Scatter3d(
                x=[p1[0], p2[0], None],
                y=[p1[1], p2[1], None],
                z=[p1[2], p2[2], None],
                mode='lines',
                line=dict(color=c, width=1.2),
                hoverinfo='none',
                showlegend=False,
            ))
        else:
            # quad/triangle mesh
            pts = [verts[i] for i in face]
            center = np.mean(pts, axis=0)
            mesh_verts.append(center)
            for p in pts:
                mesh_verts.append(p)
            n = len(face)
            for k in range(n):
                i0 = mesh_idx_offset
                i1 = mesh_idx_offset + 1 + k
                i2 = mesh_idx_offset + 1 + ((k + 1) % n)
                mesh_faces.append([i0, i1, i2])
                mesh_colors.append(c)
            mesh_idx_offset += 1 + n

    if mesh_verts:
        mv = np.array(mesh_verts)
        mf = np.array(mesh_faces)
        mesh_trace = go.Mesh3d(
            x=mv[:, 0], y=mv[:, 1], z=mv[:, 2],
            i=mf[:, 0], j=mf[:, 1], k=mf[:, 2],
            vertexcolor=[_rgba(c, 0.85) for c in mesh_colors],
            flatshading=True,
            hoverinfo='none',
            showlegend=False,
        )
        line_traces.insert(0, mesh_trace)

    # ─── ПОДПИСИ СЛОЁВ ─────────────────────────────────────
    layer_x = 0
    x_gap = 2.2
    labels = [
        (layer_x, 'Вход\n15 признаков × 60 баров', '#0077b6'),
    ]
    layer_x += x_gap
    labels.append((layer_x, 'LSTM Слой 1\nhidden=64', '#e76f51'))
    layer_x += x_gap
    labels.append((layer_x, 'LSTM Слой 2\nhidden=64', '#f4a261'))
    layer_x += x_gap
    labels.append((layer_x, 'Полносвязный\n64→32', '#2a9d8f'))
    layer_x += x_gap
    labels.append((layer_x, 'Выход\nКупить/Продать', '#e63946'))

    # add annotations
    max_y = 5
    for xx, txt, col in labels:
        line_traces.append(go.Scatter3d(
            x=[xx], y=[max_y], z=[0],
            mode='text',
            text=[txt],
            textposition='middle center',
            textfont=dict(size=10, color=col, family='Consolas'),
            hoverinfo='none',
            showlegend=False,
        ))

    # ─── ИНФОРМАЦИОННАЯ ПАНЕЛЬ ─────────────────────────────
    info = (
        "Торговая нейросеть — LSTM Ансамбль<br>"
        "Вход: 15 признаков × 60 временных шагов<br>"
        "├─ Тренд: EMA, MACD, ADX, Aroon, SAR<br>"
        "├─ Моментум: RSI, Stochastic, Williams, CCI<br>"
        "├─ Волатильность: Bollinger, ATR<br>"
        "├─ Объём: OBV, MFI, AD<br>"
        "└─ Паттерны: Doji, Hammer, Engulfing<br>"
        "LSTM: 2 слоя × 64 скрытых нейрона<br>"
        "Голова: Linear(64→32) → ReLU → Dropout → Linear(32→1)<br>"
        "Выход: бинарный (вероятность купить/продать)"
    )

    fig = go.Figure(data=line_traces)
    fig.update_layout(
        title=dict(
            text='<b>3D Архитектура нейросети</b> — LSTM Торговая Модель',
            font=dict(size=18, color='#e0e0e0'),
            x=0.5,
        ),
        scene=dict(
            xaxis=dict(visible=False, range=[-1, 12]),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='#1a1a2e',
            camera=dict(
                eye=dict(x=2.5, y=-6, z=3.5),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        paper_bgcolor='#1a1a2e',
        font=dict(color='#e0e0e0', size=11),
        margin=dict(l=10, r=10, t=50, b=10),
        width=1200,
        height=700,
        annotations=[
            dict(
                x=0.02, y=0.98, xref='paper', yref='paper',
                text=info,
                showarrow=False,
                align='left',
                font=dict(size=10, color='#adb5bd', family='Consolas'),
                bgcolor='rgba(26, 26, 46, 0.85)',
                bordercolor='#495057',
                borderwidth=1,
                borderpad=6,
            ),
        ],
    )
    return fig


if __name__ == '__main__':
    fig = create_3d_figure()
    fig.write_html('nn_3d_architecture.html', auto_open=True)
    print('Saved nn_3d_architecture.html')
