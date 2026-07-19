"""Test utilities module."""
import unittest
import torch
from utils import get_device, load_data, flatten_ds


class TestGetDevice(unittest.TestCase):
    """Test device detection."""
    
    def test_auto_device(self):
        """Test auto device detection."""
        device = get_device("auto")
        self.assertIn(device.type, ["cuda", "mps", "cpu"])
        
    def test_cpu_device(self):
        """Test explicit CPU device."""
        device = get_device("cpu")
        self.assertEqual(device.type, "cpu")
        
    def test_cuda_device(self):
        """Test CUDA device if available."""
        if torch.cuda.is_available():
            device = get_device("cuda")
            self.assertEqual(device.type, "cuda")
        else:
            device = get_device("cuda")
            # Should fall back to cpu if CUDA not available
            self.assertIn(device.type, ["cuda", "cpu"])


class TestLoadData(unittest.TestCase):
    """Test data loading."""
    
    def test_nonexistent_file(self):
        """Test loading non-existent file."""
        result = load_data("BTCUSDT", "_1d.csv")
        self.assertIsNone(result)
        
    def test_with_max_bars(self):
        """Test loading with max_bars limit."""
        result = load_data("BTCUSDT", "_1d.csv", max_bars=100)
        # If file exists, should be limited to 100 bars
        if result is not None:
            self.assertLessEqual(len(result), 100)


class TestFlattenDS(unittest.TestCase):
    """Test dataset flattening."""
    
    def test_flatten(self):
        """Test flattening TimeSeriesDataset."""
        from dataset import TimeSeriesDataset
        import pandas as pd
        import numpy as np
        
        # Create minimal test dataset
        n = 100
        df = pd.DataFrame({
            "Close": np.random.randn(n).cumsum() + 100,
            "label": np.random.randint(0, 2, n),
        })
        
        dataset = TimeSeriesDataset(df, window=10, feature_cols=["Close"])
        
        # Test flattening
        X, y = flatten_ds(dataset)
        expected_samples = n - 10  # len(dataset)
        self.assertEqual(X.shape[0], expected_samples)
        self.assertEqual(y.shape[0], expected_samples)


if __name__ == "__main__":
    unittest.main(verbosity=2)
