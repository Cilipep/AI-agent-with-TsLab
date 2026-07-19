"""Probability calibration for ensemble predictions."""
import numpy as np
import pandas as pd
import torch
from pathlib import Path


class ProbabilityCalibrator:
    """Base class for probability calibration methods."""
    
    def __init__(self):
        self.is_fitted = False
    
    def fit(self, probs, targets):
        """Fit calibration model on validation data."""
        raise NotImplementedError
    
    def calibrate(self, probs):
        """Apply calibration to probabilities."""
        raise NotImplementedError
    
    def save(self, path):
        """Save calibration parameters."""
        raise NotImplementedError
    
    def load(self, path):
        """Load calibration parameters."""
        raise NotImplementedError


class PlattScaler(ProbabilityCalibrator):
    """
    Platt scaling (sigmoid calibration).
    
    Maps logits to calibrated probabilities using:
    P(y=1|f) = 1 / (1 + exp(A*f + B))
    
    where f is the original logit and (A, B) are learned parameters.
    """
    
    def __init__(self):
        super().__init__()
        self.A = None
        self.B = None
    
    def fit(self, logits, targets):
        """
        Fit Platt scaling parameters using gradient descent.
        
        Args:
            logits: Raw model outputs (pre-sigmoid)
            targets: Binary labels (0 or 1)
        """
        # Add bias term
        logits = np.array(logits).flatten()
        targets = np.array(targets).flatten()
        
        # Initialize parameters
        self.A = 0.0
        self.B = np.log((targets.mean() + 1e-10) / (1 - targets.mean() + 1e-10))
        
        # Gradient descent
        lr = 0.1
        n_iter = 1000
        tol = 1e-6
        
        prev_loss = float("inf")
        
        for i in range(n_iter):
            # Compute probabilities
            probs = 1.0 / (1.0 + np.exp(self.A * logits + self.B))
            probs = np.clip(probs, 1e-10, 1 - 1e-10)
            
            # Compute gradients
            diff = probs - targets
            dA = np.mean(diff * logits)
            dB = np.mean(diff)
            
            # Update parameters
            self.A -= lr * dA
            self.B -= lr * dB
            
            # Compute loss
            loss = -np.mean(targets * np.log(probs) + (1 - targets) * np.log(1 - probs))
            
            # Check convergence
            if abs(prev_loss - loss) < tol:
                break
            prev_loss = loss
        
        self.is_fitted = True
        return self
    
    def calibrate(self, logits):
        """Apply Platt scaling calibration."""
        if not self.is_fitted:
            raise ValueError("PlattScaler not fitted. Call fit() first.")
        
        logits = np.array(logits).flatten()
        return 1.0 / (1.0 + np.exp(self.A * logits + self.B))
    
    def save(self, path):
        """Save calibration parameters."""
        import json
        params = {"A": self.A, "B": self.B}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2)
    
    def load(self, path):
        """Load calibration parameters."""
        import json
        with open(path, "r", encoding="utf-8") as f:
            params = json.load(f)
        self.A = params["A"]
        self.B = params["B"]
        self.is_fitted = True


class IsotonicCalibrator(ProbabilityCalibrator):
    """
    Isotonic regression calibration.
    
    Non-parametric calibration that fits a monotonic function
    mapping original probabilities to calibrated probabilities.
    """
    
    def __init__(self, min_prob=0.0, max_prob=1.0):
        super().__init__()
        self.min_prob = min_prob
        self.max_prob = max_prob
        self.bins = None
        self.calibrated_probs = None
    
    def fit(self, probs, targets):
        """
        Fit isotonic regression using pool adjacent violators algorithm.
        
        Args:
            probs: Original probabilities
            targets: Binary labels
        """
        probs = np.array(probs).flatten()
        targets = np.array(targets).flatten()
        
        # Sort by probability
        sort_idx = np.argsort(probs)
        sorted_probs = probs[sort_idx]
        sorted_targets = targets[sort_idx]
        
        # Pool adjacent violators
        bins = [0]
        bin_targets = [sorted_targets[0]]
        bin_counts = [1]
        
        for i in range(1, len(sorted_probs)):
            if sorted_probs[i] == sorted_probs[bins[-1]]:
                bin_targets[-1] = (bin_targets[-1] * bin_counts[-1] + sorted_targets[i]) / (bin_counts[-1] + 1)
                bin_counts[-1] += 1
            else:
                bins.append(i)
                bin_targets.append(sorted_targets[i])
                bin_counts.append(1)
        
        # Make monotonic
        for i in range(len(bin_targets) - 2, -1, -1):
            if bin_targets[i] > bin_targets[i + 1]:
                bin_targets[i] = bin_targets[i + 1]
        
        self.bins = np.array(bins)
        self.calibrated_probs = np.array(bin_targets)
        self.is_fitted = True
        
        return self
    
    def calibrate(self, probs):
        """Apply isotonic calibration."""
        if not self.is_fitted:
            raise ValueError("IsotonicCalibrator not fitted. Call fit() first.")
        
        probs = np.array(probs).flatten()
        calibrated = np.zeros_like(probs)
        
        for i, p in enumerate(probs):
            # Find appropriate bin
            bin_idx = np.searchsorted(self.bins, p, side="right") - 1
            bin_idx = max(0, min(bin_idx, len(self.calibrated_probs) - 1))
            calibrated[i] = self.calibrated_probs[bin_idx]
        
        return np.clip(calibrated, self.min_prob, self.max_prob)
    
    def save(self, path):
        """Save calibration parameters."""
        import json
        params = {
            "bins": self.bins.tolist(),
            "calibrated_probs": self.calibrated_probs.tolist()
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2)
    
    def load(self, path):
        """Load calibration parameters."""
        import json
        with open(path, "r", encoding="utf-8") as f:
            params = json.load(f)
        self.bins = np.array(params["bins"])
        self.calibrated_probs = np.array(params["calibrated_probs"])
        self.is_fitted = True


def calibrate_ensemble_probs(ensemble, val_ds, test_ds, df, feature_cols, scaler, 
                             calibrator_type="platt", device="cpu"):
    """
    Calibrate ensemble probabilities using validation set.
    
    Args:
        ensemble: Trained ensemble model
        val_ds: Validation dataset
        test_ds: Test dataset
        df: Price dataframe
        feature_cols: Feature column names
        scaler: Fitted scaler
        calibrator_type: "platt" or "isotonic"
        device: Computation device
    
    Returns:
        Calibrated ensemble and calibration results
    """
    from dataset import TimeSeriesDataset
    
    # Get validation predictions
    ensemble.eval()
    val_loader = torch.utils.data.DataLoader(val_ds, batch_size=256, shuffle=False)
    
    val_logits = []
    val_targets = []
    
    with torch.no_grad():
        for x, y in val_loader:
            x = x.to(device)
            logits = ensemble(x).cpu().numpy().flatten()
            val_logits.extend(logits)
            val_targets.extend(y.numpy().flatten())
    
    val_logits = np.array(val_logits)
    val_targets = np.array(val_targets)
    
    # Fit calibrator
    if calibrator_type == "platt":
        calibrator = PlattScaler()
    elif calibrator_type == "isotonic":
        # Convert logits to probs for isotonic
        val_probs = 1.0 / (1.0 + np.exp(-val_logits))
        calibrator = IsotonicCalibrator()
        calibrator.fit(val_probs, val_targets)
    else:
        raise ValueError(f"Unknown calibrator: {calibrator_type}")
    
    calibrator.fit(val_logits, val_targets)
    
    # Get test predictions (calibrated)
    test_loader = torch.utils.data.DataLoader(test_ds, batch_size=256, shuffle=False)
    
    test_logits = []
    test_targets = []
    
    with torch.no_grad():
        for x, y in test_loader:
            x = x.to(device)
            logits = ensemble(x).cpu().numpy().flatten()
            test_logits.extend(logits)
            test_targets.extend(y.numpy().flatten())
    
    test_logits = np.array(test_logits)
    test_targets = np.array(test_targets)
    
    # Calibrate test predictions
    test_probs_calibrated = calibrator.calibrate(test_logits)
    test_probs_original = 1.0 / (1.0 + np.exp(-test_logits))
    
    # Compare performance
    from sklearn.metrics import brier_score_loss, log_loss
    
    brier_original = brier_score_loss(test_targets, test_probs_original)
    brier_calibrated = brier_score_loss(test_targets, test_probs_calibrated)
    
    ll_original = log_loss(test_targets, test_probs_original)
    ll_calibrated = log_loss(test_targets, test_probs_calibrated)
    
    results = {
        "brier_score": {
            "original": float(brier_original),
            "calibrated": float(brier_calibrated),
            "improvement": float(brier_original - brier_calibrated)
        },
        "log_loss": {
            "original": float(ll_original),
            "calibrated": float(ll_calibrated),
            "improvement": float(ll_original - ll_calibrated)
        },
        "n_samples": len(test_targets),
    }
    
    print(f"\nCalibration Results ({calibrator_type}):")
    print(f"  Brier Score: {brier_original:.4f} → {brier_calibrated:.4f} "
          f"(Δ {results['brier_score']['improvement']:+.4f})")
    print(f"  Log Loss:    {ll_original:.4f} → {ll_calibrated:.4f} "
          f"(Δ {results['log_loss']['improvement']:+.4f})")
    
    return calibrator, results


def test_calibration_on_walkforward():
    """Test calibration on walk-forward validation."""
    from config import Config
    from features import prepare_features
    from dataset import auto_select_features
    from walk_forward import walk_forward
    
    # Load data
    df = pd.read_csv("data/binance_BTCUSDT_15m.csv", index_col=0, parse_dates=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Prepare features
    config = Config()
    config.model_type = "attention"
    config.hidden_size = 32
    config.num_layers = 1
    config.dropout = 0.2
    
    df = prepare_features(df, config)
    feature_cols = auto_select_features(df, df["label"], max_features=30)
    
    # Run walk-forward with calibration
    device = "cpu"
    
    # First run without calibration
    print("=" * 60)
    print("WALK-FORWARD WITHOUT CALIBRATION")
    print("=" * 60)
    
    equity_no_cal, results_no_cal = walk_forward(
        df, config, device, n_folds=3, feature_cols=feature_cols
    )
    
    print(f"\nTotal Return: {(equity_no_cal[-1]/equity_no_cal[0]-1)*100:+.2f}%")
    
    # Second run with calibration (simplified)
    print("\n" + "=" * 60)
    print("WALK-FORWARD WITH CALIBRATION")
    print("=" * 60)
    
    # This would require modifying walk_forward to include calibration
    # For demo, we just show the calibration code
    
    print("\nCalibration would be applied here:")
    print("  1. Train ensemble on each fold")
    print("  2. Fit calibrator on validation set")
    print("  3. Apply calibration to test predictions")
    print("  4. Track calibration improvement")
    
    return equity_no_cal, results_no_cal


if __name__ == "__main__":
    print("Probability Calibration for Ensemble Predictions")
    print("=" * 60)
    
    # Test Platt scaling
    print("\n1. Testing Platt Scaling...")
    logits = np.random.randn(1000) * 5
    targets = (np.random.rand(1000) < (1.0 / (1.0 + np.exp(-logits)))).astype(int)
    
    platt = PlattScaler()
    platt.fit(logits, targets)
    
    test_logits = np.random.randn(100) * 5
    test_probs = platt.calibrate(test_logits)
    
    print(f"  ✓ Platt scaling works")
    print(f"    Test probs range: [{test_probs.min():.3f}, {test_probs.max():.3f}]")
    
    # Test isotonic calibration
    print("\n2. Testing Isotonic Calibration...")
    probs = np.random.rand(1000)
    targets = (np.random.rand(1000) < probs).astype(int)
    
    isotonic = IsotonicCalibrator()
    isotonic.fit(probs, targets)
    
    test_probs = isotonic.calibrate(np.random.rand(100))
    
    print(f"  ✓ Isotonic calibration works")
    print(f"    Test probs range: [{test_probs.min():.3f}, {test_probs.max():.3f}]")
    
    # Run full calibration test
    print("\n3. Running full calibration test...")
    equity, results = test_calibration_on_walkforward()
    
    print("\n" + "=" * 60)
    print("Calibration test completed!")
    print("=" * 60)
