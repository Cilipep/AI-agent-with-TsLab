"""
Advanced financial metrics for TSLab analytics.
Sortino, Calmar, Omega ratios and related calculations.
"""

import numpy as np
import pandas as pd
from typing import Optional


def sortino_ratio(returns: np.ndarray, target_return: float = 0.0, annualize: bool = True) -> float:
    """
    Calculate Sortino ratio — measures risk-adjusted return using downside deviation.
    
    Args:
        returns: Array of periodic returns
        target_return: Minimum acceptable return (MAR)
        annualize: If True, annualize the result
    
    Returns:
        Sortino ratio value
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - target_return
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return float('inf') if np.mean(excess_returns) > 0 else 0.0
    
    downside_deviation = np.sqrt(np.mean(downside_returns ** 2))
    
    if downside_deviation == 0:
        return float('inf') if np.mean(excess_returns) > 0 else 0.0
    
    sortino = np.mean(excess_returns) / downside_deviation
    
    if annualize:
        sortino *= np.sqrt(252)  # assuming daily returns
    
    return sortino


def calmar_ratio(returns: np.ndarray, annualize: bool = True) -> float:
    """
    Calculate Calmar ratio — CAGR / Max Drawdown.
    
    Args:
        returns: Array of periodic returns
        annualize: If True, annualize CAGR
    
    Returns:
        Calmar ratio value
    """
    if len(returns) < 2:
        return 0.0
    
    cumulative = np.cumprod(1 + returns)
    total_return = cumulative[-1] / cumulative[0] - 1
    
    if annualize:
        n_periods = len(returns)
        if n_periods <= 0:
            return 0.0
        cagr = (1 + total_return) ** (252 / n_periods) - 1
    else:
        cagr = total_return
    
    # Calculate max drawdown
    peak = np.maximum.accumulate(cumulative)
    drawdowns = (peak - cumulative) / peak
    max_drawdown = np.max(drawdowns)
    
    if max_drawdown == 0:
        return float('inf') if cagr > 0 else 0.0
    
    return cagr / max_drawdown


def omega_ratio(returns: np.ndarray, threshold: float = 0.0) -> float:
    """
    Calculate Omega ratio — probability-weighted gains / losses above threshold.
    
    Args:
        returns: Array of periodic returns
        threshold: Return threshold (like MAR)
    
    Returns:
        Omega ratio value
    """
    if len(returns) < 2:
        return 1.0
    
    excess = returns - threshold
    
    gains = excess[excess > 0]
    losses = excess[excess < 0]
    
    if len(losses) == 0 or np.sum(np.abs(losses)) == 0:
        return float('inf') if len(gains) > 0 else 1.0
    
    omega = np.sum(gains) / np.sum(np.abs(losses))
    
    return omega


def max_drawdown(returns: np.ndarray) -> float:
    """Calculate maximum drawdown from returns array."""
    if len(returns) < 2:
        return 0.0
    
    cumulative = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cumulative)
    drawdowns = (peak - cumulative) / peak
    
    return np.max(drawdowns)


def max_drawdown_duration(returns: np.ndarray) -> int:
    """Calculate duration (in periods) of maximum drawdown."""
    if len(returns) < 2:
        return 0
    
    cumulative = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cumulative)
    
    in_drawdown = cumulative < peak
    durations = []
    current_duration = 0
    
    for dd in in_drawdown:
        if dd:
            current_duration += 1
        else:
            if current_duration > 0:
                durations.append(current_duration)
            current_duration = 0
    
    if current_duration > 0:
        durations.append(current_duration)
    
    return max(durations) if durations else 0


def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.0, annualize: bool = True) -> float:
    """Calculate Sharpe ratio."""
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - risk_free_rate
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns)
    
    if annualize:
        sharpe *= np.sqrt(252)
    
    return sharpe


def win_rate(returns: np.ndarray) -> float:
    """Calculate win rate (percentage of positive returns)."""
    if len(returns) == 0:
        return 0.0
    
    return np.sum(returns > 0) / len(returns)


def profit_factor(returns: np.ndarray) -> float:
    """Calculate profit factor (gross profit / gross loss)."""
    gross_profit = np.sum(returns[returns > 0])
    gross_loss = np.abs(np.sum(returns[returns < 0]))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


def calculate_all_metrics(returns: np.ndarray, trades: Optional[pd.DataFrame] = None) -> dict:
    """
    Calculate all advanced metrics at once.
    
    Args:
        returns: Array of periodic returns
        trades: Optional DataFrame with trade details
    
    Returns:
        Dictionary with all metrics
    """
    metrics = {
        'sortino_ratio': sortino_ratio(returns),
        'calmar_ratio': calmar_ratio(returns),
        'omega_ratio': omega_ratio(returns),
        'max_drawdown': max_drawdown(returns),
        'max_drawdown_duration': max_drawdown_duration(returns),
        'sharpe_ratio': sharpe_ratio(returns),
        'win_rate': win_rate(returns),
        'profit_factor': profit_factor(returns),
        'total_return': np.sum(returns),
        'avg_return': np.mean(returns),
        'std_return': np.std(returns),
        'n_periods': len(returns),
    }
    
    if trades is not None and len(trades) > 0:
        metrics['n_trades'] = len(trades)
        if 'pnl' in trades.columns:
            metrics['avg_trade_pnl'] = trades['pnl'].mean()
            metrics['best_trade'] = trades['pnl'].max()
            metrics['worst_trade'] = trades['pnl'].min()
    
    return metrics


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 252)
    
    metrics = calculate_all_metrics(returns)
    
    print("Advanced Metrics:")
    print(f"  Sortino Ratio: {metrics['sortino_ratio']:.2f}")
    print(f"  Calmar Ratio: {metrics['calmar_ratio']:.2f}")
    print(f"  Omega Ratio: {metrics['omega_ratio']:.2f}")
    print(f"  Max Drawdown: {metrics['max_drawdown']:.2%}")
    print(f"  Max DD Duration: {metrics['max_drawdown_duration']} days")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"  Win Rate: {metrics['win_rate']:.2%}")
    print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
