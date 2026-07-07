import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product

# Download data
df = yf.download('ADA-USD', period='5d', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"Data: {len(df)} bars\n")

def calc_atr(df, period=14):
    h = df['High']
    l = df['Low']
    c = df['Close'].shift(1)
    tr = pd.concat([h - l, (h - c).abs(), (l - c).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

df['ATR'] = calc_atr(df, 14)

def run_grid(df, grid_mult, stop_mult, shares, commission=0.0005, reinvest=0.10, initial_capital=25.0):
    capital = initial_capital
    positions = []
    trades = []
    equity = []

    for i in range(15, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        atr = df['ATR'].iloc[i]

        if pd.isna(atr) or atr <= 0:
            equity.append(capital)
            continue

        grid_spacing = atr * grid_mult
        stop_level = atr * stop_mult
        close = row['Close']
        low = row['Low']
        high = row['High']

        # Exits
        closed = []
        for pos in positions:
            if pos['type'] == 'long':
                if low <= pos['stop']:
                    pnl = (pos['stop'] - pos['entry']) * pos['shares']
                    comm = (pos['entry'] + pos['stop']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm})
                    closed.append(pos)
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['entry']) * pos['shares']
                    comm = (pos['entry'] + pos['tp']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm})
                    closed.append(pos)
            elif pos['type'] == 'short':
                if high >= pos['stop']:
                    pnl = (pos['entry'] - pos['stop']) * pos['shares']
                    comm = (pos['entry'] + pos['stop']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm})
                    closed.append(pos)
                elif low <= pos['tp']:
                    pnl = (pos['entry'] - pos['tp']) * pos['shares']
                    comm = (pos['entry'] + pos['tp']) * pos['shares'] * commission
                    capital += pnl - comm
                    trades.append({'pnl': pnl - comm})
                    closed.append(pos)
        for p in closed:
            positions.remove(p)

        # Entries
        if close < prev['Close'] and len([p for p in positions if p['type'] == 'long']) == 0:
            positions.append({'type': 'long', 'entry': close, 'shares': shares,
                            'stop': close - stop_level, 'tp': close + grid_spacing})
        elif close > prev['Close'] and len([p for p in positions if p['type'] == 'short']) == 0:
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
        trades.append({'pnl': pnl - comm})

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

    return {
        'grid_mult': grid_mult, 'stop_mult': stop_mult, 'shares': shares,
        'net_pnl': total_pnl, 'net_pnl_pct': total_pnl / initial_capital * 100,
        'trades': len(trades), 'win_rate': win_rate * 100,
        'profit_factor': pf, 'max_dd': max_dd * 100, 'sharpe': sharpe
    }

# Parameter grid
grid_mults = [0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0]
stop_mults = [1.0, 1.5, 2.0, 2.5, 3.0]
shares_list = [5, 10, 15, 20]

print("Running optimization...")
print(f"Combinations: {len(grid_mults) * len(stop_mults) * len(shares_list)}")

results = []
for gm, sm, sh in product(grid_mults, stop_mults, shares_list):
    r = run_grid(df, gm, sm, sh)
    if r:
        results.append(r)

results.sort(key=lambda x: x['sharpe'], reverse=True)

print(f"\n{'='*90}")
print(f"TOP 10 BY SHARPE RATIO")
print(f"{'='*90}")
print(f"{'Grid':>6} {'Stop':>6} {'Shares':>6} {'PnL$':>8} {'PnL%':>7} {'Trades':>6} {'Win%':>6} {'PF':>6} {'MaxDD%':>7} {'Sharpe':>7}")
print(f"{'-'*90}")
for r in results[:10]:
    print(f"{r['grid_mult']:>6.2f} {r['stop_mult']:>6.1f} {r['shares']:>6} {r['net_pnl']:>8.4f} {r['net_pnl_pct']:>6.1f}% {r['trades']:>6} {r['win_rate']:>5.0f}% {r['profit_factor']:>6.2f} {r['max_dd']:>6.1f}% {r['sharpe']:>7.2f}")

print(f"\n{'='*90}")
print(f"TOP 10 BY PROFIT FACTOR")
print(f"{'='*90}")
results_pf = sorted(results, key=lambda x: x['profit_factor'], reverse=True)
print(f"{'Grid':>6} {'Stop':>6} {'Shares':>6} {'PnL$':>8} {'PnL%':>7} {'Trades':>6} {'Win%':>6} {'PF':>6} {'MaxDD%':>7} {'Sharpe':>7}")
print(f"{'-'*90}")
for r in results_pf[:10]:
    print(f"{r['grid_mult']:>6.2f} {r['stop_mult']:>6.1f} {r['shares']:>6} {r['net_pnl']:>8.4f} {r['net_pnl_pct']:>6.1f}% {r['trades']:>6} {r['win_rate']:>5.0f}% {r['profit_factor']:>6.2f} {r['max_dd']:>6.1f}% {r['sharpe']:>7.2f}")

# Save
import json
with open('TsLabWorkspace/GridADAUSDT/optimization_results.json', 'w') as f:
    json.dump(results[:20], f, indent=2)

print(f"\nBest: Grid={results[0]['grid_mult']}, Stop={results[0]['stop_mult']}, Shares={results[0]['shares']}")
print(f"Sharpe={results[0]['sharpe']:.2f}, PF={results[0]['profit_factor']:.2f}, PnL={results[0]['net_pnl_pct']:.1f}%")
