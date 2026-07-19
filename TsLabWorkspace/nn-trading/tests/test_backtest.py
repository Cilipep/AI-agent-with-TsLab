"""Test backtest module."""
import unittest
import numpy as np
from backtest_v2 import calculate_sharpe, calculate_sortino, calculate_calmar


class TestSharpeRatio(unittest.TestCase):
    """Test Sharpe ratio calculation."""
    
    def test_sharpe_positive(self):
        """Test Sharpe ratio for profitable equity curve."""
        # Profitable equity curve
        equity = np.cumprod(1 + np.linspace(0.001, 0.005, 100)) * 1000
        sharpe = calculate_sharpe(equity)
        
        self.assertIsInstance(sharpe, float)
        self.assertGreater(sharpe, 0)
        
    def test_sharpe_negative(self):
        """Test Sharpe ratio for losing equity curve."""
        # Losing equity curve
        equity = np.cumprod(1 + np.linspace(-0.005, -0.001, 100)) * 1000
        sharpe = calculate_sharpe(equity)
        
        self.assertIsInstance(sharpe, float)
        self.assertLess(sharpe, 0)
        
    def test_sharpe_small_sample(self):
        """Test Sharpe ratio with small sample."""
        equity = np.array([1000, 1010, 1020, 1015, 1030])
        sharpe = calculate_sharpe(equity)
        
        self.assertIsInstance(sharpe, float)
        
    def test_sharpe_flat(self):
        """Test Sharpe ratio for flat equity curve."""
        equity = np.ones(100) * 1000
        sharpe = calculate_sharpe(equity)
        
        # Should be 0 or close to 0 for flat curve
        self.assertAlmostEqual(sharpe, 0, places=5)


class TestSortinoRatio(unittest.TestCase):
    """Test Sortino ratio calculation."""
    
    def test_sortino_positive(self):
        """Test Sortino ratio for profitable equity curve."""
        equity = np.cumprod(1 + np.linspace(0.001, 0.005, 100)) * 1000
        sortino = calculate_sortino(equity)
        
        self.assertIsInstance(sortino, float)
        self.assertGreater(sortino, 0)
        
    def test_sortino_negative(self):
        """Test Sortino ratio for losing equity curve."""
        equity = np.cumprod(1 + np.linspace(-0.005, -0.001, 100)) * 1000
        sortino = calculate_sortino(equity)
        
        self.assertIsInstance(sortino, float)
        self.assertLess(sortino, 0)
        
    def test_sortino_small_sample(self):
        """Test Sortino ratio with small sample."""
        equity = np.array([1000, 1010, 1020, 1015, 1030])
        sortino = calculate_sortino(equity)
        
        self.assertIsInstance(sortino, float)


class TestCalmarRatio(unittest.TestCase):
    """Test Calmar ratio calculation."""
    
    def test_calmar_positive(self):
        """Test Calmar ratio for profitable equity curve."""
        equity = np.cumprod(1 + np.linspace(0.001, 0.005, 100)) * 1000
        calmar = calculate_calmar(equity)
        
        self.assertIsInstance(calmar, float)
        self.assertGreater(calmar, 0)
        
    def test_calmar_negative(self):
        """Test Calmar ratio for losing equity curve."""
        equity = np.cumprod(1 + np.linspace(-0.005, -0.001, 100)) * 1000
        calmar = calculate_calmar(equity)
        
        self.assertIsInstance(calmar, float)
        self.assertLess(calmar, 0)
        
    def test_calmar_small_sample(self):
        """Test Calmar ratio with small sample."""
        equity = np.array([1000, 1010, 1020, 1015, 1030])
        calmar = calculate_calmar(equity)
        
        self.assertIsInstance(calmar, float)
        
    def test_calmar_max_drawdown_zero(self):
        """Test Calmar ratio when max drawdown is zero."""
        equity = np.ones(100) * 1000
        calmar = calculate_calmar(equity)
        
        # Should be 0 for flat curve
        self.assertEqual(calmar, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
