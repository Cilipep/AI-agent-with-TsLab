import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif


FEATURE_COLS = [
    # Momentum
    "returns", "rsi", "rsi_7", "stoch_k", "stoch_d",
    "williams_r", "cci", "mfi",
    "stoch_rsi_k", "stoch_rsi_d",
    "roc_10", "roc_20", "momentum", "ultosc",
    # Trend
    "macd", "macd_signal", "macd_hist",
    "ema_10", "ema_20", "ema_50", "ema_200",
    "sma_10", "sma_20", "sma_50",
    "adx", "adx_pos", "adx_neg",
    "aroon_up", "aroon_down", "aroonosc",
    "sar", "trix", "linreg_slope",
    # Volatility
    "bb_upper", "bb_lower", "bb_width", "bb_pct",
    "atr", "atr_pct", "natr",
    # Volume
    "volume_ratio", "volume_trend", "vpt", "obv", "adosc",
    # Multi-timeframe returns
    "returns_3", "returns_5", "returns_10", "returns_20",
    # Pattern
    "cdl_doji", "cdl_engulfing", "cdl_hammer",
]


def auto_select_features(df: pd.DataFrame, y: pd.Series, max_features: int = 40) -> list:
    """Auto-select top features using Random Forest importance + mutual information."""
    # Use all available numeric columns (not just FEATURE_COLS)
    exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
    available = [c for c in df.columns if c not in exclude
                 and df[c].dtype in [np.float64, np.float32, np.int64]
                 and not df[c].isna().all()]
    if len(available) <= max_features:
        return available

    X = df[available].copy()
    X = X.fillna(0)

    # Random Forest importance
    rf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, n_jobs=1)
    rf.fit(X, y)
    rf_importance = pd.Series(rf.feature_importances_, index=available)

    # Mutual information
    mi = mutual_info_classif(X, y, random_state=42)
    mi_importance = pd.Series(mi, index=available)

    # Combined score: normalize and average
    rf_norm = (rf_importance - rf_importance.min()) / (rf_importance.max() - rf_importance.min() + 1e-8)
    mi_norm = (mi_importance - mi_importance.min()) / (mi_importance.max() - mi_importance.min() + 1e-8)
    combined = (rf_norm + mi_norm) / 2

    selected = combined.sort_values(ascending=False).head(max_features).index.tolist()
    print(f"  Auto-selected {len(selected)} features from {len(available)}")
    return selected


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
