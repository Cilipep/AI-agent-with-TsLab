"""Shared utilities: device detection, thread management, common constants."""
import os
import torch


def get_device(preferred: str = "auto") -> torch.device:
    """Get compute device with auto-detection.

    Args:
        preferred: "auto", "cuda", "mps", or "cpu"
    """
    if preferred == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    return torch.device(preferred)


# Global instruments list — single source of truth
INSTRUMENTS = [
    ("BTCUSDT", "Bitcoin"), ("ETHUSDT", "Ethereum"), ("NEARUSDT", "NEAR"),
    ("XLMUSDT", "XLM"), ("SOLUSDT", "SOL"), ("AAVEUSDT", "AAVE"),
    ("LINKUSDT", "LINK"), ("SUIUSDT", "SUI"), ("ADAUSDT", "ADA"),
    ("BCHUSDT", "BCH"), ("TRXUSDT", "TRX"), ("UNIUSDT", "UNI"),
]


def load_data(symbol: str, suffix: str, max_bars: int = None):
    """Load CSV data from data/ directory. Single source of truth."""
    from pathlib import Path
    for prefix in ["binance_", ""]:
        cache = Path("data") / f"{prefix}{symbol}{suffix}"
        if cache.exists():
            import pandas as pd
            df = pd.read_csv(cache, index_col=0, parse_dates=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if max_bars and len(df) > max_bars:
                df = df.tail(max_bars)
            return df
    return None


def flatten_ds(dataset) -> tuple:
    """Flatten TimeSeriesDataset to numpy arrays for sklearn. Single source of truth."""
    import numpy as np
    X, y = [], []
    for i in range(len(dataset)):
        x, label = dataset[i]
        X.append(x.numpy().flatten())
        y.append(label.item())
    return np.array(X), np.array(y)
