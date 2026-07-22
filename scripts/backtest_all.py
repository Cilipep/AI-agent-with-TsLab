"""
Комплексный бэктест модулей TSLab AI Agent.
Тестирование Analytics, Optimization и Risk Management на исторических данных.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

# Импорт модулей
from analytics.advanced_metrics import (
    sortino_ratio, calmar_ratio, omega_ratio,
    max_drawdown, sharpe_ratio, win_rate, profit_factor,
    calculate_all_metrics
)
from analytics.correlation import (
    correlation_matrix, hierarchical_clustering, diversification_ratio
)
from analytics.regime import (
    threshold_regime_detection, regime_statistics, regime_transitions
)
from risk.position_sizing import (
    kelly_criterion, atr_position_size, fixed_fractional,
    volatility_adjusted_size, calculate_atr, optimal_position_size,
    backtest_position_sizing
)


def generate_crypto_data(n_days: int = 365, n_assets: int = 5) -> pd.DataFrame:
    """
    Генерация синтетических данных криптовалют.
    В реальном проекте здесь будет загрузка из API.
    """
    np.random.seed(42)
    
    assets = ['BTC', 'ETH', 'SOL', 'DOGE', 'ADA'][:n_assets]
    
    # Генерация цен с разными характеристиками
    data = {}
    for i, asset in enumerate(assets):
        # Базовая волатильность зависит от актива
        base_vol = [0.02, 0.03, 0.04, 0.05, 0.035][i]
        base_drift = [0.0005, 0.0003, 0.0008, 0.0002, 0.0004][i]
        
        returns = np.random.normal(base_drift, base_vol, n_days)
        
        # Добавляем тренды и режимы
        regime_changes = np.random.choice([0, 1], size=n_days, p=[0.7, 0.3])
        regime_mult = np.cumsum(regime_changes) % 3
        
        # В разные режимы - разная волатильность
        vol_adjustments = [1.0, 1.5, 0.8]  # Нормальная, высокая, низкая
        for j in range(3):
            mask = regime_mult == j
            returns[mask] *= vol_adjustments[j]
        
        prices = 100 * np.cumprod(1 + returns)
        data[f'{asset}USDT'] = prices
    
    dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
    df = pd.DataFrame(data, index=dates)
    
    return df


def test_analytics_module(prices_df: pd.DataFrame):
    """Тестирование модуля Analytics."""
    print("\n" + "="*60)
    print("📊 ТЕСТИРОВАНИЕ АНАЛИТИЧЕСКОГО МОДУЛЯ")
    print("="*60)
    
    returns_df = prices_df.pct_change().dropna()
    
    # 1. Базовые метрики по каждому активу
    print("\n1. БАЗОВЫЕ МЕТРИКИ ПО АКТИВАМ:")
    print("-"*50)
    
    all_metrics = {}
    for col in returns_df.columns:
        metrics = calculate_all_metrics(returns_df[col].values)
        all_metrics[col] = metrics
        
        print(f"\n{col}:")
        print(f"  Доходность:    {metrics['total_return']:.2%}")
        print(f"  Sharpe Ratio:  {metrics['sharpe_ratio']:.2f}")
        print(f"  Sortino Ratio: {metrics['sortino_ratio']:.2f}")
        print(f"  Calmar Ratio:  {metrics['calmar_ratio']:.2f}")
        print(f"  Omega Ratio:   {metrics['omega_ratio']:.2f}")
        print(f"  Max Drawdown:  {metrics['max_drawdown']:.2%}")
        print(f"  Win Rate:      {metrics['win_rate']:.2%}")
        print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
    
    # 2. Корреляционный анализ
    print("\n\n2. КОРРЕЛЯЦИОННЫЙ АНАЛИЗ:")
    print("-"*50)
    
    corr = correlation_matrix(returns_df)
    print("\nМатрица корреляций:")
    print(corr.round(2).to_string())
    
    # Кластерный анализ
    clusters = hierarchical_clustering(corr, n_clusters=2)
    print(f"\nКластеры (2 группы):")
    for cluster_id, assets in clusters['clusters'].items():
        print(f"  Кластер {cluster_id}: {', '.join(assets)}")
    
    # Коэффициент диверсификации
    div_ratio = diversification_ratio(returns_df)
    print(f"\nКоэффициент диверсификации: {div_ratio:.2f}")
    if div_ratio > 1.2:
        print("  ✓ Хорошая диверсификация")
    else:
        print("  ⚠ Слабая диверсификация")
    
    # 3. Определение режимов
    print("\n\n3. ОПРЕДЕЛЕНИЕ РЕЖИМОВ РЫНКА:")
    print("-"*50)
    
    btc_prices = prices_df['BTCUSDT']
    regime_result = threshold_regime_detection(btc_prices)
    
    regime_counts = regime_result['regime'].value_counts()
    print("\nРаспределение режимов (BTC):")
    for regime, count in regime_counts.items():
        pct = count / len(regime_result) * 100
        print(f"  {regime}: {count} дней ({pct:.1f}%)")
    
    # Статистика по режимам
    stats = regime_statistics(regime_result)
    print("\nСтатистика по режимам:")
    print(stats[['regime', 'count', 'mean_return', 'std_return', 'sharpe']].to_string(index=False))
    
    # Переходы между режимами
    transitions = regime_transitions(regime_result)
    print("\nВероятности переходов между режимами:")
    print(transitions.round(2).to_string())
    
    return all_metrics, corr, regime_result


def test_risk_module(returns_df: pd.DataFrame, initial_capital: float = 10000):
    """Тестирование модуля Risk Management."""
    print("\n" + "="*60)
    print("🛡️ ТЕСТИРОВАНИЕ МОДУЛЯ РИСК-МЕНЕДЖМЕНТА")
    print("="*60)
    
    # 1. Расчет позиций разными методами
    print("\n1. РАСЧЕТ РАЗМЕРОВ ПОЗИЦИЙ:")
    print("-"*50)
    
    btc_returns = returns_df['BTCUSDT'].values
    
    # Средние значения для Kelly
    wins = btc_returns[btc_returns > 0]
    losses = btc_returns[btc_returns < 0]
    win_rate_val = len(wins) / len(btc_returns) if len(btc_returns) > 0 else 0
    avg_win = np.mean(wins) if len(wins) > 0 else 0
    avg_loss = np.abs(np.mean(losses)) if len(losses) > 0 else 1
    
    print(f"\nХарактеристики BTC:")
    print(f"  Win Rate: {win_rate_val:.2%}")
    print(f"  Avg Win:  {avg_win:.4f}")
    print(f"  Avg Loss: {avg_loss:.4f}")
    
    # Kelly Criterion
    kelly = kelly_criterion(win_rate_val, avg_win, avg_loss, kelly_fraction=0.25)
    kelly_position = kelly * initial_capital
    print(f"\nKelly Criterion (25%):")
    print(f"  Kelly %:         {kelly:.2%}")
    print(f"  Размер позиции:  ${kelly_position:,.2f}")
    
    # ATR-based sizing
    btc_prices = 100 * np.cumprod(1 + btc_returns)
    atr = np.mean(np.abs(np.diff(btc_prices[-20:]))) if len(btc_prices) > 20 else 1
    
    atr_size = atr_position_size(
        capital=initial_capital,
        risk_per_trade_pct=0.01,
        atr=atr,
        point_value=1.0
    )
    print(f"\nATR-Based Sizing (1% риск, ATR={atr:.2f}):")
    print(f"  Размер позиции:  ${atr_size:,.2f}")
    
    # Fixed Fractional
    fixed_size = fixed_fractional(
        capital=initial_capital,
        risk_pct=0.02,
        stop_loss_pct=0.05
    )
    print(f"\nFixed Fractional (2% риск, 5% стоп):")
    print(f"  % капитала:      {fixed_size:.2%}")
    print(f"  Размер позиции:  ${fixed_size * initial_capital:,.2f}")
    
    # Volatility-adjusted
    vol_size = volatility_adjusted_size(
        capital=initial_capital,
        target_risk_pct=0.02,
        current_volatility=np.std(btc_returns),
        base_volatility=0.02
    )
    print(f"\nVolatility-Adjusted (тек. вол={np.std(btc_returns):.4f}):")
    print(f"  Размер позиции:  ${vol_size * initial_capital:,.2f}")
    
    # 2. Бэктест с разными методами sizing
    print("\n\n2. БЭКТЕСТ С РАЗНЫМИ МЕТОДАМИ RISK MANAGEMENT:")
    print("-"*50)
    
    # Создаем сигналы (простая SMA стратегия)
    btc_series = pd.Series(btc_prices)
    sma_short = btc_series.rolling(10).mean()
    sma_long = btc_series.rolling(30).mean()
    
    signals = pd.Series(0, index=btc_series.index)
    signals[sma_short > sma_long] = 1   # Long
    signals[sma_short < sma_long] = -1  # Short
    
    # Бэктест с разными методами
    methods = ['fixed', 'atr', 'kelly', 'volatility']
    backtest_results = {}
    
    for method in methods:
        result = backtest_position_sizing(
            prices=btc_series,
            signals=signals,
            sizing_method=method,
            initial_capital=initial_capital,
            risk_pct=0.02,
            win_rate=win_rate_val,
            avg_win=avg_win,
            avg_loss=avg_loss,
            atr=atr,
            current_volatility=np.std(btc_returns),
            kelly_fraction=0.25
        )
        backtest_results[method] = result
        
        final_capital = result['capital'].iloc[-1]
        total_return = (final_capital - initial_capital) / initial_capital
        
        print(f"\n{method.upper()} метод:")
        print(f"  Начальный капитал:  ${initial_capital:,.2f}")
        print(f"  Конечный капитал:   ${final_capital:,.2f}")
        print(f"  Доходность:         {total_return:.2%}")
    
    # 3. Сравнительная таблица
    print("\n\n3. СРАВНИТЕЛЬНАЯ ТАБЛИЦА МЕТОДОВ:")
    print("-"*50)
    
    comparison = []
    for method, result in backtest_results.items():
        final = result['capital'].iloc[-1]
        comparison.append({
            'Метод': method.upper(),
            'Конечный капитал': f"${final:,.2f}",
            'Доходность': f"{(final - initial_capital) / initial_capital:.2%}",
        })
    
    comp_df = pd.DataFrame(comparison)
    print(comp_df.to_string(index=False))
    
    return backtest_results


def test_optimization_concept(returns_df: pd.DataFrame):
    """Демонстрация концепции оптимизации (без реального API)."""
    print("\n" + "="*60)
    print("🎯 ДЕМОНСТРАЦИЯ ОПТИМИЗАЦИИ")
    print("="*60)
    
    print("\nКонцепция Walk-Forward Optimization:")
    print("-"*50)
    
    # Симуляция walk-forward анализа
    n_windows = 5
    in_sample_pct = 70
    
    btc_returns = returns_df['BTCUSDT'].values
    window_size = len(btc_returns) // n_windows
    
    print(f"\nПараметры:")
    print(f"  Окон: {n_windows}")
    print(f"  In-Sample: {in_sample_pct}%")
    print(f"  Out-of-Sample: {100-in_sample_pct}%")
    
    window_results = []
    
    for w in range(n_windows):
        start = w * window_size
        end = start + window_size
        
        if end > len(btc_returns):
            break
        
        window_data = btc_returns[start:end]
        split = int(len(window_data) * in_sample_pct / 100)
        
        in_sample = window_data[:split]
        out_sample = window_data[split:]
        
        # Симуляция оптимизации на in-sample
        in_sample_sharpe = sharpe_ratio(in_sample) if len(in_sample) > 1 else 0
        
        # Тест на out-of-sample
        out_sample_sharpe = sharpe_ratio(out_sample) if len(out_sample) > 1 else 0
        
        result = {
            'window': w + 1,
            'in_sample_sharpe': in_sample_sharpe,
            'out_sample_sharpe': out_sample_sharpe,
            'consistent': (in_sample_sharpe > 0) == (out_sample_sharpe > 0)
        }
        window_results.append(result)
        
        print(f"\nОкно {w+1}:")
        print(f"  In-Sample Sharpe:  {in_sample_sharpe:.2f}")
        print(f"  Out-Sample Sharpe: {out_sample_sharpe:.2f}")
        print(f"  Консистентность:   {'✓' if result['consistent'] else '✗'}")
    
    # Статистика
    consistent_windows = sum(1 for r in window_results if r['consistent'])
    print(f"\nИтого: {consistent_windows}/{len(window_results)} консистентных окон")
    
    # Демонстрация Monte Carlo
    print("\n\nДемонстрация Monte Carlo Simulation:")
    print("-"*50)
    
    n_simulations = 100
    simulated_returns = []
    
    for _ in range(n_simulations):
        # Случайная перестановка доходностей
        shuffled = np.random.permutation(btc_returns)
        sim_sharpe = sharpe_ratio(shuffled)
        simulated_returns.append(sim_sharpe)
    
    sim_stats = {
        'mean': np.mean(simulated_returns),
        'std': np.std(simulated_returns),
        'percentile_5': np.percentile(simulated_returns, 5),
        'percentile_95': np.percentile(simulated_returns, 95)
    }
    
    print(f"\nРезультаты {n_simulations} симуляций:")
    print(f"  Средний Sharpe:    {sim_stats['mean']:.2f}")
    print(f"  Стд. отклонение:   {sim_stats['std']:.2f}")
    print(f"  5-й перцентиль:    {sim_stats['percentile_5']:.2f}")
    print(f"  95-й перцентиль:   {sim_stats['percentile_95']:.2f}")
    
    return window_results, sim_stats


def generate_report(all_metrics, corr, regime_result, backtest_results, opt_results):
    """Генерация итогового отчета."""
    print("\n" + "="*60)
    print("📋 ИТОГОВЫЙ ОТЧЕТ БЭКТЕСТА")
    print("="*60)
    
    report = {
        'date': datetime.now().isoformat(),
        'modules_tested': ['analytics', 'risk', 'optimization'],
        'summary': {}
    }
    
    # Резюме по аналитике
    print("\n📊 АНАЛИТИЧЕСКИЙ МОДУЛЬ:")
    best_asset = max(all_metrics.items(), key=lambda x: x[1]['sharpe_ratio'])
    worst_asset = min(all_metrics.items(), key=lambda x: x[1]['sharpe_ratio'])
    
    print(f"  Лучший актив:  {best_asset[0]} (Sharpe: {best_asset[1]['sharpe_ratio']:.2f})")
    print(f"  Худший актив:  {worst_asset[0]} (Sharpe: {worst_asset[1]['sharpe_ratio']:.2f})")
    print(f"  Средний Sharpe: {np.mean([m['sharpe_ratio'] for m in all_metrics.values()]):.2f}")
    
    report['summary']['analytics'] = {
        'best_asset': best_asset[0],
        'worst_asset': worst_asset[0],
        'avg_sharpe': np.mean([m['sharpe_ratio'] for m in all_metrics.values()])
    }
    
    # Резюме по риск-менеджменту
    print("\n🛡️ РИСК-МЕНЕДЖМЕНТ:")
    best_method = max(backtest_results.items(), 
                     key=lambda x: x[1]['capital'].iloc[-1])
    worst_method = min(backtest_results.items(), 
                      key=lambda x: x[1]['capital'].iloc[-1])
    
    best_return = (best_method[1]['capital'].iloc[-1] - 10000) / 10000
    worst_return = (worst_method[1]['capital'].iloc[-1] - 10000) / 10000
    
    print(f"  Лучший метод:   {best_method[0].upper()} ({best_return:.2%})")
    print(f"  Худший метод:   {worst_method[0].upper()} ({worst_return:.2%})")
    
    report['summary']['risk'] = {
        'best_method': best_method[0],
        'best_return': best_return,
        'worst_method': worst_method[0],
        'worst_return': worst_return
    }
    
    # Резюме по оптимизации
    print("\n🎯 ОПТИМИЗАЦИЯ:")
    window_results, sim_stats = opt_results
    consistent_pct = sum(1 for r in window_results if r['consistent']) / len(window_results) * 100
    
    print(f"  Walk-Forward: {consistent_pct:.0f}% консистентных окон")
    print(f"  Monte Carlo:  Средний Sharpe {sim_stats['mean']:.2f}")
    
    report['summary']['optimization'] = {
        'walk_forward_consistency': consistent_pct,
        'monte_carlo_avg_sharpe': sim_stats['mean']
    }
    
    # Рекомендации
    print("\n\n💡 РЕКОМЕНДАЦИИ:")
    print("-"*50)
    
    recommendations = []
    
    if best_return > 0:
        rec = f"Использовать метод {best_method[0].upper()} для размера позиций"
        recommendations.append(rec)
        print(f"  ✓ {rec}")
    
    if consistent_pct >= 60:
        rec = "Стратегия стабильна - можно увеличить размер позиций"
        recommendations.append(rec)
        print(f"  ✓ {rec}")
    else:
        rec = "Стратегия нестабильна - рекомендуется уменьшить риск"
        recommendations.append(rec)
        print(f"  ⚠ {rec}")
    
    best_corr_pair = None
    min_corr = 1
    for i in range(len(corr.columns)):
        for j in range(i+1, len(corr.columns)):
            if corr.iloc[i, j] < min_corr:
                min_corr = corr.iloc[i, j]
                best_corr_pair = (corr.columns[i], corr.columns[j])
    
    if best_corr_pair:
        rec = f"Для диверсификации комбинировать {best_corr_pair[0]} и {best_corr_pair[1]} (корреляция: {min_corr:.2f})"
        recommendations.append(rec)
        print(f"  ✓ {rec}")
    
    report['recommendations'] = recommendations
    
    # Сохранение отчета
    report_path = f"./backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Отчет сохранен: {report_path}")
    
    return report


def main():
    """Главная функция бэктеста."""
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО БЭКТЕСТА TSLab AI Agent")
    print("="*60)
    
    # Генерация данных
    print("\n📈 Генерация исторических данных...")
    prices_df = generate_crypto_data(n_days=365, n_assets=5)
    returns_df = prices_df.pct_change().dropna()
    
    print(f"  Период: {prices_df.index[0].date()} - {prices_df.index[-1].date()}")
    print(f"  Активов: {len(prices_df.columns)}")
    print(f"  Дней: {len(prices_df)}")
    
    # Тестирование модулей
    all_metrics, corr, regime_result = test_analytics_module(prices_df)
    backtest_results = test_risk_module(returns_df)
    opt_results = test_optimization_concept(returns_df)
    
    # Генерация отчета
    report = generate_report(all_metrics, corr, regime_result, backtest_results, opt_results)
    
    print("\n" + "="*60)
    print("✅ БЭКТЕСТ ЗАВЕРШЕН УСПЕШНО")
    print("="*60)
    
    return report


if __name__ == "__main__":
    main()
