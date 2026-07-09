"""3D visualization of the neural network architecture with Russian labels."""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection


def draw_neuron(ax, x, y, z, radius=0.15, color='#2196F3', alpha=0.8):
    """Draw a single neuron as a sphere."""
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    x_sphere = radius * np.outer(np.cos(u), np.sin(v)) + x
    y_sphere = radius * np.outer(np.sin(u), np.sin(v)) + y
    z_sphere = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + z
    ax.plot_surface(x_sphere, y_sphere, z_sphere, color=color, alpha=alpha)


def draw_connection(ax, x1, y1, z1, x2, y2, z2, color='#90A4AE', alpha=0.3):
    """Draw a connection between two neurons."""
    ax.plot([x1, x2], [y1, y2], [z1, z2], color=color, alpha=alpha, linewidth=0.5)


def create_nn_visualization():
    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Layer configuration
    layers = [
        {'name': 'Входной\nслой', 'n': 8, 'x': 0, 'color': '#4CAF50'},
        {'name': 'Скрытый\nслой 1\n(TCN)', 'n': 6, 'x': 2, 'color': '#2196F3'},
        {'name': 'Скрытый\nслой 2\n(LSTM)', 'n': 6, 'x': 4, 'color': '#9C27B0'},
        {'name': 'Скрытый\nслой 3\n(Transformer)', 'n': 6, 'x': 6, 'color': '#FF9800'},
        {'name': 'Meta-learner\n(MLP)', 'n': 4, 'x': 8, 'color': '#F44336'},
        {'name': 'Выходной\nслой', 'n': 1, 'x': 10, 'color': '#E91E63'},
    ]

    # Draw neurons
    neuron_positions = []
    for layer in layers:
        positions = []
        n = layer['n']
        spacing = 1.2
        start_y = -(n - 1) * spacing / 2
        for i in range(n):
            y = start_y + i * spacing
            z = 0
            draw_neuron(ax, layer['x'], y, z, radius=0.2, color=layer['color'])
            positions.append((layer['x'], y, z))
        neuron_positions.append(positions)

    # Draw connections
    for i in range(len(neuron_positions) - 1):
        for pos1 in neuron_positions[i]:
            for pos2 in neuron_positions[i + 1]:
                draw_connection(ax, *pos1, *pos2, alpha=0.15)

    # Add layer labels
    for i, layer in enumerate(layers):
        x_pos = layer['x']
        y_pos = -3.5
        ax.text(x_pos, y_pos, 0.5, layer['name'],
                fontsize=9, ha='center', va='center',
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=layer['color'], alpha=0.7, edgecolor='none'))

    # Add feature labels on input layer
    features = ['RSI', 'MACD', 'EMA', 'ATR', 'OBV', 'BB', 'Stoch', 'ADX']
    for i, feat in enumerate(features):
        y = -3.5 + i * 1.0
        ax.text(-1.5, y, 0, feat, fontsize=7, ha='center', va='center',
                color='#333333', fontstyle='italic')

    # Add output label
    ax.text(11.5, 0, 0, 'Сигнал\n(Покупка/\nПродажа)', fontsize=9, ha='center', va='center',
            fontweight='bold', color='#E91E63')

    # Add data flow label
    ax.text(1, -3.8, 0, 'Данные →', fontsize=8, ha='center', color='#333')

    # Styling
    ax.set_xlim(-2, 12)
    ax.set_ylim(-4, 4)
    ax.set_zlim(-1, 1)
    ax.set_xlabel('Слой', fontsize=10, labelpad=10)
    ax.set_ylabel('Нейроны', fontsize=10, labelpad=10)
    ax.set_zlabel('', fontsize=10)
    ax.set_title('Архитектура нейросетевой торговой стратегии\nEnsemble: TCN + LSTM + Transformer + Meta-learner',
                 fontsize=14, fontweight='bold', pad=20)

    # Remove grid for cleaner look
    ax.grid(False)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    # Set viewing angle
    ax.view_init(elev=20, azim=-60)

    plt.tight_layout()
    output_path = "C:/Users/i59400f/Desktop/ai-agent/TsLabWorkspace/nn-trading/nn_3d_architecture.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"3D visualization saved to {output_path}")


if __name__ == "__main__":
    create_nn_visualization()
