"""
Финальный бэктест DOGE с оптимальными настройками.
Капитал: 25 USDT, Плечо: 3x, Реинвест: 15/5/0
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json


def generate_doge_data(days=180):
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


def calculate_indicators(df):
    c = df['close']
    df['sma_fast'] = c.rolling(15).mean()
    df['sma_slow'] = c.rolling(40).mean()
    df['ema_trend'] = c.ewm(span=200, adjust=False).mean()
    
    tr = pd.concat([df['high'] - df['low'], 
                    abs(df['high'] - c.shift(1)), 
                    abs(df['low'] - c.shift(1))], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    
    delta = c.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss))
    
    df['trend'] = 0
    df.loc[df['close'] > df['ema_trend'] * 1.02, 'trend'] = 1
    df.loc[df['close'] < df['ema_trend'] * 0.98, 'trend'] = -1
    
    return df


def generate_signals(df):
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


def backtest_final(df, capital=25, leverage=3):
    """Финальный бэктест с оптимальными настройками."""
    position = 0
    entry_price = 0
    sl_price = 0
    tp_price = 0
    trail_price = 0
    
    # Оптимальные параметры
    risk_pct = 0.003
    sl_mult = 2.5
    tp_mult = 3
    trail_pct = 0.015
    commission = 0.001
    
    # Адаптивный реинвест: 15/5/0
    reinvest_config = {1: 0.15, 0: 0.05, -1: 0.00}
    
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
    
    equity_history = [capital]
    daily_equity = []
    current_day = None
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        atr = df['atr'].iloc[i]
        signal = df['signal'].iloc[i]
        current_trend = df['trend'].iloc[i]
        
        if np.isnan(atr):
            atr = price * 0.02
        if np.isnan(current_trend):
            current_trend = 0
        
        # Трейлинг стоп
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
        
        # Проверка стопов
        if position != 0:
            hit_sl = (position == 1 and price <= sl_price) or (position == -1 and price >= sl_price)
            hit_tp = (position == 1 and price >= tp_price) or (position == -1 and price <= tp_price)
            
            if hit_sl or hit_tp:
                pnl_pct = ((price - entry_price) / entry_price * position) * leverage
                comm = abs(base_capital * leverage) * commission * 2
                pnl = base_capital * pnl_pct - comm
                
                reinvest_pct = reinvest_config.get(current_trend, 0.05)
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
                    'entry': round(entry_price, 6),
                    'exit': round(price, 6),
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
        
        # Новая позиция
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
        
        equity_history.append(total_value)
    
    # Close
    if position != 0:
        price = df['close'].iloc[-1]
        pnl_pct = ((price - entry_price) / entry_price * position) * leverage
        comm = abs(base_capital * leverage) * commission
        pnl = base_capital * pnl_pct - comm
        
        current_trend = df['trend'].iloc[-1] if not np.isnan(df['trend'].iloc[-1]) else 0
        reinvest_pct = reinvest_config.get(current_trend, 0.05)
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
            'entry': round(entry_price, 6),
            'exit': round(price, 6),
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
        'config': {
            'capital': capital,
            'leverage': leverage,
            'risk_pct': risk_pct,
            'sl_atr': sl_mult,
            'tp_atr': tp_mult,
            'trail_pct': trail_pct * 100,
            'reinvest': reinvest_config
        },
        'results': {
            'initial': capital,
            'final': round(final_value, 2),
            'pnl': round(final_value - capital, 2),
            'return_pct': round((final_value - capital) / capital * 100, 2),
            'max_dd': round(max_dd * 100, 2),
            'sharpe': round((final_value - capital) / capital * 100 / max(max_dd * 100, 1), 2),
            'trades': len(trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(len(wins) / len(trades) * 100, 1) if trades else 0,
            'profit_factor': round(abs(sum(t['pnl_usdt'] for t in wins) / 
                                       sum(t['pnl_usdt'] for t in losses)), 2) if losses else float('inf'),
            'total_reinvested': round(total_reinvested, 2),
            'reinvest_pool': round(reinvest_pool, 2),
            'base_capital': round(base_capital, 2)
        },
        'trades': trades,
        'trend_stats': {k: {'trades': v['trades'], 'reinvested': round(v['reinvested'], 2), 'pnl': round(v['pnl'], 2)} for k, v in trend_stats.items()},
        'equity_curve': equity_history
    }


def main():
    print("🚀 ФИНАЛЬНЫЙ БЭКТЕСТ DOGE")
    print("="*70)
    
    print("\n📋 НАСТРОЙКИ:")
    print("-"*70)
    print(f"  Капитал:        25 USDT")
    print(f"  Плечо:          3x")
    print(f"  Risk на сделку: 0.3%")
    print(f"  Stop Loss:      2.5x ATR")
    print(f"  Take Profit:    3x ATR")
    print(f"  Trail Stop:     1.5%")
    print(f"  Реинвест:       15% (↑) / 5% (→) / 0% (↓)")
    
    # Данные
    df = generate_doge_data(days=180)
    df = calculate_indicators(df)
    df = generate_signals(df)
    
    print(f"\n📈 ДАННЫЕ:")
    print("-"*70)
    print(f"  Период:         {df['date'].iloc[0].strftime('%Y-%m-%d')} - {df['date'].iloc[-1].strftime('%Y-%m-%d')}")
    print(f"  Баров:          {len(df)}")
    print(f"  Начальная цена: ${df['close'].iloc[0]:.4f}")
    print(f"  Конечная цена:  ${df['close'].iloc[-1]:.4f}")
    print(f"  Изменение:      {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:+.2f}%")
    
    # Бэктест
    result = backtest_final(df, capital=25, leverage=3)
    
    print(f"\n🎯 РЕЗУЛЬТАТЫ:")
    print("="*70)
    print(f"  Начальный капитал:     ${result['results']['initial']}")
    print(f"  Конечный капитал:      ${result['results']['final']}")
    print(f"  Чистая прибыль:        ${result['results']['pnl']}")
    print(f"  Доходность:            {result['results']['return_pct']:+.2f}%")
    print(f"  Макс. просадка:        {result['results']['max_dd']:.2f}%")
    print(f"  Sharpe Ratio:          {result['results']['sharpe']}")
    print(f"  Profit Factor:         {result['results']['profit_factor']}")
    
    print(f"\n📊 СДЕЛКИ:")
    print("-"*70)
    print(f"  Всего:                 {result['results']['trades']}")
    print(f"  Прибыльных:            {result['results']['wins']}")
    print(f"  Убыточных:             {result['results']['losses']}")
    print(f"  Win Rate:              {result['results']['win_rate']:.1f}%")
    
    print(f"\n💰 РЕИНВЕСТИРОВАНИЕ:")
    print("-"*70)
    print(f"  Всего реинвестировано: ${result['results']['total_reinvested']}")
    print(f"  Пул реинвестирования:  ${result['results']['reinvest_pool']}")
    print(f"  Базовый капитал:       ${result['results']['base_capital']}")
    
    print(f"\n📈 ПО ТРЕНДАМ:")
    print("-"*70)
    trend_names = {1: "Восходящий (15%)", 0: "Боковой (5%)", -1: "Нисходящий (0%)"}
    for trend in [1, 0, -1]:
        stats = result['trend_stats'][trend]
        print(f"  {trend_names[trend]:<25} → Сделок: {stats['trades']:>3} | Реинвест: ${stats['reinvested']:>6.2f} | PnL: ${stats['pnl']:>+8.2f}")
    
    print(f"\n📋 ДЕТАЛИ СДЕЛОК:")
    print("-"*100)
    print(f"  {'#':>3} {'Тип':>6} {'Вход':>10} {'Выход':>10} {'Рез':>5} {'PnL%':>8} {'PnL$':>10} {'Реинвест':>10} {'Тренд':>6}")
    print("-"*100)
    
    for i, t in enumerate(result['trades'], 1):
        trend_str = "↑" if t['trend'] == 1 else ("↓" if t['trend'] == -1 else "→")
        reinvest_str = f"{t['reinvest_pct']:.0f}%" if t['reinvested'] > 0 else "-"
        print(f"  {i:>3} {t['type']:>6} ${t['entry']:.4f} ${t['exit']:.4f} {t['result']:>5} {t['pnl_pct']:>+7.1f}% ${t['pnl_usdt']:>+9.2f} {reinvest_str:>10} {trend_str:>6}")
    
    # Сохранение
    output = {
        'generated_at': datetime.now().isoformat(),
        'instrument': 'DOGEUSD_PERP',
        'interval': '1H',
        'period_days': 180,
        **result
    }
    
    filename = f"./backtest_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n\n✅ БЭКТЕСТ ЗАВЕРШЕН")
    print(f"📄 Результаты: {filename}")
    
    return result


if __name__ == "__main__":
    main()
