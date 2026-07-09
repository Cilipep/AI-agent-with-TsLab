"""Walk-forward with enhanced backtest (trailing stop + dynamic sizing)."""
import os
import json
import random
import numpy as np
import torch
import pandas as pd
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
torch.set_num_threads(2)

from config import Config
from features_talib import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest_v2 import run_backtest_v2


def find_best_threshold(model, val_ds, df, config, device, start_idx):
    """Find optimal threshold on validation set."""
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


def walk_forward_enhanced(df, config, n_folds=6):
    """Walk-forward with enhanced backtest."""
    ds = TimeSeriesDataset(df, config.window)
    total = len(ds)
    fold_size = total // (n_folds + 1)

    all_results = []
    equity_parts = []
    seeds = [42 + i * 31 for i in range(config.n_models)]

    for fold in range(n_folds):
        train_end = fold_size * (fold + 1)
        test_start = train_end
        test_end = min(test_start + fold_size, total)

        if test_end <= test_start:
            break

        print(f"\nFold {fold+1}/{n_folds} | train: 0-{train_end} | test: {test_start}-{test_end}")

        # Split dataset into train/val/test
        full_train_indices = list(range(0, train_end - config.window))
        val_split = int(len(full_train_indices) * 0.85)
        train_indices = full_train_indices[:val_split]
        val_indices = full_train_indices[val_split:]

        train_ds = torch.utils.data.Subset(ds, train_indices)
        val_ds = torch.utils.data.Subset(ds, val_indices)
        test_ds = torch.utils.data.Subset(ds, range(test_start - config.window, test_end - config.window))

        # Train ensemble
        models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, val_ds, config, "cpu", quiet=True)
            models.append(model)

        ensemble = Ensemble(models)

        # Find optimal threshold on validation set
        val_start_idx = val_split + config.window  # first price index in val
        best_threshold = find_best_threshold(ensemble, val_ds, df, config, "cpu", val_start_idx)
        print(f"  Best threshold: {best_threshold}")

        # Run enhanced backtest with optimized threshold
        result = run_backtest_v2(
            ensemble, test_ds, df, config, "cpu",
            threshold=best_threshold,
            use_trailing_stop=True, trailing_stop_pct=0.01,
            use_dynamic_sizing=True,
            start_idx=test_start
        )

        all_results.append({
            "fold": fold + 1,
            "return": result["total_return_pct"],
            "drawdown": result["max_drawdown_pct"],
            "trades": result["n_trades"],
            "win_rate": result["win_rate_pct"],
            "profit_factor": result["profit_factor"],
        })

        # Offset equity
        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

        print(f"  Return: {result['total_return_pct']:+.2f}% | "
              f"DD: {result['max_drawdown_pct']:.2f}% | "
              f"Win: {result['win_rate_pct']:.1f}% | "
              f"PF: {result['profit_factor']:.2f}")

    # Concatenate equity
    full_equity = np.concatenate(equity_parts) if equity_parts else np.array([1.0])

    # Aggregate stats
    total_return = (full_equity[-1] / full_equity[0] - 1) * 100
    max_dd = ((full_equity / np.maximum.accumulate(full_equity)) - 1).min() * 100
    avg_win = np.mean([r["win_rate"] for r in all_results]) if all_results else 0

    print(f"\n{'='*60}")
    print(f"WALK-FORWARD SUMMARY ({n_folds} folds)")
    print(f"  Total return:   {total_return:+.2f}%")
    print(f"  Max drawdown:   {max_dd:.2f}%")
    print(f"  Avg win rate:   {avg_win:.1f}%")
    print(f"{'='*60}")

    return full_equity, all_results


def main():
    # Load best parameters
    params_path = Path("results/best_params_simple.json")
    with open(params_path) as f:
        best = json.load(f)

    cfg = Config()
    params = best["params"]
    cfg.model_type = "lstm"
    cfg.hidden_size = params["hidden_size"]
    cfg.num_layers = 1
    cfg.dropout = params["dropout"]
    cfg.window = params["window"]
    cfg.batch_size = params["batch_size"]
    cfg.learning_rate = params["learning_rate"]
    cfg.n_models = 3
    cfg.stop_loss_pct = params["stop_loss_pct"]
    cfg.take_profit_pct = params["take_profit_pct"]

    for d in [cfg.data_dir, cfg.model_dir, cfg.result_dir]:
        d.mkdir(exist_ok=True)

    cache_path = cfg.data_dir / f"{cfg.symbol.replace('/', '_')}_{cfg.interval}.csv"
    print("Loading data...")
    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    print(f"  Loaded {len(df)} bars")

    print("Computing features...")
    df = prepare_features(df, cfg)
    print(f"  {len(df)} rows after feature engineering")

    print("\n" + "=" * 60)
    print("WALK-FORWARD WITH ENHANCED BACKTEST")
    print("Trailing Stop: 1% | Dynamic Sizing: ON")
    print("=" * 60)

    equity, results = walk_forward_enhanced(df, cfg, n_folds=6)

    # Save results
    output = {
        "params": params,
        "enhancements": {
            "trailing_stop": 0.01,
            "dynamic_sizing": True,
        },
        "total_return_pct": (equity[-1] / equity[0] - 1) * 100,
        "max_drawdown_pct": ((equity / np.maximum.accumulate(equity)) - 1).min() * 100,
        "folds": results,
    }

    with open(cfg.result_dir / "walk_forward_enhanced.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {cfg.result_dir / 'walk_forward_enhanced.json'}")


if __name__ == "__main__":
    main()
