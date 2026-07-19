"""Probability calibration module."""
import numpy as np
from pathlib import Path


class PlattScaler:
    """Platt scaling (sigmoid calibration) for probability calibration."""
    
    def __init__(self):
        self.A = None
        self.B = None
        self.is_fitted = False
    
    def fit(self, logits, targets):
        """
        Fit Platt scaling parameters.
        
        Args:
            logits: Raw model outputs (pre-sigmoid)
            targets: Binary labels (0 or 1)
        
        Returns:
            Self (fitted calibrator)
        """
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
        
        for _ in range(n_iter):
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
        """Save calibration parameters to JSON."""
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"A": self.A, "B": self.B}, f, indent=2)
    
    def load(self, path):
        """Load calibration parameters from JSON."""
        import json
        with open(path, "r", encoding="utf-8") as f:
            params = json.load(f)
        self.A = params["A"]
        self.B = params["B"]
        self.is_fitted = True


class IsotonicCalibrator:
    """Isotonic regression calibration for probability calibration."""
    
    def __init__(self, min_prob=0.0, max_prob=1.0):
        self.min_prob = min_prob
        self.max_prob = max_prob
        self.bins = None
        self.calibrated_probs = None
        self.is_fitted = False
    
    def fit(self, probs, targets):
        """
        Fit isotonic regression using pool adjacent violators algorithm.
        
        Args:
            probs: Original probabilities
            targets: Binary labels
        
        Returns:
            Self (fitted calibrator)
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
            bin_idx = np.searchsorted(self.bins, p, side="right") - 1
            bin_idx = max(0, min(bin_idx, len(self.calibrated_probs) - 1))
            calibrated[i] = self.calibrated_probs[bin_idx]
        
        return np.clip(calibrated, self.min_prob, self.max_prob)
    
    def save(self, path):
        """Save calibration parameters to JSON."""
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "bins": self.bins.tolist(),
                "calibrated_probs": self.calibrated_probs.tolist()
            }, f, indent=2)
    
    def load(self, path):
        """Load calibration parameters from JSON."""
        import json
        with open(path, "r", encoding="utf-8") as f:
            params = json.load(f)
        self.bins = np.array(params["bins"])
        self.calibrated_probs = np.array(params["calibrated_probs"])
        self.is_fitted = True


def calibrate_ensemble_probs(ensemble, val_ds, test_ds, device="cpu"):
    """
    Calibrate ensemble probabilities using validation set.
    
    Args:
        ensemble: Trained ensemble model
        val_ds: Validation dataset
        test_ds: Test dataset
        device: Computation device
    
    Returns:
        tuple: (calibrator, calibration_results)
    """
    import torch
    from sklearn.metrics import brier_score_loss, log_loss
    
    ensemble.eval()
    
    # Get validation predictions
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
    
    # Fit Platt scaler
    platt = PlattScaler()
    platt.fit(val_logits, val_targets)
    
    # Get test predictions
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
    
    # Calibrate
    test_probs_original = 1.0 / (1.0 + np.exp(-test_logits))
    test_probs_calibrated = platt.calibrate(test_logits)
    
    # Compare
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
    
    return platt, results


if __name__ == "__main__":
    # Test the calibrators
    print("Testing probability calibrators...")
    
    # Generate test data
    np.random.seed(42)
    logits = np.random.randn(1000) * 3
    probs_true = 1.0 / (1.0 + np.exp(-logits))
    targets = (np.random.rand(1000) < probs_true).astype(int)
    
    # Test Platt scaling
    platt = PlattScaler()
    platt.fit(logits, targets)
    test_logits = np.random.randn(100) * 3
    test_probs = platt.calibrate(test_logits)
    
    print(f"✓ Platt scaling: range [{test_probs.min():.3f}, {test_probs.max():.3f}]")
    
    # Test isotonic
    probs = np.random.rand(1000)
    targets = (np.random.rand(1000) < probs).astype(int)
    
    isotonic = IsotonicCalibrator()
    isotonic.fit(probs, targets)
    test_probs = isotonic.calibrate(np.random.rand(100))
    
    print(f"✓ Isotonic calibration: range [{test_probs.min():.3f}, {test_probs.max():.3f}]")
    
    print("\nCalibrators ready to use!")
