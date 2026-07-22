"""
Оптимизированный бэктест с кредитным плечём 10x и капиталом 25 USDT.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json


def generate_crypto_data(n_days=180, n_assets=5):
    np.random.seed(42)
    assets = ['BTC', 'ETH', 'SOL', 'DOGE', 'ADA'][:n_assets]
    data = {}
    vols = [0.025, 0.035, 0.045, 0.06, 0.04]
    drifts = [0.0008, 0.0005, 0.0012, 0.0004, 0.0006]
    
    for i, asset in enumerate(assets):
        returns = np.random.normal(drifts[i], vols[i], n_days)
        prices = 100 * np.cumprod(1 + returns)
        data[f'{asset}USDT'] = prices
    
    dates = pd.date_range(start='2024-06-01', periods=n_days, freq='D')
    return pd.DataFrame(data, index=dates)


def calculate_atr(prices, period=14):
    high = prices.rolling(period).max()
    low = prices.rolling(period).min()
    close = prices
    tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def calculate_indicators(prices, sma_fast=10, sma_slow=30, atr_period=14):
    sma_f = prices.rolling(sma_fast).mean()
    sma_s = prices.rolling(sma_slow).mean()
    atr = calculate_atr(prices, atr_period)
    rsi = calculate_rsi(prices, 14)
    return sma_f, sma_s, atr, rsi


def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def generate_signals(prices, sma_fast=10, sma_slow=30, rsi_period=14):
    sma_f, sma_s, atr, rsi = calculate_indicators(prices, sma_fast, sma_slow)
    
    signals = pd.Series(0, index=prices.index)
    
    # Long: SMA cross up + RSI not overbought
    long_cond = (sma_f > sma_s) & (sma_f.shift(1) <= sma_s.shift(1)) & (rsi < 70)
    # Short: SMA cross down + RSI not oversold
    short_cond = (sma_f < sma_s) & (sma_f.shift(1) >= sma_s.shift(1)) & (rsi > 30)
    
    signals[long_cond] = 1
    signals[short_cond] = -1
    
    return signals, atr, rsi


def backtest_leveraged(prices, signals, atr, capital=25, leverage=10, 
                       risk_pct=0.02, sl_atr_mult=2, tp_atr_mult=3,
                       commission_pct=0.001):
    """
    Бэктест с кредитным плечём.
    
    Args:
        prices: Цена актива
        signals: Сигналы (1=long, -1=short, 0=flat)
        atr: ATR для расчёта стопов
        capital: Начальный капитал (USDT)
        leverage: Кредитное плечё
        risk_pct: Риск на сделку (% от капитала)
        sl_atr_mult: Множитель ATR для Stop Loss
        tp_atr_mult: Множитель ATR для Take Profit
        commission_pct: Комиссия (% от объема)
    """
    position = 0
    entry_price = 0
    sl_price = 0
    tp_price = 0
    equity = capital
    peak_equity = capital
    max_drawdown = 0
    trades = []
    
    for i in range(1, len(prices)):
        price = prices.iloc[i]
        prev_price = prices.iloc[i-1]
        signal = signals.iloc[i]
        current_atr = atr.iloc[i] if not np.isnan(atr.iloc[i]) else 1
        
        # Проверка стопов если есть позиция
        if position != 0:
            hit_sl = False
            hit_tp = False
            
            if position == 1:  # Long
                hit_sl = price <= sl_price
                hit_tp = price >= tp_price
            else:  # Short
                hit_sl = price >= sl_price
                hit_tp = price <= tp_price
            
            if hit_sl or hit_tp:
                # Закрытие позиции
                if position == 1:
                    pnl_pct = (price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - price) / entry_price
                
                # Учет плеча
                pnl_pct *= leverage
                
                # Комиссия
                commission = abs(leverage * equity) * commission_pct * 2  # вход + выход
                
                pnl = equity * pnl_pct - commission
                equity += pnl
                
                trades.append({
                    'entry': entry_price,
                    'exit': price,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'result': 'TP' if hit_tp else 'SL',
                    'pnl_pct': pnl_pct,
                    'pnl_usdt': pnl,
                    'equity': equity
                })
                
                position = 0
                entry_price = 0
        
        # Новая позиция
        if position == 0 and signal != 0:
            # Размер позиции с учетом плеча
            position_value = equity * leverage
            risk_amount = equity * risk_pct
            
            # Стоп на основе ATR
            sl_distance = current_atr * sl_atr_mult
            tp_distance = current_atr * tp_atr_mult
            
            if signal == 1:  # Long
                position = 1
                entry_price = price
                sl_price = price - sl_distance
                tp_price = price + tp_distance
            else:  # Short
                position = -1
                entry_price = price
                sl_price = price + sl_distance
                tp_price = price - tp_distance
            
            # Комиссия на вход
            commission = position_value * commission_pct
            equity -= commission
        
        # Обновление drawdown
        if equity > peak_equity:
            peak_equity = equity
        
        if peak_equity > 0:
            dd = (peak_equity - equity) / peak_equity
            if dd > max_drawdown:
                max_drawdown = dd
        
        # Проверка маржин колла
        if equity <= capital * 0.1:  # 10% от начального капитала
            if position != 0:
                trades.append({
                    'entry': entry_price,
                    'exit': price,
                    'type': 'LONG' if position == 1 else 'SHORT',
                    'result': 'LIQUIDATION',
                    'pnl_pct': -leverage,
                    'pnl_usdt': -equity,
                    'equity': 0
                })
                equity = 0
                position = 0
                break
    
    # Закрытие открытой позиции
    if position != 0:
        price = prices.iloc[-1]
        if position == 1:
            pnl_pct = (price - entry_price) / entry_price * leverage
        else:
            pnl_pct = (entry_price - price) / entry_price * leverage
        
        commission = abs(leverage * equity) * commission_pct
        pnl = equity * pnl_pct - commission
        equity += pnl
        
        trades.append({
            'entry': entry_price,
            'exit': price,
            'type': 'LONG' if position == 1 else 'SHORT',
            'result': 'EOD',
            'pnl_pct': pnl_pct,
            'pnl_usdt': pnl,
            'equity': equity
        })
    
    # Статистика
    winning_trades = [t for t in trades if t['pnl_usdt'] > 0]
    losing_trades = [t for t in trades if t['pnl_usdt'] <= 0]
    
    total_pnl = sum(t['pnl_usdt'] for t in trades)
    total_return = (equity - capital) / capital * 100
    
    stats = {
        'initial_capital': capital,
        'final_equity': round(equity, 2),
        'total_pnl': round(total_pnl, 2),
        'total_return_pct': round(total_return, 2),
        'leverage': leverage,
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': round(len(winning_trades) / len(trades) * 100, 2) if trades else 0,
        'max_drawdown_pct': round(max_drawdown * 100, 2),
        'avg_win': round(np.mean([t['pnl_usdt'] for t in winning_trades]), 2) if winning_trades else 0,
        'avg_loss': round(np.mean([t['pnl_usdt'] for t in losing_trades]), 2) if losing_trades else 0,
        'profit_factor': round(abs(sum(t['pnl_usdt'] for t in winning_trades) / 
                                   sum(t['pnl_usdt'] for t in losing_trades)), 2) if losing_trades else float('inf'),
        'trades': trades
    }
    
    return stats


def optimize_parameters(prices_df, capital=25, leverage=10):
    """Оптимизация параметров стратегии."""
    print("\n🎯 ОПТИМИЗАЦИЯ ПАРАМЕТРОВ")
    print("="*60)
    
    # Сетка параметров
    param_grid = {
        'sma_fast': [5, 10, 15],
        'sma_slow': [20, 30, 40],
        'risk_pct': [0.01, 0.02, 0.03],
        'sl_atr_mult': [1.5, 2, 2.5],
        'tp_atr_mult': [2, 3, 4]
    }
    
    results = []
    total = np.prod([len(v) for v in param_grid.values()])
    
    print(f"\nВсего комбинаций: {total}")
    
    idx = 0
    for sma_fast in param_grid['sma_fast']:
        for sma_slow in param_grid['sma_slow']:
            if sma_fast >= sma_slow:
                continue
            
            for risk_pct in param_grid['risk_pct']:
                for sl_mult in param_grid['sl_atr_mult']:
                    for tp_mult in param_grid['tp_atr_mult']:
                        idx += 1
                        
                        if idx % 50 == 0:
                            print(f"  Прогресс: {idx}/{total}")
                        
                        for asset in prices_df.columns:
                            prices = prices_df[asset]
                            signals, atr, _ = generate_signals(prices, sma_fast, sma_slow)
                            
                            stats = backtest_leveraged(
                                prices, signals, atr,
                                capital=capital, leverage=leverage,
                                risk_pct=risk_pct,
                                sl_atr_mult=sl_mult,
                                tp_atr_mult=tp_mult
                            )
                            
                            results.append({
                                'asset': asset,
                                'sma_fast': sma_fast,
                                'sma_slow': sma_slow,
                                'risk_pct': risk_pct,
                                'sl_mult': sl_mult,
                                'tp_mult': tp_mult,
                                'return_pct': stats['total_return_pct'],
                                'max_dd': stats['max_drawdown_pct'],
                                'win_rate': stats['win_rate'],
                                'trades': stats['total_trades'],
                                'final_equity': stats['final_equity']
                            })
    
    # Сортировка по доходности
    results.sort(key=lambda x: x['return_pct'], reverse=True)
    
    print("\nТОП-10 ЛУЧШИХ КОМБИНАЦИЙ:")
    print("-"*80)
    print(f"{'Asset':<12} {'Fast':>5} {'Slow':>5} {'Risk':>6} {'SL':>4} {'TP':>4} {'Return%':>10} {'MaxDD%':>8} {'WR%':>6} {'Trades':>7}")
    print("-"*80)
    
    for r in results[:10]:
        print(f"{r['asset']:<12} {r['sma_fast']:>5} {r['sma_slow']:>5} {r['risk_pct']:>6.1%} {r['sl_mult']:>4.1f} {r['tp_mult']:>4.1f} {r['return_pct']:>+10.2f} {r['max_dd']:>8.2f} {r['win_rate']:>6.1f} {r['trades']:>7}")
    
    return results


def main():
    print("🚀 ОПТИМИЗИРОВАННЫЙ БЭКТЕСТ С ПЛЕЧОМ 10x")
    print("="*60)
    print(f"  Капитал: 25 USDT")
    print(f"  Плечо: 10x")
    print(f"  Объем позиции: 250 USDT")
    
    # Генерация данных
    print("\n📈 Генерация данных...")
    prices_df = generate_crypto_data(n_days=180, n_assets=5)
    print(f"  Период: {prices_df.index[0].date()} - {prices_df.index[-1].date()}")
    
    # Оптимизация
    opt_results = optimize_parameters(prices_df, capital=25, leverage=10)
    
    # Лучшие параметры
    best = opt_results[0]
    print(f"\n\n🏆 ЛУЧШИЕ ПАРАМЕТРЫ:")
    print(f"  Актив:    {best['asset']}")
    print(f"  SMA Fast: {best['sma_fast']}")
    print(f"  SMA Slow: {best['sma_slow']}")
    print(f"  Risk:     {best['risk_pct']:.1%}")
    print(f"  SL:       {best['sl_mult']}x ATR")
    print(f"  TP:       {best['tp_mult']}x ATR")
    
    # Финальный бэктест с лучшими параметрами
    print("\n\n📊 ФИНАЛЬНЫЙ БЭКТЕСТ:")
    print("-"*60)
    
    prices = prices_df[best['asset']]
    signals, atr, rsi = generate_signals(prices, best['sma_fast'], best['sma_slow'])
    
    final_stats = backtest_leveraged(
        prices, signals, atr,
        capital=25, leverage=10,
        risk_pct=best['risk_pct'],
        sl_atr_mult=best['sl_mult'],
        tp_atr_mult=best['tp_mult']
    )
    
    print(f"\n  Начальный капитал:   ${final_stats['initial_capital']}")
    print(f"  Конечный капитал:    ${final_stats['final_equity']}")
    print(f"  Чистая прибыль:      ${final_stats['total_pnl']}")
    print(f"  Доходность:          {final_stats['total_return_pct']:+.2f}%")
    print(f"  Макс. просадка:      {final_stats['max_drawdown_pct']:.2f}%")
    print(f"  Всего сделок:        {final_stats['total_trades']}")
    print(f"  Прибыльных:          {final_stats['winning_trades']}")
    print(f"  Убыточных:           {final_stats['losing_trades']}")
    print(f"  Win Rate:            {final_stats['win_rate']:.1f}%")
    print(f"  Profit Factor:       {final_stats['profit_factor']}")
    
    # Детали сделок
    if final_stats['trades']:
        print("\n\n📋 ДЕТАЛИ СДЕЛОК:")
        print("-"*80)
        print(f"{'#':>4} {'Тип':>6} {'Вход':>10} {'Выход':>10} {'Результат':>10} {'PnL%':>8} {'PnL$':>10} {'Equity':>10}")
        print("-"*80)
        
        for i, t in enumerate(final_stats['trades'], 1):
            print(f"{i:>4} {t['type']:>6} {t['entry']:>10.2f} {t['exit']:>10.2f} {t['result']:>10} {t['pnl_pct']:>+8.2%} {t['pnl_usdt']:>+10.2f} {t['equity']:>10.2f}")
    
    # Рекомендации
    print("\n\n💡 РЕКОМЕНДАЦИИ:")
    print("-"*60)
    
    if final_stats['total_return_pct'] > 0:
        print("  ✓ Стратегия прибыльна с плечом 10x")
        print(f"  ✓ Рекомендуемый риск на сделку: {best['risk_pct']:.1%}")
        print(f"  ✓ Stop Loss: {best['sl_mult']}x ATR")
        print(f"  ✓ Take Profit: {best['tp_mult']}x ATR")
    else:
        print("  ⚠ Стратегия убыточна - рекомендуется:")
        print("    - Снизить плечо до 5x")
        print("    - Уменьшить риск до 1%")
        print("    - Использовать более консервативные стопы")
    
    if final_stats['max_drawdown_pct'] > 50:
        print("  ⚠ Высокая просадка - добавить трейлинг стоп")
    
    # Сохранение результатов
    report_path = f"./leveraged_backtest_{best['asset']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump({
            'params': best,
            'stats': {k: v for k, v in final_stats.items() if k != 'trades'},
            'trades': final_stats['trades']
        }, f, indent=2, default=str)
    
    print(f"\n\n📄 Результаты сохранены: {report_path}")
    
    return final_stats


if __name__ == "__main__":
    main()
