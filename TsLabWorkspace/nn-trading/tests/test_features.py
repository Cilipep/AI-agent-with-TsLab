"""Test features module."""
import unittest
import numpy as np
import pandas as pd
from features import (
    add_indicators, make_label, make_regime_label, 
    make_combined_label, prepare_features, add_gerchik_features
)


class TestAddIndicators(unittest.TestCase):
    """Test technical indicator calculation."""
    
    def setUp(self):
        """Create OHLCV test data."""
        np.random.seed(42)
        n = 1000
        base_price = 100
        prices = [base_price]
        for _ in range(n-1):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        self.df = pd.DataFrame({
            "Open": prices,
            "High": [max(p, p + abs(np.random.randn()) * 2) for p in prices],
            "Low": [min(p, p - abs(np.random.randn()) * 2) for p in prices],
            "Close": prices,
            "Volume": np.random.randint(100, 1000, n),
        })
        
    def test_adds_indicators(self):
        """Test that indicators are added."""
        result = add_indicators(self.df)
        self.assertGreater(len(result.columns), len(self.df.columns))
        
    def test_no_nan_main_columns(self):
        """Test that main columns don't have NaN."""
        result = add_indicators(self.df)
        self.assertFalse(result["Close"].isna().any())
        
    def test_has_technical_indicators(self):
        """Test that specific indicators are present."""
        result = add_indicators(self.df)
        
        # Test for some common indicators
        expected_indicators = ["sma_20", "ema_20", "rsi", "adx", "atr", "macd"]
        for indicator in expected_indicators:
            self.assertIn(indicator, result.columns, f"Missing indicator: {indicator}")
            
    def test_volume_indicators(self):
        """Test volume indicators are calculated."""
        result = add_indicators(self.df)
        
        # Should have volume-based indicators
        volume_indicators = ["obv", "adosc", "vwap"]
        for indicator in volume_indicators:
            self.assertIn(indicator, result.columns, f"Missing volume indicator: {indicator}")


class TestMakeLabel(unittest.TestCase):
    """Test label creation."""
    
    def setUp(self):
        """Create test data."""
        np.random.seed(42)
        n = 100
        prices = [100]
        for _ in range(n-1):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        self.df = pd.DataFrame({
            "Close": prices,
        })
        
    def test_label_shape(self):
        """Test label has correct shape."""
        label = make_label(self.df, horizon=5, threshold=0.005)
        self.assertEqual(len(label), len(self.df))
        
    def test_label_values(self):
        """Test label contains only 0 and 1."""
        label = make_label(self.df, horizon=5, threshold=0.005)
        unique_values = label.unique()
        self.assertTrue(all(v in [0, 1] for v in unique_values))
        
    def test_threshold_effect(self):
        """Test that higher threshold reduces positive labels."""
        label_low = make_label(self.df, horizon=5, threshold=0.001)
        label_high = make_label(self.df, horizon=5, threshold=0.01)
        
        # Higher threshold should have fewer positive labels
        self.assertLess(label_high.sum(), label_low.sum())


class TestMakeRegimeLabel(unittest.TestCase):
    """Test regime label creation."""
    
    def setUp(self):
        """Create test data with trends."""
        np.random.seed(42)
        n = 100
        prices = [100]
        for _ in range(n-1):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        self.df = pd.DataFrame({
            "High": [p + abs(np.random.randn()) for p in prices],
            "Low": [p - abs(np.random.randn()) for p in prices],
            "Close": prices,
        })
        
    def test_regime_label_shape(self):
        """Test regime label shape."""
        from features import add_indicators
        df = add_indicators(self.df)
        regime = make_regime_label(df)
        self.assertEqual(len(regime), len(df))
        
    def test_regime_values(self):
        """Test regime contains only 0 and 1."""
        from features import add_indicators
        df = add_indicators(self.df)
        regime = make_regime_label(df)
        unique_values = regime.unique()
        self.assertTrue(all(v in [0, 1] for v in unique_values))


class TestMakeCombinedLabel(unittest.TestCase):
    """Test combined direction + regime label."""
    
    def setUp(self):
        """Create test data."""
        np.random.seed(42)
        n = 100
        prices = [100]
        for _ in range(n-1):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        self.df = pd.DataFrame({
            "High": [p + abs(np.random.randn()) for p in prices],
            "Low": [p - abs(np.random.randn()) for p in prices],
            "Close": prices,
        })
        
    def test_combined_label_shape(self):
        """Test combined label shape."""
        label = make_combined_label(self.df)
        self.assertEqual(len(label), len(self.df))
        
    def test_combined_label_values(self):
        """Test combined label values."""
        label = make_combined_label(self.df)
        unique_values = label.unique()
        self.assertTrue(all(v in [0, 1] for v in unique_values))


class TestPrepareFeatures(unittest.TestCase):
    """Test full feature preparation pipeline."""
    
    def setUp(self):
        """Create test data."""
        np.random.seed(42)
        n = 500
        prices = [100]
        for _ in range(n-1):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        self.df = pd.DataFrame({
            "Open": np.random.randn(n) + 100,
            "High": np.random.randn(n) + 102,
            "Low": np.random.randn(n) + 98,
            "Close": prices,
            "Volume": np.random.randint(100, 1000, n),
        })
        
        from config import Config
        self.config = Config()
        
    def test_prepare_features(self):
        """Test feature preparation completes."""
        result = prepare_features(self.df, self.config)
        self.assertGreater(len(result.columns), len(self.df.columns))
        self.assertIn("label", result.columns)
        
    def test_no_nan_in_result(self):
        """Test no NaN values after preparation."""
        result = prepare_features(self.df, self.config)
        self.assertFalse(result.isna().any().any())


if __name__ == "__main__":
    unittest.main(verbosity=2)
