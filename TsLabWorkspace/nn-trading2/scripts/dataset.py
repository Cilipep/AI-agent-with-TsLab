import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler


def fit_scaler(df, feature_cols):
    scaler = StandardScaler()
    data = df[feature_cols].values
    scaler.fit(data)
    return scaler


class TimeSeriesDataset(Dataset):
    def __init__(self, df, window, feature_cols, scaler=None, label_col='label'):
        self.window = window
        self.feature_cols = feature_cols
        self.label_col = label_col

        self.features = df[feature_cols].values.astype(np.float32)
        self.labels = df[label_col].values.astype(np.float32)

        if scaler is not None:
            self.features = scaler.transform(self.features).astype(np.float32)

        self.features = np.nan_to_num(self.features, nan=0.0)
        self.labels = np.nan_to_num(self.labels, nan=0.0)

    def __len__(self):
        return len(self.features) - self.window

    def __getitem__(self, idx):
        x = self.features[idx:idx + self.window]
        y = self.labels[idx + self.window]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
