"""Multi-asset portfolio backtest with equal-weight allocation and risk management."""
import os
import random
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Subset
from matplotlib import pyplot as plt

from config import Config
from features import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train


ASSETS = {
    "XRP-USD":  0.125,
    "ADA-USD":  0.125,
    "BTC-USD":  0.125,
    "ETH-USD":  0.125,
    "DOGE-USD": 0.125,
    "BNB-USD":  0.125,
    "AVAX-USD": 0.125,
    "LINK-USD": 0.125,
}


def load_data(symbol, interval="4h", period="730d"):
    cache = f"data/{symbol}_{interval}.csv"
    if os.path.exists(cache):
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    import yfinance as yf
    df = yf.download(symbol, interval=interval, period=period, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.to_csv(cache)
    return df


def train_ensemble(df, config, device):
    ds = TimeSeriesDataset(df, config.window)
    train_size = int(len(ds) * 0.8)
    train_ds = Subset(ds, range(0, train_size))

    seeds = [42 + i * 17 for i in range(config.n_models)]
    models = []
    for seed in seeds:
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        model = build_model(config, len(ds.cols))
        model = train(model, train_ds, train_ds, config, device, quiet=True)
        models.append(model)
    return Ensemble(models), ds


def backtest_asset(ensemble, ds, full_df, test_start, config, device):
    """Backtest single asset with risk management, returns per-bar PnL array."""
    loader = torch.utils.data.DataLoader(ds, batch_size=256, shuffle=False)
    probs = []
    with torch.no_grad():
        for x, _ in loader:
            x = x.to(device)
            prob = torch.sigmoid(ensemble(x)).cpu().numpy().flatten()
            probs.extend(prob)

    probs = np.array(probs)
    # Align prices: dataset starts at (test_start - window), predictions start at window offset
    price_start = test_start
    prices = full_df["Close"].values[price_start : price_start + len(probs)]
    highs = full_df["High"].values[price_start : price_start + len(probs)]
    lows = full_df["Low"].values[price_start : price_start + len(probs)]

    sl = config.stop_loss_pct
    tp = config.take_profit_pct
    risk = config.risk_per_trade

    equity = 1.0
    position = 0
    entry = 0
    pos_size = 0
    stop = 0
    target = 0
    pnl_per_bar = []

    for i in range(len(probs) - 1):
        if position == 0:
            if probs[i] > 0.5:
                position = 1
                entry = prices[i]
                pos_size = (equity * risk) / sl
                stop = entry * (1 - sl)
                target = entry * (1 + tp)
            pnl_per_bar.append(equity)
        else:
            if lows[i] <= stop:
                pnl = (stop - entry) / entry
                equity += pos_size * pnl
                position = 0
            elif highs[i] >= target:
                pnl = (target - entry) / entry
                equity += pos_size * pnl
                position = 0
            elif probs[i] <= 0.5:
                pnl = (prices[i] - entry) / entry
                equity += pos_size * pnl
                position = 0
            pnl_per_bar.append(equity)

    return np.array(pnl_per_bar)


def portfolio_backtest(n_folds=4):
    cfg = Config()
    cfg.n_models = 3
    cfg.epochs = 20
    cfg.patience = 5
    cfg.hidden_size = 48
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=" * 60)
    print("MULTI-ASSET PORTFOLIO BACKTEST")
    print(f"Assets: {len(ASSETS)} | Allocation: equal 12.5%")
    print(f"Risk: SL={cfg.stop_loss_pct:.0%} TP={cfg.take_profit_pct:.0%} Risk/Trade={cfg.risk_per_trade:.0%}")
    print("=" * 60)

    # Load data
    asset_data = {}
    for symbol in ASSETS:
        df = load_data(symbol, cfg.interval, cfg.period)
        df = prepare_features(df, cfg)
        if len(df) < 500:
            print(f"  {symbol}: not enough data ({len(df)}), skipping")
            continue
        asset_data[symbol] = df
        print(f"  {symbol}: {len(df)} bars")

    # Walk-forward folds
    ds_sizes = {}
    for s, d in asset_data.items():
        ds_sizes[s] = len(TimeSeriesDataset(d, cfg.window))
    min_size = min(ds_sizes.values())
    fold_size = min_size // (n_folds + 1)

    portfolio_equity = [1.0]

    for fold in range(n_folds):
        print(f"\n--- Fold {fold+1}/{n_folds} ---")
        fold_equities = []

        for symbol, weight in ASSETS.items():
            if symbol not in asset_data:
                continue

            df = asset_data[symbol]
            ds = TimeSeriesDataset(df, cfg.window)
            train_end = fold_size * (fold + 1)
            test_start = train_end
            test_end = min(test_start + fold_size, len(ds))

            train_ds = Subset(ds, range(0, train_end - cfg.window))
            test_ds = Subset(ds, range(test_start - cfg.window, test_end - cfg.window))

            ensemble, _ = train_ensemble(df.iloc[:train_end], cfg, device)
            eq = backtest_asset(ensemble, test_ds, df, test_start, cfg, device)
            fold_equities.append((eq, weight))

        # Combine weighted equity curves
        if not fold_equities:
            continue
        min_len = min(len(e) for e, _ in fold_equities)
        combined = np.zeros(min_len)
        for eq, weight in fold_equities:
            normed = eq[:min_len] / eq[0]  # normalize to 1.0
            combined += (normed - 1) * weight  # weighted return contribution

        part_equity = 1 + combined
        if len(portfolio_equity) > 0:
            part_equity = part_equity * portfolio_equity[-1]
        portfolio_equity = np.concatenate([portfolio_equity, part_equity[1:]])

        fold_ret = (part_equity[-1] / part_equity[0] - 1) * 100
        print(f"  Fold return: {fold_ret:+.2f}%")

    equity = np.array(portfolio_equity)
    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100

    print(f"\n{'='*60}")
    print("PORTFOLIO RESULTS")
    print(f"{'='*60}")
    print(f"  Total return:   {total_return:+.2f}%")
    print(f"  Max drawdown:   {max_dd:.2f}%")
    print(f"  Assets:         {len(ASSETS)}")
    print(f"  Allocation:     equal weight 12.5%")
    print(f"{'='*60}")

    plt.figure(figsize=(12, 4))
    plt.plot(equity)
    plt.title("Multi-Asset Portfolio (12.5% x 8) with Risk Management")
    plt.xlabel("Step")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/portfolio_equity.png", dpi=100)
    plt.close()
    print("Saved to results/portfolio_equity.png")

    return equity


if __name__ == "__main__":
    portfolio_backtest()
