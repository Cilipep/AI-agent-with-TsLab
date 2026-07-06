"""
Regime detection for TSLab analytics.
Gaussian Mixture, threshold-based regime detection.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


def threshold_regime_detection(prices: pd.Series, 
                               window: int = 20,
                               volatility_window: int = 20,
                               high_vol_threshold: float = 1.5,
                               low_vol_threshold: float = 0.5) -> pd.DataFrame:
    """
    Detect market regimes using volatility thresholds.
    
    Args:
        prices: Price series
        window: Lookback window for trend
        volatility_window: Window for volatility calculation
        high_vol_threshold: Threshold for high volatility regime
        low_vol_threshold: Threshold for low volatility regime
    
    Returns:
        DataFrame with regime labels and indicators
    """
    returns = prices.pct_change()
    
    # Calculate rolling volatility
    rolling_vol = returns.rolling(volatility_window).std()
    avg_vol = rolling_vol.mean()
    
    # Calculate trend (price vs MA)
    ma = prices.rolling(window).mean()
    trend = (prices - ma) / ma
    
    # Determine regimes
    regimes = pd.Series(index=prices.index, dtype=str)
    
    # High volatility
    high_vol = rolling_vol > avg_vol * high_vol_threshold
    # Low volatility
    low_vol = rolling_vol < avg_vol * low_vol_threshold
    
    # Trend-based
    uptrend = trend > 0
    downtrend = trend < 0
    
    # Combine into regimes
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


def gaussian_mixture_regime(prices: pd.Series,
                            n_regimes: int = 3,
                            features: list = None,
                            lookback: int = 20) -> pd.DataFrame:
    """
    Detect regimes using Gaussian Mixture Model.
    
    Args:
        prices: Price series
        n_regimes: Number of regimes to detect
        features: List of features to use (default: returns, volatility, momentum)
        lookback: Lookback period for feature calculation
    
    Returns:
        DataFrame with regime labels and probabilities
    """
    returns = prices.pct_change()
    
    if features is None:
        features = ['returns', 'volatility', 'momentum']
    
    # Calculate features
    feature_data = {}
    
    if 'returns' in features:
        feature_data['returns'] = returns
    
    if 'volatility' in features:
        feature_data['volatility'] = returns.rolling(lookback).std()
    
    if 'momentum' in features:
        feature_data['momentum'] = prices.pct_change(lookback)
    
    if 'trend' in features:
        ma = prices.rolling(lookback).mean()
        feature_data['trend'] = (prices - ma) / ma
    
    # Create feature DataFrame
    feature_df = pd.DataFrame(feature_data, index=prices.index)
    feature_df = feature_df.dropna()
    
    if len(feature_df) < n_regimes * 10:
        print("Warning: Not enough data for reliable regime detection")
        return pd.DataFrame(index=prices.index)
    
    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(feature_df)
    
    # Fit Gaussian Mixture
    gmm = GaussianMixture(n_components=n_regimes, random_state=42)
    regimes = gmm.fit_predict(X)
    probabilities = gmm.predict_proba(X)
    
    # Create output DataFrame
    result = pd.DataFrame(index=feature_df.index)
    result['regime'] = regimes
    
    # Add probabilities for each regime
    for i in range(n_regimes):
        result[f'regime_{i}_prob'] = probabilities[:, i]
    
    # Add back price and returns
    result['price'] = prices.loc[result.index]
    result['returns'] = returns.loc[result.index]
    
    return result


def regime_statistics(regime_df: pd.DataFrame, regime_col: str = 'regime') -> pd.DataFrame:
    """
    Calculate statistics for each regime.
    
    Args:
        regime_df: DataFrame with regime labels
        regime_col: Column name containing regime labels
    
    Returns:
        DataFrame with regime statistics
    """
    if 'returns' not in regime_df.columns:
        raise ValueError("DataFrame must contain 'returns' column")
    
    stats = []
    
    for regime in regime_df[regime_col].unique():
        regime_data = regime_df[regime_df[regime_col] == regime]
        
        returns = regime_data['returns'].dropna()
        
        if len(returns) == 0:
            continue
        
        stat = {
            'regime': regime,
            'count': len(returns),
            'mean_return': returns.mean(),
            'std_return': returns.std(),
            'min_return': returns.min(),
            'max_return': returns.max(),
            'sharpe': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'win_rate': (returns > 0).mean(),
        }
        
        stats.append(stat)
    
    return pd.DataFrame(stats)


def regime_transitions(regime_df: pd.DataFrame, regime_col: str = 'regime') -> pd.DataFrame:
    """
    Calculate regime transition probabilities.
    
    Args:
        regime_df: DataFrame with regime labels
        regime_col: Column name containing regime labels
    
    Returns:
        Transition probability matrix
    """
    regimes = regime_df[regime_col].values
    n_regimes = len(np.unique(regimes))
    regime_names = np.unique(regimes)
    
    # Initialize transition count matrix
    transition_counts = np.zeros((n_regimes, n_regimes))
    
    # Count transitions
    for i in range(len(regimes) - 1):
        from_idx = np.where(regime_names == regimes[i])[0][0]
        to_idx = np.where(regime_names == regimes[i + 1])[0][0]
        transition_counts[from_idx, to_idx] += 1
    
    # Normalize to probabilities
    row_sums = transition_counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    transition_probs = transition_counts / row_sums
    
    return pd.DataFrame(transition_probs, index=regime_names, columns=regime_names)


def regime_timing_strategy(regime_df: pd.DataFrame, 
                           regime_col: str = 'regime',
                           long_regimes: list = None,
                           short_regimes: list = None) -> pd.Series:
    """
    Generate trading signals based on regime detection.
    
    Args:
        regime_df: DataFrame with regime labels
        regime_col: Column name containing regime labels
        long_regimes: List of regimes to go long
        short_regimes: List of regimes to go short
    
    Returns:
        Series with trading signals (1=long, -1=short, 0=flat)
    """
    if long_regimes is None:
        long_regimes = ['trending_low_vol', 'trending_normal_vol']
    
    if short_regimes is None:
        short_regimes = ['declining_high_vol', 'declining_normal_vol']
    
    signals = pd.Series(0, index=regime_df.index)
    
    signals[regime_df[regime_col].isin(long_regimes)] = 1
    signals[regime_df[regime_col].isin(short_regimes)] = -1
    
    return signals


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    
    # Generate sample price data with regime changes
    n_days = 500
    returns = np.concatenate([
        np.random.normal(0.002, 0.01, 150),  # Low vol uptrend
        np.random.normal(-0.001, 0.03, 100),  # High vol downtrend
        np.random.normal(0.0005, 0.015, 150),  # Normal vol sideways
        np.random.normal(0.003, 0.02, 100),  # High vol uptrend
    ])
    
    prices = 100 * np.cumprod(1 + returns)
    prices_series = pd.Series(prices, index=pd.date_range('2024-01-01', periods=n_days))
    
    # Threshold-based detection
    print("=== Threshold-Based Regime Detection ===")
    threshold_result = threshold_regime_detection(prices_series)
    print(f"Regime counts:\n{threshold_result['regime'].value_counts()}")
    
    # Gaussian Mixture detection
    print("\n=== Gaussian Mixture Regime Detection ===")
    gmm_result = gaussian_mixture_regime(prices_series, n_regimes=3)
    if not gmm_result.empty:
        print(f"Regime counts:\n{gmm_result['regime'].value_counts()}")
        
        # Regime statistics
        stats = regime_statistics(gmm_result)
        print(f"\nRegime Statistics:\n{stats}")
        
        # Transition probabilities
        transitions = regime_transitions(gmm_result)
        print(f"\nTransition Probabilities:\n{transitions.round(2)}")
