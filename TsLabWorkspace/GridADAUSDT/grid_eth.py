import yfinance as yf
import pandas as pd
import numpy as np

df = yf.download('ETH-USD', period='1mo', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"ETH: {len(df)} bars, ${df['Close'].iloc[0]:.0f} — ${df['Close'].iloc[-1]:.0f}")

def calc_atr(df, p=14):
    h, l, c = df['High'], df['Low'], df['Close'].shift(1)
    return pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1).rolling(p).mean()

df['ATR'] = calc_atr(df)

INITIAL = 25.0
COMM = 0.0005

def run(df, gm, sm, risk_pct):
    cap = INITIAL
    pos = None
    trades = []
    equity = []

    for i in range(20, len(df)):
        atr = df['ATR'].iloc[i]
        if pd.isna(atr) or atr <= 0:
            equity.append(cap)
            continue

        close, low, high = df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i]
        prev = df['Close'].iloc[i-1]
        grid = atr * gm
        stop_dist = atr * sm

        if pos:
            if pos['t'] == 'long':
                if low <= pos['s']:
                    pnl = (pos['s'] - pos['e']) * pos['q']
                    comm = (pos['e'] + pos['s']) * pos['q'] * COMM
                    cap += pnl - comm
                    trades.append({'pnl': pnl - comm, 'r': 'sl'})
                    pos = None
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['e']) * pos['q']
                    comm = (pos['e'] + pos['tp']) * pos['q'] * COMM
                    cap += pnl - comm
                    trades.append({'pnl': pnl - comm, 'r': 'tp'})
                    pos = None
            else:
                if high >= pos['s']:
                    pnl = (pos['e'] - pos['s']) * pos['q']
                    comm = (pos['e'] + pos['s']) * pos['q'] * COMM
                    cap += pnl - comm
                    trades.append({'pnl': pnl - comm, 'r': 'sl'})
                    pos = None
                elif low <= pos['tp']:
                    pnl = (pos['e'] - pos['tp']) * pos['q']
                    comm = (pos['e'] + pos['tp']) * pos['q'] * COMM
                    cap += pnl - comm
                    trades.append({'pnl': pnl - comm, 'r': 'tp'})
                    pos = None

        if pos is None and cap > 1:
            risk_m = cap * risk_pct
            qty = risk_m / stop_dist if stop_dist > 0 else 0
            if close < prev:
                pos = {'t': 'long', 'e': close, 'q': qty, 's': close - stop_dist, 'tp': close + grid}
            elif close > prev:
                pos = {'t': 'short', 'e': close, 'q': qty, 's': close + stop_dist, 'tp': close - grid}

        unr = 0
        if pos:
            unr = (close - pos['e']) * pos['q'] if pos['t'] == 'long' else (pos['e'] - close) * pos['q']
        equity.append(cap + unr)

    if pos:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['e']) if pos['t'] == 'long' else (pos['e'] - lp)) * pos['q']
        comm = (pos['e'] + lp) * pos['q'] * COMM
        cap += pnl - comm
        trades.append({'pnl': pnl - comm, 'r': 'close'})

    if not trades: return None
    wins = [t for t in trades if t['pnl'] > 0]
    w = len(wins) / len(trades)
    gp = sum(t['pnl'] for t in wins) if wins else 0
    gl = abs(sum(t['pnl'] for t in trades if t['pnl'] <= 0)) or 0.001
    pf = gp / gl
    pk = INITIAL
    mdd = 0
    for e in equity:
        if e > pk: pk = e
        d = (pk - e) / pk
        if d > mdd: mdd = d
    ret = pd.Series(equity).pct_change().dropna()
    sh = (ret.mean() / ret.std() * np.sqrt(48*365)) if len(ret) > 1 and ret.std() > 0 else 0
    pnl = cap - INITIAL
    return {'gm': gm, 'sm': sm, 'risk': risk_pct, 'pnl': pnl, 'pnl_pct': pnl/INITIAL*100,
            'trades': len(trades), 'wr': w*100, 'pf': pf, 'mdd': mdd*100, 'sh': sh,
            'tp': len([t for t in trades if t['r']=='tp']), 'sl': len([t for t in trades if t['r']=='sl'])}

print("\nRunning ETH optimization...\n")
results = []
for gm in [1.0, 1.5, 2.0, 2.5, 3.0]:
    for sm in [1.5, 2.0, 2.5, 3.0]:
        for rp in [0.01, 0.02, 0.05, 0.10]:
            r = run(df, gm, sm, rp)
            if r: results.append(r)

results.sort(key=lambda x: x['sh'], reverse=True)

fmt = "{:>5} {:>5} {:>5} {:>9} {:>7} {:>4} {:>5} {:>5} {:>5} {:>7} {:>3} {:>3}"
print("=== TOP 15 BY SHARPE ===")
print(fmt.format("Grid","Stop","Risk","PnL$","PnL%","Trd","Win%","PF","DD%","Sharpe","TP","SL"))
for r in results[:15]:
    print(fmt.format(f"{r['gm']:.1f}", f"{r['sm']:.1f}", f"{r['risk']*100:.0f}%",
          f"${r['pnl']:.2f}", f"{r['pnl_pct']:.1f}%", r['trades'], f"{r['wr']:.0f}%",
          f"{r['pf']:.2f}", f"{r['mdd']:.1f}%", f"{r['sh']:.2f}", r['tp'], r['sl']))

best = results[0]
print(f"\n{'='*80}")
print(f"BEST: Grid={best['gm']}, Stop={best['sm']}, Risk={best['risk']*100:.0f}%")
print(f"PnL: ${best['pnl']:.2f} ({best['pnl_pct']:.1f}%) | WR: {best['wr']:.0f}% | PF: {best['pf']:.2f} | DD: {best['mdd']:.1f}% | Sharpe: {best['sh']:.2f}")
print(f"{'='*80}")

# Compare all 3 coins
print(f"\n{'='*80}")
print(f"COMPARISON: BTC vs ETH vs ADA")
print(f"{'='*80}")
print(f"{'Coin':<6} {'Grid':>5} {'Stop':>5} {'Risk':>5} {'PnL%':>7} {'WR':>5} {'PF':>5} {'DD%':>6} {'Sharpe':>7}")
btc = {'coin': 'BTC', 'gm': 2.5, 'sm': 3.0, 'risk': 0.10, 'pnl_pct': 16.0, 'wr': 62, 'pf': 1.07, 'mdd': 35.6, 'sh': 2.15}
eth = {'coin': 'ETH', 'gm': best['gm'], 'sm': best['sm'], 'risk': best['risk'],
       'pnl_pct': best['pnl_pct'], 'wr': best['wr'], 'pf': best['pf'], 'mdd': best['mdd'], 'sh': best['sh']}
ada = {'coin': 'ADA', 'gm': 2.0, 'sm': 3.0, 'risk': 0.10, 'pnl_pct': -0.2, 'wr': 61, 'pf': 0.95, 'mdd': 1.2, 'sh': -2.05}
for c in [btc, eth, ada]:
    print(f"{c['coin']:<6} {c['gm']:>5.1f} {c['sm']:>5.1f} {c['risk']*100:>4.0f}% {c['pnl_pct']:>6.1f}% {c['wr']:>4.0f}% {c['pf']:>5.2f} {c['mdd']:>5.1f}% {c['sh']:>7.2f}")

import json
with open('TsLabWorkspace/GridADAUSDT/optimization_eth.json', 'w') as f:
    json.dump({'best': best, 'top15': results[:15], 'total': len(results),
               'btc_eth_ada': [btc, eth, ada]}, f, indent=2)
