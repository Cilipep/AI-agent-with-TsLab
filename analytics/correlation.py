"""
Correlation analysis for TSLab analytics.
Rolling correlation, hierarchical clustering, correlation matrices.
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Tuple
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform


def rolling_correlation(returns_df: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """
    Calculate rolling correlation matrix for multiple instruments.
    
    Args:
        returns_df: DataFrame with instrument returns (columns = instruments)
        window: Rolling window size in periods
    
    Returns:
        DataFrame with rolling correlations
    """
    if returns_df.shape[1] < 2:
        return pd.DataFrame()
    
    n_instruments = returns_df.shape[1]
    instruments = returns_df.columns.tolist()
    
    # Calculate rolling correlation for each pair
    corr_results = {}
    
    for i in range(n_instruments):
        for j in range(i + 1, n_instruments):
            pair_name = f"{instruments[i]}_{instruments[j]}"
            corr_series = returns_df.iloc[:, i].rolling(window).corr(returns_df.iloc[:, j])
            corr_results[pair_name] = corr_series
    
    return pd.DataFrame(corr_results, index=returns_df.index)


def correlation_matrix(returns_df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
    """
    Calculate correlation matrix for multiple instruments.
    
    Args:
        returns_df: DataFrame with instrument returns
        method: Correlation method ('pearson', 'spearman', 'kendall')
    
    Returns:
        Correlation matrix DataFrame
    """
    return returns_df.corr(method=method)


def hierarchical_clustering(corr_matrix: pd.DataFrame, n_clusters: int = 3) -> dict:
    """
    Perform hierarchical clustering on correlation matrix.
    
    Args:
        corr_matrix: Correlation matrix DataFrame
        n_clusters: Number of clusters to form
    
    Returns:
        Dictionary with cluster assignments and linkage matrix
    """
    # Convert correlation to distance
    distance_matrix = 1 - corr_matrix.abs()
    
    # Ensure symmetric and zero diagonal
    np.fill_diagonal(distance_matrix.values, 0)
    distance_matrix = (distance_matrix + distance_matrix.T) / 2
    
    # Convert to condensed form
    condensed_dist = squareform(distance_matrix.values)
    
    # Perform clustering
    linkage_matrix = linkage(condensed_dist, method='ward')
    clusters = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
    
    # Create cluster assignments
    cluster_assignments = {}
    for i, instrument in enumerate(corr_matrix.columns):
        cluster_id = clusters[i]
        if cluster_id not in cluster_assignments:
            cluster_assignments[cluster_id] = []
        cluster_assignments[cluster_id].append(instrument)
    
    return {
        'clusters': cluster_assignments,
        'linkage': linkage_matrix,
        'n_clusters': n_clusters,
        'distance_matrix': distance_matrix
    }


def rolling_correlation_stats(returns_df: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """
    Calculate rolling correlation statistics (mean, std, min, max) for each pair.
    
    Args:
        returns_df: DataFrame with instrument returns
        window: Rolling window size
    
    Returns:
        DataFrame with correlation statistics
    """
    rolling_corr = rolling_correlation(returns_df, window)
    
    stats = pd.DataFrame(index=rolling_corr.columns)
    stats['mean'] = rolling_corr.mean()
    stats['std'] = rolling_corr.std()
    stats['min'] = rolling_corr.min()
    stats['max'] = rolling_corr.max()
    stats['range'] = stats['max'] - stats['min']
    
    return stats


def correlation_regime_detection(returns_df: pd.DataFrame, window: int = 60, 
                                 high_threshold: float = 0.7, low_threshold: float = 0.3) -> pd.DataFrame:
    """
    Detect correlation regimes (high, medium, low correlation periods).
    
    Args:
        returns_df: DataFrame with instrument returns
        window: Rolling window size
        high_threshold: Threshold for high correlation
        low_threshold: Threshold for low correlation
    
    Returns:
        DataFrame with correlation regime labels
    """
    if returns_df.shape[1] < 2:
        return pd.DataFrame()
    
    # Calculate average pairwise correlation
    corr_matrix = rolling_correlation(returns_df, window)
    
    # Average correlation across all pairs
    avg_corr = corr_matrix.mean(axis=1)
    
    # Label regimes
    regimes = pd.Series(index=returns_df.index, dtype=str)
    regimes[avg_corr >= high_threshold] = 'high'
    regimes[avg_corr <= low_threshold] = 'low'
    regimes[(avg_corr > low_threshold) & (avg_corr < high_threshold)] = 'medium'
    
    return pd.DataFrame({
        'avg_correlation': avg_corr,
        'regime': regimes
    })


def diversification_ratio(returns_df: pd.DataFrame, weights: Optional[np.ndarray] = None) -> float:
    """
    Calculate diversification ratio (weighted avg volatility / portfolio volatility).
    
    Args:
        returns_df: DataFrame with instrument returns
        weights: Portfolio weights (equal weight if None)
    
    Returns:
        Diversification ratio (>1 indicates diversification benefit)
    """
    n_assets = returns_df.shape[1]
    
    if weights is None:
        weights = np.ones(n_assets) / n_assets
    
    # Individual volatilities
    vols = returns_df.std().values
    
    # Weighted average volatility
    weighted_avg_vol = np.sum(weights * vols)
    
    # Portfolio volatility
    cov_matrix = returns_df.cov().values
    portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_vol = np.sqrt(portfolio_var)
    
    if portfolio_vol == 0:
        return 1.0
    
    return weighted_avg_vol / portfolio_vol


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    
    # Create sample returns for 5 instruments
    n_days = 252
    instruments = ['BTC', 'ETH', 'SOL', 'DOGE', 'ADA']
    
    returns_data = {}
    for inst in instruments:
        returns_data[inst] = np.random.normal(0.001, 0.03, n_days)
    
    returns_df = pd.DataFrame(returns_data)
    
    # Correlation matrix
    corr = correlation_matrix(returns_df)
    print("Correlation Matrix:")
    print(corr.round(2))
    
    # Hierarchical clustering
    clusters = hierarchical_clustering(corr, n_clusters=2)
    print(f"\nClusters: {clusters['clusters']}")
    
    # Diversification ratio
    div_ratio = diversification_ratio(returns_df)
    print(f"\nDiversification Ratio: {div_ratio:.2f}")
