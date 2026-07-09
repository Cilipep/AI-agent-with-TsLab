"""Full comparison of all models with 160+ TA-Lib features."""
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
from features_full_talib import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest_v2 import run_backtest_v2


def train_and_test(model_type, df, cfg, ds, device="cpu"):
    """Train ensemble and test."""
    cfg.model_type = model_type

    n = len(ds)
    train_split = int(n * 0.7)
    test_split = int(n * 0.85)

    train_ds = torch.utils.data.Subset(ds, range(0, train_split))
    test_ds = torch.utils.data.Subset(ds, range(test_split, n))

    # Train ensemble
    seeds = [42 + i * 31 for i in range(cfg.n_models)]
    models = []
    for seed in seeds:
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        model = build_model(config=cfg, input_size=len(ds.cols))
        model = train(model, train_ds, train_ds, cfg, device, quiet=True)
        models.append(model)

    ensemble = Ensemble(models)

    # Test with enhanced backtest
    result = run_backtest_v2(
        ensemble, test_ds, df, cfg, device,
        use_trailing_stop=True, trailing_stop_pct=0.01,
        use_dynamic_sizing=True
    )

    return result


def main():
    # Load best parameters
    params_path = Path("results/best_params_simple.json")
    with open(params_path) as f:
        best = json.load(f)

    cfg = Config()
    params = best["params"]
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

    print("Computing FULL TA-Lib features (160+)...")
    df = prepare_features(df, cfg)
    print(f"  {len(df.columns)} features created")

    ds = TimeSeriesDataset(df, cfg.window)

    print("\n" + "=" * 70)
    print("FULL MODEL COMPARISON (160+ Features)")
    print("=" * 70)

    # Models to test
    model_types = [
        "lstm",
        "tcn",
        "transformer",
        "lstm_reg",
        "tcn_reg",
        "transformer_reg",
        "multi_task",
    ]

    results = {}

    for model_type in model_types:
        print(f"\nTraining {model_type.upper()}...")
        try:
            result = train_and_test(model_type, df, cfg, ds)
            results[model_type] = result
            print(f"  Return: {result['total_return_pct']:+.2f}%")
            print(f"  Drawdown: {result['max_drawdown_pct']:.2f}%")
            print(f"  Win Rate: {result['win_rate_pct']:.1f}%")
            print(f"  Profit Factor: {result['profit_factor']:.2f}")
        except Exception as e:
            print(f"  Error: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    print(f"\n{'Model':<20} {'Return':>10} {'Drawdown':>10} {'Win Rate':>10} {'PF':>8}")
    print("-" * 60)

    for model_type, result in results.items():
        print(f"{model_type.upper():<20} {result['total_return_pct']:>+9.2f}% "
              f"{result['max_drawdown_pct']:>9.2f}% "
              f"{result['win_rate_pct']:>9.1f}% "
              f"{result['profit_factor']:>7.2f}")

    best_model = max(results.keys(), key=lambda k: results[k]['total_return_pct'])
    print(f"\nBest model: {best_model.upper()}")

    # Feature count
    print(f"\nFeatures used: {len(df.columns)}")

    # Save results
    output = {
        "params": params,
        "features_count": len(df.columns),
        "enhancements": {
            "trailing_stop": 0.01,
            "dynamic_sizing": True,
            "full_talib": True,
        },
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "equity" and kk != "trades"}
                    for k, v in results.items()},
    }

    with open(cfg.result_dir / "full_comparison.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {cfg.result_dir / 'full_comparison.json'}")


if __name__ == "__main__":
    main()
