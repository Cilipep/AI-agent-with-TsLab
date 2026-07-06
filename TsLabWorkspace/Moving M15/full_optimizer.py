#!/usr/bin/env python3
"""
Moving M15 Strategy - Comprehensive Optimizer
Tests Williams %R strategy across multiple instruments and timeframes
"""

import pandas as pd
import numpy as np
from itertools import product
import warnings
warnings.filterwarnings('ignore')

# =================== INDICATORS ===================
def smma(series, period):
    s = series.copy(); result = s.copy()
    fv = s.first_valid_index()
    if fv is None: return pd.Series(np.nan, index=s.index)
    start = s.index.get_loc(fv)
    if start + period > len(s): return pd.Series(np.nan, index=s.index)
    result.iloc[:start] = np.nan
    result.iloc[start] = s.iloc[start:start + period].mean()
    for i in range(start + period, len(s)):
        result.iloc[i] = (result.iloc[i - 1] * (period - 1) + s.iloc[i]) / period
    return result

def williams_r(high, low, close, period=14):
    hh = high.rolling(window=period).max()
    ll = low.rolling(window=period).min()
    return -100 * (hh - close) / (hh - ll)

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

# =================== DATA DOWNLOAD ===================
def download_data(symbol, interval='1h', period='6mo'):
    import yfinance as yf
    for fmt in [f"{symbol}-USD", f"{symbol}USD"]:
        try:
            t = yf.Ticker(fmt)
            d = t.history(period=period, interval=interval)
            if not d.empty and len(d) > 100:
                d = d.reset_index()
                d.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                d['symbol'] = symbol
                return d
        except: pass
    return None

def resample(df, rule):
    d = df.copy()
    d['timestamp'] = pd.to_datetime(d['timestamp'])
    d.set_index('timestamp', inplace=True)
    d = d.resample(rule).agg({'o': 'first', 'h': 'max', 'l': 'min', 'c': 'last', 'v': 'sum'}).dropna()
    return d.reset_index()

# =================== BACKTEST ENGINE ===================
def run_backtest(df, sl, tp, smma_p, wr_p, ema_p=None, commission=0.001):
    """Run backtest with optional EMA filter"""
    c = df['c']; h = df['h']; l = df['l']
    
    # Calculate indicators
    df['s5'] = smma(c, smma_p)
    df['s5s'] = smma(c, smma_p).shift(smma_p)
    df['w'] = williams_r(h, l, c, wr_p)
    df['w8'] = smma(df['w'].copy(), 8)
    df['w21'] = smma(df['w'].copy(), 21)
    
    if ema_p:
        df['ema'] = ema(c, ema_p)
    
    # Generate signals
    df['sig'] = 0
    warmup = max(22, smma_p * 2 + wr_p)
    if ema_p: warmup = max(warmup, ema_p)
    
    for i in range(warmup, len(df)):
        s5 = df['s5'].iloc[i]; s5s = df['s5s'].iloc[i]
        w = df['w'].iloc[i]; w8 = df['w8'].iloc[i]; w21 = df['w21'].iloc[i]
        s5p = df['s5'].iloc[i-1]; s5sp = df['s5s'].iloc[i-1]
        wp = df['w'].iloc[i-1]; w8p = df['w8'].iloc[i-1]
        
        # Buy: SMMA cross up + WR filter
        buy_ma = s5 > s5s and s5p <= s5sp
        buy_wr = w > w21
        
        # Sell: SMMA cross down + WR filter
        sell_ma = s5 < s5s and s5p >= s5sp
        sell_wr = w < w21
        
        # EMA filter (optional)
        if ema_p:
            ema_val = df['ema'].iloc[i]
            if buy_ma and buy_wr and c.iloc[i] > ema_val:
                df.loc[df.index[i], 'sig'] = 1
            elif sell_ma and sell_wr and c.iloc[i] < ema_val:
                df.loc[df.index[i], 'sig'] = -1
        else:
            if buy_ma and buy_wr:
                df.loc[df.index[i], 'sig'] = 1
            elif sell_ma and sell_wr:
                df.loc[df.index[i], 'sig'] = -1
    
    # Run trades
    cap = 10000; pos = 0; ent = 0; trades = []; eq = [10000]
    
    for i in range(1, len(df)):
        p = df['c'].iloc[i]; hi = df['h'].iloc[i]; lo = df['l'].iloc[i]; sg = df['sig'].iloc[i]
        
        # Check SL/TP
        if pos == 1:
            sl_p = ent * (1 - sl); tp_p = ent * (1 + tp)
            if lo <= sl_p:
                pnl = ((sl_p - ent) / ent - commission * 2)
                cap += pnl * cap; trades.append(pnl * 100); pos = 0; eq.append(cap); continue
            elif hi >= tp_p:
                pnl = ((tp_p - ent) / ent - commission * 2)
                cap += pnl * cap; trades.append(pnl * 100); pos = 0; eq.append(cap); continue
        elif pos == -1:
            sl_p = ent * (1 + sl); tp_p = ent * (1 - tp)
            if hi >= sl_p:
                pnl = ((ent - sl_p) / ent - commission * 2)
                cap += pnl * cap; trades.append(pnl * 100); pos = 0; eq.append(cap); continue
            elif lo <= tp_p:
                pnl = ((ent - tp_p) / ent - commission * 2)
                cap += pnl * cap; trades.append(pnl * 100); pos = 0; eq.append(cap); continue
        
        # Signal entries
        if sg != 0:
            if pos == 1 and sg == -1:
                pnl = ((p - ent) / ent - commission * 2)
                cap += pnl * cap; trades.append(pnl * 100); pos = 0
            elif pos == -1 and sg == 1:
                pnl = ((ent - p) / ent - commission * 2)
                cap += pnl * cap; trades.append(pnl * 100); pos = 0
            if pos == 0: pos = sg; ent = p
        eq.append(cap)
    
    # Close remaining
    if pos != 0:
        p = df['c'].iloc[-1]
        pnl = ((p - ent) / ent - commission * 2) if pos == 1 else ((ent - p) / ent - commission * 2)
        cap += pnl * cap; trades.append(pnl * 100); eq.append(cap)
    
    if len(trades) < 3: return None
    
    wins = [t for t in trades if t > 0]; losses = [t for t in trades if t <= 0]
    ret = (cap - 10000) / 100
    peak = eq[0]; mdd = 0
    for v in eq:
        if v > peak: peak = v
        dd = (peak - v) / peak * 100
        if dd > mdd: mdd = dd
    
    return {
        'trades': len(trades), 'wins': len(wins),
        'wr': len(wins) / len(trades) * 100, 'ret': ret,
        'mdd': mdd, 'final': cap,
        'aw': np.mean([t for t in trades if t > 0]) if wins else 0,
        'al': np.mean([t for t in trades if t <= 0]) if losses else 0
    }

# =================== OPTIMIZATION ===================
def optimize_instrument(df, sl_range, tp_range, smma_range, wr_range, ema_range=[None]):
    """Find best parameters for one instrument"""
    best = None
    for sl, tp, sp, wp, ep in product(sl_range, tp_range, smma_range, wr_range, ema_range):
        if tp <= sl: continue
        r = run_backtest(df.copy(), sl, tp, sp, wp, ep)
        if r and (best is None or r['ret'] > best['ret']):
            best = r
            best['sl'] = sl; best['tp'] = tp; best['smma'] = sp; best['wr'] = wp; best['ema'] = ep
    return best

# =================== MAIN ===================
def main():
    print("=" * 80)
    print("MOVING M15 STRATEGY - MULTI-INSTRUMENT OPTIMIZER")
    print("=" * 80)
    
    # Configuration
    instruments = ['SOL', 'DOGE', 'LINK', 'ETH', 'FET', 'BTC']
    intervals = ['1h', '15m']
    
    all_results = []
    
    for interval in intervals:
        print(f"\n{'='*80}")
        print(f"TIMEFRAME: {interval.upper()}")
        print(f"{'='*80}")
        
        for sym in instruments:
            print(f"{sym}...", end=" ", flush=True)
            df = download_data(sym, interval=interval, period='6mo')
            if df is None or df.empty:
                print("SKIP"); continue
            
            print(f"{len(df)} bars", end=" ")
            
            # Optimize with EMA filter
            best = optimize_instrument(
                df,
                sl_range=[0.01, 0.02, 0.03],
                tp_range=[0.03, 0.05, 0.08],
                smma_range=[3, 5, 7],
                wr_range=[8, 10, 14],
                ema_range=[100, 200]
            )
            
            if best is None:
                print("no trades"); continue
            
            best['sym'] = sym; best['tf'] = interval
            all_results.append(best)
            
            print(f"Ret={best['ret']:+.2f}% WR={best['wr']:.0f}% MDD={best['mdd']:.1f}%")
    
    if not all_results:
        print("\nNo valid results!"); return
    
    # Sort and display
    all_results.sort(key=lambda x: x['ret'], reverse=True)
    
    print("\n" + "=" * 80)
    print("ALL RESULTS (sorted by return)")
    print("=" * 80)
    print(f"{'Sym':<7} {'TF':<4} {'SL%':>4} {'TP%':>4} {'S':>2} {'WR':>2} {'EMA':>4} {'#':>4} {'WR%':>5} {'Ret%':>7} {'MDD%':>6}")
    print("-" * 80)
    
    for r in all_results:
        s = "+" if r['ret'] > 0 else ""
        ema_str = str(r['ema']) if r['ema'] else "None"
        print(f"{r['sym']:<7} {r['tf']:<4} {r['sl']*100:>4.1f} {r['tp']*100:>4.1f} {r['smma']:>2} {r['wr']:>2} {ema_str:>4} "
              f"{r['trades']:>4} {r['wr']:>5.1f} {s}{r['ret']:>6.2f} {r['mdd']:>6.1f}")
    
    # Summary
    profitable = [r for r in all_results if r['ret'] > 0]
    print("-" * 80)
    print(f"Profitable: {len(profitable)}/{len(all_results)} ({len(profitable)/len(all_results)*100:.0f}%)")
    print(f"Best: {all_results[0]['sym']} {all_results[0]['tf']} ({all_results[0]['ret']:+.2f}%)")
    print(f"Worst: {all_results[-1]['sym']} {all_results[-1]['tf']} ({all_results[-1]['ret']:+.2f}%)")
    print(f"Avg Return: {np.mean([r['ret'] for r in all_results]):.2f}%")
    
    # Save results
    pd.DataFrame(all_results).to_csv('tmp/moving_m15_full_optimization.csv', index=False)
    print("\nSaved to tmp/moving_m15_full_optimization.csv")

if __name__ == "__main__":
    main()
