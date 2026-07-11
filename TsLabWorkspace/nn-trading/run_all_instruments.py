"""Walk-forward HybridEnsemble on all 10 instruments."""
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
import torch; torch.set_num_threads(2)

import json, random, numpy as np, pandas as pd
from torch.utils.data import Subset
from config import Config
from dataset import TimeSeriesDataset, auto_select_features
from model import build_model, Ensemble, build_sklearn_models, HybridEnsemble
from train import train
from backtest_v2 import run_backtest_v2, calculate_sharpe, calculate_sortino, calculate_calmar
from features import make_label


def flatten_ds(ds):
    X, y = [], []
    for i in range(len(ds)):
        x, label = ds[i]
        X.append(x.numpy().flatten())
        y.append(label.item())
    return np.array(X), np.array(y)


def run_one(df, cfg, name, n_folds=5):
    df["label"] = make_label(df, cfg.horizon, cfg.threshold)
    df = df.dropna()
    exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
    feature_cols = [c for c in df.columns if c not in exclude
                    and df[c].dtype in [np.float64, np.float32, np.int64]]
    if len(feature_cols) > cfg.max_features:
        feature_cols = auto_select_features(df, df["label"], max_features=cfg.max_features)

    ds = TimeSeriesDataset(df, cfg.window, feature_cols=feature_cols)
    total = len(ds)
    test_size = total // (n_folds + 1)
    min_train = total // (n_folds + 1)
    seeds = [42 + i * 17 for i in range(cfg.n_models)]
    equity_parts = []
    fold_results = []

    for fold in range(n_folds):
        train_end = min_train + fold * test_size
        test_start = train_end
        test_end = min(test_start + test_size, total)
        if test_end <= test_start:
            break

        full_train = list(range(0, train_end - cfg.window))
        vs = int(len(full_train) * 0.85)
        train_ds = Subset(ds, full_train[:vs])
        val_ds = Subset(ds, full_train[vs:])
        test_ds = Subset(ds, range(test_start - cfg.window, test_end - cfg.window))

        # Train neural models
        base_models = []
        for seed in seeds:
            torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)
            m = build_model(cfg, len(ds.cols))
            m = train(m, train_ds, val_ds, cfg, "cpu", quiet=True)
            base_models.append(m)

        # Train sklearn models
        X_tr, y_tr = flatten_ds(train_ds)
        sklearn_wrappers = build_sklearn_models(X_tr, y_tr, cfg.window, len(ds.cols), n_cpu=2)
        all_sklearn = [w for _, w in sklearn_wrappers]
        ensemble = HybridEnsemble(base_models, all_sklearn)

        # Fixed threshold for speed
        best_thr = 0.5

        r = run_backtest_v2(ensemble, test_ds, df, cfg, "cpu", threshold=best_thr,
                           use_trailing_stop=True, trailing_stop_pct=0.015,
                           use_dynamic_sizing=True, start_idx=test_start)

        part = r["equity"].copy()
        if equity_parts: part = part * equity_parts[-1][-1]
        equity_parts.append(part)

        fold_results.append({
            "fold": fold+1, "return": round(r["total_return_pct"], 2),
            "trades": r["n_trades"], "win_rate": round(r["win_rate_pct"], 1),
            "sharpe": round(r["sharpe_ratio"], 2), "threshold": best_thr,
        })
        print(f"    Fold {fold+1}: {r['total_return_pct']:+.2f}% | trades={r['n_trades']} | "
              f"win={r['win_rate_pct']:.0f}% | thr={best_thr}")

    eq = np.concatenate(equity_parts) if equity_parts else np.array([1.0])
    total_ret = (eq[-1]/eq[0]-1)*100
    max_dd = ((eq/np.maximum.accumulate(eq))-1).min()*100
    sharpe = calculate_sharpe(eq)
    sortino = calculate_sortino(eq)
    calmar = calculate_calmar(eq)

    return {
        "instrument": name,
        "total_return": round(total_ret, 2),
        "max_drawdown": round(max_dd, 2),
        "total_trades": sum(r["trades"] for r in fold_results),
        "avg_win_rate": round(np.mean([r["win_rate"] for r in fold_results]), 1),
        "sharpe": round(sharpe, 2),
        "sortino": round(sortino, 2),
        "calmar": round(calmar, 2),
        "folds": fold_results,
    }


def main():
    instruments = [
        ("NEARUSDT", "NEAR"), ("XLMUSDT", "XLM"), ("SOLUSDT", "SOL"),
        ("AAVEUSDT", "AAVE"), ("LINKUSDT", "LINK"), ("SUIUSDT", "SUI"),
        ("ADAUSDT", "ADA"), ("BCHUSDT", "BCH"), ("TRXUSDT", "TRX"),
        ("UNIUSDT", "UNI"),
    ]

    all_results = []

    for sym, name in instruments:
        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}")

        df = pd.read_csv(f"data/binance_{sym}_3tf.csv", index_col=0, parse_dates=True)

        cfg = Config()
        cfg.hidden_size = 32
        cfg.num_layers = 2
        cfg.dropout = 0.35
        cfg.window = 30
        cfg.batch_size = 64
        cfg.learning_rate = 0.0002
        cfg.n_models = 3
        cfg.max_features = 40
        cfg.stop_loss_pct = 0.03
        cfg.take_profit_pct = 0.07
        cfg.n_cpu_threads = 2

        try:
            result = run_one(df, cfg, name, n_folds=3)
            all_results.append(result)
        except Exception as e:
            print(f"  Error: {e}")

    # Summary
    print(f"\n{'='*60}")
    print("RESULTS (10 instruments, HybridEnsemble, 3 TF)")
    print("=" * 60)

    profitable = []
    for r in sorted(all_results, key=lambda x: -x["total_return"]):
        status = "+" if r["total_return"] > 0 else ""
        print(f"  {r['instrument']:8s} | {status}{r['total_return']:.2f}% | DD={r['max_drawdown']:.2f}% | "
              f"Win={r['avg_win_rate']:.0f}% | Trades={r['total_trades']:4d} | Sharpe={r['sharpe']:+.2f}")
        if r["total_return"] > 0:
            profitable.append(r)

    if profitable:
        avg_ret = np.mean([r["total_return"] for r in profitable])
        avg_sharpe = np.mean([r["sharpe"] for r in profitable])
        print(f"\nProfitable: {len(profitable)}/{len(all_results)}")
        print(f"Avg return (profitable): {avg_ret:+.2f}%")
        print(f"Avg Sharpe (profitable): {avg_sharpe:+.2f}")

    with open("results/instruments_walkforward.json", "w") as f:
        json.dump({"instruments": all_results,
                    "profitable": [r["instrument"] for r in profitable]}, f, indent=2)

    print(f"\nSaved to results/instruments_walkforward.json")


if __name__ == "__main__":
    main()
