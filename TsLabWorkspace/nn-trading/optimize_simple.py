"""Simple but robust optimization - focus on consistency."""
import os
import json
import random
import numpy as np
import torch
import pandas as pd
import optuna
from optuna.trial import Trial
from pathlib import Path

# Limit CPU threads
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

from config import Config
from features_talib import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest import run_backtest


def objective(trial: Trial, df, device: str) -> float:
    """Simple objective with strong regularization."""
    config = Config()

    # Simple model
    config.model_type = "lstm"
    config.hidden_size = trial.suggest_categorical("hidden_size", [16, 32])
    config.num_layers = 1
    config.dropout = trial.suggest_float("dropout", 0.3, 0.6)
    config.window = trial.suggest_categorical("window", [20, 30])
    config.batch_size = trial.suggest_categorical("batch_size", [64, 128])
    config.learning_rate = trial.suggest_float("learning_rate", 1e-4, 5e-4, log=True)
    config.epochs = 30
    config.patience = 10
    config.n_models = 3  # More models for stability

    # Conservative risk management
    config.stop_loss_pct = trial.suggest_float("stop_loss_pct", 0.02, 0.04)
    config.take_profit_pct = trial.suggest_float("take_profit_pct", 0.04, 0.08)
    config.risk_per_trade = 0.01  # 1% risk per trade

    # Ensure TP >= 2 * SL
    if config.take_profit_pct < 2 * config.stop_loss_pct:
        config.take_profit_pct = 2 * config.stop_loss_pct

    try:
        # Check memory
        import psutil
        mem = psutil.virtual_memory()
        if mem.percent > 85:
            return 0.0

        # Prepare dataset
        ds = TimeSeriesDataset(df, config.window)
        n = len(ds)
        split = int(n * 0.7)

        train_ds = torch.utils.data.Subset(ds, range(0, split))
        test_ds = torch.utils.data.Subset(ds, range(split, n))

        # Train ensemble with different seeds
        seeds = [42 + i * 31 for i in range(config.n_models)]
        models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
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
        if n_trades < 10:
            return 0.0

        # Score: focus on consistency and low drawdown
        dd_penalty = 1.0 / (1.0 + max_dd / 5.0)  # Stronger penalty for drawdown
        win_factor = win_rate / 100.0
        trade_bonus = min(n_trades / 50, 1.0)  # Bonus for more trades

        # Combined score
        score = total_return * dd_penalty * win_factor * trade_bonus

        # Bonus for positive return
        if total_return > 0:
            score += 5.0

        trial.set_user_attr("total_return", total_return)
        trial.set_user_attr("max_drawdown", max_dd)
        trial.set_user_attr("total_trades", n_trades)
        trial.set_user_attr("win_rate", win_rate)

        return score

    except Exception as e:
        print(f"Trial failed: {e}")
        return 0.0


def main():
    torch.set_num_threads(2)

    cfg = Config()
    for d in [cfg.data_dir, cfg.model_dir, cfg.result_dir]:
        d.mkdir(exist_ok=True)

    # Load data
    cache_path = cfg.data_dir / f"{cfg.symbol.replace('/', '_')}_{cfg.interval}.csv"
    print(f"Loading data from {cache_path}")
    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    print(f"  {len(df)} bars loaded")

    # Prepare features
    print("Computing features...")
    df = prepare_features(df, cfg)
    print(f"  {len(df)} rows after feature engineering")

    # Device
    device = "cpu"
    print(f"Using device: {device}")

    # Create study
    study = optuna.create_study(
        direction="maximize",
        study_name="nn_trading_simple",
        storage="sqlite:///optuna_simple.db",
        load_if_exists=True,
    )

    # Optimization
    n_trials = 25
    timeout = 1500  # 25 minutes

    print(f"\nStarting simple optimization ({n_trials} trials)...")
    print("=" * 50)

    study.optimize(
        lambda trial: objective(trial, df, device),
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=True,
    )

    # Results
    print("\n" + "=" * 60)
    print("SIMPLE OPTIMIZATION COMPLETE")
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
    best_params = {
        "params": best.params,
        "attrs": best.user_attrs,
        "value": best.value,
    }
    with open(cfg.result_dir / "best_params_simple.json", "w") as f:
        json.dump(best_params, f, indent=2)

    print(f"\nBest parameters saved to {cfg.result_dir / 'best_params_simple.json'}")

    # Top 5 trials
    print("\n" + "=" * 60)
    print("TOP 5 TRIALS")
    print("=" * 60)

    trials = sorted(study.trials, key=lambda t: t.value if t.value else 0, reverse=True)[:5]
    for i, trial in enumerate(trials, 1):
        if trial.value:
            print(f"\n#{i} (Trial {trial.number}): score={trial.value:.4f}")
            for k, v in trial.params.items():
                print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
