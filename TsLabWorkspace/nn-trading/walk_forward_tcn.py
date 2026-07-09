"""Walk-forward with diverse ensemble (TCN+LSTM+Transformer) and optimal weight search."""
import os
import json
import random
import numpy as np
import torch
import pandas as pd
from itertools import product
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
torch.set_num_threads(2)

from config import Config
from features import prepare_features
from dataset import TimeSeriesDataset, FEATURE_COLS
from model import build_model, Ensemble
from train import train
from backtest_v2 import run_backtest_v2

# Single attention model
MODEL_TYPES = ["attention"]


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


def find_best_weights(models, val_ds, df, config, device, start_idx):
    """Find optimal weights by grid search on validation set."""
    best_weights = [1.0 / len(models)] * len(models)
    best_return = -float("inf")

    # Grid search over weight combinations
    # Steps: 0.1, 0.2, 0.3, 0.4, 0.5
    steps = [0.1, 0.2, 0.3, 0.4, 0.5]
    n = len(models)

    for combo in product(steps, repeat=n):
        if abs(sum(combo) - 1.0) > 0.01:
            continue  # weights must sum to 1

        weights = list(combo)
        ensemble = Ensemble(models, weights)

        result = run_backtest_v2(
            ensemble, val_ds, df, config, device,
            threshold=0.5, use_trailing_stop=True,
            trailing_stop_pct=0.01, use_dynamic_sizing=True,
            start_idx=start_idx
        )

        if result["n_trades"] > 0 and result["total_return_pct"] > best_return:
            best_return = result["total_return_pct"]
            best_weights = weights

    return best_weights, best_return


def walk_forward_tcn(df, config, n_folds=6):
    """Walk-forward with diverse ensemble and optimal weight search."""
    # Use ALL features from df (excluding OHLCV and label)
    exclude_cols = {"Open", "High", "Low", "Close", "Volume", "label", "timestamp"}
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    n_features = len(feature_cols)
    print(f"  Features: {n_features}")

    # Create a raw dataset without scaling to get total size
    ds_raw = TimeSeriesDataset(df, config.window, feature_cols)
    total = len(ds_raw)
    fold_size = total // (n_folds + 1)

    all_results = []
    equity_parts = []
    n_models = len(MODEL_TYPES)
    seeds = [42 + i * 31 for i in range(n_models)]

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

        # Fit scaler ONLY on training data (no look-ahead bias)
        from sklearn.preprocessing import StandardScaler
        train_df = df.iloc[train_indices]
        scaler = StandardScaler()
        scaler.fit(train_df[feature_cols].values)

        # Feature selection on training data
        if config.use_feature_selection and n_features > config.max_features:
            print(f"  Selecting {config.max_features} features from {n_features}...")
            from feature_selection import select_features_combined
            y_train = df["label"].iloc[train_indices]
            selected_features = select_features_combined(
                train_df[feature_cols], y_train, config.max_features
            )
            feature_cols = selected_features
            n_features = len(feature_cols)
            print(f"  Selected {n_features} features")
            # Refit scaler on selected features only
            scaler.fit(train_df[feature_cols].values)

        # Create datasets with fitted scaler
        train_ds = torch.utils.data.Subset(
            TimeSeriesDataset(df, config.window, feature_cols, scaler),
            train_indices
        )
        val_ds = torch.utils.data.Subset(
            TimeSeriesDataset(df, config.window, feature_cols, scaler),
            val_indices
        )
        test_ds = torch.utils.data.Subset(
            TimeSeriesDataset(df, config.window, feature_cols, scaler),
            range(test_start - config.window, test_end - config.window)
        )

        # Train model
        torch.manual_seed(42)
        random.seed(42)
        np.random.seed(42)

        model_type = MODEL_TYPES[0]
        cfg_copy = type(config)()
        for k, v in config.__dict__.items():
            setattr(cfg_copy, k, v)
        cfg_copy.model_type = model_type

        model = build_model(cfg_copy, n_features)
        model = train(model, train_ds, val_ds, config, "cpu", quiet=True)
        print(f"    Model ({model_type}): trained")

        # Find optimal threshold
        val_start_idx = val_split + config.window
        best_threshold = find_best_threshold(model, val_ds, df, config, "cpu", val_start_idx)
        print(f"  Best threshold: {best_threshold}")

        # Run backtest on test set
        result = run_backtest_v2(
            model, test_ds, df, config, "cpu",
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
            "threshold": best_threshold,
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
    cfg = Config()

    # Attention model with aggressive feature selection
    cfg.model_type = "attention"
    cfg.hidden_size = 64
    cfg.num_layers = 2
    cfg.dropout = 0.35
    cfg.window = 30
    cfg.batch_size = 32
    cfg.learning_rate = 0.0003
    cfg.n_models = 1
    cfg.stop_loss_pct = 0.03
    cfg.take_profit_pct = 0.06
    cfg.epochs = 40
    cfg.patience = 10

    # Use all 104 features
    cfg.use_feature_selection = False
    cfg.max_features = 104

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
    print("WALK-FORWARD WITH FEATURE SELECTION")
    print(f"Base models: {', '.join(MODEL_TYPES)}")
    print(f"Feature selection: {cfg.max_features} from 55")
    print("Trailing Stop: 1% | Dynamic Sizing: ON")
    print("=" * 60)

    equity, results = walk_forward_tcn(df, cfg, n_folds=6)

    # Save results
    output = {
        "model": "diverse_ensemble_feature_selection",
        "model_types": MODEL_TYPES,
        "enhancements": {
            "trailing_stop": 0.01,
            "dynamic_sizing": True,
            "feature_selection": cfg.max_features,
        },
        "total_return_pct": (equity[-1] / equity[0] - 1) * 100,
        "max_drawdown_pct": ((equity / np.maximum.accumulate(equity)) - 1).min() * 100,
        "folds": results,
    }

    with open(cfg.result_dir / "walk_forward_tcn.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {cfg.result_dir / 'walk_forward_tcn.json'}")


if __name__ == "__main__":
    main()
