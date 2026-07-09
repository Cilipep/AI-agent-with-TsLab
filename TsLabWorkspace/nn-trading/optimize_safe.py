"""Safe Optuna optimization - limited CPU/RAM usage."""
import random
import os
import sys
import numpy as np
import torch
import pandas as pd
import optuna
from optuna.trial import Trial
from pathlib import Path

# Limit CPU threads BEFORE any torch import
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"

from config import Config
from features import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest import run_backtest

# Global resource limits
MAX_CPU_THREADS = 2
MAX_BATCH_SIZE = 32
MAX_MODELS = 2
MAX_EPOCHS = 15


def objective(trial: Trial, df, device: str) -> float:
    """Objective with resource limits."""
    config = Config()

    # Model architecture - smaller models
    config.model_type = trial.suggest_categorical("model_type", ["lstm"])
    config.hidden_size = trial.suggest_categorical("hidden_size", [32, 64])
    config.num_layers = trial.suggest_int("num_layers", 1, 2)
    config.dropout = trial.suggest_float("dropout", 0.2, 0.4)

    # Feature window - smaller windows
    config.window = trial.suggest_categorical("window", [30, 60])

    # Training - LIMITED resources
    config.batch_size = trial.suggest_categorical("batch_size", [16, 32])
    config.learning_rate = trial.suggest_float("learning_rate", 1e-4, 1e-3, log=True)
    config.epochs = MAX_EPOCHS
    config.patience = 5

    # Ensemble - fewer models
    config.n_models = trial.suggest_categorical("n_models", [2])

    # Risk management
    config.stop_loss_pct = trial.suggest_float("stop_loss_pct", 0.02, 0.04)
    config.take_profit_pct = trial.suggest_float("take_profit_pct", 0.04, 0.08)
    config.risk_per_trade = 0.02

    # Ensure TP >= 2 * SL
    if config.take_profit_pct < 2 * config.stop_loss_pct:
        config.take_profit_pct = 2 * config.stop_loss_pct

    try:
        # Check available memory before proceeding
        import psutil
        mem = psutil.virtual_memory()
        if mem.percent > 85:
            print(f"WARNING: High memory usage ({mem.percent}%), skipping trial")
            return 0.0

        # Fast single-fold train/test split
        ds = TimeSeriesDataset(df, config.window)
        n = len(ds)
        split = int(n * 0.7)

        train_ds = torch.utils.data.Subset(ds, range(0, split))
        test_ds = torch.utils.data.Subset(ds, range(split, n))

        # Train with resource limits
        seeds = [42 + i * 17 for i in range(config.n_models)]
        models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)

            # Force CPU to avoid GPU memory issues
            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, train_ds, config, "cpu", quiet=True)
            models.append(model)

        ensemble = Ensemble(models)

        # Backtest
        result = run_backtest(ensemble, test_ds, df, config, "cpu")

        total_return = result["total_return_pct"]
        max_dd = abs(result["max_drawdown_pct"])
        n_trades = result["n_trades"]
        win_rate = result["win_rate_pct"]

        # Require minimum trades
        if n_trades < 5:
            return 0.0

        # Score: risk-adjusted return
        dd_penalty = 1.0 / (1.0 + max_dd / 10.0)
        win_factor = win_rate / 100.0
        score = total_return * dd_penalty * win_factor

        trial.set_user_attr("total_return", total_return)
        trial.set_user_attr("max_drawdown", max_dd)
        trial.set_user_attr("total_trades", n_trades)
        trial.set_user_attr("win_rate", win_rate)

        return score

    except Exception as e:
        print(f"Trial failed: {e}")
        return 0.0


def main():
    # Set thread limits
    torch.set_num_threads(MAX_CPU_THREADS)

    cfg = Config()
    for d in [cfg.data_dir, cfg.model_dir, cfg.result_dir]:
        d.mkdir(exist_ok=True)

    # Load data
    cache_path = cfg.data_dir / f"{cfg.symbol.replace('/', '_')}_{cfg.interval}.csv"
    print(f"Loading data from {cache_path}")
    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)

    # Prepare features
    print("Computing features...")
    df = prepare_features(df, cfg)
    print(f"  {len(df)} rows after feature engineering")

    # Device - force CPU for safety
    device = "cpu"
    print(f"Using device: {device} (forced for resource limits)")

    # Create study
    study = optuna.create_study(
        direction="maximize",
        study_name="nn_trading_safe",
        storage="sqlite:///optuna_safe.db",
        load_if_exists=True,
    )

    # SAFE optimization - fewer trials
    n_trials = 10
    timeout = 900  # 15 minutes max

    print(f"\nStarting SAFE optimization ({n_trials} trials, {timeout}s timeout)...")
    print("Resource limits: 2 CPU threads, CPU-only, small batch size")
    print("=" * 50)

    study.optimize(
        lambda trial: objective(trial, df, device),
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=True,
    )

    # Results
    print("\n" + "=" * 60)
    print("OPTIMIZATION COMPLETE")
    print("=" * 60)

    best = study.best_trial
    print(f"\nBest trial: #{best.number}")
    print(f"Best score: {best.value:.4f}")
    print(f"\nBest hyperparameters:")
    for key, value in best.params.items():
        print(f"  {key}: {value}")

    print(f"\nBest trial attributes:")
    for key, value in best.user_attrs.items():
        print(f"  {key}: {value}")

    # Save best config
    import json
    best_params = {
        "params": best.params,
        "attrs": best.user_attrs,
        "value": best.value,
    }
    with open(cfg.result_dir / "best_params_safe.json", "w") as f:
        json.dump(best_params, f, indent=2)

    print(f"\nBest parameters saved to {cfg.result_dir / 'best_params_safe.json'}")


if __name__ == "__main__":
    main()
