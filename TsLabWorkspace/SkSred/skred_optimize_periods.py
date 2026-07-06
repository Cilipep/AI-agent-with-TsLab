import pandas as pd
import numpy as np
import os
from itertools import product

# === Optimization Parameters ===
EMA_TREND = 200
ATR_PERIOD = 14
ATR_SL_MULT = 1.5
ATR_TP_MULT = 3.0
TRAIL_ACTIVATE_PCT = 0.02
TRAIL_DISTANCE_PCT = 0.015
COMMISSION_PCT = 0.05 / 100
INITIAL_CAPITAL = 100000

# Grid search parameters
SMA_SHORT_OPTIONS = [3, 5, 7, 10]
SMA_LONG_OPTIONS = [15, 20, 30, 50]
MIN_TRADES = 10

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

def run_backtest(df, sma_short, sma_long):
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    df['sma_short'] = df['close'].rolling(window=sma_short).mean()
    df['sma_long'] = df['close'].rolling(window=sma_long).mean()
    df['atr'] = calculate_atr(df, ATR_PERIOD)
    
    # Adapt EMA period
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
    
    if len(df) < sma_long + 2:
        return None
    
    capital = INITIAL_CAPITAL
    position = 0
    entry_price = 0
    trades = []
    equity_curve = [capital]
    
    trail_activated = False
    trail_high = 0
    trail_low = float('inf')
    
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
        
        sl_distance = atr * ATR_SL_MULT
        tp_distance = atr * ATR_TP_MULT
        
        # Check SL/TP
        if position == 1:
            sl_price = entry_price - sl_distance
            tp_price = entry_price + tp_distance
            
            if low_price <= sl_price:
                exit_price = sl_price
                pnl = (exit_price - entry_price) / entry_price
                net_pnl = pnl - COMMISSION_PCT * 2
                capital *= (1 + net_pnl)
                trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'SL'})
                position = 0
                trail_activated = False
            elif high_price >= tp_price:
                exit_price = tp_price
                pnl = (exit_price - entry_price) / entry_price
                net_pnl = pnl - COMMISSION_PCT * 2
                capital *= (1 + net_pnl)
                trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'TP'})
                position = 0
                trail_activated = False
            elif trail_activated:
                if low_price <= trail_high * (1 - TRAIL_DISTANCE_PCT):
                    exit_price = trail_high * (1 - TRAIL_DISTANCE_PCT)
                    pnl = (exit_price - entry_price) / entry_price
                    net_pnl = pnl - COMMISSION_PCT * 2
                    capital *= (1 + net_pnl)
                    trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'TRAIL'})
                    position = 0
                    trail_activated = False
        
        elif position == -1:
            sl_price = entry_price + sl_distance
            tp_price = entry_price - tp_distance
            
            if high_price >= sl_price:
                exit_price = sl_price
                pnl = (entry_price - exit_price) / entry_price
                net_pnl = pnl - COMMISSION_PCT * 2
                capital *= (1 + net_pnl)
                trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'SL'})
                position = 0
                trail_activated = False
            elif low_price <= tp_price:
                exit_price = tp_price
                pnl = (entry_price - exit_price) / entry_price
                net_pnl = pnl - COMMISSION_PCT * 2
                capital *= (1 + net_pnl)
                trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'TP'})
                position = 0
                trail_activated = False
            elif trail_activated:
                if high_price >= trail_low * (1 + TRAIL_DISTANCE_PCT):
                    exit_price = trail_low * (1 + TRAIL_DISTANCE_PCT)
                    pnl = (entry_price - exit_price) / entry_price
                    net_pnl = pnl - COMMISSION_PCT * 2
                    capital *= (1 + net_pnl)
                    trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'TRAIL'})
                    position = 0
                    trail_activated = False
        
        # Update trailing stop
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
        
        # Signal exits
        if position == 1 and death_cross:
            exit_price = current_price
            pnl = (exit_price - entry_price) / entry_price
            net_pnl = pnl - COMMISSION_PCT * 2
            capital *= (1 + net_pnl)
            trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'SIGNAL'})
            position = 0
            trail_activated = False
        elif position == -1 and golden_cross:
            exit_price = current_price
            pnl = (entry_price - exit_price) / entry_price
            net_pnl = pnl - COMMISSION_PCT * 2
            capital *= (1 + net_pnl)
            trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'SIGNAL'})
            position = 0
            trail_activated = False
        
        # Enter new position
        if position == 0:
            if golden_cross and current_price > ema_trend:
                position = 1
                entry_price = current_price
                trail_activated = False
                trail_high = current_price
            elif death_cross and current_price < ema_trend:
                position = -1
                entry_price = current_price
                trail_activated = False
                trail_low = current_price
        
        equity_curve.append(capital)
    
    # Close open position
    if position != 0:
        exit_price = df.iloc[-1]['close']
        pnl = (exit_price - entry_price) / entry_price if position == 1 else (entry_price - exit_price) / entry_price
        net_pnl = pnl - COMMISSION_PCT * 2
        capital *= (1 + net_pnl)
        trades.append({'pnl_pct': net_pnl * 100, 'exit_type': 'EOD'})
    
    if len(trades) < MIN_TRADES:
        return None
    
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
    
    return {
        'total_return_pct': round(total_return, 2),
        'win_rate': round(win_rate, 1),
        'profit_factor': round(profit_factor, 2),
        'max_drawdown_pct': round(max_drawdown, 2),
        'sharpe': round(sharpe, 2),
        'trades': len(trades)
    }

def main():
    base_dir = r"C:\Users\i59400f\Desktop\ai-agent\tmp\market_data"
    
    print("=" * 100)
    print("SkSRED Period Optimization | H4 Timeframe")
    print("=" * 100)
    
    # Load H4 data
    csv_path = os.path.join(base_dir, "ALL_INSTRUMENTS_H4_60d.csv")
    if not os.path.exists(csv_path):
        print(f"Data file not found: {csv_path}")
        return
    
    df_all = pd.read_csv(csv_path)
    symbols = sorted(df_all['symbol'].unique())
    
    # Generate parameter combinations
    param_combos = [(s, l) for s, l in product(SMA_SHORT_OPTIONS, SMA_LONG_OPTIONS) if l >= 2 * s]
    print(f"\nParameter combinations: {len(param_combos)}")
    print(f"Instruments: {len(symbols)}")
    print(f"Minimum trades: {MIN_TRADES}\n")
    
    all_results = []
    
    for symbol in symbols:
        print(f"Optimizing {symbol}...", end=" ")
        
        df_sym = df_all[df_all['symbol'] == symbol].copy()
        
        best_result = None
        best_params = None
        
        for sma_short, sma_long in param_combos:
            result = run_backtest(df_sym, sma_short, sma_long)
            
            if result is not None:
                if best_result is None or result['total_return_pct'] > best_result['total_return_pct']:
                    best_result = result
                    best_params = (sma_short, sma_long)
        
        if best_result:
            print(f"Best: SMA({best_params[0]}/{best_params[1]}) -> {best_result['total_return_pct']:+.2f}%")
            all_results.append({
                'symbol': symbol,
                'sma_short': best_params[0],
                'sma_long': best_params[1],
                'total_return_pct': best_result['total_return_pct'],
                'win_rate': best_result['win_rate'],
                'profit_factor': best_result['profit_factor'],
                'max_drawdown_pct': best_result['max_drawdown_pct'],
                'sharpe': best_result['sharpe'],
                'trades': best_result['trades']
            })
        else:
            print("No valid result")
    
    # Sort by return
    all_results.sort(key=lambda x: x['total_return_pct'], reverse=True)
    
    print(f"\n{'='*100}")
    print("OPTIMIZATION RESULTS (H4)")
    print(f"{'='*100}\n")
    
    print(f"{'Symbol':<16} {'SMA_S':>6} {'SMA_L':>6} {'Ret%':>8} {'WR%':>6} {'PF':>6} {'MaxDD%':>8} {'Sharpe':>7} {'Trades':>7}")
    print("-" * 100)
    
    for r in all_results:
        print(f"{r['symbol']:<16} {r['sma_short']:>6} {r['sma_long']:>6} {r['total_return_pct']:>+8.2f} {r['win_rate']:>5.1f}% {r['profit_factor']:>6.2f} {r['max_drawdown_pct']:>7.2f}% {r['sharpe']:>7.2f} {r['trades']:>7}")
    
    print("-" * 100)
    
    returns = [r['total_return_pct'] for r in all_results]
    winners = [r for r in all_results if r['total_return_pct'] > 0]
    
    print(f"\n{'SUMMARY':=^100}")
    print(f"Profitable: {len(winners)}/{len(all_results)} ({len(winners)/len(all_results)*100:.0f}%)")
    print(f"Avg Return: {np.mean(returns):+.2f}% | Median: {np.median(returns):+.2f}%")
    print(f"Best: {all_results[0]['symbol']} SMA({all_results[0]['sma_short']}/{all_results[0]['sma_long']}) ({all_results[0]['total_return_pct']:+.2f}%)")
    print(f"Worst: {all_results[-1]['symbol']} ({all_results[-1]['total_return_pct']:+.2f}%)")
    
    # Period distribution
    print(f"\n{'OPTIMAL PERIOD DISTRIBUTION':=^100}")
    short_periods = [r['sma_short'] for r in all_results if r['total_return_pct'] > 0]
    long_periods = [r['sma_long'] for r in all_results if r['total_return_pct'] > 0]
    
    from collections import Counter
    print(f"\nSMA_SHORT distribution (profitable):")
    for p, c in Counter(short_periods).most_common():
        print(f"  {p}: {c} instruments")
    
    print(f"\nSMA_LONG distribution (profitable):")
    for p, c in Counter(long_periods).most_common():
        print(f"  {p}: {c} instruments")
    
    # Save results
    output_path = r"C:\Users\i59400f\Desktop\ai-agent\tmp\skred_optimized_periods.csv"
    df_results = pd.DataFrame(all_results)
    df_results.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
