"""Binance Testnet Paper Trading - uses cached data for training, live price for trading."""
import os
import torch

import time, json, hmac, hashlib, random
import numpy as np
import pandas as pd
import requests
from pathlib import Path
from datetime import datetime, timezone

from config import Config
from dataset import TimeSeriesDataset, auto_select_features, fit_scaler
from model import build_model, build_sklearn_models, HybridEnsemble
from train import train
from features import make_label


# Binance Testnet
BASE_URL = "https://testnet.binance.vision"
API_KEY = os.environ.get("BINANCE_TESTNET_API_KEY", "")
API_SECRET = os.environ.get("BINANCE_TESTNET_API_SECRET", "")


def sign_request(params: dict) -> dict:
    """Sign request with HMAC-SHA256."""
    params["timestamp"] = int(time.time() * 1000)
    # Must sort alphabetically for Binance
    query = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params


def get_live_price(symbol: str) -> float:
    """Get current price from testnet."""
    url = f"{BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return float(resp.json()["price"])


def get_balance() -> dict:
    """Get USDT balance from testnet."""
    if not API_KEY:
        return {"USDT": 10000.0}

    params = {"recvWindow": 60000}
    params = sign_request(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    resp = requests.get(f"{BASE_URL}/api/v3/account", params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    balances = resp.json().get("balances", [])
    return {b["asset"]: float(b["free"]) for b in balances if float(b["free"]) > 0}


def get_positions() -> dict:
    """Get current positions."""
    if not API_KEY:
        return {}

    params = {"recvWindow": 60000}
    params = sign_request(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    resp = requests.get(f"{BASE_URL}/api/v3/account", params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    balances = resp.json().get("balances", [])
    return {b["asset"]: float(b["free"]) for b in balances if float(b["free"]) > 0}


def place_order(symbol: str, side: str, quantity: float) -> dict:
    """Place market order on testnet."""
    if not API_KEY:
        print(f"  [MOCK] {side} {quantity} {symbol}")
        return {"status": "MOCK_FILLED", "side": side, "quantity": quantity}

    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "recvWindow": 60000,
    }
    params = sign_request(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    resp = requests.post(f"{BASE_URL}/api/v3/order", params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def train_model_from_cache(name: str, cfg) -> tuple:
    """Train ensemble from cached historical data."""
    data_path = f"data/binance_{name}USDT_3tf.csv"
    if not Path(data_path).exists():
        print(f"  ERROR: {data_path} not found")
        return None, []

    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    print(f"  Loaded {len(df)} bars from cache")

    df["label"] = make_label(df, cfg.horizon, cfg.threshold).values
    df = df.dropna()

    exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
    feature_cols = [c for c in df.columns if c not in exclude
                   and df[c].dtype in [np.float64, np.float32, np.int64]]
    if len(feature_cols) > cfg.max_features:
        feature_cols = auto_select_features(df, df["label"], max_features=cfg.max_features)

    print(f"  Features: {len(feature_cols)}")

    # Fit scaler ONLY on first 85% (training data) — prevent data leakage
    train_df = df.iloc[:int(len(df) * 0.85)]
    scaler = fit_scaler(train_df, feature_cols)
    ds = TimeSeriesDataset(df, cfg.window, feature_cols=feature_cols, scaler=scaler)

    val_split = int(len(ds) * 0.85)
    train_ds = torch.utils.data.Subset(ds, range(0, val_split))
    val_ds = torch.utils.data.Subset(ds, range(val_split, len(ds)))

    seeds = [42 + i * 17 for i in range(cfg.n_models)]
    base_models = []
    for seed in seeds:
        torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)
        m = build_model(cfg, len(feature_cols))
        m = train(m, train_ds, val_ds, cfg, "cpu", quiet=True)
        base_models.append(m)
        print(f"  Trained NN model (seed={seed})")

    X, y = [], []
    for i in range(len(train_ds)):
        x, label = train_ds[i]
        X.append(x.numpy().flatten())
        y.append(label.item())
    X = np.array(X)
    y = np.array(y)

    sklearn_wrappers = build_sklearn_models(X, y, cfg.window, len(feature_cols), n_cpu=2)
    all_sklearn = [w for _, w in sklearn_wrappers]

    ensemble = HybridEnsemble(base_models, all_sklearn)
    return ensemble, feature_cols


def predict_signal(ensemble, df: pd.DataFrame, cfg, feature_cols: list, scaler=None) -> float:
    """Get prediction from ensemble using cached data."""
    df = df.copy()
    df["label"] = make_label(df, cfg.horizon, cfg.threshold).values
    df = df.dropna()

    if scaler is None:
        # Fallback: fit on this data (less accurate, but functional)
        scaler = fit_scaler(df, feature_cols)
    ds = TimeSeriesDataset(df, cfg.window, feature_cols=feature_cols, scaler=scaler)

    if len(ds) == 0:
        return 0.5

    x, _ = ds[len(ds)-1]
    x = x.unsqueeze(0)

    ensemble.eval()
    with torch.no_grad():
        prob = torch.sigmoid(ensemble(x)).item()

    return prob


def run_trading_loop(symbol: str, name: str, cfg, interval_minutes: int = 60):
    """Main trading loop."""
    print(f"\n{'='*60}")
    print(f"TRADING: {name}")
    print(f"{'='*60}")

    # Train model from cached data (with retry)
    print("\nTraining model from cached data...")
    ensemble, feature_cols = None, None
    for attempt in range(3):
        ensemble, feature_cols = train_model_from_cache(name, cfg)
        if ensemble is not None:
            break
        print(f"  Attempt {attempt+1}/3 failed, retrying in 10s...")
        time.sleep(10)

    if ensemble is None:
        print("Failed to train model after 3 attempts. Exiting.")
        return

    # Load cached data for predictions
    data_path = f"data/binance_{symbol}_3tf.csv"
    if not Path(data_path).exists():
        data_path = f"data/{symbol}_3tf.csv"
    df_cached = pd.read_csv(data_path, index_col=0, parse_dates=True)

    all_results = []
    position = None  # Track position: {"side": "LONG", "entry_price": ..., "qty": ...}

    while True:
        try:
            now = datetime.now(timezone.utc)
            print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S UTC')}]")

            # Get live price
            live_price = get_live_price(symbol)
            print(f"  Live price: {live_price:.4f}")

            # Get prediction
            prob = predict_signal(ensemble, df_cached, cfg, feature_cols)
            signal = "BUY" if prob > 0.5 else "SELL" if prob < 0.4 else "HOLD"
            print(f"  Signal: {signal} (prob={prob:.4f})")

            # Get balance
            balance = get_balance()
            usdt = balance.get("USDT", 0)
            asset_qty = balance.get(name, 0)
            print(f"  Balance: {usdt:.2f} USDT | {asset_qty:.4f} {name}")

            # Trading logic
            if signal == "BUY" and position is None and usdt > 100:
                # Buy $1000 (5% of balance), min notional is ~$5
                target_usd = min(1000, usdt * 0.05)
                raw_qty = target_usd / live_price
                # Round to valid step: 0.1 for NEAR, 0.01 for SOL
                precision = 1 if "NEAR" in name else 2
                qty = round(raw_qty, precision)
                if qty * live_price >= 5:  # Min notional check
                    print(f"  -> BUY {qty} {name} @ {live_price:.4f} (${qty * live_price:.2f})")
                    order = place_order(symbol, "BUY", qty)
                    print(f"  Order: {order.get('status', 'UNKNOWN')}")
                    position = {"side": "LONG", "entry_price": live_price, "qty": qty}
                    all_results.append({
                        "time": now.isoformat(),
                        "action": "BUY",
                        "price": live_price,
                        "qty": qty,
                        "prob": prob,
                    })

            elif signal == "SELL" and position is not None:
                # Sell position
                qty = position["qty"]
                print(f"  -> SELL {qty} {name} @ {live_price:.4f}")
                order = place_order(symbol, "SELL", qty)
                pnl = (live_price - position["entry_price"]) / position["entry_price"] * 100
                print(f"  Order: {order.get('status', 'UNKNOWN')} | PnL: {pnl:+.2f}%")
                all_results.append({
                    "time": now.isoformat(),
                    "action": "SELL",
                    "price": live_price,
                    "qty": qty,
                    "pnl_pct": round(pnl, 2),
                    "prob": prob,
                })
                position = None

            # Save results
            with open(f"results/testnet_{name.lower()}_log.json", "w") as f:
                json.dump(all_results, f, indent=2)

            print(f"\n  Waiting {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(60)


def main():
    if not API_KEY:
        print("=" * 60)
        print("WARNING: No API keys! Running in MOCK mode.")
        print("=" * 60)

    # Optimized params from Optuna walk-forward (5-fold validated)
    INSTRUMENTS = {
        "ETH": {
            "symbol": "ETHUSDT",
            "params": {
                "hidden_size": 32, "num_layers": 2, "dropout": 0.4899, "nhead": 8,
                "window": 20, "max_features": 40, "batch_size": 128,
                "learning_rate": 0.000181, "stop_loss_pct": 0.0332, "take_profit_pct": 0.0852,
            },
        },
        "SOL": {
            "symbol": "SOLUSDT",
            "params": {
                "hidden_size": 16, "num_layers": 2, "dropout": 0.3037, "nhead": 4,
                "window": 30, "max_features": 40, "batch_size": 128,
                "learning_rate": 0.000209, "stop_loss_pct": 0.0415, "take_profit_pct": 0.1030,
            },
        },
        "XLM": {
            "symbol": "XLMUSDT",
            "params": {
                "hidden_size": 16, "num_layers": 1, "dropout": 0.3443, "nhead": 4,
                "window": 40, "max_features": 40, "batch_size": 32,
                "learning_rate": 0.000232, "stop_loss_pct": 0.0236, "take_profit_pct": 0.0810,
            },
        },
        "NEAR": {
            "symbol": "NEARUSDT",
            "params": {
                "hidden_size": 32, "num_layers": 2, "dropout": 0.3246, "nhead": 4,
                "window": 30, "max_features": 50, "batch_size": 32,
                "learning_rate": 0.000253, "stop_loss_pct": 0.0256, "take_profit_pct": 0.1111,
            },
        },
        "AAVE": {
            "symbol": "AAVEUSDT",
            "params": {
                "hidden_size": 16, "num_layers": 2, "dropout": 0.4361, "nhead": 4,
                "window": 40, "max_features": 30, "batch_size": 64,
                "learning_rate": 0.000335, "stop_loss_pct": 0.0209, "take_profit_pct": 0.1196,
            },
        },
    }

    for name, cfg_data in INSTRUMENTS.items():
        cfg = Config()
        for k, v in cfg_data["params"].items():
            setattr(cfg, k, v)
        cfg.n_models = 3
        cfg.epochs = 15
        cfg.patience = 5

        run_trading_loop(cfg_data["symbol"], name, cfg, interval_minutes=60)


if __name__ == "__main__":
    main()
