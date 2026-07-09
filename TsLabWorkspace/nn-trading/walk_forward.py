"""Walk-forward validation: anchored (expanding window) with stacking ensemble support."""
import random
from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Subset

from dataset import TimeSeriesDataset
from model import build_model, Ensemble, StackingEnsemble, train_stacking
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


@dataclass
class WindowResult:
    fold: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    equity: np.ndarray
    n_trades: int
    win_rate: float
    return_pct: float
    sharpe: float = 0.0
    sortino: float = 0.0


def train_stacking_ensemble(base_models, train_ds, val_ds, config, device):
    """Train stacking ensemble: freeze base models, train meta-learner."""
    stacking = StackingEnsemble(base_models)
    stacking = train_stacking(stacking, train_ds, val_ds, config, device, epochs=20, lr=0.001)
    return stacking


def walk_forward(df: pd.DataFrame, config, device: str, n_folds: int = 20,
                 use_stacking: bool = False):
    """
    Anchored (expanding window) walk-forward validation.

    For each fold i:
      train on [0..fold_size*(i+1)]
      test on [fold_size*(i+1)..fold_size*(i+2)]

    The training window EXPANDS each fold (anchored), giving more data over time.

    Args:
        n_folds: Number of test windows (default: 20 for statistical significance)
        use_stacking: Use StackingEnsemble instead of weighted average
    """
    ds = TimeSeriesDataset(df, config.window)
    total = len(ds)
    # For anchored WF: train grows, test is fixed size
    test_size = total // (n_folds + 1)
    min_train_size = total // (n_folds + 1)  # first fold train size

    all_results = []
    equity_parts = []
    position_offset = 0

    seeds = [42 + i * 17 for i in range(config.n_models)]

    print(f"\n{'='*60}")
    print(f"ANCHORED WALK-FORWARD: {n_folds} folds")
    print(f"Total data: {total} | Test size per fold: {test_size}")
    print(f"Stacking: {'ON' if use_stacking else 'OFF'}")
    print(f"{'='*60}")

    for fold in range(n_folds):
        train_end = min_train_size + fold * test_size
        test_start = train_end
        test_end = min(test_start + test_size, total)

        if test_end <= test_start:
            break

        print(f"\n{'='*60}")
        print(f"Fold {fold+1}/{n_folds} | "
              f"train: 0-{train_end} ({train_end} bars) | "
              f"test: {test_start}-{test_end} ({test_end - test_start} bars)")

        # Split dataset into train/val/test
        full_train_indices = list(range(0, train_end - config.window))
        val_split = int(len(full_train_indices) * 0.85)
        train_indices = full_train_indices[:val_split]
        val_indices = full_train_indices[val_split:]

        train_ds = Subset(ds, train_indices)
        val_ds = Subset(ds, val_indices)
        test_ds = Subset(ds, range(test_start - config.window, test_end - config.window))

        print(f"  train={len(train_ds)} val={len(val_ds)} test={len(test_ds)}")

        # Train base models
        base_models = []
        for i, seed in enumerate(seeds):
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)

            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, val_ds, config, device, quiet=True)
            base_models.append(model)

        # Use stacking or weighted ensemble
        if use_stacking and len(base_models) >= 2:
            print("  Training stacking ensemble...")
            ensemble = train_stacking_ensemble(base_models, train_ds, val_ds, config, device)
        else:
            ensemble = Ensemble(base_models)

        # Find optimal threshold on validation set
        val_start_idx = val_split + config.window  # first price index in val
        best_threshold = find_best_threshold(ensemble, val_ds, df, config, device, val_start_idx)
        print(f"  Best threshold: {best_threshold}")

        # Predict on test set with optimized threshold
        result = run_backtest_v2(
            ensemble, test_ds, df, config, device,
            threshold=best_threshold,
            use_trailing_stop=True, trailing_stop_pct=0.01,
            use_dynamic_sizing=True,
            start_idx=test_start
        )

        wr = WindowResult(
            fold=fold + 1,
            train_start=0,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
            equity=result["equity"],
            n_trades=result["n_trades"],
            win_rate=result["win_rate_pct"],
            return_pct=result["total_return_pct"],
            sharpe=result["sharpe_ratio"],
            sortino=result["sortino_ratio"],
        )
        all_results.append(wr)

        # Offset equity for concatenation
        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

        print(f"  Return: {result['total_return_pct']:+.2f}% | "
              f"Trades: {result['n_trades']} | "
              f"Win: {result['win_rate_pct']:.1f}% | "
              f"Sharpe: {result['sharpe_ratio']:.2f} | "
              f"Costs: {result['total_cost_pct']:.2f}%")

    # Concatenate all equity curves
    full_equity = np.concatenate(equity_parts) if equity_parts else np.array([1.0])

    # Aggregate stats
    total_return = (full_equity[-1] / full_equity[0] - 1) * 100
    max_dd = ((full_equity / np.maximum.accumulate(full_equity)) - 1).min() * 100
    total_trades = sum(r.n_trades for r in all_results)
    avg_win = np.mean([r.win_rate for r in all_results]) if all_results else 0
    avg_sharpe = np.mean([r.sharpe for r in all_results]) if all_results else 0
    avg_sortino = np.mean([r.sortino for r in all_results if r.sortino < 100]) if all_results else 0

    # Calculate full-equity Sharpe/Sortino
    from backtest_v2 import calculate_sharpe, calculate_sortino, calculate_calmar
    full_sharpe = calculate_sharpe(full_equity)
    full_sortino = calculate_sortino(full_equity)
    full_calmar = calculate_calmar(full_equity)

    print(f"\n{'='*60}")
    print(f"ANCHORED WALK-FORWARD SUMMARY ({n_folds} folds)")
    print(f"{'='*60}")
    print(f"  Total return:    {total_return:+.2f}%")
    print(f"  Max drawdown:    {max_dd:.2f}%")
    print(f"  Total trades:    {total_trades}")
    print(f"  Avg win rate:    {avg_win:.1f}%")
    print(f"  Sharpe ratio:    {full_sharpe:.2f}")
    print(f"  Sortino ratio:   {full_sortino:.2f}")
    print(f"  Calmar ratio:    {full_calmar:.2f}")
    print(f"  Avg fold Sharpe: {avg_sharpe:.2f}")
    print(f"  Avg fold Sortino:{avg_sortino:.2f}")
    print(f"{'='*60}")

    # Per-fold summary table
    print(f"\n{'Fold':>4} {'Train':>8} {'Test':>8} {'Return':>10} {'Trades':>7} {'Win%':>6} {'Sharpe':>8}")
    print("-" * 55)
    for r in all_results:
        print(f"{r.fold:>4} {r.train_end:>8} {r.test_end - r.test_start:>8} "
              f"{r.return_pct:>+9.2f}% {r.n_trades:>7} {r.win_rate:>5.1f}% {r.sharpe:>8.2f}")

    return full_equity, all_results
