"""
Комплексный бэктест модулей TSLab AI Agent (автономная версия).
Работает без внешних зависимостей除了 numpy и pandas.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from datetime import datetime
import json


# ==========================================
# Встроенные функции аналитики
# ==========================================

def sortino_ratio(returns, target=0):
    if len(returns) < 2: return 0.0
    excess = returns - target
    downside = excess[excess < 0]
    if len(downside) == 0: return float('inf') if np.mean(excess) > 0 else 0.0
    downside_dev = np.sqrt(np.mean(downside ** 2))
    if downside_dev == 0: return float('inf') if np.mean(excess) > 0 else 0.0
    return np.mean(excess) / downside_dev * np.sqrt(252)

def calmar_ratio(returns):
    if len(returns) < 2: return 0.0
    cum = np.cumprod(1 + returns)
    total_return = cum[-1] / cum[0] - 1
    n = len(returns)
    cagr = (1 + total_return) ** (252 / n) - 1 if n > 0 else 0
    peak = np.maximum.accumulate(cum)
    max_dd = np.max((peak - cum) / peak)
    if max_dd == 0: return float('inf') if cagr > 0 else 0.0
    return cagr / max_dd

def omega_ratio(returns, threshold=0):
    if len(returns) < 2: return 1.0
    excess = returns - threshold
    gains = excess[excess > 0]
    losses = excess[excess < 0]
    if len(losses) == 0 or np.sum(np.abs(losses)) == 0:
        return float('inf') if len(gains) > 0 else 1.0
    return np.sum(gains) / np.sum(np.abs(losses))

def max_drawdown(returns):
    if len(returns) < 2: return 0.0
    cum = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cum)
    return np.max((peak - cum) / peak)

def sharpe_ratio(returns, rf=0):
    if len(returns) < 2: return 0.0
    excess = returns - rf
    if np.std(excess) == 0: return 0.0
    return np.mean(excess) / np.std(excess) * np.sqrt(252)

def win_rate(returns):
    if len(returns) == 0: return 0.0
    return np.sum(returns > 0) / len(returns)

def profit_factor(returns):
    gross_profit = np.sum(returns[returns > 0])
    gross_loss = np.abs(np.sum(returns[returns < 0]))
    if gross_loss == 0: return float('inf') if gross_profit > 0 else 0.0
    return gross_profit / gross_loss

def calculate_all_metrics(returns):
    return {
        'sortino_ratio': sortino_ratio(returns),
        'calmar_ratio': calmar_ratio(returns),
        'omega_ratio': omega_ratio(returns),
        'max_drawdown': max_drawdown(returns),
        'sharpe_ratio': sharpe_ratio(returns),
        'win_rate': win_rate(returns),
        'profit_factor': profit_factor(returns),
        'total_return': np.sum(returns),
        'avg_return': np.mean(returns),
        'std_return': np.std(returns),
        'n_periods': len(returns),
    }

def correlation_matrix(returns_df):
    return returns_df.corr()

def diversification_ratio(returns_df, weights=None):
    n = returns_df.shape[1]
    if weights is None:
        weights = np.ones(n) / n
    vols = returns_df.std().values
    weighted_avg_vol = np.sum(weights * vols)
    cov = returns_df.cov().values
    port_var = np.dot(weights.T, np.dot(cov, weights))
    port_vol = np.sqrt(port_var)
    if port_vol == 0: return 1.0
    return weighted_avg_vol / port_vol

def threshold_regime_detection(prices, window=20, vol_window=20):
    returns = prices.pct_change()
    rolling_vol = returns.rolling(vol_window).std()
    avg_vol = rolling_vol.mean()
    ma = prices.rolling(window).mean()
    trend = (prices - ma) / ma
    
    regimes = pd.Series(index=prices.index, dtype=str)
    high_vol = rolling_vol > avg_vol * 1.5
    low_vol = rolling_vol < avg_vol * 0.5
    uptrend = trend > 0
    downtrend = trend < 0
    
    regimes[high_vol & uptrend] = 'trending_high_vol'
    regimes[high_vol & downtrend] = 'declining_high_vol'
    regimes[high_vol & ~uptrend & ~downtrend] = 'sideways_high_vol'
    regimes[low_vol & uptrend] = 'trending_low_vol'
    regimes[low_vol & downtrend] = 'declining_low_vol'
    regimes[low_vol & ~uptrend & ~downtrend] = 'sideways_low_vol'
    regimes[~high_vol & ~low_vol & uptrend] = 'trending_normal_vol'
    regimes[~high_vol & ~low_vol & downtrend] = 'declining_normal_vol'
    regimes[~high_vol & ~low_vol & ~uptrend & ~downtrend] = 'sideways_normal_vol'
    
    return pd.DataFrame({
        'price': prices,
        'returns': returns,
        'volatility': rolling_vol,
        'trend': trend,
        'regime': regimes
    })

def regime_statistics(regime_df, regime_col='regime'):
    stats = []
    for regime in regime_df[regime_col].unique():
        data = regime_df[regime_df[regime_col] == regime]
        returns = data['returns'].dropna()
        if len(returns) == 0: continue
        stats.append({
            'regime': regime,
            'count': len(returns),
            'mean_return': returns.mean(),
            'std_return': returns.std(),
            'sharpe': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'win_rate': (returns > 0).mean(),
        })
    return pd.DataFrame(stats)

def regime_transitions(regime_df, regime_col='regime'):
    regimes = regime_df[regime_col].dropna().values
    n = len(np.unique(regimes))
    names = np.unique(regimes)
    counts = np.zeros((n, n))
    for i in range(len(regimes) - 1):
        from_idx = np.where(names == regimes[i])[0][0]
        to_idx = np.where(names == regimes[i + 1])[0][0]
        counts[from_idx, to_idx] += 1
    row_sums = counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    return pd.DataFrame(counts / row_sums, index=names, columns=names)


# ==========================================
# Встроенные функции риск-менеджмента
# ==========================================

def kelly_criterion(win_rate_val, avg_win, avg_loss, kelly_fraction=0.25):
    if avg_loss == 0 or win_rate_val <= 0 or win_rate_val >= 1: return 0.0
    avg_win = abs(avg_win)
    avg_loss = abs(avg_loss)
    kelly = win_rate_val - ((1 - win_rate_val) / (avg_win / avg_loss))
    return max(0.0, min(1.0, kelly * kelly_fraction))

def atr_position_size(capital, risk_pct, atr, point_value=1.0, max_pct=0.2):
    if atr <= 0 or capital <= 0: return 0.0
    risk_amount = capital * risk_pct
    size = risk_amount / (atr * point_value)
    max_pos = capital * max_pct / (atr * point_value)
    return min(size, max_pos)

def fixed_fractional(capital, risk_pct, stop_loss_pct):
    if stop_loss_pct <= 0: return 0.0
    return min(risk_pct / stop_loss_pct, 1.0)

def backtest_position_sizing(prices, signals, method='fixed', capital=10000, **kwargs):
    pos = 0
    results = []
    for i in range(len(prices)):
        price = prices.iloc[i]
        signal = signals.iloc[i]
        
        if signal != 0:
            if method == 'fixed':
                frac = fixed_fractional(capital, kwargs.get('risk_pct', 0.02), kwargs.get('sl_pct', 0.05))
                shares = (frac * capital) / price
            elif method == 'kelly':
                kelly = kelly_criterion(kwargs.get('wr', 0.5), kwargs.get('aw', 1), kwargs.get('al', 1), 0.25)
                shares = (kelly * capital) / price
            elif method == 'atr':
                atr = kwargs.get('atr', 1)
                size = atr_position_size(capital, kwargs.get('risk_pct', 0.01), atr)
                shares = size / price
            else:
                shares = (kwargs.get('risk_pct', 0.02) * capital) / price
            pos = shares * signal
        else:
            pos = 0
        
        pnl = pos * (price - prices.iloc[i-1]) if i > 0 else 0
        capital += pnl
        results.append({'price': price, 'signal': signal, 'capital': capital, 'pnl': pnl})
    
    return pd.DataFrame(results)


# ==========================================
# Генерация данных
# ==========================================

def generate_crypto_data(n_days=365, n_assets=5):
    np.random.seed(42)
    assets = ['BTC', 'ETH', 'SOL', 'DOGE', 'ADA'][:n_assets]
    data = {}
    vols = [0.02, 0.03, 0.04, 0.05, 0.035]
    drifts = [0.0005, 0.0003, 0.0008, 0.0002, 0.0004]
    
    for i, asset in enumerate(assets):
        returns = np.random.normal(drifts[i], vols[i], n_days)
        prices = 100 * np.cumprod(1 + returns)
        data[f'{asset}USDT'] = prices
    
    dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
    return pd.DataFrame(data, index=dates)


# ==========================================
# Тестирование модулей
# ==========================================

def test_analytics(prices_df):
    print("\n" + "="*60)
    print("📊 ТЕСТИРОВАНИЕ АНАЛИТИЧЕСКОГО МОДУЛЯ")
    print("="*60)
    
    returns_df = prices_df.pct_change().dropna()
    
    print("\n1. БАЗОВЫЕ МЕТРИКИ ПО АКТИВАМ:")
    print("-"*50)
    
    all_metrics = {}
    for col in returns_df.columns:
        metrics = calculate_all_metrics(returns_df[col].values)
        all_metrics[col] = metrics
        print(f"\n{col}:")
        print(f"  Доходность:    {metrics['total_return']:.2%}")
        print(f"  Sharpe:        {metrics['sharpe_ratio']:.2f}")
        print(f"  Sortino:       {metrics['sortino_ratio']:.2f}")
        print(f"  Calmar:        {metrics['calmar_ratio']:.2f}")
        print(f"  Max Drawdown:  {metrics['max_drawdown']:.2%}")
        print(f"  Win Rate:      {metrics['win_rate']:.2%}")
        print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
    
    print("\n\n2. КОРРЕЛЯЦИОННЫЙ АНАЛИЗ:")
    print("-"*50)
    corr = correlation_matrix(returns_df)
    print(corr.round(2).to_string())
    
    div = diversification_ratio(returns_df)
    print(f"\nКоэффициент диверсификации: {div:.2f}")
    
    print("\n\n3. ОПРЕДЕЛЕНИЕ РЕЖИМОВ:")
    print("-"*50)
    regime = threshold_regime_detection(prices_df['BTCUSDT'])
    stats = regime_statistics(regime)
    print(stats[['regime', 'count', 'mean_return', 'sharpe']].to_string(index=False))
    
    return all_metrics, corr, regime

def test_risk(returns_df, capital=10000):
    print("\n" + "="*60)
    print("🛡️ ТЕСТИРОВАНИЕ РИСК-МЕНЕДЖМЕНТА")
    print("="*60)
    
    btc = returns_df['BTCUSDT'].values
    wins = btc[btc > 0]
    losses = btc[btc < 0]
    wr = len(wins) / len(btc)
    aw = np.mean(wins)
    al = abs(np.mean(losses))
    
    print(f"\nХарактеристики BTC: WR={wr:.2%}, AvgWin={aw:.4f}, AvgLoss={al:.4f}")
    
    kelly = kelly_criterion(wr, aw, al, 0.25)
    print(f"\nKelly (25%): {kelly:.2%} = ${kelly * capital:,.2f}")
    
    btc_prices = pd.Series(100 * np.cumprod(1 + btc))
    sma10 = btc_prices.rolling(10).mean()
    sma30 = btc_prices.rolling(30).mean()
    signals = pd.Series(0, index=btc_prices.index)
    signals[sma10 > sma30] = 1
    signals[sma10 < sma30] = -1
    
    print("\nБЭКТЕСТ С РАЗНЫМИ МЕТОДАМИ:")
    print("-"*50)
    
    results = {}
    for method in ['fixed', 'kelly', 'atr']:
        r = backtest_position_sizing(btc_prices, signals, method, capital,
                                    risk_pct=0.02, wr=wr, aw=aw, al=al, atr=1)
        results[method] = r
        final = r['capital'].iloc[-1]
        ret = (final - capital) / capital
        print(f"  {method.upper():10} → ${final:,.2f} ({ret:+.2%})")
    
    return results

def test_optimization(returns_df):
    print("\n" + "="*60)
    print("🎯 ДЕМОНСТРАЦИЯ ОПТИМИЗАЦИИ")
    print("="*60)
    
    btc = returns_df['BTCUSDT'].values
    n_windows = 5
    window_size = len(btc) // n_windows
    
    print(f"\nWalk-Forward ({n_windows} окон, 70/30 split):")
    print("-"*50)
    
    consistent = 0
    for w in range(n_windows):
        start = w * window_size
        end = start + window_size
        if end > len(btc): break
        
        data = btc[start:end]
        split = int(len(data) * 0.7)
        in_s = sharpe_ratio(data[:split]) if len(data[:split]) > 1 else 0
        out_s = sharpe_ratio(data[split:]) if len(data[split:]) > 1 else 0
        ok = (in_s > 0) == (out_s > 0)
        consistent += ok
        
        print(f"  Окно {w+1}: In={in_s:.2f}, Out={out_s:.2f} {'✓' if ok else '✗'}")
    
    print(f"\nКонсистентность: {consistent}/{n_windows} ({consistent/n_windows*100:.0f}%)")
    
    print("\nMonte Carlo (100 симуляций):")
    print("-"*50)
    sims = [sharpe_ratio(np.random.permutation(btc)) for _ in range(100)]
    print(f"  Средний Sharpe: {np.mean(sims):.2f}")
    print(f"  5-95% диапазон: [{np.percentile(sims, 5):.2f}, {np.percentile(sims, 95):.2f}]")
    
    return {'consistent': consistent, 'total': n_windows, 'mc_mean': np.mean(sims)}

def main():
    print("🚀 КОМПЛЕКСНЫЙ БЭКТЕСТ TSLab AI Agent")
    print("="*60)
    
    print("\n📈 Генерация данных...")
    prices = generate_crypto_data(365, 5)
    returns = prices.pct_change().dropna()
    print(f"  Период: {prices.index[0].date()} - {prices.index[-1].date()}")
    print(f"  Активов: {len(prices.columns)}, Дней: {len(prices)}")
    
    m, c, r = test_analytics(prices)
    br = test_risk(returns)
    o = test_optimization(returns)
    
    print("\n" + "="*60)
    print("📋 ИТОГОВЫЕ РЕКОМЕНДАЦИИ")
    print("="*60)
    
    best = max(m.items(), key=lambda x: x[1]['sharpe_ratio'])
    worst = min(m.items(), key=lambda x: x[1]['sharpe_ratio'])
    print(f"\n  Лучший актив:  {best[0]} (Sharpe {best[1]['sharpe_ratio']:.2f})")
    print(f"  Худший актив:  {worst[0]} (Sharpe {worst[1]['sharpe_ratio']:.2f})")
    
    best_m = max(br.items(), key=lambda x: x[1]['capital'].iloc[-1])
    print(f"  Лучший метод:  {best_m[0].upper()}")
    
    if o['consistent'] >= 3:
        print(f"  ✓ Стратегия стабильна ({o['consistent']}/{o['total']} окон)")
    else:
        print(f"  ⚠ Стратегия нестабильна - снизить риск")
    
    print("\n✅ БЭКТЕСТ ЗАВЕРШЕН")


if __name__ == "__main__":
    main()
