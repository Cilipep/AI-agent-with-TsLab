#!/usr/bin/env python3
"""
Optimization: Moving M15 Strategy for DOGEUSDT
Tests multiple parameter combinations to find best settings
"""

import pandas as pd
import numpy as np
from itertools import product

# =================== INDICATORS ===================
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

# =================== DATA DOWNLOAD ===================
def download_data(symbol):
    import yfinance as yf
    ticker = yf.Ticker(f"{symbol}=X")
    df = ticker.history(period="60d", interval="15m")
    if df.empty:
        return None
    df = df.reset_index()
    df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df['symbol'] = symbol
    return df

def download_crypto(symbol):
    """Download crypto data from yfinance"""
    import yfinance as yf
    # Try different formats for crypto
    for fmt in [f"{symbol}-USD", f"{symbol}USD", symbol]:
        try:
            ticker = yf.Ticker(fmt)
            df = ticker.history(period="60d", interval="15m")
            if not df.empty and len(df) > 100:
                df = df.reset_index()
                df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df['symbol'] = symbol
                return df
        except:
            continue
    return None

# =================== BACKTEST ENGINE ===================
def run_backtest(df, sl_pct, tp_pct, smma_period, wr_period, initial_capital=10000):
    commission = 0.001  # 0.1% for crypto (higher than forex)
    
    # Calculate indicators
    close = df['close']
    high = df['high']
    low = df['low']
    
    df['smma5'] = smma(close, smma_period)
    df['smma5_shifted'] = smma(close, smma_period).shift(smma_period)
    df['wr'] = williams_r(high, low, close, wr_period)
    df['wr8'] = smma(df['wr'].copy(), 8)
    df['wr21'] = smma(df['wr'].copy(), 21)
    
    # Generate signals
    df['signal'] = 0
    warmup = max(22, smma_period * 2 + wr_period)
    
    for i in range(warmup, len(df)):
        s5 = df['smma5'].iloc[i]
        s5s = df['smma5_shifted'].iloc[i]
        w = df['wr'].iloc[i]
        w8 = df['wr8'].iloc[i]
        w21 = df['wr21'].iloc[i]
        
        s5_prev = df['smma5'].iloc[i-1]
        s5s_prev = df['smma5_shifted'].iloc[i-1]
        w_prev = df['wr'].iloc[i-1]
        w8_prev = df['wr8'].iloc[i-1]
        
        # BUY
        buy_ma = s5 > s5s and s5_prev <= s5s_prev
        buy_wr = w > w8 and w_prev <= w8_prev
        buy_filter = w > w21
        
        # SELL
        sell_ma = s5 < s5s and s5_prev >= s5s_prev
        sell_wr = w < w8 and w_prev >= w8_prev
        sell_filter = w < w21
        
        if buy_ma and buy_wr and buy_filter:
            df.loc[df.index[i], 'signal'] = 1
        elif sell_ma and sell_wr and sell_filter:
            df.loc[df.index[i], 'signal'] = -1
    
    # Run trades
    capital = initial_capital
    position = 0
    entry_price = 0
    trades = []
    equity = [initial_capital]
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        h = df['high'].iloc[i]
        l = df['low'].iloc[i]
        sig = df['signal'].iloc[i]
        
        # Check SL/TP
        if position == 1:
            sl = entry_price * (1 - sl_pct)
            tp = entry_price * (1 + tp_pct)
            if l <= sl:
                pnl = ((sl - entry_price) / entry_price - commission * 2) * capital
                capital += pnl
                trades.append(pnl_pct(sl, entry_price, commission))
                position = 0
                equity.append(capital)
                continue
            elif h >= tp:
                pnl = ((tp - entry_price) / entry_price - commission * 2) * capital
                capital += pnl
                trades.append(pnl_pct(tp, entry_price, commission))
                position = 0
                equity.append(capital)
                continue
        elif position == -1:
            sl = entry_price * (1 + sl_pct)
            tp = entry_price * (1 - tp_pct)
            if h >= sl:
                pnl = ((entry_price - sl) / entry_price - commission * 2) * capital
                capital += pnl
                trades.append(pnl_pct(entry_price, sl, commission))
                position = 0
                equity.append(capital)
                continue
            elif l <= tp:
                pnl = ((entry_price - tp) / entry_price - commission * 2) * capital
                capital += pnl
                trades.append(pnl_pct(entry_price, tp, commission))
                position = 0
                equity.append(capital)
                continue
        
        # Signal
        if sig != 0:
            if position == 1 and sig == -1:
                pnl = ((price - entry_price) / entry_price - commission * 2) * capital
                capital += pnl
                trades.append(pnl_pct(price, entry_price, commission))
                position = 0
            elif position == -1 and sig == 1:
                pnl = ((entry_price - price) / entry_price - commission * 2) * capital
                capital += pnl
                trades.append(pnl_pct(entry_price, price, commission))
                position = 0
            
            if position == 0:
                position = sig
                entry_price = price
        
        equity.append(capital)
    
    # Close remaining
    if position != 0:
        price = df['close'].iloc[-1]
        if position == 1:
            pnl = ((price - entry_price) / entry_price - commission * 2)
        else:
            pnl = ((entry_price - price) / entry_price - commission * 2)
        capital += pnl * capital
        equity.append(capital)
    
    if not trades:
        return None
    
    wins = [t for t in trades if t > 0]
    total_return = (equity[-1] - initial_capital) / initial_capital * 100
    
    peak = equity[0]
    max_dd = 0
    for val in equity:
        if val > peak: peak = val
        dd = (peak - val) / peak * 100
        if dd > max_dd: max_dd = dd
    
    return {
        'trades': len(trades),
        'wins': len(wins),
        'win_rate': len(wins) / len(trades) * 100,
        'return': total_return,
        'max_dd': max_dd,
        'avg_win': np.mean([t for t in trades if t > 0]) * 100 if wins else 0,
        'avg_loss': np.mean([t for t in trades if t <= 0]) * 100 if len(wins) < len(trades) else 0,
    }

def pnl_pct(exit_price, entry_price, commission):
    return ((exit_price - entry_price) / entry_price - commission * 2) * 100

# =================== MAIN ===================
def main():
    print("=" * 70)
    print("Moving M15 Strategy Optimization - DOGEUSDT")
    print("=" * 70)
    
    # Download DOGE data
    print("\nDownloading DOGE data...")
    df = download_crypto("DOGE")
    
    if df is None or df.empty:
        # Try as forex pair
        df = download_data("DOGEUSDT")
    
    if df is None or df.empty:
        print("Failed to download DOGE data!")
        print("Trying alternative sources...")
        # Try with different interval
        import yfinance as yf
        for fmt in ["DOGE-USD", "DOGEUSD"]:
            try:
                ticker = yf.Ticker(fmt)
                df = ticker.history(period="3mo", interval="1h")
                if not df.empty and len(df) > 100:
                    df = df.reset_index()
                    df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
                    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    df['symbol'] = 'DOGE'
                    print(f"Downloaded {len(df)} H1 bars for DOGE")
                    break
            except:
                continue
    
    if df is None or df.empty:
        print("ERROR: Could not download DOGE data")
        return
    
    print(f"Data: {len(df)} bars, {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Price range: {df['close'].min():.6f} - {df['close'].max():.6f}")
    
    # Parameter ranges to optimize
    sl_range = [0.01, 0.015, 0.02, 0.025, 0.03]      # 1%, 1.5%, 2%, 2.5%, 3%
    tp_range = [0.02, 0.03, 0.04, 0.05, 0.06]         # 2%, 3%, 4%, 5%, 6%
    smma_range = [3, 5, 7, 10]                          # SMMA periods
    wr_range = [10, 14, 20]                             # Williams %R periods
    
    results = []
    total = len(sl_range) * len(tp_range) * len(smma_range) * len(wr_range)
    
    print(f"\nOptimizing {total} parameter combinations...")
    print("-" * 70)
    
    count = 0
    for sl, tp, smma_p, wr_p in product(sl_range, tp_range, smma_range, wr_range):
        if tp <= sl:  # TP must be > SL
            continue
        
        count += 1
        result = run_backtest(df.copy(), sl, tp, smma_p, wr_p)
        
        if result and result['trades'] >= 5:  # Minimum 5 trades
            result['sl'] = sl
            result['tp'] = tp
            result['smma'] = smma_p
            result['wr'] = wr_p
            results.append(result)
        
        if count % 50 == 0:
            print(f"  Progress: {count}/{total} combinations tested...")
    
    if not results:
        print("No valid results found!")
        return
    
    # Sort by return
    results.sort(key=lambda x: x['return'], reverse=True)
    
    # Print top 10
    print("\n" + "=" * 70)
    print("TOP 10 PARAMETER COMBINATIONS")
    print("=" * 70)
    print(f"{'SL%':>6} {'TP%':>6} {'SMMA':>6} {'WR':>4} {'Trades':>7} {'WinR%':>6} {'Return%':>8} {'MaxDD%':>7} {'AvgW%':>6} {'AvgL%':>6}")
    print("-" * 70)
    
    for r in results[:10]:
        print(f"{r['sl']*100:>6.1f} {r['tp']*100:>6.1f} {r['smma']:>6} {r['wr']:>4} "
              f"{r['trades']:>7} {r['win_rate']:>6.1f} {r['return']:>8.2f} "
              f"{r['max_dd']:>7.2f} {r['avg_win']:>6.2f} {r['avg_loss']:>6.2f}")
    
    # Print bottom 5
    print("\nWORST 5:")
    print("-" * 70)
    for r in results[-5:]:
        print(f"{r['sl']*100:>6.1f} {r['tp']*100:>6.1f} {r['smma']:>6} {r['wr']:>4} "
              f"{r['trades']:>7} {r['win_rate']:>6.1f} {r['return']:>8.2f} "
              f"{r['max_dd']:>7.2f} {r['avg_win']:>6.2f} {r['avg_loss']:>6.2f}")
    
    # Best params detail
    best = results[0]
    print("\n" + "=" * 70)
    print("BEST PARAMETERS")
    print("=" * 70)
    print(f"Stop Loss:    {best['sl']*100:.1f}%")
    print(f"Take Profit:  {best['tp']*100:.1f}%")
    print(f"SMMA Period:  {best['smma']}")
    print(f"WR Period:    {best['wr']}")
    print(f"Trades:       {best['trades']}")
    print(f"Win Rate:     {best['win_rate']:.1f}%")
    print(f"Total Return: {best['return']:.2f}%")
    print(f"Max Drawdown: {best['max_dd']:.2f}%")
    print(f"Avg Win:      {best['avg_win']:.2f}%")
    print(f"Avg Loss:     {best['avg_loss']:.2f}%")
    print("=" * 70)
    
    # Save results
    pd.DataFrame(results).to_csv('tmp/moving_m15_optimization.csv', index=False)
    print(f"\nResults saved to tmp/moving_m15_optimization.csv")

if __name__ == "__main__":
    main()
