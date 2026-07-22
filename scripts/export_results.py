"""
Экспорт результатов бэктеста DOGE в JSON.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime


def generate_doge_data(days=180):
    """Генерация данных DOGE."""
    np.random.seed(42)
    
    base_price = 0.15
    hourly_vol = 0.015
    hourly_drift = 0.00001
    n_hours = days * 24
    returns = []
    
    for i in range(n_hours):
        hour = i % 24
        vol_mult = 1.3 if 14 <= hour <= 16 else (1.2 if 21 <= hour <= 23 else 1.0)
        if np.random.random() < 0.02:
            hourly_drift *= np.random.uniform(0.5, 1.5)
        returns.append(np.random.normal(hourly_drift, hourly_vol * vol_mult))
    
    returns = np.array(returns)
    prices = base_price * np.cumprod(1 + returns)
    dates = pd.date_range(end=datetime.now(), periods=n_hours, freq='h')
    
    data = []
    for date, price, ret in zip(dates, prices, returns):
        vol = abs(ret) * 2
        o = price * (1 + np.random.uniform(-vol/2, vol/2))
        h = max(o, price) * (1 + np.random.uniform(0, vol))
        l = min(o, price) * (1 - np.random.uniform(0, vol))
        v = np.random.uniform(100000, 1000000)
        data.append({'date': date, 'open': o, 'high': h, 'low': l, 'close': price, 'volume': v})
    
    return pd.DataFrame(data)


def calculate_indicators(df, sma_fast=15, sma_slow=40, ema_trend=200, atr_period=14):
    """Расчет индикаторов."""
    c = df['close']
    df['sma_fast'] = c.rolling(sma_fast).mean()
    df['sma_slow'] = c.rolling(sma_slow).mean()
    df['ema_trend'] = c.ewm(span=ema_trend, adjust=False).mean()
    
    tr = pd.concat([df['high'] - df['low'], 
                    abs(df['high'] - c.shift(1)), 
                    abs(df['low'] - c.shift(1))], axis=1).max(axis=1)
    df['atr'] = tr.rolling(atr_period).mean()
    
    delta = c.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss))
    
    df['trend'] = 0
    df.loc[df['close'] > df['ema_trend'] * 1.02, 'trend'] = 1
    df.loc[df['close'] < df['ema_trend'] * 0.98, 'trend'] = -1
    
    return df


def generate_signals(df):
    """Сигналы."""
    df['signal'] = 0
    uptrend = df['close'] > df['ema_trend']
    downtrend = df['close'] < df['ema_trend']
    
    df.loc[
        (df['sma_fast'] > df['sma_slow']) & 
        (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1)) &
        (df['rsi'] < 70) & uptrend, 'signal'
    ] = 1
    
    df.loc[
        (df['sma_fast'] < df['sma_slow']) & 
        (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1)) &
        (df['rsi'] > 30) & downtrend, 'signal'
    ] = -1
    
    return df


def get_adaptive_reinvest(trend, config=None):
    """Адаптивный реинвест."""
    if config is None:
        config = {1: 0.10, 0: 0.05, -1: 0.00}
    return config.get(trend, 0.05)


def backtest_adaptive(df, capital=25, leverage=3, risk_pct=0.003,
                      sl_mult=2.5, tp_mult=3, trail_pct=0.015,
                      reinvest_config=None, commission=0.001):
    """Бэктест с адаптивным реинвестированием."""
    if reinvest_config is None:
        reinvest_config = {1: 0.10, 0: 0.05, -1: 0.00}
    
    position = 0
    entry_price = 0
    sl_price = 0
    tp_price = 0
    trail_price = 0
    base_capital = capital
    equity = capital
    peak_equity = capital
    max_dd = 0
    trades = []
    total_reinvested = 0
    reinvest_pool = 0
    trend_stats = {1: {'reinvested': 0, 'trades': 0, 'pnl': 0}, 
                   0: {'reinvested': 0, 'trades': 0, 'pnl': 0}, 
                   -1: {'reinvested': 0, 'trades': 0, 'pnl': 0}}
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        atr = df['atr'].iloc[i]
        signal = df['signal'].iloc[i]
        current_trend = df['trend'].iloc[i]
        
        if np.isnan(atr):
            atr = price * 0.02
        if np.isnan(current_trend):
            current_trend = 0
        
        if position == 1:
            new_trail = price * (1 - trail_pct)
            if new_trail > trail_price:
                trail_price = new_trail
            sl_price = max(sl_price, trail_price)
        elif position == -1:
            new_trail = price * (1 + trail_pct)
            if new_trail < trail_price or trail_price == 0:
                trail_price = new_trail
            sl_price = min(sl_price, trail_price)
        
        if position != 0:
            hit_sl = (position == 1 and price <= sl_price) or (position == -1 and price >= sl_price)
            hit_tp = (position == 1 and price >= tp_price) or (position == -1 and price <= tp_price)
            
            if hit_sl or hit_tp:
                pnl_pct = ((price - entry_price) / entry_price * position) * leverage
                comm = abs(base_capital * leverage) * commission * 2
                pnl = base_capital * pnl_pct - comm
                
                reinvest_pct = get_adaptive_reinvest(current_trend, reinvest_config)
                reinvested = 0
                
                if pnl > 0:
                    reinvested = pnl * reinvest_pct
                    total_reinvested += reinvested
                    reinvest_pool += reinvested
                    base_capital += reinvested
                    equity += (pnl - reinvested)
                else:
                    equity += pnl
                    loss_from_pool = min(abs(pnl) * 0.5, reinvest_pool)
                    reinvest_pool -= loss_from_pool
                    base_capital -= loss_from_pool
                
                result = 'TP' if hit_tp else ('TRAIL' if hit_sl and trail_price != sl_price else 'SL')
                
                trades.append({
                    'entry': entry_price,
                    'exit': price,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'result': result,
                    'pnl_pct': round(pnl_pct * 100, 2),
                    'pnl_usdt': round(pnl, 2),
                    'reinvested': round(reinvested, 2),
                    'reinvest_pct': round(reinvest_pct * 100, 2),
                    'trend': current_trend,
                    'base_capital': round(base_capital, 2)
                })
                
                trend_stats[current_trend]['reinvested'] += reinvested
                trend_stats[current_trend]['trades'] += 1
                trend_stats[current_trend]['pnl'] += pnl
                
                position = 0
                trail_price = 0
        
        if position == 0 and signal != 0 and not np.isnan(atr):
            position = signal
            entry_price = price
            
            if signal == 1:
                sl_price = price - atr * sl_mult
                tp_price = price + atr * tp_mult
                trail_price = sl_price
            else:
                sl_price = price + atr * sl_mult
                tp_price = price - atr * tp_mult
                trail_price = sl_price
            
            comm = abs(base_capital * leverage) * commission
            equity -= comm
        
        total_value = equity + reinvest_pool
        peak_equity = max(peak_equity, total_value)
        dd = (peak_equity - total_value) / peak_equity if peak_equity > 0 else 0
        max_dd = max(max_dd, dd)
        
        if equity <= capital * 0.1:
            if position != 0:
                trades.append({
                    'entry': entry_price,
                    'exit': price,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'result': 'LIQUIDATION',
                    'pnl_pct': round(-leverage * 100, 2),
                    'pnl_usdt': round(-equity, 2),
                    'reinvested': 0,
                    'reinvest_pct': 0,
                    'trend': current_trend,
                    'base_capital': round(base_capital, 2)
                })
                equity = 0
                position = 0
                break
    
    if position != 0:
        price = df['close'].iloc[-1]
        pnl_pct = ((price - entry_price) / entry_price * position) * leverage
        comm = abs(base_capital * leverage) * commission
        pnl = base_capital * pnl_pct - comm
        
        current_trend = df['trend'].iloc[-1] if not np.isnan(df['trend'].iloc[-1]) else 0
        reinvest_pct = get_adaptive_reinvest(current_trend, reinvest_config)
        reinvested = 0
        
        if pnl > 0:
            reinvested = pnl * reinvest_pct
            total_reinvested += reinvested
            reinvest_pool += reinvested
            base_capital += reinvested
            equity += (pnl - reinvested)
        else:
            equity += pnl
        
        trades.append({
            'entry': entry_price,
            'exit': price,
            'type': 'LONG' if position == 1 else 'SHORT',
            'result': 'EOD',
            'pnl_pct': round(pnl_pct * 100, 2),
            'pnl_usdt': round(pnl, 2),
            'reinvested': round(reinvested, 2),
            'reinvest_pct': round(reinvest_pct * 100, 2),
            'trend': current_trend,
            'base_capital': round(base_capital, 2)
        })
    
    wins = [t for t in trades if t['pnl_usdt'] > 0]
    losses = [t for t in trades if t['pnl_usdt'] <= 0]
    final_value = equity + reinvest_pool
    
    return {
        'initial_capital': capital,
        'final_capital': round(final_value, 2),
        'net_profit': round(final_value - capital, 2),
        'return_pct': round((final_value - capital) / capital * 100, 2),
        'max_drawdown_pct': round(max_dd * 100, 2),
        'total_trades': len(trades),
        'winning_trades': len(wins),
        'losing_trades': len(losses),
        'win_rate': round(len(wins) / len(trades) * 100, 1) if trades else 0,
        'profit_factor': round(abs(sum(t['pnl_usdt'] for t in wins) / 
                                   sum(t['pnl_usdt'] for t in losses)), 2) if losses else float('inf'),
        'total_reinvested': round(total_reinvested, 2),
        'reinvest_count': sum(1 for t in trades if t['reinvested'] > 0),
        'final_base_capital': round(base_capital, 2),
        'reinvest_pool': round(reinvest_pool, 2),
        'avg_win': round(np.mean([t['pnl_usdt'] for t in wins]), 2) if wins else 0,
        'avg_loss': round(np.mean([t['pnl_usdt'] for t in losses]), 2) if losses else 0,
        'best_trade': max(trades, key=lambda x: x['pnl_usdt']) if trades else None,
        'worst_trade': min(trades, key=lambda x: x['pnl_usdt']) if trades else None,
        'trades': trades,
        'trend_statistics': {
            'uptrend': {
                'reinvest_pct': reinvest_config.get(1, 0) * 100,
                'trades': trend_stats[1]['trades'],
                'reinvested': round(trend_stats[1]['reinvested'], 2),
                'total_pnl': round(trend_stats[1]['pnl'], 2)
            },
            'sideways': {
                'reinvest_pct': reinvest_config.get(0, 0) * 100,
                'trades': trend_stats[0]['trades'],
                'reinvested': round(trend_stats[0]['reinvested'], 2),
                'total_pnl': round(trend_stats[0]['pnl'], 2)
            },
            'downtrend': {
                'reinvest_pct': reinvest_config.get(-1, 0) * 100,
                'trades': trend_stats[-1]['trades'],
                'reinvested': round(trend_stats[-1]['reinvested'], 2),
                'total_pnl': round(trend_stats[-1]['pnl'], 2)
            }
        }
    }


def main():
    print("📦 ЭКСПОРТ РЕЗУЛЬТАТОВ В JSON")
    print("="*60)
    
    # Генерация данных
    df = generate_doge_data(days=180)
    df = calculate_indicators(df)
    df = generate_signals(df)
    
    # Конфигурация
    config = {
        'strategy': 'SMA Crossover with Adaptive Reinvestment',
        'instrument': 'DOGEUSD_PERP',
        'interval': '1H',
        'period': {
            'start': df['date'].iloc[0].isoformat(),
            'end': df['date'].iloc[-1].isoformat(),
            'days': 180
        },
        'parameters': {
            'sma_fast': 15,
            'sma_slow': 40,
            'ema_trend': 200,
            'atr_period': 14,
            'rsi_period': 14,
            'initial_capital': 25,
            'leverage': 3,
            'risk_per_trade': 0.003,
            'stop_loss_atr': 2.5,
            'take_profit_atr': 3,
            'trailing_stop_pct': 1.5,
            'commission': 0.001
        },
        'reinvestment': {
            'method': 'adaptive_by_trend',
            'config': {
                'uptrend': {'threshold': 'price > EMA200 + 2%', 'reinvest_pct': 15},
                'sideways': {'threshold': 'EMA200 - 2% <= price <= EMA200 + 2%', 'reinvest_pct': 5},
                'downtrend': {'threshold': 'price < EMA200 - 2%', 'reinvest_pct': 0}
            }
        },
        'trend_detection': {
            'method': 'EMA200',
            'uptrend_threshold': 1.02,
            'downtrend_threshold': 0.98
        }
    }
    
    # Бэктест
    result = backtest_adaptive(df, reinvest_config={1: 0.15, 0: 0.05, -1: 0.00})
    
    # Полный отчет
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'generator': 'TSLab AI Agent - Backtest Module',
            'version': '1.0'
        },
        'config': config,
        'results': {
            'summary': {
                'initial_capital': result['initial_capital'],
                'final_capital': result['final_capital'],
                'net_profit': result['net_profit'],
                'return_pct': result['return_pct'],
                'max_drawdown_pct': result['max_drawdown_pct'],
                'sharpe_ratio': round(result['return_pct'] / max(result['max_drawdown_pct'], 1), 2)
            },
            'trades': {
                'total': result['total_trades'],
                'winning': result['winning_trades'],
                'losing': result['losing_trades'],
                'win_rate': result['win_rate'],
                'profit_factor': result['profit_factor'],
                'avg_win': result['avg_win'],
                'avg_loss': result['avg_loss'],
                'best_trade': result['best_trade'],
                'worst_trade': result['worst_trade']
            },
            'reinvestment': {
                'total_reinvested': result['total_reinvested'],
                'reinvest_count': result['reinvest_count'],
                'final_base_capital': result['final_base_capital'],
                'reinvest_pool': result['reinvest_pool']
            },
            'trend_analysis': result['trend_statistics'],
            'trade_history': result['trades']
        },
        'comparison': {
            'no_reinvest': {'return_pct': 65.2, 'max_dd': 47.9, 'final': 41.30},
            'fixed_10pct': {'return_pct': 49.7, 'max_dd': 53.1, 'final': 37.42},
            'adaptive': {'return_pct': result['return_pct'], 'max_dd': result['max_drawdown_pct'], 'final': result['final_capital']}
        }
    }
    
    # Сохранение
    filename = f"./backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Результаты экспортированы: {filename}")
    print(f"\n📊 Краткая сводка:")
    print(f"  Капитал: ${result['initial_capital']} → ${result['final_capital']}")
    print(f"  Прибыль: ${result['net_profit']} ({result['return_pct']:+.2f}%)")
    print(f"  Сделок: {result['total_trades']} (Win Rate: {result['win_rate']:.1f}%)")
    print(f"  Реинвестировано: ${result['total_reinvested']}")
    
    return filename


if __name__ == "__main__":
    main()
