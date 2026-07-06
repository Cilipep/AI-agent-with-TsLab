#!/usr/bin/env python3
"""
Detailed Backtest: Moving M15 Strategy - BTCUSD
Same parameters as DOGE optimization
"""

import pandas as pd
import numpy as np

# =================== PARAMETERS ===================
SYMBOL = "BTC"
INITIAL_CAPITAL = 10000
SL_PCT = 0.03       # 3%
TP_PCT = 0.06       # 6%
SMMA_PERIOD = 7
WR_PERIOD = 10
COMMISSION = 0.001

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
    for fmt in [f"{symbol}-USD", f"{symbol}USD"]:
        try:
            ticker = yf.Ticker(fmt)
            df = ticker.history(period="6mo", interval="1h")
            if not df.empty and len(df) > 100:
                df = df.reset_index()
                df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df['symbol'] = symbol
                return df
        except:
            continue
    return None

def main():
    print("=" * 70)
    print("DETAILED BACKTEST: Moving M15 Strategy - BTCUSD")
    print("=" * 70)
    print(f"\nParameters: SL={SL_PCT*100}% TP={TP_PCT*100}% SMMA={SMMA_PERIOD} WR={WR_PERIOD}")
    
    print(f"\nDownloading {SYMBOL} data...")
    df = download_data(SYMBOL)
    
    if df is None or df.empty:
        print("Failed to download!")
        return
    
    print(f"Data: {len(df)} bars, {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    
    # Indicators
    close = df['close']
    high = df['high']
    low = df['low']
    
    df['smma'] = smma(close, SMMA_PERIOD)
    df['smma_shifted'] = smma(close, SMMA_PERIOD).shift(SMMA_PERIOD)
    df['wr'] = williams_r(high, low, close, WR_PERIOD)
    df['wr8'] = smma(df['wr'].copy(), 8)
    df['wr21'] = smma(df['wr'].copy(), 21)
    
    # Signals
    df['signal'] = 0
    warmup = max(22, SMMA_PERIOD * 2 + WR_PERIOD)
    
    for i in range(warmup, len(df)):
        s5 = df['smma'].iloc[i]; s5s = df['smma_shifted'].iloc[i]
        w = df['wr'].iloc[i]; w8 = df['wr8'].iloc[i]; w21 = df['wr21'].iloc[i]
        s5_prev = df['smma'].iloc[i-1]; s5s_prev = df['smma_shifted'].iloc[i-1]
        w_prev = df['wr'].iloc[i-1]; w8_prev = df['wr8'].iloc[i-1]
        
        buy = (s5 > s5s and s5_prev <= s5s_prev and w > w8 and w_prev <= w8_prev and w > w21)
        sell = (s5 < s5s and s5_prev >= s5s_prev and w < w8 and w_prev >= w8_prev and w < w21)
        
        if buy: df.loc[df.index[i], 'signal'] = 1
        elif sell: df.loc[df.index[i], 'signal'] = -1
    
    signal_count = int(df['signal'].abs().sum())
    print(f"Signals: {signal_count}")
    
    if signal_count == 0:
        print("No signals!")
        return
    
    # Backtest
    capital = INITIAL_CAPITAL
    position = 0; entry_price = 0; entry_time = None
    trades = []; equity_curve = [INITIAL_CAPITAL]; equity_times = [df['timestamp'].iloc[0]]
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]; h = df['high'].iloc[i]; l = df['low'].iloc[i]
        signal = df['signal'].iloc[i]; ts = df['timestamp'].iloc[i]
        
        if position == 1:
            sl = entry_price * (1 - SL_PCT); tp = entry_price * (1 + TP_PCT)
            if l <= sl:
                pnl = ((sl - entry_price)/entry_price - COMMISSION*2)
                capital += pnl * capital
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'dir': 'LONG',
                             'entry': entry_price, 'exit': sl, 'pnl_pct': pnl*100, 'pnl_usd': pnl*capital, 'type': 'SL'})
                position = 0; equity_curve.append(capital); equity_times.append(ts); continue
            elif h >= tp:
                pnl = ((tp - entry_price)/entry_price - COMMISSION*2)
                capital += pnl * capital
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'dir': 'LONG',
                             'entry': entry_price, 'exit': tp, 'pnl_pct': pnl*100, 'pnl_usd': pnl*capital, 'type': 'TP'})
                position = 0; equity_curve.append(capital); equity_times.append(ts); continue
        elif position == -1:
            sl = entry_price * (1 + SL_PCT); tp = entry_price * (1 - TP_PCT)
            if h >= sl:
                pnl = ((entry_price - sl)/entry_price - COMMISSION*2)
                capital += pnl * capital
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'dir': 'SHORT',
                             'entry': entry_price, 'exit': sl, 'pnl_pct': pnl*100, 'pnl_usd': pnl*capital, 'type': 'SL'})
                position = 0; equity_curve.append(capital); equity_times.append(ts); continue
            elif l <= tp:
                pnl = ((entry_price - tp)/entry_price - COMMISSION*2)
                capital += pnl * capital
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'dir': 'SHORT',
                             'entry': entry_price, 'exit': tp, 'pnl_pct': pnl*100, 'pnl_usd': pnl*capital, 'type': 'TP'})
                position = 0; equity_curve.append(capital); equity_times.append(ts); continue
        
        if signal != 0:
            if position == 1 and signal == -1:
                pnl = ((price - entry_price)/entry_price - COMMISSION*2)
                capital += pnl * capital
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'dir': 'LONG',
                             'entry': entry_price, 'exit': price, 'pnl_pct': pnl*100, 'pnl_usd': pnl*capital, 'type': 'SIGNAL'})
                position = 0; equity_curve.append(capital); equity_times.append(ts)
            elif position == -1 and signal == 1:
                pnl = ((entry_price - price)/entry_price - COMMISSION*2)
                capital += pnl * capital
                trades.append({'entry_time': entry_time, 'exit_time': ts, 'dir': 'SHORT',
                             'entry': entry_price, 'exit': price, 'pnl_pct': pnl*100, 'pnl_usd': pnl*capital, 'type': 'SIGNAL'})
                position = 0; equity_curve.append(capital); equity_times.append(ts)
            if position == 0: position = signal; entry_price = price; entry_time = ts
        equity_curve.append(capital); equity_times.append(ts)
    
    if position != 0:
        price = df['close'].iloc[-1]
        pnl = ((price - entry_price)/entry_price - COMMISSION*2) if position == 1 else ((entry_price - price)/entry_price - COMMISSION*2)
        capital += pnl * capital
        trades.append({'entry_time': entry_time, 'exit_time': df['timestamp'].iloc[-1], 'dir': 'LONG' if position==1 else 'SHORT',
                      'entry': entry_price, 'exit': price, 'pnl_pct': pnl*100, 'pnl_usd': pnl*capital, 'type': 'END'})
        equity_curve.append(capital); equity_times.append(df['timestamp'].iloc[-1])
    
    # Metrics
    wins = [t for t in trades if t['pnl_usd'] > 0]
    losses = [t for t in trades if t['pnl_usd'] <= 0]
    total_return = (capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    
    gp = sum(t['pnl_usd'] for t in wins) if wins else 0
    gl = abs(sum(t['pnl_usd'] for t in losses)) if losses else 0
    pf = gp / gl if gl > 0 else float('inf')
    
    peak = equity_curve[0]; mdd = 0
    for v in equity_curve:
        if v > peak: peak = v
        dd = (peak - v) / peak * 100
        if dd > mdd: mdd = dd
    
    returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] for i in range(1, len(equity_curve))]
    sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252 * 24) if returns and np.std(returns) > 0 else 0
    
    holding = []
    for t in trades:
        if t['entry_time'] and t['exit_time']:
            holding.append((t['exit_time'] - t['entry_time']).total_seconds() / 3600)
    avg_hold = np.mean(holding) if holding else 0
    
    # Print
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Symbol:              BTCUSD")
    print(f"Period:              {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Initial Capital:     ${INITIAL_CAPITAL:,.2f}")
    print(f"Final Capital:       ${capital:,.2f}")
    print("-" * 70)
    print(f"Total Trades:        {len(trades)}")
    print(f"Wins/Losses:         {len(wins)}/{len(losses)}")
    print(f"Win Rate:            {len(wins)/len(trades)*100:.1f}%")
    print(f"Total Return:        {total_return:.2f}%")
    print(f"Profit Factor:       {pf:.2f}")
    print(f"Max Drawdown:        {mdd:.2f}%")
    print(f"Sharpe Ratio:        {sharpe:.2f}")
    print("-" * 70)
    print(f"Avg PnL/Trade:       {np.mean([t['pnl_pct'] for t in trades]):.3f}%")
    print(f"Avg Win:             {np.mean([t['pnl_pct'] for t in wins]):.3f}%" if wins else "")
    print(f"Avg Loss:            {np.mean([t['pnl_pct'] for t in losses]):.3f}%" if losses else "")
    print(f"SL Hits:             {len([t for t in trades if t['type']=='SL'])}")
    print(f"TP Hits:             {len([t for t in trades if t['type']=='TP'])}")
    print(f"Signal Exits:        {len([t for t in trades if t['type']=='SIGNAL'])}")
    print(f"Avg Holding:         {avg_hold:.1f} hours")
    print("=" * 70)
    
    print(f"\nALL TRADES:")
    print("-" * 100)
    print(f"{'Time':<22} {'Dir':<7} {'Type':<7} {'Entry':>12} {'Exit':>12} {'PnL%':>8} {'PnL$':>10}")
    print("-" * 100)
    for t in trades:
        s = "+" if t['pnl_pct'] > 0 else ""
        print(f"{str(t['entry_time'])[:19]:<22} {t['dir']:<7} {t['type']:<7} "
              f"${t['entry']:,.2f} ${t['exit']:,.2f} {s}{t['pnl_pct']:.3f}% {s}${t['pnl_usd']:,.2f}")
    
    print("\n" + "=" * 70)
    print("MONTHLY BREAKDOWN:")
    print("=" * 70)
    tdf = pd.DataFrame(trades)
    tdf['month'] = pd.to_datetime(tdf['entry_time']).dt.to_period('M')
    for m, g in tdf.groupby('month'):
        w = len(g[g['pnl_usd']>0]); t = len(g)
        r = g['pnl_usd'].sum() / INITIAL_CAPITAL * 100
        print(f"{m}: {t} trades, {w} wins ({w/t*100:.0f}%), Return: {r:.2f}%")

if __name__ == "__main__":
    main()
