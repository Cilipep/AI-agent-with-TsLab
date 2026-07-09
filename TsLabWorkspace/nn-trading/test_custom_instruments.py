"""Test any custom list of instruments."""
import os
import sys
import json
import random
import numpy as np
import torch
import pandas as pd
from pathlib import Path
import yfinance as yf

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
torch.set_num_threads(2)

from config import Config
from features_full_talib import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest_v2 import run_backtest_v2


def download_data(symbol, period="1820d", interval="1d"):
    """Download data from yfinance."""
    cache_path = Path("data") / f"{symbol.replace('/', '_')}_{interval}.csv"

    if cache_path.exists():
        print(f"  Loading cached data from {cache_path}")
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    print(f"  Downloading {symbol}...")
    try:
        df = yf.download(symbol, period=period, interval=interval)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            raise ValueError(f"No data for {symbol}")
        df.to_csv(cache_path)
        print(f"  Saved {len(df)} bars")
        return df
    except Exception as e:
        print(f"  Download failed: {e}")
        return None


def walk_forward_optimized(df, config, model_type="transformer", n_folds=5):
    """Walk-forward with optimization."""
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

        print(f"  Fold {fold+1}/{n_folds}...")

        train_ds = torch.utils.data.Subset(ds, range(0, train_end - config.window))
        test_ds = torch.utils.data.Subset(ds, range(test_start - config.window, test_end - config.window))

        models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, train_ds, config, "cpu", quiet=True)
            models.append(model)

        ensemble = Ensemble(models)

        result = run_backtest_v2(
            ensemble, test_ds, df, config, "cpu",
            use_trailing_stop=True, trailing_stop_pct=0.01,
            use_dynamic_sizing=True
        )

        all_results.append({
            "fold": fold + 1,
            "return": result["total_return_pct"],
            "drawdown": result["max_drawdown_pct"],
            "trades": result["n_trades"],
            "win_rate": result["win_rate_pct"],
            "profit_factor": result["profit_factor"],
        })

        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

    full_equity = np.concatenate(equity_parts) if equity_parts else np.array([1.0])

    total_return = (full_equity[-1] / full_equity[0] - 1) * 100
    max_dd = ((full_equity / np.maximum.accumulate(full_equity)) - 1).min() * 100
    avg_win = np.mean([r["win_rate"] for r in all_results]) if all_results else 0
    avg_pf = np.mean([r["profit_factor"] for r in all_results if r["profit_factor"] < 100]) if all_results else 0

    return {
        "total_return": total_return,
        "max_drawdown": max_dd,
        "avg_win_rate": avg_win,
        "avg_profit_factor": avg_pf,
        "folds": all_results,
    }


def test_instruments(instruments):
    """Test a list of (symbol, name) tuples."""
    # Load best parameters
    params_path = Path("results/best_params_simple.json")
    with open(params_path) as f:
        best = json.load(f)

    cfg = Config()
    params = best["params"]
    cfg.model_type = "transformer"
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

    print("=" * 70)
    print(f"CUSTOM INSTRUMENT TEST: {len(instruments)} instruments")
    print("Model: Transformer | Trailing Stop: 1% | Dynamic Sizing: ON")
    print("=" * 70)

    all_results = {}

    for symbol, name in instruments:
        print(f"\n{'='*70}")
        print(f"TESTING: {name} ({symbol})")
        print("=" * 70)

        try:
            df = download_data(symbol, period="1820d", interval="1d")
            if df is None or len(df) < 100:
                print(f"  Skipping {name}: insufficient data")
                continue

            print(f"  Data: {len(df)} bars")

            print("  Computing features...")
            df = prepare_features(df, cfg)
            print(f"  Features: {len(df.columns)}")

            print("  Running walk-forward...")
            result = walk_forward_optimized(df, cfg, model_type="transformer", n_folds=5)

            all_results[name] = result

            print(f"\n  Results for {name}:")
            print(f"    Total Return: {result['total_return']:+.2f}%")
            print(f"    Max Drawdown: {result['max_drawdown']:.2f}%")
            print(f"    Avg Win Rate: {result['avg_win_rate']:.1f}%")
            print(f"    Avg PF: {result['avg_profit_factor']:.2f}")

        except Exception as e:
            print(f"  Error: {e}")
            all_results[name] = {"error": str(e)}

    # Summary
    print("\n" + "=" * 70)
    print("CUSTOM INSTRUMENTS SUMMARY")
    print("=" * 70)

    print(f"\n{'Instrument':<20} {'Return':>10} {'Drawdown':>10} {'Win Rate':>10} {'PF':>8}")
    print("-" * 68)

    for name, result in all_results.items():
        if "error" not in result:
            print(f"{name:<20} {result['total_return']:>+9.2f}% "
                  f"{result['max_drawdown']:>9.2f}% "
                  f"{result['avg_win_rate']:>9.1f}% "
                  f"{result['avg_profit_factor']:>7.2f}")
        else:
            print(f"{name:<20} ERROR: {result['error'][:30]}")

    # Save
    output = {
        "instruments": {n: {"symbol": s, "name": n} for s, n in instruments},
        "results": all_results,
    }

    output_path = cfg.result_dir / "custom_instruments_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")
    return all_results


if __name__ == "__main__":
    # Example: python test_custom_instruments.py SOL-USD SOLana XRP-USD Ripple
    if len(sys.argv) < 3 or (len(sys.argv) - 1) % 2 != 0:
        print("Usage: python test_custom_instruments.py SYMBOL1 NAME1 SYMBOL2 NAME2 ...")
        print("Example: python test_custom_instruments.py SOL-USD Solana XRP-USD Ripple")
        sys.exit(1)

    instruments = []
    for i in range(1, len(sys.argv), 2):
        instruments.append((sys.argv[i], sys.argv[i + 1]))

    test_instruments(instruments)
