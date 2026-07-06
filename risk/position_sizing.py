"""
Position sizing algorithms for TSLab risk management.
Kelly Criterion, ATR-based sizing, fixed fractional, etc.
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple


def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float, 
                    kelly_fraction: float = 0.25) -> float:
    """
    Calculate Kelly Criterion position size.
    
    Kelly % = W - [(1-W) / R]
    where W = win rate, R = avg_win / avg_loss
    
    Args:
        win_rate: Probability of winning (0-1)
        avg_win: Average winning trade (absolute value)
        avg_loss: Average losing trade (absolute value)
        kelly_fraction: Fraction of Kelly to use (0.25 = quarter Kelly)
    
    Returns:
        Position size as fraction of capital (0-1)
    """
    if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
        return 0.0
    
    avg_win = abs(avg_win)
    avg_loss = abs(avg_loss)
    
    win_loss_ratio = avg_win / avg_loss
    
    kelly = win_rate - ((1 - win_rate) / win_loss_ratio)
    
    # Apply fractional Kelly
    kelly *= kelly_fraction
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, kelly))


def kelly_from_trades(trades: pd.DataFrame, 
                      win_col: str = 'pnl',
                      kelly_fraction: float = 0.25) -> float:
    """
    Calculate Kelly from trade history DataFrame.
    
    Args:
        trades: DataFrame with trade results
        win_col: Column name with profit/loss values
        kelly_fraction: Fraction of Kelly to use
    
    Returns:
        Position size as fraction of capital
    """
    if len(trades) == 0:
        return 0.0
    
    wins = trades[trades[win_col] > 0][win_col]
    losses = trades[trades[win_col] < 0][win_col]
    
    if len(wins) == 0 or len(losses) == 0:
        return 0.0
    
    win_rate = len(wins) / len(trades)
    avg_win = wins.mean()
    avg_loss = abs(losses.mean())
    
    return kelly_criterion(win_rate, avg_win, avg_loss, kelly_fraction)


def atr_position_size(capital: float, risk_per_trade_pct: float,
                      atr: float, point_value: float = 1.0,
                      max_position_pct: float = 0.2) -> float:
    """
    Calculate position size based on ATR (Average True Range).
    
    Position Size = (Capital * Risk%) / (ATR * Point Value)
    
    Args:
        capital: Trading capital
        risk_per_trade_pct: Risk per trade as percentage (e.g., 0.01 for 1%)
        atr: Current ATR value
        point_value: Value per point movement
        max_position_pct: Maximum position size as fraction of capital
    
    Returns:
        Number of contracts/shares to trade
    """
    if atr <= 0 or capital <= 0:
        return 0.0
    
    risk_amount = capital * risk_per_trade_pct
    position_size = risk_amount / (atr * point_value)
    
    # Apply maximum position limit
    max_position = capital * max_position_pct / (atr * point_value)
    
    return min(position_size, max_position)


def fixed_fractional(capital: float, risk_pct: float, 
                     stop_loss_pct: float) -> float:
    """
    Fixed fractional position sizing.
    
    Position Size = (Capital * Risk%) / Stop Loss Amount
    
    Args:
        capital: Trading capital
        risk_pct: Risk per trade as fraction (e.g., 0.02 for 2%)
        stop_loss_pct: Stop loss distance as fraction (e.g., 0.05 for 5%)
    
    Returns:
        Position size as fraction of capital
    """
    if stop_loss_pct <= 0 or risk_pct <= 0:
        return 0.0
    
    position_size = risk_pct / stop_loss_pct
    
    return min(position_size, 1.0)


def volatility_adjusted_size(capital: float, target_risk_pct: float,
                            current_volatility: float, 
                            base_volatility: float = 0.02,
                            max_leverage: float = 3.0) -> float:
    """
    Volatility-adjusted position sizing.
    
    Adjusts position size inversely with volatility.
    
    Args:
        capital: Trading capital
        target_risk_pct: Target risk as fraction
        current_volatility: Current volatility (e.g., 0.03 for 3%)
        base_volatility: Base volatility for normalization
        max_leverage: Maximum leverage allowed
    
    Returns:
        Position size as fraction of capital
    """
    if current_volatility <= 0 or base_volatility <= 0:
        return 0.0
    
    vol_adjustment = base_volatility / current_volatility
    position_size = target_risk_pct * vol_adjustment
    
    # Apply leverage limit
    return min(position_size, max_leverage)


def calculate_atr(prices: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range.
    
    Args:
        prices: DataFrame with columns [open, high, low, close]
        period: ATR period
    
    Returns:
        Series with ATR values
    """
    high = prices['high']
    low = prices['low']
    close = prices['close']
    
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR is smoothed average of True Range
    atr = tr.rolling(window=period).mean()
    
    return atr


def optimal_position_size(capital: float, 
                         method: str = 'kelly',
                         **kwargs) -> float:
    """
    Calculate optimal position size using specified method.
    
    Args:
        capital: Trading capital
        method: Sizing method ('kelly', 'atr', 'fixed', 'volatility')
        **kwargs: Additional parameters for the method
    
    Returns:
        Position size (number of contracts or fraction of capital)
    """
    if method == 'kelly':
        return kelly_criterion(
            kwargs.get('win_rate', 0.5),
            kwargs.get('avg_win', 1.0),
            kwargs.get('avg_loss', 1.0),
            kwargs.get('kelly_fraction', 0.25)
        ) * capital
    
    elif method == 'atr':
        return atr_position_size(
            capital,
            kwargs.get('risk_per_trade_pct', 0.01),
            kwargs.get('atr', 1.0),
            kwargs.get('point_value', 1.0),
            kwargs.get('max_position_pct', 0.2)
        )
    
    elif method == 'fixed':
        return fixed_fractional(
            capital,
            kwargs.get('risk_pct', 0.02),
            kwargs.get('stop_loss_pct', 0.05)
        ) * capital
    
    elif method == 'volatility':
        return volatility_adjusted_size(
            capital,
            kwargs.get('target_risk_pct', 0.02),
            kwargs.get('current_volatility', 0.02),
            kwargs.get('base_volatility', 0.02),
            kwargs.get('max_leverage', 3.0)
        ) * capital
    
    else:
        raise ValueError(f"Unknown sizing method: {method}")


def backtest_position_sizing(prices: pd.Series, signals: pd.Series,
                            sizing_method: str = 'fixed',
                            initial_capital: float = 10000,
                            risk_pct: float = 0.02,
                            **kwargs) -> pd.DataFrame:
    """
    Backtest a position sizing strategy.
    
    Args:
        prices: Price series
        signals: Trading signals (1=long, -1=short, 0=flat)
        sizing_method: Position sizing method
        initial_capital: Starting capital
        risk_pct: Risk per trade
        **kwargs: Additional parameters
    
    Returns:
        DataFrame with backtest results
    """
    capital = initial_capital
    position = 0
    results = []
    
    for i in range(len(prices)):
        price = prices.iloc[i]
        signal = signals.iloc[i]
        
        # Calculate position size
        if signal != 0:
            position_size = optimal_position_size(
                capital,
                method=sizing_method,
                risk_per_trade_pct=risk_pct,
                **kwargs
            )
            
            # Simple position sizing (fraction of capital)
            shares = position_size / price
            position = shares * signal
        else:
            position = 0
        
        # Calculate PnL
        if i > 0:
            price_change = price - prices.iloc[i-1]
            pnl = position * price_change
            capital += pnl
        
        results.append({
            'price': price,
            'signal': signal,
            'position': position,
            'capital': capital,
            'pnl': pnl if i > 0 else 0,
        })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    # Example usage
    print("=== Position Sizing Examples ===\n")
    
    # Kelly Criterion
    print("1. Kelly Criterion:")
    kelly = kelly_criterion(win_rate=0.55, avg_win=1.5, avg_loss=1.0, kelly_fraction=0.25)
    print(f"   Win rate: 55%, Avg Win/Loss: 1.5")
    print(f"   Kelly position size: {kelly:.2%} of capital\n")
    
    # ATR-based
    print("2. ATR-Based Sizing:")
    atr_size = atr_position_size(
        capital=10000,
        risk_per_trade_pct=0.01,
        atr=2.5,
        point_value=1.0,
        max_position_pct=0.2
    )
    print(f"   Capital: $10,000, Risk: 1%, ATR: 2.5")
    print(f"   Position size: {atr_size:.0f} contracts\n")
    
    # Fixed fractional
    print("3. Fixed Fractional:")
    fixed_size = fixed_fractional(
        capital=10000,
        risk_pct=0.02,
        stop_loss_pct=0.05
    )
    print(f"   Risk: 2%, Stop Loss: 5%")
    print(f"   Position size: {fixed_size:.2%} of capital\n")
    
    # Volatility-adjusted
    print("4. Volatility-Adjusted:")
    vol_size = volatility_adjusted_size(
        capital=10000,
        target_risk_pct=0.02,
        current_volatility=0.03,
        base_volatility=0.02
    )
    print(f"   Current vol: 3%, Base vol: 2%")
    print(f"   Position size: {vol_size:.2%} of capital")
