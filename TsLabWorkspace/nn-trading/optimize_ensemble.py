"""Optimize with ensemble of LSTM + GradientBoosting + RandomForest."""
import os
import json
import random
import numpy as np
import torch
import pandas as pd
import optuna
from optuna.trial import Trial
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score

# Limit CPU threads
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"

from config import Config
from features import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest import run_backtest


def train_sklearn_models(X_train, y_train, X_test, y_test, trial):
    """Train sklearn models and return accuracy."""
    # Gradient Boosting
    gb_params = {
        "n_estimators": trial.suggest_int("gb_n_estimators", 50, 200),
        "max_depth": trial.suggest_int("gb_max_depth", 3, 8),
        "learning_rate": trial.suggest_float("gb_lr", 0.01, 0.2, log=True),
        "subsample": trial.suggest_float("gb_subsample", 0.6, 1.0),
    }
    gb = GradientBoostingClassifier(**gb_params, random_state=42)
    gb.fit(X_train, y_train)
    gb_acc = accuracy_score(y_test, gb.predict(X_test))

    # Random Forest
    rf_params = {
        "n_estimators": trial.suggest_int("rf_n_estimators", 50, 200),
        "max_depth": trial.suggest_int("rf_max_depth", 5, 15),
        "min_samples_split": trial.suggest_int("rf_min_samples_split", 2, 10),
    }
    rf = RandomForestClassifier(**rf_params, random_state=42, n_jobs=2)
    rf.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf.predict(X_test))

    return gb, rf, gb_acc, rf_acc


def objective(trial: Trial, df, device: str) -> float:
    """Objective with LSTM + sklearn ensemble."""
    config = Config()

    # LSTM parameters
    config.model_type = "lstm"
    config.hidden_size = trial.suggest_categorical("hidden_size", [32, 64, 128])
    config.num_layers = trial.suggest_int("num_layers", 1, 2)
    config.dropout = trial.suggest_float("dropout", 0.2, 0.4)
    config.window = trial.suggest_categorical("window", [30, 60])
    config.batch_size = trial.suggest_categorical("batch_size", [32, 64])
    config.learning_rate = trial.suggest_float("learning_rate", 1e-4, 1e-3, log=True)
    config.epochs = 15
    config.patience = 5
    config.n_models = 2

    # Risk management
    config.stop_loss_pct = trial.suggest_float("stop_loss_pct", 0.02, 0.04)
    config.take_profit_pct = trial.suggest_float("take_profit_pct", 0.04, 0.08)
    config.risk_per_trade = 0.02

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

        # Get features for sklearn
        feature_cols = [c for c in df.columns if c not in ["label", "Open", "High", "Low", "Close", "Volume"]]
        X = df[feature_cols].values
        y = df["label"].values

        # Time series split for sklearn
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Train sklearn models
        gb, rf, gb_acc, rf_acc = train_sklearn_models(X_train, y_train, X_test, y_test, trial)

        # Train LSTM ensemble
        train_ds = torch.utils.data.Subset(ds, range(0, split))
        test_ds = torch.utils.data.Subset(ds, range(split, n))

        seeds = [42 + i * 17 for i in range(config.n_models)]
        lstm_models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            model = build_model(config, len(ds.cols))
            model = train(model, train_ds, train_ds, config, "cpu", quiet=True)
            lstm_models.append(model)

        lstm_ensemble = Ensemble(lstm_models)

        # Get LSTM predictions
        from torch.utils.data import DataLoader
        loader = DataLoader(test_ds, batch_size=256, shuffle=False)
        lstm_probs = []
        with torch.no_grad():
            for x, _ in loader:
                prob = torch.sigmoid(lstm_ensemble(x)).numpy().flatten()
                lstm_probs.extend(prob)
        lstm_preds = (np.array(lstm_probs) > 0.5).astype(int)

        # Get sklearn predictions
        gb_preds = gb.predict(X_test)
        rf_preds = rf.predict(X_test)

        # Ensemble: majority vote
        ensemble_preds = ((lstm_preds + gb_preds + rf_preds) >= 2).astype(int)

        # Calculate accuracy
        test_labels = y[split:split+len(ensemble_preds)]
        ensemble_acc = accuracy_score(test_labels, ensemble_preds)

        # Run backtest with ensemble predictions
        # Create mock model that returns ensemble predictions
        class EnsembleModel:
            def __init__(self, probs):
                self.probs = probs
            def __call__(self, x):
                return torch.tensor(self.probs[:len(x)]).unsqueeze(1).float()

        mock_ensemble = EnsembleModel(lstm_probs)

        # Backtest
        result = run_backtest(mock_ensemble, test_ds, df, config, "cpu")

        total_return = result["total_return_pct"]
        max_dd = abs(result["max_drawdown_pct"])
        n_trades = result["n_trades"]
        win_rate = result["win_rate_pct"]

        if n_trades < 5:
            return 0.0

        # Score: ensemble accuracy + risk-adjusted return
        dd_penalty = 1.0 / (1.0 + max_dd / 10.0)
        win_factor = win_rate / 100.0
        acc_bonus = ensemble_acc * 10  # Bonus for accuracy
        score = total_return * dd_penalty * win_factor + acc_bonus

        trial.set_user_attr("total_return", total_return)
        trial.set_user_attr("max_drawdown", max_dd)
        trial.set_user_attr("total_trades", n_trades)
        trial.set_user_attr("win_rate", win_rate)
        trial.set_user_attr("ensemble_acc", ensemble_acc)
        trial.set_user_attr("gb_acc", gb_acc)
        trial.set_user_attr("rf_acc", rf_acc)

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
        study_name="nn_trading_ensemble",
        storage="sqlite:///optuna_ensemble.db",
        load_if_exists=True,
    )

    # Optimization
    n_trials = 15
    timeout = 1200  # 20 minutes

    print(f"\nStarting ensemble optimization ({n_trials} trials)...")
    print("=" * 50)

    study.optimize(
        lambda trial: objective(trial, df, device),
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=True,
    )

    # Results
    print("\n" + "=" * 60)
    print("ENSEMBLE OPTIMIZATION COMPLETE")
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
    with open(cfg.result_dir / "best_params_ensemble.json", "w") as f:
        json.dump(best_params, f, indent=2)

    print(f"\nBest parameters saved to {cfg.result_dir / 'best_params_ensemble.json'}")


if __name__ == "__main__":
    main()
