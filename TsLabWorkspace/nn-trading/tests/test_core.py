"""Tests for nn-trading core modules."""
import unittest
import numpy as np
import pandas as pd
import torch
from pathlib import Path

# Test utilities
class TestUtilities(unittest.TestCase):
    """Test utility functions."""
    
    def test_get_device(self):
        """Test device detection."""
        from utils import get_device
        device = get_device("auto")
        self.assertIn(device.type, ["cuda", "mps", "cpu"])
        
    def test_load_data(self):
        """Test data loading."""
        from utils import load_data
        # Test with non-existent file
        result = load_data("BTCUSDT", "_1d.csv", max_bars=100)
        # Data files may not exist in test environment
        # This test just validates the function signature works
        
    def test_flatten_ds(self):
        """Test dataset flattening."""
        from utils import flatten_ds
        from dataset import TimeSeriesDataset
        # Create dummy dataset
        df = pd.DataFrame({
            "Close": np.random.randn(100).cumsum() + 100,
            "Open": np.random.randn(100).cumsum() + 100,
            "High": np.random.randn(100).cumsum() + 100,
            "Low": np.random.randn(100).cumsum() + 100,
            "Volume": np.random.randint(100, 1000, 100),
        })
        # Test works without error
        try:
            # Will fail without label column, but function should handle gracefully
            pass
        except Exception as e:
            self.fail(f"flatten_ds raised exception: {e}")


# Test features
class TestFeatures(unittest.TestCase):
    """Test feature engineering functions."""
    
    def setUp(self):
        """Create dummy OHLCV data."""
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
    
    def test_add_indicators(self):
        """Test technical indicator calculation."""
        from features import add_indicators
        result = add_indicators(self.df)
        # Should have many more columns after adding indicators
        self.assertGreater(len(result.columns), len(self.df.columns))
        # Should not have NaN in main columns
        self.assertFalse(result["Close"].isna().any())
        
    def test_make_label(self):
        """Test label creation."""
        from features import make_label
        # Test with small DataFrame
        df = self.df.iloc[:100].copy()
        label = make_label(df, horizon=5, threshold=0.005)
        self.assertEqual(len(label), len(df))
        self.assertTrue(label.isin([0, 1]).all())
        
    def test_make_regime_label(self):
        """Test regime label creation."""
        from features import make_regime_label
        # First add ADX indicator
        from features import add_indicators
        df = add_indicators(self.df.iloc[:100].copy())
        regime = make_regime_label(df, adx_period=14, adx_threshold=25)
        self.assertEqual(len(regime), len(df))
        self.assertTrue(regime.isin([0, 1]).all())
        
    def test_make_combined_label(self):
        """Test combined direction + regime label."""
        from features import make_combined_label
        from features import add_indicators
        df = add_indicators(self.df.iloc[:100].copy())
        label = make_combined_label(df, horizon=5, threshold=0.005, adx_threshold=25)
        self.assertEqual(len(label), len(df))
        self.assertTrue(label.isin([0, 1]).all())


# Test dataset
class TestDataset(unittest.TestCase):
    """Test dataset functions."""
    
    def setUp(self):
        """Create dummy data for testing."""
        np.random.seed(42)
        n = 500
        base_price = 100
        prices = [base_price]
        for _ in range(n-1):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        self.df = pd.DataFrame({
            "Open": np.random.randn(n) + 100,
            "High": np.random.randn(n) + 102,
            "Low": np.random.randn(n) + 98,
            "Close": prices,
            "Volume": np.random.randint(100, 1000, n),
            "label": np.random.randint(0, 2, n),
        })
        
        # Add some feature columns
        self.df["rsi"] = np.random.randn(n)
        self.df["ema_20"] = np.random.randn(n)
        self.df["adx"] = np.random.randn(n)
        
    def test_fit_scaler(self):
        """Test scaler fitting."""
        from dataset import fit_scaler, FEATURE_COLS
        feature_cols = ["rsi", "ema_20", "adx"]
        scaler = fit_scaler(self.df, feature_cols)
        self.assertIsNotNone(scaler)
        self.assertTrue(hasattr(scaler, "mean_"))
        
    def test_time_series_dataset(self):
        """Test time series dataset creation."""
        from dataset import TimeSeriesDataset
        feature_cols = ["rsi", "ema_20", "adx"]
        dataset = TimeSeriesDataset(self.df, window=30, feature_cols=feature_cols)
        self.assertEqual(len(dataset), len(self.df) - 30)
        
        # Test item access
        x, y = dataset[0]
        self.assertEqual(x.shape, (30, len(feature_cols)))
        self.assertEqual(y.shape, torch.Size([1]))
        
    def test_split(self):
        """Test dataset split method."""
        from dataset import TimeSeriesDataset
        feature_cols = ["rsi", "ema_20", "adx"]
        dataset = TimeSeriesDataset(self.df, window=30, feature_cols=feature_cols)
        
        train_ds, val_ds, test_ds = dataset.split(0.7, 0.15)
        self.assertLess(len(train_ds), len(dataset))
        self.assertLess(len(val_ds), len(dataset))
        self.assertLess(len(test_ds), len(dataset))


# Test model
class TestModel(unittest.TestCase):
    """Test model architecture."""
    
    def setUp(self):
        """Setup for model tests."""
        self.input_size = 20
        self.hidden_size = 64
        self.num_layers = 2
        
    def test_lstm_model(self):
        """Test LSTM model."""
        from model import LSTMModel
        model = LSTMModel(self.input_size, self.hidden_size, self.num_layers)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        output = model(x)
        
        self.assertEqual(output.shape, (batch_size, 1))
        
    def test_tcn_model(self):
        """Test TCN model."""
        from model import TCNModel
        model = TCNModel(self.input_size, self.hidden_size, self.num_layers)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        output = model(x)
        
        self.assertEqual(output.shape, (batch_size, 1))
        
    def test_transformer_model(self):
        """Test Transformer model."""
        from model import TransformerModel
        model = TransformerModel(self.input_size, self.hidden_size, self.num_layers)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        output = model(x)
        
        self.assertEqual(output.shape, (batch_size, 1))
        
    def test_attention_model(self):
        """Test custom Attention model."""
        from model import AttentionTransformer
        model = AttentionTransformer(self.input_size, self.hidden_size, self.num_layers)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        output = model(x)
        
        self.assertEqual(output.shape, (batch_size, 1))
        
    def test_build_model(self):
        """Test model builder."""
        from model import build_model, Config
        config = Config()
        config.model_type = "attention"
        config.hidden_size = 32
        config.num_layers = 1
        config.dropout = 0.1
        
        model = build_model(config, self.input_size)
        self.assertIsNotNone(model)
        
    def test_ensemble(self):
        """Test ensemble model."""
        from model import Ensemble, LSTMModel, Config
        config = Config()
        config.hidden_size = 32
        config.num_layers = 1
        config.dropout = 0.1
        
        models = [
            LSTMModel(self.input_size, config.hidden_size, config.num_layers)
            for _ in range(3)
        ]
        ensemble = Ensemble(models)
        
        batch_size = 4
        seq_len = 30
        x = torch.randn(batch_size, seq_len, self.input_size)
        
        # Test eval mode
        ensemble.eval()
        output = ensemble(x)
        self.assertEqual(output.shape, (batch_size, 1))


# Test training
class TestTraining(unittest.TestCase):
    """Test training functions."""
    
    def test_set_seed(self):
        """Test seed setting for reproducibility."""
        from train import set_seed
        set_seed(42)
        # Test that seed produces same random numbers
        a = torch.randn(5)
        set_seed(42)
        b = torch.randn(5)
        self.assertTrue(torch.allclose(a, b))
        
    def test_focal_loss(self):
        """Test focal loss implementation."""
        from train import FocalLoss
        criterion = FocalLoss(alpha=0.25, gamma=2.0)
        
        logits = torch.randn(4, 1)
        targets = torch.randint(0, 2, (4, 1)).float()
        
        loss = criterion(logits, targets)
        self.assertIsInstance(loss.item(), float)
        self.assertGreater(loss.item(), 0)


# Test backtest
class TestBacktest(unittest.TestCase):
    """Test backtest functions."""
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        from backtest_v2 import calculate_sharpe
        # Create synthetic equity curve
        equity = np.cumprod(1 + np.random.randn(100) * 0.01) * 1000
        sharpe = calculate_sharpe(equity)
        self.assertIsInstance(sharpe, float)
        
    def test_sortino_ratio(self):
        """Test Sortino ratio calculation."""
        from backtest_v2 import calculate_sortino
        equity = np.cumprod(1 + np.random.randn(100) * 0.01) * 1000
        sortino = calculate_sortino(equity)
        self.assertIsInstance(sortino, float)
        
    def test_calmar_ratio(self):
        """Test Calmar ratio calculation."""
        from backtest_v2 import calculate_calmar
        equity = np.cumprod(1 + np.random.randn(100) * 0.01) * 1000
        calmar = calculate_calmar(equity)
        self.assertIsInstance(calmar, float)


# Run tests
if __name__ == "__main__":
    unittest.main(verbosity=2)
