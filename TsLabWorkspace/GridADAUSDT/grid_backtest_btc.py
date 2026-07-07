import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product

# Download BTC data - 1 month for EMA200
df = yf.download('BTC-USD', period='1mo', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"BTC Data: {len(df)} bars, {df.index[0]} — {df.index[-1]}")
print(f"Price range: ${df['Low'].min():.0f} — ${df['High'].max():.0f}")

def calc_atr(df, period=14):
    h, l, c = df['High'], df['Low'], df['Close'].shift(1)
    tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

df['ATR'] = calc_atr(df, 14)
df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

def run_grid(df, grid_mult, stop_mult, shares, use_filter=False,
             commission=0.0005, initial_capital=25.0):
    capital = initial_capital
    positions = []
    trades = []
    equity = []

    for i in range(210, len(df)):  # start after EMA200 warmup
        row = df.iloc[i]
        prev = df.iloc[i-1]
        atr = df['ATR'].iloc[i]

        if pd.isna(atr) or atr <= 0:
            equity.append(capital)
            continue

        grid_spacing = atr * grid_mult
        stop_level = atr * stop_mult
        close, low, high = row['Close'], row['Low'], row['High']
        ema = df['EMA200'].iloc[i]

        # Exits
        closed = []
        for pos in positions:
            if pos['type'] == 'long':
                if low <= pos['stop']:
                    pnl = (pos['stop'] - pos['entry']) * pos['shares']
                    comm = (pos['entry'] + pos['stop']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'stop', 'type': 'long'})
                    closed.append(pos)
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['entry']) * pos['shares']
                    comm = (pos['entry'] + pos['tp']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'tp', 'type': 'long'})
                    closed.append(pos)
            elif pos['type'] == 'short':
                if high >= pos['stop']:
                    pnl = (pos['entry'] - pos['stop']) * pos['shares']
                    comm = (pos['entry'] + pos['stop']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'stop', 'type': 'short'})
                    closed.append(pos)
                elif low <= pos['tp']:
                    pnl = (pos['entry'] - pos['tp']) * pos['shares']
                    comm = (pos['entry'] + pos['tp']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'tp', 'type': 'short'})
                    closed.append(pos)
        for p in closed:
            positions.remove(p)

        # Trend filter
        if use_filter and not pd.isna(ema):
            trend_long = close > ema
            trend_short = close < ema
        else:
            trend_long = True
            trend_short = True

        # Entries
        price_drop = close < prev['Close']
        price_rise = close > prev['Close']

        if price_drop and trend_long and len([p for p in positions if p['type'] == 'long']) == 0:
            positions.append({'type': 'long', 'entry': close, 'shares': shares,
                            'stop': close - stop_level, 'tp': close + grid_spacing})
        elif price_rise and trend_short and len([p for p in positions if p['type'] == 'short']) == 0:
            positions.append({'type': 'short', 'entry': close, 'shares': shares,
                            'stop': close + stop_level, 'tp': close - grid_spacing})

        unrealized = sum((close - p['entry']) * p['shares'] if p['type'] == 'long'
                        else (p['entry'] - close) * p['shares'] for p in positions)
        equity.append(capital + unrealized)

    for pos in positions:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['entry']) if pos['type'] == 'long' else (pos['entry'] - lp)) * pos['shares']
        comm = (pos['entry'] + lp) * pos['shares'] * commission
        capital += pnl - comm
        trades.append({'pnl': pnl - comm, 'reason': 'close', 'type': pos['type']})

    if not trades:
        return None

    total_pnl = capital - initial_capital
    wins = [t for t in trades if t['pnl'] > 0]
    win_rate = len(wins) / len(trades)
    gp = sum(t['pnl'] for t in wins) if wins else 0
    gl = abs(sum(t['pnl'] for t in trades if t['pnl'] <= 0)) or 0.001
    pf = gp / gl

    peak = initial_capital
    max_dd = 0
    for eq in equity:
        if eq > peak: peak = eq
        dd = (peak - eq) / peak
        if dd > max_dd: max_dd = dd

    ret = pd.Series(equity).pct_change().dropna()
    sharpe = (ret.mean() / ret.std() * np.sqrt(48 * 365)) if len(ret) > 1 and ret.std() > 0 else 0

    longs = len([t for t in trades if t['type'] == 'long'])
    shorts = len([t for t in trades if t['type'] == 'short'])
    tp = len([t for t in trades if t['reason'] == 'tp'])
    sl = len([t for t in trades if t['reason'] == 'stop'])

    return {
        'grid_mult': grid_mult, 'stop_mult': stop_mult, 'shares': shares,
        'filter': use_filter, 'net_pnl': total_pnl, 'net_pnl_pct': total_pnl / initial_capital * 100,
        'trades': len(trades), 'win_rate': win_rate * 100, 'pf': pf, 'max_dd': max_dd * 100,
        'sharpe': sharpe, 'tp': tp, 'sl': sl, 'longs': longs, 'shorts': shorts
    }

# Optimization
print("\n" + "="*100)
print("GRID STRATEGY ON BTC — 1 MONTH OPTIMIZATION")
print("="*100)

all_results = []
for gm in [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]:
    for sm in [1.5, 2.0, 2.5, 3.0, 4.0]:
        for sh in [5, 10, 15, 20]:
            for filt in [False, True]:
                r = run_grid(df, gm, sm, sh, use_filter=filt)
                if r:
                    all_results.append(r)

# Without filter
no_filter = [r for r in all_results if not r['filter']]
with_filter = [r for r in all_results if r['filter']]

no_filter.sort(key=lambda x: x['sharpe'], reverse=True)
with_filter.sort(key=lambda x: x['sharpe'], reverse=True)

print(f"\n--- WITHOUT FILTER (top 5) ---")
print(f"{'Grid':>6} {'Stop':>6} {'Sh':>4} {'PnL$':>9} {'PnL%':>7} {'Trd':>4} {'Win%':>5} {'PF':>5} {'DD%':>5} {'Sharpe':>7} {'L':>3} {'S':>3} {'TP':>3} {'SL':>3}")
for r in no_filter[:5]:
    f_str = "EMA" if r['filter'] else "---"
    print(f"{r['grid_mult']:>6.1f} {r['stop_mult']:>6.1f} {r['shares']:>4} ${r['net_pnl']:>8.2f} {r['net_pnl_pct']:>6.1f}% {r['trades']:>4} {r['win_rate']:>4.0f}% {r['pf']:>5.2f} {r['max_dd']:>4.1f}% {r['sharpe']:>7.2f} {r['longs']:>3} {r['shorts']:>3} {r['tp']:>3} {r['sl']:>3}")

print(f"\n--- WITH EMA200 FILTER (top 5) ---")
print(f"{'Grid':>6} {'Stop':>6} {'Sh':>4} {'PnL$':>9} {'PnL%':>7} {'Trd':>4} {'Win%':>5} {'PF':>5} {'DD%':>5} {'Sharpe':>7} {'L':>3} {'S':>3} {'TP':>3} {'SL':>3}")
for r in with_filter[:5]:
    print(f"{r['grid_mult']:>6.1f} {r['stop_mult']:>6.1f} {r['shares']:>4} ${r['net_pnl']:>8.2f} {r['net_pnl_pct']:>6.1f}% {r['trades']:>4} {r['win_rate']:>4.0f}% {r['pf']:>5.2f} {r['max_dd']:>4.1f}% {r['sharpe']:>7.2f} {r['longs']:>3} {r['shorts']:>3} {r['tp']:>3} {r['sl']:>3}")

# Best overall
best = max(all_results, key=lambda x: x['sharpe'])
print(f"\n{'='*100}")
print(f"BEST OVERALL: Grid={best['grid_mult']}, Stop={best['stop_mult']}, Shares={best['shares']}, Filter={'EMA200' if best['filter'] else 'None'}")
print(f"PnL: ${best['net_pnl']:.2f} ({best['net_pnl_pct']:.1f}%)")
print(f"Trades: {best['trades']} (Win: {best['win_rate']:.0f}%, PF: {best['pf']:.2f})")
print(f"Max DD: {best['max_dd']:.1f}%, Sharpe: {best['sharpe']:.2f}")
print(f"{'='*100}")

import json
with open('TsLabWorkspace/GridADAUSDT/optimization_btc.json', 'w') as f:
    json.dump({'best_no_filter': no_filter[0], 'best_with_filter': with_filter[0],
               'best_overall': best, 'total_combinations': len(all_results),
               'top10': sorted(all_results, key=lambda x: x['sharpe'], reverse=True)[:10]}, f, indent=2)
