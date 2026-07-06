#!/usr/bin/env python3
"""
Optimization: Moving M15 Strategy for DOGEUSDT (fast version)
"""

import pandas as pd
import numpy as np
from itertools import product

def smma(series, period):
    s = series.copy()
    result = s.copy()
    first_valid = s.first_valid_index()
    if first_valid is None:
        return pd.Series(np.nan, index=s.index)
    start = s.index.get_loc(first_valid)
    if start + period > len(s):
        return pd.Series(np.nan, index=s.index)
    result.iloc[:start] = np.nan
    result.iloc[start] = s.iloc[start:start + period].mean()
    for i in range(start + period, len(s)):
        result.iloc[i] = (result.iloc[i - 1] * (period - 1) + s.iloc[i]) / period
    return result

def williams_r(high, low, close, period=14):
    hh = high.rolling(window=period).max()
    ll = low.rolling(window=period).min()
    return -100 * (hh - close) / (hh - ll)

def download_data(symbol):
    import yfinance as yf
    for fmt in [f"{symbol}-USD", f"{symbol}USD", symbol]:
        try:
            ticker = yf.Ticker(fmt)
            df = ticker.history(period="3mo", interval="1h")
            if not df.empty and len(df) > 100:
                df = df.reset_index()
                df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df['symbol'] = symbol
                return df
        except:
            continue
    return None

def run_backtest(df, sl_pct, tp_pct, smma_p, wr_p, commission=0.001):
    close = df['close']
    high = df['high']
    low = df['low']
    
    df['s5'] = smma(close, smma_p)
    df['s5s'] = smma(close, smma_p).shift(smma_p)
    df['w'] = williams_r(high, low, close, wr_p)
    df['w8'] = smma(df['w'].copy(), 8)
    df['w21'] = smma(df['w'].copy(), 21)
    
    df['signal'] = 0
    warmup = max(22, smma_p * 2 + wr_p)
    
    for i in range(warmup, len(df)):
        s5 = df['s5'].iloc[i]; s5s = df['s5s'].iloc[i]
        w = df['w'].iloc[i]; w8 = df['w8'].iloc[i]; w21 = df['w21'].iloc[i]
        s5_prev = df['s5'].iloc[i-1]; s5s_prev = df['s5s'].iloc[i-1]
        w_prev = df['w'].iloc[i-1]; w8_prev = df['w8'].iloc[i-1]
        
        buy = (s5 > s5s and s5_prev <= s5s_prev and w > w8 and w_prev <= w8_prev and w > w21)
        sell = (s5 < s5s and s5_prev >= s5s_prev and w < w8 and w_prev >= w8_prev and w < w21)
        
        if buy: df.loc[df.index[i], 'signal'] = 1
        elif sell: df.loc[df.index[i], 'signal'] = -1
    
    capital = 10000; pos = 0; entry = 0; trades = []; eq = [10000]
    
    for i in range(1, len(df)):
        p = df['close'].iloc[i]; h = df['high'].iloc[i]; l = df['low'].iloc[i]; sig = df['signal'].iloc[i]
        
        if pos == 1:
            sl = entry * (1 - sl_pct); tp = entry * (1 + tp_pct)
            if l <= sl:
                pnl = ((sl - entry)/entry - commission*2) * capital; capital += pnl
                trades.append(pnl); pos = 0; eq.append(capital); continue
            elif h >= tp:
                pnl = ((tp - entry)/entry - commission*2) * capital; capital += pnl
                trades.append(pnl); pos = 0; eq.append(capital); continue
        elif pos == -1:
            sl = entry * (1 + sl_pct); tp = entry * (1 - tp_pct)
            if h >= sl:
                pnl = ((entry - sl)/entry - commission*2) * capital; capital += pnl
                trades.append(pnl); pos = 0; eq.append(capital); continue
            elif l <= tp:
                pnl = ((entry - tp)/entry - commission*2) * capital; capital += pnl
                trades.append(pnl); pos = 0; eq.append(capital); continue
        
        if sig != 0:
            if pos == 1 and sig == -1:
                pnl = ((p - entry)/entry - commission*2) * capital; capital += pnl
                trades.append(pnl); pos = 0
            elif pos == -1 and sig == 1:
                pnl = ((entry - p)/entry - commission*2) * capital; capital += pnl
                trades.append(pnl); pos = 0
            if pos == 0: pos = sig; entry = p
        eq.append(capital)
    
    if pos != 0:
        p = df['close'].iloc[-1]
        pnl = ((p - entry)/entry - commission*2) if pos == 1 else ((entry - p)/entry - commission*2)
        capital += pnl * capital; eq.append(capital)
    
    if len(trades) < 5: return None
    wins = [t for t in trades if t > 0]
    ret = (eq[-1] - 10000) / 100
    peak = eq[0]; mdd = 0
    for v in eq:
        if v > peak: peak = v
        dd = (peak - v) / peak * 100
        if dd > mdd: mdd = dd
    
    return {
        'trades': len(trades), 'wins': len(wins),
        'win_rate': len(wins)/len(trades)*100, 'return': ret,
        'max_dd': mdd,
        'avg_win': np.mean([t for t in trades if t > 0])*100 if wins else 0,
        'avg_loss': np.mean([t for t in trades if t <= 0])*100 if len(wins) < len(trades) else 0,
    }

def main():
    print("=" * 70)
    print("Moving M15 Optimization - DOGEUSD")
    print("=" * 70)
    
    df = download_data("DOGE")
    if df is None or df.empty:
        print("Failed to download!")
        return
    
    print(f"Data: {len(df)} bars, {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Price: {df['close'].min():.6f} - {df['close'].max():.6f}")
    
    # Reduced parameter ranges for speed
    sl_range = [0.01, 0.02, 0.03]
    tp_range = [0.02, 0.04, 0.06]
    smma_range = [3, 5, 7]
    wr_range = [10, 14]
    
    results = []
    total = 0
    
    for sl, tp, smma_p, wr_p in product(sl_range, tp_range, smma_range, wr_range):
        if tp <= sl: continue
        total += 1
        r = run_backtest(df.copy(), sl, tp, smma_p, wr_p)
        if r:
            r['sl'] = sl; r['tp'] = tp; r['smma'] = smma_p; r['wr'] = wr_p
            results.append(r)
    
    if not results:
        print("No results!")
        return
    
    results.sort(key=lambda x: x['return'], reverse=True)
    
    print(f"\nTested {total} combinations, {len(results)} valid")
    print("\n" + "=" * 70)
    print("TOP 10:")
    print("=" * 70)
    print(f"{'SL%':>6} {'TP%':>6} {'S':>3} {'WR':>3} {'#':>4} {'WR%':>5} {'Ret%':>7} {'MDD%':>6} {'W%':>5} {'L%':>5}")
    print("-" * 70)
    for r in results[:10]:
        print(f"{r['sl']*100:>6.1f} {r['tp']*100:>6.1f} {r['smma']:>3} {r['wr']:>3} "
              f"{r['trades']:>4} {r['win_rate']:>5.1f} {r['return']:>7.2f} "
              f"{r['max_dd']:>6.2f} {r['avg_win']:>5.2f} {r['avg_loss']:>5.2f}")
    
    best = results[0]
    print("\n" + "=" * 70)
    print("BEST: SL={}%, TP={}%, SMMA={}, WR={} | Trades={} WinRate={:.1f}% Return={:.2f}% MDD={:.2f}%".format(
        best['sl']*100, best['tp']*100, best['smma'], best['wr'],
        best['trades'], best['win_rate'], best['return'], best['max_dd']))
    print("=" * 70)
    
    pd.DataFrame(results).to_csv('tmp/moving_m15_opt_doge.csv', index=False)
    print("Saved to tmp/moving_m15_opt_doge.csv")

if __name__ == "__main__":
    main()
