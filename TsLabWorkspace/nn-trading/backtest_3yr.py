"""Full 3-year backtest. Scaler leak fixed + embargo."""
import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
import torch; torch.set_num_threads(2)

import json, random, numpy as np, pandas as pd
from config import Config
from dataset import TimeSeriesDataset, auto_select_features, fit_scaler
from model import build_model, build_sklearn_models, HybridEnsemble
from train import train
from backtest_v2 import run_backtest_v2, calculate_sharpe, calculate_sortino, calculate_calmar
from features import make_label

EMBARGO = 7


def flatten_ds(ds):
    X, y = [], []
    for i in range(len(ds)):
        x, label = ds[i]
        X.append(x.numpy().flatten())
        y.append(label.item())
    return np.array(X), np.array(y)


def backtest_instrument(sym, name, cfg, n_folds=3):
    mtf_path = f"data/binance_{sym}_3tf.csv"
    d1_path = f"data/binance_{sym}_1d.csv"
    df = pd.read_csv(mtf_path if os.path.exists(mtf_path) else d1_path, index_col=0, parse_dates=True)

    df = df.copy()
    df["label"] = make_label(df, cfg.horizon, cfg.threshold).values
    df = df.dropna()

    exclude = {"Open", "High", "Low", "Close", "Volume", "label"}
    feature_cols = [c for c in df.columns if c not in exclude
                    and df[c].dtype in [np.float64, np.float32, np.int64]
                    and not df[c].isna().all()]
    if len(feature_cols) > cfg.max_features:
        feature_cols = auto_select_features(df, df["label"], max_features=cfg.max_features)

    total = len(df)
    test_size = total // (n_folds + 1)
    min_train = total // (n_folds + 1)
    seeds = [42 + i * 17 for i in range(cfg.n_models)]

    equity_parts = []
    fold_results = []

    for fold in range(n_folds):
        train_end = min_train + fold * test_size
        test_start = train_end + EMBARGO
        test_end = min(test_start + test_size, total)
        if test_end <= test_start:
            break

        # FIT SCALER ON TRAIN ONLY
        train_df = df.iloc[:train_end]
        scaler = fit_scaler(train_df, feature_cols)

        train_ds = TimeSeriesDataset(df.iloc[:train_end], cfg.window, feature_cols=feature_cols, scaler=scaler)
        vs = int(len(train_ds) * 0.85)
        train_sub = torch.utils.data.Subset(train_ds, range(0, vs))
        val_sub = torch.utils.data.Subset(train_ds, range(vs, len(train_ds)))

        test_start_idx = max(0, test_start - cfg.window)
        test_ds = TimeSeriesDataset(df.iloc[test_start_idx:test_end], cfg.window, feature_cols=feature_cols, scaler=scaler)

        base_models = []
        for seed in seeds:
            torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)
            m = build_model(cfg, len(feature_cols))
            m = train(m, train_sub, val_sub, cfg, "cpu", quiet=True)
            base_models.append(m)

        X_tr, y_tr = flatten_ds(train_sub)
        sklearn_wrappers = build_sklearn_models(X_tr, y_tr, cfg.window, len(feature_cols), n_cpu=2)
        ensemble = HybridEnsemble(base_models, [w for _, w in sklearn_wrappers])

        r = run_backtest_v2(ensemble, test_ds, df, cfg, "cpu", threshold=0.5,
                           use_trailing_stop=True, trailing_stop_pct=0.015,
                           use_dynamic_sizing=True, start_idx=test_start)

        part = r["equity"].copy()
        if equity_parts: part = part * equity_parts[-1][-1]
        equity_parts.append(part)

        fold_results.append({
            "fold": fold+1, "return": round(r["total_return_pct"], 2),
            "trades": r["n_trades"], "win_rate": round(r["win_rate_pct"], 1),
        })
        print(f"    Fold {fold+1}: {r['total_return_pct']:+.2f}% | trades={r['n_trades']} | win={r['win_rate_pct']:.0f}%")

    eq = np.concatenate(equity_parts) if equity_parts else np.array([1.0])
    total_ret = (eq[-1]/eq[0]-1)*100
    max_dd = ((eq/np.maximum.accumulate(eq))-1).min()*100
    return {
        "instrument": name, "symbol": sym,
        "total_return": round(total_ret, 2), "max_drawdown": round(max_dd, 2),
        "total_trades": sum(r["trades"] for r in fold_results),
        "avg_win_rate": round(np.mean([r["win_rate"] for r in fold_results]), 1),
        "sharpe": round(calculate_sharpe(eq), 2),
        "sortino": round(calculate_sortino(eq), 2),
        "calmar": round(calculate_calmar(eq), 2),
        "equity_curve": eq.tolist(), "folds": fold_results,
    }


def simulate_portfolio(instrument_results, alloc):
    min_len = min(len(r["equity_curve"]) for r in instrument_results)
    portfolio_equity = np.ones(min_len)
    for r in instrument_results:
        pct = alloc.get(r["instrument"], 0) / 100
        eq = np.array(r["equity_curve"][:min_len]) / r["equity_curve"][0]
        portfolio_equity += (eq - 1) * pct
    total_ret = (portfolio_equity[-1] / portfolio_equity[0] - 1) * 100
    max_dd = ((portfolio_equity / np.maximum.accumulate(portfolio_equity)) - 1).min() * 100
    return {
        "total_return": round(total_ret, 2), "max_drawdown": round(max_dd, 2),
        "sharpe": round(calculate_sharpe(portfolio_equity), 2),
        "sortino": round(calculate_sortino(portfolio_equity), 2),
        "calmar": round(calculate_calmar(portfolio_equity), 2),
        "equity_curve": portfolio_equity.tolist(),
    }


def main():
    alloc_path = Path("results/portfolio_allocation.json")
    alloc = json.load(open(alloc_path)).get("allocation", {}) if alloc_path.exists() else {}

    instruments = [("SOLUSDT","SOL"),("XLMUSDT","XLM"),("BCHUSDT","BCH"),("AAVEUSDT","AAVE"),("NEARUSDT","NEAR")]

    cfg = Config()
    cfg.hidden_size=32; cfg.num_layers=2; cfg.dropout=0.35; cfg.window=30
    cfg.batch_size=64; cfg.learning_rate=0.0002; cfg.n_models=3; cfg.max_features=40
    cfg.stop_loss_pct=0.03; cfg.take_profit_pct=0.07; cfg.n_cpu_threads=2

    print("=" * 70)
    print("FULL BACKTEST (Fixed scaler + embargo=7)")
    print("=" * 70)

    all_results = []
    for sym, name in instruments:
        print(f"\n  {name}")
        try:
            result = backtest_instrument(sym, name, cfg, n_folds=3)
            all_results.append(result)
        except Exception as e:
            print(f"  Error: {e}")

    portfolio = simulate_portfolio(all_results, alloc) if all_results else {}

    print(f"\n{'='*70}")
    print("RESULTS")
    print("=" * 70)
    for r in sorted(all_results, key=lambda x: -x["total_return"]):
        print(f"  {r['instrument']:8s} | {r['total_return']:+7.2f}% | DD={r['max_drawdown']:+.2f}% | Sharpe={r['sharpe']:+.2f}")
    print(f"  {'PORTFOLIO':8s} | {portfolio.get('total_return',0):+7.2f}% | DD={portfolio.get('max_drawdown',0):+.2f}% | Sharpe={portfolio.get('sharpe',0):+.2f}")

    output = {"instruments": [{k:v for k,v in r.items() if k!="equity_curve"} for r in all_results],
              "portfolio": {k:v for k,v in portfolio.items() if k!="equity_curve"}, "allocation": alloc}
    with open("results/full_backtest_fixed.json", "w") as f:
        json.dump(output, f, indent=2)
    with open("results/equity_curves_fixed.json", "w") as f:
        json.dump({r["instrument"]: r["equity_curve"] for r in all_results} | {"portfolio": portfolio.get("equity_curve",[])}, f)
    print(f"\nSaved to results/full_backtest_fixed.json")


from pathlib import Path
if __name__ == "__main__":
    main()
