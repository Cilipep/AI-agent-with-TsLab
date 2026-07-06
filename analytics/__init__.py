"""
TSLab Analytics Module
Advanced financial metrics, correlation analysis, and regime detection.
"""

from .advanced_metrics import (
    sortino_ratio,
    calmar_ratio,
    omega_ratio,
    max_drawdown,
    sharpe_ratio,
    win_rate,
    profit_factor,
    calculate_all_metrics,
)

from .correlation import (
    rolling_correlation,
    correlation_matrix,
    hierarchical_clustering,
    diversification_ratio,
)

from .regime import (
    threshold_regime_detection,
    gaussian_mixture_regime,
    regime_statistics,
    regime_transitions,
)

from .generate_report import AnalyticsReport

__all__ = [
    # Advanced metrics
    'sortino_ratio',
    'calmar_ratio',
    'omega_ratio',
    'max_drawdown',
    'sharpe_ratio',
    'win_rate',
    'profit_factor',
    'calculate_all_metrics',
    
    # Correlation
    'rolling_correlation',
    'correlation_matrix',
    'hierarchical_clustering',
    'diversification_ratio',
    
    # Regime
    'threshold_regime_detection',
    'gaussian_mixture_regime',
    'regime_statistics',
    'regime_transitions',
    
    # Report
    'AnalyticsReport',
]
