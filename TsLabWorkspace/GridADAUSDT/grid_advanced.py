import yfinance as yf
import pandas as pd
import numpy as np

df = yf.download('BTC-USD', period='1mo', interval='30m', progress=False)
df.columns = df.columns.droplevel(1)
print(f"BTC: {len(df)} bars, ${df['Close'].iloc[0]:.0f} — ${df['Close'].iloc[-1]:.0f}")

def calc_atr(df, p=14):
    h, l, c = df['High'], df['Low'], df['Close'].shift(1)
    return pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1).rolling(p).mean()

def calc_adx(df, p=14):
    plus_dm = df['High'].diff()
    minus_dm = -df['Low'].diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    atr = calc_atr(df, p)
    plus_di = 100 * (plus_dm.ewm(alpha=1/p).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1/p).mean() / atr)
    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1))
    return dx.ewm(alpha=1/p).mean()

df['ATR'] = calc_atr(df)
df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
df['ADX'] = calc_adx(df)
df['RSI'] = 100 - 100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() /
                          df['Close'].diff().clip(upper=0).abs().rolling(14).mean().replace(0, 1))

INITIAL = 25.0
COMM = 0.0005

# === VERSION 1: Base Grid (baseline) ===
def run_v1(df, gm, sm, risk_pct):
    cap = INITIAL
    pos = None
    trades = []
    equity = []
    for i in range(20, len(df)):
        atr = df['ATR'].iloc[i]
        if pd.isna(atr) or atr <= 0:
            equity.append(cap); continue
        close, low, high = df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i]
        prev = df['Close'].iloc[i-1]
        grid, stop_d = atr * gm, atr * sm
        if pos:
            if pos['t'] == 'long':
                if low <= pos['s']:
                    pnl = (pos['s'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
            else:
                if high >= pos['s']:
                    pnl = (pos['e'] - pos['s']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif low <= pos['tp']:
                    pnl = (pos['e'] - pos['tp']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
        if pos is None and cap > 1:
            qty = (cap * risk_pct) / stop_d if stop_d > 0 else 0
            if close < prev:
                pos = {'t': 'long', 'e': close, 'q': qty, 's': close - stop_d, 'tp': close + grid}
            elif close > prev:
                pos = {'t': 'short', 'e': close, 'q': qty, 's': close + stop_d, 'tp': close - grid}
        unr = (close - pos['e']) * pos['q'] if pos and pos['t'] == 'long' else (
            (pos['e'] - close) * pos['q'] if pos else 0)
        equity.append(cap + unr)
    if pos:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['e']) if pos['t'] == 'long' else (pos['e'] - lp)) * pos['q']
        cap += pnl - (pos['e'] + lp) * pos['q'] * COMM
        trades.append({'pnl': pnl})
    return cap, trades, equity

# === VERSION 2: With ADX filter (skip trending markets) ===
def run_v2(df, gm, sm, risk_pct, adx_thresh=25):
    cap = INITIAL
    pos = None
    trades = []
    equity = []
    for i in range(20, len(df)):
        atr = df['ATR'].iloc[i]
        adx = df['ADX'].iloc[i]
        if pd.isna(atr) or atr <= 0 or pd.isna(adx):
            equity.append(cap); continue
        close, low, high = df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i]
        prev = df['Close'].iloc[i-1]
        grid, stop_d = atr * gm, atr * sm
        trending = adx > adx_thresh
        if pos:
            if pos['t'] == 'long':
                if low <= pos['s']:
                    pnl = (pos['s'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
            else:
                if high >= pos['s']:
                    pnl = (pos['e'] - pos['s']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif low <= pos['tp']:
                    pnl = (pos['e'] - pos['tp']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
        if pos is None and cap > 1 and not trending:
            qty = (cap * risk_pct) / stop_d if stop_d > 0 else 0
            if close < prev:
                pos = {'t': 'long', 'e': close, 'q': qty, 's': close - stop_d, 'tp': close + grid}
            elif close > prev:
                pos = {'t': 'short', 'e': close, 'q': qty, 's': close + stop_d, 'tp': close - grid}
        unr = (close - pos['e']) * pos['q'] if pos and pos['t'] == 'long' else (
            (pos['e'] - close) * pos['q'] if pos else 0)
        equity.append(cap + unr)
    if pos:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['e']) if pos['t'] == 'long' else (pos['e'] - lp)) * pos['q']
        cap += pnl - (pos['e'] + lp) * pos['q'] * COMM
        trades.append({'pnl': pnl})
    return cap, trades, equity

# === VERSION 3: Trailing stop (moves to breakeven after 1R profit) ===
def run_v3(df, gm, sm, risk_pct):
    cap = INITIAL
    pos = None
    trades = []
    equity = []
    for i in range(20, len(df)):
        atr = df['ATR'].iloc[i]
        if pd.isna(atr) or atr <= 0:
            equity.append(cap); continue
        close, low, high = df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i]
        prev = df['Close'].iloc[i-1]
        grid, stop_d = atr * gm, atr * sm
        if pos:
            # Update trailing stop
            if pos['t'] == 'long' and close > pos['e'] + stop_d:
                new_stop = pos['e'] + stop_d * 0.5  # move to breakeven + buffer
                if new_stop > pos['s']:
                    pos['s'] = new_stop
            elif pos['t'] == 'short' and close < pos['e'] - stop_d:
                new_stop = pos['e'] - stop_d * 0.5
                if new_stop < pos['s']:
                    pos['s'] = new_stop
            # Check exits
            if pos['t'] == 'long':
                if low <= pos['s']:
                    pnl = (pos['s'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
            else:
                if high >= pos['s']:
                    pnl = (pos['e'] - pos['s']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif low <= pos['tp']:
                    pnl = (pos['e'] - pos['tp']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
        if pos is None and cap > 1:
            qty = (cap * risk_pct) / stop_d if stop_d > 0 else 0
            if close < prev:
                pos = {'t': 'long', 'e': close, 'q': qty, 's': close - stop_d, 'tp': close + grid}
            elif close > prev:
                pos = {'t': 'short', 'e': close, 'q': qty, 's': close + stop_d, 'tp': close - grid}
        unr = (close - pos['e']) * pos['q'] if pos and pos['t'] == 'long' else (
            (pos['e'] - close) * pos['q'] if pos else 0)
        equity.append(cap + unr)
    if pos:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['e']) if pos['t'] == 'long' else (pos['e'] - lp)) * pos['q']
        cap += pnl - (pos['e'] + lp) * pos['q'] * COMM
        trades.append({'pnl': pnl})
    return cap, trades, equity

# === VERSION 4: RSI filter (buy oversold, sell overbought) ===
def run_v4(df, gm, sm, risk_pct):
    cap = INITIAL
    pos = None
    trades = []
    equity = []
    for i in range(20, len(df)):
        atr = df['ATR'].iloc[i]
        rsi = df['RSI'].iloc[i]
        if pd.isna(atr) or atr <= 0 or pd.isna(rsi):
            equity.append(cap); continue
        close, low, high = df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i]
        prev = df['Close'].iloc[i-1]
        grid, stop_d = atr * gm, atr * sm
        if pos:
            if pos['t'] == 'long':
                if low <= pos['s']:
                    pnl = (pos['s'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
            else:
                if high >= pos['s']:
                    pnl = (pos['e'] - pos['s']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif low <= pos['tp']:
                    pnl = (pos['e'] - pos['tp']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
        if pos is None and cap > 1:
            qty = (cap * risk_pct) / stop_d if stop_d > 0 else 0
            if close < prev and rsi < 45:  # oversold bias for longs
                pos = {'t': 'long', 'e': close, 'q': qty, 's': close - stop_d, 'tp': close + grid}
            elif close > prev and rsi > 55:  # overbought bias for shorts
                pos = {'t': 'short', 'e': close, 'q': qty, 's': close + stop_d, 'tp': close - grid}
        unr = (close - pos['e']) * pos['q'] if pos and pos['t'] == 'long' else (
            (pos['e'] - close) * pos['q'] if pos else 0)
        equity.append(cap + unr)
    if pos:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['e']) if pos['t'] == 'long' else (pos['e'] - lp)) * pos['q']
        cap += pnl - (pos['e'] + lp) * pos['q'] * COMM
        trades.append({'pnl': pnl})
    return cap, trades, equity

# === VERSION 5: Combined (ADX + trailing + RSI) ===
def run_v5(df, gm, sm, risk_pct, adx_thresh=20):
    cap = INITIAL
    pos = None
    trades = []
    equity = []
    for i in range(20, len(df)):
        atr = df['ATR'].iloc[i]
        adx = df['ADX'].iloc[i]
        rsi = df['RSI'].iloc[i]
        if pd.isna(atr) or atr <= 0 or pd.isna(adx) or pd.isna(rsi):
            equity.append(cap); continue
        close, low, high = df['Close'].iloc[i], df['Low'].iloc[i], df['High'].iloc[i]
        prev = df['Close'].iloc[i-1]
        grid, stop_d = atr * gm, atr * sm
        trending = adx > adx_thresh
        if pos:
            # Trailing stop
            if pos['t'] == 'long' and close > pos['e'] + stop_d:
                ns = pos['e'] + stop_d * 0.5
                if ns > pos['s']: pos['s'] = ns
            elif pos['t'] == 'short' and close < pos['e'] - stop_d:
                ns = pos['e'] - stop_d * 0.5
                if ns < pos['s']: pos['s'] = ns
            if pos['t'] == 'long':
                if low <= pos['s']:
                    pnl = (pos['s'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif high >= pos['tp']:
                    pnl = (pos['tp'] - pos['e']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
            else:
                if high >= pos['s']:
                    pnl = (pos['e'] - pos['s']) * pos['q']
                    cap += pnl - (pos['e'] + pos['s']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
                elif low <= pos['tp']:
                    pnl = (pos['e'] - pos['tp']) * pos['q']
                    cap += pnl - (pos['e'] + pos['tp']) * pos['q'] * COMM
                    trades.append({'pnl': pnl}); pos = None
        if pos is None and cap > 1 and not trending:
            qty = (cap * risk_pct) / stop_d if stop_d > 0 else 0
            if close < prev and rsi < 45:
                pos = {'t': 'long', 'e': close, 'q': qty, 's': close - stop_d, 'tp': close + grid}
            elif close > prev and rsi > 55:
                pos = {'t': 'short', 'e': close, 'q': qty, 's': close + stop_d, 'tp': close - grid}
        unr = (close - pos['e']) * pos['q'] if pos and pos['t'] == 'long' else (
            (pos['e'] - close) * pos['q'] if pos else 0)
        equity.append(cap + unr)
    if pos:
        lp = df['Close'].iloc[-1]
        pnl = ((lp - pos['e']) if pos['t'] == 'long' else (pos['e'] - lp)) * pos['q']
        cap += pnl - (pos['e'] + lp) * pos['q'] * COMM
        trades.append({'pnl': pnl})
    return cap, trades, equity

def metrics(cap, trades, equity):
    if not trades: return None
    pnl = cap - INITIAL
    wins = [t for t in trades if t['pnl'] > 0]
    wr = len(wins)/len(trades)*100
    gp = sum(t['pnl'] for t in wins) if wins else 0
    gl = abs(sum(t['pnl'] for t in trades if t['pnl']<=0)) or 0.001
    pf = gp/gl
    pk = INITIAL
    mdd = 0
    for e in equity:
        if e > pk: pk = e
        d = (pk-e)/pk
        if d > mdd: mdd = d
    ret = pd.Series(equity).pct_change().dropna()
    sh = (ret.mean()/ret.std()*np.sqrt(48*365)) if len(ret)>1 and ret.std()>0 else 0
    return {'pnl': pnl, 'pnl_pct': pnl/INITIAL*100, 'trades': len(trades),
            'wr': wr, 'pf': pf, 'mdd': mdd*100, 'sh': sh}

# Run all versions with best params
print("\n" + "="*100)
print("BTC GRID STRATEGY — 5 VERSIONS COMPARISON")
print("="*100)

versions = [
    ('V1: Base Grid', lambda: run_v1(df, 2.5, 3.0, 0.10)),
    ('V2: +ADX Filter', lambda: run_v2(df, 2.5, 3.0, 0.10, 25)),
    ('V3: +Trailing Stop', lambda: run_v3(df, 2.5, 3.0, 0.10)),
    ('V4: +RSI Filter', lambda: run_v4(df, 2.5, 3.0, 0.10)),
    ('V5: ADX+Trail+RSI', lambda: run_v5(df, 2.5, 3.0, 0.10, 20)),
]

print(f"{'Version':<22} {'PnL$':>8} {'PnL%':>7} {'Trades':>6} {'Win%':>5} {'PF':>5} {'DD%':>6} {'Sharpe':>7}")
print("-"*100)
best_v = None
for name, fn in versions:
    cap, trades, eq = fn()
    m = metrics(cap, trades, eq)
    if m:
        print(f"{name:<22} ${m['pnl']:>7.2f} {m['pnl_pct']:>6.1f}% {m['trades']:>6} {m['wr']:>4.0f}% {m['pf']:>5.2f} {m['mdd']:>5.1f}% {m['sh']:>7.2f}")
        if best_v is None or m['sh'] > best_v['sh']:
            best_v = m
            best_v['name'] = name

# Optimize best version further
print(f"\n{'='*100}")
print(f"OPTIMIZING BEST: {best_v['name']}")
print("="*100)

opt_results = []
for gm in [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
    for sm in [1.5, 2.0, 2.5, 3.0, 3.5]:
        for rp in [0.05, 0.08, 0.10, 0.12, 0.15]:
            for adx_t in [15, 20, 25, 30]:
                cap, trades, eq = run_v5(df, gm, sm, rp, adx_t)
                m = metrics(cap, trades, eq)
                if m:
                    m['gm'] = gm; m['sm'] = sm; m['risk'] = rp; m['adx'] = adx_t
                    opt_results.append(m)

opt_results.sort(key=lambda x: x['sh'], reverse=True)
print(f"{'Grid':>5} {'Stop':>5} {'Risk':>5} {'ADX':>4} {'PnL$':>8} {'PnL%':>7} {'Trd':>4} {'Win%':>5} {'PF':>5} {'DD%':>5} {'Sharpe':>7}")
for r in opt_results[:15]:
    print(f"{r['gm']:>5.1f} {r['sm']:>5.1f} {r['risk']*100:>4.0f}% {r['adx']:>4} ${r['pnl']:>7.2f} {r['pnl_pct']:>6.1f}% {r['trades']:>4} {r['wr']:>4.0f}% {r['pf']:>5.2f} {r['mdd']:>4.1f}% {r['sh']:>7.2f}")

final = opt_results[0]
print(f"\n{'='*100}")
print(f"FINAL BEST: Grid={final['gm']}, Stop={final['sm']}, Risk={final['risk']*100:.0f}%, ADX<{final['adx']}")
print(f"PnL: ${final['pnl']:.2f} ({final['pnl_pct']:.1f}%) | WR: {final['wr']:.0f}% | PF: {final['pf']:.2f} | DD: {final['mdd']:.1f}% | Sharpe: {final['sh']:.2f}")
print(f"{'='*100}")

import json
with open('TsLabWorkspace/GridADAUSDT/optimization_advanced.json', 'w') as f:
    json.dump({'versions': [{'name': n, 'metrics': metrics(*fn())} for n, fn in versions if metrics(*fn())],
               'top15': opt_results[:15], 'final_best': final, 'total': len(opt_results)}, f, indent=2)
