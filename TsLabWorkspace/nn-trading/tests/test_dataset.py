"""Test dataset module."""
import unittest
import numpy as np
import pandas as pd
import torch
from dataset import TimeSeriesDataset, auto_select_features, fit_scaler, FEATURE_COLS


class TestFitScaler(unittest.TestCase):
    """Test scaler fitting."""
    
    def setUp(self):
        """Create test data."""
        np.random.seed(42)
        n = 100
        self.df = pd.DataFrame({
            "Close": np.random.randn(n).cumsum() + 100,
            "Open": np.random.randn(n) + 100,
            "High": np.random.randn(n) + 102,
            "Low": np.random.randn(n) + 98,
            "Volume": np.random.randint(100, 1000, n),
            "rsi": np.random.randn(n),
            "ema_20": np.random.randn(n),
            "adx": np.random.randn(n),
        })
        
    def test_fit_scaler(self):
        """Test scaler can be fitted."""
        feature_cols = ["rsi", "ema_20", "adx"]
        scaler = fit_scaler(self.df, feature_cols)
        
        self.assertIsNotNone(scaler)
        self.assertTrue(hasattr(scaler, "mean_"))
        self.assertTrue(hasattr(scaler, "scale_"))
        
    def test_scaler_fitted_shape(self):
        """Test scaler has correct shape."""
        feature_cols = ["rsi", "ema_20", "adx"]
        scaler = fit_scaler(self.df, feature_cols)
        
        self.assertEqual(len(scaler.mean_), len(feature_cols))
        self.assertEqual(len(scaler.scale_), len(feature_cols))


class TestTimeSeriesDataset(unittest.TestCase):
    """Test TimeSeriesDataset class."""
    
    def setUp(self):
        """Create test data."""
        np.random.seed(42)
        n = 200
        base_price = 100
        prices = [base_price]
        for _ in range(n-1):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        self.df = pd.DataFrame({
            "Close": prices,
            "Open": np.random.randn(n) + 100,
            "High": np.random.randn(n) + 102,
            "Low": np.random.randn(n) + 98,
            "Volume": np.random.randint(100, 1000, n),
            "label": np.random.randint(0, 2, n),
        })
        
        # Add feature columns
        self.df["rsi"] = np.random.randn(n)
        self.df["ema_20"] = np.random.randn(n)
        self.df["adx"] = np.random.randn(n)
        
        self.feature_cols = ["rsi", "ema_20", "adx"]
        self.window = 30
        
    def test_dataset_length(self):
        """Test dataset length is correct."""
        dataset = TimeSeriesDataset(
            self.df, 
            window=self.window, 
            feature_cols=self.feature_cols
        )
        
        expected_length = len(self.df) - self.window
        self.assertEqual(len(dataset), expected_length)
        
    def test_item_shape(self):
        """Test item has correct shape."""
        dataset = TimeSeriesDataset(
            self.df, 
            window=self.window, 
            feature_cols=self.feature_cols
        )
        
        x, y = dataset[0]
        
        self.assertEqual(x.shape, torch.Size([self.window, len(self.feature_cols)]))
        self.assertEqual(y.shape, torch.Size([1]))
        
    def test_item_types(self):
        """Test item types are correct."""
        dataset = TimeSeriesDataset(
            self.df, 
            window=self.window, 
            feature_cols=self.feature_cols
        )
        
        x, y = dataset[0]
        
        self.assertIsInstance(x, torch.Tensor)
        self.assertIsInstance(y, torch.Tensor)
        
    def test_split(self):
        """Test dataset split method."""
        dataset = TimeSeriesDataset(
            self.df, 
            window=self.window, 
            feature_cols=self.feature_cols
        )
        
        train_ratio = 0.7
        val_ratio = 0.15
        
        train_ds, val_ds, test_ds = dataset.split(train_ratio, val_ratio)
        
        # All splits should be subsets of original
        self.assertLess(len(train_ds), len(dataset))
        self.assertLess(len(val_ds), len(dataset))
        self.assertLess(len(test_ds), len(dataset))
        
        # Total should be close to original
        total = len(train_ds) + len(val_ds) + len(test_ds)
        self.assertEqual(total, len(dataset))


class TestAutoSelectFeatures(unittest.TestCase):
    """Test automatic feature selection."""
    
    def setUp(self):
        """Create test data."""
        np.random.seed(42)
        n = 200
        base_price = 100
        prices = [base_price]
        for _ in range(n-1):
            change = np.random.randn() * 2
            prices.append(prices[-1] + change)
        
        # Create many feature columns
        feature_names = [f"feature_{i}" for i in range(50)]
        feature_dict = {name: np.random.randn(n) for name in feature_names}
        
        self.df = pd.DataFrame({
            "Close": prices,
            "Open": np.random.randn(n) + 100,
            "High": np.random.randn(n) + 102,
            "Low": np.random.randn(n) + 98,
            "Volume": np.random.randint(100, 1000, n),
            "label": np.random.randint(0, 2, n),
        })
        self.df.update(feature_dict)
        
    def test_auto_select_features(self):
        """Test feature selection works."""
        y = self.df["label"]
        selected = auto_select_features(self.df, y, max_features=20)
        
        self.assertLessEqual(len(selected), 20)
        self.assertIsInstance(selected, list)
        
    def test_selected_features_in_df(self):
        """Test selected features exist in dataframe."""
        y = self.df["label"]
        selected = auto_select_features(self.df, y, max_features=10)
        
        for feature in selected:
            self.assertIn(feature, self.df.columns)
            
    def test_excludes_label_columns(self):
        """Test label columns are excluded."""
        y = self.df["label"]
        selected = auto_select_features(self.df, y, max_features=5)
        
        excluded = {"Open", "High", "Low", "Close", "Volume", "label"}
        for feature in selected:
            self.assertNotIn(feature, excluded)


if __name__ == "__main__":
    unittest.main(verbosity=2)
