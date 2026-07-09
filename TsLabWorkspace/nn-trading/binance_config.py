"""Binance Futures Testnet configuration."""
import os
from dataclasses import dataclass


@dataclass
class BinanceConfig:
    # API keys — set via environment variables or edit directly
    api_key: str = os.environ.get("BINANCE_TESTNET_API_KEY", "")
    api_secret: str = os.environ.get("BINANCE_TESTNET_API_SECRET", "")

    # Testnet endpoints
    base_url: str = "https://testnet.binancefuture.com"
    ws_url: str = "wss://stream.binancefuture.com"

    # Trading parameters
    symbol: str = "BTCUSDT"
    leverage: int = 10
    margin_type: str = "CROSSED"  # CROSSED or ISOLATED
    position_side: str = "BOTH"   # BOTH for one-way mode

    # Order sizing
    risk_per_trade: float = 0.02   # 2% of balance per trade
    max_position_pct: float = 0.3  # max 30% of balance in position

    # Risk management
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04

    # Signal threshold
    signal_threshold: float = 0.55

    # Intervals
    polling_interval_sec: int = 60  # check signal every N seconds
    kline_interval: str = "1h"      # 1m, 5m, 15m, 1h, 4h, 1d

    # Feature window
    lookback_bars: int = 100  # enough for window=30 + some buffer

    def validate(self) -> bool:
        if not self.api_key or not self.api_secret:
            print("[!] BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET not set")
            print("    Set env vars or edit binance_config.py")
            return False
        return True
