"""Final optimization with LSTM + GradientBoosting + multiple instruments."""
import os
import json
import random
import numpy as np
import torch
import pandas as pd
import optuna
from optuna.trial import Trial
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

# CPU throttling — limit to 2 threads
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["NUMEXPR_NUM_THREADS"] = "2"

from config import Config
from features import prepare_features
from dataset import TimeSeriesDataset, auto_select_features, FEATURE_COLS
from model import build_model, Ensemble, build_sklearn_models, HybridEnsemble
from train import train
from backtest import run_backtest


def download_data(symbol: str, period: str = "1820d", interval: str = "1d"):
    """Download data from yfinance."""
    import yfinance as yf
    cache_path = Path("data") / f"{symbol.replace('/', '_')}_{interval}.csv"

    if cache_path.exists():
        print(f"  Loading cached data from {cache_path}")
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    print(f"  Downloading {symbol}...")
    df = yf.download(symbol, period=period, interval=interval)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.to_csv(cache_path)
    print(f"  Saved {len(df)} bars to {cache_path}")
    return df


def prepare_ensemble_data(df, config, split_idx, feature_cols=None):
    """Prepare data for both LSTM and sklearn models."""
    ds = TimeSeriesDataset(df, config.window, feature_cols=feature_cols)
    n = len(ds)

    # LSTM data
    train_ds = torch.utils.data.Subset(ds, range(0, split_idx))
    test_ds = torch.utils.data.Subset(ds, range(split_idx, n))

    # Sklearn data - flatten sequences
    cols = feature_cols or FEATURE_COLS
    available_cols = [c for c in cols if c in df.columns]
    X = df[available_cols].values
    y = df["label"].values

    # Create sequences for sklearn
    X_seq = []
    y_seq = []
    for i in range(config.window, len(X)):
        X_seq.append(X[i-config.window:i].flatten())
        y_seq.append(y[i])

    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    # Scale features
    scaler = StandardScaler()
    X_train_scaler = scaler.fit_transform(X_seq[:split_idx])
    X_test_scaler = scaler.transform(X_seq[split_idx:])

    return train_ds, test_ds, X_train_scaler, y_seq[:split_idx], X_test_scaler, y_seq[split_idx:], ds


def train_ensemble_models(train_ds, config, ds, n_models=3):
    """Train LSTM ensemble with different seeds."""
    seeds = [42 + i * 31 for i in range(n_models)]
    models = []
    for seed in seeds:
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        model = build_model(config, len(ds.cols))
        model = train(model, train_ds, train_ds, config, "cpu", quiet=True)
        models.append(model)
    return Ensemble(models)


def get_ensemble_predictions(ensemble, test_ds, device="cpu"):
    """Get predictions from LSTM ensemble."""
    from torch.utils.data import DataLoader
    loader = DataLoader(test_ds, batch_size=256, shuffle=False)
    probs = []
    with torch.no_grad():
        for x, _ in loader:
            prob = torch.sigmoid(ensemble(x)).numpy().flatten()
            probs.extend(prob)
    return np.array(probs)


def train_gradient_boosting(X_train, y_train, trial):
    """Train Gradient Boosting model."""
    params = {
        "n_estimators": trial.suggest_int("gb_n_estimators", 50, 150),
        "max_depth": trial.suggest_int("gb_max_depth", 3, 6),
        "learning_rate": trial.suggest_float("gb_lr", 0.01, 0.1, log=True),
        "subsample": trial.suggest_float("gb_subsample", 0.7, 0.9),
    }
    gb = GradientBoostingClassifier(**params, random_state=42)
    gb.fit(X_train, y_train)
    return gb


def combined_score(total_return, max_dd, win_rate, n_trades, lstm_acc, gb_acc):
    """Calculate combined score for ensemble."""
    dd_penalty = 1.0 / (1.0 + max_dd / 5.0)
    win_factor = win_rate / 100.0
    trade_bonus = min(n_trades / 30, 1.0)

    base_score = total_return * dd_penalty * win_factor * trade_bonus

    if total_return > 0:
        base_score += 5.0

    acc_bonus = (lstm_acc + gb_acc) * 2
    return base_score + acc_bonus


def objective(trial: Trial, df, config, device: str) -> float:
    """Objective with LSTM + GradientBoosting + hybrid ensemble."""
    # Neural network parameters
    config.hidden_size = trial.suggest_categorical("hidden_size", [32, 64, 128])
    config.num_layers = trial.suggest_categorical("num_layers", [1, 2])
    config.dropout = trial.suggest_float("dropout", 0.2, 0.5)
    config.window = trial.suggest_categorical("window", [20, 30, 40])
    config.batch_size = trial.suggest_categorical("batch_size", [64, 128])
    config.learning_rate = trial.suggest_float("learning_rate", 1e-4, 5e-4, log=True)
    config.epochs = 15
    config.patience = 5
    config.n_models = 1

    # Feature selection
    config.max_features = trial.suggest_categorical("max_features", [30, 40, 50])

    # Risk management
    config.stop_loss_pct = trial.suggest_float("stop_loss_pct", 0.02, 0.05)
    config.take_profit_pct = trial.suggest_float("take_profit_pct", 0.05, 0.12)
    config.risk_per_trade = 0.01

    if config.take_profit_pct < 2 * config.stop_loss_pct:
        config.take_profit_pct = 2 * config.stop_loss_pct

    try:
        import psutil
        if psutil.virtual_memory().percent > 85:
            return 0.0

        # Auto-select features
        feature_cols = auto_select_features(df, df["label"], max_features=config.max_features)

        # Prepare data
        split_idx = int(len(df) * 0.7)
        train_ds, test_ds, X_train, y_train, X_test, y_test, ds = prepare_ensemble_data(
            df, config, split_idx, feature_cols=feature_cols
        )

        # Train LSTM ensemble
        lstm_ensemble = train_ensemble_models(train_ds, config, ds)

        # Get LSTM predictions
        lstm_probs = get_ensemble_predictions(lstm_ensemble, test_ds)
        lstm_preds = (lstm_probs > 0.5).astype(int)

        # Train sklearn models
        sklearn_wrappers = build_sklearn_models(
            X_train, y_train,
            window=config.window, n_features=len(feature_cols),
            n_cpu=config.n_cpu_threads,
        )
        all_sklearn = [w for _, w in sklearn_wrappers]

        # Hybrid ensemble predictions
        hybrid = HybridEnsemble(lstm_ensemble.models, all_sklearn)
        hybrid_probs = get_ensemble_predictions(hybrid, test_ds)
        hybrid_preds = (hybrid_probs > 0.5).astype(int)

        # Train Gradient Boosting for comparison
        gb = train_gradient_boosting(X_train, y_train, trial)
        gb_preds = gb.predict(X_test)

        # Calculate accuracies
        test_labels = y_test[:len(hybrid_preds)]
        lstm_acc = accuracy_score(test_labels, lstm_preds)
        gb_acc = accuracy_score(test_labels, gb_preds)
        hybrid_acc = accuracy_score(test_labels, hybrid_preds)

        # Run backtest with hybrid ensemble
        result = run_backtest(hybrid, test_ds, df, config, device)

        total_return = result["total_return_pct"]
        max_dd = abs(result["max_drawdown_pct"])
        n_trades = result["n_trades"]
        win_rate = result["win_rate_pct"]

        if n_trades < 5:
            return 0.0

        # Score: prefer hybrid accuracy + backtest performance
        score = combined_score(total_return, max_dd, win_rate, n_trades, hybrid_acc, gb_acc)

        trial.set_user_attr("total_return", total_return)
        trial.set_user_attr("max_drawdown", max_dd)
        trial.set_user_attr("total_trades", n_trades)
        trial.set_user_attr("win_rate", win_rate)
        trial.set_user_attr("lstm_acc", lstm_acc)
        trial.set_user_attr("gb_acc", gb_acc)
        trial.set_user_attr("hybrid_acc", hybrid_acc)

        return score

    except Exception as e:
        import traceback
        print(f"Trial failed: {e}")
        traceback.print_exc()
        return 0.0


def optimize_for_instrument(df, instrument_name, n_trials=20):
    """Optimize model for a specific instrument."""
    print(f"\n{'='*60}")
    print(f"OPTIMIZING FOR: {instrument_name}")
    print("=" * 60)

    print("Computing features...")
    cfg = Config()
    df = prepare_features(df, cfg)
    print(f"  {len(df)} rows after feature engineering")

    study = optuna.create_study(
        direction="maximize",
        study_name=f"nn_trading_v2_{instrument_name}",
        storage=f"sqlite:///optuna_v2_{instrument_name}.db",
        load_if_exists=True,
    )

    study.optimize(
        lambda trial: objective(trial, df, cfg, "cpu"),
        n_trials=n_trials,
        timeout=1800,
        show_progress_bar=True,
    )

    best = study.best_trial
    print(f"\nBest score: {best.value:.4f}")
    print(f"Best params: {best.params}")

    return best


def run_walk_forward_optimized(df, config, instrument_name, n_folds=6, feature_cols=None):
    """Run walk-forward with optimized parameters."""
    print(f"\n{'='*60}")
    print(f"WALK-FORWARD: {instrument_name}")
    print("=" * 60)

    from walk_forward import walk_forward
    equity, results = walk_forward(df, config, "cpu", n_folds=n_folds, feature_cols=feature_cols)

    total_return = (equity[-1] / equity[0] - 1) * 100
    max_dd = ((equity / np.maximum.accumulate(equity)) - 1).min() * 100

    print(f"\nResults for {instrument_name}:")
    print(f"  Total Return: {total_return:+.2f}%")
    print(f"  Max Drawdown: {max_dd:.2f}%")
    print(f"  Total Trades: {sum(r.n_trades for r in results)}")
    print(f"  Avg Win Rate: {np.mean([r.win_rate for r in results]):.1f}%")

    return {
        "instrument": instrument_name,
        "total_return": total_return,
        "max_drawdown": max_dd,
        "total_trades": sum(r.n_trades for r in results),
        "avg_win_rate": np.mean([r.win_rate for r in results]),
        "folds": len(results),
    }


def main():
    torch.set_num_threads(2)

    instruments = [
        ("BTCUSDT", "Bitcoin"),
        ("ETHUSDT", "Ethereum"),
        ("SOLUSDT", "Solana"),
    ]

    Path("data").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)

    print("=" * 60)
    print("DOWNLOADING DATA")
    print("=" * 60)

    all_data = {}
    for symbol, name in instruments:
        try:
            df = download_data(symbol, period="1820d", interval="1d")
            if len(df) > 100:
                all_data[name] = df
                print(f"  {name}: {len(df)} bars")
            else:
                print(f"  {name}: insufficient data ({len(df)} bars)")
        except Exception as e:
            print(f"  {name}: error downloading - {e}")

    print("\n" + "=" * 60)
    print("OPTIMIZATION PHASE")
    print("=" * 60)

    optimized_params = {}
    for name, df in all_data.items():
        best = optimize_for_instrument(df, name, n_trials=3)
        optimized_params[name] = {
            "params": best.params,
            "attrs": best.user_attrs,
            "value": best.value,
        }

    with open("results/optimized_v2_all.json", "w") as f:
        json.dump(optimized_params, f, indent=2)

    print("\n" + "=" * 60)
    print("WALK-FORWARD VALIDATION")
    print("=" * 60)

    walk_forward_results = []
    for name, df in all_data.items():
        if name in optimized_params:
            cfg = Config()
            params = optimized_params[name]["params"]

            cfg.hidden_size = params.get("hidden_size", 64)
            cfg.num_layers = params.get("num_layers", 2)
            cfg.dropout = params.get("dropout", 0.35)
            cfg.window = params.get("window", 30)
            cfg.batch_size = params.get("batch_size", 64)
            cfg.learning_rate = params.get("learning_rate", 0.0003)
            cfg.n_models = 3
            cfg.max_features = params.get("max_features", 40)
            cfg.stop_loss_pct = params.get("stop_loss_pct", 0.03)
            cfg.take_profit_pct = params.get("take_profit_pct", 0.07)

            df_features = prepare_features(df, cfg)
            feature_cols = auto_select_features(df_features, df_features["label"], max_features=cfg.max_features)

            result = run_walk_forward_optimized(df_features, cfg, name, n_folds=5, feature_cols=feature_cols)
            walk_forward_results.append(result)

    final_output = {
        "instruments": walk_forward_results,
        "optimized_params": optimized_params,
    }

    with open("results/final_v2_results.json", "w") as f:
        json.dump(final_output, f, indent=2)

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    for result in walk_forward_results:
        print(f"\n{result['instrument']}:")
        print(f"  Return: {result['total_return']:+.2f}%")
        print(f"  Drawdown: {result['max_drawdown']:.2f}%")
        print(f"  Trades: {result['total_trades']}")
        print(f"  Win Rate: {result['avg_win_rate']:.1f}%")

    if walk_forward_results:
        avg_return = np.mean([r['total_return'] for r in walk_forward_results])
        avg_dd = np.mean([r['max_drawdown'] for r in walk_forward_results])
        print(f"\nPortfolio Average:")
        print(f"  Avg Return: {avg_return:+.2f}%")
        print(f"  Avg Drawdown: {avg_dd:.2f}%")

    print(f"\nResults saved to results/final_v2_results.json")


if __name__ == "__main__":
    main()
