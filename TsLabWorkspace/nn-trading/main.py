"""Entry point: download data -> features -> walk-forward ensemble -> backtest."""
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yfinance as yf
from matplotlib import pyplot as plt

from config import Config
from features import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest import run_backtest
from walk_forward import walk_forward


def download(symbol: str, interval: str, period: str) -> pd.DataFrame:
    """Download OHLCV data via yfinance."""
    print(f"Downloading {symbol} {interval} ({period})...")
    df = yf.download(symbol, interval=interval, period=period, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    if df.empty:
        raise ValueError(f"No data downloaded for {symbol}")
    print(f"  {len(df)} bars loaded")
    return df


def plot_results(equity, result_dir: Path, title="Equity Curve"):
    plt.figure(figsize=(12, 4))
    plt.plot(equity)
    plt.title(title)
    plt.xlabel("Step")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(result_dir / "equity_curve.png", dpi=100)
    plt.close()
    print(f"  Saved equity curve to {result_dir / 'equity_curve.png'}")


def main():
    cfg = Config()
    for d in [cfg.data_dir, cfg.model_dir, cfg.result_dir]:
        d.mkdir(exist_ok=True)

    # 1. Data
    cache_path = cfg.data_dir / f"{cfg.symbol.replace('/', '_')}_{cfg.interval}.csv"
    if cache_path.exists():
        print(f"Loading cached data from {cache_path}")
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    else:
        df = download(cfg.symbol, cfg.interval, cfg.period)
        df.to_csv(cache_path)
        print(f"  Cached to {cache_path}")

    # 2. Features
    print("Computing features...")
    df = prepare_features(df, cfg)
    print(f"  {len(df)} rows after feature engineering")

    # 3. Walk-forward
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nRunning walk-forward validation ({cfg.n_models}-model ensemble, 4 folds)...")
    equity, results = walk_forward(df, cfg, device, n_folds=4)

    # 4. Plot
    plot_results(equity, cfg.result_dir, "Walk-Forward Equity Curve")


if __name__ == "__main__":
    main()
