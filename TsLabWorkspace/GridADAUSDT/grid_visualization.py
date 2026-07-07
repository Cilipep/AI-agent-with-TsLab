import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Download BTC data
df = yf.download('BTC-USD', period='5d', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)

# Parameters
GRID_MULT = 2.5
STOP_MULT = 3.0
TRAILING_UP_STOP = 65000
TRAILING_DOWN_STOP = 55000

# Calculate ATR
def calc_atr(df, p=14):
    h, l, c = df['High'], df['Low'], df['Close'].shift(1)
    return pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1).rolling(p).mean()

df['ATR'] = calc_atr(df)

# Take last 100 bars for visualization
df = df.tail(100).copy()
df['GridBase'] = df['Close']
df['UpperBoundary'] = df['GridBase'] + df['ATR'] * GRID_MULT
df['LowerBoundary'] = df['GridBase'] - df['ATR'] * GRID_MULT
df['StopLevelLong'] = df['GridBase'] - df['ATR'] * STOP_MULT
df['StopLevelShort'] = df['GridBase'] + df['ATR'] * STOP_MULT

# Create figure
fig, axes = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [4, 1]})
fig.suptitle('Grid Bot — Trailing Up & Down (Bybit Logic)', fontsize=14, fontweight='bold')

# Main chart
ax1 = axes[0]

# Price
ax1.plot(df.index, df['Close'], color='#2196F3', linewidth=1.5, label='BTC Price', zorder=5)

# Grid levels
ax1.plot(df.index, df['UpperBoundary'], color='#4CAF50', linewidth=1, linestyle='-', alpha=0.7, label='Upper Boundary (Grid Sell)')
ax1.plot(df.index, df['LowerBoundary'], color='#F44336', linewidth=1, linestyle='-', alpha=0.7, label='Lower Boundary (Grid Buy)')
ax1.plot(df.index, df['GridBase'], color='#9E9E9E', linewidth=1, linestyle='--', alpha=0.5, label='Grid Base')

# Stop levels
ax1.plot(df.index, df['StopLevelLong'], color='#FF9800', linewidth=1, linestyle=':', alpha=0.7, label='Stop Level Long')
ax1.plot(df.index, df['StopLevelShort'], color='#FF9800', linewidth=1, linestyle=':', alpha=0.7, label='Stop Level Short')

# Trailing stop lines
ax1.axhline(y=TRAILING_UP_STOP, color='#00BCD4', linewidth=2, linestyle='-', alpha=0.8, label=f'Trailing Up Stop (${TRAILING_UP_STOP:,})')
ax1.axhline(y=TRAILING_DOWN_STOP, color='#E91E63', linewidth=2, linestyle='-', alpha=0.8, label=f'Trailing Down Stop (${TRAILING_DOWN_STOP:,})')

# Fill trailing zones
ax1.fill_between(df.index, TRAILING_UP_STOP, df['Close'].max()*1.02, alpha=0.1, color='#00BCD4', label='Trailing Up Zone')
ax1.fill_between(df.index, TRAILING_DOWN_STOP, df['Close'].min()*0.98, alpha=0.1, color='#E91E63', label='Trailing Down Zone')

# Fill grid zone
ax1.fill_between(df.index, df['LowerBoundary'], df['UpperBoundary'], alpha=0.15, color='#4CAF50', label='Active Grid Zone')

ax1.set_ylabel('BTC Price ($)', fontsize=11)
ax1.set_title('Price with Grid Levels and Trailing Zones')
ax1.legend(loc='upper left', fontsize=8, ncol=2)
ax1.grid(True, alpha=0.3)

# Add annotations
mid_idx = len(df) // 2
ax1.annotate('Trailing Up\nactivates above\nthis line', 
             xy=(df.index[mid_idx], TRAILING_UP_STOP), 
             xytext=(df.index[mid_idx-20], TRAILING_UP_STOP+1000),
             fontsize=8, color='#00BCD4',
             arrowprops=dict(arrowstyle='->', color='#00BCD4'))

ax1.annotate('Trailing Down\nactivates below\nthis line', 
             xy=(df.index[mid_idx], TRAILING_DOWN_STOP), 
             xytext=(df.index[mid_idx-20], TRAILING_DOWN_STOP-1000),
             fontsize=8, color='#E91E63',
             arrowprops=dict(arrowstyle='->', color='#E91E63'))

# ATR chart
ax2 = axes[1]
ax2.fill_between(df.index, 0, df['ATR'], color='#FF9800', alpha=0.3)
ax2.plot(df.index, df['ATR'], color='#FF9800', linewidth=1, label='ATR(14)')
ax2.set_ylabel('ATR ($)', fontsize=11)
ax2.set_xlabel('Date', fontsize=11)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

# Format dates
import matplotlib.dates as mdates
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('TsLabWorkspace/GridADAUSDT/GridBot_TrailingUpDown.png', dpi=150, bbox_inches='tight')
print("График сохранён: GridBot_TrailingUpDown.png")

# Also create a logic diagram
fig2, ax = plt.subplots(1, 1, figsize=(14, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_title('Trailing Up / Trailing Down — Bybit Logic', fontsize=14, fontweight='bold')

# Draw grid example
grid_y = [2, 3, 4, 5, 6, 7, 8]
grid_labels = ['Buy 5', 'Buy 4', 'Buy 3', 'Buy 2', 'Sell 1', 'Sell 2', 'Sell 3']
colors = ['#4CAF50', '#4CAF50', '#4CAF50', '#4CAF50', '#F44336', '#F44336', '#F44336']

for i, (y, label, color) in enumerate(zip(grid_y, grid_labels, colors)):
    ax.barh(y, 8, left=1, height=0.4, color=color, alpha=0.3)
    ax.text(5, y, label, ha='center', va='center', fontsize=10, fontweight='bold')

# Trailing arrows
ax.annotate('TRAILING UP\nPrice > Upper → Grid shifts UP', 
            xy=(9, 8.5), fontsize=10, ha='center', color='#00BCD4', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#E0F7FA', alpha=0.8))
ax.annotate('TRAILING DOWN\nPrice < Lower → Grid shifts DOWN', 
            xy=(9, 1.5), fontsize=10, ha='center', color='#E91E63', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FCE4EC', alpha=0.8))

# Add arrows
ax.annotate('', xy=(9, 8.2), xytext=(9, 7.2),
            arrowprops=dict(arrowstyle='->', color='#00BCD4', lw=2))
ax.annotate('', xy=(9, 1.8), xytext=(9, 2.8),
            arrowprops=dict(arrowstyle='->', color='#E91E63', lw=2))

# Labels
ax.text(0.5, 5, 'Upper\nBoundary', ha='center', va='center', fontsize=9, color='#4CAF50')
ax.text(0.5, 4.5, 'Lower\nBoundary', ha='center', va='center', fontsize=9, color='#F44336')
ax.text(0.5, 5.5, 'Grid\nBase', ha='center', va='center', fontsize=9, color='#9E9E9E')

plt.tight_layout()
plt.savefig('TsLabWorkspace/GridADAUSDT/GridBot_TrailingLogic.png', dpi=150, bbox_inches='tight')
print("График сохранён: GridBot_TrailingLogic.png")
