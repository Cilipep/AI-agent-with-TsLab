"""Test all improvements: anchored walk-forward, transaction costs, stacking, metrics."""
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
from model import build_model, Ensemble, StackingEnsemble, train_stacking
from train import train
from backtest_v2 import run_backtest_v2, calculate_sharpe, calculate_sortino, calculate_calmar


def download_data(symbol="BTC-USD", period="1820d", interval="1d"):
    """Download data from yfinance."""
    cache_path = Path("data") / f"{symbol.replace('/', '_')}_{interval}.csv"

    if cache_path.exists():
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    import yfinance as yf
    print(f"  Downloading {symbol}...")
    df = yf.download(symbol, period=period, interval=interval)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.to_csv(cache_path)
    return df


def run_anchored_walkforward(df, config, n_folds=20, use_stacking=False):
    """Run anchored walk-forward with all improvements."""
    ds = TimeSeriesDataset(df, config.window)
    total = len(ds)
    test_size = total // (n_folds + 1)
    min_train_size = total // (n_folds + 1)

    all_results = []
    equity_parts = []
    seeds = [42 + i * 31 for i in range(config.n_models)]

    print(f"\n{'='*70}")
    print(f"ANCHORED WALK-FORWARD: {n_folds} folds")
    print(f"Stacking: {'ON' if use_stacking else 'OFF'}")
    print(f"{'='*70}")

    for fold in range(n_folds):
        train_end = min_train_size + fold * test_size
        test_start = train_end
        test_end = min(test_start + test_size, total)

        if test_end <= test_start:
            break

        print(f"\nFold {fold+1}/{n_folds} | train: 0-{train_end} | test: {test_start}-{test_end}")

        # Split dataset
        full_train_indices = list(range(0, train_end - config.window))
        val_split = int(len(full_train_indices) * 0.85)
        train_indices = full_train_indices[:val_split]
        val_indices = full_train_indices[val_split:]

        train_ds = torch.utils.data.Subset(ds, train_indices)
        val_ds = torch.utils.data.Subset(ds, val_indices)
        test_ds = torch.utils.data.Subset(ds, range(test_start - config.window, test_end - config.window))

        # Train base models
        base_models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, val_ds, config, "cpu", quiet=True)
            base_models.append(model)

        # Use stacking or weighted ensemble
        if use_stacking and len(base_models) >= 2:
            stacking = StackingEnsemble(base_models)
            stacking = train_stacking(stacking, train_ds, val_ds, config, "cpu", epochs=20, lr=0.001)
            ensemble = stacking
        else:
            ensemble = Ensemble(base_models)

        # Run backtest with transaction costs
        result = run_backtest_v2(
            ensemble, test_ds, df, config, "cpu",
            threshold=0.5,
            use_trailing_stop=True,
            trailing_stop_pct=0.01,
            use_dynamic_sizing=True,
            start_idx=test_start,
            commission_pct=config.commission_pct,
            slippage_pct=config.slippage_pct,
            spread_pct=config.spread_pct,
        )

        all_results.append({
            "fold": fold + 1,
            "return": result["total_return_pct"],
            "drawdown": result["max_drawdown_pct"],
            "trades": result["n_trades"],
            "win_rate": result["win_rate_pct"],
            "sharpe": result["sharpe_ratio"],
            "sortino": result["sortino_ratio"],
            "pf": result["profit_factor"],
            "costs": result["total_cost_pct"],
        })

        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

        print(f"  Return: {result['total_return_pct']:+.2f}% | "
              f"Sharpe: {result['sharpe_ratio']:.2f} | "
              f"Costs: {result['total_cost_pct']:.2f}%")

    # Aggregate
    full_equity = np.concatenate(equity_parts) if equity_parts else np.array([1.0])
    total_return = (full_equity[-1] / full_equity[0] - 1) * 100
    max_dd = ((full_equity / np.maximum.accumulate(full_equity)) - 1).min() * 100
    full_sharpe = calculate_sharpe(full_equity)
    full_sortino = calculate_sortino(full_equity)
    full_calmar = calculate_calmar(full_equity)
    total_trades = sum(r["trades"] for r in all_results)
    avg_costs = np.mean([r["costs"] for r in all_results])

    return {
        "total_return": total_return,
        "max_drawdown": max_dd,
        "sharpe": full_sharpe,
        "sortino": full_sortino,
        "calmar": full_calmar,
        "total_trades": total_trades,
        "avg_costs": avg_costs,
        "folds": all_results,
    }


def main():
    cfg = Config()
    for d in [cfg.data_dir, cfg.model_dir, cfg.result_dir]:
        d.mkdir(exist_ok=True)

    print("=" * 70)
    print("TEST ALL IMPROVEMENTS")
    print("=" * 70)

    # Download data
    df = download_data("BTC-USD", period="1820d", interval="1d")
    print(f"Data: {len(df)} bars")

    # Prepare features
    print("Computing features...")
    df = prepare_features(df, cfg)
    print(f"Features: {len(df.columns)}")

    # Test 1: Old way (5 folds, no costs)
    print("\n" + "=" * 70)
    print("TEST 1: OLD WAY (5 folds, no costs)")
    print("=" * 70)

    old_result = run_anchored_walkforward(df, cfg, n_folds=5, use_stacking=False)

    # Test 2: New way (20 folds, with costs)
    print("\n" + "=" * 70)
    print("TEST 2: NEW WAY (20 folds, with costs)")
    print("=" * 70)

    new_result = run_anchored_walkforward(df, cfg, n_folds=20, use_stacking=False)

    # Test 3: With stacking
    print("\n" + "=" * 70)
    print("TEST 3: STACKING ENSEMBLE (20 folds, with costs)")
    print("=" * 70)

    stacking_result = run_anchored_walkforward(df, cfg, n_folds=20, use_stacking=True)

    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON: OLD vs NEW vs STACKING")
    print("=" * 70)

    print(f"\n{'Metric':<20} {'Old (5f)':>12} {'New (20f)':>12} {'Stacking':>12}")
    print("-" * 60)
    print(f"{'Return':<20} {old_result['total_return']:>+11.2f}% {new_result['total_return']:>+11.2f}% {stacking_result['total_return']:>+11.2f}%")
    print(f"{'Drawdown':<20} {old_result['max_drawdown']:>11.2f}% {new_result['max_drawdown']:>11.2f}% {stacking_result['max_drawdown']:>11.2f}%")
    print(f"{'Sharpe':<20} {old_result['sharpe']:>12.2f} {new_result['sharpe']:>12.2f} {stacking_result['sharpe']:>12.2f}")
    print(f"{'Sortino':<20} {old_result['sortino']:>12.2f} {new_result['sortino']:>12.2f} {stacking_result['sortino']:>12.2f}")
    print(f"{'Calmar':<20} {old_result['calmar']:>12.2f} {new_result['calmar']:>12.2f} {stacking_result['calmar']:>12.2f}")
    print(f"{'Trades':<20} {old_result['total_trades']:>12} {new_result['total_trades']:>12} {stacking_result['total_trades']:>12}")
    print(f"{'Avg Costs':<20} {'N/A':>12} {new_result['avg_costs']:>11.2f}% {stacking_result['avg_costs']:>11.2f}%")

    # Transaction cost impact
    print(f"\n{'='*70}")
    print("TRANSACTION COST IMPACT")
    print(f"{'='*70}")
    print(f"  Commission:  {cfg.commission_pct*100:.2f}% per trade")
    print(f"  Slippage:    {cfg.slippage_pct*100:.2f}% per trade")
    print(f"  Spread:      {cfg.spread_pct*100:.2f}% per trade")
    print(f"  Total round-trip: {(cfg.commission_pct*2 + cfg.slippage_pct*2 + cfg.spread_pct)*100:.2f}%")

    # Save results
    output = {
        "old_5folds": old_result,
        "new_20folds": new_result,
        "stacking_20folds": stacking_result,
        "config": {
            "commission_pct": cfg.commission_pct,
            "slippage_pct": cfg.slippage_pct,
            "spread_pct": cfg.spread_pct,
        }
    }

    output_path = cfg.result_dir / "improvements_comparison.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
