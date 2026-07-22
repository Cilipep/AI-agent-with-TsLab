"""
Бэктест DOGE с загрузкой конфигурации из JSON файла.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime


def load_config(config_path):
    """Загрузка конфигурации из JSON."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


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


def calculate_indicators(df, config):
    """Расчет индикаторов из конфига."""
    ind = config['entry']['indicators']
    c = df['close']
    
    df['sma_fast'] = c.rolling(ind['sma_fast']['period']).mean()
    df['sma_slow'] = c.rolling(ind['sma_slow']['period']).mean()
    df['ema_trend'] = c.ewm(span=ind['ema_trend']['period'], adjust=False).mean()
    
    tr = pd.concat([df['high'] - df['low'], 
                    abs(df['high'] - c.shift(1)), 
                    abs(df['low'] - c.shift(1))], axis=1).max(axis=1)
    df['atr'] = tr.rolling(ind['atr']['period']).mean()
    
    delta = c.diff()
    gain = delta.where(delta > 0, 0).rolling(ind['rsi']['period']).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(ind['rsi']['period']).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss))
    
    # Тренд из конфига
    trend = config['trend_detection']
    df['trend'] = 0
    df.loc[c > df['ema_trend'] * trend['uptrend_threshold'], 'trend'] = 1
    df.loc[c < df['ema_trend'] * trend['downtrend_threshold'], 'trend'] = -1
    
    return df


def generate_signals(df, config):
    """Генерация сигналов из конфига."""
    df['signal'] = 0
    rsi = config['entry']['indicators']['rsi']
    uptrend = df['close'] > df['ema_trend']
    downtrend = df['close'] < df['ema_trend']
    
    df.loc[
        (df['sma_fast'] > df['sma_slow']) & 
        (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1)) &
        (df['rsi'] < rsi['overbought']) & uptrend, 'signal'
    ] = 1
    
    df.loc[
        (df['sma_fast'] < df['sma_slow']) & 
        (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1)) &
        (df['rsi'] > rsi['oversold']) & downtrend, 'signal'
    ] = -1
    
    return df


def backtest_from_config(df, config):
    """Бэктест с параметрами из конфига."""
    # Извлечение параметров
    capital = config['capital']['initial']
    leverage = config['capital']['leverage']
    risk_pct = config['risk_management']['position_sizing']['risk_per_trade_pct'] / 100
    sl_mult = config['risk_management']['stop_loss']['atr_multiplier']
    tp_mult = config['risk_management']['take_profit']['atr_multiplier']
    trail_pct = config['risk_management']['trailing_stop']['trail_pct'] / 100
    commission = config['commission']['rate_pct'] / 100
    
    reinvest_config = {}
    for trend, params in config['reinvestment']['rules'].items():
        if trend == 'uptrend':
            reinvest_config[1] = params['reinvest_pct'] / 100
        elif trend == 'sideways':
            reinvest_config[0] = params['reinvest_pct'] / 100
        elif trend == 'downtrend':
            reinvest_config[-1] = params['reinvest_pct'] / 100
    
    # Переменные
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
        'initial': capital,
        'final': round(final_value, 2),
        'pnl': round(final_value - capital, 2),
        'return_pct': round((final_value - capital) / capital * 100, 2),
        'max_dd': round(max_dd * 100, 2),
        'trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': round(len(wins) / len(trades) * 100, 1) if trades else 0,
        'profit_factor': round(abs(sum(t['pnl_usdt'] for t in wins) / 
                                   sum(t['pnl_usdt'] for t in losses)), 2) if losses else float('inf'),
        'total_reinvested': round(total_reinvested, 2),
        'reinvest_pool': round(reinvest_pool, 2),
        'base_capital': round(base_capital, 2),
        'trend_stats': {k: {'trades': v['trades'], 'reinvested': round(v['reinvested'], 2), 'pnl': round(v['pnl'], 2)} for k, v in trend_stats.items()},
        'trades': trades
    }


def main():
    # Загрузка конфига
    config_path = "./strategy_config.json"
    config = load_config(config_path)
    
    print("🚀 БЭКТЕСТ DOGE ИЗ КОНФИГА")
    print("="*70)
    
    # Вывод конфига
    print(f"\n📋 КОНФИГУРАЦИЯ (из {config_path}):")
    print("-"*70)
    print(f"  Стратегия:     {config['strategy']['name']}")
    print(f"  Инструмент:    {config['instrument']['symbol']}")
    print(f"  Интервал:      {config['instrument']['interval']}")
    print(f"  Капитал:       {config['capital']['initial']} {config['capital']['currency']}")
    print(f"  Плечо:         {config['capital']['leverage']}x")
    print(f"  Risk:          {config['risk_management']['position_sizing']['risk_per_trade_pct']}%")
    print(f"  Stop Loss:     {config['risk_management']['stop_loss']['atr_multiplier']}x ATR")
    print(f"  Take Profit:   {config['risk_management']['take_profit']['atr_multiplier']}x ATR")
    print(f"  Trail Stop:    {config['risk_management']['trailing_stop']['trail_pct']}%")
    
    print(f"\n  Реинвестирование:")
    for trend, params in config['reinvestment']['rules'].items():
        print(f"    {trend:<12} → {params['reinvest_pct']}%")
    
    # Данные
    df = generate_doge_data(days=config['backtest_results']['days'])
    df = calculate_indicators(df, config)
    df = generate_signals(df, config)
    
    print(f"\n📈 ДАННЫЕ:")
    print("-"*70)
    print(f"  Период:    {df['date'].iloc[0].strftime('%Y-%m-%d')} - {df['date'].iloc[-1].strftime('%Y-%m-%d')}")
    print(f"  Баров:     {len(df)}")
    print(f"  Изменение: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:+.2f}%")
    
    # Бэктест
    result = backtest_from_config(df, config)
    
    print(f"\n🎯 РЕЗУЛЬТАТЫ:")
    print("="*70)
    print(f"  Начальный капитал:     ${result['initial']}")
    print(f"  Конечный капитал:      ${result['final']}")
    print(f"  Чистая прибыль:        ${result['pnl']}")
    print(f"  Доходность:            {result['return_pct']:+.2f}%")
    print(f"  Макс. просадка:        {result['max_dd']:.2f}%")
    print(f"  Profit Factor:         {result['profit_factor']}")
    
    print(f"\n📊 СДЕЛКИ:")
    print("-"*70)
    print(f"  Всего:          {result['trades']}")
    print(f"  Прибыльных:     {result['wins']}")
    print(f"  Убыточных:      {result['losses']}")
    print(f"  Win Rate:       {result['win_rate']:.1f}%")
    
    print(f"\n💰 РЕИНВЕСТИРОВАНИЕ:")
    print("-"*70)
    print(f"  Реинвестировано: ${result['total_reinvested']}")
    print(f"  Пул:             ${result['reinvest_pool']}")
    print(f"  Базовый капитал: ${result['base_capital']}")
    
    print(f"\n📈 ПО ТРЕНДАМ:")
    print("-"*70)
    trend_names = {1: "Восходящий", 0: "Боковой", -1: "Нисходящий"}
    reinvest_pcts = {1: config['reinvestment']['rules']['uptrend']['reinvest_pct'],
                     0: config['reinvestment']['rules']['sideways']['reinvest_pct'],
                     -1: config['reinvestment']['rules']['downtrend']['reinvest_pct']}
    
    for trend in [1, 0, -1]:
        stats = result['trend_stats'][trend]
        print(f"  {trend_names[trend]:<15} ({reinvest_pcts[trend]:>2}%) → Сделок: {stats['trades']:>3} | "
              f"Реинвест: ${stats['reinvested']:>6.2f} | PnL: ${stats['pnl']:>+8.2f}")
    
    # Топ сделки
    print(f"\n📋 ТОП-10 СДЕЛОК:")
    print("-"*100)
    sorted_trades = sorted(result['trades'], key=lambda x: x['pnl_usdt'], reverse=True)
    
    for i, t in enumerate(sorted_trades[:10], 1):
        trend_str = "↑" if t['trend'] == 1 else ("↓" if t['trend'] == -1 else "→")
        reinvest_str = f"{t['reinvest_pct']:.0f}%" if t['reinvested'] > 0 else "-"
        print(f"  {i:>3}. {t['type']:6} ${t['entry']:.4f} → ${t['exit']:.4f} | "
              f"{t['result']:5} | {t['pnl_pct']:>+7.1f}% | ${t['pnl_usdt']:>+8.2f} | "
              f"Реинвест: {reinvest_str:>4} | {trend_str}")
    
    print(f"\n✅ БЭКТЕСТ ЗАВЕРШЕН")
    print(f"📄 Конфиг: {config_path}")
    
    return result


if __name__ == "__main__":
    main()
