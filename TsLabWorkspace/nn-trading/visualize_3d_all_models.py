"""3D visualization of the neural network architecture — all 10 models."""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches
from matplotlib import rcParams

rcParams['font.family'] = 'Segoe UI'

FEATURES = [
    'returns', 'rsi', 'stoch_k', 'williams_r',
    'macd', 'macd_signal', 'macd_hist',
    'ema_10', 'ema_20', 'adx',
    'bb_upper', 'bb_lower', 'bb_width', 'atr'
]

MODELS = {
    'LSTM': {
        'layers': [
            ('Вход\n(14 фич)', 14, '#4CAF50'),
            ('LSTM 1\n64u', 16, '#8b5cf6'),
            ('LSTM 2\n64u', 16, '#8b5cf6'),
            ('Head\n64→32→1', 8, '#ef4444'),
            ('Выход', 1, '#ec4899'),
        ],
    },
    'TCN': {
        'layers': [
            ('Вход\n(14 фич)', 14, '#4CAF50'),
            ('TCN Block 1\nConv1d k=3 dil=1', 12, '#06b6d4'),
            ('TCN Block 2\nConv1d k=3 dil=2', 12, '#06b6d4'),
            ('Head\n64→32→16→1', 6, '#ef4444'),
            ('Выход', 1, '#ec4899'),
        ],
    },
    'Transformer': {
        'layers': [
            ('Вход\n(14 фич)', 14, '#4CAF50'),
            ('Projection\nLin(14→64)', 10, '#6366f1'),
            ('Encoder L1\nAttn+FFN', 12, '#f59e0b'),
            ('Encoder L2\nAttn+FFN', 12, '#f59e0b'),
            ('Head\n64→32→16→1', 6, '#ef4444'),
            ('Выход', 1, '#ec4899'),
        ],
    },
    'Attention': {
        'layers': [
            ('Вход\n(14 фич)', 14, '#4CAF50'),
            ('Projection\nLin(14→64)+LN', 10, '#6366f1'),
            ('AttnBlock 1\nMHA(8)+Res', 12, '#f59e0b'),
            ('AttnBlock 2\nMHA(8)+Res', 12, '#f59e0b'),
            ('Head\n64→32→1', 6, '#ef4444'),
            ('Выход', 1, '#ec4899'),
        ],
    },
    'Multi-Task': {
        'layers': [
            ('Вход\n(14 фич)', 14, '#4CAF50'),
            ('LSTM 1\n64u', 16, '#8b5cf6'),
            ('LSTM 2\n64u', 16, '#8b5cf6'),
            ('Class Head', 4, '#ef4444'),
            ('Reg Head', 4, '#10b981'),
            ('Conf Head', 4, '#f59e0b'),
            ('3 Выхода', 1, '#ec4899'),
        ],
    },
    'Ensemble': {
        'layers': [
            ('Вход\n(14 фич)', 14, '#4CAF50'),
            ('LSTM', 10, '#8b5cf6'),
            ('TCN', 10, '#06b6d4'),
            ('Transformer', 10, '#f59e0b'),
            ('Weighted\nAvg', 4, '#10b981'),
            ('Выход', 1, '#ec4899'),
        ],
    },
}


def draw_neuron_3d(ax, x, y, z, r, color, alpha=0.85):
    u = np.linspace(0, 2 * np.pi, 16)
    v = np.linspace(0, np.pi, 16)
    xs = r * np.outer(np.cos(u), np.sin(v)) + x
    ys = r * np.outer(np.sin(u), np.sin(v)) + y
    zs = r * np.outer(np.ones_like(u), np.cos(v)) + z
    ax.plot_surface(xs, ys, zs, color=color, alpha=alpha, shade=True)


def create_single_model(ax, model_name, model_data, base_x=0):
    layers = model_data['layers']
    spacing = 3.5
    positions = []

    for li, (label, n, color) in enumerate(layers):
        x = base_x + li * spacing
        n_display = min(n, 16)
        y_spacing = min(0.7, 8 / n_display)
        start_y = -(n_display - 1) * y_spacing / 2
        layer_pos = []
        for i in range(n_display):
            y = start_y + i * y_spacing
            z = np.sin(i * 0.5) * 0.1  # slight wave
            draw_neuron_3d(ax, x, y, z, 0.18, color)
            layer_pos.append((x, y, z))
        positions.append(layer_pos)

    # Connections
    for i in range(len(positions) - 1):
        for p1 in positions[i]:
            for p2 in positions[i + 1]:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                        color='#555', alpha=0.08, linewidth=0.3)

    # Layer labels
    for li, (label, n, color) in enumerate(layers):
        x = base_x + li * spacing
        ax.text(x, -3.5, 0, label, fontsize=6, ha='center', va='center',
                fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.2', facecolor=color, alpha=0.25, edgecolor='none'))

    # Model title
    ax.text(base_x + (len(layers) - 1) * spacing / 2, -4.5, 0,
            model_name, fontsize=10, ha='center', fontweight='bold', color='#fff')


def create_all_models():
    fig = plt.figure(figsize=(28, 20), facecolor='#0a0a0f')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0a0a0f')

    # Grid layout: 3 rows x 2 cols
    offsets = [
        (0, 10),       # LSTM        (row 0, col 0)
        (0, -10),      # TCN         (row 0, col 1)
        (15, 10),      # Transformer (row 1, col 0)
        (15, -10),     # Attention   (row 1, col 1)
        (30, 5),       # Multi-Task  (row 2, col 0)
        (30, -15),     # Ensemble    (row 2, col 1)
    ]

    for (oy, ox), (name, data) in zip(offsets, MODELS.items()):
        create_single_model(ax, name, data, base_x=oy)
        # Shift y for visual separation
        for li, (_, n, _) in enumerate(data['layers']):
            pass  # already handled in draw

    # Feature list on the side
    ax.text(-4, 0, 0, 'ФИЧИ:\n' + '\n'.join(FEATURES), fontsize=6,
            fontfamily='monospace', color='#888', ha='right', va='center',
            bbox=dict(boxstyle='round', facecolor='#1a1a2e', alpha=0.8, edgecolor='#333'))

    # Title
    ax.text(17, 0, 6, 'Архитектура нейросети — NN-Trading\n7 моделей: LSTM, TCN, Transformer, Attention, Multi-Task, Ensemble',
            fontsize=16, ha='center', fontweight='bold', color='#fff',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a2e', alpha=0.9, edgecolor='#6366f1'))

    # Styling
    ax.set_xlim(-6, 42)
    ax.set_ylim(-20, 20)
    ax.set_zlim(-2, 8)
    ax.set_xlabel('Модели', fontsize=10, color='#666', labelpad=15)
    ax.set_ylabel('Нейроны', fontsize=10, color='#666', labelpad=15)
    ax.set_zlabel('', fontsize=10)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('#222')
    ax.yaxis.pane.set_edgecolor('#222')
    ax.zaxis.pane.set_edgecolor('#222')
    ax.tick_params(colors='#444', labelsize=7)
    ax.view_init(elev=25, azim=-55)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#4CAF50', label='Вход (14 фич)'),
        mpatches.Patch(facecolor='#6366f1', label='Projection'),
        mpatches.Patch(facecolor='#8b5cf6', label='LSTM'),
        mpatches.Patch(facecolor='#06b6d4', label='TCN'),
        mpatches.Patch(facecolor='#f59e0b', label='Attention/Transformer'),
        mpatches.Patch(facecolor='#ef4444', label='FFN/Head'),
        mpatches.Patch(facecolor='#ec4899', label='Выход'),
        mpatches.Patch(facecolor='#10b981', label='Meta-learner'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8,
              facecolor='#1a1a2e', edgecolor='#333', labelcolor='#ccc')

    plt.tight_layout()
    out = "C:/Users/i59400f/Desktop/ai-agent/TsLabWorkspace/nn-trading/nn_3d_all_models.png"
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='#0a0a0f')
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    create_all_models()
