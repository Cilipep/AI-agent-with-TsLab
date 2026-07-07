import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product

df = yf.download('ADA-USD', period='5d', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"Data: {len(df)} bars, {df.index[0]} — {df.index[-1]}")
print(f"Price range: {df['Low'].min():.4f} — {df['High'].max():.4f}")

def calc_atr(df, period=14):
    h, l, c = df['High'], df['Low'], df['Close'].shift(1)
    tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

df['ATR'] = calc_atr(df, 14)
df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()

def run_grid_filtered(df, grid_mult, stop_mult, shares, ema_filter='ema200',
                      commission=0.0005, initial_capital=25.0):
    capital = initial_capital
    positions = []
    trades = []
    equity = []

    for i in range(50, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        atr = df['ATR'].iloc[i]
        ema_val = df[ema_filter].iloc[i] if ema_filter and ema_filter in df.columns else None

        if pd.isna(atr) or atr <= 0:
            equity.append(capital)
            continue

        grid_spacing = atr * grid_mult
        stop_level = atr * stop_mult
        close, low, high = row['Close'], row['Low'], row['High']

        # Exits
        closed = []
        for pos in positions:
            if pos['type'] == 'long':
                if low <= pos['stop']:
                    pnl = (pos['stop'] - pos['entry']) * pos['shares']
                    comm = (pos['entry'] + pos['stop']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'stop'})
                    closed.append(pos)
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['entry']) * pos['shares']
                    comm = (pos['entry'] + pos['tp']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'tp'})
                    closed.append(pos)
            elif pos['type'] == 'short':
                if high >= pos['stop']:
                    pnl = (pos['entry'] - pos['stop']) * pos['shares']
                    comm = (pos['entry'] + pos['stop']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'stop'})
                    closed.append(pos)
                elif low <= pos['tp']:
                    pnl = (pos['entry'] - pos['tp']) * pos['shares']
                    comm = (pos['entry'] + pos['tp']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'tp'})
                    closed.append(pos)
        for p in closed:
            positions.remove(p)

        # Entries with trend filter
        long_condition = close < prev['Close']  # price dropped
        short_condition = close > prev['Close']  # price rose

        if ema_val is not None and not pd.isna(ema_val):
            trend_long = close > ema_val
            trend_short = close < ema_val
        else:
            trend_long = True
            trend_short = True

        if long_condition and trend_long and len([p for p in positions if p['type'] == 'long']) == 0:
            positions.append({'type': 'long', 'entry': close, 'shares': shares,
                            'stop': close - stop_level, 'tp': close + grid_spacing})
        elif short_condition and trend_short and len([p for p in positions if p['type'] == 'short']) == 0:
            positions.append({'type': 'short', 'entry': close, 'shares': shares,
                            'stop': close + stop_level, 'tp': close - grid_spacing})

        unrealized = sum((close - p['entry']) * p['shares'] if p['type'] == 'long'
                        else (p['entry'] - close) * p['shares'] for p in positions)
        equity.append(capital + unrealized)

    # Close remaining
    for pos in positions:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['entry']) if pos['type'] == 'long' else (pos['entry'] - lp)) * pos['shares']
        comm = (pos['entry'] + lp) * pos['shares'] * commission
        capital += pnl - comm
        trades.append({'pnl': pnl - comm, 'reason': 'close'})

    if not trades:
        return None

    total_pnl = capital - initial_capital
    wins = [t for t in trades if t['pnl'] > 0]
    win_rate = len(wins) / len(trades) if trades else 0
    gross_profit = sum(t['pnl'] for t in wins) if wins else 0
    gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] <= 0)) or 0.01
    pf = gross_profit / gross_loss

    peak = initial_capital
    max_dd = 0
    for eq in equity:
        if eq > peak: peak = eq
        dd = (peak - eq) / peak
        if dd > max_dd: max_dd = dd

    returns = pd.Series(equity).pct_change().dropna()
    sharpe = (returns.mean() / returns.std() * np.sqrt(48 * 365)) if len(returns) > 1 and returns.std() > 0 else 0

    stop_trades = len([t for t in trades if t['reason'] == 'stop'])
    tp_trades = len([t for t in trades if t['reason'] == 'tp'])

    return {
        'grid_mult': grid_mult, 'stop_mult': stop_mult, 'shares': shares,
        'filter': ema_filter,
        'net_pnl': total_pnl, 'net_pnl_pct': total_pnl / initial_capital * 100,
        'trades': len(trades), 'win_rate': win_rate * 100,
        'profit_factor': pf, 'max_dd': max_dd * 100, 'sharpe': sharpe,
        'stop_trades': stop_trades, 'tp_trades': tp_trades
    }

# Compare: no filter vs EMA200 vs EMA50
print("\n" + "="*95)
print("COMPARISON: No Filter vs EMA200 vs EMA50")
print("="*95)

configs = [
    ('No Filter', ''),
    ('EMA200', 'ema200'),
    ('EMA50', 'ema50'),
]

best_results = []
for label, ema in configs:
    results = []
    for gm in [1.0, 1.5, 2.0, 2.5, 3.0]:
        for sm in [1.5, 2.0, 2.5, 3.0]:
            for sh in [5, 10, 15, 20]:
                r = run_grid_filtered(df, gm, sm, sh, ema_filter=ema)
                if r:
                    results.append(r)
    if results:
        best = max(results, key=lambda x: x['sharpe'])
        best_results.append((label, best))
        print(f"\n--- {label} ---")
        print(f"  Best: Grid={best['grid_mult']}, Stop={best['stop_mult']}, Shares={best['shares']}")
        print(f"  PnL: ${best['net_pnl']:.4f} ({best['net_pnl_pct']:.1f}%)")
        print(f"  Trades: {best['trades']} (TP:{best['tp_trades']}, SL:{best['stop_trades']})")
        print(f"  Win Rate: {best['win_rate']:.0f}%")
        print(f"  Profit Factor: {best['profit_factor']:.2f}")
        print(f"  Max Drawdown: {best['max_dd']:.1f}%")
        print(f"  Sharpe: {best['sharpe']:.2f}")

# Full optimization with best filter
print("\n" + "="*95)
print("FULL OPTIMIZATION WITH EMA200 FILTER")
print("="*95)

all_results = []
for gm in [0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0]:
    for sm in [1.0, 1.5, 2.0, 2.5, 3.0]:
        for sh in [5, 10, 15, 20]:
            r = run_grid_filtered(df, gm, sm, sh, ema_filter='ema200')
            if r:
                all_results.append(r)

all_results.sort(key=lambda x: x['sharpe'], reverse=True)
print(f"{'Grid':>6} {'Stop':>6} {'Shares':>6} {'PnL$':>8} {'PnL%':>7} {'Trades':>6} {'Win%':>6} {'PF':>6} {'MaxDD%':>7} {'Sharpe':>7} {'TP':>4} {'SL':>4}")
print("-"*95)
for r in all_results[:15]:
    print(f"{r['grid_mult']:>6.2f} {r['stop_mult']:>6.1f} {r['shares']:>6} {r['net_pnl']:>8.4f} {r['net_pnl_pct']:>6.1f}% {r['trades']:>6} {r['win_rate']:>5.0f}% {r['profit_factor']:>6.2f} {r['max_dd']:>6.1f}% {r['sharpe']:>7.2f} {r['tp_trades']:>4} {r['stop_trades']:>4}")

import json
with open('TsLabWorkspace/GridADAUSDT/optimization_filtered.json', 'w') as f:
    json.dump({'best_without_filter': best_results[0][1] if best_results else None,
               'best_with_ema200': best_results[1][1] if len(best_results) > 1 else None,
               'best_with_ema50': best_results[2][1] if len(best_results) > 2 else None,
               'top15_ema200': all_results[:15]}, f, indent=2)

print(f"\nSaved to optimization_filtered.json")
