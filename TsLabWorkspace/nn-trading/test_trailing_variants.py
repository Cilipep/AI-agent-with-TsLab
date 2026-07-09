"""Test different trailing stop percentages."""
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


def main():
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
    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    df = prepare_features(df, cfg)

    ds = TimeSeriesDataset(df, cfg.window)
    n = len(ds)
    test_split = int(n * 0.85)
    test_ds = torch.utils.data.Subset(ds, range(test_split, n))

    # Train ensemble
    seeds = [42 + i * 31 for i in range(cfg.n_models)]
    models = []
    for seed in seeds:
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        model = build_model(config=cfg, input_size=len(ds.cols))
        model = train(model, torch.utils.data.Subset(ds, range(0, int(n * 0.7))),
                     torch.utils.data.Subset(ds, range(0, int(n * 0.7))), cfg, "cpu", quiet=True)
        models.append(model)
    ensemble = Ensemble(models)

    print("=" * 70)
    print("TRAILING STOP OPTIMIZATION")
    print("=" * 70)

    # Test different trailing stop percentages
    trailing_pcts = [0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05]
    results = []

    for pct in trailing_pcts:
        result = run_backtest_v2(
            ensemble, test_ds, df, cfg, "cpu",
            use_trailing_stop=True, trailing_stop_pct=pct,
            use_dynamic_sizing=True
        )
        results.append({
            "trailing_pct": pct,
            "return": result["total_return_pct"],
            "drawdown": result["max_drawdown_pct"],
            "win_rate": result["win_rate_pct"],
            "trades": result["n_trades"],
            "profit_factor": result["profit_factor"],
        })
        print(f"Trailing {pct*100:.1f}%: Return {result['total_return_pct']:+.2f}%, "
              f"DD {result['max_drawdown_pct']:.2f}%, Win {result['win_rate_pct']:.1f}%")

    # Find best
    best_result = max(results, key=lambda x: x["return"])
    print(f"\nBest trailing stop: {best_result['trailing_pct']*100:.1f}%")
    print(f"  Return: {best_result['return']:+.2f}%")
    print(f"  Drawdown: {best_result['drawdown']:.2f}%")
    print(f"  Win Rate: {best_result['win_rate']:.1f}%")

    # Compare with no trailing stop
    result_no_trailing = run_backtest_v2(
        ensemble, test_ds, df, cfg, "cpu",
        use_trailing_stop=False, use_dynamic_sizing=True
    )

    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"{'Method':<25} {'Return':>10} {'Drawdown':>10} {'Win Rate':>10}")
    print("-" * 60)
    print(f"{'No Trailing Stop':<25} {result_no_trailing['total_return_pct']:>+9.2f}% "
          f"{result_no_trailing['max_drawdown_pct']:>9.2f}% "
          f"{result_no_trailing['win_rate_pct']:>9.1f}%")
    print(f"{'Best Trailing (' + str(best_result['trailing_pct']*100) + '%)':<25} "
          f"{best_result['return']:>+9.2f}% {best_result['drawdown']:>9.2f}% {best_result['win_rate']:>9.1f}%")


if __name__ == "__main__":
    main()
