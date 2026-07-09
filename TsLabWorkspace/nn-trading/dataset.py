import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler


FEATURE_COLS = [
    "returns", "rsi", "stoch_k", "williams_r",
    "macd", "macd_signal", "macd_hist",
    "ema_10", "ema_20", "adx",
    "bb_upper", "bb_lower", "bb_width", "atr",
]

# Add volume_ratio if present — handled dynamically
VOLUME_COL = "volume_ratio"


class TimeSeriesDataset(Dataset):
    def __init__(self, df: pd.DataFrame, window: int, feature_cols: list[str] = None,
                 scaler: StandardScaler = None):
        self.window = window
        self.cols = [c for c in (feature_cols or FEATURE_COLS) if c in df.columns]

        raw = df[self.cols].values.astype(np.float32)
        if scaler is None:
            self.scaler = StandardScaler()
            self.scaler.fit(raw)
        else:
            self.scaler = scaler
        self.scaled = self.scaler.transform(raw)

        self.labels = df["label"].values.astype(np.float32)
        self.n = len(df) - window

    def __len__(self):
        return self.n

    def __getitem__(self, idx):
        x = self.scaled[idx : idx + self.window]  # (window, features)
        y = self.labels[idx + self.window]          # scalar
        return torch.tensor(x), torch.tensor(y)

    def split(self, train_ratio: float, val_ratio: float):
        n = self.n
        t = int(n * train_ratio)
        v = int(n * (train_ratio + val_ratio))
        return (
            torch.utils.data.Subset(self, range(0, t)),
            torch.utils.data.Subset(self, range(t, v)),
            torch.utils.data.Subset(self, range(v, n)),
        )
