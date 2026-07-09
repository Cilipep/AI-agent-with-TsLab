"""Quick Optuna optimization - fewer trials and folds for faster results."""
import random
import numpy as np
import torch
import pandas as pd
import optuna
from optuna.trial import Trial
from pathlib import Path

from config import Config
from features import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest import run_backtest


def objective(trial: Trial, df, device: str) -> float:
    """Simplified objective with fast walk-forward."""
    config = Config()

    # Model architecture
    config.model_type = trial.suggest_categorical("model_type", ["lstm", "tcn"])
    config.hidden_size = trial.suggest_categorical("hidden_size", [32, 64, 128])
    config.num_layers = trial.suggest_int("num_layers", 1, 3)
    config.dropout = trial.suggest_float("dropout", 0.1, 0.4)

    # Feature window
    config.window = trial.suggest_categorical("window", [30, 60, 90])

    # Training
    config.batch_size = trial.suggest_categorical("batch_size", [32, 64, 128])
    config.learning_rate = trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True)
    config.epochs = 20  # Fixed for speed
    config.patience = 7

    # Ensemble
    config.n_models = trial.suggest_categorical("n_models", [2, 3])

    # Risk management
    config.stop_loss_pct = trial.suggest_float("stop_loss_pct", 0.01, 0.04)
    config.take_profit_pct = trial.suggest_float("take_profit_pct", 0.03, 0.08)
    config.risk_per_trade = 0.02

    # Ensure TP >= 2 * SL
    if config.take_profit_pct < 2 * config.stop_loss_pct:
        config.take_profit_pct = 2 * config.stop_loss_pct

    try:
        # Fast single-fold train/test split
        ds = TimeSeriesDataset(df, config.window)
        n = len(ds)
        split = int(n * 0.7)

        train_ds = torch.utils.data.Subset(ds, range(0, split))
        test_ds = torch.utils.data.Subset(ds, range(split, n))

        # Train small ensemble
        seeds = [42 + i * 17 for i in range(config.n_models)]
        models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)

            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, train_ds, config, device, quiet=True)
            models.append(model)

        ensemble = Ensemble(models)

        # Backtest
        result = run_backtest(ensemble, test_ds, df, config, device)

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

    # Device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Create study
    study = optuna.create_study(
        direction="maximize",
        study_name="nn_trading_quick",
        storage="sqlite:///optuna_quick.db",
        load_if_exists=True,
    )

    # Quick optimization
    n_trials = 20  # Quick run
    timeout = 1800  # 30 minutes max

    print(f"\nStarting quick optimization ({n_trials} trials, {timeout}s timeout)...")
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
    with open(cfg.result_dir / "best_params_quick.json", "w") as f:
        json.dump(best_params, f, indent=2)

    print(f"\nBest parameters saved to {cfg.result_dir / 'best_params_quick.json'}")

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
