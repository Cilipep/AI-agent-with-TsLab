"""
Tests for TSLab Analytics module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import pandas as pd
from analytics.advanced_metrics import (
    sortino_ratio,
    calmar_ratio,
    omega_ratio,
    max_drawdown,
    sharpe_ratio,
    win_rate,
    profit_factor,
    calculate_all_metrics,
)
from analytics.correlation import (
    correlation_matrix,
    hierarchical_clustering,
    diversification_ratio,
)
from analytics.regime import (
    threshold_regime_detection,
    regime_statistics,
)


class TestAdvancedMetrics:
    """Test advanced metrics functions."""
    
    def test_sortino_ratio_positive_returns(self):
        returns = np.array([0.01, 0.02, -0.005, 0.015, 0.01])
        result = sortino_ratio(returns, target_return=0)
        assert result > 0, "Sortino should be positive for positive mean returns"
    
    def test_sortino_ratio_negative_returns(self):
        returns = np.array([-0.01, -0.02, -0.005, -0.015, -0.01])
        result = sortino_ratio(returns, target_return=0)
        assert result < 0, "Sortino should be negative for negative mean returns"
    
    def test_sortino_ratio_no_downside(self):
        returns = np.array([0.01, 0.02, 0.015, 0.01, 0.005])
        result = sortino_ratio(returns, target_return=0)
        assert result == float('inf'), "Sortino should be inf when no downside"
    
    def test_calmar_ratio(self):
        returns = np.array([0.01, 0.02, -0.01, 0.015, 0.01])
        result = calmar_ratio(returns)
        assert isinstance(result, (float, int)), "Calmar should be a number"
    
    def test_omega_ratio(self):
        returns = np.array([0.01, 0.02, -0.005, 0.015, 0.01])
        result = omega_ratio(returns, threshold=0)
        assert result > 1, "Omega should be > 1 when gains exceed losses"
    
    def test_max_drawdown(self):
        returns = np.array([0.1, 0.1, -0.3, 0.1, 0.1])
        result = max_drawdown(returns)
        assert 0 <= result <= 1, "Max drawdown should be between 0 and 1"
        assert result > 0, "Max drawdown should be positive"
    
    def test_sharpe_ratio(self):
        returns = np.array([0.01, 0.02, -0.01, 0.015, 0.01])
        result = sharpe_ratio(returns)
        assert isinstance(result, (float, int)), "Sharpe should be a number"
    
    def test_win_rate(self):
        returns = np.array([0.01, -0.01, 0.02, -0.01, 0.01])
        result = win_rate(returns)
        assert 0 <= result <= 1, "Win rate should be between 0 and 1"
        assert result == 0.6, "Win rate should be 60%"
    
    def test_profit_factor(self):
        returns = np.array([0.02, -0.01, 0.03, -0.01, 0.01])
        result = profit_factor(returns)
        assert result > 1, "Profit factor should be > 1 when profitable"
    
    def test_calculate_all_metrics(self):
        returns = np.random.normal(0.001, 0.02, 252)
        metrics = calculate_all_metrics(returns)
        
        assert 'sortino_ratio' in metrics
        assert 'calmar_ratio' in metrics
        assert 'omega_ratio' in metrics
        assert 'max_drawdown' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'win_rate' in metrics
        assert 'profit_factor' in metrics


class TestCorrelation:
    """Test correlation functions."""
    
    def test_correlation_matrix(self):
        np.random.seed(42)
        returns_df = pd.DataFrame({
            'A': np.random.normal(0.001, 0.02, 100),
            'B': np.random.normal(0.001, 0.03, 100),
            'C': np.random.normal(0.001, 0.025, 100),
        })
        
        corr = correlation_matrix(returns_df)
        assert corr.shape == (3, 3), "Correlation matrix should be 3x3"
        assert np.allclose(np.diag(corr), 1), "Diagonal should be 1"
    
    def test_hierarchical_clustering(self):
        np.random.seed(42)
        returns_df = pd.DataFrame({
            'A': np.random.normal(0.001, 0.02, 100),
            'B': np.random.normal(0.001, 0.03, 100),
            'C': np.random.normal(0.001, 0.025, 100),
        })
        
        corr = correlation_matrix(returns_df)
        clusters = hierarchical_clustering(corr, n_clusters=2)
        
        assert 'clusters' in clusters
        assert len(clusters['clusters']) == 2
    
    def test_diversification_ratio(self):
        np.random.seed(42)
        returns_df = pd.DataFrame({
            'A': np.random.normal(0.001, 0.02, 100),
            'B': np.random.normal(0.001, 0.03, 100),
        })
        
        result = diversification_ratio(returns_df)
        assert result >= 1, "Diversification ratio should be >= 1"


class TestRegime:
    """Test regime detection functions."""
    
    def test_threshold_regime_detection(self):
        np.random.seed(42)
        prices = pd.Series(100 * np.cumprod(1 + np.random.normal(0.001, 0.02, 200)))
        
        result = threshold_regime_detection(prices)
        
        assert 'regime' in result.columns
        assert 'volatility' in result.columns
        assert 'trend' in result.columns
    
    def test_regime_statistics(self):
        np.random.seed(42)
        prices = pd.Series(100 * np.cumprod(1 + np.random.normal(0.001, 0.02, 200)))
        
        regime_result = threshold_regime_detection(prices)
        stats = regime_statistics(regime_result)
        
        assert 'regime' in stats.columns
        assert 'count' in stats.columns
        assert 'mean_return' in stats.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
