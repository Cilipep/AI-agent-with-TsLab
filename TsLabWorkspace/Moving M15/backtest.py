#!/usr/bin/env python3
"""
Backtest: Moving M15 Strategy (corrected)
Strategy from Grand Capital webinar:
- Main: SMMA(5) Close vs SMMA(5) Close shifted +5 bars
- Sub: Williams %R(14), SMMA(8) of WR, SMMA(21) of WR
"""

import pandas as pd
import numpy as np

# =================== PARAMETERS ===================
SYMBOL = "GBPUSD"
TIMEFRAME = "M15"
INITIAL_CAPITAL = 10000
COMMISSION_PCT = 0.0002
SL_PCT = 0.003   # 30 pips for GBPUSD M15
TP_PCT = 0.006   # 60 pips

# =================== INDICATORS ===================
def smma(series, period):
    """Smoothed Moving Average (SMMA) - handles NaN in input"""
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
    """Williams %R indicator (returns -100 to 0)"""
    hh = high.rolling(window=period).max()
    ll = low.rolling(window=period).min()
    return -100 * (hh - close) / (hh - ll)

# =================== DATA DOWNLOAD ===================
def download_data(symbol, timeframe):
    """Download M15 data from yfinance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(f"{symbol}=X")
        df = ticker.history(period="60d", interval="15m")
        if df.empty:
            return None
        df = df.reset_index()
        df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df['symbol'] = symbol
        print(f"Downloaded {len(df)} M15 bars for {symbol}")
        return df
    except Exception as e:
        print(f"Download failed: {e}")
        return None

# =================== SIGNALS ===================
def calculate_signals(df):
    """Calculate indicators and generate signals"""
    close = df['close']
    high = df['high']
    low = df['low']
    
    # Main window
    df['smma5'] = smma(close, 5)
    df['smma5_shifted'] = smma(close, 5).shift(5)
    
    # Sub-window: Williams %R + its own MAs
    df['wr14'] = williams_r(high, low, close, 14)
    df['wr8'] = smma(df['wr14'].copy(), 8)    # SMMA(8) of WR
    df['wr21'] = smma(df['wr14'].copy(), 21)   # SMMA(21) of WR
    
    df['signal'] = 0
    
    for i in range(22, len(df)):
        smma5 = df['smma5'].iloc[i]
        smma5s = df['smma5_shifted'].iloc[i]
        wr = df['wr14'].iloc[i]
        wr8 = df['wr8'].iloc[i]
        wr21 = df['wr21'].iloc[i]
        
        smma5_prev = df['smma5'].iloc[i-1]
        smma5s_prev = df['smma5_shifted'].iloc[i-1]
        wr_prev = df['wr14'].iloc[i-1]
        wr8_prev = df['wr8'].iloc[i-1]
        
        # BUY: MA crosses up + WR crosses above its MA8 + WR above MA21
        buy_ma = smma5 > smma5s and smma5_prev <= smma5s_prev
        buy_wr = wr > wr8 and wr_prev <= wr8_prev
        buy_filter = wr > wr21
        
        # SELL: MA crosses down + WR crosses below its MA8 + WR below MA21
        sell_ma = smma5 < smma5s and smma5_prev >= smma5s_prev
        sell_wr = wr < wr8 and wr_prev >= wr8_prev
        sell_filter = wr < wr21
        
        if buy_ma and buy_wr and buy_filter:
            df.loc[df.index[i], 'signal'] = 1
        elif sell_ma and sell_wr and sell_filter:
            df.loc[df.index[i], 'signal'] = -1
    
    return df

# =================== BACKTEST ENGINE ===================
def run_backtest(df, sl_pct, tp_pct, initial_capital):
    """Run backtest with position tracking"""
    capital = initial_capital
    position = 0
    entry_price = 0
    trades = []
    equity_curve = [initial_capital]
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        high = df['high'].iloc[i]
        low = df['low'].iloc[i]
        signal = df['signal'].iloc[i]
        ts = df['timestamp'].iloc[i]
        
        # Check SL/TP if in position
        if position == 1:
            sl = entry_price * (1 - sl_pct)
            tp = entry_price * (1 + tp_pct)
            if low <= sl:
                pnl = ((sl - entry_price) / entry_price - COMMISSION_PCT * 2) * capital
                capital += pnl
                trades.append({'ts': ts, 'dir': 'LONG', 'entry': entry_price, 'exit': sl,
                             'pnl_pct': ((sl - entry_price)/entry_price - COMMISSION_PCT*2)*100, 'type': 'SL'})
                position = 0
                equity_curve.append(capital)
                continue
            elif high >= tp:
                pnl = ((tp - entry_price) / entry_price - COMMISSION_PCT * 2) * capital
                capital += pnl
                trades.append({'ts': ts, 'dir': 'LONG', 'entry': entry_price, 'exit': tp,
                             'pnl_pct': ((tp - entry_price)/entry_price - COMMISSION_PCT*2)*100, 'type': 'TP'})
                position = 0
                equity_curve.append(capital)
                continue
        
        elif position == -1:
            sl = entry_price * (1 + sl_pct)
            tp = entry_price * (1 - tp_pct)
            if high >= sl:
                pnl = ((entry_price - sl) / entry_price - COMMISSION_PCT * 2) * capital
                capital += pnl
                trades.append({'ts': ts, 'dir': 'SHORT', 'entry': entry_price, 'exit': sl,
                             'pnl_pct': ((entry_price - sl)/entry_price - COMMISSION_PCT*2)*100, 'type': 'SL'})
                position = 0
                equity_curve.append(capital)
                continue
            elif low <= tp:
                pnl = ((entry_price - tp) / entry_price - COMMISSION_PCT * 2) * capital
                capital += pnl
                trades.append({'ts': ts, 'dir': 'SHORT', 'entry': entry_price, 'exit': tp,
                             'pnl_pct': ((entry_price - tp)/entry_price - COMMISSION_PCT*2)*100, 'type': 'TP'})
                position = 0
                equity_curve.append(capital)
                continue
        
        # Process new signals
        if signal != 0:
            # Close opposite
            if position == 1 and signal == -1:
                pnl_pct = (price - entry_price) / entry_price - COMMISSION_PCT * 2
                capital += pnl_pct * capital
                trades.append({'ts': ts, 'dir': 'LONG', 'entry': entry_price, 'exit': price,
                             'pnl_pct': pnl_pct * 100, 'type': 'SIGNAL'})
                position = 0
            elif position == -1 and signal == 1:
                pnl_pct = (entry_price - price) / entry_price - COMMISSION_PCT * 2
                capital += pnl_pct * capital
                trades.append({'ts': ts, 'dir': 'SHORT', 'entry': entry_price, 'exit': price,
                             'pnl_pct': pnl_pct * 100, 'type': 'SIGNAL'})
                position = 0
            
            if position == 0:
                position = signal
                entry_price = price
        
        equity_curve.append(capital)
    
    # Close remaining
    if position != 0:
        price = df['close'].iloc[-1]
        pnl_pct = ((price - entry_price)/entry_price if position == 1 else (entry_price - price)/entry_price) - COMMISSION_PCT * 2
        capital += pnl_pct * capital
        trades.append({'ts': df['timestamp'].iloc[-1], 'dir': 'LONG' if position == 1 else 'SHORT',
                      'entry': entry_price, 'exit': price, 'pnl_pct': pnl_pct * 100, 'type': 'END'})
        equity_curve.append(capital)
    
    return trades, equity_curve, capital

# =================== METRICS ===================
def calculate_metrics(trades, equity_curve, initial_capital):
    if not trades:
        return None
    
    wins = [t for t in trades if t['pnl_pct'] > 0]
    losses = [t for t in trades if t['pnl_pct'] <= 0]
    total_return = (equity_curve[-1] - initial_capital) / initial_capital * 100
    
    gp = sum(t['pnl_pct'] for t in wins) if wins else 0
    gl = abs(sum(t['pnl_pct'] for t in losses)) if losses else 0
    pf = gp / gl if gl > 0 else float('inf')
    
    peak = equity_curve[0]
    max_dd = 0
    for val in equity_curve:
        if val > peak: peak = val
        dd = (peak - val) / peak * 100
        if dd > max_dd: max_dd = dd
    
    returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] for i in range(1, len(equity_curve))]
    sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252 * 96) if returns and np.std(returns) > 0 else 0
    
    return {
        'total_trades': len(trades),
        'wins': len(wins), 'losses': len(losses),
        'win_rate': len(wins) / len(trades) * 100,
        'total_return_pct': total_return,
        'profit_factor': pf,
        'max_drawdown_pct': max_dd,
        'sharpe': sharpe,
        'avg_pnl_pct': np.mean([t['pnl_pct'] for t in trades]),
        'avg_win_pct': np.mean([t['pnl_pct'] for t in wins]) if wins else 0,
        'avg_loss_pct': np.mean([t['pnl_pct'] for t in losses]) if losses else 0,
        'sl_hits': len([t for t in trades if t['type'] == 'SL']),
        'tp_hits': len([t for t in trades if t['type'] == 'TP']),
        'signal_exits': len([t for t in trades if t['type'] == 'SIGNAL']),
    }

# =================== MAIN ===================
def main():
    print("=" * 60)
    print("Moving M15 Strategy Backtest")
    print("=" * 60)
    
    df = download_data(SYMBOL, TIMEFRAME)
    if df is None or df.empty:
        return
    
    print(f"\nPeriod: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"Price: {df['close'].min():.5f} - {df['close'].max():.5f}")
    
    df = calculate_signals(df)
    signal_count = int(df['signal'].abs().sum())
    print(f"Signals: {signal_count}")
    
    if signal_count == 0:
        # Show component analysis
        valid = df.dropna(subset=['smma5', 'smma5_shifted', 'wr14', 'wr8', 'wr21'])
        ma_up = ((valid['smma5'] > valid['smma5_shifted']) & (valid['smma5'].shift(1) <= valid['smma5_shifted'].shift(1))).sum()
        ma_dn = ((valid['smma5'] < valid['smma5_shifted']) & (valid['smma5'].shift(1) >= valid['smma5_shifted'].shift(1))).sum()
        wr_up = ((valid['wr14'] > valid['wr8']) & (valid['wr14'].shift(1) <= valid['wr8'].shift(1))).sum()
        wr_dn = ((valid['wr14'] < valid['wr8']) & (valid['wr14'].shift(1) >= valid['wr8'].shift(1))).sum()
        print(f"\nComponents: MA cross ↑{ma_up} ↓{ma_dn} | WR cross ↑{wr_up} ↓{wr_dn}")
        print("Conditions too strict for this data. Try wider SL/TP.")
        return
    
    trades, equity_curve, final_capital = run_backtest(df, SL_PCT, TP_PCT, INITIAL_CAPITAL)
    metrics = calculate_metrics(trades, equity_curve, INITIAL_CAPITAL)
    
    if not metrics:
        print("No trades!")
        return
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Symbol:              {SYMBOL} M15")
    print(f"Initial Capital:     ${INITIAL_CAPITAL:,.2f}")
    print(f"Final Capital:       ${final_capital:,.2f}")
    print("-" * 60)
    print(f"Total Trades:        {metrics['total_trades']}")
    print(f"Wins/Losses:         {metrics['wins']}/{metrics['losses']}")
    print(f"Win Rate:            {metrics['win_rate']:.1f}%")
    print(f"Total Return:        {metrics['total_return_pct']:.2f}%")
    print(f"Profit Factor:       {metrics['profit_factor']:.2f}")
    print(f"Max Drawdown:        {metrics['max_drawdown_pct']:.2f}%")
    print(f"Sharpe Ratio:        {metrics['sharpe']:.2f}")
    print("-" * 60)
    print(f"Avg PnL/Trade:       {metrics['avg_pnl_pct']:.3f}%")
    print(f"Avg Win:             {metrics['avg_win_pct']:.3f}%")
    print(f"Avg Loss:            {metrics['avg_loss_pct']:.3f}%")
    print(f"SL Hits:             {metrics['sl_hits']}")
    print(f"TP Hits:             {metrics['tp_hits']}")
    print(f"Signal Exits:        {metrics['signal_exits']}")
    print("=" * 60)
    
    pd.DataFrame(trades).to_csv('tmp/moving_m15_trades.csv', index=False)
    print(f"\nTrades saved to tmp/moving_m15_trades.csv")
    
    print(f"\nAll trades:")
    print("-" * 85)
    for t in trades:
        s = "+" if t['pnl_pct'] > 0 else ""
        print(f"{t['ts']} | {t['dir']:5} | {t['type']:6} | "
              f"Entry: {t['entry']:.5f} | Exit: {t['exit']:.5f} | PnL: {s}{t['pnl_pct']:.3f}%")

if __name__ == "__main__":
    main()
