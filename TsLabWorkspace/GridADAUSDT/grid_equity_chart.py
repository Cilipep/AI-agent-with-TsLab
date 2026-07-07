import yfinance as yf
import pandas as pd
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

CONFIG = {
    'symbol': 'BTC/USDT', 'timeframe': '30m', 'initial_capital': 40.0,
    'leverage': 10, 'grid_multiplier': 2.5, 'stop_multiplier': 3.0,
    'risk_per_trade': 0.10, 'reinvest_pct': 0.10, 'commission': 0.0005, 'atr_period': 14,
}

def calc_atr(df, p=14):
    h, l, c = df['High'], df['Low'], df['Close'].shift(1)
    return pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1).rolling(p).mean()

print("Загрузка данных...")
df = yf.download('BTC-USD', period='1mo', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
df['ATR'] = calc_atr(df)
print(f"Данные: {len(df)} баров")

# Run bot
cap = CONFIG['initial_capital']
lev = CONFIG['leverage']
pos = None
trades = []
equity = []
timestamps = df.index[20:]

for i in range(20, len(df)):
    atr = df['ATR'].iloc[i]
    close, low, high = df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i]

    if pos:
        if pos['t'] == 'long':
            if low <= pos['s']:
                pnl = (pos['s'] - pos['e']) * pos['q']
                comm = (pos['e'] + pos['s']) * pos['q'] * CONFIG['commission']
                cap += pnl - comm
                trades.append({'pnl': pnl - comm, 'reason': 'sl'})
                pos = None
            elif high >= pos['tp']:
                pnl = (pos['tp'] - pos['e']) * pos['q']
                comm = (pos['e'] + pos['tp']) * pos['q'] * CONFIG['commission']
                reinvest = (pnl - comm) * CONFIG['reinvest_pct'] if pnl > comm else 0
                cap += pnl - comm + reinvest
                trades.append({'pnl': pnl - comm, 'reason': 'tp'})
                pos = None
        else:
            if high >= pos['s']:
                pnl = (pos['e'] - pos['s']) * pos['q']
                comm = (pos['e'] + pos['s']) * pos['q'] * CONFIG['commission']
                cap += pnl - comm
                trades.append({'pnl': pnl - comm, 'reason': 'sl'})
                pos = None
            elif low <= pos['tp']:
                pnl = (pos['e'] - pos['tp']) * pos['q']
                comm = (pos['e'] + pos['tp']) * pos['q'] * CONFIG['commission']
                reinvest = (pnl - comm) * CONFIG['reinvest_pct'] if pnl > comm else 0
                cap += pnl - comm + reinvest
                trades.append({'pnl': pnl - comm, 'reason': 'tp'})
                pos = None

    if pos is None and cap > 1 and not pd.isna(atr) and atr > 0:
        prev = df['Close'].iloc[i-1]
        sd = atr * CONFIG['stop_multiplier']
        gs = atr * CONFIG['grid_multiplier']
        qty = (cap * CONFIG['risk_per_trade'] * lev) / sd
        mv = qty * close / lev
        if mv > cap * 0.95:
            qty = (cap * 0.95 * lev) / close
        if close < prev:
            pos = {'t': 'long', 'e': close, 'q': qty, 's': close - sd, 'tp': close + gs}
        elif close > prev:
            pos = {'t': 'short', 'e': close, 'q': qty, 's': close + sd, 'tp': close - gs}

    unr = 0
    if pos:
        unr = (close - pos['e']) * pos['q'] if pos['t'] == 'long' else (pos['e'] - close) * pos['q']
    equity.append(cap + unr)

if pos:
    lp = df['Close'].iloc[-1]
    pnl = ((lp - pos['e']) if pos['t'] == 'long' else (pos['e'] - lp)) * pos['q']
    comm = (pos['e'] + lp) * pos['q'] * CONFIG['commission']
    cap += pnl - comm
    trades.append({'pnl': pnl - comm})

# Create chart
fig, axes = plt.subplots(3, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
fig.suptitle('GridBot Final — Equity Curve (BTC, 40 USDT, 10x)', fontsize=14, fontweight='bold')

# 1. Equity Curve
ax1 = axes[0]
ax1.plot(timestamps, equity, color='#2196F3', linewidth=1.5, label='Equity')
ax1.axhline(y=CONFIG['initial_capital'], color='gray', linestyle='--', alpha=0.5, label='Start ($40)')
ax1.fill_between(timestamps, CONFIG['initial_capital'], equity, where=[e >= CONFIG['initial_capital'] for e in equity], alpha=0.15, color='green')
ax1.fill_between(timestamps, CONFIG['initial_capital'], equity, where=[e < CONFIG['initial_capital'] for e in equity], alpha=0.15, color='red')
ax1.set_ylabel('Equity ($)', fontsize=11)
ax1.set_title(f'PnL: ${equity[-1]-CONFIG["initial_capital"]:.2f} ({(equity[-1]/CONFIG["initial_capital"]-1)*100:.1f}%)')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# 2. BTC Price
ax2 = axes[1]
ax2.plot(timestamps, df['Close'].iloc[20:], color='#FF9800', linewidth=1, label='BTC Price')
ax2.set_ylabel('BTC Price ($)', fontsize=11)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

# 3. Drawdown
ax3 = axes[2]
peak = CONFIG['initial_capital']
dd = []
for e in equity:
    if e > peak: peak = e
    dd.append((peak - e) / peak * 100)
ax3.fill_between(timestamps, 0, dd, color='red', alpha=0.4)
ax3.set_ylabel('Drawdown (%)', fontsize=11)
ax3.set_xlabel('Date', fontsize=11)
ax3.invert_yaxis()
ax3.grid(True, alpha=0.3)

ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('TsLabWorkspace/GridADAUSDT/GridBot_EquityCurve.png', dpi=150, bbox_inches='tight')
print("График сохранён: GridBot_EquityCurve.png")

# Trade distribution
fig2, (ax_pnl, ax_type) = plt.subplots(1, 2, figsize=(12, 4))
fig2.suptitle('Trade Analysis', fontsize=12, fontweight='bold')

pnl_values = [t['pnl'] for t in trades]
colors = ['green' if p > 0 else 'red' for p in pnl_values]
ax_pnl.bar(range(len(pnl_values)), pnl_values, color=colors, alpha=0.7, width=0.8)
ax_pnl.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
ax_pnl.set_xlabel('Trade #')
ax_pnl.set_ylabel('PnL ($)')
ax_pnl.set_title(f'Trade PnL (Win: {len([p for p in pnl_values if p>0])}/{len(pnl_values)})')
ax_pnl.grid(True, alpha=0.3)

# Cumulative PnL
cum_pnl = np.cumsum(pnl_values)
ax_type.plot(cum_pnl, color='#4CAF50', linewidth=1.5)
ax_type.fill_between(range(len(cum_pnl)), 0, cum_pnl, where=[c >= 0 for c in cum_pnl], alpha=0.2, color='green')
ax_type.fill_between(range(len(cum_pnl)), 0, cum_pnl, where=[c < 0 for c in cum_pnl], alpha=0.2, color='red')
ax_type.set_xlabel('Trade #')
ax_type.set_ylabel('Cumulative PnL ($)')
ax_type.set_title('Cumulative PnL')
ax_type.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('TsLabWorkspace/GridADAUSDT/GridBot_TradeAnalysis.png', dpi=150, bbox_inches='tight')
print("График сохранён: GridBot_TradeAnalysis.png")
