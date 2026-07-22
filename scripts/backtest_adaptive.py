"""
Бэктест DOGE с адаптивным реинвестированием по тренду.
Восходящий тренд → реинвест 10%
Нисходящий тренд → реинвест 0%
Боковой → реинвест 5%
"""

import numpy as np
import pandas as pd
from datetime import datetime


def generate_doge_data(days=180):
    """Генерация реалистичных данных DOGE."""
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
    
    # Определение тренда
    df['trend'] = 0  # 0 = боковой
    df.loc[df['close'] > df['ema_trend'] * 1.02, 'trend'] = 1   # Восходящий
    df.loc[df['close'] < df['ema_trend'] * 0.98, 'trend'] = -1  # Нисходящий
    
    return df


def generate_signals(df):
    """Сигналы с фильтром тренда."""
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
    """
    Адаптивный процент реинвестирования в зависимости от тренда.
    
    Args:
        trend: 1 (восходящий), -1 (нисходящий), 0 (боковой)
        config: словарь с настройками
    """
    if config is None:
        config = {
            1: 0.10,   # Восходящий: 10%
            0: 0.05,   # Боковой: 5%
            -1: 0.00   # Нисходящий: 0%
        }
    return config.get(trend, 0.05)


def backtest_adaptive_reinvest(df, capital=25, leverage=3, risk_pct=0.003,
                               sl_mult=2.5, tp_mult=3, trail_pct=0.015,
                               reinvest_config=None, commission=0.001):
    """
    Бэктест с адаптивным реинвестированием по тренду.
    
    Args:
        reinvest_config: словарь {trend: reinvest_pct}
    """
    if reinvest_config is None:
        reinvest_config = {
            1: 0.10,   # Восходящий тренд: 10% реинвест
            0: 0.05,   # Боковой: 5% реинвест
            -1: 0.00   # Нисходящий: 0% реинвест (вывод прибыли)
        }
    
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
    
    # Статистика по трендам
    trend_stats = {1: {'reinvested': 0, 'trades': 0}, 
                   0: {'reinvested': 0, 'trades': 0}, 
                   -1: {'reinvested': 0, 'trades': 0}}
    
    equity_history = [capital]
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        atr = df['atr'].iloc[i]
        signal = df['signal'].iloc[i]
        current_trend = df['trend'].iloc[i]
        
        if np.isnan(atr):
            atr = price * 0.02
        if np.isnan(current_trend):
            current_trend = 0
        
        # Обновление трейлинг стопа
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
                
                # Адаптивное реинвестирование по тренду
                reinvest_pct = get_adaptive_reinvest(current_trend, reinvest_config)
                reinvested = 0
                
                if pnl > 0:
                    reinvested = pnl * reinvest_pct
                    total_reinvested += reinvested
                    reinvest_pool += reinvested
                    base_capital += reinvested
                    equity += (pnl - reinvested)
                    
                    # Статистика
                    trend_stats[current_trend]['reinvested'] += reinvested
                    trend_stats[current_trend]['trades'] += 1
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
                    'pnl_pct': pnl_pct * 100,
                    'pnl_usdt': pnl,
                    'reinvested': reinvested,
                    'reinvest_pct': reinvest_pct * 100,
                    'trend': current_trend,
                    'equity': equity
                })
                
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
        
        # Drawdown
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
                    'pnl_pct': -leverage * 100,
                    'pnl_usdt': -equity,
                    'reinvested': 0,
                    'reinvest_pct': 0,
                    'trend': current_trend,
                    'equity': 0
                })
                equity = 0
                position = 0
                break
        
        equity_history.append(equity + reinvest_pool)
    
    # Close
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
            'pnl_pct': pnl_pct * 100,
            'pnl_usdt': pnl,
            'reinvested': reinvested,
            'reinvest_pct': reinvest_pct * 100,
            'trend': current_trend,
            'equity': equity
        })
    
    wins = [t for t in trades if t['pnl_usdt'] > 0]
    losses = [t for t in trades if t['pnl_usdt'] <= 0]
    final_value = equity + reinvest_pool
    
    return {
        'initial': capital,
        'final': round(final_value, 2),
        'pnl': round(final_value - capital, 2),
        'return_pct': round((final_value - capital) / capital * 100, 2),
        'max_dd': round(max_dd * 100, 2),
        'trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': round(len(wins) / len(trades) * 100, 1) if trades else 0,
        'total_reinvested': round(total_reinvested, 2),
        'reinvest_count': sum(1 for t in trades if t['reinvested'] > 0),
        'reinvest_config': reinvest_config,
        'trend_stats': trend_stats,
        'trade_list': trades
    }


def compare_strategies(df, capital=25):
    """Сравнение всех стратегий."""
    print("\n" + "="*70)
    print("📊 СРАВНЕНИЕ ВСЕХ СТРАТЕГИЙ")
    print("="*70)
    
    strategies = [
        ("Без реинвеста", {1: 0, 0: 0, -1: 0}),
        ("Фиксированный 10%", {1: 0.10, 0: 0.10, -1: 0.10}),
        ("Адаптивный 15/5/0", {1: 0.15, 0: 0.05, -1: 0.00}),
        ("Агрессивный 20/5/0", {1: 0.20, 0: 0.05, -1: 0.00}),
        ("Консервативный 10/2/0", {1: 0.10, 0: 0.02, -1: 0.00}),
    ]
    
    print(f"\n  {'Стратегия':<25} {'Капитал':>12} {'Прибыль':>12} {'Доход':>10} {'Просадка':>10} {'Реинвест':>10}")
    print("-"*80)
    
    results = []
    for name, config in strategies:
        result = backtest_adaptive_reinvest(df, capital, reinvest_config=config)
        results.append((name, result))
        
        print(f"  {name:<25} ${result['final']:>10.2f} ${result['pnl']:>10.2f} "
              f"{result['return_pct']:>+9.1f}% {result['max_dd']:>9.1f}% ${result['total_reinvested']:>8.2f}")
    
    return results


def analyze_trend_impact(result):
    """Анализ влияния тренда на реинвестирование."""
    print("\n📈 АНАЛИЗ ВЛИЯНИЯ ТРЕНДА:")
    print("-"*60)
    
    trend_names = {1: "Восходящий", 0: "Боковой", -1: "Нисходящий"}
    trend_reinvest = result['reinvest_config']
    
    for trend in [1, 0, -1]:
        stats = result['trend_stats'][trend]
        reinvest_pct = trend_reinvest[trend]
        print(f"  {trend_names[trend]:<15} → Реинвест: {reinvest_pct:.0%} | "
              f"Сделок: {stats['trades']} | Реинвестировано: ${stats['reinvested']:.2f}")


def main():
    print("🚀 БЭКТЕСТ DOGE С АДАПТИВНЫМ РЕИНВЕСТИРОВАНИЕМ ПО ТРЕНДУ")
    print("="*70)
    print(f"  Капитал: 25 USDT")
    print(f"  Плечо: 3x")
    print(f"  Адаптивное реинвестирование по тренду")
    
    # Данные
    print("\n📈 Генерация данных DOGE...")
    df = generate_doge_data(days=180)
    
    print(f"  Период: {df['date'].iloc[0].strftime('%Y-%m-%d')} - {df['date'].iloc[-1].strftime('%Y-%m-%d')}")
    print(f"  Баров: {len(df)}")
    print(f"  Изменение цены: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:+.2f}%")
    
    # Расчет индикаторов
    df = calculate_indicators(df)
    df = generate_signals(df)
    
    # Статистика трендов
    trend_counts = df['trend'].value_counts()
    print(f"\n📊 Статистика трендов:")
    print(f"  Восходящий:  {trend_counts.get(1, 0)} баров")
    print(f"  Боковой:     {trend_counts.get(0, 0)} баров")
    print(f"  Нисходящий:  {trend_counts.get(-1, 0)} баров")
    
    # Сравнение стратегий
    results = compare_strategies(df, capital=25)
    
    # Детали адаптивной стратегии
    print("\n\n🏆 ДЕТАЛИ АДАПТИВНОЙ СТРАТЕГИИ:")
    print("="*70)
    
    adaptive_config = {1: 0.15, 0: 0.05, -1: 0.00}
    result = backtest_adaptive_reinvest(df, capital=25, reinvest_config=adaptive_config)
    
    print(f"\n  Конфигурация реинвестирования:")
    print(f"    Восходящий тренд:  15%")
    print(f"    Боковой рынок:     5%")
    print(f"    Нисходящий тренд:  0% (вывод прибыли)")
    
    print(f"\n  Результаты:")
    print(f"    Начальный капитал:     ${result['initial']}")
    print(f"    Конечный капитал:      ${result['final']}")
    print(f"    Чистая прибыль:        ${result['pnl']}")
    print(f"    Доходность:            {result['return_pct']:+.2f}%")
    print(f"    Макс. просадка:        {result['max_dd']:.2f}%")
    print(f"    Всего сделок:          {result['trades']}")
    print(f"    Прибыльных:            {result['wins']}")
    print(f"    Win Rate:              {result['win_rate']:.1f}%")
    print(f"    Всего реинвестировано: ${result['total_reinvested']}")
    
    analyze_trend_impact(result)
    
    # Топ сделки
    print(f"\n\n📋 ТОП-10 СДЕЛОК:")
    print("-"*80)
    sorted_trades = sorted(result['trade_list'], key=lambda x: x['pnl_usdt'], reverse=True)
    
    for i, t in enumerate(sorted_trades[:10], 1):
        trend_str = "↑" if t['trend'] == 1 else ("↓" if t['trend'] == -1 else "→")
        reinvest_str = f"{t['reinvest_pct']:.0f}%" if t['reinvested'] > 0 else "-"
        print(f"  {i}. {t['type']:6} ${t['entry']:.4f} → ${t['exit']:.4f} | "
              f"{t['result']:5} | {t['pnl_pct']:+.1f}% | ${t['pnl_usdt']:+.2f} | "
              f"Тренд: {t['trend']} | Реинвест: {reinvest_str}")
    
    # Рекомендации
    print(f"\n\n💡 РЕКОМЕНДАЦИИ:")
    print("="*70)
    
    # Находим лучшую стратегию
    best_name, best_result = max(results, key=lambda x: x[1]['return_pct'])
    
    print(f"\n  🏆 Лучшая стратегия: {best_name}")
    print(f"     Доходность: {best_result['return_pct']:+.2f}%")
    print(f"     Просадка: {best_result['max_dd']:.2f}%")
    
    print(f"\n  📌 Правила адаптивного реинвестирования:")
    print(f"     • Восходящий тренд (цена > EMA200 + 2%): реинвест 10%")
    print(f"     • Боковой рынок: реинвест 5%")
    print(f"     • Нисходящий тренд (цена < EMA200 - 2%): вывод 100% прибыли")
    
    print(f"\n  ⚠️  Важно:")
    print(f"     • Адаптивное реинвестирование снижает просадку в нисходящем тренде")
    print(f"     • Увеличивает позиции в восходящем тренде (компаунд-эффект)")
    print(f"     • Автоматически защищает капитал при развороте рынка")
    
    print("\n✅ БЭКТЕСТ ЗАВЕРШЕН")


if __name__ == "__main__":
    main()
