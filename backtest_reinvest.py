"""
Бэктест DOGE с реинвестированием 10% прибыли.
Консервативные параметры: плечо 3x, трейлинг стоп, EMA фильтр.
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


def backtest_with_reinvest(df, capital=25, leverage=3, risk_pct=0.003,
                           sl_mult=2.5, tp_mult=3, trail_pct=0.015,
                           reinvest_pct=0.10, commission=0.001):
    """
    Бэктест с реинвестированием прибыли.
    
    Реинвестирование работает через увеличение базового капитала:
    - 10% прибыли идут в "пул реинвестирования"
    - Пул увеличивает размер будущих позиций
    - 90% прибыли остаются в equity
    
    Args:
        reinvest_pct: Процент прибыли для реинвестирования (0.10 = 10%)
    """
    position = 0
    entry_price = 0
    sl_price = 0
    tp_price = 0
    trail_price = 0
    
    # Разделяем капитал: equity (текущий) и base_capital (для sizing)
    base_capital = capital  # Увеличивается при реинвестировании
    equity = capital
    peak_equity = capital
    max_dd = 0
    trades = []
    total_reinvested = 0
    reinvest_pool = 0  # Пул реинвестирования
    
    equity_history = [capital]
    
    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        atr = df['atr'].iloc[i]
        signal = df['signal'].iloc[i]
        
        if np.isnan(atr):
            atr = price * 0.02
        
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
                
                # Реинвестирование: 10% прибыли идут в пул
                reinvested = 0
                if pnl > 0:
                    reinvested = pnl * reinvest_pct
                    total_reinvested += reinvested
                    reinvest_pool += reinvested
                    base_capital += reinvested  # Увеличиваем базовый капитал
                    equity += (pnl - reinvested)  # 90% прибыли в equity
                else:
                    equity += pnl
                    # При убытке - уменьшаем пул реинвестирования
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
                    'base_capital': base_capital,
                    'equity': equity
                })
                
                position = 0
                trail_price = 0
        
        # Новая позиция (размер позиции зависит от base_capital)
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
            
            # Комиссия от base_capital (размер позиции)
            comm = abs(base_capital * leverage) * commission
            equity -= comm
        
        # Drawdown
        total_value = equity + reinvest_pool
        peak_equity = max(peak_equity, total_value)
        dd = (peak_equity - total_value) / peak_equity if peak_equity > 0 else 0
        max_dd = max(max_dd, dd)
        
        # Liquidation check
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
                    'base_capital': base_capital,
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
            'base_capital': base_capital,
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
        'final_base_capital': round(base_capital, 2),
        'reinvest_pool': round(reinvest_pool, 2),
        'trade_list': trades,
        'equity_history': equity_history
    }


def compare_reinvest_scenarios(df, capital=25):
    """Сравнение разных процентов реинвестирования."""
    scenarios = [0, 0.05, 0.10, 0.15, 0.20]
    results = []
    
    # Копируем и рассчитываем индикаторы один раз
    df_copy = df.copy()
    df_copy = calculate_indicators(df_copy)
    df_copy = generate_signals(df_copy)
    
    print("\n📊 СРАВНЕНИЕ СЦЕНАРИЕВ РЕИНВЕСТИРОВАНИЯ:")
    print("-"*70)
    print(f"  {'Реинвест%':>10} {'Конечный':>12} {'Прибыль':>12} {'Доходность':>12} {'Просадка':>10}")
    print("-"*70)
    
    for reinvest in scenarios:
        result = backtest_with_reinvest(
            df_copy, capital=capital, leverage=3,
            risk_pct=0.003, sl_mult=2.5, tp_mult=3,
            trail_pct=0.015, reinvest_pct=reinvest
        )
        
        results.append({
            'reinvest_pct': reinvest,
            'final': result['final'],
            'pnl': result['pnl'],
            'return_pct': result['return_pct'],
            'max_dd': result['max_dd'],
            'reinvested': result['total_reinvested']
        })
        
        reinvest_str = f"{reinvest:.0%}" if reinvest > 0 else "Нет"
        print(f"  {reinvest_str:>10} ${result['final']:>10.2f} ${result['pnl']:>10.2f} {result['return_pct']:>+11.2f}% {result['max_dd']:>9.2f}%")
    
    return results


def main():
    print("🚀 БЭКТЕСТ DOGE С РЕИНВЕСТИРОВАНИЕМ 10%")
    print("="*60)
    print(f"  Капитал: 25 USDT")
    print(f"  Плечо: 3x")
    print(f"  Реинвестирование: 10% прибыли")
    print(f"  Инструмент: DOGEUSD_PERP")
    
    # Данные
    print("\n📈 Генерация данных DOGE...")
    df = generate_doge_data(days=180)
    
    print(f"  Период: {df['date'].iloc[0].strftime('%Y-%m-%d')} - {df['date'].iloc[-1].strftime('%Y-%m-%d')}")
    print(f"  Баров: {len(df)}")
    print(f"  Изменение цены: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:+.2f}%")
    
    # Расчет индикаторов
    df = calculate_indicators(df)
    df = generate_signals(df)
    
    # Бэктест с 10% реинвестированием
    print("\n🎯 БЭКТЕСТ С РЕИНВЕСТИРОВАНИЕМ 10%:")
    print("="*60)
    
    result_10 = backtest_with_reinvest(
        df, capital=25, leverage=3,
        risk_pct=0.003, sl_mult=2.5, tp_mult=3,
        trail_pct=0.015, reinvest_pct=0.10
    )
    
    print(f"\n🏆 РЕЗУЛЬТАТЫ (10% реинвестирование):")
    print(f"  Начальный капитал:     ${result_10['initial']}")
    print(f"  Конечный капитал:      ${result_10['final']}")
    print(f"  Чистая прибыль:        ${result_10['pnl']}")
    print(f"  Доходность:            {result_10['return_pct']:+.2f}%")
    print(f"  Макс. просадка:        {result_10['max_dd']:.2f}%")
    print(f"  Всего сделок:          {result_10['trades']}")
    print(f"  Прибыльных:            {result_10['wins']}")
    print(f"  Win Rate:              {result_10['win_rate']:.1f}%")
    print(f"  Всего реинвестировано: ${result_10['total_reinvested']}")
    print(f"  Сделок с реинвестом:   {result_10['reinvest_count']}")
    
    # Сравнение без реинвестирования
    result_0 = backtest_with_reinvest(
        df, capital=25, leverage=3,
        risk_pct=0.003, sl_mult=2.5, tp_mult=3,
        trail_pct=0.015, reinvest_pct=0
    )
    
    print(f"\n\n📊 СРАВНЕНИЕ С БЕЗ РЕИНВЕСТИРОВАНИЯ:")
    print("-"*60)
    print(f"  {'Метрика':<25} {'Без реинвеста':>15} {'С реинвестом':>15}")
    print(f"  {'Конечный капитал':<25} ${result_0['final']:>13.2f} ${result_10['final']:>13.2f}")
    print(f"  {'Прибыль':<25} ${result_0['pnl']:>13.2f} ${result_10['pnl']:>13.2f}")
    print(f"  {'Доходность':<25} {result_0['return_pct']:>+14.2f}% {result_10['return_pct']:>+14.2f}%")
    print(f"  {'Просадка':<25} {result_0['max_dd']:>14.2f}% {result_10['max_dd']:>14.2f}%")
    
    # Дополнительная прибыль от реинвестирования
    extra_profit = result_10['pnl'] - result_0['pnl']
    print(f"\n  💰 Дополнительная прибыль от реинвестирования: ${extra_profit:.2f}")
    
    # Сравнение разных процентов
    compare_reinvest_scenarios(df, capital=25)
    
    # Детали сделок с реинвестированием
    print(f"\n\n📋 СДЕЛКИ С РЕИНВЕСТИРОВАНИЕМ:")
    print("-"*80)
    print(f"  {'#':>3} {'Тип':>6} {'Вход':>10} {'Выход':>10} {'Рез':>5} {'PnL%':>8} {'PnL$':>10} {'Реинвест':>10}")
    print("-"*80)
    
    for i, t in enumerate(result_10['trade_list'], 1):
        reinvest_str = f"${t['reinvested']:.2f}" if t['reinvested'] > 0 else "-"
        print(f"  {i:>3} {t['type']:>6} ${t['entry']:.4f} ${t['exit']:.4f} {t['result']:>5} {t['pnl_pct']:>+7.1f}% ${t['pnl_usdt']:>+9.2f} {reinvest_str:>10}")
    
    # Рекомендации
    print(f"\n\n💡 РЕКОМЕНДАЦИИ ПО РЕИНВЕСТИРОВАНИЮ:")
    print("-"*60)
    
    if result_10['return_pct'] > result_0['return_pct']:
        print(f"  ✓ Реинвестирование 10% увеличивает доходность на {result_10['return_pct'] - result_0['return_pct']:.2f}%")
        print(f"  ✓ Дополнительная прибыль: ${extra_profit:.2f}")
        print(f"  ✓ Компаунд-эффект работает")
    else:
        print(f"  ⚠ Реинвестирование не дало преимущества в текущих условиях")
    
    print(f"\n  📌 Оптимальные параметры:")
    print(f"     - Реинвестирование: 10% прибыли")
    print(f"     - Плечо: 3x")
    print(f"     - Risk: 0.3%")
    print(f"     - Stop Loss: 2.5x ATR")
    print(f"     - Take Profit: 3x ATR")
    print(f"     - Trail Stop: 1.5%")
    
    print("\n✅ БЭКТЕСТ ЗАВЕРШЕН")


if __name__ == "__main__":
    main()
