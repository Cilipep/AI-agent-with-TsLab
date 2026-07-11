"""Walk-forward with multi-timeframe features and BTC-specific tuning."""
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import torch
torch.set_num_threads(2)

import json
import random
import numpy as np
import pandas as pd
from torch.utils.data import Subset
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

from config import Config
from features import prepare_features
from dataset import TimeSeriesDataset, auto_select_features, FEATURE_COLS
from model import build_model, Ensemble, build_sklearn_models, HybridEnsemble
from train import train
from backtest_v2 import run_backtest_v2, calculate_sharpe, calculate_sortino, calculate_calmar


def find_best_threshold(model, val_ds, df, config, device, start_idx):
    best_threshold = 0.5
    best_return = -float("inf")
    for threshold in [0.3, 0.35, 0.4, 0.45, 0.5]:
        result = run_backtest_v2(
            model, val_ds, df, config, device,
            threshold=threshold, use_trailing_stop=True,
            trailing_stop_pct=0.01, use_dynamic_sizing=True,
            start_idx=start_idx
        )
        if result["n_trades"] > 0 and result["total_return_pct"] > best_return:
            best_return = result["total_return_pct"]
            best_threshold = threshold
    return best_threshold


def flatten_ds(ds):
    X, y = [], []
    for i in range(len(ds)):
        x, label = ds[i]
        X.append(x.numpy().flatten())
        y.append(label.item())
    return np.array(X), np.array(y)


def walk_forward_mtf(df_daily, config, device, n_folds=5):
    """Walk-forward with multi-timeframe features."""
    # Compute labels on daily data
    from features import make_label
    df_daily["label"] = make_label(df_daily, config.horizon, config.threshold)
    df_daily = df_daily.dropna()

    # Auto-select from ALL columns (excluding non-numeric / label / OHLC)
    exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
    feature_cols = [c for c in df_daily.columns if c not in exclude]
    # Further auto-select top N
    if len(feature_cols) > config.max_features:
        feature_cols = auto_select_features(df_daily, df_daily["label"], max_features=config.max_features)

    print(f"  Features: {len(feature_cols)}")

    ds = TimeSeriesDataset(df_daily, config.window, feature_cols=feature_cols)
    total = len(ds)
    test_size = total // (n_folds + 1)
    min_train_size = total // (n_folds + 1)

    seeds = [42 + i * 17 for i in range(config.n_models)]
    all_results = []
    equity_parts = []

    for fold in range(n_folds):
        train_end = min_train_size + fold * test_size
        test_start = train_end
        test_end = min(test_start + test_size, total)
        if test_end <= test_start:
            break

        print(f"\n  Fold {fold+1}/{n_folds} | train: 0-{train_end} | test: {test_start}-{test_end}")

        full_train_indices = list(range(0, train_end - config.window))
        val_split = int(len(full_train_indices) * 0.85)
        train_indices = full_train_indices[:val_split]
        val_indices = full_train_indices[val_split:]

        train_ds = Subset(ds, train_indices)
        val_ds = Subset(ds, val_indices)
        test_ds = Subset(ds, range(test_start - config.window, test_end - config.window))

        # Train neural models
        base_models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, val_ds, config, device, quiet=True)
            base_models.append(model)

        # Train sklearn
        X_train, y_train = flatten_ds(train_ds)
        sklearn_wrappers = build_sklearn_models(
            X_train, y_train, config.window, len(ds.cols), n_cpu=config.n_cpu_threads,
        )
        all_sklearn = [w for _, w in sklearn_wrappers]

        ensemble = HybridEnsemble(base_models, all_sklearn)

        val_start_idx = val_split + config.window
        best_threshold = find_best_threshold(ensemble, val_ds, df_daily, config, device, val_start_idx)

        result = run_backtest_v2(
            ensemble, test_ds, df_daily, config, device,
            threshold=best_threshold, use_trailing_stop=True,
            trailing_stop_pct=0.01, use_dynamic_sizing=True,
            start_idx=test_start
        )

        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

        wr = {
            "fold": fold + 1,
            "return_pct": result["total_return_pct"],
            "trades": result["n_trades"],
            "win_rate": result["win_rate_pct"],
            "sharpe": result["sharpe_ratio"],
        }
        all_results.append(wr)

        print(f"    Return: {result['total_return_pct']:+.2f}% | "
              f"Trades: {result['n_trades']} | "
              f"Win: {result['win_rate_pct']:.1f}% | "
              f"Sharpe: {result['sharpe_ratio']:.2f}")

    full_equity = np.concatenate(equity_parts) if equity_parts else np.array([1.0])
    total_return = (full_equity[-1] / full_equity[0] - 1) * 100
    max_dd = ((full_equity / np.maximum.accumulate(full_equity)) - 1).min() * 100
    total_trades = sum(r["trades"] for r in all_results)
    avg_win = np.mean([r["win_rate"] for r in all_results]) if all_results else 0
    sharpe = calculate_sharpe(full_equity)
    sortino = calculate_sortino(full_equity)
    calmar = calculate_calmar(full_equity)

    return {
        "total_return": round(total_return, 2),
        "max_drawdown": round(max_dd, 2),
        "total_trades": total_trades,
        "avg_win_rate": round(avg_win, 1),
        "sharpe": round(sharpe, 2),
        "sortino": round(sortino, 2),
        "calmar": round(calmar, 2),
        "folds": all_results,
    }


def main():
    instruments = [
        ("BTC-USD", "Bitcoin", {"hidden_size": 64, "num_layers": 2, "dropout": 0.3, "window": 30, "stop_loss_pct": 0.025, "take_profit_pct": 0.08}),
        ("ETH-USD", "Ethereum", {"hidden_size": 32, "num_layers": 2, "dropout": 0.35, "window": 30, "stop_loss_pct": 0.03, "take_profit_pct": 0.07}),
        ("SOL-USD", "Solana",   {"hidden_size": 32, "num_layers": 1, "dropout": 0.35, "window": 30, "stop_loss_pct": 0.03, "take_profit_pct": 0.07}),
    ]

    all_results = []

    for symbol, name, params in instruments:
        print(f"\n{'='*60}")
        print(f"  {name} (multi-timeframe)")
        print(f"{'='*60}")

        df = pd.read_csv(f"data/binance_{symbol}_multi_tf.csv", index_col=0, parse_dates=True)

        cfg = Config()
        cfg.hidden_size = params["hidden_size"]
        cfg.num_layers = params["num_layers"]
        cfg.dropout = params["dropout"]
        cfg.window = params["window"]
        cfg.batch_size = 64
        cfg.learning_rate = 0.0002
        cfg.n_models = 3
        cfg.max_features = 50
        cfg.stop_loss_pct = params["stop_loss_pct"]
        cfg.take_profit_pct = params["take_profit_pct"]
        cfg.n_cpu_threads = 2

        result = walk_forward_mtf(df, cfg, "cpu", n_folds=5)
        result["instrument"] = name
        all_results.append(result)

    print(f"\n{'='*60}")
    print("FINAL RESULTS (Multi-Timeframe HybridEnsemble)")
    print(f"{'='*60}")

    for r in all_results:
        print(f"\n{r['instrument']}:")
        print(f"  Return:    {r['total_return']:+.2f}%")
        print(f"  Drawdown:  {r['max_drawdown']:.2f}%")
        print(f"  Trades:    {r['total_trades']}")
        print(f"  Win Rate:  {r['avg_win_rate']:.1f}%")
        print(f"  Sharpe:    {r['sharpe']:.2f}")
        print(f"  Sortino:   {r['sortino']:.2f}")
        print(f"  Calmar:    {r['calmar']:.2f}")

    if all_results:
        avg_ret = np.mean([r['total_return'] for r in all_results])
        avg_dd = np.mean([r['max_drawdown'] for r in all_results])
        avg_sharpe = np.mean([r['sharpe'] for r in all_results])
        print(f"\nPortfolio Average:")
        print(f"  Avg Return:   {avg_ret:+.2f}%")
        print(f"  Avg Drawdown: {avg_dd:.2f}%")
        print(f"  Avg Sharpe:   {avg_sharpe:.2f}")

    with open("results/walk_forward_mtf_results.json", "w") as f:
        json.dump({"instruments": all_results}, f, indent=2)

    print(f"\nSaved to results/walk_forward_mtf_results.json")


if __name__ == "__main__":
    main()
