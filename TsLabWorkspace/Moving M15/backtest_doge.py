#!/usr/bin/env python3
"""
Detailed Backtest: Moving M15 Strategy - DOGEUSD
Best parameters from optimization
"""

import pandas as pd
import numpy as np

# =================== PARAMETERS ===================
SYMBOL = "DOGE"
INITIAL_CAPITAL = 10000
SL_PCT = 0.03       # 3%
TP_PCT = 0.06       # 6%
SMMA_PERIOD = 7
WR_PERIOD = 10
COMMISSION = 0.001  # 0.1% for crypto

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

# =================== MAIN ===================
def main():
    print("=" * 70)
    print("DETAILED BACKTEST: Moving M15 Strategy - DOGEUSD")
    print("=" * 70)
    print(f"\nParameters:")
    print(f"  Stop Loss:       {SL_PCT*100}%")
    print(f"  Take Profit:     {TP_PCT*100}%")
    print(f"  SMMA Period:     {SMMA_PERIOD}")
    print(f"  Williams %R:     {WR_PERIOD}")
    print(f"  Commission:      {COMMISSION*100}%")
    print(f"  Initial Capital: ${INITIAL_CAPITAL:,}")
    
    # Download data
    print(f"\nDownloading {SYMBOL} data...")
    df = download_data(SYMBOL)
    
    if df is None or df.empty:
        print("Failed to download!")
        return
    
    print(f"\nData: {len(df)} bars")
    print(f"Period: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Price range: ${df['close'].min():.6f} - ${df['close'].max():.6f}")
    
    # Calculate indicators
    print("\nCalculating indicators...")
    close = df['close']
    high = df['high']
    low = df['low']
    
    df['smma'] = smma(close, SMMA_PERIOD)
    df['smma_shifted'] = smma(close, SMMA_PERIOD).shift(SMMA_PERIOD)
    df['wr'] = williams_r(high, low, close, WR_PERIOD)
    df['wr8'] = smma(df['wr'].copy(), 8)
    df['wr21'] = smma(df['wr'].copy(), 21)
    
    # Generate signals
    df['signal'] = 0
    warmup = max(22, SMMA_PERIOD * 2 + WR_PERIOD)
    
    for i in range(warmup, len(df)):
        s5 = df['smma'].iloc[i]
        s5s = df['smma_shifted'].iloc[i]
        w = df['wr'].iloc[i]
        w8 = df['wr8'].iloc[i]
        w21 = df['wr21'].iloc[i]
        
        s5_prev = df['smma'].iloc[i-1]
        s5s_prev = df['smma_shifted'].iloc[i-1]
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
    
    signal_count = int(df['signal'].abs().sum())
    print(f"Generated signals: {signal_count}")
    
    if signal_count == 0:
        print("No signals!")
        return
    
    # Run backtest
    print("\nRunning backtest...")
    capital = INITIAL_CAPITAL
    position = 0
    entry_price = 0
    entry_time = None
    trades = []
    equity_curve = [INITIAL_CAPITAL]
    equity_times = [df['timestamp'].iloc[0]]
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        high_val = df['high'].iloc[i]
        low_val = df['low'].iloc[i]
        signal = df['signal'].iloc[i]
        ts = df['timestamp'].iloc[i]
        
        # Check SL/TP
        if position == 1:
            sl = entry_price * (1 - SL_PCT)
            tp = entry_price * (1 + TP_PCT)
            
            if low_val <= sl:
                pnl_pct = ((sl - entry_price) / entry_price - COMMISSION * 2) * 100
                pnl_usd = ((sl - entry_price) / entry_price - COMMISSION * 2) * capital
                capital += pnl_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': ts,
                    'direction': 'LONG', 'entry': entry_price, 'exit': sl,
                    'pnl_pct': pnl_pct, 'pnl_usd': pnl_usd, 'exit_type': 'SL'
                })
                position = 0
                equity_curve.append(capital)
                equity_times.append(ts)
                continue
            elif high_val >= tp:
                pnl_pct = ((tp - entry_price) / entry_price - COMMISSION * 2) * 100
                pnl_usd = ((tp - entry_price) / entry_price - COMMISSION * 2) * capital
                capital += pnl_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': ts,
                    'direction': 'LONG', 'entry': entry_price, 'exit': tp,
                    'pnl_pct': pnl_pct, 'pnl_usd': pnl_usd, 'exit_type': 'TP'
                })
                position = 0
                equity_curve.append(capital)
                equity_times.append(ts)
                continue
        
        elif position == -1:
            sl = entry_price * (1 + SL_PCT)
            tp = entry_price * (1 - TP_PCT)
            
            if high_val >= sl:
                pnl_pct = ((entry_price - sl) / entry_price - COMMISSION * 2) * 100
                pnl_usd = ((entry_price - sl) / entry_price - COMMISSION * 2) * capital
                capital += pnl_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': ts,
                    'direction': 'SHORT', 'entry': entry_price, 'exit': sl,
                    'pnl_pct': pnl_pct, 'pnl_usd': pnl_usd, 'exit_type': 'SL'
                })
                position = 0
                equity_curve.append(capital)
                equity_times.append(ts)
                continue
            elif low_val <= tp:
                pnl_pct = ((entry_price - tp) / entry_price - COMMISSION * 2) * 100
                pnl_usd = ((entry_price - tp) / entry_price - COMMISSION * 2) * capital
                capital += pnl_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': ts,
                    'direction': 'SHORT', 'entry': entry_price, 'exit': tp,
                    'pnl_pct': pnl_pct, 'pnl_usd': pnl_usd, 'exit_type': 'TP'
                })
                position = 0
                equity_curve.append(capital)
                equity_times.append(ts)
                continue
        
        # Process new signals
        if signal != 0:
            # Close opposite position
            if position == 1 and signal == -1:
                pnl_pct = ((price - entry_price) / entry_price - COMMISSION * 2) * 100
                pnl_usd = ((price - entry_price) / entry_price - COMMISSION * 2) * capital
                capital += pnl_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': ts,
                    'direction': 'LONG', 'entry': entry_price, 'exit': price,
                    'pnl_pct': pnl_pct, 'pnl_usd': pnl_usd, 'exit_type': 'SIGNAL'
                })
                position = 0
                equity_curve.append(capital)
                equity_times.append(ts)
            elif position == -1 and signal == 1:
                pnl_pct = ((entry_price - price) / entry_price - COMMISSION * 2) * 100
                pnl_usd = ((entry_price - price) / entry_price - COMMISSION * 2) * capital
                capital += pnl_usd
                trades.append({
                    'entry_time': entry_time, 'exit_time': ts,
                    'direction': 'SHORT', 'entry': entry_price, 'exit': price,
                    'pnl_pct': pnl_pct, 'pnl_usd': pnl_usd, 'exit_type': 'SIGNAL'
                })
                position = 0
                equity_curve.append(capital)
                equity_times.append(ts)
            
            # Open new position
            if position == 0:
                position = signal
                entry_price = price
                entry_time = ts
        
        equity_curve.append(capital)
        equity_times.append(ts)
    
    # Close remaining position
    if position != 0:
        price = df['close'].iloc[-1]
        if position == 1:
            pnl_pct = ((price - entry_price) / entry_price - COMMISSION * 2) * 100
            pnl_usd = ((price - entry_price) / entry_price - COMMISSION * 2) * capital
        else:
            pnl_pct = ((entry_price - price) / entry_price - COMMISSION * 2) * 100
            pnl_usd = ((entry_price - price) / entry_price - COMMISSION * 2) * capital
        capital += pnl_usd
        trades.append({
            'entry_time': entry_time, 'exit_time': df['timestamp'].iloc[-1],
            'direction': 'LONG' if position == 1 else 'SHORT',
            'entry': entry_price, 'exit': price,
            'pnl_pct': pnl_pct, 'pnl_usd': pnl_usd, 'exit_type': 'END'
        })
        equity_curve.append(capital)
        equity_times.append(df['timestamp'].iloc[-1])
    
    # Calculate metrics
    wins = [t for t in trades if t['pnl_usd'] > 0]
    losses = [t for t in trades if t['pnl_usd'] <= 0]
    
    total_return = (capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    
    gross_profit = sum(t['pnl_usd'] for t in wins) if wins else 0
    gross_loss = abs(sum(t['pnl_usd'] for t in losses)) if losses else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    peak = equity_curve[0]
    max_dd = 0
    max_dd_idx = 0
    for idx, val in enumerate(equity_curve):
        if val > peak:
            peak = val
        dd = (peak - val) / peak * 100
        if dd > max_dd:
            max_dd = dd
            max_dd_idx = idx
    
    # Sharpe ratio
    returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] 
               for i in range(1, len(equity_curve))]
    sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252 * 24) if returns and np.std(returns) > 0 else 0
    
    # Average holding time
    holding_times = []
    for t in trades:
        if t['entry_time'] and t['exit_time']:
            delta = t['exit_time'] - t['entry_time']
            holding_times.append(delta.total_seconds() / 3600)  # hours
    avg_holding = np.mean(holding_times) if holding_times else 0
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Symbol:              {SYMBOL}")
    print(f"Period:              {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Initial Capital:     ${INITIAL_CAPITAL:,.2f}")
    print(f"Final Capital:       ${capital:,.2f}")
    print("-" * 70)
    print(f"Total Trades:        {len(trades)}")
    print(f"Wins/Losses:         {len(wins)}/{len(losses)}")
    print(f"Win Rate:            {len(wins)/len(trades)*100:.1f}%")
    print(f"Total Return:        {total_return:.2f}%")
    print(f"Profit Factor:       {profit_factor:.2f}")
    print(f"Max Drawdown:        {max_dd:.2f}%")
    print(f"Sharpe Ratio:        {sharpe:.2f}")
    print("-" * 70)
    print(f"Avg PnL/Trade:       {np.mean([t['pnl_pct'] for t in trades]):.3f}%")
    print(f"Avg Win:             {np.mean([t['pnl_pct'] for t in wins]):.3f}%")
    print(f"Avg Loss:            {np.mean([t['pnl_pct'] for t in losses]):.3f}%")
    print(f"SL Hits:             {len([t for t in trades if t['exit_type'] == 'SL'])}")
    print(f"TP Hits:             {len([t for t in trades if t['exit_type'] == 'TP'])}")
    print(f"Signal Exits:        {len([t for t in trades if t['exit_type'] == 'SIGNAL'])}")
    print(f"Avg Holding Time:    {avg_holding:.1f} hours")
    print("=" * 70)
    
    # Print all trades
    print(f"\nALL TRADES:")
    print("-" * 100)
    print(f"{'Entry Time':<22} {'Dir':<6} {'Type':<7} {'Entry':>12} {'Exit':>12} {'PnL%':>8} {'PnL$':>10}")
    print("-" * 100)
    
    for t in trades:
        sign = "+" if t['pnl_pct'] > 0 else ""
        print(f"{str(t['entry_time'])[:19]:<22} {t['direction']:<6} {t['exit_type']:<7} "
              f"${t['entry']:.6f} ${t['exit']:.6f} {sign}{t['pnl_pct']:.3f}% {sign}${t['pnl_usd']:.2f}")
    
    # Monthly breakdown
    print("\n" + "=" * 70)
    print("MONTHLY BREAKDOWN:")
    print("=" * 70)
    
    trades_df = pd.DataFrame(trades)
    trades_df['month'] = pd.to_datetime(trades_df['entry_time']).dt.to_period('M')
    
    for month, group in trades_df.groupby('month'):
        m_wins = len(group[group['pnl_usd'] > 0])
        m_total = len(group)
        m_return = group['pnl_usd'].sum()
        m_return_pct = m_return / INITIAL_CAPITAL * 100
        print(f"{month}: {m_total} trades, {m_wins} wins ({m_wins/m_total*100:.0f}%), Return: {m_return_pct:.2f}%")
    
    # Save results
    trades_df.to_csv('tmp/moving_m15_doge_trades.csv', index=False)
    print(f"\nTrades saved to tmp/moving_m15_doge_trades.csv")
    
    # Equity curve
    equity_df = pd.DataFrame({'timestamp': equity_times, 'equity': equity_curve})
    equity_df.to_csv('tmp/moving_m15_doge_equity.csv', index=False)
    print("Equity curve saved to tmp/moving_m15_doge_equity.csv")

if __name__ == "__main__":
    main()
