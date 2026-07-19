# Neural Network Signal via WebSocket
# Stream live predictions from TSLab to external clients

# Requirements:
#   pip install websockets asyncio aiohttp

import asyncio
import json
import websockets
import aiohttp
import torch
import numpy as np
import pandas as pd
from pathlib import Path

from config import Config
from dataset import TimeSeriesDataset, auto_select_features, fit_scaler
from model import build_model, HybridEnsemble
from features import make_label

# TSLab API
API_BASE = "http://localhost:5000/api"

# WebSocket server settings
WS_HOST = "localhost"
WS_PORT = 8765
WS_PATH = "/signal"

# Trading config
TRADING_CONFIG = {
    "NEAR": {
        "symbol": "NEARUSDT",
        "params": {
            "hidden_size": 32, "num_layers": 2, "dropout": 0.3246, "nhead": 4,
            "window": 30, "max_features": 50, "batch_size": 32,
            "learning_rate": 0.000253, "stop_loss_pct": 0.0256, "take_profit_pct": 0.1111,
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
}


class SignalStreamer:
    def __init__(self, symbol: str, cfg: Config):
        self.symbol = symbol
        self.cfg = cfg
        self.model = None
        self.feature_cols = None
        self.scaler = None
        self.df_cached = None
        self.clients = set()

    async def load_model(self):
        """Load ensemble model from cached data."""
        data_path = f"data/binance_{self.symbol}_3tf.csv"
        if not Path(data_path).exists():
            raise FileNotFoundError(f"Data not found: {data_path}")

        self.df_cached = pd.read_csv(data_path, index_col=0, parse_dates=True)
        self.df_cached["label"] = make_label(self.df_cached, self.cfg.horizon, self.cfg.threshold).values
        self.df_cached = self.df_cached.dropna()

        exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
        self.feature_cols = [c for c in self.df_cached.columns if c not in exclude
                            and self.df_cached[c].dtype in [np.float64, np.float32, np.int64]]
        if len(self.feature_cols) > self.cfg.max_features:
            self.feature_cols = auto_select_features(self.df_cached, self.df_cached["label"], 
                                                    max_features=self.cfg.max_features)

        # Fit scaler on first 85%
        train_df = self.df_cached.iloc[:int(len(self.df_cached) * 0.85)]
        self.scaler = fit_scaler(train_df, self.feature_cols)

        # Build and train ensemble
        ds = TimeSeriesDataset(self.df_cached, self.cfg.window, 
                              feature_cols=self.feature_cols, scaler=self.scaler)
        val_split = int(len(ds) * 0.85)
        train_ds = torch.utils.data.Subset(ds, range(0, val_split))
        val_ds = torch.utils.data.Subset(ds, range(val_split, len(ds)))

        # Load saved ensemble (if exists) or train new
        ensemble_path = f"models/ensemble_{self.symbol.lower()}.pt"
        if Path(ensemble_path).exists():
            self.model = HybridEnsemble.load(ensemble_path, [], [], device="cpu")
            print(f"  Loaded saved ensemble: {ensemble_path}")
        else:
            # Train new ensemble (simplified)
            base_models = []
            for seed in [42, 59, 83]:
                torch.manual_seed(seed)
                m = build_model(self.cfg, len(self.feature_cols))
                m = train(m, train_ds, val_ds, self.cfg, "cpu", quiet=True)
                base_models.append(m)

            # Simplified sklearn wrappers
            sklearn_wrappers = []
            self.model = HybridEnsemble(base_models, sklearn_wrappers)

            # Save
            Path("models").mkdir(exist_ok=True)
            self.model.save(ensemble_path)
            print(f"  Saved ensemble: {ensemble_path}")

    async def predict(self) -> float:
        """Get latest prediction from ensemble."""
        if self.model is None:
            return 0.5

        ds = TimeSeriesDataset(self.df_cached, self.cfg.window,
                              feature_cols=self.feature_cols, scaler=self.scaler)
        if len(ds) == 0:
            return 0.5

        x, _ = ds[len(ds) - 1]
        x = x.unsqueeze(0)

        self.model.eval()
        with torch.no_grad():
            prob = torch.sigmoid(self.model(x)).item()

        return prob

    async def broadcast_signal(self):
        """Broadcast signal to all connected clients."""
        prob = await self.predict()
        signal = "BUY" if prob > 0.5 else "SELL" if prob < 0.4 else "HOLD"

        message = json.dumps({
            "timestamp": pd.Timestamp.now().isoformat(),
            "symbol": self.symbol,
            "signal": signal,
            "probability": round(prob, 4),
            "confidence": round(abs(prob - 0.5) * 2, 4),  # 0-1 scale
        })

        if self.clients:
            print(f"  Broadcasting: {signal} (p={prob:.4f})")
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
        else:
            print(f"  No clients connected. Signal: {signal} (p={prob:.4f})")

    async def register_client(self, websocket):
        """Add new client to broadcast list."""
        self.clients.add(websocket)
        print(f"  Client connected. Total: {len(self.clients)}")
        try:
            await websocket.send(json.dumps({
                "type": "connected",
                "symbol": self.symbol,
                "message": "Signal streaming started",
            }))
            await self.broadcast_signal()
            async for _ in websocket:
                # Keep connection alive
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            print(f"  Client disconnected. Total: {len(self.clients)}")

    async def stream_loop(self, interval_seconds: int = 300):
        """Main streaming loop."""
        print(f"\n{'='*60}")
        print(f"STREAMING: {self.symbol} (interval: {interval_seconds}s)")
        print(f"{'='*60}")

        # Load model
        print("\nLoading model...")
        await self.load_model()

        # WebSocket server
        async with websockets.serve(self.register_client, WS_HOST, WS_PORT, path=WS_PATH):
            print(f"\nWebSocket server started: ws://{WS_HOST}:{WS_PORT}{WS_PATH}")
            print("Clients can connect to receive live signals\n")

            # Main loop
            while True:
                try:
                    await self.broadcast_signal()
                except Exception as e:
                    print(f"  ERROR: {e}")
                await asyncio.sleep(interval_seconds)


async def main():
    """Start streaming for multiple symbols."""
    symbols = ["NEAR", "SOL"]
    interval = 300  # 5 minutes

    print("Neural Network Signal Streamer")
    print("=" * 40)
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Interval: {interval}s ({interval/60}m)")
    print(f"WebSocket: ws://{WS_HOST}:{WS_PORT}{WS_PATH}")
    print("")

    tasks = []
    for symbol in symbols:
        cfg = Config()
        cfg_data = TRADING_CONFIG.get(symbol, {})
        for k, v in cfg_data.get("params", {}).items():
            setattr(cfg, k, v)
        cfg.n_models = 3
        cfg.epochs = 15

        streamer = SignalStreamer(symbol, cfg)
        tasks.append(streamer.stream_loop(interval))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nStopped by user")
