"""Test enhanced backtest with trailing stop and dynamic sizing."""
import os
import json
import random
import numpy as np
import torch
import pandas as pd
from pathlib import Path

# Limit CPU threads
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
torch.set_num_threads(2)

from config import Config
from features_talib import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest_v2 import run_backtest_v2, run_backtest_original


def main():
    # Load best parameters
    params_path = Path("results/best_params_simple.json")
    with open(params_path) as f:
        best = json.load(f)

    print("=" * 60)
    print("TESTING ENHANCED BACKTEST")
    print("=" * 60)

    # Apply parameters to config
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

    print(f"\nModel: LSTM {cfg.hidden_size} units, dropout {cfg.dropout:.3f}")
    print(f"Window: {cfg.window}, SL: {cfg.stop_loss_pct*100:.2f}%, TP: {cfg.take_profit_pct*100:.2f}%")

    # Create directories
    for d in [cfg.data_dir, cfg.model_dir, cfg.result_dir]:
        d.mkdir(exist_ok=True)

    # Load data
    cache_path = cfg.data_dir / f"{cfg.symbol.replace('/', '_')}_{cfg.interval}.csv"
    print(f"\nLoading data from {cache_path}...")
    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    print(f"  Loaded {len(df)} bars")

    # Prepare features
    print("Computing features...")
    df = prepare_features(df, cfg)
    print(f"  {len(df)} rows after feature engineering")

    # Device
    device = "cpu"
    print(f"Using device: {device}")

    # Create dataset
    ds = TimeSeriesDataset(df, cfg.window)
    n = len(ds)
    train_split = int(n * 0.7)
    test_split = int(n * 0.85)

    train_ds = torch.utils.data.Subset(ds, range(0, train_split))
    test_ds = torch.utils.data.Subset(ds, range(test_split, n))

    print(f"\nDataset splits:")
    print(f"  Train: {len(train_ds)} samples")
    print(f"  Test: {len(test_ds)} samples")

    # Train ensemble
    print(f"\nTraining ensemble ({cfg.n_models} models)...")
    seeds = [42 + i * 31 for i in range(cfg.n_models)]
    models = []

    for i, seed in enumerate(seeds):
        print(f"  Training model {i+1}/{cfg.n_models}...")
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)

        model = build_model(config=cfg, input_size=len(ds.cols))
        model = train(model, train_ds, train_ds, cfg, device, quiet=True)
        models.append(model)

    ensemble = Ensemble(models)
    print("  Ensemble trained!")

    # Test 1: Original backtest
    print("\n" + "=" * 60)
    print("TEST 1: Original Backtest")
    print("=" * 60)

    result_original = run_backtest_original(ensemble, test_ds, df, cfg, device)
    print(f"  Return: {result_original['total_return_pct']:+.2f}%")
    print(f"  Drawdown: {result_original['max_drawdown_pct']:.2f}%")
    print(f"  Trades: {result_original['n_trades']}")
    print(f"  Win Rate: {result_original['win_rate_pct']:.1f}%")
    print(f"  Profit Factor: {result_original['profit_factor']:.2f}")

    # Test 2: Enhanced with trailing stop
    print("\n" + "=" * 60)
    print("TEST 2: With Trailing Stop (2%)")
    print("=" * 60)

    result_trailing = run_backtest_v2(
        ensemble, test_ds, df, cfg, device,
        use_trailing_stop=True, trailing_stop_pct=0.02,
        use_dynamic_sizing=False
    )
    print(f"  Return: {result_trailing['total_return_pct']:+.2f}%")
    print(f"  Drawdown: {result_trailing['max_drawdown_pct']:.2f}%")
    print(f"  Trades: {result_trailing['n_trades']}")
    print(f"  Win Rate: {result_trailing['win_rate_pct']:.1f}%")
    print(f"  Profit Factor: {result_trailing['profit_factor']:.2f}")

    # Test 3: Enhanced with dynamic sizing
    print("\n" + "=" * 60)
    print("TEST 3: With Dynamic Position Sizing")
    print("=" * 60)

    result_dynamic = run_backtest_v2(
        ensemble, test_ds, df, cfg, device,
        use_trailing_stop=False, use_dynamic_sizing=True
    )
    print(f"  Return: {result_dynamic['total_return_pct']:+.2f}%")
    print(f"  Drawdown: {result_dynamic['max_drawdown_pct']:.2f}%")
    print(f"  Trades: {result_dynamic['n_trades']}")
    print(f"  Win Rate: {result_dynamic['win_rate_pct']:.1f}%")
    print(f"  Profit Factor: {result_dynamic['profit_factor']:.2f}")

    # Test 4: Both enhancements
    print("\n" + "=" * 60)
    print("TEST 4: Trailing Stop + Dynamic Sizing")
    print("=" * 60)

    result_both = run_backtest_v2(
        ensemble, test_ds, df, cfg, device,
        use_trailing_stop=True, trailing_stop_pct=0.02,
        use_dynamic_sizing=True
    )
    print(f"  Return: {result_both['total_return_pct']:+.2f}%")
    print(f"  Drawdown: {result_both['max_drawdown_pct']:.2f}%")
    print(f"  Trades: {result_both['n_trades']}")
    print(f"  Win Rate: {result_both['win_rate_pct']:.1f}%")
    print(f"  Profit Factor: {result_both['profit_factor']:.2f}")

    # Summary
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)

    summary = {
        "Original": result_original,
        "Trailing Stop": result_trailing,
        "Dynamic Sizing": result_dynamic,
        "Both": result_both,
    }

    print(f"\n{'Method':<20} {'Return':>10} {'Drawdown':>10} {'Win Rate':>10} {'Trades':>8}")
    print("-" * 60)

    for name, result in summary.items():
        print(f"{name:<20} {result['total_return_pct']:>+9.2f}% {result['max_drawdown_pct']:>9.2f}% {result['win_rate_pct']:>9.1f}% {result['n_trades']:>7}")

    # Find best
    best_method = max(summary.keys(), key=lambda k: summary[k]['total_return_pct'])
    print(f"\nBest method: {best_method}")

    # Save results
    output = {
        "params": params,
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "equity" and kk != "trades"}
                    for k, v in summary.items()},
    }

    with open(cfg.result_dir / "backtest_comparison.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {cfg.result_dir / 'backtest_comparison.json'}")


if __name__ == "__main__":
    main()
