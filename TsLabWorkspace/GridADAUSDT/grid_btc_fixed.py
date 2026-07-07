import yfinance as yf
import pandas as pd
import numpy as np

df = yf.download('BTC-USD', period='1mo', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"BTC: {len(df)} bars, ${df['Close'].iloc[0]:.0f} — ${df['Close'].iloc[-1]:.0f}")

def calc_atr(df, p=14):
    h, l, c = df['High'], df['Low'], df['Close'].shift(1)
    return pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1).rolling(p).mean()

df['ATR'] = calc_atr(df)
df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

INITIAL = 25.0
COMM = 0.0005

def run(df, gm, sm, risk_pct, use_ema=False):
    cap = INITIAL
    pos = None
    trades = []
    equity = []

    for i in range(210, len(df)):
        atr = df['ATR'].iloc[i]
        if pd.isna(atr) or atr <= 0:
            equity.append(cap)
            continue

        close, low, high = df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i]
        prev_close = df['Close'].iloc[i-1]
        ema = df['EMA200'].iloc[i]
        grid = atr * gm
        stop_dist = atr * sm

        # Exit
        if pos:
            if pos['type'] == 'long':
                if low <= pos['stop']:
                    pnl = (pos['stop'] - pos['entry']) * pos['qty']
                    comm = (pos['entry'] + pos['stop']) * pos['qty'] * COMM
                    cap += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'stop'})
                    pos = None
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['entry']) * pos['qty']
                    comm = (pos['entry'] + pos['tp']) * pos['qty'] * COMM
                    cap += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'tp'})
                    pos = None
            else:
                if high >= pos['stop']:
                    pnl = (pos['entry'] - pos['stop']) * pos['qty']
                    comm = (pos['entry'] + pos['stop']) * pos['qty'] * COMM
                    cap += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'stop'})
                    pos = None
                elif low <= pos['tp']:
                    pnl = (pos['entry'] - pos['tp']) * pos['qty']
                    comm = (pos['entry'] + pos['tp']) * pos['qty'] * COMM
                    cap += pnl - comm
                    trades.append({'pnl': pnl - comm, 'reason': 'tp'})
                    pos = None

        # Entry
        if pos is None and cap > 1:
            risk_money = cap * risk_pct
            qty = risk_money / stop_dist if stop_dist > 0 else 0

            if close < prev_close:
                trend_ok = (not use_ema) or (not pd.isna(ema) and close > ema)
                if trend_ok:
                    pos = {'type': 'long', 'entry': close, 'qty': qty,
                           'stop': close - stop_dist, 'tp': close + grid}
            elif close > prev_close:
                trend_ok = (not use_ema) or (not pd.isna(ema) and close < ema)
                if trend_ok:
                    pos = {'type': 'short', 'entry': close, 'qty': qty,
                           'stop': close + stop_dist, 'tp': close - grid}

        unr = 0
        if pos:
            unr = (close - pos['entry']) * pos['qty'] if pos['type'] == 'long' else (pos['entry'] - close) * pos['qty']
        equity.append(cap + unr)

    # Close last
    if pos:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['entry']) if pos['type'] == 'long' else (pos['entry'] - lp)) * pos['qty']
        comm = (pos['entry'] + lp) * pos['qty'] * COMM
        cap += pnl - comm
        trades.append({'pnl': pnl - comm, 'reason': 'close'})

    if not trades:
        return None

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

    return {'gm': gm, 'sm': sm, 'risk': risk_pct, 'ema': use_ema,
            'pnl': pnl, 'pnl_pct': pnl/INITIAL*100, 'trades': len(trades),
            'wr': w*100, 'pf': pf, 'mdd': mdd*100, 'sh': sh,
            'tp': len([t for t in trades if t['reason']=='tp']),
            'sl': len([t for t in trades if t['reason']=='stop'])}

print("\nRunning optimization (160 combinations)...\n")
results = []
for gm in [1.0, 1.5, 2.0, 2.5, 3.0]:
    for sm in [1.5, 2.0, 2.5, 3.0]:
        for rp in [0.01, 0.02, 0.05, 0.10]:
            for ema in [False, True]:
                r = run(df, gm, sm, rp, ema)
                if r: results.append(r)

nf = sorted([r for r in results if not r['ema']], key=lambda x: x['sh'], reverse=True)
wf = sorted([r for r in results if r['ema']], key=lambda x: x['sh'], reverse=True)

fmt = "{:>5} {:>5} {:>5} {:>9} {:>7} {:>4} {:>5} {:>5} {:>5} {:>7} {:>3} {:>3}"
print("=== WITHOUT FILTER (top 10) ===")
print(fmt.format("Grid","Stop","Risk","PnL$","PnL%","Trd","Win%","PF","DD%","Sharpe","TP","SL"))
for r in nf[:10]:
    print(fmt.format(f"{r['gm']:.1f}", f"{r['sm']:.1f}", f"{r['risk']*100:.0f}%",
          f"${r['pnl']:.2f}", f"{r['pnl_pct']:.1f}%", r['trades'], f"{r['wr']:.0f}%",
          f"{r['pf']:.2f}", f"{r['mdd']:.1f}%", f"{r['sh']:.2f}", r['tp'], r['sl']))

print("\n=== WITH EMA200 FILTER (top 10) ===")
print(fmt.format("Grid","Stop","Risk","PnL$","PnL%","Trd","Win%","PF","DD%","Sharpe","TP","SL"))
for r in wf[:10]:
    print(fmt.format(f"{r['gm']:.1f}", f"{r['sm']:.1f}", f"{r['risk']*100:.0f}%",
          f"${r['pnl']:.2f}", f"{r['pnl_pct']:.1f}%", r['trades'], f"{r['wr']:.0f}%",
          f"{r['pf']:.2f}", f"{r['mdd']:.1f}%", f"{r['sh']:.2f}", r['tp'], r['sl']))

best = max(results, key=lambda x: x['sh'])
print(f"\n{'='*85}")
print(f"BEST: Grid={best['gm']}, Stop={best['sm']}, Risk={best['risk']*100:.0f}%, Filter={'EMA200' if best['ema'] else 'None'}")
print(f"PnL: ${best['pnl']:.2f} ({best['pnl_pct']:.1f}%) | WR: {best['wr']:.0f}% | PF: {best['pf']:.2f} | DD: {best['mdd']:.1f}% | Sharpe: {best['sh']:.2f}")
print(f"{'='*85}")

import json
with open('TsLabWorkspace/GridADAUSDT/optimization_btc_final.json', 'w') as f:
    json.dump({'best': best, 'top10_nofilter': nf[:10], 'top10_with_filter': wf[:10], 'total': len(results)}, f, indent=2)
