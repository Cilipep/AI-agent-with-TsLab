"""
Tests for TSLab Risk Management module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import pandas as pd
from risk.position_sizing import (
    kelly_criterion,
    kelly_from_trades,
    atr_position_size,
    fixed_fractional,
    volatility_adjusted_size,
    calculate_atr,
    optimal_position_size,
)


class TestKellyCriterion:
    """Test Kelly Criterion calculations."""
    
    def test_kelly_positive_edge(self):
        # 60% win rate, 1.5:1 win/loss ratio
        result = kelly_criterion(win_rate=0.6, avg_win=1.5, avg_loss=1.0)
        assert result > 0, "Kelly should be positive with positive edge"
        assert result <= 1, "Kelly should be <= 1"
    
    def test_kelly_no_edge(self):
        # 50% win rate, 1:1 ratio = no edge
        result = kelly_criterion(win_rate=0.5, avg_win=1.0, avg_loss=1.0)
        assert result == 0, "Kelly should be 0 with no edge"
    
    def test_kelly_negative_edge(self):
        # 40% win rate, 1:1 ratio = negative edge
        result = kelly_criterion(win_rate=0.4, avg_win=1.0, avg_loss=1.0)
        assert result == 0, "Kelly should be 0 with negative edge"
    
    def test_kelly_fraction(self):
        # Full Kelly vs quarter Kelly
        full = kelly_criterion(win_rate=0.6, avg_win=1.5, avg_loss=1.0, kelly_fraction=1.0)
        quarter = kelly_criterion(win_rate=0.6, avg_win=1.5, avg_loss=1.0, kelly_fraction=0.25)
        assert quarter == full * 0.25, "Quarter Kelly should be 25% of full Kelly"
    
    def test_kelly_from_trades(self):
        trades = pd.DataFrame({
            'pnl': [100, -50, 150, -80, 120, -60, 90]
        })
        
        result = kelly_from_trades(trades, kelly_fraction=0.25)
        assert 0 <= result <= 1, "Kelly from trades should be between 0 and 1"


class TestATRPositionSize:
    """Test ATR-based position sizing."""
    
    def test_atr_basic(self):
        result = atr_position_size(
            capital=10000,
            risk_per_trade_pct=0.01,
            atr=2.5,
            point_value=1.0
        )
        assert result > 0, "ATR position size should be positive"
        assert result <= 200, "Position size should be reasonable"
    
    def test_atr_zero_atr(self):
        result = atr_position_size(
            capital=10000,
            risk_per_trade_pct=0.01,
            atr=0,
            point_value=1.0
        )
        assert result == 0, "ATR position size should be 0 with zero ATR"
    
    def test_atr_max_position(self):
        result = atr_position_size(
            capital=10000,
            risk_per_trade_pct=0.10,
            atr=0.1,
            point_value=1.0,
            max_position_pct=0.2
        )
        max_possible = 10000 * 0.2 / 0.1
        assert result <= max_possible, "Should not exceed max position"


class TestFixedFractional:
    """Test fixed fractional position sizing."""
    
    def test_fixed_basic(self):
        result = fixed_fractional(
            capital=10000,
            risk_pct=0.02,
            stop_loss_pct=0.05
        )
        assert 0 <= result <= 1, "Fixed fractional should be between 0 and 1"
        assert result == 0.4, "Should be 40% (2% risk / 5% stop)"
    
    def test_fixed_tight_stop(self):
        result = fixed_fractional(
            capital=10000,
            risk_pct=0.02,
            stop_loss_pct=0.01
        )
        assert result == 1.0, "Should be capped at 100%"


class TestVolatilityAdjusted:
    """Test volatility-adjusted position sizing."""
    
    def test_vol_basic(self):
        result = volatility_adjusted_size(
            capital=10000,
            target_risk_pct=0.02,
            current_volatility=0.02,
            base_volatility=0.02
        )
        assert result == 0.02, "Should be target risk when vol matches base"
    
    def test_vol_high_volatility(self):
        result = volatility_adjusted_size(
            capital=10000,
            target_risk_pct=0.02,
            current_volatility=0.04,  # Double base vol
            base_volatility=0.02
        )
        assert result < 0.02, "Should reduce size when volatility is high"
    
    def test_vol_low_volatility(self):
        result = volatility_adjusted_size(
            capital=10000,
            target_risk_pct=0.02,
            current_volatility=0.01,  # Half base vol
            base_volatility=0.02
        )
        assert result > 0.02, "Should increase size when volatility is low"


class TestATRCalculation:
    """Test ATR calculation."""
    
    def test_calculate_atr(self):
        prices = pd.DataFrame({
            'open': [100, 102, 101, 103, 102],
            'high': [103, 104, 103, 105, 104],
            'low': [99, 101, 100, 102, 101],
            'close': [102, 103, 102, 104, 103]
        })
        
        atr = calculate_atr(prices, period=3)
        assert len(atr) == len(prices), "ATR should have same length as input"
        assert atr.iloc[-1] > 0, "ATR should be positive"


class TestOptimalPositionSize:
    """Test optimal position size routing."""
    
    def test_optimal_kelly(self):
        result = optimal_position_size(
            capital=10000,
            method='kelly',
            win_rate=0.6,
            avg_win=1.5,
            avg_loss=1.0
        )
        assert result > 0, "Optimal Kelly should be positive"
    
    def test_optimal_atr(self):
        result = optimal_position_size(
            capital=10000,
            method='atr',
            risk_per_trade_pct=0.01,
            atr=2.5
        )
        assert result > 0, "Optimal ATR should be positive"
    
    def test_optimal_unknown_method(self):
        with pytest.raises(ValueError):
            optimal_position_size(capital=10000, method='unknown')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
