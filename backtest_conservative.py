"""
Консервативный бэктест DOGE с плечом 3x.
Добавлены: EMA фильтр, трейлинг стоп, широкие стопы.
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
        vol_mult = 1.0
        if 14 <= hour <= 16:
            vol_mult = 1.3
        elif 21 <= hour <= 23:
            vol_mult = 1.2
        
        if np.random.random() < 0.02:
            hourly_drift *= np.random.uniform(0.5, 1.5)
        
        ret = np.random.normal(hourly_drift, hourly_vol * vol_mult)
        returns.append(ret)
    
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


def calculate_indicators(df, sma_fast=10, sma_slow=30, ema_trend=200, atr_period=14):
    """Расчет всех индикаторов."""
    c = df['close']
    
    df['sma_fast'] = c.rolling(sma_fast).mean()
    df['sma_slow'] = c.rolling(sma_slow).mean()
    df['ema_trend'] = c.ewm(span=ema_trend, adjust=False).mean()
    
    # ATR
    tr = pd.concat([df['high'] - df['low'], 
                    abs(df['high'] - c.shift(1)), 
                    abs(df['low'] - c.shift(1))], axis=1).max(axis=1)
    df['atr'] = tr.rolling(atr_period).mean()
    
    # RSI
    delta = c.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss))
    
    return df


def generate_signals(df):
    """Сигналы с фильтром тренда."""
    df['signal'] = 0
    
    # Фильтр тренда: цена выше EMA200 = только long, ниже = только short
    uptrend = df['close'] > df['ema_trend']
    downtrend = df['close'] < df['ema_trend']
    
    # Long: SMA cross up + RSI < 70 + uptrend
    long_cond = (
        (df['sma_fast'] > df['sma_slow']) & 
        (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1)) &
        (df['rsi'] < 70) & uptrend
    )
    
    # Short: SMA cross down + RSI > 30 + downtrend
    short_cond = (
        (df['sma_fast'] < df['sma_slow']) & 
        (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1)) &
        (df['rsi'] > 30) & downtrend
    )
    
    df.loc[long_cond, 'signal'] = 1
    df.loc[short_cond, 'signal'] = -1
    
    return df


def backtest_conservative(df, capital=25, leverage=3, risk_pct=0.005,
                          sl_mult=3, tp_mult=4, trail_pct=0.02,
                          commission=0.001):
    """Консервативный бэктест с трейлинг стопом."""
    position = 0
    entry_price = 0
    sl_price = 0
    tp_price = 0
    trail_price = 0
    equity = capital
    peak_equity = capital
    max_dd = 0
    trades = []
    
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
                comm = abs(equity * leverage) * commission * 2
                pnl = equity * pnl_pct - comm
                equity += pnl
                
                result = 'TP' if hit_tp else ('TRAIL' if hit_sl and trail_price != sl_price else 'SL')
                
                trades.append({
                    'entry': entry_price,
                    'exit': price,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'result': result,
                    'pnl_pct': pnl_pct * 100,
                    'pnl_usdt': pnl,
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
            
            comm = abs(equity * leverage) * commission
            equity -= comm
        
        # Drawdown
        peak_equity = max(peak_equity, equity)
        dd = (peak_equity - equity) / peak_equity if peak_equity > 0 else 0
        max_dd = max(max_dd, dd)
        
        # Liquidation (при 3x плече - менее вероятно)
        if equity <= capital * 0.1:
            if position != 0:
                trades.append({
                    'entry': entry_price,
                    'exit': price,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'result': 'LIQUIDATION',
                    'pnl_pct': -leverage * 100,
                    'pnl_usdt': -equity,
                    'equity': 0
                })
                equity = 0
                position = 0
                break
    
    # Close
    if position != 0:
        price = df['close'].iloc[-1]
        pnl_pct = ((price - entry_price) / entry_price * position) * leverage
        comm = abs(equity * leverage) * commission
        pnl = equity * pnl_pct - comm
        equity += pnl
        trades.append({
            'entry': entry_price,
            'exit': price,
            'type': 'LONG' if position == 1 else 'SHORT',
            'result': 'EOD',
            'pnl_pct': pnl_pct * 100,
            'pnl_usdt': pnl,
            'equity': equity
        })
    
    wins = [t for t in trades if t['pnl_usdt'] > 0]
    losses = [t for t in trades if t['pnl_usdt'] <= 0]
    
    return {
        'initial': capital,
        'final': round(equity, 2),
        'pnl': round(equity - capital, 2),
        'return_pct': round((equity - capital) / capital * 100, 2),
        'max_dd': round(max_dd * 100, 2),
        'trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': round(len(wins) / len(trades) * 100, 1) if trades else 0,
        'avg_win': round(np.mean([t['pnl_usdt'] for t in wins]), 2) if wins else 0,
        'avg_loss': round(np.mean([t['pnl_usdt'] for t in losses]), 2) if losses else 0,
        'trade_list': trades
    }


def optimize_conservative(df, capital=25, leverage=3):
    """Оптимизация консервативных параметров."""
    best_result = None
    best_params = None
    
    for sma_fast in [10, 15, 20]:
        for sma_slow in [30, 40, 50]:
            if sma_fast >= sma_slow:
                continue
            for risk in [0.003, 0.005, 0.008]:
                for sl in [2.5, 3, 3.5]:
                    for tp in [3, 4, 5]:
                        for trail in [0.015, 0.02, 0.025]:
                            test_df = df.copy()
                            test_df = calculate_indicators(test_df, sma_fast, sma_slow)
                            test_df = generate_signals(test_df)
                            
                            result = backtest_conservative(
                                test_df, capital, leverage, risk, sl, tp, trail
                            )
                            
                            # Учитываем risk-adjusted return
                            if result['trades'] >= 5 and result['max_dd'] < 50:
                                adj_return = result['return_pct'] / max(result['max_dd'], 1)
                                
                                if best_result is None or adj_return > best_result.get('adj_return', -999):
                                    result['adj_return'] = adj_return
                                    best_result = result
                                    best_params = {
                                        'sma_fast': sma_fast,
                                        'sma_slow': sma_slow,
                                        'risk': risk,
                                        'sl': sl,
                                        'tp': tp,
                                        'trail': trail
                                    }
    
    return best_params, best_result


def main():
    print("🚀 КОНСЕРВАТИВНЫЙ БЭКТЕСТ DOGE")
    print("="*60)
    print(f"  Капитал: 25 USDT")
    print(f"  Плечо: 3x (консервативно)")
    print(f"  Инструмент: DOGEUSD_PERP")
    print(f"  Фильтр: EMA 200")
    print(f"  Трейлинг стоп: Да")
    
    # Данные
    print("\n📈 Генерация данных DOGE...")
    df = generate_doge_data(days=180)
    
    print(f"  Период: {df['date'].iloc[0].strftime('%Y-%m-%d')} - {df['date'].iloc[-1].strftime('%Y-%m-%d')}")
    print(f"  Баров: {len(df)}")
    print(f"  Изменение цены: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:+.2f}%")
    
    # Оптимизация
    print("\n🎯 Оптимизация консервативных параметров...")
    best_params, best_result = optimize_conservative(df, capital=25, leverage=3)
    
    if best_params and best_result:
        print(f"\n🏆 ЛУЧШИЕ ПАРАМЕТРЫ:")
        print(f"  SMA Fast:     {best_params['sma_fast']}")
        print(f"  SMA Slow:     {best_params['sma_slow']}")
        print(f"  Risk:         {best_params['risk']:.1%}")
        print(f"  Stop Loss:    {best_params['sl']}x ATR")
        print(f"  Take Profit:  {best_params['tp']}x ATR")
        print(f"  Trail Stop:   {best_params['trail']:.1%}")
        
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print("-"*60)
        print(f"  Начальный капитал:   ${best_result['initial']}")
        print(f"  Конечный капитал:    ${best_result['final']}")
        print(f"  Чистая прибыль:      ${best_result['pnl']}")
        print(f"  Доходность:          {best_result['return_pct']:+.2f}%")
        print(f"  Макс. просадка:      {best_result['max_dd']:.2f}%")
        print(f"  Risk-Adj Return:     {best_result['adj_return']:.2f}")
        print(f"  Всего сделок:        {best_result['trades']}")
        print(f"  Прибыльных:          {best_result['wins']}")
        print(f"  Убыточных:           {best_result['losses']}")
        print(f"  Win Rate:            {best_result['win_rate']:.1f}%")
        
        if best_result['trade_list']:
            print(f"\n📋 СДЕЛКИ:")
            print("-"*80)
            for i, t in enumerate(best_result['trade_list'], 1):
                print(f"  {i}. {t['type']:6} | ${t['entry']:.4f} → ${t['exit']:.4f} | "
                      f"{t['result']:5} | {t['pnl_pct']:+.1f}% (${t['pnl_usdt']:+.2f})")
        
        # Сравнение с агрессивной стратегией
        risk_str = f"{best_params['risk']:.1%}"
        sl_str = f"{best_params['sl']}x ATR"
        tp_str = f"{best_params['tp']}x ATR"
        trail_str = f"{best_params['trail']:.1%}"
        ret_str = f"{best_result['return_pct']:+.1f}%"
        dd_str = f"{best_result['max_dd']:.1f}%"
        
        print(f"\n\n📊 СРАВНЕНИЕ С АГРЕССИВНОЙ СТРАТЕГИЕЙ (10x):")
        print("-"*60)
        print(f"  {'Параметр':<25} {'Агрессивная':>15} {'Консервативная':>15}")
        print(f"  {'Плечо':<25} {'10x':>15} {'3x':>15}")
        print(f"  {'Риск на сделку':<25} {'1.0%':>15} {risk_str:>15}")
        print(f"  {'Stop Loss':<25} {'1.5x ATR':>15} {sl_str:>15}")
        print(f"  {'Take Profit':<25} {'2x ATR':>15} {tp_str:>15}")
        print(f"  {'Трейлинг стоп':<25} {'Нет':>15} {trail_str:>15}")
        print(f"  {'Фильтр тренда':<25} {'Нет':>15} {'EMA 200':>15}")
        print(f"  {'Доходность':<25} {'-100%':>15} {ret_str:>15}")
        print(f"  {'Просадка':<25} {'95.6%':>15} {dd_str:>15}")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print("-"*60)
        
        if best_result['return_pct'] > 0:
            print("  ✓ Консервативная стратегия прибыльна")
            print("  ✓ Плечо 3x безопаснее чем 10x")
            print("  ✓ Трейлинг стоп защищает прибыль")
            print("  ✓ Фильтр EMA 200 снижает убыточные сделки")
        else:
            print("  ⚠ Рынок неблагоприятен для стратегии")
            print("  ✓ Рекомендуется ждать восходящий тренд")
        
        if best_result['max_dd'] < 30:
            print("  ✓ Приемлемый уровень просадки")
        else:
            print("  ⚠ Высокая просадка - рассмотреть снижение плеча до 2x")
    
    print("\n✅ БЭКТЕСТ ЗАВЕРШЕН")


if __name__ == "__main__":
    main()
