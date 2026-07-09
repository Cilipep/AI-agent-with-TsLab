"""Unified optimization script - replaces optimize.py, optimize_v2.py, optimize_simple.py, optimize_quick.py, optimize_safe.py."""
import os
import json
import random
import numpy as np
import torch
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
torch.set_num_threads(2)

from config import Config
from features_full_talib import prepare_features
from dataset import TimeSeriesDataset
from model import build_model, Ensemble
from train import train
from backtest_v2 import run_backtest_v2


@dataclass
class OptimizeConfig:
    """Optimization configuration."""
    n_trials: int = 50           # Number of Optuna trials
    n_folds: int = 5             # Walk-forward folds for evaluation
    n_models: int = 3            # Ensemble size
    timeout: int = 3600          # Timeout in seconds (1 hour)
    direction: str = "maximize"  # Optimize for maximize/minimize
    metric: str = "return"       # Metric to optimize: return, sharpe, calmar
    use_optuna: bool = True      # Use Optuna (False = random search)
    random_seed: int = 42


@dataclass
class ParamRanges:
    """Parameter ranges for optimization."""
    hidden_size: tuple = (16, 128)
    num_layers: tuple = (1, 3)
    dropout: tuple = (0.1, 0.5)
    window: tuple = (20, 120)
    batch_size: tuple = (32, 128)
    learning_rate: tuple = (1e-4, 1e-2)
    stop_loss_pct: tuple = (0.01, 0.05)
    take_profit_pct: tuple = (0.02, 0.08)
    trailing_stop_pct: tuple = (0.005, 0.03)


PRESETS = {
    "quick": {"n_trials": 20, "n_folds": 3, "timeout": 600},
    "safe": {"n_trials": 50, "n_folds": 5, "timeout": 1800},
    "full": {"n_trials": 100, "n_folds": 5, "timeout": 3600},
    "exhaustive": {"n_trials": 200, "n_folds": 10, "timeout": 7200},
}


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


def evaluate_params(df, config, params, n_folds=5):
    """Evaluate a set of parameters using walk-forward."""
    cfg = Config()
    cfg.model_type = "transformer"
    cfg.hidden_size = params["hidden_size"]
    cfg.num_layers = params.get("num_layers", 1)
    cfg.dropout = params["dropout"]
    cfg.window = params["window"]
    cfg.batch_size = params["batch_size"]
    cfg.learning_rate = params["learning_rate"]
    cfg.n_models = 3
    cfg.stop_loss_pct = params["stop_loss_pct"]
    cfg.take_profit_pct = params["take_profit_pct"]

    ds = TimeSeriesDataset(df, cfg.window)
    total = len(ds)
    fold_size = total // (n_folds + 1)

    results = []
    equity_parts = []
    seeds = [42 + i * 31 for i in range(cfg.n_models)]

    for fold in range(n_folds):
        train_end = fold_size * (fold + 1)
        test_start = train_end
        test_end = min(test_start + fold_size, total)

        if test_end <= test_start:
            break

        train_ds = torch.utils.data.Subset(ds, range(0, train_end - cfg.window))
        test_ds = torch.utils.data.Subset(ds, range(test_start - cfg.window, test_end - cfg.window))

        models = []
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            model = build_model(cfg, len(ds.cols))
            model = train(model, train_ds, train_ds, cfg, "cpu", quiet=True)
            models.append(model)

        ensemble = Ensemble(models)

        result = run_backtest_v2(
            ensemble, test_ds, df, cfg, "cpu",
            use_trailing_stop=True,
            trailing_stop_pct=params.get("trailing_stop_pct", 0.01),
            use_dynamic_sizing=True
        )

        results.append(result)

        part = result["equity"].copy()
        if equity_parts:
            part = part * equity_parts[-1][-1]
        equity_parts.append(part)

    if not equity_parts:
        return {"return": -100, "drawdown": -100, "sharpe": -10, "trades": 0}

    full_equity = np.concatenate(equity_parts)
    total_return = (full_equity[-1] / full_equity[0] - 1) * 100
    max_dd = ((full_equity / np.maximum.accumulate(full_equity)) - 1).min() * 100
    total_trades = sum(r["n_trades"] for r in results)
    avg_sharpe = np.mean([r["sharpe_ratio"] for r in results])
    avg_pf = np.mean([r["profit_factor"] for r in results if r["profit_factor"] < 100])

    return {
        "return": total_return,
        "drawdown": max_dd,
        "sharpe": avg_sharpe,
        "profit_factor": avg_pf,
        "trades": total_trades,
    }


def random_search(df, opt_config: OptimizeConfig, param_ranges: ParamRanges):
    """Random search optimization."""
    all_results = []
    best_score = -float("inf")
    best_params = None

    for trial in range(opt_config.n_trials):
        params = {
            "hidden_size": random.choice([16, 32, 64, 128]),
            "num_layers": random.choice([1, 2, 3]),
            "dropout": random.uniform(*param_ranges.dropout),
            "window": random.choice([20, 30, 40, 60, 80, 120]),
            "batch_size": random.choice([32, 64, 128]),
            "learning_rate": random.uniform(*param_ranges.learning_rate),
            "stop_loss_pct": random.uniform(*param_ranges.stop_loss_pct),
            "take_profit_pct": random.uniform(*param_ranges.take_profit_pct),
            "trailing_stop_pct": random.uniform(*param_ranges.trailing_stop_pct),
        }

        print(f"\nTrial {trial+1}/{opt_config.n_trials}")
        print(f"  Params: {json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in params.items()})}")

        metrics = evaluate_params(df, Config(), params, opt_config.n_folds)

        # Score based on metric
        if opt_config.metric == "return":
            score = metrics["return"]
        elif opt_config.metric == "sharpe":
            score = metrics["sharpe"]
        elif opt_config.metric == "calmar":
            score = metrics["return"] / abs(metrics["drawdown"]) if metrics["drawdown"] != 0 else 0
        else:
            score = metrics["return"]

        print(f"  Return: {metrics['return']:+.2f}% | DD: {metrics['drawdown']:.2f}% | "
              f"Sharpe: {metrics['sharpe']:.2f} | PF: {metrics['profit_factor']:.2f}")

        all_results.append({"params": params, "metrics": metrics, "score": score})

        if score > best_score:
            best_score = score
            best_params = params
            print(f"  ** NEW BEST ** Score: {score:.4f}")

    return best_params, best_score, all_results


def optuna_search(df, opt_config: OptimizeConfig, param_ranges: ParamRanges):
    """Optuna Bayesian optimization."""
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    all_results = []

    def objective(trial):
        params = {
            "hidden_size": trial.suggest_categorical("hidden_size", [16, 32, 64, 128]),
            "num_layers": trial.suggest_int("num_layers", 1, 3),
            "dropout": trial.suggest_float("dropout", *param_ranges.dropout),
            "window": trial.suggest_categorical("window", [20, 30, 40, 60, 80, 120]),
            "batch_size": trial.suggest_categorical("batch_size", [32, 64, 128]),
            "learning_rate": trial.suggest_float("learning_rate", *param_ranges.learning_rate, log=True),
            "stop_loss_pct": trial.suggest_float("stop_loss_pct", *param_ranges.stop_loss_pct),
            "take_profit_pct": trial.suggest_float("take_profit_pct", *param_ranges.take_profit_pct),
            "trailing_stop_pct": trial.suggest_float("trailing_stop_pct", *param_ranges.trailing_stop_pct),
        }

        metrics = evaluate_params(df, Config(), params, opt_config.n_folds)

        all_results.append({"params": params, "metrics": metrics})

        if opt_config.metric == "return":
            return metrics["return"]
        elif opt_config.metric == "sharpe":
            return metrics["sharpe"]
        elif opt_config.metric == "calmar":
            return metrics["return"] / abs(metrics["drawdown"]) if metrics["drawdown"] != 0 else 0
        return metrics["return"]

    study = optuna.create_study(
        direction=opt_config.direction,
        sampler=optuna.samplers.TPESampler(seed=opt_config.random_seed),
    )

    print(f"\nRunning Optuna optimization ({opt_config.n_trials} trials)...")
    study.optimize(objective, n_trials=opt_config.n_trials, timeout=opt_config.timeout)

    best_params = study.best_params
    best_score = study.best_value

    return best_params, best_score, all_results


def main():
    import sys

    # Parse arguments
    preset = sys.argv[1] if len(sys.argv) > 1 else "safe"
    symbol = sys.argv[2] if len(sys.argv) > 2 else "BTC-USD"
    metric = sys.argv[3] if len(sys.argv) > 3 else "return"

    if preset not in PRESETS:
        print(f"Available presets: {', '.join(PRESETS.keys())}")
        sys.exit(1)

    preset_config = PRESETS[preset]
    opt_config = OptimizeConfig(
        n_trials=preset_config["n_trials"],
        n_folds=preset_config["n_folds"],
        timeout=preset_config["timeout"],
        metric=metric,
    )

    param_ranges = ParamRanges()

    print("=" * 70)
    print(f"OPTIMIZATION: {preset.upper()}")
    print(f"Symbol: {symbol} | Metric: {metric}")
    print(f"Trials: {opt_config.n_trials} | Folds: {opt_config.n_folds}")
    print("=" * 70)

    # Download data
    df = download_data(symbol, period="1820d", interval="1d")
    print(f"Data: {len(df)} bars")

    # Prepare features
    print("Computing features...")
    df = prepare_features(df, Config())
    print(f"Features: {len(df.columns)}")

    # Run optimization
    try:
        best_params, best_score, all_results = optuna_search(df, opt_config, param_ranges)
        search_type = "Optuna"
    except ImportError:
        print("Optuna not installed, using random search...")
        best_params, best_score, all_results = random_search(df, opt_config, param_ranges)
        search_type = "Random"

    # Print results
    print(f"\n{'='*70}")
    print(f"OPTIMIZATION COMPLETE ({search_type})")
    print(f"{'='*70}")
    print(f"\nBest {metric}: {best_score:.4f}")
    print(f"\nBest parameters:")
    for k, v in best_params.items():
        print(f"  {k}: {round(v, 4) if isinstance(v, float) else v}")

    # Top 5 results
    sorted_results = sorted(all_results, key=lambda x: x.get("score", x["metrics"]["return"]), reverse=True)
    print(f"\nTop 5 results:")
    for i, r in enumerate(sorted_results[:5], 1):
        score = r.get("score", r["metrics"]["return"])
        m = r["metrics"]
        print(f"  {i}. Score: {score:.4f} | Return: {m['return']:+.2f}% | DD: {m['drawdown']:.2f}% | Sharpe: {m['sharpe']:.2f}")

    # Save results
    output = {
        "preset": preset,
        "symbol": symbol,
        "metric": metric,
        "search_type": search_type,
        "best_params": best_params,
        "best_score": best_score,
        "all_results": all_results,
    }

    output_path = Path("results") / f"optimize_{preset}_{symbol}_{metric}.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
