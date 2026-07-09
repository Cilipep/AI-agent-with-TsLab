"""Run walk-forward validation with best optimized parameters."""
import os
import json
import numpy as np
import pandas as pd
import torch
from pathlib import Path

# Limit CPU threads
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
torch.set_num_threads(2)

from config import Config
from features import prepare_features
from walk_forward import walk_forward


def main():
    # Load best parameters
    params_path = Path("results/best_params_safe.json")
    with open(params_path) as f:
        best = json.load(f)

    print("=" * 60)
    print("WALK-FORWARD VALIDATION")
    print("=" * 60)
    print(f"\nUsing optimized params from: {params_path}")

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
    print(f"  Ensemble:     {cfg.n_models} models")
    print(f"  Stop Loss:    {cfg.stop_loss_pct*100:.2f}%")
    print(f"  Take Profit:  {cfg.take_profit_pct*100:.2f}%")

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

    # Run walk-forward
    print(f"\n{'='*60}")
    print("STARTING WALK-FORWARD VALIDATION")
    print("=" * 60)

    equity, results = walk_forward(df, cfg, device, n_folds=8)

    # Save results
    output_path = cfg.result_dir / "walk_forward_results.json"
    output_data = {
        "params": params,
        "n_folds": len(results),
        "total_return_pct": (equity[-1] / equity[0] - 1) * 100,
        "max_drawdown_pct": ((equity / np.maximum.accumulate(equity)) - 1).min() * 100,
        "folds": [
            {
                "fold": r.fold,
                "train_range": f"{r.train_start}-{r.train_end}",
                "test_range": f"{r.test_start}-{r.test_end}",
                "return_pct": r.return_pct,
                "trades": r.n_trades,
                "win_rate": r.win_rate,
            }
            for r in results
        ],
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
