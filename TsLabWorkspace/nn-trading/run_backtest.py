"""Run full backtest with best optimized parameters."""
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
from features import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest import run_backtest


def main():
    # Load best parameters
    params_path = Path("results/best_params_safe.json")
    with open(params_path) as f:
        best = json.load(f)

    print("=" * 60)
    print("BACKTEST WITH OPTIMIZED PARAMETERS")
    print("=" * 60)
    print(f"\nLoaded best params from: {params_path}")
    print(f"Optimization score: {best['value']:.4f}")

    # Apply parameters to config
    cfg = Config()
    params = best["params"]

    cfg.model_type = params["model_type"]
    cfg.hidden_size = params["hidden_size"]
    cfg.num_layers = params["num_layers"]
    cfg.dropout = params["dropout"]
    cfg.window = params["window"]
    cfg.batch_size = params["batch_size"]
    cfg.learning_rate = params["learning_rate"]
    cfg.n_models = params["n_models"]
    cfg.stop_loss_pct = params["stop_loss_pct"]
    cfg.take_profit_pct = params["take_profit_pct"]

    print(f"\n{'='*60}")
    print("MODEL CONFIGURATION")
    print("=" * 60)
    print(f"  Model:        {cfg.model_type}")
    print(f"  Hidden size:  {cfg.hidden_size}")
    print(f"  Layers:       {cfg.num_layers}")
    print(f"  Dropout:      {cfg.dropout:.3f}")
    print(f"  Window:       {cfg.window}")
    print(f"  Batch size:   {cfg.batch_size}")
    print(f"  Learning rate:{cfg.learning_rate:.6f}")
    print(f"  Ensemble:     {cfg.n_models} models")
    print(f"  Stop Loss:    {cfg.stop_loss_pct*100:.2f}%")
    print(f"  Take Profit:  {cfg.take_profit_pct*100:.2f}%")
    print(f"  R/R Ratio:    1:{cfg.take_profit_pct/cfg.stop_loss_pct:.1f}")

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
    print(f"\nUsing device: {device}")

    # Create dataset and split
    ds = TimeSeriesDataset(df, cfg.window)
    n = len(ds)
    train_split = int(n * 0.7)
    val_split = int(n * 0.85)

    train_ds = torch.utils.data.Subset(ds, range(0, train_split))
    val_ds = torch.utils.data.Subset(ds, range(train_split, val_split))
    test_ds = torch.utils.data.Subset(ds, range(val_split, n))

    print(f"\nDataset splits:")
    print(f"  Train: {len(train_ds)} samples")
    print(f"  Val:   {len(val_ds)} samples")
    print(f"  Test:  {len(test_ds)} samples")

    # Train ensemble
    print(f"\n{'='*60}")
    print(f"TRAINING ENSEMBLE ({cfg.n_models} models)")
    print("=" * 60)

    seeds = [42 + i * 17 for i in range(cfg.n_models)]
    models = []

    for i, seed in enumerate(seeds):
        print(f"\nTraining model {i+1}/{cfg.n_models} (seed={seed})...")
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)

        model = build_model(config=cfg, input_size=len(ds.cols))
        model = train(model, train_ds, val_ds, cfg, device, quiet=False)
        models.append(model)
        print(f"  Model {i+1} trained successfully")

    ensemble = Ensemble(models)

    # Run backtest
    print(f"\n{'='*60}")
    print("RUNNING BACKTEST ON TEST SET")
    print("=" * 60)

    result = run_backtest(ensemble, test_ds, df, cfg, device)

    # Print results
    print(f"\n{'='*60}")
    print("BACKTEST RESULTS")
    print("=" * 60)

    print(f"\n{'Performance Metrics':=^50}")
    print(f"  Total Return:     {result['total_return_pct']:+.2f}%")
    print(f"  Max Drawdown:     {result['max_drawdown_pct']:.2f}%")
    print(f"  Profit Factor:    {result['profit_factor']:.2f}")
    print(f"  Win Rate:         {result['win_rate_pct']:.1f}%")
    print(f"  Total Trades:     {result['n_trades']}")

    # Trade analysis
    trades_df = result["trades"]
    if len(trades_df) > 0:
        print(f"\n{'Trade Analysis':=^50}")
        print(f"  Winning trades:   {(trades_df['pnl'] > 0).sum()}")
        print(f"  Losing trades:    {(trades_df['pnl'] < 0).sum()}")
        print(f"  Avg win:          {trades_df[trades_df['pnl'] > 0]['pnl'].mean()*100:.2f}%")
        print(f"  Avg loss:         {trades_df[trades_df['pnl'] < 0]['pnl'].mean()*100:.2f}%")

        # Exit reasons
        print(f"\n{'Exit Reasons':=^50}")
        reasons = trades_df["reason"].value_counts()
        for reason, count in reasons.items():
            pct = count / len(trades_df) * 100
            print(f"  {reason:8s}: {count:4d} ({pct:.1f}%)")

    # Save results
    output_path = cfg.result_dir / "backtest_results.json"
    output_data = {
        "params": params,
        "metrics": {
            "total_return_pct": result["total_return_pct"],
            "max_drawdown_pct": result["max_drawdown_pct"],
            "profit_factor": result["profit_factor"],
            "win_rate_pct": result["win_rate_pct"],
            "n_trades": result["n_trades"],
        },
        "trades": trades_df.to_dict("records") if len(trades_df) > 0 else [],
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"Results saved to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
