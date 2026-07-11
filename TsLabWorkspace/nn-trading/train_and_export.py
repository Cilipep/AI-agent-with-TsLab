"""
Train NN Trading model with best features and export to ONNX.

Usage:
    python train_and_export.py --symbol BTCUSDT --interval 1d --epochs 50
    python train_and_export.py --symbol ETHUSDT --interval 1h --epochs 30
"""
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import argparse
import json
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from pathlib import Path
from datetime import datetime, timezone
import requests
import time

# ============================================================
# 1. DATA DOWNLOAD
# ============================================================

def download_klines(symbol: str, interval: str, days: int) -> pd.DataFrame:
    """Download klines from Binance API."""
    base_url = "https://api.binance.com/api/v3"
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 24 * 3600 * 1000

    all_frames = []
    current = start_ms

    while current < end_ms:
        params = {"symbol": symbol, "interval": interval, "limit": 1000, "startTime": current}
        resp = requests.get(f"{base_url}/klines", params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break

        df = pd.DataFrame(data, columns=[
            "Open_time", "Open", "High", "Low", "Close", "Volume",
            "Close_time", "Quote_volume", "Trades", "Taker_buy_base", "Taker_buy_quote", "Ignore",
        ])
        df["Open_time"] = pd.to_datetime(df["Open_time"], unit="ms")
        df.set_index("Open_time", inplace=True)
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = df[col].astype(float)
        all_frames.append(df[["Open", "High", "Low", "Close", "Volume"]])

        current = int(df.index[-1].timestamp() * 1000) + 1
        time.sleep(0.25)

    if not all_frames:
        raise ValueError(f"No data downloaded for {symbol}")

    full = pd.concat(all_frames).drop_duplicates().sort_index()
    return full


# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute comprehensive technical indicators."""
    import talib

    df = df.copy()
    c = df["Close"].values.astype(np.float64)
    h = df["High"].values.astype(np.float64)
    l = df["Low"].values.astype(np.float64)
    v = df["Volume"].values.astype(np.float64)

    # Trend
    df["ema10"] = talib.EMA(c, 10)
    df["ema20"] = talib.EMA(c, 20)
    df["ema50"] = talib.EMA(c, 50)
    df["sma20"] = talib.SMA(c, 20)
    df["adx"] = talib.ADX(h, l, c, 14)
    macd, sig, hist = talib.MACD(c)
    df["macd"] = macd
    df["macd_sig"] = sig
    df["macd_hist"] = hist

    # Momentum
    df["rsi"] = talib.RSI(c, 14)
    df["rsi7"] = talib.RSI(c, 7)
    df["stoch_k"], df["stoch_d"] = talib.STOCH(h, l, c)
    df["willr"] = talib.WILLR(h, l, c, 14)
    df["cci"] = talib.CCI(h, l, c, 14)
    df["roc"] = talib.ROC(c, 10)
    df["mom"] = talib.MOM(c, 10)

    # Volatility
    bu, bm, bl = talib.BBANDS(c, 20)
    df["bb_w"] = (bu - bl) / bm
    df["bb_pct"] = (c - bl) / (bu - bl + 1e-8)
    df["atr"] = talib.ATR(h, l, c, 14)
    df["natr"] = talib.NATR(h, l, c, 14)

    # Volume
    if v.sum() > 0:
        df["obv"] = talib.OBV(c, v)
        df["mfi"] = talib.MFI(h, l, c, v, 14)

    # Multi-timeframe returns
    for p in [3, 5, 10, 20]:
        df[f"ret_{p}"] = df["Close"].pct_change(p)

    # Price relative to MAs
    df["pvs_ema10"] = c / (df["ema10"] + 1e-8) - 1
    df["pvs_ema20"] = c / (df["ema20"] + 1e-8) - 1
    df["pvs_ema50"] = c / (df["ema50"] + 1e-8) - 1

    # Returns
    df["returns"] = df["Close"].pct_change()
    df["log_ret"] = np.log(c / np.roll(c, 1))

    return df


def create_label(df: pd.DataFrame, horizon: int = 5, threshold: float = 0.001) -> pd.Series:
    """Create classification label: 1 if price goes up by more than threshold."""
    future_return = df["Close"].shift(-horizon) / df["Close"] - 1
    return (future_return > threshold).astype(int)


def select_features(df: pd.DataFrame, y: pd.Series, max_features: int = 40) -> list:
    """Auto-select best features using Random Forest importance + mutual information."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_selection import mutual_info_classif

    exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
    available = [c for c in df.columns if c not in exclude
                 and df[c].dtype in [np.float64, np.float32, np.int64]
                 and not df[c].isna().all()]

    if len(available) <= max_features:
        return available

    X = df[available].fillna(0)
    y_valid = y.loc[X.index]

    # RF importance
    rf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, n_jobs=1)
    rf.fit(X, y_valid)
    rf_imp = pd.Series(rf.feature_importances_, index=available)

    # Mutual information
    mi = mutual_info_classif(X, y_valid, random_state=42)
    mi_imp = pd.Series(mi, index=available)

    # Combined score
    rf_n = (rf_imp - rf_imp.min()) / (rf_imp.max() - rf_imp.min() + 1e-8)
    mi_n = (mi_imp - mi_imp.min()) / (mi_imp.max() - mi_imp.min() + 1e-8)
    combined = (rf_n + mi_n) / 2

    selected = combined.sort_values(ascending=False).head(max_features).index.tolist()
    print(f"  Selected {len(selected)} features from {len(available)}")
    return selected


# ============================================================
# 3. DATASET
# ============================================================

class TimeSeriesDataset:
    def __init__(self, features: np.ndarray, labels: np.ndarray, window: int, scaler=None):
        self.window = window
        self.features = features.astype(np.float32)
        self.labels = labels.astype(np.float32)

        if scaler is None:
            self.scaler = StandardScaler()
            self.scaler.fit(self.features)
        else:
            self.scaler = scaler

        self.scaled = self.scaler.transform(self.features)
        self.n = len(self.scaled) - window

    def __len__(self):
        return self.n

    def __getitem__(self, idx):
        x = self.scaled[idx:idx + self.window]
        y = self.labels[idx + self.window]
        return torch.tensor(x), torch.tensor(y)


# ============================================================
# 4. MODELS
# ============================================================

class AttentionTransformer(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, nhead=8, dropout=0.35):
        super().__init__()
        self.input_proj = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.pos_enc = PositionalEncoding(hidden_size, dropout)
        nhead = min(nhead, hidden_size // 16)
        self.blocks = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=hidden_size, nhead=nhead, dim_feedforward=hidden_size * 4,
                dropout=dropout, batch_first=True, activation="gelu", norm_first=True,
            ) for _ in range(num_layers)
        ])
        self.head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1),
        )

    def forward(self, x):
        x = self.input_proj(x)
        x = self.pos_enc(x)
        for block in self.blocks:
            x = block(x)
        return self.head(x[:, -1, :])


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(0, max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return self.dropout(x + self.pe[:, :x.size(1), :])


# ============================================================
# 5. TRAINING
# ============================================================

def train_model(model, train_loader, val_loader, config, device, epochs=50):
    """Train model with early stopping."""
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=0.01)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    best_val_loss = float("inf")
    best_state = None
    patience = 10
    patience_counter = 0

    for epoch in range(epochs):
        # Train
        model.train()
        total_loss, correct, total = 0, 0, 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device).unsqueeze(1)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item() * x.size(0)
            correct += ((out > 0.5).float() == y).sum().item()
            total += x.size(0)
        scheduler.step()

        # Validate
        model.eval()
        val_loss, val_correct, val_total = 0, 0, 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device).unsqueeze(1)
                out = model(x)
                val_loss += criterion(out, y).item() * x.size(0)
                val_correct += ((out > 0.5).float() == y).sum().item()
                val_total += x.size(0)

        val_loss /= val_total
        val_acc = val_correct / val_total

        if epoch % 10 == 0:
            print(f"  Epoch {epoch:3d} | val_loss={val_loss:.4f} acc={val_acc:.3f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping at epoch {epoch}")
                break

    if best_state:
        model.load_state_dict(best_state)
    return model


# ============================================================
# 6. MAIN PIPELINE
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Train NN Trading model and export to ONNX")
    parser.add_argument("--symbol", default="BTCUSDT", help="Binance symbol")
    parser.add_argument("--interval", default="1d", help="Kline interval (1m,5m,15m,1h,4h,1d)")
    parser.add_argument("--days", type=int, default=1820, help="Days of history")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--window", type=int, default=30, help="Lookback window")
    parser.add_argument("--hidden", type=int, default=64, help="Hidden size")
    parser.add_argument("--layers", type=int, default=2, help="Number of layers")
    parser.add_argument("--dropout", type=float, default=0.35, help="Dropout rate")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--max-features", type=int, default=40, help="Max features to select")
    parser.add_argument("--output-dir", default="models", help="Output directory")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Create output directory
    Path(args.output_dir).mkdir(exist_ok=True)

    # 1. Download data
    print(f"\n{'='*60}")
    print(f"1. Downloading {args.symbol} {args.interval} ({args.days} days)")
    print(f"{'='*60}")
    df = download_klines(args.symbol, args.interval, args.days)
    print(f"  Downloaded {len(df)} bars")

    # 2. Compute features
    print(f"\n{'='*60}")
    print("2. Computing features")
    print(f"{'='*60}")
    df = compute_features(df)
    print(f"  {len(df.columns)} columns")

    # 3. Create labels
    df["label"] = create_label(df, horizon=5, threshold=0.001)
    df = df.dropna()
    print(f"  {len(df)} rows after dropna")

    # 4. Select features
    print(f"\n{'='*60}")
    print(f"3. Selecting top {args.max_features} features")
    print(f"{'='*60}")
    feature_cols = select_features(df, df["label"], max_features=args.max_features)

    # 5. Prepare data
    print(f"\n{'='*60}")
    print("4. Preparing datasets")
    print(f"{'='*60}")
    X = df[feature_cols].values.astype(np.float32)
    y = df["label"].values.astype(np.float32)

    # Train/val/test split (70/15/15)
    n = len(X)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)

    # Fit scaler on train only
    scaler = StandardScaler()
    scaler.fit(X[:train_end])

    train_ds = TimeSeriesDataset(X[:train_end], y[:train_end], args.window, scaler)
    val_ds = TimeSeriesDataset(X[:val_end], y[:val_end], args.window, scaler)
    test_ds = TimeSeriesDataset(X, y, args.window, scaler)

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False)

    print(f"  Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

    # 6. Train model
    print(f"\n{'='*60}")
    print("5. Training model")
    print(f"{'='*60}")
    model = AttentionTransformer(
        input_size=len(feature_cols),
        hidden_size=args.hidden,
        num_layers=args.layers,
        dropout=args.dropout,
    ).to(device)

    config = {"lr": args.lr}
    model = train_model(model, train_loader, val_loader, config, device, epochs=args.epochs)

    # 7. Evaluate
    print(f"\n{'='*60}")
    print("6. Evaluating on test set")
    print(f"{'='*60}")
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for x, y in test_loader:
            x = x.to(device)
            preds = (torch.sigmoid(model(x)) > 0.5).float()
            all_preds.extend(preds.cpu().numpy().flatten())
            all_labels.extend(y.numpy())

    acc = accuracy_score(all_labels, all_preds)
    print(f"  Test Accuracy: {acc:.4f}")
    print(f"  Test samples: {len(all_labels)}")

    # 8. Export to ONNX
    print(f"\n{'='*60}")
    print("7. Exporting to ONNX")
    print(f"{'='*60}")
    model.eval()
    dummy = torch.randn(1, args.window, len(feature_cols)).to(device)
    onnx_path = f"{args.output_dir}/{args.symbol}_{args.interval}.onnx"

    torch.onnx.export(
        model, dummy, onnx_path,
        export_params=True,
        opset_version=18,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    )

    import os
    size = os.path.getsize(onnx_path)
    print(f"  Saved: {onnx_path} ({size/1024:.1f} KB)")

    # 9. Save metadata
    metadata = {
        "symbol": args.symbol,
        "interval": args.interval,
        "window": args.window,
        "hidden_size": args.hidden,
        "num_layers": args.layers,
        "dropout": args.dropout,
        "features": feature_cols,
        "test_accuracy": float(acc),
        "train_samples": len(train_ds),
        "val_samples": len(val_ds),
        "test_samples": len(test_ds),
        "total_bars": len(df),
        "created_at": datetime.now().isoformat(),
        "onnx_path": onnx_path,
    }

    meta_path = f"{args.output_dir}/{args.symbol}_{args.interval}_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata: {meta_path}")

    # 10. Save scaler for TSLab integration
    import pickle
    scaler_path = f"{args.output_dir}/{args.symbol}_{args.interval}_scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump({"scaler": scaler, "features": feature_cols, "window": args.window}, f)
    print(f"  Scaler: {scaler_path}")

    print(f"\n{'='*60}")
    print("DONE!")
    print(f"{'='*60}")
    print(f"  Model: {onnx_path}")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Window: {args.window}")
    print(f"  Test Accuracy: {acc:.4f}")


if __name__ == "__main__":
    main()
