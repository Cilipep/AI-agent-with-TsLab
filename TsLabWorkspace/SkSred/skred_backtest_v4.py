import pandas as pd
import numpy as np
import os

# === SkSred v4 Parameters ===
SMA_SHORT = 5
SMA_LONG = 20
EMA_TREND = 200  # Trend filter
ATR_PERIOD = 14
ATR_SL_MULT = 1.5  # SL = ATR * 1.5
ATR_TP_MULT = 3.0  # TP = ATR * 3.0
TRAIL_ACTIVATE_PCT = 0.02  # Activate trailing stop at 2% profit
TRAIL_DISTANCE_PCT = 0.015  # Trail at 1.5% from peak
COMMISSION_PCT = 0.05 / 100
INITIAL_CAPITAL = 100000

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calculate_atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def run_backtest(df, symbol, timeframe='H1'):
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Calculate indicators
    df['sma_short'] = df['close'].rolling(window=SMA_SHORT).mean()
    df['sma_long'] = df['close'].rolling(window=SMA_LONG).mean()
    df['atr'] = calculate_atr(df, ATR_PERIOD)
    
    # Adapt EMA period based on available data
    available_bars = len(df)
    if available_bars >= EMA_TREND:
        ema_period = EMA_TREND
    elif available_bars >= 100:
        ema_period = 100
    elif available_bars >= 50:
        ema_period = 50
    else:
        ema_period = min(20, available_bars // 2)
    
    df['ema_trend'] = calculate_ema(df['close'], ema_period)
    
    df = df.dropna(subset=['sma_short', 'sma_long', 'ema_trend', 'atr']).reset_index(drop=True)
    
    if len(df) < SMA_LONG + 2:
        return None
    
    capital = INITIAL_CAPITAL
    position = 0
    entry_price = 0
    entry_time = None
    trades = []
    equity_curve = [capital]
    
    # Trailing stop variables
    trail_activated = False
    trail_high = 0  # For long positions
    trail_low = float('inf')  # For short positions
    
    for i in range(1, len(df)):
        current_price = df.iloc[i]['close']
        high_price = df.iloc[i]['high']
        low_price = df.iloc[i]['low']
        
        sma1_t = df.iloc[i]['sma_short']
        sma2_t = df.iloc[i]['sma_long']
        sma1_y = df.iloc[i-1]['sma_short']
        sma2_y = df.iloc[i-1]['sma_long']
        
        ema_trend = df.iloc[i]['ema_trend']
        atr = df.iloc[i]['atr']
        
        golden_cross = (sma1_t > sma2_t) and (sma1_y <= sma2_y)
        death_cross = (sma1_t < sma2_t) and (sma1_y >= sma2_y)
        
        # Dynamic SL/TP based on ATR
        sl_distance = atr * ATR_SL_MULT
        tp_distance = atr * ATR_TP_MULT
        
        # Check SL/TP first if in position
        if position == 1:
            sl_price = entry_price - sl_distance
            tp_price = entry_price + tp_distance
            
            # Check if SL or TP hit
            if low_price <= sl_price:
                exit_price = sl_price
                pnl = (exit_price - entry_price) / entry_price
                commission = COMMISSION_PCT * 2
                net_pnl = pnl - commission
                capital *= (1 + net_pnl)
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': df.iloc[i]['timestamp'],
                    'direction': 'LONG',
                    'exit_type': 'SL',
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl_pct': net_pnl * 100,
                    'capital_after': capital
                })
                position = 0
                trail_activated = False
            elif high_price >= tp_price:
                exit_price = tp_price
                pnl = (exit_price - entry_price) / entry_price
                commission = COMMISSION_PCT * 2
                net_pnl = pnl - commission
                capital *= (1 + net_pnl)
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': df.iloc[i]['timestamp'],
                    'direction': 'LONG',
                    'exit_type': 'TP',
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl_pct': net_pnl * 100,
                    'capital_after': capital
                })
                position = 0
                trail_activated = False
            # Trailing stop for long
            elif trail_activated:
                if low_price <= trail_high * (1 - TRAIL_DISTANCE_PCT):
                    exit_price = trail_high * (1 - TRAIL_DISTANCE_PCT)
                    pnl = (exit_price - entry_price) / entry_price
                    commission = COMMISSION_PCT * 2
                    net_pnl = pnl - commission
                    capital *= (1 + net_pnl)
                    trades.append({
                        'entry_time': entry_time,
                        'exit_time': df.iloc[i]['timestamp'],
                        'direction': 'LONG',
                        'exit_type': 'TRAIL',
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl_pct': net_pnl * 100,
                        'capital_after': capital
                    })
                    position = 0
                    trail_activated = False
        
        elif position == -1:
            sl_price = entry_price + sl_distance
            tp_price = entry_price - tp_distance
            
            if high_price >= sl_price:
                exit_price = sl_price
                pnl = (entry_price - exit_price) / entry_price
                commission = COMMISSION_PCT * 2
                net_pnl = pnl - commission
                capital *= (1 + net_pnl)
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': df.iloc[i]['timestamp'],
                    'direction': 'SHORT',
                    'exit_type': 'SL',
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl_pct': net_pnl * 100,
                    'capital_after': capital
                })
                position = 0
                trail_activated = False
            elif low_price <= tp_price:
                exit_price = tp_price
                pnl = (entry_price - exit_price) / entry_price
                commission = COMMISSION_PCT * 2
                net_pnl = pnl - commission
                capital *= (1 + net_pnl)
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': df.iloc[i]['timestamp'],
                    'direction': 'SHORT',
                    'exit_type': 'TP',
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl_pct': net_pnl * 100,
                    'capital_after': capital
                })
                position = 0
                trail_activated = False
            # Trailing stop for short
            elif trail_activated:
                if high_price >= trail_low * (1 + TRAIL_DISTANCE_PCT):
                    exit_price = trail_low * (1 + TRAIL_DISTANCE_PCT)
                    pnl = (entry_price - exit_price) / entry_price
                    commission = COMMISSION_PCT * 2
                    net_pnl = pnl - commission
                    capital *= (1 + net_pnl)
                    trades.append({
                        'entry_time': entry_time,
                        'exit_time': df.iloc[i]['timestamp'],
                        'direction': 'SHORT',
                        'exit_type': 'TRAIL',
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl_pct': net_pnl * 100,
                        'capital_after': capital
                    })
                    position = 0
                    trail_activated = False
        
        # Update trailing stop levels if in position
        if position == 1:
            if not trail_activated:
                unrealized_pct = (high_price - entry_price) / entry_price
                if unrealized_pct >= TRAIL_ACTIVATE_PCT:
                    trail_activated = True
                    trail_high = high_price
            else:
                trail_high = max(trail_high, high_price)
        elif position == -1:
            if not trail_activated:
                unrealized_pct = (entry_price - low_price) / entry_price
                if unrealized_pct >= TRAIL_ACTIVATE_PCT:
                    trail_activated = True
                    trail_low = low_price
            else:
                trail_low = min(trail_low, low_price)
        
        # Check signal exits (only if not stopped out/taken profit)
        if position == 1 and death_cross:
            exit_price = current_price
            pnl = (exit_price - entry_price) / entry_price
            commission = COMMISSION_PCT * 2
            net_pnl = pnl - commission
            capital *= (1 + net_pnl)
            trades.append({
                'entry_time': entry_time,
                'exit_time': df.iloc[i]['timestamp'],
                'direction': 'LONG',
                'exit_type': 'SIGNAL',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl_pct': net_pnl * 100,
                'capital_after': capital
            })
            position = 0
            trail_activated = False
        elif position == -1 and golden_cross:
            exit_price = current_price
            pnl = (entry_price - exit_price) / entry_price
            commission = COMMISSION_PCT * 2
            net_pnl = pnl - commission
            capital *= (1 + net_pnl)
            trades.append({
                'entry_time': entry_time,
                'exit_time': df.iloc[i]['timestamp'],
                'direction': 'SHORT',
                'exit_type': 'SIGNAL',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl_pct': net_pnl * 100,
                'capital_after': capital
            })
            position = 0
            trail_activated = False
        
        # Enter new position (with trend filter)
        if position == 0:
            if golden_cross and current_price > ema_trend:  # Long only above EMA 200
                position = 1
                entry_price = current_price
                entry_time = df.iloc[i]['timestamp']
                trail_activated = False
                trail_high = current_price
            elif death_cross and current_price < ema_trend:  # Short only below EMA 200
                position = -1
                entry_price = current_price
                entry_time = df.iloc[i]['timestamp']
                trail_activated = False
                trail_low = current_price
        
        equity_curve.append(capital)
    
    if position != 0:
        exit_price = df.iloc[-1]['close']
        pnl = (exit_price - entry_price) / entry_price if position == 1 else (entry_price - exit_price) / entry_price
        commission = COMMISSION_PCT * 2
        net_pnl = pnl - commission
        capital *= (1 + net_pnl)
        trades.append({
            'entry_time': entry_time,
            'exit_time': df.iloc[-1]['timestamp'],
            'direction': 'LONG' if position == 1 else 'SHORT',
            'exit_type': 'EOD',
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl_pct': net_pnl * 100,
            'capital_after': capital
        })
    
    if len(trades) == 0:
        return {'symbol': symbol, 'timeframe': timeframe, 'trades': 0, 'total_return_pct': 0, 'win_rate': 0, 'profit_factor': 0, 'max_drawdown_pct': 0, 'sharpe': 0, 'sl_count': 0, 'tp_count': 0, 'trail_count': 0, 'signal_count': 0}
    
    trade_returns = [t['pnl_pct'] / 100 for t in trades]
    wins = [r for r in trade_returns if r > 0]
    losses = [r for r in trade_returns if r <= 0]
    
    win_rate = len(wins) / len(trades) * 100
    gross_profit = sum(wins) if wins else 0
    gross_loss = abs(sum(losses)) if losses else 0.0001
    profit_factor = gross_profit / gross_loss
    
    equity = np.array(equity_curve)
    peak = np.maximum.accumulate(equity)
    drawdown = (peak - equity) / peak
    max_drawdown = drawdown.max() * 100
    
    avg_return = np.mean(trade_returns)
    std_return = np.std(trade_returns)
    sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
    
    total_return = ((capital - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    
    sl_count = sum(1 for t in trades if t['exit_type'] == 'SL')
    tp_count = sum(1 for t in trades if t['exit_type'] == 'TP')
    trail_count = sum(1 for t in trades if t['exit_type'] == 'TRAIL')
    signal_count = sum(1 for t in trades if t['exit_type'] == 'SIGNAL')
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'trades': len(trades),
        'total_return_pct': round(total_return, 2),
        'win_rate': round(win_rate, 1),
        'profit_factor': round(profit_factor, 2),
        'max_drawdown_pct': round(max_drawdown, 2),
        'sharpe': round(sharpe, 2),
        'sl_count': sl_count,
        'tp_count': tp_count,
        'trail_count': trail_count,
        'signal_count': signal_count
    }

def main():
    base_dir = r"C:\Users\i59400f\Desktop\ai-agent\tmp\market_data"
    
    print("=" * 110)
    print(f"SkSRED v4 | SMA({SMA_SHORT}/{SMA_LONG}) | EMA{EMA_TREND} Filter | ATR SL:{ATR_SL_MULT}x TP:{ATR_TP_MULT}x | Trail:{TRAIL_ACTIVATE_PCT*100:.0f}%/{TRAIL_DISTANCE_PCT*100:.1f}%")
    print("=" * 110)
    
    # Process all available timeframes
    timeframes = ['H1', 'H4', 'D1']
    
    for tf in timeframes:
        csv_path = os.path.join(base_dir, f"ALL_INSTRUMENTS_{tf}_60d.csv")
        if not os.path.exists(csv_path):
            print(f"\n{tf}: Data file not found, skipping...")
            continue
        
        print(f"\n{'='*110}")
        print(f"TIMEFRAME: {tf}")
        print(f"{'='*110}")
        
        df_all = pd.read_csv(csv_path)
        symbols = sorted(df_all['symbol'].unique())
        print(f"Instruments: {len(symbols)}\n")
        
        results = []
        for symbol in symbols:
            df_sym = df_all[df_all['symbol'] == symbol].copy()
            result = run_backtest(df_sym, symbol, tf)
            if result:
                results.append(result)
        
        results.sort(key=lambda x: x['total_return_pct'], reverse=True)
        
        print(f"{'Symbol':<16} {'Trades':>7} {'Ret%':>8} {'WR%':>6} {'PF':>6} {'MaxDD%':>8} {'SL':>4} {'TP':>4} {'Trail':>6} {'Sig':>4}")
        print("-" * 110)
        
        for r in results:
            print(f"{r['symbol']:<16} {r['trades']:>7} {r['total_return_pct']:>+8.2f} {r['win_rate']:>5.1f}% {r['profit_factor']:>6.2f} {r['max_drawdown_pct']:>7.2f}% {r['sl_count']:>4} {r['tp_count']:>4} {r['trail_count']:>6} {r['signal_count']:>4}")
        
        print("-" * 110)
        
        returns = [r['total_return_pct'] for r in results]
        winners = [r for r in results if r['total_return_pct'] > 0]
        
        print(f"\n{'SUMMARY':=^110}")
        if len(results) > 0:
            print(f"Profitable: {len(winners)}/{len(results)} ({len(winners)/len(results)*100:.0f}%)")
            print(f"Avg Return: {np.mean(returns):+.2f}% | Median: {np.median(returns):+.2f}%")
            print(f"Best: {results[0]['symbol']} ({results[0]['total_return_pct']:+.2f}%)")
            print(f"Worst: {results[-1]['symbol']} ({results[-1]['total_return_pct']:+.2f}%)")
        else:
            print("No results (insufficient data for this timeframe)")
        
        total_sl = sum(r['sl_count'] for r in results)
        total_tp = sum(r['tp_count'] for r in results)
        total_trail = sum(r['trail_count'] for r in results)
        total_sig = sum(r['signal_count'] for r in results)
        total_trades = sum(r['trades'] for r in results)
        if total_trades > 0:
            print(f"\nExit distribution: SL={total_sl} ({total_sl/total_trades*100:.0f}%) | TP={total_tp} ({total_tp/total_trades*100:.0f}%) | Trail={total_trail} ({total_trail/total_trades*100:.0f}%) | Signal={total_sig} ({total_sig/total_trades*100:.0f}%)")
        
        print(f"\n{'TOP 5':=^110}")
        for r in results[:5]:
            print(f"  {r['symbol']}: {r['total_return_pct']:+.2f}% | WR:{r['win_rate']:.0f}% | PF:{r['profit_factor']:.2f} | SL:{r['sl_count']} TP:{r['tp_count']} Trail:{r['trail_count']} Sig:{r['signal_count']}")
        
        print(f"\n{'BOTTOM 5':=^110}")
        for r in results[-5:]:
            print(f"  {r['symbol']}: {r['total_return_pct']:+.2f}% | WR:{r['win_rate']:.0f}% | PF:{r['profit_factor']:.2f} | SL:{r['sl_count']} TP:{r['tp_count']} Trail:{r['trail_count']} Sig:{r['signal_count']}")
        
        # Save results
        df_results = pd.DataFrame(results)
        output_path = os.path.join(r"C:\Users\i59400f\Desktop\ai-agent\tmp", f"skred_v4_{tf.lower()}_results.csv")
        df_results.to_csv(output_path, index=False)
        print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
